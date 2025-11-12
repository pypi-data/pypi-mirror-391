from __future__ import annotations
from typing import Any, Optional, TypedDict, List, Dict, Union

from .core.http import HttpClient

class ObjectField(TypedDict, total=False):
    """Field descriptor for object-type columns."""
    key: str
    keyType: str


class AgentflowTrigger(TypedDict, total=False):
    """Trigger configuration attached to a table or column.

    Note: exact schemas for `condition` and `filters` may evolve; we leave them open.
    """
    _id: str
    id: str
    condition: Dict[str, Any]
    name: Optional[str]
    goal: str
    agentflow_id: Optional[str]
    filters: List[Dict[str, Any]]
    schedule_time: Optional[str]
    event: str
    start_from_agent_id: Optional[str]
    trigger_type: str  # e.g. "coworker"


class Column(TypedDict, total=False):
    """Column definition for a table."""
    column_name: str
    column_type: str
    column_id: str
    array_type: Optional[str]
    default_value: Union[Any, List[Any], Dict[str, Any]]
    object_fields: List[ObjectField]
    triggers: List[AgentflowTrigger]
    enum_options: List[str]


class CreateTableInput(TypedDict, total=False):
    """Typed input for creating a table.

    Required keys: projectID, table_name
    Optional keys: columns, triggers
    """
    projectID: str
    table_name: str
    columns: List[Column]
    triggers: List[AgentflowTrigger]


class Tables:
    def __init__(self, http: HttpClient):
        self.http = http

    # Tables
    def create_table(self, project_id: str, spec: CreateTableInput):
        """Create a new table.

        Args:
            project_id: The project ID (placed into query as `projectID`).
            spec: Table specification containing at least `table_name`.

        The backend expects `projectID` in both query params and JSON body.
        """
        # API expects projectID as query param and in body with 'projectID' casing
        params = {"projectID": project_id}
        body = {"projectID": project_id, **spec}
        return self.http.request("POST", "/create/table", params=params, json=body)

    # New: POST /storage/{projectID}/{collection_name}
    def create_records_by_collection(self, project_id: str, collection_name: str, records: List[dict]):
        return self.http.request("POST", f"/storage/{project_id}/{collection_name}", json=records)

    def list_tables(self, project_id: str):
        return self.http.request("GET", f"/storage/{project_id}")

    def get_table(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}")

    def get_table_view(self, table_id: str):
        return self.http.request("GET", f"/table/view/{table_id}")

    def rename_table(self, project_id: str, table_id: str, new_name: str):
        return self.http.request("POST", f"/table/rename/{project_id}", json={"tableId": table_id, "newName": new_name})

    # Columns
    def get_columns(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/column/storage/{project_id}/{table_id}")

    def edit_columns(self, table_id: str, spec: dict):
        return self.http.request("POST", f"/edit/columns/{table_id}", json=spec)

    def delete_column(self, project_id: str, column_id: str):
        return self.http.request("DELETE", f"/delete/column/{project_id}", json={"columnId": column_id})

    # New: POST /column/storage/{projectID}/{table_id}?ignore_existing_columns=...
    def add_columns(self, project_id: str, table_id: str, columns: List[Column], ignore_existing_columns: Optional[bool] = None):
        params: Dict[str, Any] = {}
        if ignore_existing_columns is not None:
            params["ignore_existing_columns"] = ignore_existing_columns
        return self.http.request("POST", f"/column/storage/{project_id}/{table_id}", params=params or None, json=columns)

    # New: PUT /edit/columns/{projectId} with rename body
    def update_column_name(self, project_id: str, *, column_id: str, column_name: str, table_id: str):
        body = {"column_id": column_id, "column_name": column_name, "table_id": table_id}
        return self.http.request("PUT", f"/edit/columns/{project_id}", json=body)

    # New: PATCH /edit/columns/{table_id} with full Column
    def patch_column(self, table_id: str, column: Column):
        return self.http.request("PATCH", f"/edit/columns/{table_id}", json=column)

    # New: DELETE /delete/column/{projectId} body { table_id, column_id }
    def delete_column_extended(self, project_id: str, *, table_id: str, column_id: str):
        return self.http.request("DELETE", f"/delete/column/{project_id}", json={"table_id": table_id, "column_id": column_id})

    # Records
    def create_record(self, project_id: str, table_id: str, record: dict):
        return self.http.request("POST", f"/storage/{project_id}/{table_id}", json=record)

    def get_record(self, project_id: str, table_id: str, record_id: str):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}/{record_id}")

    def update_record(self, project_id: str, table_id: str, record_id: str, record: dict):
        return self.http.request("PUT", f"/storage/{project_id}/{table_id}/{record_id}", json=record)

    def delete_record(self, project_id: str, table_id: str, record_id: str):
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}/{record_id}")

    def list_records(self, project_id: str, table_id: str, query: Optional[dict] = None):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}", params=query)

    # New: DELETE /storage/{projectID}/{tableId} body { storage_ids: [] }
    def delete_records_bulk(self, project_id: str, table_id: str, storage_ids: List[str]):
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}", json={"storage_ids": storage_ids})

    # New: PUT /bulk/storage/{projectID}/{table_id} body { records, record_ids: { storage_ids: [] } }
    def bulk_update_records(self, project_id: str, table_id: str, *, records: Dict[str, Any], record_ids: Dict[str, Any]):
        return self.http.request("PUT", f"/bulk/storage/{project_id}/{table_id}", json={"records": records, "record_ids": record_ids})

    def export(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/table_data/storage/{table_id}/export")

    # New: PUT /table/rename/{projectID} body { table_id, table_name, triggers? }
    def rename_table_extended(self, project_id: str, *, table_id: str, table_name: str, triggers: Optional[List[AgentflowTrigger]] = None):
        body: Dict[str, Any] = {"table_id": table_id, "table_name": table_name}
        if triggers is not None:
            body["triggers"] = triggers
        return self.http.request("PUT", f"/table/rename/{project_id}", json=body)

    # New: POST /table/column_mapper
    def column_mapper(self, *, column_names: List[Dict[str, str]], csv_headers: List[str]):
        body = {"column_names": column_names, "csv_headers": csv_headers}
        return self.http.request("POST", "/table/column_mapper", json=body)

    # New: POST /table/fieldcount/{project_id}/{table_id}
    def field_count(self, project_id: str, table_id: str, filters: List[Dict[str, Any]]):
        return self.http.request("POST", f"/table/fieldcount/{project_id}/{table_id}", json=filters)
