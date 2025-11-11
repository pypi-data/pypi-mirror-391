# src/email_insights.py
import os
from typing import Optional, Dict, Any, List, Union
import openapi_client
from openapi_client.configuration import Configuration as ApiConfiguration
from openapi_client.api_client import ApiClient
from openapi_client.api.email_insights_api import EmailInsightsApi
from openapi_client.models.analyze_email_request import AnalyzeEmailRequest
from openapi_client.models.batch_analyze_emails_request import BatchAnalyzeEmailsRequest
from openapi_client.models.export_request import ExportRequest
from openapi_client.exceptions import ApiException


class EmailInsights:
    def __init__(self, api_key: str, api_instance: Optional[EmailInsightsApi] = None):
        """
        Initialize the EmailInsights class with the provided API key.

        :param api_key: The API key for authentication.
        :param api_instance: Optional API instance for testing purposes.
        """
        self.config = ApiConfiguration()
        self.config.api_key = {"opportifyToken": api_key}
        self.host = "https://api.opportify.ai"
        self.prefix = "insights"
        self.version = "v1"
        self.debug_mode = False
        self.final_url = ""
        self.config_changed = False
        
        self._update_final_url()
        
        if api_instance:
            self.api_instance = api_instance
        else:
            self._refresh_api_instance(first_run=True)


    def _refresh_api_instance(self, first_run: bool = False) -> None:
        """
        Ensures API instance is updated only if config has changed.
        
        :param first_run: Whether this is the first initialization.
        """
        if not self.config_changed and not first_run:
            return
        
        self._update_final_url()
        self.config.host = self.final_url
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = EmailInsightsApi(api_client)
        self.config_changed = False

    def _update_final_url(self) -> None:
        """
        Updates the final URL used for API requests.
        """
        base = self.host.rstrip('/')
        segments = []
        
        prefix = self.prefix.strip('/')
        if prefix:
            segments.append(prefix)
        
        version = self.version.strip('/')
        if version:
            segments.append(version)
        
        self.final_url = base + ('/' + '/'.join(segments) if segments else '')

    def analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the email with the given parameters.

        :param params: Dictionary containing parameters for email analysis.
        :return: The analysis result as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        # Ensure latest config before API call
        self._refresh_api_instance()
        
        params = self._normalize_request(params)
        analyze_email_request = AnalyzeEmailRequest(**params)

        try:
            result = self.api_instance.analyze_email(analyze_email_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def batch_analyze(self, params: Dict[str, Any], content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a batch of emails for analysis.

        :param params: Dictionary containing parameters for batch email analysis.
        :param content_type: Optional content type (defaults to application/json).
                           Supported: 'application/json', 'multipart/form-data', 'text/plain'
        :return: The batch job information as a dictionary (job_id, status, etc.).
        :raises Exception: If an API exception occurs.
        """
        # Ensure latest config before API call
        self._refresh_api_instance()
        
        # Default to application/json if not specified
        content_type = content_type or 'application/json'

        try:
            if content_type == 'application/json':
                params = self._normalize_batch_request(params)
                batch_analyze_emails_request = BatchAnalyzeEmailsRequest(**params)
                result = self.api_instance.batch_analyze_emails(
                    batch_analyze_emails_request,
                    _content_type=content_type
                )
            elif content_type == 'multipart/form-data':
                if 'file' not in params or not os.path.exists(params['file']):
                    raise ValueError('File parameter is required and must be a valid file path')
                
                with open(params['file'], 'rb') as file_handle:
                    # Create multipart data
                    files = {'file': (os.path.basename(params['file']), file_handle)}
                    data = {}
                    
                    # Add optional parameters
                    enable_ai = self._resolve_boolean(params, ['enable_ai', 'enableAi'])
                    if enable_ai is not None:
                        data['enable_ai'] = 'true' if enable_ai else 'false'
                    
                    enable_auto_correction = self._resolve_boolean(params, ['enable_auto_correction', 'enableAutoCorrection'])
                    if enable_auto_correction is not None:
                        data['enable_auto_correction'] = 'true' if enable_auto_correction else 'false'
                    
                    # Add name parameter if provided
                    if 'name' in params:
                        data['name'] = str(params['name'])
                    
                    # Prepare the request body as multipart
                    multipart_data = self._prepare_multipart_data(files, data)
                    result = self.api_instance.batch_analyze_emails(
                        multipart_data,
                        _content_type=content_type
                    )
            elif content_type == 'text/plain':
                if 'text' not in params:
                    raise ValueError('Text parameter is required for text/plain content type')
                
                result = self.api_instance.batch_analyze_emails(
                    params['text'],
                    _content_type=content_type
                )
            else:
                raise ValueError(f'Unsupported content type: {content_type}')

            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def batch_analyze_file(self, file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Submit a batch of emails for analysis using a file.

        :param file_path: Path to the file containing emails (CSV or text).
        :param options: Additional options like enableAi, enableAutoCorrection, name.
        :return: The batch job information as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        options = options or {}
        params = {'file': file_path, **options}
        return self.batch_analyze(params, 'multipart/form-data')

    def get_batch_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a batch email analysis job.

        :param job_id: The unique identifier of the batch job.
        :return: The batch job status as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        # Ensure latest config before API call
        self._refresh_api_instance()

        try:
            result = self.api_instance.get_email_batch_status(job_id)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def create_batch_export(self, job_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Request a custom export for a completed email batch job.

        :param job_id: The unique identifier of the batch job.
        :param payload: Optional export configuration (export_type, filters, columns).
        :return: The export creation response as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        self._refresh_api_instance()
        
        job_id = job_id.strip()
        if not job_id:
            raise ValueError('Job ID cannot be empty when creating an export.')
        
        payload = payload or {}
        normalized_payload = self._normalize_export_request(payload)
        export_request = ExportRequest(**normalized_payload) if normalized_payload else None

        try:
            result = self.api_instance.create_email_batch_export(job_id, export_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def get_batch_export_status(self, job_id: str, export_id: str) -> Dict[str, Any]:
        """
        Retrieve the status of a previously requested email batch export.

        :param job_id: The unique identifier of the batch job.
        :param export_id: The unique identifier of the export.
        :return: The export status as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        self._refresh_api_instance()
        
        job_id = job_id.strip()
        export_id = export_id.strip()
        
        if not job_id or not export_id:
            raise ValueError('Job ID and export ID are required to fetch export status.')

        try:
            result = self.api_instance.get_email_batch_export_status(job_id, export_id)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def set_host(self, host: str) -> "EmailInsights":
        """
        Set the host.

        :param host: The host URL.
        :return: The current instance for chaining.
        """
        if self.host != host:
            self.host = host
            self.config_changed = True
        return self

    def set_version(self, version: str) -> "EmailInsights":
        """
        Set the version.

        :param version: The API version.
        :return: The current instance for chaining.
        """
        if self.version != version:
            self.version = version
            self.config_changed = True
        return self

    def set_prefix(self, prefix: str) -> "EmailInsights":
        """
        Set the prefix.

        :param prefix: The URL prefix.
        :return: The current instance for chaining.
        """
        prefix = prefix.strip('/')
        if self.prefix != prefix:
            self.prefix = prefix
            self.config_changed = True
        return self

    def set_debug_mode(self, debug_mode: bool) -> "EmailInsights":
        """
        Set the debug mode.

        :param debug_mode: Enable or disable debug mode.
        :return: The current instance for chaining.
        """
        if self.debug_mode != debug_mode:
            self.debug_mode = debug_mode
            self.config_changed = True
        return self

    def _normalize_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the request parameters.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        if 'email' not in params:
            raise ValueError('The email parameter is required for analysis.')
        
        normalized = {}
        normalized["email"] = str(params["email"])
        
        # Only include optional parameters if explicitly provided by user
        enable_ai = self._resolve_boolean(params, ['enable_ai', 'enableAi'])
        if enable_ai is not None:
            normalized["enable_ai"] = enable_ai
        
        enable_auto_correction = self._resolve_boolean(params, ['enable_auto_correction', 'enableAutoCorrection'])
        if enable_auto_correction is not None:
            normalized["enable_auto_correction"] = enable_auto_correction
        
        enable_domain_enrichment = self._resolve_boolean(params, ['enable_domain_enrichment', 'enableDomainEnrichment'])
        if enable_domain_enrichment is not None:
            normalized["enable_domain_enrichment"] = enable_domain_enrichment

        return normalized

    def _normalize_batch_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the batch request parameters.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        if 'emails' not in params:
            raise ValueError("'emails' parameter is required for batch analysis")
        
        emails = params['emails']
        if not isinstance(emails, list):
            raise ValueError("'emails' parameter must be a list")
        
        normalized = {}
        normalized["emails"] = [str(email) for email in emails]

        enable_ai = self._resolve_boolean(params, ['enable_ai', 'enableAi'])
        if enable_ai is not None:
            normalized['enable_ai'] = enable_ai

        enable_auto_correction = self._resolve_boolean(params, ['enable_auto_correction', 'enableAutoCorrection'])
        if enable_auto_correction is not None:
            normalized['enable_auto_correction'] = enable_auto_correction

        # Add name parameter if provided
        if 'name' in params:
            normalized['name'] = str(params['name'])

        return normalized

    def _normalize_export_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize export payload for batch exports.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        normalized = {}

        if self._has_any_key(params, ['export_type', 'exportType']):
            value = params.get('export_type') or params.get('exportType')
            normalized['export_type'] = str(value).lower()

        if 'filters' in params and params['filters'] is not None:
            if not isinstance(params['filters'], dict):
                raise ValueError('Filters must be provided as a dictionary.')
            normalized['filters'] = params['filters']

        if 'columns' in params and params['columns'] is not None:
            if not isinstance(params['columns'], list):
                raise ValueError('Columns must be provided as a list.')
            normalized['columns'] = [str(column) for column in params['columns']]

        return normalized

    def _has_any_key(self, params: Dict[str, Any], keys: List[str]) -> bool:
        """
        Check if params has any of the specified keys.

        :param params: The parameters dictionary.
        :param keys: List of keys to check.
        :return: True if any key exists.
        """
        return any(key in params for key in keys)

    def _resolve_boolean(self, params: Dict[str, Any], keys: List[str], default: Optional[bool] = None) -> Optional[bool]:
        """
        Resolve boolean value from params using multiple possible keys.

        :param params: The parameters dictionary.
        :param keys: List of possible keys.
        :param default: Default value if none found.
        :return: Boolean value or default.
        """
        for key in keys:
            if key in params:
                return self._to_boolean(params[key], key)
        return default

    def _to_boolean(self, value: Any, parameter_name: str) -> bool:
        """
        Convert a value to boolean.

        :param value: The value to convert.
        :param parameter_name: Name for error messages.
        :return: Boolean value.
        """
        if isinstance(value, bool):
            return value
        
        if value in (1, 0, '1', '0'):
            return bool(int(value))
        
        if isinstance(value, str):
            value_lower = value.lower()
            if value_lower in ('true', 'yes', '1'):
                return True
            if value_lower in ('false', 'no', '0'):
                return False
        
        raise ValueError(f'Invalid boolean value provided for {parameter_name}')

    def _prepare_multipart_data(self, files: Dict[str, Any], data: Dict[str, Any]) -> Any:
        """
        Prepare multipart form data for file upload.
        
        :param files: Files dictionary.
        :param data: Additional form data.
        :return: Prepared multipart data.
        """
        # For Python SDK, we'll pass the file path directly and let the OpenAPI client handle it
        # This is a placeholder that may need adjustment based on how the openapi_client handles multipart
        return {**files, **data}
