from tokenizer import tokenize

"""
parser.py -- implement parser for simple expressions

Accept a string of tokens, return an AST expressed as stack of dictionaries
"""

ebnf = """
    factor = <number> | "(" expression ")"
    term = factor { "*"|"/" factor }
    expression = term { "+"|"-" term }
    statement = <print> expression | expression
    program = expression { ";" expression }
"""


def parse_factor(tokens):
    """
    factor = <number> | "(" expression ")"
    """
    token = tokens[0]
    if token["tag"] == "number":
        return {
            "tag":"number",
            "value": token["value"]
        }, tokens[1:]
    if token["tag"] == "(":
        ast, tokens = parse_expression(tokens[1:])
        assert tokens[0]["tag"] == ")"
        return ast, tokens[1:]
    raise Exception(f"Unexpected token '{token['tag']}' at position {token['position']}.")  

def test_parse_factor():
    """
    factor = <number> | "(" expression ")"
    """
    print("testing parse_factor()")
    for s in ["1","22","333"]:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        assert ast=={'tag': 'number', 'value': int(s)}
        assert tokens[0]['tag'] == None 
    for s in ["(1)","(22)"]:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        s_n = s.replace("(","").replace(")","")
        assert ast=={'tag': 'number', 'value': int(s_n)}
        assert tokens[0]['tag'] == None 
    tokens = tokenize("(2+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}

    # 1. Nested parentheses
    tokens = tokenize("((5))")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': 'number', 'value': 5}

    # 2. Parentheses with multiplication
    tokens = tokenize("(4*6)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        'tag': '*',
        'left': {'tag': 'number', 'value': 4},
        'right': {'tag': 'number', 'value': 6}
    }

    # 3. Parentheses with division
    tokens = tokenize("(10/2)")
    ast, tokens = parse_factor(tokens)
    assert ast == {
        'tag': '/',
        'left': {'tag': 'number', 'value': 10},
        'right': {'tag': 'number', 'value': 2}
    }

    # 4. Mixed operator inside parentheses
    tokens = tokenize("(1+2*3)")
    ast, tokens = parse_factor(tokens)
    # Should be parsed as 1 + (2*3) because of precedence
    assert ast['tag'] == '+'
    assert ast['left'] == {'tag': 'number', 'value': 1}
    assert ast['right']['tag'] == '*'

    # 5. Larger nested expression
    tokens = tokenize("((2+3)*(4-1))")
    ast, tokens = parse_factor(tokens)
    assert ast['tag'] == '*'
    assert ast['left']['tag'] == '+'
    assert ast['right']['tag'] == '-'

    # 6. Parentheses around a single negative number (edge case if tokenizer supports it)
    tokens = tokenize("(-7)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': 'number', 'value': -7}


def parse_term(tokens):
    """
    term = factor { "*"|"/" factor }
    """
    node, tokens = parse_factor(tokens)
    while tokens[0]["tag"] in ["*","/"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_factor(tokens[1:])
        node = {"tag":tag, "left":node, "right":right_node}

    return node, tokens

def test_parse_term():
    """
    term = factor { "*"|"/" factor }
    """
    print("testing parse_term()")
    for s in ["1","22","333"]:
        tokens = tokenize(s)
        ast, tokens = parse_term(tokens)
        assert ast=={'tag': 'number', 'value': int(s)}
        assert tokens[0]['tag'] == None 
    tokens = tokenize("2*4")
    ast, tokens = parse_term(tokens)
    assert ast == {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}
    tokens = tokenize("2*4/6")
    ast, tokens = parse_term(tokens)
    assert ast == {'tag': '/', 'left': {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}, 'right': {'tag': 'number', 'value': 6}}

# 1. Single division
    tokens = tokenize("8/2")
    ast, tokens = parse_term(tokens)
    assert ast == {
        'tag': '/',
        'left': {'tag': 'number', 'value': 8},
        'right': {'tag': 'number', 'value': 2}
    }

    # 2. Multiple multiplications
    tokens = tokenize("2*3*4")
    ast, tokens = parse_term(tokens)
    assert ast == {
        'tag': '*',
        'left': {
            'tag': '*',
            'left': {'tag': 'number', 'value': 2},
            'right': {'tag': 'number', 'value': 3}
        },
        'right': {'tag': 'number', 'value': 4}
    }

    # 3. Multiplication followed by division
    tokens = tokenize("10*2/5")
    ast, tokens = parse_term(tokens)
    assert ast['tag'] == '/'
    assert ast['left']['tag'] == '*'

    # 4. Parentheses affecting factor
    tokens = tokenize("(2*3)")
    ast, tokens = parse_term(tokens)
    assert ast == {
        'tag': '*',
        'left': {'tag': 'number', 'value': 2},
        'right': {'tag': 'number', 'value': 3}
    }

    # 5. Multiplication with parentheses as factor
    tokens = tokenize("6*(2+1)")
    ast, tokens = parse_term(tokens)
    assert ast == {
        'tag': '*',
        'left': {'tag': 'number', 'value': 6},
        'right': {
            'tag': '+',
            'left': {'tag': 'number', 'value': 2},
            'right': {'tag': 'number', 'value': 1}
        }
    }

    
def parse_expression(tokens):
    """
    expression = term { "+"|"-" term }
    """
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+","-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = {"tag":tag, "left":node, "right":right_node}

    return node, tokens

def test_parse_expression():
    """
    expression = term { "+"|"-" term }
    """
    print("testing parse_expression()")
    for s in ["1","22","333"]:
        tokens = tokenize(s)
        ast, tokens = parse_expression(tokens)
        assert ast=={'tag': 'number', 'value': int(s)}
        assert tokens[0]['tag'] == None 
    tokens = tokenize("2*4")
    ast, tokens = parse_expression(tokens)
    assert ast == {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}
    tokens = tokenize("1+2*4")
    ast, tokens = parse_expression(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}}
    tokens = tokenize("1+(2+3)*4")
    ast, tokens = parse_expression(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': '*', 'left': {'tag': '+', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}, 'right': {'tag': 'number', 'value': 4}}}

def parse_statement(tokens):
    """
    statement = <print> expression | expression
    """
    if tokens[0]["tag"] == "print":
        value_ast, tokens = parse_expression(tokens[1:])
        ast = {
            'tag':'print',
            'value': value_ast
        }

    else:
        ast, tokens = parse_expression(tokens)
    return ast, tokens

def test_parse_statement():
    """
    statement = <print> expression | expression
    """
    print("testing parse_statement()")
    tokens = tokenize("1+(2+3)*4")
    ast, tokens = parse_statement(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': '*', 'left': {'tag': '+', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}, 'right': {'tag': 'number', 'value': 4}}}
    tokens = tokenize("print 2*4")
    ast, tokens = parse_statement(tokens)
    assert ast == {'tag': 'print', 'value': {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}}

def parse_program(tokens):
    """
    program = [ statement { ";" statement } ] ;
    """
    statements = []
    if tokens[0]["tag"]:
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            statement, tokens = parse_statement(tokens)
            statements.append(statement)
    assert (
        tokens[0]["tag"] == None
    ), f"Expected end of input at position {tokens[0]['position']}, got [{tokens[0]}]"
    return {"tag": "program", "statements": statements}, tokens[1:]

def test_parse_program():
    """program = [ statement { ";" statement } ]"""
    print("testing parse_program...")
    ast, tokens = parse_program(tokenize("print 1; print 2"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }

def parse(tokens):
    ast, _ = parse_program(tokens)
    return ast

def test_parse():
    """
        program = expression
    """
    print("testing parse()")
    tokens = tokenize("1+(2+3)*4")
    ast1, _ = parse_program(tokens)
    ast2 = parse(tokens)
    assert ast1 == ast2, "parse() is not evaluating via parse_program()"



if __name__ == "__main__":
    test_parse_factor()
    test_parse_term()
    test_parse_expression()
    test_parse_statement()
    test_parse_program()
    test_parse()
    print("done.")
