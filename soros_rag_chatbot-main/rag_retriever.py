# rag_retriever.py

from typing import List, Tuple
import chromadb
from chromadb.utils import embedding_functions

from rag_data import load_qa_dataframe


class ChromaEmbeddingRetriever:
    """
    Embedding-based retriever using Sentence-Transformer + ChromaDB.

    - Indexes each Soros Q&A row as one document: "Q: ...\\nA: ..."
    - Uses sentence-transformer embeddings under the hood.
    - Returns (question, answer) pairs for the top_k most relevant documents.
    """

    def __init__(self, persist_dir: str = "chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        # Load Soros Q&A dataframe
        self.df = load_qa_dataframe()

        # Create / load Chroma collection with Sentence-Transformer embeddings
        self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name="soros_qa",
            embedding_function=self._embedding_fn,
        )

        # If collection is empty, populate it from the dataframe
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

            doc_text = f"Q: {q}\\nA: {a}"
            documents.append(doc_text)
            metadatas.append({"row_index": i, "label": label})
            ids.append(str(i))

        self._collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, str]]:
        """
        Return top_k (question, answer) pairs most relevant to the query.
        """
        query = (query or "").strip()
        if not query:
            # Simple fallback: first few rows if query is empty
            rows = self.df.head(top_k)
            return list(zip(rows["Question"], rows["Answer"]))

        result = self._collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        ids = result.get("ids", [[]])[0]
        # If no ids returned, fallback to first few rows
        if not ids:
            rows = self.df.head(top_k)
            return list(zip(rows["Question"], rows["Answer"]))

        # Map ids back to dataframe rows
        pairs: List[Tuple[str, str]] = []
        for id_str in ids:
            idx = int(id_str)
            row = self.df.iloc[idx]
            pairs.append((row["Question"], row["Answer"]))

        return pairs


# Quick manual test
if __name__ == "__main__":
    retriever = ChromaEmbeddingRetriever()
    query = "How does Soros think about risk and reflexivity?"
    results = retriever.retrieve(query, top_k=3)

    print(f"Query: {query}\\n")
    for i, (q, a) in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print("Q:", q)
        print("A:", a)
        print()
