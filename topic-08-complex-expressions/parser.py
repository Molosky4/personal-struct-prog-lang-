#!/usr/bin/env python
from tokenizer import tokenize

"""
current_parser.py

Parser for simple expressions and statements.
"""

# Grammar 
#    simple_expression = <identifier> | <boolean> | <number> | <string> | <null> | list | #   object | "-" simple_expression | "!" simple_expression | function | ( "(" expression ")" )

grammar = """
    simple_expression = <identifier> | <boolean> | <number> | <string> | list | "-" simple_expression | "!" simple_expression | ( "(" expression ")" )
    list = "[" expression { "," expression } "]"
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    complex_expression = simple_expression
    arithmetic_factor = complex_expression
    arithmetic_term = arithmetic_factor { "*"|"/" arithmetic_factor }
    arithmetic_expression = arithmetic_term { "+"|"-" arithmetic_term }
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    logical_factor = relational_expression
    logical_term = logical_factor { "&&" logical_factor }
    logical_expression = logical_term { "||" logical_term }
    expression = logical_expression
    statement_block = "{" statement { ";" statement } "}"
    assignment_statement = expression [ "=" expression ]
    print_statement = "print" [ expression ]
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    break_statement = "break"
    continue_statement = "continue"
    while_statement = "while" "(" expression ")" statement_block
    statement = statement_block | if_statement | while_statement | print_statement | assignment_statement | break_statement | continue_statement
    program = [ statement { ";" statement } ]
"""

# --- Parsing Functions and Their Tests ---

def parse_list(tokens):
    """
    list = "[" expression { "," expression } "]"
    """
    assert tokens[0]["tag"] == "[", f"Expected '[' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "]":
        value, tokens = parse_expression(tokens)
        items.append(value)
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            if tokens[0]["tag"] == "]":
                break
            value, tokens = parse_expression(tokens)
            items.append(value)
    assert tokens[0]["tag"] == "]", f"Expected ']' at position {tokens[0]['position']}, got {tokens[0:]}."
    return {"tag":"list", "items":items}, tokens

def test_parse_list():
    """
    list = "[" expression { "," expression } "]"
    """
    tokens = tokenize("[1,2,3,4]")
    ast, tokens = parse_list(tokens)
    assert ast == {'tag': 'list', 'items': [{'tag': 'number', 'value': 1}, {'tag': 'number', 'value': 2}, {'tag': 'number', 'value': 3}, {'tag': 'number', 'value': 4}]}
    tokens = tokenize("[]")
    ast, tokens = parse_list(tokens)
    assert ast == {'tag': 'list', 'items': []}
    tokens = tokenize("[1,2,3,4,]")
    ast, tokens = parse_list(tokens)
    assert ast == {'tag': 'list', 'items': [{'tag': 'number', 'value': 1}, {'tag': 'number', 'value': 2}, {'tag': 'number', 'value': 3}, {'tag': 'number', 'value': 4}]}
    tokens = tokenize("[1,2,[3,4]]")
    ast, tokens = parse_list(tokens)
    assert ast== {'tag': 'list', 'items': [{'tag': 'number', 'value': 1}, {'tag': 'number', 'value': 2}, {'tag': 'list', 'items': [{'tag': 'number', 'value': 3}, {'tag': 'number', 'value': 4}]}]}    

def parse_object(tokens):
    """
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    """
    assert tokens[0]["tag"] == "{", f"Expected '{{' at position {tokens[0]['position']}"
    tokens = tokens[1:]
    items = []
    if tokens[0]["tag"] != "}":
        key, tokens = parse_expression(tokens)
        assert tokens[0]["tag"] == ":", "Expecting ':'"
        tokens = tokens[1:]
        value, tokens = parse_expression(tokens)
        items.append({"key":key, "value":value})
        while tokens[0]["tag"] == ",":
            tokens = tokens[1:]
            if tokens[0]["tag"] == "}":
                break
            key, tokens = parse_expression(tokens)
            assert tokens[0]["tag"] == ":", "Expecting ':'"
            tokens = tokens[1:]
            value, tokens = parse_expression(tokens)
            items.append({"key":key, "value":value})
    assert tokens[0]["tag"] == "}", f"Expected '}}' at position {tokens[0]['position']}, got {tokens[0:]}."
    return {"tag":"object", "items":items}, tokens

def test_parse_object():
    """
    object = "{" [ expression ":" expression { "," expression ":" expression } ] "}"
    """
    tokens = tokenize("{}")
    ast, tokens = parse_object(tokens)
    assert ast=={'tag': 'object', 'items': []}
    print(ast)
    tokens = tokenize('{"a":1}')
    ast, tokens = parse_object(tokens)
    assert ast == {'tag': 'object', 'items': [{'key': {'tag': 'string', 'value': 'a'}, 'value': {'tag': 'number', 'value': 1}}]}
    tokens = tokenize('{a:1}')
    ast, tokens = parse_object(tokens)
    assert ast == {'tag': 'object', 'items': [{'key': {'tag': 'identifier', 'value': 'a'}, 'value': {'tag': 'number', 'value': 1}}]}
    tokens = tokenize('{a:1,b:{c:2},}')
    ast, tokens = parse_object(tokens)


def parse_factor(tokens):
    """
    factor = <number> | <boolean> | <string> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    """
    token = tokens[0]
    if token["tag"] == "number":
        return {"tag": "number", "value": token["value"]}, tokens[1:]
    if token["tag"] == "string":
        return {"tag": "string", "value": token["value"]}, tokens[1:]
    if token["tag"] == "boolean":
        return {"tag": "boolean", "value": token["value"]}, tokens[1:]
    if token["tag"] == "identifier":
        return {"tag": "identifier", "value": token["value"]}, tokens[1:]
    if token["tag"] == "(":
        ast, tokens = parse_expression(tokens[1:])
        assert tokens[0]["tag"] == ")", f"Expected ')' but got {tokens[0]}"
        return ast, tokens[1:]
    if token["tag"] == "!":
        ast, tokens = parse_expression(tokens[1:])
        return {"tag": "!", "value": ast}, tokens
    if token["tag"] == "-":
        ast, tokens = parse_expression(tokens[1:])
        return {"tag": "negate", "value": ast}, tokens
    if token["tag"] == "[":
        ast, tokens = parse_list(tokens)
        return ast, tokens
    if token["tag"] == "{":
        ast, tokens = parse_object(tokens)
        return ast, tokens
    raise Exception(f"Unexpected token '{token['tag']}' at position {token['position']}, {[[tokens]]}.")

def test_parse_factor():
    """
    factor = <number> | <boolean> | <string> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    """
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        assert ast == {"tag": "number", "value": int(s)}
        assert tokens[0]["tag"] is None
    for s in ['true', 'false']:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        assert ast == {"tag": "boolean", "value": (s == "true")}
        assert tokens[0]["tag"] is None
    for s in ['"1"', '"abc"', '""','"hi""hello"']:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        assert ast == {"tag": "string", "value": s[1:-1].replace('""','"')}
        assert tokens[0]["tag"] is None
    for s in ["(1)", "(22)"]:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        s_n = s.replace("(", "").replace(")", "")
        assert ast == {"tag": "number", "value": int(s_n)}
        assert tokens[0]["tag"] is None
    tokens = tokenize("(2+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 2},
        "right": {"tag": "number", "value": 3},
    }
    tokens = tokenize("x")
    ast, tokens = parse_factor(tokens)
    assert ast == {"tag": "identifier", "value": "x"}
    tokens = tokenize("(x+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "number", "value": 3}
    }
    tokens = tokenize("-(x+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        'tag': 'negate',
        'value': {
            'tag': '+',
            'left': {'tag': 'identifier', 'value': 'x'},
            'right': {'tag': 'number', 'value': 3}
        }
    }
    tokens = tokenize("!1")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': '!', 'value': {'tag': 'number', 'value': 1}}

def parse_term(tokens):
    """
    term = factor { "*"|"/" factor }
    """
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}
    return node, tokens

def test_parse_term():
    """
    term = factor { "*"|"/" factor }
    """
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_term(tokens)
        assert ast == {"tag": "number", "value": int(s)}
        assert tokens[0]["tag"] is None
    tokens = tokenize("2*4")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "tag": "*",
        "left": {"tag": "number", "value": 2},
        "right": {"tag": "number", "value": 4},
    }
    tokens = tokenize("2*4/6")
    ast, tokens = parse_term(tokens)
    assert ast == {
        "tag": "/",
        "left": {
            "tag": "*",
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 4},
        },
        "right": {"tag": "number", "value": 6},
    }

def parse_arithmetic_expression(tokens):
    """
    arithmetic_expression = term { "+"|"-" term }
    """
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}
    return node, tokens

def test_parse_arithmetic_expression():
    """
    arithmetic_expression = term { "+"|"-" term }
    """
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_arithmetic_expression(tokens)
        assert ast == {"tag": "number", "value": int(s)}
        assert tokens[0]["tag"] is None
    tokens = tokenize("2*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "*",
        "left": {"tag": "number", "value": 2},
        "right": {"tag": "number", "value": 4},
    }
    tokens = tokenize("1+2*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 4},
        },
    }
    tokens = tokenize("1+(2+3)*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {
                "tag": "+",
                "left": {"tag": "number", "value": 2},
                "right": {"tag": "number", "value": 3},
            },
            "right": {"tag": "number", "value": 4},
        },
    }

def parse_relational_expression(tokens):
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    """
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<", ">", "<=", ">=", "==", "!="]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}
    return node, tokens

def test_parse_relational_expression():
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression }
    """
    for operator in ["<", ">", "<=", ">=", "==", "!="]:
        tokens = tokenize(f"2{operator}4")
        ast, tokens = parse_relational_expression(tokens)
        assert ast == {
            "tag": operator,
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 4},
        }, f"AST = [{ast}]"
    tokens = tokenize("2>4==3")
    ast, tokens = parse_relational_expression(tokens)
    assert ast == {
        "tag": "==",
        "left": {"tag": ">", "left": {"tag": "number", "value": 2}, "right": {"tag": "number", "value": 4}},
        "right": {"tag": "number", "value": 3},
    }
    tokens = tokenize("x<y>z")
    ast, tokens = parse_relational_expression(tokens)
    assert ast == {
        "tag": ">",
        "left": {
            "tag": "<",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }

def parse_logical_factor(tokens):
    """
    logical_factor = relational_expression
    """
    return parse_relational_expression(tokens)

def test_parse_logical_factor():
    """
    logical_factor = relational_expression
    """
    tokens = tokenize("x")
    ast, tokens = parse_logical_factor(tokens)
    assert ast == {"tag": "identifier", "value": "x"}
    tokens = tokenize("!x")
    ast, tokens = parse_logical_factor(tokens)
    assert ast == {
        "tag": "!",
        "value": {"tag": "identifier", "value": "x"},
    }

def parse_logical_term(tokens):
    """
    logical_term = logical_factor { "&&" logical_factor }
    """
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "&&":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens

def test_parse_logical_term():
    """
    logical_term = logical_factor { "&&" logical_factor }
    """
    tokens = tokenize("x")
    ast, tokens = parse_logical_term(tokens)
    assert ast == {"tag": "identifier", "value": "x"}
    tokens = tokenize("x&&y")
    ast, tokens = parse_logical_term(tokens)
    assert ast == {
        "tag": "&&",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    tokens = tokenize("x&&y&&z")
    ast, tokens = parse_logical_term(tokens)
    assert ast == {
        "tag": "&&",
        "left": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }

def parse_logical_expression(tokens):
    """
    logical_expression = logical_term { "||" logical_term }
    """
    node, tokens = parse_logical_term(tokens)
    while tokens[0]["tag"] == "||":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens

def test_parse_logical_expression():
    """
    logical_expression = logical_term { "||" logical_term }
    """
    tokens = tokenize("x")
    ast, tokens = parse_logical_expression(tokens)
    assert ast == {"tag": "identifier", "value": "x"}
    tokens = tokenize("x||y")
    ast, tokens = parse_logical_expression(tokens)
    assert ast == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    tokens = tokenize("x||y&&z")
    ast, tokens = parse_logical_expression(tokens)
    assert ast == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }

def parse_expression(tokens):
    """
    expression = logical_expression
    """
    return parse_logical_expression(tokens)

def test_parse_expression():
    """
    expression = logical_expression
    """
    for s in ["1", "1+1", "1 && 1", "1 < 2"]:
        t = tokenize(s)
        ast, tokens = parse_expression(t)
        ast2, tokens2 = parse_logical_expression(t)
        assert ast == ast2

def parse_statement_block(tokens):
    """
    statement_block = "{" statement { ";" statement } "}"
    """ 
    ast = {"tag": "block", "statements": []}
    assert tokens[0]["tag"] == "{", f"Expected '{{', got {tokens[0]}"
    tokens = tokens[1:]
    if tokens[0]["tag"] != "}":
        statement, tokens = parse_statement(tokens)
        ast["statements"].append(statement)
    while tokens[0]["tag"] == ";":
        tokens = tokens[1:]
        statement, tokens = parse_statement(tokens)
        ast["statements"].append(statement)
    assert tokens[0]["tag"] == "}", f"Expected '}}', got {tokens[0]}"
    return ast, tokens[1:]

def test_parse_statement_block():
    """
    statement_block = "{" statement { ";" statement } "}"
    """ 
    ast, _ = parse_statement_block(tokenize("{}"))
    assert ast == {'tag': 'block', 'statements': []}
    ast, _ = parse_statement_block(tokenize("{i=2}"))
    assert ast == {'tag': 'block', 'statements': [
        {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'i'},
         'value': {'tag': 'number', 'value': 2}}
    ]}
    ast, _ = parse_statement_block(tokenize("{i=2;k=3}"))
    assert ast == {'tag': 'block', 
        'statements': [
            {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'i'},
             'value': {'tag': 'number', 'value': 2}}, 
            {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'k'},
             'value': {'tag': 'number', 'value': 3}}
        ]
    }

def parse_print_statement(tokens):
    """
    print_statement = "print" [ expression ]
    """
    assert tokens[0]["tag"] == "print", f"Expected 'print', got {tokens[0]}"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        return {"tag": "print", "value": None}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "print", "value": value}, tokens

def test_parse_print_statement():
    """
    print_statement = "print" [ expression ]
    """
    ast, tokens = parse_print_statement(tokenize("print 1"))
    assert ast == {"tag": "print", "value": {"tag": "number", "value": 1}}

def parse_if_statement(tokens):
    """
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    """
    assert tokens[0]["tag"] == "if", f"Expected 'if', got {tokens[0]}"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", f"Expected '(', got {tokens[0]}"
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")", f"Expected ')', got {tokens[0]}"
    tokens = tokens[1:]
    then_statement, tokens = parse_statement_block(tokens)
    else_statement = None
    if tokens[0]["tag"] == "else":
        tokens = tokens[1:]
        else_statement, tokens = parse_statement_block(tokens)
    ast = {
        "tag": "if",
        "condition": condition,
        "then": then_statement,
        "else": else_statement,
    }
    return ast, tokens

def test_parse_if_statement():
    """
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    """
    ast, _ = parse_if_statement(tokenize("if(1){print 1}"))
    assert ast == {
        'tag': 'if', 
        'condition': {'tag': 'number', 'value': 1}, 
        'then': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 1}}]}, 
        'else': None
    }
    ast, _ = parse_if_statement(tokenize("if(1){print 1}else{print 2}"))
    assert ast == {
        'tag': 'if',
        'condition': {'tag': 'number', 'value': 1},
        'then': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 1}}]},
        'else': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 2}}]}
    }

def parse_while_statement(tokens):
    """
    while_statement = "while" "(" expression ")" statement_block
    """
    assert tokens[0]["tag"] == "while", f"Expected 'while', got {tokens[0]}"
    tokens = tokens[1:]
    assert tokens[0]["tag"] == "(", f"Expected '(', got {tokens[0]}"
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")", f"Expected ')', got {tokens[0]}"
    tokens = tokens[1:]
    do_statement, tokens = parse_statement_block(tokens)
    ast = {
        "tag": "while",
        "condition": condition,
        "do": do_statement,
    }
    return ast, tokens

def test_parse_while_statement():
    """
    while_statement = "while" "(" expression ")" statement_block
    """
    ast, _ = parse_while_statement(tokenize("while(1){print 1}"))
    assert ast == {
        'tag': 'while', 
        'condition': {'tag': 'number', 'value': 1}, 
        'do': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 1}}]}
    }

def parse_assignment_statement(tokens):
    """
    assignment_statement = expression [ "=" expression ]
    """
    target, tokens = parse_expression(tokens)
    if tokens[0]["tag"] == "=":
        tokens = tokens[1:]
        value, tokens = parse_expression(tokens)
        return {"tag": "assign", "target": target, "value": value}, tokens
    return target, tokens

def test_parse_assignment_statement():
    """
    assignment_statement = expression [ "=" expression ]
    """
    ast, tokens = parse_assignment_statement(tokenize("i=2"))
    assert ast == {
        "tag": "assign",
        "target": {"tag": "identifier", "value": "i"},
        "value": {"tag": "number", "value": 2},
    }
    ast, tokens = parse_assignment_statement(tokenize("2"))
    assert ast == {"tag": "number", "value": 2}

def parse_break_statement(tokens):
    """
    break_statement = "break"
    """
    assert tokens[0]["tag"] == "break", f"Expected 'break', got {tokens[0]}"
    tokens = tokens[1:]
    ast = {
        "tag": "break",
    }
    return ast, tokens

def test_parse_break_statement():
    """
    break_statement = "break"
    """
    ast, _ = parse_break_statement(tokenize("break"))
    assert ast == {
        'tag': 'break'
    }

def parse_continue_statement(tokens):
    """
    continue_statement = "continue"
    """
    assert tokens[0]["tag"] == "continue", f"Expected 'continue', got {tokens[0]}"
    tokens = tokens[1:]
    ast = {
        "tag": "continue",
    }
    return ast, tokens

def test_parse_continue_statement():
    """
    continue_statement = "continue"
    """
    ast, _ = parse_continue_statement(tokenize("continue"))
    assert ast == {
        'tag': 'continue'
    }


def parse_statement(tokens):
    """
    statement = statement_block | if_statement | while_statement | print_statement | assignment_statement | break_statement | continue_statement
    """
    tag = tokens[0]["tag"]
    if tag == "{":
        return parse_statement_block(tokens)
    if tag == "if":
        return parse_if_statement(tokens)
    if tag == "while":
        return parse_while_statement(tokens)
    if tag == "print":
        return parse_print_statement(tokens)
    if tag == "break":
        return parse_break_statement(tokens)
    if tag == "continue":
        return parse_continue_statement(tokens)
    return parse_assignment_statement(tokens)

def test_parse_statement():
    """
    statement = statement_block | if_statement | while_statement | print_statement | assignment_statement | break_statement | continue_statement
    """
    ast, _ = parse_statement(tokenize("{print 1}"))
    assert ast == {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 1}}]}
    ast, _ = parse_statement(tokenize("print 1"))
    assert ast == {"tag": "print", "value": {"tag": "number", "value": 1}}
    ast, _ = parse_statement(tokenize("x=3"))
    assert ast == {"tag": "assign", "target": {"tag": "identifier", "value": "x"}, "value": {"tag": "number", "value": 3}}
    ast, _ = parse_statement(tokenize("break"))
    assert ast == {
        'tag': 'break'
    }
    ast, _ = parse_statement(tokenize("continue"))
    assert ast == {
        'tag': 'continue'
    }

def parse_program(tokens):
    """
    program = [ statement { ";" statement } ]
    """
    statements = []
    if tokens[0]["tag"]:
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            statement, tokens = parse_statement(tokens)
            statements.append(statement)
    assert tokens[0]["tag"] is None, f"Expected end of input at position {tokens[0]['position']}, got [{tokens[0]}]"
    return {"tag": "program", "statements": statements}, tokens[1:]

def test_parse_program():
    """
    program = [ statement { ";" statement } ]
    """
    ast, tokens = parse_program(tokenize("print 1; print 2"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }

def parse(tokens):
    ast, tokens = parse_program(tokens)
    return ast

# --- Grammar Verification Mechanism ---

# Normalize the grammar by stripping whitespace from each nonempty line.
normalized_grammar = "\n".join([line.strip() for line in grammar.splitlines() if line.strip()])

if __name__ == "__main__":
    test_parse_list()
    test_parse_object()
    exit(0)
    # List of all test functions.
    test_functions = [
        test_parse_factor,
        test_parse_term,
        test_parse_arithmetic_expression,
        test_parse_relational_expression,
        test_parse_logical_factor,
        test_parse_logical_term,
        test_parse_logical_expression,
        test_parse_expression,
        test_parse_statement_block,
        test_parse_print_statement,
        test_parse_if_statement,
        test_parse_while_statement,
        test_parse_assignment_statement,
        test_parse_break_statement,
        test_parse_continue_statement,
        test_parse_statement,
        test_parse_program,
    ]

    test_functions = [
        test_parse_list,
    ]

    untested_grammar = normalized_grammar

    # For each test function, verify that:
    # 1. Its docstring rule appears in the normalized grammar.
    # 2. The corresponding parsing function shares the same docstring rule.
    for test_function in test_functions:
        test_rule = test_function.__doc__.strip().splitlines()[0].strip()
        # print("Testing rule from test:", test_rule)
        if test_rule not in untested_grammar:
            raise Exception(f"Rule [{test_rule}] not found in grammar.")
        untested_grammar = untested_grammar.replace(test_rule, "").strip()

        # Determine the corresponding parsing function name (drop the "test_" prefix).
        parsing_function_name = test_function.__name__[5:]
        print(f"testing {parsing_function_name}...")
        if parsing_function_name not in globals():
            raise Exception(f"Parsing function {parsing_function_name} not found for test {test_function.__name__}")
        parsing_function = globals()[parsing_function_name]
        if not parsing_function.__doc__:
            raise Exception(f"Parsing function {parsing_function_name} has no docstring.")
        function_rule = parsing_function.__doc__.strip().splitlines()[0].strip()
        if test_rule != function_rule:
            raise Exception(
                f"Mismatch in docstring rules for {parsing_function_name}: "
                f"test rule is [{test_rule}] but function rule is [{function_rule}]."
            )
        # Run the test function.
        test_function()

    if untested_grammar.strip():
        print("Untested grammar rules:")
        print(untested_grammar)
    else:
        print("All grammar rules are covered.")

    print("done.")