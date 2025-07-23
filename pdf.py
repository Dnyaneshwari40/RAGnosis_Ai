import pypdf
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

#TEXT EXTRACTION

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or "" # or "" handles pages with no text.
            return text
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_path}' not found.")
        return None
    except pypdf.errors.PdfReadError:
        print(f"Error: Unable to read PDF file '{pdf_path}'.")
        return None

pdf_text = extract_text_from_pdf("SAMPLE4.pdf") #replace "your_pdf_file.pdf"
if pdf_text:
    print("PDF Text Extracted")
else:
    print("PDF text extraction failed.")

#CHUNKING
def chunk_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

if pdf_text:
    chunks = chunk_text(pdf_text)
    print(f"Created {len(chunks)} chunks.")




embedding_model = SentenceTransformer('all-MiniLM-L6-v2') #lightweight model

if pdf_text:
    embeddings = embedding_model.encode(chunks)
    print("Embeddings created.")

#STORING IN CHROMADB

if pdf_text:
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="pdf_chunks")

    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    print("Chunks and embeddings stored in ChromaDB.")

