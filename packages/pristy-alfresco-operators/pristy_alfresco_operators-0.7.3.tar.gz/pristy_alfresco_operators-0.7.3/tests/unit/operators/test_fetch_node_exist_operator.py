# SPDX-FileCopyrightText: 2025 Jeci <info@jeci.fr>
#
# SPDX-License-Identifier: Apache-2.0

"""
Tests for AlfrescoFetchNodeExistOperator.
"""

import pytest
from unittest.mock import MagicMock
from airflow.exceptions import AirflowException
from pristy.alfresco_operator.fetch_node_exist_operator import (
    AlfrescoFetchNodeExistOperator,
)


class TestAlfrescoFetchNodeExistOperator:
    """Tests for AlfrescoFetchNodeExistOperator."""

    def test_node_exists_returns_true(self, mock_airflow_context):
        """Test that operator returns True when node exists (200 response)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create operator
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists", node_id="node-uuid-123"
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result is True

        # Verify HTTP call was made
        operator.http_hook.run.assert_called_once_with(
            endpoint="/alfresco/api/-default-/public/alfresco/versions/1/nodes/node-uuid-123",
            data={"include": "path"},
        )

    def test_node_not_found_returns_false(self, mock_airflow_context):
        """Test that operator returns False when node doesn't exist (404 response)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 404

        # Create operator
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists", node_id="nonexistent-uuid"
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result is False

    def test_node_error_raises_exception(self, mock_airflow_context):
        """Test that operator raises AirflowException for server errors (500)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = b"Internal Server Error"

        # Create operator
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists", node_id="node-uuid-123"
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute and assert exception
        with pytest.raises(AirflowException):
            operator.execute(mock_airflow_context)

    def test_fetch_node_exist_with_noderef(self, mock_airflow_context):
        """Test node existence check with full nodeRef format."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create operator with full nodeRef
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists",
            node_id="workspace://SpacesStore/node-uuid-123",
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result is True

        # Verify HTTP call extracts UUID from nodeRef
        operator.http_hook.run.assert_called_once_with(
            endpoint="/alfresco/api/-default-/public/alfresco/versions/1/nodes/node-uuid-123",
            data={"include": "path"},
        )

    def test_fetch_node_exist_with_mapped_argument(self, mock_airflow_context):
        """Test node existence check with mapped argument (dynamic task mapping)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create mock mapped argument
        mock_mapped_arg = MagicMock()
        mock_mapped_arg.resolve.return_value = "node-uuid-123"

        # Create operator with mapped argument
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists",
            node_id=mock_mapped_arg,
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute
        result = operator.execute(mock_airflow_context)

        # Assert
        assert result is True

        # Verify resolve was called
        mock_mapped_arg.resolve.assert_called_once_with(mock_airflow_context)

    def test_unauthorized_raises_exception(self, mock_airflow_context):
        """Test that operator raises AirflowException for authentication errors (401)."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.content = b"Unauthorized"

        # Create operator
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists", node_id="node-uuid-123"
        )

        # Mock the http_hook after initialization
        operator.http_hook = MagicMock()
        operator.http_hook.run.return_value = mock_response

        # Execute and assert exception
        with pytest.raises(AirflowException):
            operator.execute(mock_airflow_context)

    def test_http_endpoint_called_correctly(self, mock_airflow_context):
        """Test that the HTTP endpoint is called with correct parameters."""
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create operator with custom connection ID
        operator = AlfrescoFetchNodeExistOperator(
            task_id="test_exists",
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
