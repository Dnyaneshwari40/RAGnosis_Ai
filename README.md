# RAGNOSIS




## About the Project

This project is a web-based application designed to help users efficiently process and understand information from PDF documents and interact with a chatbot. It combines a robust PDF summarization engine, powered by advanced NLP models, with a conversational AI interface. Users can upload PDF files to get concise summaries and engage in a chat, potentially asking questions about the summarized content or general queries.

The application leverages vector databases for efficient information retrieval and state-of-the-art Hugging Face transformers for natural language processing tasks, ensuring high-quality summaries and intelligent chatbot responses.

## Features

* **PDF Text Extraction**: Extracts text content from uploaded PDF documents.
* **Intelligent PDF Summarization**: Generates concise and relevant summaries of PDF content using the `facebook/bart-large-cnn` model.
* **Text Chunking & Embedding**: Processes large documents by chunking text and creating embeddings for efficient storage and retrieval using ChromaDB and `SentenceTransformer` (`all-MiniLM-L6-v2`).
* **Chatbot Integration**: Provides a conversational interface.
* **User Authentication**: Supports user registration and login functionalities.
* **Web Interface**: A user-friendly web interface built with HTML for easy interaction.

## Technologies Used

* **Backend**:
    * Python 3.x
    * Flask (Implied by `main.py` typically being a Flask app entry)
    * `transformers` library (Hugging Face)
    * `pypdf`
    * `chromadb`
    * `sentence-transformers`
* **Frontend**:
    * HTML5
    * (Potentially CSS and JavaScript for styling and interactivity)
* **Database**:
    * SQLite (or similar, implied by `db.sql` and `main.py`'s use of a local database file)
* **Machine Learning Models**:
    * `facebook/bart-large-cnn` for summarization
    * `all-MiniLM-L6-v2` for embeddings

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *If you don't have a `requirements.txt`, you'll need to create one. Here are the likely contents based on your files:*
    ```
    Flask
    pypdf
    chromadb
    sentence-transformers
    transformers
    torch # Transformers often require torch or tensorflow
    scipy # Some NLP libraries might have this dependency
    ```
    You might also need to install a PyTorch version compatible with your system (CPU or GPU):
    ```bash
    pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cpu](https://download.pytorch.org/whl/cpu) # For CPU, adjust for GPU if needed
    ```

### Database Setup

1.  **Initialize the database:**
    The `db.sql` file contains the schema for your application's database.
    You'll need a database client (e.g., `sqlite3` for SQLite) to create the database and tables.
    ```bash
    # Assuming SQLite and Flask expects 'instance' folder
    mkdir instance
    sqlite3 instance/database.db < db.sql
    ```
    *Note: `main.py` likely connects to `instance/database.db` or similar.*

### Running the Application

1.  **Activate your virtual environment (if not already active):**
    ```bash
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
2.  **Run the Flask application:**
    ```bash
    python main.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5000/` (or the address shown in your terminal).

## Usage

1.  **Register/Login**: Navigate to the `/register` or `/login` page to create an account or log in.
2.  **Upload PDF**: Once logged in, you should be able to navigate to a page (likely `/mainpage`) where you can upload PDF files for summarization.
3.  **View Summary**: After uploading, the application will process the PDF and display a summary.
4.  **Interact with Chatbot**: Access the chatbot interface (likely `/chat`) to ask questions or interact with the AI.

## File Structure

* `bart_large_summ.py`: Core logic for PDF text extraction, chunking, embedding with ChromaDB, retrieval, and summarization using `bart-large-cnn` model.
* `chatbot.py`: Contains the logic for the conversational AI/chatbot.
* `db.sql`: SQL script for creating the database schema (user tables, etc.).
* `main.py`: The main Flask application entry point, handling routes, database interactions, and integrating the PDF and chatbot functionalities.
* `pdf.py`: (Potentially older/alternative PDF processing logic, or specific PDF utility functions used by `main.py` or `bart_large_summ.py`).
* `Sample_Main.py`: (Likely a sample or development version of `main.py`, perhaps for testing specific functionalities).
* `chat.html`: Frontend template for the chatbot interface.
* `index.html`: The main landing page or entry point for the web application.
* `login.html`: Frontend template for user login.
* `mainpage.html`: Frontend template for the main application dashboard, likely where PDF uploads and summaries are displayed.
* `register.html`: Frontend template for new user registration.
* `./chroma_db/`: Directory where ChromaDB will store its persistent vector database (created by `bart_large_summ.py`).
* `./instance/database.db`: (Expected) Location for the SQLite database file.
* `SAMPLE4.pdf`: (A sample PDF file used for testing the summarization script).

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Make your changes and ensure your code adheres to the project's style.
4.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a Pull Request.



## Acknowledgments

* Hugging Face Transformers for providing powerful NLP models.
* ChromaDB for the efficient vector database.
* `pypdf` for PDF parsing.
* `Sentence-Transformers` for embedding models.
* Flask for the web framework.

---
