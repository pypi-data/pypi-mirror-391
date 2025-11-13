# daffalib/cli.py
import json
import sys
from pprint import pprint

from .api import API

BANNER = """
Welcome to the daffalib Interactive Console!
============================================
Enter commands like:
  - get <endpoint>
  - post <endpoint> '{"key": "value"}'
  - put <endpoint> '{"key": "value"}'
  - delete <endpoint>
  - help
  - exit

First, please provide the base URL for the API.
(e.g., https://jsonplaceholder.typicode.com)
"""

HELP_TEXT = """
Available commands:
  get <endpoint>
    - Sends a GET request. Example: get /posts/1

  post <endpoint> '<json_data>'
    - Sends a POST request. JSON data must be in single quotes.
    - Example: post /posts '{"title": "foo", "body": "bar"}'

  put <endpoint> '<json_data>'
    - Sends a PUT request. JSON data must be in single quotes.
    - Example: put /posts/1 '{"title": "updated"}'

  delete <endpoint>
    - Sends a DELETE request. Example: delete /posts/1

  help
    - Shows this help message.

  exit
    - Exits the console.
"""

def main() -> None:
    """
    Initializes and runs the custom interactive REPL for daffalib.
    """
    print(BANNER)
    try:
        base_url = input("Enter Base URL: ")
        if not base_url:
            print("Base URL cannot be empty. Exiting.")
            sys.exit(1)
        req = API(base_url)
        print(f"API client initialized for {base_url}\n")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return

    while True:
        try:
            raw_input = input("daffalib> ").strip()
            if not raw_input:
                continue

            parts = raw_input.split(maxsplit=2)
            command = parts[0].lower()

            if command == "exit":
                break
            elif command == "help":
                print(HELP_TEXT)
                continue

            if command not in ["get", "post", "put", "delete"]:
                print(f"Error: Unknown command '{command}'. Type 'help' for available commands.")
                continue

            endpoint = parts[1] if len(parts) > 1 else ""
            result = None

            if command == "get":
                result = req.get(endpoint)
            elif command == "delete":
                result = req.delete(endpoint)
            elif command in ["post", "put"]:
                if len(parts) < 3:
                    print(f"Error: '{command}' command requires a JSON data argument.")
                    continue
                try:
                    data = json.loads(parts[2])
                except json.JSONDecodeError:
                    print("Error: Invalid JSON data provided.")
                    continue
                
                if command == "post":
                    result = req.post(data, endpoint=endpoint)
                else: # put
                    result = req.put(endpoint, data=data)
            
            if isinstance(result, (dict, list)):
                pprint(result)
            else:
                print(result)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"An error occurred: {e}")

    print("\nExiting.")

if __name__ == "__main__":
    main()