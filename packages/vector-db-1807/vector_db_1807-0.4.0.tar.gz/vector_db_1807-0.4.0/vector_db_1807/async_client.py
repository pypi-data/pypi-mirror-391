import httpx
from typing import List, Dict, Any, Optional
from .exceptions import APIError


class AsyncVectorClient:
    """
    Asynchronous Python SDK client for your Vector Database API.
    Enforces metadata['text'] for RAG behavior.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.yourdomain.com",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    # -------------------------------------------------------
    # ADD VECTOR (strict metadata["text"])
    # -------------------------------------------------------
    async def add_vector(
        self,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        # ---------- Validate metadata ---------- #
        if metadata is None:
            raise ValueError(
                "metadata is required.\n"
                "Example:\n"
                'await db.add_vector(embedding, metadata={"text": "full content"})'
            )

        if "text" not in metadata or not metadata["text"]:
            raise ValueError(
                "metadata['text'] is required and cannot be empty.\n"
                "This is the document text used for RAG context."
            )

        payload = {
            "embedding": embedding,
            "metadata": metadata,
        }

        res = await self.client.post("/vector/add", json=payload)
        return self._handle_response(res)

    # -------------------------------------------------------
    # SEARCH
    # -------------------------------------------------------
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        payload = {
            "query_vector": query_vector,
            "top_k": top_k,
            "filters": filters or {},
        }

        res = await self.client.post("/vector/search", json=payload)
        return self._handle_response(res)

    # -------------------------------------------------------
    # INDEX OPS
    # -------------------------------------------------------
    async def save_index(self) -> Dict[str, Any]:
        res = await self.client.post("/vector/index/save")
        return self._handle_response(res)

    async def load_index(self) -> Dict[str, Any]:
        res = await self.client.post("/vector/index/load")
        return self._handle_response(res)

    # -------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------
    async def aclose(self):
        await self.client.aclose()

    # -------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------
    def _handle_response(self, res: httpx.Response) -> Dict[str, Any]:
        try:
            data = res.json()
        except Exception:
            raise APIError(res.status_code, "Invalid JSON response from server")

        if not res.is_success:
            message = data.get("detail") or data.get("error") or res.reason_phrase
            raise APIError(res.status_code, message)

        return data
