# interpreter.py

# Import the AST node types from parser.py
# MODIFIED: Note the '.' for relative import inside a package
from .parser import (
    NumNode, StringNode, VarAccessNode, BinOpNode, 
    AssignNode, PrintNode, IfNode, WhileNode
)

class Interpreter:
    # MODIFIED: __init__ no longer takes 'output_list'
    def __init__(self):
        self.symbol_table = {}
        # MODIFIED: self.output is removed

    def _is_truthy(self, val):
        """Helper to determine if a value is 'true'."""
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return len(val) > 0
        return False # Default for other types (like None)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value
    
    def visit_VarAccessNode(self, node):
        name = node.name
        if name in self.symbol_table:
            return self.symbol_table[name]
        else:
            raise Exception(f"Variable '{name}' is not defined.")

    def visit_AssignNode(self, node):
        value = self.visit(node.value)
        self.symbol_table[node.name] = value

    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        
        # --- THIS IS THE KEY CHANGE ---
        # Instead of appending to a list, we just print
        # directly to the console for the CLI.
        
        # Convert Python booleans to simpler strings for output
        if isinstance(value, bool):
            print("True" if value else "False")
        else:
            print(str(value))

    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op_token.type

        # --- Arithmetic Operations ---
        if op in ('PLUS', 'MINUS', 'MUL', 'DIV', 'MODULO'):
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if op == 'PLUS': return left + right
                elif op == 'MINUS': return left - right
                elif op == 'MUL': return left * right
                elif op == 'DIV':
                    if right == 0: raise Exception("Runtime error: Division by zero")
                    return left / right # Use float division
                elif op == 'MODULO':
                    if right == 0: raise Exception("Runtime error: Modulo by zero")
                    return left % right
            
            elif isinstance(left, str) and isinstance(right, str):
                if op == 'PLUS': return left + right
                else: raise Exception(f"Unsupported operation '{op}' for strings")
            
            else:
                raise Exception(f"Type mismatch: Cannot perform '{op}' on {type(left)} and {type(right)}")

        # --- Comparison Operations ---
        elif op in ('GREATER', 'LESS', 'GREATER_EQ', 'LESS_EQ', 'EQUALTO', 'NOT_EQUAL'):
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if op == 'GREATER': return left > right
                elif op == 'LESS': return left < right
                elif op == 'GREATER_EQ': return left >= right
                elif op == 'LESS_EQ': return left <= right
                elif op == 'EQUALTO': return left == right
                elif op == 'NOT_EQUAL': return left != right
            
            elif isinstance(left, str) and isinstance(right, str):
                if op == 'EQUALTO': return left == right
                elif op == 'NOT_EQUAL': return left != right
                else: raise Exception(f"Cannot perform '{op}' on strings, only '==' and '!='")
            
            else:
                # Allow equality check between different types (will always be False)
                if op == 'EALTO': return False
                elif op == 'NOT_EQUAL': return True
                else:
                    raise Exception(f"Type mismatch: Cannot perform '{op}' on {type(left)} and {type(right)}")

        else:
            raise Exception(f"Unknown binary operator: {op}")

    def visit_IfNode(self, node):
        """Visit an IfNode"""
        
        # Iterate through the (condition, statements) pairs for IF and ELIF
        for condition_node, statements in node.cases:
            condition_value = self.visit(condition_node)
            
            if self._is_truthy(condition_value):
                # Execute all statements in this block
                for stmt in statements:
                    self.visit(stmt)
                return # IMPORTANT: Exit after the first true block

        # If no 'if' or 'else if' was true, run the 'else' block if it exists
        if node.else_case:
            for stmt in node.else_case:
                self.visit(stmt)

    def visit_WhileNode(self, node):
        """Visit a WhileNode"""
        
        # Loop while the condition is true
        while self._is_truthy(self.visit(node.condition_node)):
            # Execute all statements in the block
            for stmt in node.statements:
                self.visit(stmt)
