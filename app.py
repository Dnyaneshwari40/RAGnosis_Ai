from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import mysql.connector
from dotenv import load_dotenv
import pypdf
import re
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq


app = Flask(__name__, template_folder="templates")
CORS(app)

UPLOAD_FOLDER = "document_store"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

dotenv_path = os.path.join("C:/Users/Diya Suryawanshi/OneDrive/Desktop/RAGNOSIS_AI", ".env")
load_dotenv(dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========== Database ==========
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="rag_nosis"
)

# ========== Embedding & Vector Store ==========
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_chunks")

latest_uploaded_file = None

# ========== PDF Utilities ==========
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            return "".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        print(f"[PDF ERROR] {str(e)}")
        return None

def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    text = clean_text(text)
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def store_chunks_in_chroma(chunks):
    collection.delete()  
    collection.add(
        embeddings=embedding_model.encode(chunks).tolist(),
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    print(f"[CHROMA] Stored {len(chunks)} chunks.")

def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results.get("documents", [[]])[0]

# ========== Groq LLM ==========
def get_latest_groq_model():
    import requests
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        response = requests.get("https://api.groq.com/v1/models", headers=headers)
        models = response.json().get("data", [])
        return models[0]['id'] if models else "llama3-8b-8192"
    except:
        return "llama3-8b-8192"

llm = ChatGroq(model_name=get_latest_groq_model(), groq_api_key=GROQ_API_KEY)

def get_chatbot_answer(question):
    chunks = retrieve_relevant_chunks(question, top_k=5)
    if not chunks:
        return "No relevant information found."

    context = "\n\n".join(chunks)
    prompt = f"Answer the following based on the context:\n{context}\n\nQuestion: {question}\nAnswer:"
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"[LLM ERROR] {str(e)}")
        return "Failed to generate response."

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
    return jsonify({"error": "Invalid credentials"}), 400

@app.route("/auth/mainpage")
def mainpage():
    return render_template("mainpage.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    global latest_uploaded_file
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    latest_uploaded_file = file_path

    text = extract_text_from_pdf(file_path)
    if not text:
        return jsonify({"error": "Failed to extract PDF text"}), 500

    chunks = chunk_text(text)
    store_chunks_in_chroma(chunks)

    return jsonify({"message": f"File '{filename}' processed successfully"})

@app.route("/auth/chat", methods=["GET"])
def chat_page():
    return render_template("chat.html")

@app.route("/auth/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    question = data.get("message", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    answer = get_chatbot_answer(question)
    return jsonify({"response": answer})


if __name__ == "__main__":
    app.run(debug=True)
