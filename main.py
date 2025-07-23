from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import mysql.connector
import requests
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from dotenv import load_dotenv

app = Flask(__name__, template_folder="templates")
CORS(app)
# database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  
    database="rag_nosis"
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/auth/register', methods=["GET"])
def register_form():
    return render_template('register.html')

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    fullname = data.get('fullname')
    username = data.get('username')
    password = data.get('password')

    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (fullname, username, password) VALUES (%s, %s, %s)",
                       (fullname, username, password))
        db.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400


@app.route("/auth/login", methods=["GET"])
def login_form():
    return render_template('login.html')

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and user[0] == password:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 400

# env load
dotenv_path = os.path.join("C:/Users/Dnyanehswari/OneDrive/Documents/RAGNOSIS", ".env")
load_dotenv(dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# upload folder
UPLOAD_FOLDER = "C:/Users/Dnyanehswari/OneDrive/Documents/RAGNOSIS/document_store"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
latest_uploaded_file = None

def get_latest_groq_model():
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    try:
        response = requests.get("https://api.groq.com/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            if models:
                return models[0]['id']
    except Exception as e:
        print("Error fetching Groq models:", str(e))
    return "llama3-8b-8192"

latest_model = get_latest_groq_model()
print(f" Using Groq Model: {latest_model}")

llm = ChatGroq(model_name=latest_model, groq_api_key=GROQ_API_KEY)

def extract_text_from_pdf(pdf_filename):
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text = "\n".join([doc.page_content for doc in documents])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {pdf_filename}: {str(e)}")
        return None

def generate_summary(text):
    if not text:
        return "No text available for summarization."

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)

    full_summary = ""
    for chunk in chunks:
        summary_prompt = f"Summarize the following text:\n{chunk}\nSummary:"
        try:
            response = llm.invoke(summary_prompt)
            full_summary += response.content.strip() + "\n\n"
        except Exception as e:
            print(f"Error summarizing text: {str(e)}")
            return "Error generating summary."

    return full_summary.strip()


@app.route("/auth/mainpage")
def mainpage():
    return render_template("mainpage.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    global latest_uploaded_file

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        latest_uploaded_file = filename
        print(f"File uploaded: {filename}")

        return jsonify({"message": "File uploaded successfully", "filename": filename})

@app.route("/generate_summary", methods=["POST"])
def generate_summary_api():
    global latest_uploaded_file
    if not latest_uploaded_file:
        return jsonify({"summary": "No file uploaded yet. Please upload a file first."}), 400

    print(f"Generating summary for: {latest_uploaded_file}")

    text = extract_text_from_pdf(latest_uploaded_file)
    if not text:
        return jsonify({"summary": "Error extracting text from PDF."}), 500

    summary = generate_summary(text)
    print(f"Summary Generated for: {latest_uploaded_file}")

    return jsonify({"summary": summary, "filename": latest_uploaded_file})

latest_uploaded_file = "SAMPLE4.pdf"

def get_chatbot_answer(question):
    global latest_uploaded_file
    if not latest_uploaded_file:
        return "Please upload a file first."

    text = extract_text_from_pdf(latest_uploaded_file)
    if not text:
        return "Error extracting text from PDF."
        
    prompt = f"Answer the following question based on the provided document:\nDocument:\n{text}\n\nQuestion: {question}\nAnswer:"
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return "Error generating answer."

@app.route('/auth/chat', methods=['GET'])
def chat_page():
    return render_template("chat.html")  

@app.route('/auth/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()  
        if not data or "message" not in data:
            return jsonify({"error": "No message received"}), 400  
        
        question = data["message"]
        answer = get_chatbot_answer(question)  

        print(f"Question: {question}")
        print(f"Answer: {answer}")

        return jsonify({"response": answer})  
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    print("Extracting text from:", latest_uploaded_file)
    print(extract_text_from_pdf(latest_uploaded_file))
    app.run(debug=True)