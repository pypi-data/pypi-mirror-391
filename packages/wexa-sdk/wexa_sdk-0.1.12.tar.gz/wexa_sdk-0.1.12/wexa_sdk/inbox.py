from __future__ import annotations
from typing import Any, Dict, Optional, TypedDict, Literal

from .core.http import HttpClient

class Inbox:
    def __init__(self, http: HttpClient):
        self.http = http

    class InboxCreateBody(TypedDict, total=False):
        _id: str
        type: str
        status: str
        created_at: float
        updated_at: float
        agent_id: str
        coworker_id: str
        coworker_name: str
        agent_title: str
        summary: str
        execution_id: str
        projectID: str
        # Allow extra fields if backend accepts more
        Name: str
        Description: str

    def create(self, body: InboxCreateBody):
        """
        Create inbox
        POST /inbox/create
        Creates a new inbox request entry (preview, runtime_input, or anomaly_detection).
        """
        return self.http.request("POST", "/inbox/create", json=body)

    def list(
        self,
        project_id: str,
        *,
        limit: Optional[int] = 100,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search_key: Optional[str] = None,
        after_id: Optional[str] = None,
        view: Literal["ui", "studio"] = "ui",
    ):
        """
        GET /inbox
        Query: projectID (required), limit, status, type, search_key, after_id, view
        """
        params: Dict[str, Any] = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        if status is not None:
            params["status"] = status
        if type is not None:
            params["type"] = type
        if search_key is not None:
            params["search_key"] = search_key
        if after_id is not None:
            params["after_id"] = after_id
        if view:
            params["view"] = view
        return self.http.request("GET", "/inbox", params=params)

    class UpdateRuntimeBody(TypedDict):
        is_submitted: bool
        values: Dict[str, str]
        agent_id: str

    def update_runtime(self, execution_id: str, project_id: Optional[str], body: UpdateRuntimeBody):
        """
        Update inbox at runtime
        POST /inbox/update/runtime_input/{execution_id}?projectID=...
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/runtime_input/{execution_id}", params=params, json=body)

    class UpdateAnomalyBody(TypedDict):
        is_approved: bool

    def update_anomaly(self, execution_id: str, project_id: Optional[str], body: UpdateAnomalyBody):
        """
        Update anomaly detection inbox
        POST /inbox/update/anomaly_detection/{execution_id}?projectID=...
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/anomaly_detection/{execution_id}", params=params, json=body)

    class UpdatePreviewBody(TypedDict):
        agent_id: str
        is_approved: bool
        preview_input: Dict[str, Any]

    def update_preview(self, execution_id: str, project_id: Optional[str], body: UpdatePreviewBody):
        """
        Update Preview Inbox (Approve or Draft)
        POST /inbox/update/preview/{execution_id}?projectID=...
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/preview/{execution_id}", params=params, json=body)

    # GET /inbox/{id}?projectID=...
    def get(self, inbox_id: str, project_id: Optional[str] = None):
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/inbox/{inbox_id}", params=params)
