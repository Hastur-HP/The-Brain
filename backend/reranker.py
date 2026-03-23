import logging
import asyncio
import httpx
from sentence_transformers import CrossEncoder
from backend.config import RERANKER_MAX_BATCH_SIZE

_logger = logging.getLogger(__name__)


class DocumentReranker:
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
        base_url: str = "",
        api_key: str = "",
        timeout: int = 60,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self._reranker = None

    def load(self):
        """Preloads the local model into memory if we are NOT using an external API."""
        if self.base_url:
            return None  # Skip loading on CPU if an external URL is provided

        if self._reranker is None:
            _logger.info(f"Loading local CPU reranker {self.model_name} ...")
            self._reranker = CrossEncoder(self.model_name)
            _logger.info("Local Reranker ready.")
        return self._reranker

    async def rerank(self, query: str, documents: list[str], top_n: int = 20):
        """Routes to an external API with payload batching, otherwise runs local CPU inference."""

        # External routing
        if self.base_url:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            all_results = []
            batch_size = RERANKER_MAX_BATCH_SIZE

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                _logger.info(
                    f"Sending batched rerank requests to {self.base_url} for {len(documents)} docs"
                )

                # Slice the documents into batches of 50
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    payload = {
                        "model": self.model_name,
                        "query": query,
                        "documents": batch_docs,
                        "top_n": len(batch_docs),  # Scores sorted globally later
                    }

                    resp = await client.post(
                        f"{self.base_url.rstrip('/')}/rerank",
                        json=payload,
                        headers=headers,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    if "results" in data:
                        for r in data["results"]:
                            # The API returns an index for the batch (0-49).
                            # We must remap it to the global document index (e.g., 50-99).
                            r["index"] = r["index"] + i
                            all_results.append(r)

            # Sort the combined results from all batches globally
            all_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            results = all_results[:top_n]
            _logger.info(
                f"[rerank-external] top: "
                f"{[round(r.get('relevance_score', 0), 3) for r in results[:5]]}"
            )
            return results

        # Local routing
        loop = asyncio.get_running_loop()
        pairs = [[query, doc] for doc in documents]

        scores = await loop.run_in_executor(
            None, lambda: self.load().predict(pairs, show_progress_bar=False)
        )

        results = [
            {"index": i, "relevance_score": float(s)} for i, s in enumerate(scores)
        ]
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        _logger.info(
            f"[rerank-local] {len(documents)} docs → top: "
            f"{[round(r['relevance_score'], 3) for r in results[:5]]}"
        )
        return results[:top_n]
