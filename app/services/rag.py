import os, logging
from pathlib import Path

logger = logging.getLogger(__name__)
# Use domestic mirror for faster model download
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")


CHROMA_PERSIST_DIR = "storage/chroma_db"
KB_FILE = "storage/product_kb.md"
COLLECTION_NAME = "telecom_products"
EMBEDDING_MODEL = "BAAI/bge-small-zh"

_collection = None


def _get_root():
    return Path(__file__).parent.parent.parent


def _extract_keywords(content):
    kws = []
    if "学生" in content or "校园" in content: kws.append("学生")
    if "老人" in content or "银发" in content: kws.append("老年人")
    if "家庭" in content or "全家" in content: kws.append("家庭")
    if "企业" in content or "商务" in content or "商户" in content: kws.append("企业")
    if "流量" in content: kws.append("流量")
    if "宽带" in content: kws.append("宽带")
    return kws


def _load_kb_chunks():
    kb_path = _get_root() / KB_FILE
    with open(kb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    chunks = []
    current_title = None
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and "产品知识库" not in stripped:
            if current_title and current_lines:
                content = "".join(current_lines)
                kws = _extract_keywords(content)
                chunks.append({"id": current_title, "content": content, "title": current_title, "keywords": ", ".join(kws)})
            current_title = stripped.lstrip("#").strip()
            if ". " in current_title[:5]:
                current_title = current_title.split(". ", 1)[-1]
            current_lines = [line]
        elif current_title:
            current_lines.append(line)
    
    if current_title and current_lines:
        content = "".join(current_lines)
        kws = _extract_keywords(content)
        chunks.append({"id": current_title, "content": content, "title": current_title, "keywords": ", ".join(kws)})
    
    return chunks


def build_index():
    global _collection
    import chromadb
    from chromadb.utils import embedding_functions
    persist_dir = str(_get_root() / CHROMA_PERSIST_DIR)
    client = chromadb.PersistentClient(path=persist_dir)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    chunks = _load_kb_chunks()
    if not chunks:
        return 0
    _collection.add(ids=[c["id"] for c in chunks], documents=[c["content"] for c in chunks], metadatas=[{"title": c["title"], "keywords": c["keywords"]} for c in chunks])
    logger.info(f"Index built: {len(chunks)} products")
    return len(chunks)


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
    import chromadb
    persist_dir = str(_get_root() / CHROMA_PERSIST_DIR)
    if not os.path.exists(persist_dir):
        build_index()
        return _collection
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        from chromadb.utils import embedding_functions
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        _collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    except Exception:
        build_index()
    return _collection


def search(query, n_results=3):
    try:
        collection = _get_collection()
        results = collection.query(query_texts=[query], n_results=min(n_results, 10))
        output = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for i in range(len(ids)):
            output.append({"title": ids[i], "content": documents[i], "score": round(1.0 - distances[i], 4) if distances else 0})
        return output
    except Exception as e:
        logger.error(f"RAG search failed: {e}")
        return []


def search_product_kb(query):
    results = search(query, n_results=3)
    if not results:
        return {"success": True, "data": [], "message": f"未找到与'{query}'相关的产品信息"}
    formatted = []
    for r in results:
        formatted.append(f"【{r['title']}】(相关度: {r['score']})\n{r['content'][:300]}")
    return {"success": True, "data": results, "message": "\n\n".join(formatted)}