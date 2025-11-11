from __future__ import annotations
import time
from typing import Any, Callable, Optional

from .core.http import HttpClient

DEFAULT_TERMINAL = {"completed", "failed", "canceled"}

class Executions:
    def __init__(self, http: HttpClient, polling: Optional[dict] = None):
        self.http = http
        self.polling = polling or {}

    def start(self, payload: dict, *, projectID: Optional[str] = None):
        """
        Create/Start an execution.

        POST /execute_flow?projectID=...
        Body requires at least:
          - agentflow_id: str
          - executed_by: str
          - goal: str
          - input_variables: dict
          - projectID: str (backend may also accept via query)
        """
        params = {"projectID": projectID} if projectID else None
        return self.http.request("POST", "/execute_flow", json=payload, params=params)

    def get(self, execution_id: str):
        return self.http.request("GET", f"/execute_flow/{execution_id}")

    def monitor(self, agentflow_id: str):
        return self.http.request("GET", f"/execute_flow/{agentflow_id}/monitor")

    def pause(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/pause")

    def resume(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/resume")

    def cancel(self, execution_id: str):
        return self.http.request("POST", f"/execute_flow/{execution_id}/cancel")

    def execute(self, execution_id: str, *, projectID: str, body: Optional[dict] = None):
        """
        Execute an existing execution by ID.

        POST /execute_flow/{execution_id}/execute?projectID=...
        The backend may expect execution_id and/or projectID in the body as well.
        """
        params = {"projectID": projectID}
        json_body = {"execution_id": execution_id, "projectID": projectID}
        if body:
            json_body.update(body)
        return self.http.request("POST", f"/execute_flow/{execution_id}/execute", params=params, json=json_body)

    # Removed wait/approve/update-runtime endpoints per request
