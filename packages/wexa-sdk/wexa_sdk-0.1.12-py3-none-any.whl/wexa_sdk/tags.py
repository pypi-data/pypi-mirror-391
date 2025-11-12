from __future__ import annotations
from .core.http import HttpClient


class Tags:
    def __init__(self, http: HttpClient):
        self.http = http

    def get_by_project_id(self, project_id: str):
        """
        Retrieve Tags by Project ID
        GET /tagsbyprojectId/{projectID}
        """
        return self.http.request("GET", f"/tagsbyprojectId/{project_id}")


