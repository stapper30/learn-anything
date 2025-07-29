"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

const FileForm = () => {
    const router = useRouter();
    const [selectedFile, setSelectedFile] = useState(null);
    const [title, setTitle] = useState('');
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'application/pdf') {
            setSelectedFile(file);
        } else {
            alert('Please select a PDF file');
            event.target.value = '';
        }
    };

    const handleTitleChange = (event) => {
        setTitle(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        setLoading(true);
        if (!selectedFile) {
            alert('Please select a PDF file');
            return;
        }
        if (!title.trim()) {
            alert('Please enter a title');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('title', title);

        fetch('http://127.0.0.1:8000/create_course/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload successful:', data);
            router.push('/'); // Redirect to home page after successful upload
        })
        .catch(error => {
            console.error('Upload failed:', error);
            setLoading(false);
            router.push('/'); // Redirect to home page after successful upload
        });
        
        console.log('Selected PDF:', selectedFile, 'Title:', title);
    };

    return (
        <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Create a New Course</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                        Course Name:
                    </label>
                    <input
                        id="title"
                        type="text"
                        value={title}
                        onChange={handleTitleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter course name"
                        required
                    />
                </div>

                <div>
                    <label htmlFor="pdf-upload" className="block text-sm font-medium text-gray-700 mb-1">
                        Upload Slides/Coursebook PDF:
                    </label>
                    <input
                        id="pdf-upload"
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        required
                    />
                </div>
                
                {selectedFile && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                        <p className="text-sm text-green-700">
                            <span className="font-medium">Selected:</span> {selectedFile.name}
                        </p>
                    </div>
                )}
                
                <button 
                    type="submit"
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 font-medium"
                >
                    {loading ? 'Creating new course (takes a while)...' : 'Create Course'}
                </button>
            </form>
        </div>
    );
};

export default FileForm;