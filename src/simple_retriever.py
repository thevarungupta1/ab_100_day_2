from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.document_loader import load_documents

def retrieve_context(query, top_k=2):
    documents = load_documents()
    
    texts = [doc["content"] for doc in documents]

    vertorizer = TfidfVectorizer()
    vectors = vertorizer.fit_transform(texts)
    
    query_vector = vertorizer.transform([query])
    scores = cosine_similarity(query_vector, vectors).flatten()
    
    ranked = scores.argsort()[::-1][:top_k]

    results = []
    
    for index in ranked:
        results.append({
            "source": documents[index]["file_name"],
            "content": documents[index]["content"],
            "score": scores[index]
        })
        
    return results