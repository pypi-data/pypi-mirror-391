import httpx
from typing import List, Dict, Any, Optional
from .exceptions import APIError


class AsyncVectorClient:
    """
    Asynchronous SDK client for your Vector Database API.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.yourdomain.com",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    # -------------------------------
    # Core Methods
    # -------------------------------

    async def add_vector(
        self, embedding: List[float], metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        res = await self._client.post(
            f"{self.base_url}/vector/add",
            json={"embedding": embedding, "metadata": metadata or {}},
            headers=self.headers,
        )
        return self._handle_response(res)

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        res = await self._client.post(
            f"{self.base_url}/vector/search",
            json={
                "query_vector": query_vector,
                "top_k": top_k,
                "filters": filters or {},
            },
            headers=self.headers,
        )
        return self._handle_response(res)

    async def save_index(self) -> Dict[str, Any]:
        res = await self._client.post(
            f"{self.base_url}/vector/index/save", headers=self.headers
        )
        return self._handle_response(res)

    async def load_index(self) -> Dict[str, Any]:
        res = await self._client.post(
            f"{self.base_url}/vector/index/load", headers=self.headers
        )
        return self._handle_response(res)

    async def aclose(self):
        """Close persistent HTTP connection."""
        await self._client.aclose()

    # -------------------------------
    # Internal Helpers
    # -------------------------------

    def _handle_response(self, res: httpx.Response) -> Dict[str, Any]:
        try:
            data = res.json()
        except Exception:
            raise APIError(res.status_code, "Invalid JSON response")

        if res.is_error:
            message = data.get("detail") or data.get("error") or res.reason_phrase
            raise APIError(res.status_code, message)

        return data
