from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os, tempfile, openai

# ✅ Load .env with TOGETHER_API_KEY
load_dotenv()
openai.api_key = os.getenv("TOGETHER_API_KEY")
openai.api_base = "https://api.together.xyz/v1"

# 🚀 FastAPI app instance
app = FastAPI()

# 🔐 Allow CORS (adjust origin for your frontend domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 ChromaDB setup
VECTOR_DB_PATH = "chroma_store"
vectorstore = None


@app.get("/")
def root():
    return {"message": "🧠 Resume Chat API is running!"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        embedding = HuggingFaceEmbeddings(
            model_name="intfloat/e5-small-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

        global vectorstore
        vectorstore = Chroma.from_documents(chunks, embedding, persist_directory=VECTOR_DB_PATH)

        os.remove(tmp_path)
        return {"message": "✅ Resume uploaded and indexed successfully."}

    except Exception as e:
        print("[/upload error]", e)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        question = body.get("message", "").strip()

        if not question:
            return JSONResponse(status_code=400, content={"error": "Question is required."})

        global vectorstore
        if vectorstore is None:
            embedding = HuggingFaceEmbeddings(
                model_name="intfloat/e5-small-v2",
                encode_kwargs={"normalize_embeddings": True}
            )
            vectorstore = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding)

        retriever = vectorstore.as_retriever()
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs[:2]])

        # 🧠 Construct prompt for Mistral
        prompt = f"[INST] Use the following resume to answer the question.\n\n{context}\n\nQuestion: {question} [/INST]"

        def stream():
            try:
                response = openai.ChatCompletion.create(
                    model="mistralai/Mistral-7B-Instruct-v0.2",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    temperature=0.7,
                    max_tokens=300
                )
                for chunk in response:
                    content = chunk.choices[0].delta.get("content", "")
                    if content:
                        yield f"data: {content}\n\n"
            except Exception as e:
                print("[streaming error]", e)
                yield f"data: ERROR: {str(e)}\n\n"

        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        print("[/chat error]", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
