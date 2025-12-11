#!/usr/bin/env python3
import sys

# Assumes these exist in the same directory
from tokenizer import tokenize
from parser import parse
from evaluator import evaluate

class WatchedEnvironment(dict):
    """
    A dictionary subclass that intercepts variable assignments.
    If the key matches 'watch_target', it prints the change.
    """
    def __init__(self, watch_target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watch_target = watch_target

    def __setitem__(self, key, value):
        # 1. Check if this is the variable we are watching
        if self.watch_target and key == self.watch_target:
            print(f"\n[WATCH] Identifier '{key}' modified.")
            print(f"        New Value: {value}")
            # Note: Exact line numbers require AST metadata not present in the 
            # provided evaluator, so we report the runtime context.
            print(f"        Context: Runtime Assignment\n")
            
        # 2. Perform the actual dictionary assignment
        super().__setitem__(key, value)

def main():
    # 1. Parse Arguments
    watch_target = None
    script_file = None

    # We skip the first arg (runner.py itself)
    for arg in sys.argv[1:]:
        if arg.startswith("watch="):
            # Split on the first '=' to handle the argument
            parts = arg.split("=", 1)
            if len(parts) == 2:
                watch_target = parts[1]
        elif not script_file and not arg.startswith("-"):
            # Assume the first non-flag argument is the filename
            script_file = arg

    # 2. Initialize the Environment
    # If a watch target exists, use our Proxy class. Otherwise, standard dict.
    if watch_target:
        print(f"--> Debug mode enabled. Watching: {watch_target}")
        environment = WatchedEnvironment(watch_target)
    else:
        environment = {}

    # 3. Execution Logic
    if script_file:
        # File Mode
        try:
            with open(script_file, 'r') as f:
                source_code = f.read()
            
            tokens = tokenize(source_code)
            ast = parse(tokens)
            final_value, exit_status = evaluate(ast, environment)
            
            if exit_status == "exit":
                sys.exit(final_value if isinstance(final_value, int) else 0)
                
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # REPL Mode
        print(f"Interactive Mode. {'Watching: ' + watch_target if watch_target else ''}")
        while True:
            try:
                source_code = input('>> ')

                if source_code.strip() in ['exit', 'quit']:
                    break

                tokens = tokenize(source_code)
                ast = parse(tokens)
                final_value, exit_status = evaluate(ast, environment)
                
                if exit_status == "exit":
                    print(f"Exiting with code: {final_value}")
                    sys.exit(final_value if isinstance(final_value, int) else 0)
                elif final_value is not None:
                    print(final_value)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
