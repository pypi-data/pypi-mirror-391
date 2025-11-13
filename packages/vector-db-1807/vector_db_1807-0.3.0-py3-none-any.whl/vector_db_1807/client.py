import requests
from typing import List, Dict, Any, Optional
from .exceptions import APIError


class VectorClient:
    """
    Synchronous SDK client for your Vector Database API.
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

    # -------------------------------
    # Core Methods
    # -------------------------------

    def add_vector(
        self, embedding: List[float], metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/vector/add",
            json={"embedding": embedding, "metadata": metadata or {}},
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/vector/search",
            json={
                "query_vector": query_vector,
                "top_k": top_k,
                "filters": filters or {},
            },
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def save_index(self) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/vector/index/save",
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def load_index(self) -> Dict[str, Any]:
        res = requests.post(
            f"{self.base_url}/vector/index/load",
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    # -------------------------------
    # Internal Helpers
    # -------------------------------

    def _handle_response(self, res: requests.Response) -> Dict[str, Any]:
        try:
            data = res.json()
        except Exception:
            raise APIError(res.status_code, "Invalid JSON response")

        if not res.ok:
            message = data.get("detail") or data.get("error") or res.reason
            raise APIError(res.status_code, message)

        return data
