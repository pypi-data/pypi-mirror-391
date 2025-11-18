# vector_db_1807/client.py
import requests
from typing import List, Dict, Any, Optional
from .exceptions import APIError


class VectorClient:
    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8000", timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def add_vector(
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
        res = requests.post(
            f"{self.base_url}/vector/add",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def search(
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
        res = requests.post(
            f"{self.base_url}/vector/search",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def list_documents(self) -> Dict[str, Any]:
        res = requests.get(
            f"{self.base_url}/vector/documents",
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        res = requests.delete(
            f"{self.base_url}/vector/document/{document_id}",
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(res)

    def _handle_response(self, res):
        try:
            data = res.json()
        except Exception:
            raise APIError(res.status_code, "Invalid JSON response")
        if not res.ok:
            raise APIError(
                res.status_code, data.get("detail") or data.get("error") or res.reason
            )
        return data
