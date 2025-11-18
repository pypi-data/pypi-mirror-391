#### Code Example

```
pip install vector_db_1807
```
or
```
uv add vector_db_1807
```

```
import os
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, OllamaLLM
# import your local SDK client
from vector_db_1807 import VectorClient

# ---------------- CONFIG ----------------
API_URL = ""
API_KEY = ""
PDF_FILE = ""
TOP_K = 3

# ---------------- INIT ----------------
embedder = OllamaEmbeddings(model="llama3.2")     
llm = OllamaLLM(model="llama3.2")

# Vector DB SDK client
client = VectorClient(
    api_key=API_KEY,
    base_url=API_URL,
)

# ---------------- LOAD PDF ----------------
loader = PyPDFLoader(PDF_FILE)
pages = loader.load()
full_text = "\n\n".join([p.page_content for p in pages])

print(f"[INFO] Loaded {len(pages)} pages from {PDF_FILE}")


# ---------------- CREATE EMBEDDING ----------------
embedding = embedder.embed_query(full_text)

metadata = {
    "text": full_text,
    "file_name": os.path.basename(PDF_FILE),
    "source": "resume",
}


# ---------------- STEP 1: ADD VECTOR ----------------
print("\n[INFO] Uploading vector using VectorClient...")

add_resp = client.add_vector(
    embedding=embedding,
    metadata=metadata,
)

print("[INFO] Added successfully:\n", json.dumps(add_resp, indent=2))

document_id = add_resp["data"]["document_id"]


# ---------------- STEP 2: SEARCH ----------------
query = "What companies/organizations has he worked in so far?"
query_vector = embedder.embed_query(query)

print("\n[INFO] Searching via VectorClient...")

search_resp = client.search(
    query_vector=query_vector,
    document_id=document_id,
    top_k=TOP_K
)

results = search_resp["data"]["results"]

print("[INFO] Search results:", json.dumps(results, indent=2))

if not results:
    print("[WARN] No vector matches found.")
    exit()

best = results[0]
context = best["metadata"]["text"]

print(f"[INFO] Using context from: {best['metadata']['file_name']}")


# ---------------- STEP 3: LLM ANSWER ----------------
prompt = f"""
Answer the question ONLY using the following context:

<context>
{context}
</context>

Question: {query}

Answer:
"""

answer = llm.invoke(prompt)

print("\n" + "="*60)
print("QUESTION:", query)
print("ANSWER:\n", answer)
print("="*60)
```