import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import pypdf
import re


import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ==========================
# ✅ Step 1: Extract Text from PDF
# ==========================
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

pdf_text = extract_text_from_pdf("SAMPLE4.pdf")  # Replace with your PDF file

# ==========================
# ✅ Step 2: Preprocess & Chunk Text
# ==========================
def clean_text(text):
    text = re.sub(r'\n+', ' ', text)  # Remove extra newlines
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def chunk_text(text, chunk_size=500, chunk_overlap=100):
    chunks = []
    text = clean_text(text)
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

chunks = chunk_text(pdf_text)

# ==========================
# ✅ Step 3: Store in ChromaDB with Embeddings
# ==========================
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_chunks")

# Check if already stored
if collection.count() == 0:
    collection.add(
        embeddings=embedding_model.encode(chunks).tolist(),
        documents=chunks,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

print(f"✅ Stored {len(chunks)} chunks in ChromaDB.")

# ==========================
# ✅ Step 4: Retrieve Relevant Chunks from ChromaDB
# ==========================
def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results["documents"][0] if results and "documents" in results else []

retrieved_chunks = retrieve_relevant_chunks("Summarize this document", top_k=7)  # Fetch 7 best chunks

# ==========================
# ✅ Step 5: Summarize Using Optimized Model
# ==========================
model_name = "facebook/bart-large-cnn"  # Faster & better than Pegasus for large docs
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

def summarize_chunks(chunks):
    summaries = []
    batch_size = 3  # Process multiple chunks at once
    for i in range(0, len(chunks), batch_size):
        batch = " ".join(chunks[i:i + batch_size])  # Merge multiple chunks
        summary = summarizer(batch, max_length=150, min_length=50, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return summaries

summarized_texts = summarize_chunks(retrieved_chunks)

# ==========================
# ✅ Step 6: Print Final Summaries
# ==========================
final_summary = " ".join(summarized_texts)
print("\n✅ Final Document Summary:\n", final_summary)
