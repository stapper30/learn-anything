"use client";
import { useState, useEffect, use } from 'react';

import Concept from "@/components/Concept";
import SideNav from "@/components/SideNav";
import Test from "@/components/Test";
import { useAuth } from "@/context/AuthContext";
import AuthChecker from "@/components/AuthChecker";

export default function ConceptsPage({ params }) {
    const { course_id: courseId } = use(params);
    // Fetch concepts data
    // Replace with your actual API endpoint
    const [concepts, setConcepts] = useState({
        concepts: [{
            title: "",
            examples: [],
            explanation: "",
        }]
    });
    const [title, setTitle] = useState("");

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchConcepts = async () => {
            fetch('http://127.0.0.1:8000/concepts/' + courseId, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                }
            }
            ).then(response => {
                if (!response.ok) {
                    throw new Error("Failed to fetch concepts");
                }
                return response.json();
            }).then(data => {
                setConcepts({ concepts: data });
                console.log("Concepts fetched successfully:", data);
                setLoading(false);
            }).catch(error => {
                console.error("Error fetching concepts:", error);
                setLoading(false);
            })
        }
        fetchConcepts();
    }, []);

    useEffect(() => {
        fetch('http://127.0.0.1:8000/courses/' + courseId, {
            method: 'GET',
            headers: {
                "Authorization": `Bearer ${localStorage.getItem('token')}`,
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch course details");
            }
            return response.json();
        }).then(data => {
            console.log("Course details fetched successfully:", data);
            setTitle(data.title);
        }).catch(error => {
            console.error("Error fetching course details:", error);
            alert("Failed to fetch course details. Please try again.");
        })
    }, []);
    console.log("Concepts data:", concepts);
    console.log("Loading state:", loading);
    if (loading) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }
    if (!concepts || concepts.concepts.length === 0) {
        return <div className="flex items-center justify-center min-h-screen">No concepts found.</div>;
    }


    return (
        <AuthChecker>
            <div>
                <a href="#top" className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors">
                    Back to Top
                </a>
            </div>
            <div className="container mx-auto p-4 max-w-6xl">
                <div className="flex gap-6">
                    <SideNav concepts={concepts} />

                    <div className="w-3/4">
                        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
                            <h1 className="text-3xl font-bold mb-6">Concepts {title ? ("- " + title) : null}</h1>
                            <p className="mb-6 text-gray-700">
                                Work your way through each concept. When you've understood each one, create some Anki flashcards to solidify your knowledge. Have fun!
                            </p>
                        </div>
                        {concepts.concepts.map((concept) => (
                            <Concept
                                id={concept.id}
                                key={concept.id}
                                title={concept.title}
                                examples={concept.examples}
                                explanation={concept.explanation}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </AuthChecker>
    );
}
