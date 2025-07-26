from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import mysql.connector
from dotenv import load_dotenv
import pypdf
import re
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
import requests 


app = Flask(__name__, template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "document_store"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 
dotenv_path = os.path.join("C:/Users/Diya Suryawanshi/OneDrive/Desktop/RAGNOSIS_AI", ".env")
load_dotenv(dotenv_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found. Please ensure it's set in your .env file or as a system environment variable.")
  

# ========== Database ==========
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Riddhi@1804",
    database="rag_nosis"
)

# ========== Embedding & Vector Store ==========
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_chunks")

latest_uploaded_file = None

# ========== PDF Utilities ==========
def extract_text_from_pdf(pdf_path):
    print(f"[PDF_UTIL] Attempting to extract text from: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text_content = "".join([page.extract_text() or "" for page in reader.pages])
            if not text_content.strip():
                print(f"[PDF ERROR] Extracted text is empty or only whitespace from '{os.path.basename(pdf_path)}'")
                return None
            print(f"[PDF_UTIL] Successfully extracted {len(text_content)} characters.")
            return text_content
    except Exception as e:
        print(f"[PDF ERROR] Failed to extract text from '{os.path.basename(pdf_path)}': {str(e)}")
        return None

def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    text = clean_text(text)
    if not text:
        print("[CHUNK_UTIL] No text to chunk after cleaning.")
        return []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    print(f"[CHUNK_UTIL] Created {len(chunks)} chunks.")
    return chunks

def store_chunks_in_chroma(chunks):
    try:
        
        collection.delete(ids=collection.get()['ids']) 
        print("[CHROMA] Cleared existing chunks in collection.")
    except Exception as e:
        print(f"[CHROMA ERROR] Failed to clear existing chunks: {str(e)}")
        
    if chunks: 
        new_ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(
            embeddings=embedding_model.encode(chunks).tolist(),
            documents=chunks,
            ids=new_ids
        )
        print(f"[CHROMA] Stored {len(chunks)} new chunks.")
    else:
        print("[CHROMA] No chunks to store.")

def retrieve_relevant_chunks(query, top_k=5):
    if collection.count() == 0:
        print("[CHROMA] No documents in collection to query. Collection is empty.")
        return []
    try:
        query_embedding = embedding_model.encode(query).tolist()
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=['documents'])
        retrieved_docs = results.get("documents", [[]])[0]
        print(f"[CHROMA] Retrieved {len(retrieved_docs)} relevant chunks for query.")
        return retrieved_docs
    except Exception as e:
        print(f"[CHROMA ERROR] Failed to retrieve chunks for query '{query}': {str(e)}")
        return []

# ========== Groq LLM ==========

llm = None
if GROQ_API_KEY:
    try:
        
        llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=GROQ_API_KEY)
        print("[LLM] ChatGroq initialized successfully with 'llama3-8b-8192'.")
    except Exception as e:
        print(f"[LLM ERROR] Error initializing ChatGroq: {e}. Chatbot functionality may be limited.")
else:
    print("Warning: GROQ_API_KEY is missing. ChatGroq LLM will not be functional.")


def get_chatbot_answer(question):
    if not llm:
        return "Chatbot not initialized. Please ensure GROQ_API_KEY is set and LLM initialized correctly."

    chunks = retrieve_relevant_chunks(question, top_k=5)
    if not chunks:
        return "No relevant information found in the uploaded document. Please upload a PDF first."

    context = "\n\n".join(chunks)
    prompt = f"Answer the following based on the context:\n{context}\n\nQuestion: {question}\nAnswer:"
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"[LLM ERROR] Failed to generate response from LLM: {str(e)}")
        return "Failed to generate response due to an internal LLM error."

# ========== Routes ==========

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auth/register", methods=["GET"])
def register_form():
    return render_template("register.html")

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (fullname, username, password) VALUES (%s, %s, %s)",
                       (data['fullname'], data['username'], data['password']))
        db.commit()
        return jsonify({"message": "Registration successful"}), 201
    except mysql.connector.Error as err:
        print(f"[DB ERROR] Registration failed: {str(err)}")
        return jsonify({"error": str(err)}), 400

@app.route("/auth/login", methods=["GET"])
def login_form():
    return render_template("login.html")

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (data['username'],))
    user = cursor.fetchone()
    if user and user[0] == data['password']:
        return jsonify({"message": "Login successful"}), 200
    print("[AUTH] Invalid login credentials.")
    return jsonify({"error": "Invalid credentials"}), 400

@app.route("/auth/mainpage")
def mainpage():
    return render_template("mainpage.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    global latest_uploaded_file
    print("[UPLOAD] Received upload request.")
    file = request.files.get("file")

    if not file or file.filename == "":
        print("[UPLOAD ERROR] No file selected or empty filename.")
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    print(f"[UPLOAD] Attempting to save file to: {file_path}")

    try:
        file.save(file_path)
        print(f"[UPLOAD] File '{filename}' saved successfully.")
    except Exception as e:
        print(f"[UPLOAD ERROR] Failed to save file '{filename}': {str(e)}")
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    latest_uploaded_file = file_path

    print(f"[UPLOAD] Extracting text from PDF: {filename}")
    text = extract_text_from_pdf(file_path)
    if not text:
        print(f"[UPLOAD ERROR] Failed to extract text from {filename}. File might be empty, corrupted, or password-protected.")
        return jsonify({"error": "Failed to extract text from PDF. It might be empty, corrupted, or password-protected."}), 500

    print("[UPLOAD] Chunking text...")
    chunks = chunk_text(text)
    if not chunks:
        print(f"[UPLOAD ERROR] No chunks generated for {filename}. Extracted text might be too short or clean_text removed everything.")
        return jsonify({"error": "No meaningful content found in the PDF to process."}), 500

    print("[UPLOAD] Storing chunks in ChromaDB...")
    store_chunks_in_chroma(chunks)
    print(f"[UPLOAD] File '{filename}' processed successfully and chunks stored.")

    return jsonify({"message": f"File '{filename}' processed successfully", "filename": filename})

@app.route("/auth/chat", methods=["GET"])
def chat_page():
    return render_template("chat.html")

@app.route("/auth/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    question = data.get("message", "")
    if not question:
        print("[CHAT] No question provided.")
        return jsonify({"error": "No question provided"}), 400

    print(f"[CHAT] Received question: '{question}'")
    answer = get_chatbot_answer(question)
    print(f"[CHAT] Sending answer: '{answer[:50]}...'") 
    return jsonify({"response": answer})

@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    data = request.get_json()
    filename = data.get("filename")
    print(f"[SUMMARY] Received request to summarize: {filename}")

    if not filename:
        print("[SUMMARY ERROR] No filename provided for summarization.")
        return jsonify({"error": "No filename provided for summarization."}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        print(f"[SUMMARY ERROR] File '{filename}' not found on server at: {file_path}")
        return jsonify({"error": f"File '{filename}' not found on server."}), 404

    text = extract_text_from_pdf(file_path)
    if not text:
        print(f"[SUMMARY ERROR] Failed to extract text for summarization from {filename}.")
        return jsonify({"error": "Failed to extract text from PDF for summarization."}), 500

    if not llm:
        print("[SUMMARY ERROR] LLM not initialized. Cannot generate summary.")
        return jsonify({"error": "LLM not initialized. Cannot generate summary."}), 500

    summary_prompt = f"Summarize the following document concisely. Focus on key information, main ideas, and important findings:\n\n{text}\n\nSummary:"
    print("[SUMMARY] Sending text to LLM for summarization.")
    try:
        response = llm.invoke(summary_prompt)
        summary = response.content.strip()
        print("[SUMMARY] Summary generated successfully.")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        print(f"[SUMMARY ERROR] Failed to generate summary from LLM: {str(e)}")
        return jsonify({"error": "Failed to generate summary due to an internal LLM error."}), 500


if __name__ == "__main__":
    app.run(debug=True)