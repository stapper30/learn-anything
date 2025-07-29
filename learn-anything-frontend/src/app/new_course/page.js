"use client";

import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import FileForm from "@/components/FileForm";
import AuthChecker from "@/components/AuthChecker";

export default function NewCoursePage() {
    return (
        <AuthChecker>
            <FileForm />
        </AuthChecker>
    );
}