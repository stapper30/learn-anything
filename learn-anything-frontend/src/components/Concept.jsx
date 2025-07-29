import React, { useRef } from 'react';
import AiChat from './AiChat';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import Popup from './Popup';


const Concept = ({ id, title, examples, explanation }) => {

    const arrowRef = useRef(null);
    const [isOpen, setIsOpen] = React.useState(false);
    const [loadingFlashcards, setLoadingFlashcards] = React.useState(false);
    const [flashcards, setFlashcards] = React.useState([]);

    const toggleArrow = () => {
        if (arrowRef.current) {
            arrowRef.current.textContent = !arrowRef.current.open ? '▼' : '▶';
            arrowRef.current.open = !arrowRef.current.open;
        }
    };

    return (
        <details className="concept bg-white rounded-lg shadow-md p-4 mb-6 border border-gray-200 w-full" id={id}>
            <summary className="flex items-center cursor-pointer" onClick={toggleArrow}>
                <h2 className="text-xl font-bold text-gray-800"><span ref={arrowRef}>▶</span> {title}</h2>
                <div className="ml-auto">
                    <button className="ml-auto bg-blue-500 text-white px-4 mr-2 py-2 h-12 rounded-md hover:bg-blue-600 transition-colors" onClick={() => {
                        setIsOpen(true);
                        setLoadingFlashcards(true);
                        fetch(`http://127.0.0.1:8000/concepts/${id}/generate_flashcards/`, {
                            method: 'GET',
                            headers: {
                                "Authorization": `Bearer ${localStorage.getItem('token')}`,
                            }
                        }).then(response => {
                            if (!response.ok) {
                                throw new Error("Failed to generate flashcards");
                            }
                            return response.json();
                        }).then(data => {
                            console.log("Flashcards generated successfully:", data);
                            setFlashcards(data.flashcards.flashcards);
                            setLoadingFlashcards(false);

                        }).catch(error => {
                            console.error("Error generating flashcards:", error);
                            alert("Failed to generate flashcards. Please try again.");
                            setLoadingFlashcards(false);
                            setIsOpen(false);
                        });
                    }}>
                        Create Anki
                    </button>
                    <button className="ml-auto bg-red-500 text-white px-4 py-2 h-12 rounded-md hover:bg-red-600 transition-colors" onClick={() => {
                        fetch(`http://127.0.0.1:8000/concepts/${id}/`, {
                            method: 'DELETE',
                            headers: {
                                "Authorization": `Bearer ${localStorage.getItem('token')}`,
                            }
                        }).then(response => {
                            if (!response.ok) {
                                throw new Error("Failed to delete concept");
                            }
                            console.log("Concept deleted successfully");
                            setConcepts(prevConcepts =>
                                prevConcepts.filter(concept => concept.id !== id)
                            );
                        }).catch(error => {
                            console.error("Error deleting concept:", error);
                            alert("Failed to delete concept. Please try again.");
                        });
                    }}>
                        Delete
                    </button>
                    <Popup isOpen={isOpen} onClose={() => setIsOpen(false)}>
                        <h2 className="text-xl font-bold mb-4">Flashcards for {title}</h2>
                        <p>Copy and paste the text as is into a .txt file, and import that into Anki</p>
                        <div className="bg-gray-100 p-4 rounded-md w-full">
                            {loadingFlashcards ? (
                                <p>Loading flashcards...</p>
                            ) : (
                                <div>
                                    {flashcards.map((card, index) => (
                                        <div key={index} className="mb-2">
                                            "{card.question}","{card.answer}"
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </Popup>
                </div>
            </summary>
            <div className="explanation mb-6">
                <ReactMarkdown
                    children={explanation}
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                    className="p-2"
                />
            </div>
            <div className="examples">
                {examples && examples !== ":{" ? <h3 className="text-lg font-semibold text-gray-700 mb-3">Examples</h3> : null}
                <div className="space-y-4">
                    {examples && examples !== ":{" && examples.map((example, index) => (
                        <div key={index} className="bg-gray-50 rounded-md p-4 border-l-4 border-blue-400">
                            <ReactMarkdown
                                key={index}
                                children={example}
                                remarkPlugins={[remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                                className="p-2"
                            />
                        </div>
                    ))}
                </div>
            </div>
            <AiChat id={id} title={title} explanation={explanation} examples={examples} />
        </details>
    )
}

export default Concept;