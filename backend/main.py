from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import tempfile, os
from dotenv import load_dotenv

# 🔐 Load environment variables
load_dotenv()

# Load model & tokenizer locally
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Resume Chat API is running locally with FLAN-T5 🚀"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VECTOR_DB_PATH = "chroma_store"
vectorstore = None

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
        vectorstore = Chroma.from_documents(
            chunks, embedding, persist_directory=VECTOR_DB_PATH
        )

        os.remove(tmp_path)
        return {"message": "Resume uploaded and indexed successfully."}
    except Exception as e:
        print("[UPLOAD ERROR]", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        question = body.get("message", "").strip()

        if not question:
            return JSONResponse(status_code=400, content={"error": "Message required."})

        global vectorstore
        if vectorstore is None:
            embedding = HuggingFaceEmbeddings(
                model_name="intfloat/e5-small-v2",
                encode_kwargs={"normalize_embeddings": True}
            )
            vectorstore = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding)

        retriever = vectorstore.as_retriever()
        docs = retriever.get_relevant_documents(question)
        context = "\n\n".join([doc.page_content for doc in docs[:3]])

        if not context.strip():
            return JSONResponse(status_code=400, content={"error": "No relevant content found in résumé."})

        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        print("[DEBUG] Prompt:\n", prompt)

        def stream():
            try:
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=300,
                    do_sample=True,
                    temperature=0.7
                )
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                for char in generated_text:
                    yield f"data: {char}\n\n"
            except Exception as e:
                print("[stream error]", e)
                yield f"data: ERROR: {str(e)}\n\n"

        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        print("[/chat error]", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
