# daffalib/cli.py
import code
import readline
import rlcompleter
from typing import Any, Dict

from .api import API

BANNER = """
Welcome to the daffalib Interactive Console!
============================================
A `req` object of type `daffalib.API` is available.

Example commands:
  - req.get('posts/1')
  - req.post({'title': 'foo', 'body': 'bar', 'userId': 1}, endpoint='posts')
  - req.put('posts/1', {'id': 1, 'title': 'foo', 'body': 'bar', 'userId': 1})
  - req.delete('posts/1')
  - exit() or Ctrl-D to quit.

First, please provide the base URL for the API.
(e.g., https://jsonplaceholder.typicode.com)
"""

def main() -> None:
    """
    Initializes and runs the interactive REPL for daffalib.
    """
    print(BANNER)
    try:
        base_url = input("Enter Base URL: ")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return

    req = API(base_url)

    # Setup autocompletion and history
    namespace: Dict[str, Any] = globals().copy()
    namespace.update(locals())
    readline.set_completer(rlcompleter.Completer(namespace).complete)
    readline.parse_and_bind("tab: complete")

    # Start the interactive console
    try:
        code.interact(local=namespace)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")

if __name__ == "__main__":
    main()
