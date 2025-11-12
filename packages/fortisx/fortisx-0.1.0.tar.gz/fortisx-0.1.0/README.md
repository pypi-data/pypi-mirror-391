# FortisX Python SDK

This guide explains how to interact with the API using the Python client.

---

## Installation

```bash
pip install fortisx
```

---

## Initialization

```python
from fortisx import API

api = API("YOUR_API_KEY")
```

**Constructor options**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `api_key` | `str` | – | API key used for authorization |
| `base_url` | `str` | `https://api.fortisx.fi/v1` | Override if using a custom environment |
| `timeout` | `int` | `10` | Request timeout in seconds |

---

## Methods

| Method | Arguments | Returns | Description |
|--------|-----------|---------|-------------|
| `get(endpoint: str, params: dict | None = None)` | endpoint path, optional query params | `dict` | Performs a GET request |
| `post(endpoint: str, data: dict | None = None)` | endpoint path, optional JSON body | `dict` | Performs a POST request |
| `put(endpoint: str, data: dict | None = None)` | endpoint path, optional JSON body | `dict` | Performs a PUT request |
| `delete(endpoint: str)` | endpoint path | `dict` | Performs a DELETE request |

**Headers added automatically**

```json
{ "Authorization": "Bearer {api_key}", "Accept": "application/json" }
```

---

## Error handling

All methods may raise `APIError(message: str, status: int | None, details: dict | None)`.

```python
from fortisx import API, APIError

api = API("YOUR_API_KEY")
try:
    data = api.get("ping")
    print(data)
except APIError as e:
    print(e.status, e, e.details)
```

---

## Example: `/ping` Endpoint

```python
from fortisx import API

api = API("demo-key")

res = api.get("ping")
print(res)  # {'status': 'ok'}
```
