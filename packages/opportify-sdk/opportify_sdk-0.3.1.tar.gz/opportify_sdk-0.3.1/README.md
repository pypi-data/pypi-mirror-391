# Opportify-SDK-Python

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
    - [Calling Email Insights](#calling-email-insights)
    - [Calling IP Insights](#calling-ip-insights)
- [Batch Analysis (Email & IP)](#batch-analysis-email--ip)
    - [Batch Email Analysis (JSON)](#1-batch-email-analysis-json)
    - [Batch Email Analysis (Plain Text)](#2-batch-email-analysis-plain-text)
    - [Batch Email Analysis (File Upload)](#3-batch-email-analysis-file-upload)
    - [Batch IP Analysis (JSON)](#4-batch-ip-analysis-json)
    - [Batch IP Analysis (Plain Text)](#5-batch-ip-analysis-plain-text)
    - [Batch IP Analysis (File Upload)](#6-batch-ip-analysis-file-upload)
- [Batch Export Jobs](#batch-export-jobs)
    - [Email Batch Exports](#email-batch-exports)
    - [IP Batch Exports](#ip-batch-exports)
- [Enabling Debug Mode](#enabling-debug-mode)
- [Handling Errors](#handling-errors)
- [About this package](#about-this-package)

## Overview

The **Opportify Insights API** provides access to a powerful and up-to-date platform. With advanced data warehousing and AI-driven capabilities, this API is designed to empower your business to make informed, data-driven decisions and effectively assess potential risks.

[Sign Up Free](https://www.opportify.ai)

### Base URL
Use the following base URL for all API requests:

```plaintext
https://api.opportify.ai/insights/v1/<service>/<endpoint>
```

## Requirements

Requires Python [v3.8 or later](https://www.python.org/downloads/)

## Getting Started

First, install Opportify via the pip package manager:

```shell
pip install opportify-sdk
```

### Calling Email Insights

```python
from opportify_sdk import EmailInsights

email_insights = EmailInsights("YOUR-API-KEY-HERE")

params = {
    "email": "test@gmial.com",  # *gmial* - just an example to be auto-corrected
    "enableAi": True,
    "enableAutoCorrection": True,
    "enableDomainEnrichment": True  # Optional: include domain enrichment block
}

result = email_insights.analyze(params)
```

### Calling IP Insights

```python
from opportify_sdk import IpInsights

ip_insights = IpInsights("<YOUR-KEY-HERE>")

params = {
    "ip": "3.1.122.82",
    "enableAi": True
}

result = ip_insights.analyze(params)
```


## Batch Analysis (Email & IP)

You can submit multiple emails or IPs in a single request. Batch jobs are processed asynchronously; the response returns a job identifier (`job_id`) you can poll for status.

#### 1. Batch Email Analysis (JSON)

```python
from opportify_sdk import EmailInsights

email_insights = EmailInsights("<YOUR-KEY-HERE>")

params = {
    'emails': [
        'one@example.com',
        'two@example.org'
    ],
    'name': 'Customer Email Validation',  # Optional: descriptive name for the job
    'enableAi': True,
    'enableAutoCorrection': True
}

# Default content type is application/json
batch = email_insights.batch_analyze(params)

# Optional: poll status later
status = email_insights.get_batch_status(batch['job_id'])
```

#### 2. Batch Email Analysis (Plain Text)
Provide one email per line and set the content type to `text/plain`.

```python
content = "one@example.com\nTwo.User@example.org"  # newline-delimited emails
batch = email_insights.batch_analyze({'text': content}, 'text/plain')
status = email_insights.get_batch_status(batch['job_id'])
```

#### 3. Batch Email Analysis (File Upload)
Supply a `.csv` (one email per row; header optional) via `batch_analyze_file()`. A `.csv` triggers `multipart/form-data`; other extensions fall back to `text/plain` (newline-delimited body).

```python
batch = email_insights.batch_analyze_file('emails.csv', {
    'name': 'Monthly Email Cleanup',  # Optional: descriptive name for the job
    'enableAi': True,
    'enableAutoCorrection': True
})
status = email_insights.get_batch_status(batch['job_id'])
```

#### 4. Batch IP Analysis (JSON)

```python
from opportify_sdk import IpInsights

ip_insights = IpInsights("<YOUR-KEY-HERE>")

params = {
    'ips': [
        '1.1.1.1',
        '8.8.8.8'
    ],
    'name': 'Network Security Scan',  # Optional: descriptive name for the job
    'enableAi': True
}

batch = ip_insights.batch_analyze(params)  # application/json
status = ip_insights.get_batch_status(batch['job_id'])
```

#### 5. Batch IP Analysis (Plain Text)

```python
content = "1.1.1.1\n8.8.8.8"  # newline-delimited IPs
batch = ip_insights.batch_analyze({'text': content}, 'text/plain')
status = ip_insights.get_batch_status(batch['job_id'])
```

#### 6. Batch IP Analysis (File Upload)

```python
batch = ip_insights.batch_analyze_file('ips.csv', {
    'name': 'Firewall IP Assessment',  # Optional: descriptive name for the job
    'enableAi': True
})
status = ip_insights.get_batch_status(batch['job_id'])
```

#### Convenience & Notes
- `batch_analyze_file()` auto-selects content type: `.csv` -> `multipart/form-data`; otherwise `text/plain`.
- For `text/plain`, pass newline-delimited values via the `text` key.
- For `multipart/form-data`, pass a readable file path via the `file` key (handled internally by `batch_analyze_file()`).
- The `name` parameter is optional for all batch operations and helps with job identification and tracking.
- `enableAutoCorrection` applies only to Email Insights.
- Always wrap calls in a try-except (see Error Handling) to capture API errors.
- Polling cadence depends on payload size; a short delay (1–3s) between status checks is recommended.

## Batch Export Jobs

Use batch exports to materialize filtered results from completed jobs. Exports run asynchronously and expose polling helpers similar to batch status checks.

### Email Batch Exports

```python
email_insights = EmailInsights('<YOUR-KEY-HERE>')

# Trigger a new export for a completed batch job
export = email_insights.create_batch_export('job-uuid-here', {
    'exportType': 'csv',
    'columns': [
        'emailAddress',
        'emailProvider',
        'riskReport.score',
        'isDeliverable'
    ],
    'filters': {
        'isDeliverable': 'true',
        'riskReport.score': {'min': 400}
    }
})

# Poll until the export is ready
status = email_insights.get_batch_export_status('job-uuid-here', export['export_id'])

if status['status'] == 'COMPLETED':
    # Use status['download_url'] for the pre-signed file link
    print(f"Download: {status['download_url']}")
```

### IP Batch Exports

```python
ip_insights = IpInsights('<YOUR-KEY-HERE>')

export = ip_insights.create_batch_export('job-uuid-here', {
    'exportType': 'json',
    'columns': [
        'result.ipAddress',
        'result.connectionType',
        'result.riskReport.score'
    ],
    'filters': {
        'result.riskReport.level': ['low', 'medium']
    }
})

status = ip_insights.get_batch_export_status('job-uuid-here', export['export_id'])

if status['status'] == 'COMPLETED':
    # Use status['download_url'] to retrieve the generated export
    print(f"Download: {status['download_url']}")
elif status['status'] == 'FAILED':
    # Review status['error_code'] and status['error_message'] for remediation guidance
    print(f"Error: {status['error_code']} - {status['error_message']}")
```


## Enabling Debug Mode

```python
client_insights.set_debug_mode(True)
```

## Handling Errors

We strongly recommend that any usage of this SDK happens within a try-except to properly handle any exceptions or errors.

```python
from openapi_client.exceptions import ApiException

try:
    # Email or IP Insights usage...
    result = email_insights.analyze(params)
except ApiException as e:
    print(f"API Error: {e.status} - {e.reason}")
    print(f"Response: {e.body}")
except Exception as e:
    print(f"Error: {str(e)}")
```

Below are common error responses you might encounter:

| Status Code | Error Type | Description |
|------------|------------|-------------|
| `400` | Bad Request | Invalid parameters or malformed request |
| `401` | Unauthorized | Invalid or missing API key |
| `402` | Payment Required | Account has insufficient credits |
| `403` | Forbidden | Plan limitation or feature not available |
| `404` | Not Found | Resource not found (e.g., invalid job ID) |
| `413` | Payload Too Large | Request exceeds maximum size (3MB) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server-side error occurred |

## About this package

This Python package is a customization of the base generated by:

- [OpenAPI Generator](https://openapi-generator.tech) project.

