# rag_retriever.py

from typing import List, Tuple
import os

import chromadb
from chromadb.utils import embedding_functions

from .rag_data import load_qa_dataframe


class ChromaEmbeddingRetriever:
    """
    Embedding-based retriever using Sentence-Transformer + ChromaDB.
    Indexes each Soros Q&A row as one document: "Q: ...\nA: ...".
    Returns (question, answer) pairs for the top_k most relevant documents.
    """

    def __init__(self, persist_dir: str, model_name: str = "all-MiniLM-L6-v2"):
        self.df = load_qa_dataframe()

        use_st = os.getenv("ENABLE_SENTENCE_TRANSFORMER", "0") == "1"
        if use_st:
            try:
                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=model_name
                )
                print(f"Chroma retriever using sentence-transformer model: {model_name}")
            except Exception as e:
                print(f"WARNING: sentence-transformer embedding init failed ({e}); falling back to DefaultEmbeddingFunction.")
                self._embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        else:
            print("Chroma retriever using DefaultEmbeddingFunction (fastembed) for stability. Set ENABLE_SENTENCE_TRANSFORMER=1 to try all-MiniLM.")
            self._embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name="soros_qa",
            embedding_function=self._embedding_fn,
        )

        if self._collection.count() == 0:
            self._build_index()

    def _build_index(self) -> None:
        documents = []
        metadatas = []
        ids = []

        for i, row in self.df.iterrows():
            q = str(row["Question"])
            a = str(row["Answer"])
            label = str(row.get("Label", ""))

            doc_text = f"Q: {q}\nA: {a}"
            documents.append(doc_text)
            metadatas.append({"row_index": i, "label": label})
            ids.append(str(i))

        self._collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, str]]:
        query = (query or "").strip()
        if not query:
            rows = self.df.head(top_k)
            return list(zip(rows["Question"], rows["Answer"]))

        result = self._collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        ids = result.get("ids", [[]])[0]
        if not ids:
            rows = self.df.head(top_k)
            return list(zip(rows["Question"], rows["Answer"]))

        pairs: List[Tuple[str, str]] = []
        for id_str in ids:
            idx = int(id_str)
            row = self.df.iloc[idx]
            pairs.append((row["Question"], row["Answer"]))

        return pairs


if __name__ == "__main__":
    retriever = ChromaEmbeddingRetriever(persist_dir="chroma_db")
    query = "How does Soros think about risk and reflexivity?"
    results = retriever.retrieve(query, top_k=3)
    print(f"Query: {query}\n")
    for i, (q, a) in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print("Q:", q)
        print("A:", a)
        print()
