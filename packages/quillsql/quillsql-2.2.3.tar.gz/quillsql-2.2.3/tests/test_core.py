import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quillsql.core import Quill


@patch("quillsql.core.CachedConnection")
def test_query_handles_none_tenant_flag_responses(mock_cached_connection):
    mock_connection = MagicMock()
    mock_connection.database_type = "PostgreSQL"
    mock_cached_connection.return_value = mock_connection

    quill = Quill(
        private_key="test-key",
        database_type="PostgreSQL",
        database_config={},
    )

    quill.run_queries = MagicMock(
        side_effect=[
            {"queryResults": [None]},
            {"queryResults": []},
        ]
    )

    def post_quill_side_effect(path, payload):
        if path == "tenant-mapped-flags":
            return {
                "queries": [
                    'SELECT * FROM (SELECT "id" AS "customer_id", "name" AS "quill_label", "id" AS "quill_flag" FROM "public"."customers") AS "subq_owner_query" WHERE "customer_id" IN (2)'
                ],
                "metadata": {"queryOrder": ["customer_id"]},
            }
        return {"queries": [], "metadata": {}}

    quill.post_quill = MagicMock(side_effect=post_quill_side_effect)

    result = quill.query(
        tenants=["tenant-1"],
        metadata={
            "task": "report",
            "clientId": "client-123",
            "reportId": "report-456",
            "databaseType": "PostgreSQL",
        },
    )

    assert result["status"] == "success"
    assert result["data"] == {}

