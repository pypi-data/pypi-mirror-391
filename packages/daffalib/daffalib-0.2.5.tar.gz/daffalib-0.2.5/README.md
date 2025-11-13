# daffalib

[![PyPI version](https://badge.fury.io/py/daffalib.svg)](https://badge.fury.io/py/daffalib)

A modern and ultra-simple Python wrapper for the `requests` library, designed to simplify REST API interactions with flexible configuration and built-in REPL support.

## Features

-   **Simple Interface**: Clean and intuitive methods for `GET`, `POST`, `PUT`, and `DELETE`.
-   **Automatic JSON Parsing**: Responses are automatically converted to Python dictionaries.
-   **Graceful Fallback**: If a response is not valid JSON, the raw text content is returned.
-   **Automatic Error Handling**: Raises `requests.HTTPError` for unsuccessful responses (4xx or 5xx status codes).
-   **Flexible Configuration**: Easily configure base URLs, default headers, and authentication for your API session.
-   **Interactive REPL**: A command-line tool for interacting with APIs directly from your terminal.

## Installation

Install `daffalib` using pip:

```bash
pip install daffalib
```

## Basic Usage

Instantiate the `API` class with a base URL and start making requests. The methods return a dictionary or a string directly.

```python
from daffalib import API
from requests.exceptions import HTTPError

# Use a public test API
api = API("https://jsonplaceholder.typicode.com")

try:
    # GET request
    posts = api.get("posts")
    print(f"Found {len(posts)} posts.")

    # GET a single item
    post = api.get("posts/1")
    print(f"Title of post #1: {post['title']}")

    # POST request
    new_post_data = {
        "title": "My New Post",
        "body": "This is the content.",
        "userId": 1
    }
    created_post = api.post(new_post_data, endpoint="posts")
    print(f"Created new post with ID: {created_post['id']}")

    # PUT request
    updated_data = {"title": "Updated Title"}
    updated_post = api.put("posts/1", data=updated_data)
    print(f"Updated post #1's title to: {updated_post['title']}")

    # DELETE request
    response = api.delete("posts/1")
    print("Delete response:", response) # Often empty on success

except HTTPError as e:
    print(f"An HTTP error occurred: {e.response.status_code} {e.response.reason}")
except Exception as e:
    print(f"An error occurred: {e}")

```

### Custom Headers and Authentication

You can configure default headers and authentication when initializing the `API` object.

```python
from daffalib import API
from requests.auth import HTTPBasicAuth

# Custom headers
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "X-Custom-Header": "MyValue"
}

# Basic Authentication
auth = HTTPBasicAuth('your_username', 'your_password')

# Initialize with headers and auth
secure_api = API(
    base_url="https://api.yourapi.com/v1/",
    headers=headers,
    auth=auth
)

# All requests made with `secure_api` will now include the configured headers and auth
data = secure_api.get("user/profile")
print(data)
```

### Interactive REPL Mode

`daffalib` includes a command-line tool for quick API exploration. Just run `daffalib-cli` in your terminal.

1.  **Start the tool:**
    ```bash
    daffalib-cli
    ```

2.  **Enter the base URL when prompted:**
    ```
    Welcome to the daffalib Interactive Console!
    ...
    Enter Base URL: https://jsonplaceholder.typicode.com
    API client initialized for https://jsonplaceholder.typicode.com

    daffalib>
    ```

3.  **Use direct commands to interact with the API:**
    ```bash
    daffalib> get /users/1
    {'address': {'city': 'Gwenborough',
                 'geo': {'lat': '-37.3159', 'lng': '81.1496'},
                 'street': 'Kulas Light',
                 'suite': 'Apt. 556',
                 'zipcode': '92998-3874'},
     'company': {'bs': 'harness real-time e-markets',
                 'catchPhrase': 'Multi-layered client-server neural-net',
                 'name': 'Romaguera-Crona'},
     'email': 'Sincere@april.biz',
     'id': 1,
     'name': 'Leanne Graham',
     'phone': '1-770-736-8031 x56442',
     'username': 'Bret',
     'website': 'hildegard.org'}

    daffalib> post /todos '{"userId": 1, "title": "Learn daffalib", "completed": true}'
    {'userId': 1, 'title': 'Learn daffalib', 'completed': True, 'id': 201}

    daffalib> exit
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
