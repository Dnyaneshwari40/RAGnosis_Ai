from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Load API Key from .env
dotenv_path = os.path.join("C:/Users/Dnyanehswari/OneDrive/Documents/RAGNOSIS", ".env")
load_dotenv(dotenv_path=dotenv_path)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq model
# ✅ Auto-select latest available model
def get_latest_model():
    import requests
    url = "https://console.groq.com/api/models"  # Replace with correct API if needed

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        response.raise_for_status()
        models = response.json().get("models", [])
        return models[0] if models else "llama3-8b-8192"  # Default model if no list
    except Exception as e:
        print(f"⚠️ Error fetching latest model: {e}")
        return "llama3-8b-8192"  # Use a default model

latest_model = get_latest_model()
print(f"✅ Using Model: {latest_model}")

llm = ChatGroq(model_name=latest_model, groq_api_key=GROQ_API_KEY)

UPLOAD_FOLDER = "C:/Users/Dnyanehswari/OneDrive/Documents/RAGNOSIS/document_store"
pdf_filename = "SAMPLE4.pdf"  # Ensure this file exists

# ✅ Global cache for PDF text
cached_pdf_text = None

# 🔥 Optimized PDF Text Extraction
def extract_text_from_pdf():
    global cached_pdf_text
    if cached_pdf_text:
        print("✅ Using Cached PDF Text")
        return cached_pdf_text  # Return from cache

    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
    print("📂 Loading PDF from:", pdf_path)

    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        text = "\n".join([doc.page_content for doc in documents])

        cached_pdf_text = text.strip()  # Cache the text
        print("📜 Extracted Text Cached!")
        return cached_pdf_text
    except Exception as e:
        print(f"❌ Error extracting text from {pdf_filename}: {str(e)}")
        return None

# 🔥 Optimized Chatbot Answer Retrieval
def get_chatbot_answer(question):
    pdf_text = extract_text_from_pdf()

    if pdf_text:
        limited_text = pdf_text[:2000]  # ✅ Only use first 2000 chars for fast response
        search_prompt = f"Answer concisely: {question} based on this text: {limited_text}"

        try:
            response = llm.invoke(search_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"❌ Error generating response: {str(e)}")

    return "No relevant answer found in the document."

@app.route("/chat", methods=["POST"])
def chat():
    print("📩 Request received!")

    data = request.get_json()
    print("📨 Received data:", data)

    question = data.get("query", "")
    if not question:
        print("⚠️ No question received!")
        return jsonify({"answer": "Please provide a valid question."}), 400

    print("❓ User Question:", question)
    answer = get_chatbot_answer(question)
    
    print("🤖 Bot Answer:", answer)
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    print("🚀 Starting Flask chatbot server on port 5001...")
    app.run(port=5001, debug=False, threaded=True)  # ✅ Faster performance with threading
