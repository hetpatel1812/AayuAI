"""
Aayu AI — RAG Service
ChromaDB embedding + retrieval for medical knowledge base.
"""
import os
import json

# ChromaDB will be lazy-loaded
_collection = None


def _get_collection():
    """Lazy-load ChromaDB collection."""
    global _collection
    if _collection is not None:
        return _collection

    try:
        import chromadb
        persist_dir = os.environ.get('CHROMA_PERSIST_DIR',
                                      os.path.join(os.path.dirname(__file__), '..', 'chroma_db'))
        client = chromadb.PersistentClient(path=persist_dir)
        _collection = client.get_or_create_collection(
            name='aayu_medical_knowledge',
            metadata={'hnsw:space': 'cosine'}
        )
        return _collection
    except Exception as e:
        print(f"ChromaDB init error: {e}")
        return None


def load_knowledge_base(data_path=None):
    """Load medical knowledge from JSON into ChromaDB.
    
    Args:
        data_path: Path to parameters.json knowledge base file.
    """
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'parameters.json')

    if not os.path.exists(data_path):
        print(f"Knowledge base not found: {data_path}")
        return

    collection = _get_collection()
    if not collection:
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        params = json.load(f)

    documents = []
    ids = []
    metadatas = []

    for param in params:
        doc = f"{param['name']}: {param.get('description', '')} Normal range: {param.get('ref_low', '')} - {param.get('ref_high', '')} {param.get('unit', '')}. {param.get('explanation', '')}"
        documents.append(doc)
        ids.append(param['name'].lower().replace(' ', '_'))
        metadatas.append({'category': param.get('category', 'Other')})

    collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
    print(f"Loaded {len(documents)} parameters into knowledge base.")


def retrieve_context(query, n_results=3):
    """Retrieve relevant medical context for a query.
    
    Args:
        query: User query or parameter name.
        n_results: Number of results to return.
    
    Returns:
        str: Combined context text.
    """
    collection = _get_collection()
    if not collection:
        return ''

    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        if results and results['documents']:
            return '\n\n'.join(results['documents'][0])
    except Exception as e:
        print(f"RAG retrieval error: {e}")

    return ''
