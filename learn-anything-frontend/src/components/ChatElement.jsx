import React, {useRef} from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function ChatElement({ answer, setAnswers }) {
    const arrowRef = useRef(null);

    const toggleArrow = () => {
        if (arrowRef.current) {
            arrowRef.current.textContent = !arrowRef.current.open ? '▼ ' : '▶ ';
            arrowRef.current.open = !arrowRef.current.open;
        }
    };

    return (
        <details>
            <summary className="bg-white w-auto flex items-center my-2 p-2 rounded-md cursor-pointer" onClick={toggleArrow}>
                <div>
                    <span ref={arrowRef}>▶ </span><b className="text-gray-500">Question: </b>{answer.question}</div>
                <button className="ml-auto bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors" onClick={() => {
                    fetch(`http://127.0.0.1:8000/answers/${answer.id}/`, {
                        method: 'DELETE',
                        headers: {
                            "Authorization": `Bearer ${localStorage.getItem('token')}`,
                        }
                    }).then(response => {
                        if (!response.ok) {
                            throw new Error("Failed to delete answer");
                        }
                        console.log("Answer deleted successfully");
                        setAnswers(prevAnswers => prevAnswers.filter(a => a.id !== answer.id));
                    }).catch(error => {
                        console.error("Error deleting answer:", error);
                        alert("Failed to delete answer. Please try again.");
                    });
                }}>
                    Delete
                </button>
            </summary>
            <ReactMarkdown
                children={answer.text}
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
                className="p-2"
            />
        </details>
    );
}