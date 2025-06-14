# 📄 Resume Chat Assistant

Upload your résumé and chat with it using AI! Powered by LangChain, Chroma, and Mistral-7B-Instruct.


## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + Tailwind CSS
- **Backend**: FastAPI + LangChain + Chroma
- **LLM**: mistralai/Mistral-7B-Instruct via Together API
- **Streaming**: SSE (Server-Sent Events)

## ✨ Features

- ✅ Upload and parse PDF résumé
- ✅ Chat with streaming answers from your résumé
- ✅ Personalized greeting (extracts name/email/phone)
- ✅ Role-fit score calculator (enter job description)
- ✅ Chat export (as .txt)
- ✅ Dark mode toggle
- ✅ Skill suggestions
- ✅ Secure: file sanitization + PDF-only validation

## 🚀 Getting Started

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/resume-chat-app
cd resume-chat-app
cd backend
pip install -r requirements.txt
# Add Together API Key
echo TOGETHER_API_KEY=your_key > .env
uvicorn main:app --reload
cd frontend
npm install
npm run dev
