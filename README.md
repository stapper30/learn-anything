# Learn Anything

**Learn Anything** is an AI-enabled learning platform designed to help users grasp technical concepts through visual breakdowns, structured explanations, and interactive content. This project uses a FastAPI + PostgreSQL backend and a React/Next.js frontend styled with Tailwind CSS.

> ⚠️ This project is not currently deployed. It is shared as a codebase only.

---
Demo Video:
https://github.com/user-attachments/assets/576a6d0a-ddb6-4749-90b7-514ca93b96a9

---

## 🧠 How It Works 
Upload your course book or your slides for your course. The program extracts the text and uses the OpenAI API to break the content down into chunkable concepts with examples and explanations. You can then interact with these concepts and ask questions to further your understanding.

This is intended to be an effective replacement for coursebooks, which are often incomplete and uninteractive.

This project aims to effectively answer two questions: What if I could just digest this course chunk by chunk? And if only I could ask my coursebook questions! 

---

## 🏗 Tech Stack

### Frontend
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **Usage**: Serves static pages and UI only (no API routes)

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Purpose**: Handles all data processing and API requests

---

## 🚧 Setup

This project is **not currently packaged for easy setup**. It assumes:
- Familiarity with Python + FastAPI
- PostgreSQL instance available
- Node.js (18+) and package manager (`npm` or `pnpm`) installed

If you're comfortable configuring the backend and frontend manually, the code is available for exploration.

---

## 📦 Installation (Manual)

**Backend**
1. Create and activate a Python virtual environment.
2. Install dependencies and configure database.py with your postgres settings
3. Start the FastAPI server.

**Frontend**
1. Install dependencies with `npm install`.
2. Run `npm run dev` to launch the Next.js dev server.

---

## 📄 License

MIT License – See `LICENSE` file for details.
