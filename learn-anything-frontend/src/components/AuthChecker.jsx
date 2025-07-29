'use client';

import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

export default function AuthChecker({ children }) {
    const { setUser, clearUser } = useAuth();
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (!token) {
            console.log("No token found, redirecting to login");
            clearUser();
            router.replace("/login");
            return;
        }

        fetch("http://127.0.0.1:8000/users/me/", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
            .then((res) => {
                if (!res.ok) {
                    throw new Error("Invalid token");
                }
                return res.json();
            })
            .then((data) => {
                setUser({
                    username: data.username,
                    name: data.name,
                    user_id: data.id,
                });
                setLoading(false);
            })
            .catch((err) => {
                console.error("Auth error:", err);
                clearUser();
                localStorage.removeItem("token");
                router.replace("/login");
            });
    }, []);

    if (loading) {
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    return <>{children}</>;
}
