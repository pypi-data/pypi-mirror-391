import sys

# Import your existing language engine components
from .lexer import lex
from .parser import Parser
from .interpreter import Interpreter

def main():
    # Get the file path from the command-line arguments
    # sys.argv[0] is the command itself ('iloko')
    # sys.argv[1] is the file path we want
    if len(sys.argv) < 2:
        print("Error: Please provide a file to run.")
        print("Usage: iloko <filename.iloko>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Read the .iloko file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Run the interpreter
    try:
        tokens = lex(code)
        parser = Parser(tokens)
        ast_statements = parser.parse()
        
        # The interpreter will now print directly to the console
        interpreter = Interpreter() 
        
        for stmt in ast_statements:
            interpreter.visit(stmt)
            
    except Exception as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

