from tokenizer import tokenize
from parser import parse

printed_string = None

def evaluate(ast, environment={}):
    global printed_string
    if ast["tag"] == "program":
        # TODO: Should this return a value? Probably not? 
        status = None
        last_value = None
        for statement in ast["statements"]:
            value, status = evaluate(statement, environment)
            last_value = value
            if status:
                return value, status
        return last_value, status
    if ast["tag"] == "block":
        for statement in ast["statements"]:
            value, status = evaluate(statement, environment)
            if status:
                return value, status
        return None, None
    if ast["tag"] == "print":
        value, status = evaluate(ast["value"], environment)
        if status:
            return value, status
        s = str(value)
        print(s)
        printed_string = s
        return None, None
    if ast["tag"] == "if":
        condition_value, status = evaluate(ast["condition"], environment)
        if condition_value:
            value, status = evaluate(ast["then"], environment)
            if status:
                return value, status
        else:
            if ast["else"]:
                value, status = evaluate(ast["else"], environment)
            if status:
                return value, status
        return None, None
    if ast["tag"] == "while":
        print(environment)
        value, status = evaluate(ast["condition"], environment)
        if status:
            return value, status
        while value:
            print(environment)
            value, status = evaluate(ast["do"], environment)
            if status:
                if status == "break":
                    break
                if status == "continue":
                    continue
                return value, status
            value, status = evaluate(ast["condition"], environment)
            if status: 
                return value, status
        return None, None
    if ast["tag"] == "break":
        return None, "break"
    if ast["tag"] == "continue":
        return None, "continue"
    if ast["tag"] == "assign":
        target = ast["target"]
        assert target["tag"] == "identifier"
        identifier = target["value"]
        assert type(identifier) is str
        value, status = evaluate(ast["value"],environment)
        if status:
            return value, status
        environment[identifier] = value
        return None, None
    if ast["tag"] == "number":
        return ast["value"], None
    if ast["tag"] == "string":
        return ast["value"], None
    if ast["tag"] == "identifier":
        if ast["value"] in environment:
            return environment[ast["value"]], None
        parent_environment = environment
        while "$parent" in parent_environment:
            parent_environment = environment["$parent"]
            if ast["value"] in parent_environment:
                return parent_environment[ast["value"]], None
        raise Exception(f"Value [{ast["value"]}] not found in environment {environment}.")
    if ast["tag"] in ["+", "-", "*", "/"]:
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        if ast["tag"] == "+":
            return left_value + right_value, None
        if ast["tag"] == "-":
            return left_value - right_value, None
        if ast["tag"] == "*":
            return left_value * right_value, None
        if ast["tag"] == "/":
            return left_value / right_value, None
    if ast["tag"] == "negate":
        value, status= evaluate(ast["value"], environment)
        if status:
            return left_value, status
        return -value, None
    if ast["tag"] == "&&":
        # TODO: Implement short circuit code
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value and right_value, None
    if ast["tag"] == "||":
        # TODO: Implement short circuit code
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value or right_value, None
    if ast["tag"] == "!":
        value, status = evaluate(ast["value"], environment)
        if status:
            return value, status
        return not value, None
    if ast["tag"] == "<":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value < right_value, None
    if ast["tag"] == ">":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value > right_value, None
    if ast["tag"] == "<=":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value <= right_value, None
    if ast["tag"] == ">=":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value >= right_value, None
    if ast["tag"] == "==":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value == right_value, None
    if ast["tag"] == "!=":
        left_value, status = evaluate(ast["left"], environment)
        if status:
            return left_value, status
        right_value, status = evaluate(ast["right"], environment)
        if status:
            return right_value, status
        return left_value != right_value, None
    assert False, f"Unexpected ast tag, [{ast["tag"]}]"


def test_evaluate_number():
    print("testing evaluate number")
    assert evaluate({"tag":"number","value":4}) == (4, None)

def test_evaluate_addition():
    print("testing evaluate addition")
    ast = {
        "tag":"+",
        "left":{"tag":"number","value":1},
        "right":{"tag":"number","value":3}
        }
    assert evaluate(ast) == (4, None)

def test_evaluate_subtraction():
    print("testing evaluate subtraction")
    ast = {
        "tag":"-",
        "left":{"tag":"number","value":3},
        "right":{"tag":"number","value":2}
        }
    assert evaluate(ast) == (1, None)

def test_evaluate_multiplication():
    print("testing evaluate multiplication")
    ast = {
        "tag":"*",
        "left":{"tag":"number","value":3},
        "right":{"tag":"number","value":2}
        }
    assert evaluate(ast) == (6, None)

def test_evaluate_division():
    print("testing evaluate division")
    ast = {
        "tag":"/",
        "left":{"tag":"number","value":4},
        "right":{"tag":"number","value":2}
        }
    assert evaluate(ast) == (2, None)

def eval(s, environment={}):
    tokens = tokenize(s)
    ast = parse(tokens)
    result, status = evaluate(ast, environment)
    assert status == None
    return result

def test_evaluate_expression():
    print("testing evaluate expression")
    assert eval("1+2+3") == 6
    assert eval("1+2*3") == 7
    assert eval("(1+2)*3") == 9
    assert eval("(1.0+2.1)*3") == 9.3
    assert eval("1<2") == True
    assert eval("2<1") == False
    assert eval("2>1") == True
    assert eval("1>2") == False
    assert eval("1<=2") == True
    assert eval("2<=2") == True
    assert eval("2<=1") == False
    assert eval("2>=1") == True
    assert eval("2>=2") == True
    assert eval("1>=2") == False
    assert eval("2==2") == True
    assert eval("1==2") == False
    assert eval("2!=1") == True
    assert eval("1!=1") == False
    # tokens = tokenize("-1")
    # ast = parse(tokens)
    # result = evaluate(ast, {})
    # print(ast, result)
    # exit(0)

    assert eval("-1") == -1
    assert eval("-(1)") == -1
    assert eval("!1") == False
    assert eval("!0") == True
    assert eval("0&&1") == False
    assert eval("1&&1") == True
    assert eval("1||1") == True
    assert eval("0||1") == True
    assert eval("0||0") == False


def test_evaluate_identifier():
    print("testing evaluate identifier")
    try:
        assert eval("x+3") == 6
        raise Exception("Error expected for missing value in environment")
    except Exception as e:
        assert "not found" in str(e) 
    assert eval("x+3", {"x":3}) == 6
    assert eval("x+y",{"x":4,"y":5}) == 9
    assert eval("x+y",{"$parent":{"x":4},"y":5}) == 9

def test_evaluate_print():
    print("testing evaluate print")
    assert eval("print 3") == None    
    assert printed_string == "3"
    assert eval("print 3.14") == None    
    assert printed_string == "3.14"

def test_evaluate_assignment():
    print("testing evaluate assignment")
    env = {"x":4,"y":5}
    assert eval("x=7",env) == 7
    assert env["x"] == 7

def test_if_statement():
    print("testing if statement")
    env = {"x":4,"y":5}
    assert eval("if(1){x=8}",env) == None
    assert env["x"] == 8
    assert eval("if(0){x=5}else{y=9}",env) == None
    assert env["x"] == 8
    assert env["y"] == 9

def test_while_statement():
    print("testing while statement")
    env = {"x":4,"y":5}
    assert eval("while(x<6){y=y+1;x=x+1}",env) == None
    assert env["x"] == 6
    assert env["y"] == 7

if __name__ == "__main__":
    test_evaluate_number()
    test_evaluate_addition()
    test_evaluate_subtraction()
    test_evaluate_multiplication()
    test_evaluate_division()
    test_evaluate_expression()
    test_evaluate_print()
    test_evaluate_identifier()
    test_if_statement()
    test_while_statement()
    print("done.")
