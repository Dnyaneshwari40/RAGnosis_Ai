
## RAGNOSIS AI

RAGNOSIS AI is a Flask-based web application that leverages Retrieval Augmented Generation (RAG) to provide a powerful document question-answering and summarization tool. Users can upload PDF documents, ask questions about their content, and receive concise summaries. The application integrates a MySQL database for user management, ChromaDB for vector storage, and Groq's LLMs for natural language processing.

---

### Features

- **User Authentication:** Secure registration and login system for users.
- **PDF Upload and Processing:**
  - Upload PDF documents.
  - Automatic text extraction from PDFs.
  - Text cleaning and chunking for efficient processing.
- **Intelligent Q&A:**
  - Ask questions about the content of uploaded PDFs.
  - Retrieval-Augmented Generation (RAG) using ChromaDB for relevant chunk retrieval and a Groq LLM for answer generation.
- **Document Summarization:** Generate concise summaries of uploaded PDF documents.
- **Persistent Vector Store:** ChromaDB stores document embeddings, allowing for efficient retrieval.
- **Scalable LLM Integration:** Utilizes Groq's API for fast and efficient language model inference.

---

### Technologies Used

- **Backend:** Flask (Python)
- **Database:** MySQL
- **Vector Database:** ChromaDB
- **Embedding Model:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **Large Language Model (LLM):** Groq (`llama3-8b-8192`)
- **PDF Processing:** `pypdf`
- **Environment Management:** `python-dotenv`
- **CORS:** `Flask-CORS`
- **Utilities:** `werkzeug` (for secure filenames), `re` (regex)

---

### Setup and Installation

Follow these steps to set up and run RAGNOSIS AI locally.

---

#### Prerequisites

- Python 3.8+
- MySQL Server

---

#### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd RAGNOSIS_AI
````

---

#### 2. Set up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The `requirements.txt` file should contain the following:

```
Flask==2.3.3
Flask-Cors==4.0.0
mysql-connector-python==8.0.33
python-dotenv==1.0.1
pypdf==4.2.0
chromadb==0.4.24
sentence-transformers==2.7.0
langchain-groq==0.1.5
requests==2.31.0
```

---

#### 4. Database Setup

**Create MySQL Database:**

```sql
CREATE DATABASE rag_nosis;
```

**Create `users` Table:**

```sql
USE rag_nosis;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Update Database Credentials in `app.py`:**

```python
db = mysql.connector.connect(
    host="localhost",
    user="root",          # Your MySQL username
    password="Riddhi@1804", # Your MySQL password
    database="rag_nosis"
)
```

---

#### 5. Configure Groq API Key

**Get a Groq API Key:**

Sign up on the [Groq website](https://groq.com/) and obtain your API key.

**Create a `.env` file:**

```env
GROQ_API_KEY="your_groq_api_key_here"
```

Ensure `dotenv_path` in `app.py` points correctly:

```python
dotenv_path = os.path.join("C:/Users/Diya Suryawanshi/OneDrive/Desktop/RAGNOSIS_AI", ".env")
load_dotenv(dotenv_path)
```

---

#### 6. Run the Application

```bash
python app.py
```

The application will start on: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

### Usage

* **Register:** [http://127.0.0.1:5000/auth/register](http://127.0.0.1:5000/auth/register)
* **Login:** [http://127.0.0.1:5000/auth/login](http://127.0.0.1:5000/auth/login)
* **Main Page:** [http://127.0.0.1:5000/auth/mainpage](http://127.0.0.1:5000/auth/mainpage)
* **Upload PDF:** Upload a PDF to extract and chunk text into ChromaDB.
* **Chat (Q\&A):** [http://127.0.0.1:5000/auth/chat](http://127.0.0.1:5000/auth/chat)
* **Generate Summary:** Trigger a `POST` request to `/generate_summary` after upload.

---

### Project Structure

```
.
├── app.py              # Main Flask application file
├── templates/          # HTML templates for the web interface
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── mainpage.html
│   └── chat.html
├── document_store/     # Directory to store uploaded PDF files
├── chroma_db/          # Directory for ChromaDB persistent storage
├── .env                # Environment variables (e.g., GROQ_API_KEY)
└── requirements.txt    # Python dependencies
```


