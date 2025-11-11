# coding: utf-8

"""
Unit tests for EmailInsights wrapper class.

Tests cover all new features including:
- Configuration management (prefix, host, version, debug mode)
- Multiple content types for batch analysis
- Batch file upload
- Batch export creation and status
- Parameter normalization
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from opportify_sdk import EmailInsights
from openapi_client.exceptions import ApiException


class TestEmailInsightsWrapper(unittest.TestCase):
    """EmailInsights wrapper unit tests"""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.api_key = "test-api-key-123"
        self.mock_api = Mock()
        self.email_insights = EmailInsights(self.api_key, api_instance=self.mock_api)

    def tearDown(self) -> None:
        """Clean up after tests."""
        pass

    # ========== Configuration Tests ==========

    def test_initialization(self) -> None:
        """Test EmailInsights initialization with default values."""
        client = EmailInsights("test-key")
        self.assertEqual(client.host, "https://api.opportify.ai")
        self.assertEqual(client.prefix, "insights")
        self.assertEqual(client.version, "v1")
        self.assertEqual(client.debug_mode, False)
        self.assertEqual(client.final_url, "https://api.opportify.ai/insights/v1")

    def test_set_host(self) -> None:
        """Test setting custom host."""
        self.email_insights.set_host("https://api.staging.opportify.ai")
        self.assertEqual(self.email_insights.host, "https://api.staging.opportify.ai")
        self.assertTrue(self.email_insights.config_changed)

    def test_set_version(self) -> None:
        """Test setting custom API version."""
        self.email_insights.set_version("v2")
        self.assertEqual(self.email_insights.version, "v2")
        self.assertTrue(self.email_insights.config_changed)

    def test_set_prefix(self) -> None:
        """Test setting custom URL prefix."""
        self.email_insights.set_prefix("api/insights")
        self.assertEqual(self.email_insights.prefix, "api/insights")
        self.assertTrue(self.email_insights.config_changed)

    def test_set_prefix_strips_slashes(self) -> None:
        """Test that prefix strips leading/trailing slashes."""
        self.email_insights.set_prefix("/api/insights/")
        self.assertEqual(self.email_insights.prefix, "api/insights")

    def test_set_debug_mode(self) -> None:
        """Test enabling debug mode."""
        self.email_insights.set_debug_mode(True)
        self.assertTrue(self.email_insights.debug_mode)
        self.assertTrue(self.email_insights.config_changed)

    def test_method_chaining(self) -> None:
        """Test that setter methods support chaining."""
        result = (self.email_insights
                  .set_host("https://custom.api.com")
                  .set_version("v2")
                  .set_prefix("custom")
                  .set_debug_mode(True))
        self.assertIs(result, self.email_insights)

    def test_update_final_url(self) -> None:
        """Test final URL construction."""
        self.email_insights.host = "https://api.example.com"
        self.email_insights.prefix = "insights"
        self.email_insights.version = "v1"
        self.email_insights._update_final_url()
        self.assertEqual(self.email_insights.final_url, "https://api.example.com/insights/v1")

    def test_update_final_url_no_prefix(self) -> None:
        """Test final URL construction without prefix."""
        self.email_insights.host = "https://api.example.com"
        self.email_insights.prefix = ""
        self.email_insights.version = "v1"
        self.email_insights._update_final_url()
        self.assertEqual(self.email_insights.final_url, "https://api.example.com/v1")

    def test_update_final_url_no_version(self) -> None:
        """Test final URL construction without version."""
        self.email_insights.host = "https://api.example.com"
        self.email_insights.prefix = "insights"
        self.email_insights.version = ""
        self.email_insights._update_final_url()
        self.assertEqual(self.email_insights.final_url, "https://api.example.com/insights")

    # ========== Analyze Tests ==========

    def test_analyze_success(self) -> None:
        """Test successful email analysis."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"email": "test@example.com", "isDeliverable": True}
        self.mock_api.analyze_email.return_value = mock_response

        params = {
            "email": "test@example.com",
            "enableAi": True,
            "enableAutoCorrection": True
        }
        result = self.email_insights.analyze(params)

        self.assertEqual(result["email"], "test@example.com")
        self.assertTrue(result["isDeliverable"])
        self.mock_api.analyze_email.assert_called_once()

    def test_analyze_missing_email(self) -> None:
        """Test analyze raises error when email is missing."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.analyze({})
        self.assertIn("email parameter is required", str(context.exception))

    def test_analyze_api_exception(self) -> None:
        """Test analyze handles API exceptions."""
        self.mock_api.analyze_email.side_effect = ApiException(status=403, reason="Forbidden")

        params = {"email": "test@example.com"}
        with self.assertRaises(Exception) as context:
            self.email_insights.analyze(params)
        self.assertIn("API exception", str(context.exception))

    def test_analyze_api_exception_401_unauthorized(self) -> None:
        """Test analyze handles 401 Unauthorized (invalid API key)."""
        self.mock_api.analyze_email.side_effect = ApiException(status=401, reason="Unauthorized")

        params = {"email": "test@example.com"}
        with self.assertRaises(Exception) as context:
            self.email_insights.analyze(params)
        self.assertIn("API exception", str(context.exception))

    def test_analyze_api_exception_402_payment_required(self) -> None:
        """Test analyze handles 402 Payment Required (quota exceeded)."""
        self.mock_api.analyze_email.side_effect = ApiException(status=402, reason="Payment Required")

        params = {"email": "test@example.com"}
        with self.assertRaises(Exception) as context:
            self.email_insights.analyze(params)
        self.assertIn("API exception", str(context.exception))

    def test_analyze_api_exception_429_rate_limit(self) -> None:
        """Test analyze handles 429 Too Many Requests."""
        self.mock_api.analyze_email.side_effect = ApiException(status=429, reason="Too Many Requests")

        params = {"email": "test@example.com"}
        with self.assertRaises(Exception) as context:
            self.email_insights.analyze(params)
        self.assertIn("API exception", str(context.exception))

    def test_analyze_api_exception_500_server_error(self) -> None:
        """Test analyze handles 500 Internal Server Error."""
        self.mock_api.analyze_email.side_effect = ApiException(status=500, reason="Internal Server Error")

        params = {"email": "test@example.com"}
        with self.assertRaises(Exception) as context:
            self.email_insights.analyze(params)
        self.assertIn("API exception", str(context.exception))

    # ========== Batch Analyze Tests (JSON) ==========

    def test_batch_analyze_json(self) -> None:
        """Test batch analyze with JSON content type."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"job_id": "job-123", "status": "PENDING"}
        self.mock_api.batch_analyze_emails.return_value = mock_response

        params = {
            "emails": ["test1@example.com", "test2@example.com"],
            "enableAi": True,
            "name": "Test Batch"
        }
        result = self.email_insights.batch_analyze(params)

        self.assertEqual(result["job_id"], "job-123")
        self.mock_api.batch_analyze_emails.assert_called_once()

    def test_batch_analyze_missing_emails(self) -> None:
        """Test batch analyze raises error when emails list is missing."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze({})
        self.assertIn("'emails' parameter is required", str(context.exception))

    def test_batch_analyze_emails_not_list(self) -> None:
        """Test batch analyze raises error when emails is not a list."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze({"emails": "not-a-list"})
        self.assertIn("'emails' parameter must be a list", str(context.exception))

    # ========== Batch Analyze Tests (Plain Text) ==========

    def test_batch_analyze_text_plain(self) -> None:
        """Test batch analyze with text/plain content type."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"job_id": "job-456", "status": "PENDING"}
        self.mock_api.batch_analyze_emails.return_value = mock_response

        params = {"text": "test1@example.com\ntest2@example.com"}
        result = self.email_insights.batch_analyze(params, "text/plain")

        self.assertEqual(result["job_id"], "job-456")
        self.mock_api.batch_analyze_emails.assert_called_once()

    def test_batch_analyze_text_plain_missing_text(self) -> None:
        """Test batch analyze text/plain raises error when text is missing."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze({}, "text/plain")
        self.assertIn("Text parameter is required", str(context.exception))

    # ========== Batch Analyze Tests (Multipart File) ==========

    @patch('builtins.open', new_callable=mock_open, read_data=b'email1@example.com\nemail2@example.com')
    @patch('os.path.exists')
    def test_batch_analyze_multipart(self, mock_exists, mock_file) -> None:
        """Test batch analyze with multipart/form-data content type."""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.to_dict.return_value = {"job_id": "job-789", "status": "PENDING"}
        self.mock_api.batch_analyze_emails.return_value = mock_response

        params = {
            "file": "/path/to/emails.csv",
            "enableAi": True,
            "name": "File Upload Test"
        }
        result = self.email_insights.batch_analyze(params, "multipart/form-data")

        self.assertEqual(result["job_id"], "job-789")
        mock_file.assert_called_once_with("/path/to/emails.csv", "rb")

    def test_batch_analyze_multipart_missing_file(self) -> None:
        """Test batch analyze multipart raises error when file is missing."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze({}, "multipart/form-data")
        self.assertIn("File parameter is required", str(context.exception))

    @patch('os.path.exists')
    def test_batch_analyze_multipart_file_not_exists(self, mock_exists) -> None:
        """Test batch analyze multipart raises error when file doesn't exist."""
        mock_exists.return_value = False
        params = {"file": "/nonexistent/file.csv"}
        
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze(params, "multipart/form-data")
        self.assertIn("File parameter is required", str(context.exception))

    # ========== Batch Analyze File Tests ==========

    @patch('builtins.open', new_callable=mock_open, read_data=b'email@example.com')
    @patch('os.path.exists')
    def test_batch_analyze_file(self, mock_exists, mock_file) -> None:
        """Test batch_analyze_file convenience method."""
        mock_exists.return_value = True
        mock_response = Mock()
        mock_response.to_dict.return_value = {"job_id": "job-999", "status": "PENDING"}
        self.mock_api.batch_analyze_emails.return_value = mock_response

        result = self.email_insights.batch_analyze_file(
            "/path/to/file.csv",
            {"enableAi": True, "name": "Convenience Test"}
        )

        self.assertEqual(result["job_id"], "job-999")

    # ========== Unsupported Content Type Test ==========

    def test_batch_analyze_unsupported_content_type(self) -> None:
        """Test batch analyze raises error for unsupported content type."""
        params = {"emails": ["test@example.com"]}
        
        with self.assertRaises(ValueError) as context:
            self.email_insights.batch_analyze(params, "application/xml")
        self.assertIn("Unsupported content type", str(context.exception))

    # ========== Batch Status Tests ==========

    def test_get_batch_status(self) -> None:
        """Test getting batch status."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            "job_id": "job-123",
            "status": "COMPLETED",
            "progress": 100
        }
        self.mock_api.get_email_batch_status.return_value = mock_response

        result = self.email_insights.get_batch_status("job-123")

        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["progress"], 100)
        self.mock_api.get_email_batch_status.assert_called_once_with("job-123")

    def test_get_batch_status_api_exception(self) -> None:
        """Test get_batch_status handles API exceptions."""
        self.mock_api.get_email_batch_status.side_effect = ApiException(status=404, reason="Job Not Found")

        with self.assertRaises(Exception) as context:
            self.email_insights.get_batch_status("invalid-job-id")
        self.assertIn("API exception", str(context.exception))

    # ========== Batch Export Tests ==========

    def test_create_batch_export(self) -> None:
        """Test creating batch export."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"export_id": "export-123", "status": "PENDING"}
        self.mock_api.create_email_batch_export.return_value = mock_response

        payload = {
            "exportType": "csv",
            "columns": ["email", "isDeliverable", "riskReport.score"],
            "filters": {"isDeliverable": "true"}
        }
        result = self.email_insights.create_batch_export("job-123", payload)

        self.assertEqual(result["export_id"], "export-123")
        self.mock_api.create_email_batch_export.assert_called_once()

    def test_create_batch_export_empty_job_id(self) -> None:
        """Test create_batch_export raises error for empty job ID."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.create_batch_export("  ", {})
        self.assertIn("Job ID cannot be empty", str(context.exception))

    def test_create_batch_export_no_payload(self) -> None:
        """Test create_batch_export works with no payload."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {"export_id": "export-456", "status": "PENDING"}
        self.mock_api.create_email_batch_export.return_value = mock_response

        result = self.email_insights.create_batch_export("job-123")

        self.assertEqual(result["export_id"], "export-456")

    def test_get_batch_export_status(self) -> None:
        """Test getting batch export status."""
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            "export_id": "export-123",
            "status": "COMPLETED",
            "download_url": "https://example.com/download/export-123.csv"
        }
        self.mock_api.get_email_batch_export_status.return_value = mock_response

        result = self.email_insights.get_batch_export_status("job-123", "export-123")

        self.assertEqual(result["status"], "COMPLETED")
        self.assertIn("download_url", result)
        self.mock_api.get_email_batch_export_status.assert_called_once_with("job-123", "export-123")

    def test_get_batch_export_status_empty_ids(self) -> None:
        """Test get_batch_export_status raises error for empty IDs."""
        with self.assertRaises(ValueError) as context:
            self.email_insights.get_batch_export_status("  ", "export-123")
        self.assertIn("Job ID and export ID are required", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.email_insights.get_batch_export_status("job-123", "  ")
        self.assertIn("Job ID and export ID are required", str(context.exception))

    def test_create_batch_export_api_exception(self) -> None:
        """Test create_batch_export handles API exceptions."""
        self.mock_api.create_email_batch_export.side_effect = ApiException(status=404, reason="Job Not Found")

        with self.assertRaises(Exception) as context:
            self.email_insights.create_batch_export("invalid-job-id", {})
        self.assertIn("API exception", str(context.exception))

    def test_create_batch_export_job_not_ready(self) -> None:
        """Test create_batch_export handles job not ready error."""
        self.mock_api.create_email_batch_export.side_effect = ApiException(status=409, reason="Conflict")

        with self.assertRaises(Exception) as context:
            self.email_insights.create_batch_export("pending-job-id", {})
        self.assertIn("API exception", str(context.exception))

    def test_get_batch_export_status_api_exception(self) -> None:
        """Test get_batch_export_status handles API exceptions."""
        self.mock_api.get_email_batch_export_status.side_effect = ApiException(status=404, reason="Export Not Found")

        with self.assertRaises(Exception) as context:
            self.email_insights.get_batch_export_status("job-123", "invalid-export-id")
        self.assertIn("API exception", str(context.exception))

    def test_batch_analyze_api_exception(self) -> None:
        """Test batch_analyze handles API exceptions."""
        self.mock_api.batch_analyze_emails.side_effect = ApiException(status=413, reason="Payload Too Large")

        params = {"emails": ["test@example.com"]}
        with self.assertRaises(Exception) as context:
            self.email_insights.batch_analyze(params)
        self.assertIn("API exception", str(context.exception))

    # ========== Normalization Tests ==========

    def test_normalize_request_camelcase(self) -> None:
        """Test request normalization with camelCase parameters."""
        params = {
            "email": "test@example.com",
            "enableAi": True,
            "enableAutoCorrection": False,
            "enableDomainEnrichment": True
        }
        normalized = self.email_insights._normalize_request(params)

        self.assertEqual(normalized["email"], "test@example.com")
        self.assertTrue(normalized["enable_ai"])
        self.assertFalse(normalized["enable_auto_correction"])
        self.assertTrue(normalized["enable_domain_enrichment"])

    def test_normalize_request_snake_case(self) -> None:
        """Test request normalization with snake_case parameters."""
        params = {
            "email": "test@example.com",
            "enable_ai": True,
            "enable_auto_correction": False
        }
        normalized = self.email_insights._normalize_request(params)

        self.assertTrue(normalized["enable_ai"])
        self.assertFalse(normalized["enable_auto_correction"])

    def test_normalize_request_without_optional_params(self) -> None:
        """Test request normalization when optional params are not provided."""
        params = {
            "email": "test@example.com"
        }
        normalized = self.email_insights._normalize_request(params)

        self.assertEqual(normalized["email"], "test@example.com")
        # Optional params should not be in normalized dict if not provided
        self.assertNotIn("enable_ai", normalized)
        self.assertNotIn("enable_auto_correction", normalized)
        self.assertNotIn("enable_domain_enrichment", normalized)

    def test_normalize_batch_request_with_name(self) -> None:
        """Test batch request normalization includes name parameter."""
        params = {
            "emails": ["test@example.com"],
            "name": "My Batch Job",
            "enableAi": True
        }
        normalized = self.email_insights._normalize_batch_request(params)

        self.assertEqual(normalized["name"], "My Batch Job")
        self.assertTrue(normalized["enable_ai"])

    def test_normalize_export_request(self) -> None:
        """Test export request normalization."""
        params = {
            "exportType": "CSV",
            "filters": {"isDeliverable": "true"},
            "columns": ["email", "riskReport.score"]
        }
        normalized = self.email_insights._normalize_export_request(params)

        self.assertEqual(normalized["export_type"], "csv")  # Lowercased
        self.assertEqual(normalized["filters"], {"isDeliverable": "true"})
        self.assertEqual(normalized["columns"], ["email", "riskReport.score"])

    def test_normalize_export_request_invalid_filters(self) -> None:
        """Test export normalization raises error for invalid filters."""
        params = {"filters": "not-a-dict"}
        
        with self.assertRaises(ValueError) as context:
            self.email_insights._normalize_export_request(params)
        self.assertIn("Filters must be provided as a dictionary", str(context.exception))

    def test_normalize_export_request_invalid_columns(self) -> None:
        """Test export normalization raises error for invalid columns."""
        params = {"columns": "not-a-list"}
        
        with self.assertRaises(ValueError) as context:
            self.email_insights._normalize_export_request(params)
        self.assertIn("Columns must be provided as a list", str(context.exception))

    # ========== Boolean Resolution Tests ==========

    def test_resolve_boolean_true_values(self) -> None:
        """Test boolean resolution for various true values."""
        test_cases = [True, 1, "1", "true", "True", "TRUE", "yes", "Yes"]
        for value in test_cases:
            result = self.email_insights._to_boolean(value, "test_param")
            self.assertTrue(result, f"Failed for value: {value}")

    def test_resolve_boolean_false_values(self) -> None:
        """Test boolean resolution for various false values."""
        test_cases = [False, 0, "0", "false", "False", "FALSE", "no", "No"]
        for value in test_cases:
            result = self.email_insights._to_boolean(value, "test_param")
            self.assertFalse(result, f"Failed for value: {value}")

    def test_resolve_boolean_invalid_value(self) -> None:
        """Test boolean resolution raises error for invalid values."""
        with self.assertRaises(ValueError) as context:
            self.email_insights._to_boolean("invalid", "test_param")
        self.assertIn("Invalid boolean value", str(context.exception))

    def test_resolve_boolean_with_default(self) -> None:
        """Test boolean resolution with default value."""
        params = {}
        result = self.email_insights._resolve_boolean(params, ["enable_ai"], True)
        self.assertTrue(result)

    def test_has_any_key(self) -> None:
        """Test _has_any_key helper method."""
        params = {"enable_ai": True, "email": "test@example.com"}
        
        self.assertTrue(self.email_insights._has_any_key(params, ["enable_ai", "enableAi"]))
        self.assertFalse(self.email_insights._has_any_key(params, ["not_present", "alsoNotPresent"]))


if __name__ == '__main__':
    unittest.main()
