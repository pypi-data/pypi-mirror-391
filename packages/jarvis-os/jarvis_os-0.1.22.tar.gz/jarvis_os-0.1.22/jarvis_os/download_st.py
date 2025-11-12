from sentence_transformers import SentenceTransformer

# Force-load and save locally
model = SentenceTransformer("all-MiniLM-L6-v2")
model.save("models/all-MiniLM-L6-v2")
