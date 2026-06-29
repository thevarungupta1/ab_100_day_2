from pathlib import Path

def load_documents(data_dir= "data"):
    documents = []
    
    for file_path in Path(data_dir).glob("*.txt"):
        documents.append({
            "file_name": file_path.name,
            "content": file_path.read_text(encoding="utf-8")
        })
        
    return documents