# vector_db_1807/async_client.py
import httpx
from typing import List, Dict, Any, Optional
from .exceptions import APIError


class AsyncVectorClient:
    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8000", timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    async def add_vector(
        self,
        embedding: List[float],
        metadata: Dict[str, Any],
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if metadata is None or "text" not in metadata or not metadata["text"]:
            raise ValueError("metadata['text'] is required")
        payload = {"embedding": embedding, "metadata": metadata}
        if document_id:
            payload["document_id"] = document_id
        res = await self.client.post("/vector/add", json=payload)
        return self._handle_response(res)

    async def search(
        self,
        query_vector: List[float],
        document_id: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not document_id:
            raise ValueError("document_id is required for document-scoped search")
        payload = {
            "query_vector": query_vector,
            "document_id": document_id,
            "top_k": top_k,
            "filters": filters or {},
        }
        res = await self.client.post("/vector/search", json=payload)
        return self._handle_response(res)

    async def list_documents(self):
        res = await self.client.get("/vector/documents")
        return self._handle_response(res)

    async def delete_document(self, document_id: str):
        res = await self.client.delete(f"/vector/document/{document_id}")
        return self._handle_response(res)

    def _handle_response(self, res: httpx.Response):
        try:
            data = res.json()
        except Exception:
            raise APIError(res.status_code, "Invalid JSON")
        if not res.is_success:
            raise APIError(
                res.status_code,
                data.get("detail") or data.get("error") or res.reason_phrase,
            )
        return data

    async def aclose(self):
        await self.client.aclose()
