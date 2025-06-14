# 📄 Resume Chat Assistant

An AI-powered résumé assistant that lets users upload a PDF resume, chat with it, and assess how well it matches a job description.


---

## 🚀 Features

- 📄 Upload your PDF résumé
- 💬 Chat with your résumé using natural language
- 📊 Role-fit score calculator (0–100%)
- 🎯 Personalized greeting and information extraction (name, email, phone)
- 🌗 Dark mode toggle
- 🧠 Skill suggestions based on content
- 📥 Download full Q&A chat history
- ✅ Resume summarization (optional)
- 🛡️ File type validation, streaming responses (SSE)

---

## 🧱 Architecture

```
📦 root/
├── frontend/ (Next.js 14 + Tailwind CSS)
│   └── app/page.tsx     ← main UI
├── backend/ (FastAPI + LangChain)
│   └── main.py          ← upload, chat, score endpoints
├── chroma_store/        ← Vector DB for local embeddings
├── .env                 ← API keys and config
├── README.md
```

---

## ⚙️ Tech Stack

| Layer         | Stack                                 |
|--------------|----------------------------------------|
| Front-end     | Next.js 14, Tailwind CSS, React Icons |
| Back-end      | FastAPI, LangChain, Chroma DB         |
| LLM API       | Together API (Mistral-7B-Instruct)     |
| Embeddings    | `intfloat/e5-small-v2` (Hugging Face) |
| Streaming     | Server-Sent Events (SSE)              |

---

## 🧪 Setup Instructions

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/resume-chat.git
cd resume-chat
```

---

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file:

```
TOGETHER_API_KEY=your_api_key_here
```

Run the FastAPI server:

```bash
uvicorn main:app --reload
```

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

By default, frontend runs on `http://localhost:3000` and backend on `http://localhost:8000`.

---

## 🎥 Walk-through

> [📹 Loom Walkthrough](https://www.loom.com/share/12d2e4dcf95e4e86a06050480ffee112?sid=15005e6e-bad6-40b6-b97e-913c44aa73aa) ← Replace with your recording

---

## 🔎 Known Trade-offs / Issues

| Trade-off | Description |
|----------|-------------|
| ❗ Resource Usage | Mistral-7B-Instruct runs via Together API; local inference not ideal on <16GB RAM. |
| 📄 Resume PDF | Extraction quality depends on document formatting (tabular or scanned PDFs may fail). |
| 🎯 Role-fit Accuracy | Scoring is approximate and prompt-based, not learned classification. |
| ⚠️ SSE Limit | Some browsers may mishandle large streamed payloads—tested in Chrome/Edge. |
| 🌐 CORS | Ensure correct `localhost` port is whitelisted in FastAPI CORS config. |

---

## ✅ Future Enhancements

- 🎙️ Voice-to-text queries
- 📍 Named entity highlighting
- 📂 Multiple resume uploads
- 🧾 Export as formatted PDF summary

---

## 📬 Contact

Made with ❤️ by [Goutham Mathi](https://github.com/Gouthammathi)  
📧 goouthamm@gmail.com
