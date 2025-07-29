'use client';

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import Login from "@/components/Login";
import FileForm from "@/components/FileForm";
import { useRouter } from "next/navigation";
import AuthChecker from "@/components/AuthChecker";
import Link from "next/link";
import Image from "next/image";
import Course from "@/components/Course";

export default function Home() {
  const { user, setUser, clearUser } = useAuth();
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/courses/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      }
    }).then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch courses");
      }
      return response.json();
    }).then(data => {
      console.log("Courses fetched successfully:", data);
      setCourses(data);
    }).catch(error => {
      console.error("Error fetching courses:", error);
    });
  }, []);

  return (
    <AuthChecker>
      <div className="mt-12 flex items-center justify-center">
        <div className="max-w-md w-full">
          <div className="flex justify-center items-center">
            <Image src="/icon.png" alt="Logo" width={100} height={100} className="block" />
            <h1 className="text-4xl font-semibold text-center">Learn Anything</h1>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md mt-6">
            <h1 className="text-xl font-semibold mb-4 text-center">Your Courses</h1>
            {courses.length > 0 ? (
              <ul className="space-y-4">
                {courses.map((course) => (
                  <li key={course.id}>
                    <Course id={course.id} title={course.title} setCourses={setCourses} />
                  </li>
                ))}
              </ul>
            ) : (
                <p className="text-center">No courses yet - time to lock in!</p>
            )}
            <Link href="/new_course/" className="text-center text-xl text-white font-bold rounded-lg bg-blue-500 shadow-md hover:shadow-lg hover:bg-blue-600 block transition-shadow duration-300 p-6 mt-4 border border-gray-200">
               Add New Course
            </Link>
          </div>
        </div>
      </div>
    </AuthChecker>
  );
}
