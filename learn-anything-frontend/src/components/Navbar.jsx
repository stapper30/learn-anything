"use client";

import { useAuth } from "@/context/AuthContext";

import Link from "next/link";
import { useRouter } from "next/navigation";
import AuthChecker from "@/components/AuthChecker";
import Image from "next/image";

export default function Navbar() {
    const { user, setUser, clearUser } = useAuth();
    const router = useRouter();
    console.log("User in Navbar:", user);
    if (!user.user_id) {
        return null; // Don't render Navbar if user is not authenticated
    }
    return (
        <div className="flex items-center justify-center p-4 bg-gray-200 text-black">
            <div className="flex items-center justify-between space-x-4 w-full max-w-6xl px-8">
                <Link href="/" className=" hover:underline block">
                    My Courses
                </Link>
                <div>
                    <Image rel="icon" src="/icon.png" alt="Logo" width={40} height={40} className="inline-block mr-2" />
                    <span>Welcome to Learn Anything, {user.name}!</span>
                </div>
                <button onClick={() => {
                    localStorage.removeItem('token');
                    clearUser();
                    console.log("Token cleared");
                    router.push("/login");
                }} className="bg-red-500 text-white float-right px-4 py-2 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500">
                    Logout
                </button>
            </div>
        </div>
    );
}