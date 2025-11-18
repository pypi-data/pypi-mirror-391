# lexer.py
import re

# Define all possible token types
TOKEN_TYPES = [
    # Keywords (must come before ID)
    ('PRINT',     r'IPAKITA'),
    ('LET',       r'IKABIL'),
    
    # MODIFIED: Changed names to be valid regex group names (no spaces)
    ('NO_KET_DI', r'NO KET DI'),       # 'ELSE IF' - MUST come before 'NO'
    ('NO_KUMA',   r'NO KUMA'),         # 'ELSE'
    
    ('NO',        r'NO'),              # 'IF'
    ('BAYAT',     r'BAYAT'),            # 'WHILE'
    ('NALPAS',     r'NALPAS'),            # 'END' (for IF and WHILE)

    # Identifiers
    ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identifiers (variables)

    # Literals
    ('NUMBER',    r'\d+(\.\d+)?'),     # Support integers (10) and floats (10.5)
    ('STRING',    r'\"[^\"]*\"|\'[^\']*\'' ), # Support "..." or '...'

    # Comparison Operators
    ('EQUALTO',   r'=='),             # Equals (comparison)
    ('NOT_EQUAL', r'!='),             # Not equals
    ('GREATER_EQ',r'>='),             # Greater than or equals
    ('LESS_EQ',   r'<='),             # Less than or equals
    ('GREATER',   r'>'),              # Greater than
    ('LESS',      r'<'),              # Less than

    # Arithmetic & Assignment
    ('PLUS',      r'\+'),              # Plus sign
    ('MINUS',     r'-'),              # Minus sign
    ('MUL',       r'\*'),              # Multiply sign
    ('DIV',       r'/'),              # Divide sign
    ('MODULO',    r'\%'),              # Modulo sign
    ('EQUALS',    r'='),              # Equals sign (for assignment)
    
    # Delimiters
    ('LPAREN',    r'\('),              # Left parenthesis
    ('RPAREN',    r'\)'),              # Right parenthesis
    ('NEWLINE',   r'\n'),              # Newline
    ('SKIP',      r'[ \t]+'),          # Skip whitespace
    ('COMMENT',   r'#[^\n]*'),         # Skip comments
]

# A simple Token object
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        """String representation for debugging."""
        return f"Token({self.type}, {repr(self.value)})"

def lex(code):
    """
    The lexer function.
    Takes source code as a string and returns a list of Tokens.
    """
    tokens = []
    # Combine all regex patterns
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_TYPES)
    
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()

        if kind == 'NUMBER':
            # Convert to float or int based on value
            value = float(value) if '.' in value else int(value)
        elif kind == 'STRING':
            value = value[1:-1] # Remove the surrounding quotes
        elif kind in ('SKIP', 'COMMENT'): # Skip whitespace and comments
            continue 
        elif kind == 'NEWLINE':
            pass # We'll keep newlines for parsing blocks

        tokens.append(Token(kind, value))
        
    return tokens
