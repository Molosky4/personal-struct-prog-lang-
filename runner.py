#!/usr/bin/env python
import sys
import os
from tokenizer import tokenize
from parser import parse
from evaluator import evaluate

class WatchContext:
    """Context manager for tracking variable watches"""
    def __init__(self, watch_var=None):
        self.watch_var = watch_var
        self.watch_enabled = watch_var is not None
        self.stack_trace = []
    
    def record_change(self, var_name, new_value):
        """Record when a watched variable changes"""
        if self.watch_enabled and var_name == self.watch_var:
            location = self._get_location()
            print(f"\n[WATCH: {self.watch_var}] New value: {self._format_value(new_value)}")
            print(f"         Location: {location}")
            if self.stack_trace:
                print(f"         Call stack depth: {len(self.stack_trace)}")
    
    def _get_location(self):
        """Get human-readable location"""
        # In a real implementation, we'd track line/column from AST
        # For now, return call stack depth info
        if self.stack_trace:
            return f"in function '{self.stack_trace[-1]}'"
        return "at module level"
    
    def _format_value(self, val):
        """Format value for display"""
        if isinstance(val, str):
            return f'"{val}"'
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, list):
            return f"[{', '.join(self._format_value(v) for v in val)}]"
        elif isinstance(val, dict):
            items = ', '.join(f'"{k}": {self._format_value(v)}' for k, v in val.items())
            return f"{{{items}}}"
        elif val is None:
            return "null"
        else:
            return str(val)

# Global watch context
watch_context = None

def parse_command_line_args():
    """
    Parse command line arguments
    
    Supported formats:
    - python runner.py script.t              # Run script
    - python runner.py                       # REPL mode
    - python runner.py script.t watch=x      # Run with watch on variable 'x'
    
    Returns: (filename, watch_var)
    """
    filename = None
    watch_var = None
    
    for arg in sys.argv[1:]:
        if arg.startswith("watch="):
            watch_var = arg.split("=", 1)[1]
            if not watch_var:
                print("Error: watch argument requires a variable name (watch=variable_name)")
                sys.exit(1)
        elif not arg.startswith("-"):
            filename = arg
    
    return filename, watch_var


def wrap_evaluate_for_watch(original_evaluate, watch_ctx):
    """
    Wrapper around evaluate() to track variable assignments
    """
    def wrapped_evaluate(ast, environment):
        # Track assignment operations
        if ast["tag"] == "assign" and watch_ctx.watch_enabled:
            target = ast["target"]
            if isinstance(target, dict) and target.get("tag") == "identifier":
                var_name = target.get("value")
                # Evaluate the assignment
                result, status = original_evaluate(ast, environment)
                # Record the change
                if var_name in environment:
                    watch_ctx.record_change(var_name, environment[var_name])
                return result, status
        
        # Regular evaluation for non-assignment or non-watched variables
        return original_evaluate(ast, environment)
    
    return wrapped_evaluate


def main():
    global watch_context
    
    filename, watch_var = parse_command_line_args()
    
    # Initialize watch context
    watch_context = WatchContext(watch_var)
    
    if watch_var:
        print(f"[DEBUG] Watching variable: '{watch_var}'")
        print()
    
    environment = {}
    
    if filename:
        # File execution mode
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        
        try:
            with open(filename, 'r') as f:
                source_code = f.read()
            
            tokens = tokenize(source_code)
            ast = parse(tokens)
            final_value, exit_status = evaluate(ast, environment)
            
            if exit_status == "exit":
                exit_code = final_value if isinstance(final_value, int) else 0
                sys.exit(exit_code)
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # REPL mode
        print("Language Interpreter REPL")
        if watch_var:
            print(f"Watching: {watch_var}")
        print("Type 'exit' or 'quit' to exit\n")
        
        while True:
            try:
                # Read input
                source_code = input('>> ')
                
                # Exit conditions
                if source_code.strip() in ['exit', 'quit']:
                    break
                
                if not source_code.strip():
                    continue
                
                # Tokenize, parse, and execute
                tokens = tokenize(source_code)
                ast = parse(tokens)
                final_value, exit_status = evaluate(ast, environment)
                
                if exit_status == "exit":
                    exit_code = final_value if isinstance(final_value, int) else 0
                    sys.exit(exit_code)
                
                elif final_value is not None:
                    # Print result in REPL if not None
                    if isinstance(final_value, bool):
                        print(f"true" if final_value else "false")
                    elif final_value is None:
                        print("null")
                    else:
                        print(final_value)
            
            except KeyboardInterrupt:
                print("\n")
                continue
            
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
