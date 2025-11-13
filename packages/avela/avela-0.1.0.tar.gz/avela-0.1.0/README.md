# Avela Python SDK

Official Python SDK for the [Avela Education Platform API](https://avela.org/api).

[![PyPI version](https://badge.fury.io/py/avela.svg)](https://badge.fury.io/py/avela)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ **Dynamic endpoint access** - No need to update SDK when new endpoints are added
- ✅ **OAuth2 authentication** - Automatic token management and refresh
- ✅ **Type hints** - Full type annotations for better IDE support
- ✅ **Modern Python** - Built for Python 3.10+
- ✅ **Session management** - Connection pooling for better performance
- ✅ **Error handling** - Comprehensive exception hierarchy
- ✅ **Environment support** - Works with dev, qa, uat, and production

## Installation

```bash
pip install avela
```

## Quick Start

```python
from avela import AvelaAPI

# Initialize the client
api = AvelaAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    environment="uat"  # or "dev", "qa", "prod"
)

# List applicants
applicants = api.applicants.list(limit=100, offset=0)

# Get a specific form
form = api.forms.get("form-id-123")

# Update form questions
api.forms.call("POST", "form-id/questions", json={
    "questions": [
        {
            "key": "student_name",
            "type": "FreeText",
            "answer": {"free_text": {"value": "John Doe"}}
        }
    ]
})
```

## Authentication

### Getting API Credentials

Contact Avela Support for API credentials at info@avela.org.

### Environment Options

- `dev` - Development environment
- `qa` - QA/Testing environment
- `uat` - User Acceptance Testing environment
- `prod` - Production environment

## Resource-Specific Request Formats

**Important**: Different API resources require data to be wrapped in resource-specific keys. This is an API requirement, not an SDK limitation.

### Common Wrapper Patterns

```python
# Applicants - require "applicant" wrapper for create/update/patch
api.applicants.create({
    "applicant": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    }
})

api.applicants.update("applicant-id", {
    "applicant": {
        "middle_name": "test"
    }
})

# Forms questions - require "questions" array wrapper
api.forms.call("POST", "form-id/questions", json={
    "questions": [
        {
            "key": "internal1",
            "type": "FreeText",
            "answer": {"free_text": {"value": "Updated value"}}
        }
    ]
})
```

**Note**: Consult the [Avela API Documentation](https://avela.org/api) for specific wrapper requirements for each resource type.

## Usage Examples

### Listing Resources

```python
# List all applicants with pagination
applicants = api.applicants.list(limit=100, offset=0)

# List with filters
applicants = api.applicants.list(
    limit=50,
    reference_id=["450156", "450157"]
)
```

### Getting a Single Resource

```python
# Get a specific form by ID
form = api.forms.get("e4c2f10d-b94a-49eb-b6b2-a129b0840f90")

# Get an applicant
applicant = api.applicants.get("b28a524c-1c3d-43be-8620-02319bb8fbaa")
```

### Creating Resources

```python
# Create a new applicant (note: requires "applicant" wrapper)
new_applicant = api.applicants.create({
    "applicant": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "birth_date": "2005-03-15"
    }
})
```

### Updating Resources

```python
# Update an applicant (note: requires "applicant" wrapper)
updated = api.applicants.update("b28a524c-1c3d-43be-8620-02319bb8fbaa", {
    "applicant": {
        "middle_name": "test"
    }
})

# Partial update (PATCH) - also requires wrapper
patched = api.applicants.patch("applicant-id", {
    "applicant": {
        "phone_number": "555-0123"
    }
})
```

### Custom Endpoint Calls

For endpoints that don't fit the standard REST pattern:

```python
# Update form questions (custom endpoint)
api.forms.call("POST", "form-id/questions", json={
    "questions": [
        {
            "key": "internal1",
            "type": "FreeText",
            "answer": {"free_text": {"value": "Updated value"}}
        }
    ]
})

# Any custom endpoint
response = api.custom_resource.call("GET", "special/endpoint", params={"filter": "value"})
```

### Context Manager

Use with a context manager to automatically close sessions:

```python
with AvelaAPI(client_id, client_secret, environment="uat") as api:
    applicants = api.applicants.list()
    # Session automatically closed when exiting the block
```

## Dynamic Endpoint Access

The SDK uses dynamic endpoint proxies, which means you can access **any** API endpoint without the SDK needing an update:

```python
# These all work automatically:
api.applicants.list()
api.forms.get("id")
api.organizations.list()
api.any_new_resource.create({...})  # Works even if endpoint was just added!
```

### Available Methods on All Resources

Every resource proxy provides these methods:

- `list(**params)` - GET /{resource}
- `get(id)` - GET /{resource}/{id}
- `create(data)` - POST /{resource}
- `update(id, data)` - PUT /{resource}/{id}
- `patch(id, data)` - PATCH /{resource}/{id}
- `delete(id)` - DELETE /{resource}/{id}
- `call(method, path, **kwargs)` - Custom requests

## Error Handling

The SDK provides a comprehensive exception hierarchy:

```python
from avela import (
    AvelaAPI,
    AvelaError,          # Base exception
    APIError,            # General API errors
    AuthenticationError, # Auth failures
    ValidationError,     # 400 errors
    NotFoundError,       # 404 errors
    RateLimitError,      # 429 errors
    ServerError,         # 5xx errors
)

try:
    api = AvelaAPI(client_id, client_secret)
    applicants = api.applicants.list()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except NotFoundError as e:
    print(f"Resource not found: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except ServerError as e:
    print(f"Server error [{e.status_code}]: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Advanced Usage

### Custom Timeout

```python
# Set custom timeout (default is 30 seconds)
api = AvelaAPI(
    client_id,
    client_secret,
    environment="uat",
    timeout=60  # 60 seconds
)
```

### Manual Token Refresh

```python
# The SDK automatically refreshes tokens, but you can do it manually:
api.auth.authenticate()

# Check if token is expired
if api.auth.is_token_expired():
    api.auth.authenticate()
```

### Direct HTTP Access

```python
# Access the underlying session for custom requests
response = api.session.get(
    "https://custom.api.endpoint.com/resource",
    headers=api.auth.get_auth_headers()
)
```

## Generating Custom Examples with AI

You can use an LLM to generate custom examples tailored to your specific use case. Here's a prompt template:

```
I'm using the Avela Python SDK to interact with the Avela Education Platform API.

SDK Installation:
pip install avela

Basic SDK Usage:
- Initialize: api = AvelaAPI(client_id="...", client_secret="...", environment="uat")
- Dynamic endpoints: api.{resource}.list(), api.{resource}.get(id), api.{resource}.create(data)
- Custom calls: api.{resource}.call(method, path, **kwargs)

Important API Requirements:
- Applicants require {"applicant": {...}} wrapper for create/update/patch
- Forms questions require {"questions": [...]} wrapper
- Refer to https://avela.org/api for specific wrapper requirements

My use case:
[Describe what you want to accomplish, e.g., "Fetch all applicants born after 2020 and export to Excel"]

Please generate a complete Python script with:
1. Proper error handling
2. Pagination if needed
3. Progress indicators
4. Comments explaining each step
```

## Complete Examples

### Fetching and Processing Applicants

```python
from avela import AvelaAPI
import csv

# Initialize API
api = AvelaAPI(
    client_id="your_client_id",
    client_secret="your_client_secret",
    environment="uat"
)

# Fetch all applicants with pagination
all_applicants = []
offset = 0
limit = 1000

while True:
    batch = api.applicants.list(limit=limit, offset=offset)
    if not batch:
        break

    all_applicants.extend(batch)
    offset += limit

# Export to CSV
with open("applicants.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=all_applicants[0].keys())
    writer.writeheader()
    writer.writerows(all_applicants)

print(f"Exported {len(all_applicants)} applicants")
```

### Bulk Updating Forms

```python
from avela import AvelaAPI
import csv

api = AvelaAPI(client_id, client_secret, environment="uat")

# Read updates from CSV
with open("form_updates.csv") as f:
    reader = csv.DictReader(f)

    for row in reader:
        form_id = row["form_id"]
        question_key = row["question_key"]
        answer_value = row["answer_value"]

        # Update form question
        api.forms.call("POST", f"{form_id}/questions", json={
            "questions": [{
                "key": question_key,
                "type": "FreeText",
                "answer": {"free_text": {"value": answer_value}}
            }]
        })

        print(f"✓ Updated {form_id} - {question_key}")
```

## Contributing

Contributions are welcome! We'd love your help improving the Avela Python SDK.

**For development setup, testing, and publishing instructions, see [CONTRIBUTING.md](CONTRIBUTING.md)**

Quick links:
- [Development Setup](CONTRIBUTING.md#development-setup)
- [Running Tests](CONTRIBUTING.md#running-tests)
- [Code Quality](CONTRIBUTING.md#code-quality)
- [Publishing to PyPI](CONTRIBUTING.md#publishing-to-pypi)

## Support

- **Issues:** [GitHub Issues](https://github.com/avela/avela-python/issues)
- **Email:** info@avela.org

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### 0.1.0 (2025-01-12)

- Initial release
- OAuth2 authentication with automatic token refresh
- Dynamic endpoint access for all API resources
- Comprehensive error handling
- Support for all HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Type hints throughout
- Context manager support
