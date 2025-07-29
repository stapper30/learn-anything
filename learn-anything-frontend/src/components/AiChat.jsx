"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import ChatElement from './ChatElement';

export default function AiChat({ id, title, examples, explanation }) {
    const [answers, setAnswers] = React.useState([]);
    const [isLoading, setIsLoading] = React.useState(false);
    const [tempQuestion, setTempQuestion] = React.useState('');
    const detailsRef = useRef(null);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/answers/' + id, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        }).then(response => {
            if (!response.ok) {
                console.error("Failed to fetch answers");
            }
            return response.json();
        }).then(data => {
            setAnswers(data);
        }).catch(error => {
            console.error("Error fetching answers:", error);
        })
    }, []);

    const openDetails = () => {
        if (detailsRef.current) {
            detailsRef.current.open = true;
        }
    };

    const askQuestion = (question, concept, examples, id) => {
        setIsLoading(true);
        setTempQuestion(question);

        const context = concept + (examples ? '\n\nExamples:\n' + examples.join('\n') : '');

        fetch('http://127.0.0.1:8000/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({
                'question': question,
                'context': context,
                'concept_id': id,
            }),
        }).then(response => {
            console.log("Response received:", response);
            console.log("Response status:", response.status);
            if (!response.ok) {
                console.error("Failed to ask question");
            }
            return response.json();
        }).then(data => {
            console.log("Question answered successfully:", data);
            console.log([...answers, data[0]]);
            setAnswers([...answers, data[0]]);
            setIsLoading(false);
        }).catch(error => {
            console.log("Error asking question:", error);
            setIsLoading(false);
        });
    };

    return (
        <div>
            <details className="mt-4 bg-gray-100 p-4 rounded-md" ref={detailsRef}>
                <summary className="cursor-pointer">Ask Questions and View Chat</summary>
                {answers.length > 0 && (
                    <div className="p-4 rounded-md">
                        <div className="prose max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-900 prose-code:text-blue-600 prose-code:bg-blue-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono">
                            {answers.map((answer, idx) => (
                                <ChatElement key={idx} answer={answer} setAnswers={setAnswers} />
                            ))}
                            {isLoading && (
                                <div>
                                    <div className="bg-gray-100 w-auto p-2 rounded-md">
                                        <b className="text-gray-500">Question: </b>{tempQuestion}
                                    </div>
                                    <ReactMarkdown
                                        children={"Loading..."}
                                        className="p-2"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            <form className="flex w-full mt-2 px-4" onSubmit={(e) => {
                e.preventDefault();
                openDetails();
                askQuestion(e.target.question.value, explanation, examples, id);
                e.target.question.value = '';
            }
            }>
                <div className="w-14 flex-1 mr-4">
                    <input
                        type="text"
                        name="question"
                        id="question"
                        placeholder="Ask a question about this concept..."
                        className=" px-3 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                </div>
                <div className="w-36 flex-0">
                    {!isLoading && (<input type="submit" className="bg-blue-500 w-full text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500" value="Ask Question" />)}
                    {isLoading && <div className="mt-4 text-gray-500">Loading...</div>}
                </div>
            </form>
            </details>
        </div>
    )
}