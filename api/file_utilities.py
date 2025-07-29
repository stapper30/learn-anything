import PyPDF2
from openai import OpenAI
from pydantic import BaseModel
from pydantic import BaseModel
import asyncio
import tiktoken
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key}")  # Debugging line to check if the API key is loaded correctly
client = OpenAI(api_key=api_key)

text = """
    { "concepts": [{ "title": "Definition of a Function and its Properties", "example": "Consider the function f: {1,2,3} → {a,b,c} defined as f(1)=a, f(2)=b, f(3)=c. This is a function because each element in the domain maps to a unique element in the codomain. It is one-to-one because different inputs produce different outputs: f(1) ≠ f(2). It is onto if every element in {a,b,c} is mapped to by some element in the domain.", "explanation": "A function is a rule that assigns exactly one output (codomain element) to each input (domain element). It is called one-to-one if no two different inputs share the same output. It is onto if every element in the codomain is an output of some input. In that case, an inverse function can be defined reversing the mapping." }, { "title": "Important Functions: Power, Exponential, and Logarithm", "example": "Power function example: f(x) = x^2. Exponential function example: f(x) = 2^x. Logarithm example: log_2(8) = 3, since 2^3 = 8.", "explanation": "Power functions involve raising the input to a fixed power. Exponential functions raise a fixed base to the power of the input. Logarithms are the inverse of exponential functions, converting multiplication into addition and solving for the exponent in equations like y = a^x." }, { "title": "Ceiling and Floor Functions", "example": "Ceiling example: ⌈3.1⌉ = 4, ⌈4⌉ = 4. Floor example: ⌊3.7⌋ = 3, ⌊3⌋ = 3.", "explanation": "The ceiling function rounds any real number up to the nearest integer, while the floor function rounds down to the nearest integer. These are helpful in algorithms for discretizing values or handling boundaries." }, { "title": "Basic Properties of Exponentials and Logarithms", "example": "For a>1, 2^{3+4} = 2^3 * 2^4 = 8 * 16 = 128. Also, log_2(8 * 16) = log_2(8) + log_2(16) = 3 + 4 = 7.", "explanation": "Exponential functions with base greater than one are strictly increasing and satisfy the rule a^{x+y} = a^x * a^y. Logarithms reverse exponentials and turn multiplication into addition: log_a(x*y) = log_a(x) + log_a(y). These properties enable simplifying complex expressions." }, { "title": "Sequences and Summations", "example": "Sequence example: f(n) = 2n, gives 0, 2, 4, 6, .... Sum example: the sum of first n natural numbers: 1 + 2 + ... + n = n(n+1)/2.", "explanation": "A sequence is a function from natural numbers to real numbers describing ordered lists. Summation notation condenses repeated addition over sequences. Important summations include arithmetic series and geometric series." }, { "title": "Proof by Mathematical Induction", "example": "Prove that the sum of the first n odd numbers is n^2. Base: For n=1, sum=1=1^2. Induction: Assume true for n, prove for n+1: sum to n+1 = sum to n + (2(n+1)-1) = n^2 + 2n+1 = (n+1)^2.", "explanation": "Induction proves statements for all natural numbers by showing the base case is true and that truth for n implies truth for n+1. It's widely used for proving formulas, inequalities, and properties of sequences or algorithms." }, { "title": "Binary Trees: Definition and Traversal", "example": "A binary tree with root A, left child B, right child C. Preorder traversal visits A, B, C; inorder visits B, A, C; postorder visits B, C, A.", "explanation": "Binary trees are hierarchical data structures with nodes having up to two children. Depth measures distance from the root; height is maximum depth. Traversal methods explore nodes in different orders, useful for various algorithms." }, { "title": "Limit Concepts and Examples", "example": "lim_{x→∞} x^2 = ∞, lim_{x→∞} 1/x = 0, lim_{x→∞} (x-1)/(x+1) = 1.", "explanation": "Limits describe the behavior of functions as inputs grow large or approach specific values. They are foundational for defining continuity, derivatives, and integrals." }, { "title": "Derivative Definition and Basic Rules", "example": "If f(x)=x^3 then the derivative f'(x)=3x^2. Sum rule: (f+g)'=f'+g'. Product rule: (fg)'=f g' + f' g.", "explanation": "The derivative is the instantaneous rate of change of a function, defined via limits. Basic rules allow computing derivatives of sums and products, essential for calculus and algorithm analysis." }, { "title": "L'Hôpital's Rule for Evaluating Indeterminate Limits", "example": "lim_{x→∞} e^x / x^2 = ∞, found by differentiating numerator and denominator repeatedly.", "explanation": "When limits yield indeterminate forms like ∞/∞, L'Hôpital's Rule allows evaluation by differentiating numerator and denominator separately and then taking the limit." }, { "title": "Definition of an Algorithm", "example": "An algorithm to compute Fibonacci numbers using recursion is a sequence of steps that returns the nth Fibonacci number without ambiguity or creativity.", "explanation": "Algorithms are precise procedures for solving problems with clear, finite steps. They must define unambiguous instructions that a computer or human can follow." }, { "title": "Algorithm Correctness and Resource Use", "example": "Slow recursive Fibonacci algorithm is correct but inefficient. Fast iterative version uses linear time and constant space.", "explanation": "Correctness proves that algorithms produce the desired output. Resource use measures time and memory consumption, crucial for comparing and choosing algorithms." }, { "title": "Measuring Running Time: Input Size and Elementary Operations", "example": "Sorting 100 elements may take roughly 10,000 operations for a quadratic algorithm, while sorting 10,000 elements could take 100 million operations.", "explanation": "Input size quantifies the problem scale. Elementary operations are simple steps whose costs do not depend on input size. Running time counts these operations to analyze algorithm efficiency." }, { "title": "Growth Rates of Common Functions", "example": "Logarithmic growth: lg 1,000 ≈ 10; quadratic growth: 1,000^2 = 1,000,000; exponential growth: 2^{10} = 1,024.", "explanation": "Different functions grow at different rates, affecting algorithm performance drastically. Understanding these growth rates helps predict feasibility for large inputs." }, { "title": "Estimating Running Time from Loop Structures", "example": "A single loop from 1 to n with constant work inside has O(n) time. Nested loops two levels deep yield O(n^2) time.", "explanation": "Running time often corresponds to how many times loops execute and the work per iteration. Nested loops multiply these factors leading to polynomial time complexities." }] }
"""

class Concept(BaseModel):
    title: str
    examples: list[str]
    explanation: str
    
class OutputFormatConcept(BaseModel):
    concepts: list[Concept]
    
class Flashcard(BaseModel):
    question: str
    answer: str
    
class OutputFormatFlashcard(BaseModel):
    flashcards: list[Flashcard]
    
def chunk_text(text, max_tokens=300):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    words = text.split("\n")
    chunks = []
    current = ""
    for line in words:
        if len(tokenizer.encode(current + line)) < max_tokens:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def embed(texts):
    embeddings = [] 
    for text in texts:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        embeddings.append(response.data[0].embedding)
    print(embeddings)                          
    return embeddings

def ask_question(question, context):
        
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=
        [{        
         'role': "system",
         "content":"You are an expert in the relevant subject matter. Answer based on the provided context if relevant. If the context does not contain the answer, use general knowledge. Your answers should be clear and allow the reader to understand the answer to their question well. "
        },
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question:\n{question}"
            )
        }],
    )
    
    return response.output_text
    
def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    
    return text

def extract_text_from_pdf_pages(pdf_path, start_page=0, end_page=None):
    """
    Extract text from specific pages of a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        start_page (int): Starting page (0-indexed)
        end_page (int): Ending page (0-indexed), None for last page
        
    Returns:
        str: Extracted text from specified pages
    """
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if end_page is None:
                end_page = len(pdf_reader.pages)
            
            for page_num in range(start_page, min(end_page, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
                
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

    return text

def summarise_chunk(chunk):
    """    
    Args:
        chunk (str): Text chunk to summarise
        
    Returns:
        str: Summary of the text chunk
    """
  
    
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=
        [{        
         'role': "system",
         "content":r"""Break the entire text up into concepts. They can build on each other. 
         
         You are an expert tutor in the relevant subject. They should allow the reader to gain a strong understanding of the content. The concepts will be read chunk by chunk by the user in order to learn the content, so they need to be thorough and complete. The concepts should be clear, allowing the user to understand the content. If no example exists in the text, create two high quality, thorough examples. Ignore any course overviews, contents pages etc. Once again, the user should be able to read the concepts in order to fully learn and comprehend the content. The concepts should be independent from the source text, such that the source text is not needed to understand the topic - your summaries are a full replacement, to be augmented with the reader asking questions of an AI model.
         
         Math Formatting Rules:

        Any and all math expressions must be wrapped (this includes any powers, symbols, subscripts, and anything that is not plain text):

        Inline math: wrap in single dollar signs → $...$

        Block math: wrap in double dollar signs on separate lines:
        $$
        ...
        $$
        Do not escape dollar signs with backslashes.

        Do not use display environments like \[ or \begin{equation}.

        All math must be valid KaTeX syntax, renderable with remark-math and rehype-katex in a React Markdown component.

        If you include math and fail to wrap it correctly, the output is considered invalid."""
        },
        {
            "role": "user",
            "content": chunk
        }],
        text_format=OutputFormatConcept,       
    )
    
    return json.loads(response.output_text)
    
    #print(response.output_text)

def ask_gpt(question, context):
    """
    Ask a question to the GPT model with the provided context.
    
    Args:
        question (str): The question to ask
        context (str): Context to provide for answering the question
        
    Returns:
        str: Answer from the GPT model
    """
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=
        [{        
         'role': "system",
         "content":"You are an expert in the relevant subject matter. Your answers should be clear and allow the reader to understand the answer to their question well. You may include LaTeX-style math expressions in your responses. Use inline math between single dollar signs ie $...$ and display math between double dollar signs ie $$...$$. Only include expressions that are valid KaTeX syntax, as they will be rendered using remark-math and rehype-katex in a React Markdown component. Be reasonably concise, but not at the cost of thoroughness. Do NOT use backslashes for math, as they will not be rendered correctly. "
        },
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question:\n{question}"
            )
        }],
    )
    
    return response.output_text

def generate_flashcards(concept):
    """
    Generate flashcards for a given concept.
    
    Args:
        concept (Concept): The concept to generate flashcards for
        
    Returns:
        list[dict]: List of flashcards with question and answer
    """
    flashcards = ""
    
    examples = "\n".join(concept.examples)
    print(f"Generating flashcards for concept: {concept.title}")
    print(f"Concept Examples: {examples}")
    
    response=client.responses.parse(
        model="gpt-4.1-mini",
        input=
        [{        
         'role': "system",
         "content":"""You are an expert in the relevant subject matter. Generate multiple flashcards for the given concept. Each flashcard should have a question and an answer. The questions should be clear and allow the reader to understand the answer to their question well. Flashcards should only ask about one little idea, not multiple linked ideas.Remember to make sure that the basic concepts are covered in the flashcards - the user can just get rid of them later if they already know.
         Ensure that everything that is mentioned in the content is included in the flashcards. You will probably have to do at the very least three flashcards. Ensure that you also include things mentioned in the concept examples. Leave nothing out these, should be thorough.
         """
        },
        { 
            "role": "user",
            "content": concept.explanation + "\n\n" +
            f"Examples:\n{examples}\n\n"
        }],
        text_format=OutputFormatFlashcard,       
    )
    print(response.output_text)
    
    return response.output_parsed

# chunk = extract_text_from_pdf_pages(Path(r"api\uploads\SE284 2025 coursebook.pdf"), start_page=6, end_page=19)

# summarise_chunk(chunk)


# chunk_embeddings = embed(chunks)

# questions = [
#     "Explain the difference between domain and codomain ",
#     "What is a limit? Give an example. "
# ]

# outputs = []

#     # Embed the question
# for question in questions:
#     # Embed the question
#     question_embed = embed([question])[0]

#     # Find best matching chunks
#     similarities = cosine_similarity(np.array(question_embed).reshape(1, -1), np.array(chunk_embeddings))[0]
#     top_n = 3
#     top_indices = np.argsort(similarities)[-top_n:][::-1]
#     retrieved_context = "\n\n".join([chunks[i] for i in top_indices])
    
#     outputs.append(ask_question(question, retrieved_context))
