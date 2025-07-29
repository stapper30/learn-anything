import React from 'react';
import Link from 'next/link';

const Course = ({ id, title, setCourses }) => {
    return (
        <div className="bg-white flex rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border border-gray-200">
            <div className="space-y-2 w-3/4">
                <h3 className="text-xl font-semibold text-gray-800 leading-tight">{title}</h3>
                <Link href={`/concepts/` + id} className="text-blue-500 hover:underline">
                    View Concepts
                </Link>
            </div>
            <div>
                <button className="ml-auto bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors" onClick={() => {
                    fetch(`http://127.0.0.1:8000/courses/${id}/`, {
                        method: 'DELETE',
                        headers: {
                            "Authorization": `Bearer ${localStorage.getItem('token')}`,
                        }
                    }).then(response => {
                        
                        console.log("Course deleted successfully");
                        setCourses(prevCourses => prevCourses.filter(course => course.id !== id));
                    }).catch(error => {
                        console.error("Error deleting course:", error);
                        alert("Failed to delete course. Please try again.");
                    });
                }}>
                    Delete
                </button>

            </div>
        </div>
    );
};

export default Course;


