# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for AlfrescoFetchNodeOperator.
"""

import pytest
from unittest.mock import MagicMock
from pristy.alfresco_operator.fetch_node_operator import AlfrescoFetchNodeOperator


class TestAlfrescoFetchNodeOperator:
    """Tests for AlfrescoFetchNodeOperator."""

    def test_fetch_node_basic(self, sample_alfresco_node, mock_airflow_context):
        """Test basic node fetch with UUID."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": sample_alfresco_node}

        # Create operator
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch", node_id="node-uuid-123"
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result["id"] == "workspace://SpacesStore/node-uuid-123"
        assert result["name"] == "test-document.pdf"
        assert result["nodeType"] == "cm:content"

        # Verify HTTP call was made with correct endpoint
        operator.http_hook.run.assert_called_once_with(
            endpoint="/alfresco/api/-default-/public/alfresco/versions/1/nodes/node-uuid-123",
            data={"include": "path"},
        )

    def test_fetch_node_with_noderef(
        self, sample_alfresco_node, mock_airflow_context
    ):
        """Test node fetch with full nodeRef format (workspace://SpacesStore/{uuid})."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": sample_alfresco_node}

        # Create operator with full nodeRef
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch",
            node_id="workspace://SpacesStore/node-uuid-123",
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert result
        assert result["id"] == "workspace://SpacesStore/node-uuid-123"
        assert result["name"] == "test-document.pdf"

        # Verify HTTP call extracts UUID from nodeRef
        operator.http_hook.run.assert_called_once_with(
            endpoint="/alfresco/api/-default-/public/alfresco/versions/1/nodes/node-uuid-123",
            data={"include": "path"},
        )

    def test_fetch_node_with_uuid_only(
        self, sample_alfresco_node, mock_airflow_context
    ):
        """Test node fetch with plain UUID (no workspace:// prefix)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": sample_alfresco_node}

        # Create operator with plain UUID
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch",
            node_id="node-uuid-123",
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result["name"] == "test-document.pdf"

        # Verify HTTP call uses UUID as-is
        operator.http_hook.run.assert_called_once_with(
            endpoint="/alfresco/api/-default-/public/alfresco/versions/1/nodes/node-uuid-123",
            data={"include": "path"},
        )

    def test_fetch_node_with_mapped_argument(
        self, sample_alfresco_node, mock_airflow_context
    ):
        """Test node fetch with mapped argument (dynamic task mapping)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": sample_alfresco_node}

        # Create mock mapped argument
        mock_mapped_arg = MagicMock()
        mock_mapped_arg.resolve.return_value = "node-uuid-123"

        # Create operator with mapped argument
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch",
            node_id=mock_mapped_arg,
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result["name"] == "test-document.pdf"

        # Verify resolve was called
        mock_mapped_arg.resolve.assert_called_once_with(mock_airflow_context)

    def test_fetch_folder_node(self, sample_alfresco_folder, mock_airflow_context):
        """Test fetching a folder node."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": sample_alfresco_folder}

        # Create operator
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch",
            node_id="folder-uuid-456",
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result["id"] == "workspace://SpacesStore/folder-uuid-456"
        assert result["name"] == "Test Folder"
        assert result["isFolder"] is True
        assert result["nodeType"] == "cm:folder"

    def test_http_endpoint_called_correctly(self, mock_airflow_context):
        """Test that the HTTP endpoint is called with correct parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"entry": {"id": "test", "name": "Test"}}

        # Create operator
        operator = AlfrescoFetchNodeOperator(
            task_id="test_fetch",
            node_id="test-uuid",
            http_conn_id="custom_conn",
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        operator.execute(mock_airflow_context)

        # Verify the endpoint and data parameter
        call_args = operator.http_hook.run.call_args
        assert call_args[1]["endpoint"] == "/alfresco/api/-default-/public/alfresco/versions/1/nodes/test-uuid"
        assert call_args[1]["data"] == {"include": "path"}
