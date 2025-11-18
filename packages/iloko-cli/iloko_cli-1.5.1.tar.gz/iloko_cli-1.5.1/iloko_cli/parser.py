# parser.py

# --- 4. AST NODES ---
# These classes define the structure of our "tree"

class NumNode:
    """Represents a number."""
    def __init__(self, token): 
        self.value = token.value
    def __repr__(self): 
        return f"Num({self.value})"

class StringNode:
    """Represents a string."""
    def __init__(self, token): 
        self.value = token.value
    def __repr__(self): 
        return f"Str({self.value})"

class VarAccessNode:
    """Represents a variable access (e.g., 'PRINT a')"""
    def __init__(self, token): 
        self.name = token.value
    def __repr__(self): 
        return f"Var({self.name})"

class BinOpNode:
    """Represents a binary operation (e.g., 10 + 5)"""
    def __init__(self, left, op_token, right):
        self.left = left
        self.op_token = op_token
        self.right = right
    def __repr__(self): 
        return f"BinOp({self.left}, {self.op_token.type}, {self.right})"

class AssignNode:
    """Represents assignment (e.g., 'LET a = 10')"""
    def __init__(self, name_token, value_node):
        self.name = name_token.value
        self.value = value_node
    def __repr__(self): 
        return f"Assign({self.name}, {self.value})"

class PrintNode:
    """Represents a print statement"""
    def __init__(self, value_node):
        self.value = value_node
    def __repr__(self): 
        return f"Print({self.value})"

class IfNode:
    """Represents an if-elif-else block."""
    def __init__(self, cases, else_case):
        # cases is a list of tuples: (condition_node, statements_list)
        self.cases = cases
        # else_case is a list of statements, or None
        self.else_case = else_case
    
    def __repr__(self):
        return f"If(Cases: {self.cases}, Else: {self.else_case})"

class WhileNode:
    """Represents a 'BAYAT' (while) loop."""
    def __init__(self, condition_node, statements):
        self.condition_node = condition_node
        self.statements = statements
    
    def __repr__(self):
        return f"While(Condition: {self.condition_node}, Body: {self.statements})"


# --- 5. PARSER ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = -1
        self.current_token = None
        self.advance()

    def advance(self):
        self.idx += 1
        self.current_token = self.tokens[self.idx] if self.idx < len(self.tokens) else None

    def skip_newlines(self):
        """Skip over one or more NEWLINE tokens."""
        while self.current_token and self.current_token.type == 'NEWLINE':
            self.advance()

    def parse(self):
        statements = []
        self.skip_newlines() # Skip any leading newlines
        
        while self.current_token:
            statements.append(self.parse_statement())
            
            # After a statement, we expect a newline or end of file
            if self.current_token:
                if self.current_token.type != 'NEWLINE':
                    # If it's not a newline, it must be a block-ender
                    if self.current_token.type not in ('NALPAS', 'NO_KET_DI', 'NO_KUMA'):
                        raise Exception(f"Expected newline, but got {self.current_token}")
                else:
                    self.skip_newlines() # Skip trailing newlines

        return statements

    def parse_statement(self):
        """Parse a single statement."""
        if self.current_token.type == 'LET':
            return self.parse_let_statement()
        elif self.current_token.type == 'PRINT':
            return self.parse_print_statement()
        elif self.current_token.type == 'NO': # Check for 'IF'
            return self.parse_if_statement()
        elif self.current_token.type == 'BAYAT': # Check for 'WHILE'
            return self.parse_while_statement()
        else:
            raise Exception(f"Unexpected token: {self.current_token}")

    def parse_let_statement(self):
        """Parse 'LET ID = expression'"""
        self.advance() # Skip LET
        if self.current_token.type != 'ID':
            raise Exception("Expected identifier after 'IKABIL'")
        name_token = self.current_token
        self.advance()
        if self.current_token.type != 'EQUALS':
            raise Exception("Expected '=' in assignment")
        self.advance()
        value_node = self.parse_comparison()
        return AssignNode(name_token, value_node)


    def parse_print_statement(self):
        """Parse 'PRINT expression'"""
        self.advance() # Skip PRINT
        value_node = self.parse_comparison()
        return PrintNode(value_node)

    def parse_if_statement(self):
        """
        Parses an if-elif-else block.
        NO condition NEWLINE
            statements
        (NO KET DI condition NEWLINE
            statements)*
        (NO KUMA NEWLINE
            statements)?
        NALPAS
        """
        cases = []
        else_case = None

        # --- Parse IF ---
        self.advance() # Skip 'NO'
        condition = self.parse_comparison()
        
        if not self.current_token or self.current_token.type != 'NEWLINE':
            raise Exception("Expected newline after 'NO' condition")
        self.skip_newlines()

        statements = self.parse_statements_until(['NO_KET_DI', 'NO_KUMA', 'NALPAS'])
        cases.append((condition, statements))

        # --- Parse ELIF(s) ---
        while self.current_token and self.current_token.type == 'NO_KET_DI':
            self.advance() # Skip 'NO_KET_DI'
            condition = self.parse_comparison()
            
            if not self.current_token or self.current_token.type != 'NEWLINE':
                raise Exception("Expected newline after 'NO KET DI' condition")
            self.skip_newlines()
            
            statements = self.parse_statements_until(['NO_KET_DI', 'NO_KUMA', 'NALPAS'])
            cases.append((condition, statements))

        # --- Parse ELSE ---
        if self.current_token and self.current_token.type == 'NO_KUMA':
            self.advance() # Skip 'NO_KUMA'
            
            if not self.current_token or self.current_token.type != 'NEWLINE':
                raise Exception("Expected newline after 'NO KUMA'")
            self.skip_newlines()
            
            else_case = self.parse_statements_until(['NALPAS'])

        # --- Expect END ---
        if not self.current_token or self.current_token.type != 'NALPAS':
            raise Exception(f"Expected 'NALPAS' to end 'NO' block, but got {self.current_token}")
        self.advance() # Skip 'NALPAS'

        return IfNode(cases, else_case)

    def parse_while_statement(self):
        """
        Parses a while loop.
        BAYAT condition NEWLINE
            statements
        NALPAS
        """
        self.advance() # Skip 'BAYAT'
        condition = self.parse_comparison()

        if not self.current_token or self.current_token.type != 'NEWLINE':
            raise Exception("Expected newline after 'BAYAT' condition")
        self.skip_newlines()

        # 'NALPAS' is the only stop token for a while loop
        statements = self.parse_statements_until(['NALPAS'])

        if not self.current_token or self.current_token.type != 'NALPAS':
            raise Exception(f"Expected 'NALPAS' to end 'BAYAT' block, but got {self.current_token}")
        self.advance() # Skip 'NALPAS'

        return WhileNode(condition, statements)

    def parse_statements_until(self, stop_tokens):
        """Parses statements until one of the stop_tokens is encountered."""
        statements = []
        
        # Check for empty block
        if not self.current_token or self.current_token.type in stop_tokens:
            return statements
            
        while self.current_token and self.current_token.type not in stop_tokens:
            statements.append(self.parse_statement())
            
            if self.current_token and self.current_token.type not in stop_tokens:
                if self.current_token.type != 'NEWLINE':
                    raise Exception(f"Expected newline after statement in block, got {self.current_token}")
                self.skip_newlines()
                
                if not self.current_token:
                    raise Exception(f"Unexpected end of file, expected one of {stop_tokens}")

        return statements

    # --- NEW Expression Parsing Hierarchy ---
    # This respects operator precedence:
    # 1. ( )
    # 2. * / %
    # 3. + -
    # 4. > < == != >= <=
    
    def parse_comparison(self):
        """Parse comparison operations (==, !=, <, <=, >, >=)."""
        left = self.parse_expression()
        
        while self.current_token and self.current_token.type in ('EQUALTO', 'NOT_EQUAL', 'LESS', 'LESS_EQ', 'GREATER', 'GREATER_EQ'):
            op_token = self.current_token
            self.advance()
            right = self.parse_expression()
            left = BinOpNode(left, op_token, right)
            
        return left

    def parse_expression(self):
        """Parse addition and subtraction (+, -)."""
        left = self.parse_term()

        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op_token = self.current_token
            self.advance()
            right = self.parse_term()
            left = BinOpNode(left, op_token, right)
            
        return left
        
    def parse_term(self):
        """Parse multiplication, division, and modulo (*, /, %)."""
        left = self.parse_atom()

        while self.current_token and self.current_token.type in ('MUL', 'DIV', 'MODULO'):
            op_token = self.current_token
            self.advance()
            right = self.parse_atom()
            left = BinOpNode(left, op_token, right)
            
        return left

    def parse_atom(self):
        """Parse a single 'atom' like a NUMBER, STRING, ID, or (expression)."""
        token = self.current_token
        
        if token is None:
            raise Exception("Unexpected end of input")

        if token.type == 'NUMBER':
            self.advance()
            return NumNode(token)
        elif token.type == 'STRING':
            self.advance()
            return StringNode(token)
        elif token.type == 'ID':
            self.advance()
            return VarAccessNode(token)
        elif token.type == 'LPAREN':
            self.advance() # Skip (
            node = self.parse_comparison() # Start parsing from the top
            if not self.current_token or self.current_token.type != 'RPAREN':
                raise Exception(f"Expected ')', but got {self.current_token}")
            self.advance() # Skip )
            return node
        else:
            raise Exception(f"Unexpected token: {self.current_token}")
