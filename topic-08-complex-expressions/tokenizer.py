import re

# Define patterns for tokens
patterns = [
    [r"print","print"],
    [r"if","if"],
    [r"else","else"],
    [r"while","while"],
    [r"continue","continue"],
    [r"break","break"],
    [r"return","return"],
    [r"assert","assert"],
    [r"and","&&"],
    [r"or","||"],
    [r"not","!"],
    [r"true|false","boolean"],
    [r"\d*\.\d+|\d+\.\d*|\d+", "number"],
    [r'"([^"]|"")*"', "string"],  # string literals
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers
    [r"\+", "+"],
    [r"\-", "-"],
    [r"\*", "*"],
    [r"\/", "/"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\)", ")"],
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"\=", "="],
    [r"\,", ","],
    [r"\;", ";"],
    [r"\:", ":"],
    [r"\&\&", "&&"],
    [r"\|\|", "||"],
    [r"\!", "!"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"\[", "["],
    [r"\]", "]"],
    [r"\.", "."],
    [r"\s+","whitespace"],
    [r".","error"]
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0]) 

def tokenize(characters):
    tokens = []
    position = 0
    while position < len(characters):
        for pattern, tag in patterns:
            match = pattern.match(characters, position)
            if match:
                break
        assert match
        # (process errors)
        if tag == "error":
            raise Exception("Syntax error")
        token = {
            "tag":tag,
            "position":position,
            "value":match.group(0)
        }
        if token["tag"] == "boolean":
            token["value"] = token["value"] == "true"
        if token["tag"] == "number":
            if "." in token["value"]:
                token["value"] = float(token["value"])
            else:
                token["value"] = int(token["value"])
        if token["tag"] == "string":
            token["value"] = token["value"][1:-1].replace('""', '"')
        if token["tag"] != "whitespace":
            tokens.append(token)
        position = match.end()
    # append end-of-stream marker
    tokens.append({
        "tag":None,
        "value":None,
        "position":position
    })
    return tokens

def test_simple_token():
    print("test simple token")
    examples = "+-*/()=;<>{}[].,:"
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example
        assert t["position"] == 0
        assert t["value"] == example
    examples = "==\t!=\t<=\t>=\t&&\t||\t!".split("\t")
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example
        assert t["position"] == 0
        assert t["value"] == example

def test_number_tokens():
    print("test number tokens")
    for s in ["1","11"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == int(s)
    for s in ["1.1","11.11","11.",".11"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == float(s)

def test_boolean_tokens():
    print("test boolean tokens")
    for s in ["true","false"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "boolean"
        assert t[0]["value"] == (s == "true")

def test_string_tokens():
    print("test string tokens")
    for s in ['"1"','"abc"','""']:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "string"
        assert t[0]["value"] == s[1:-1]

def test_multiple_tokens():
    print("test multiple tokens")
    tokens = tokenize("1+2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 1, 'value': '+'}, {'tag': 'number', 'position': 2, 'value': 2}, {'tag': None, 'value': None, 'position': 3}]

def test_whitespace():
    print("test whitespace")
    tokens = tokenize("1 + 2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 2, 'value': '+'}, {'tag': 'number', 'position': 4, 'value': 2}, {'tag': None, 'value': None, 'position': 5}]

def test_keywords():
    print("test keywords...")
    for keyword in [
        "print","if","else","while","continue","break","return","assert"
    ]:
        t = tokenize(keyword)
        assert len(t) == 2
        assert t[0]["tag"] == keyword, f"expected {keyword}, got {t[0]}"
        assert "value" not in t

def test_identifier_tokens():
    print("test identifier tokens...")
    for s in ["x", "y", "z", "alpha", "beta", "gamma"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "identifier"
        assert t[0]["value"] == s



def test_error():
    print("test error")
    try:
        t = tokenize("$1+2")
        assert False, "Should have raised an error for an invalid character."
    except Exception as e:
        assert "Syntax error" in str(e),f"Unexpected exception: {e}"

if __name__ == "__main__":
    test_simple_token()
    test_number_tokens()
    test_boolean_tokens()
    test_string_tokens()
    test_multiple_tokens()
    test_whitespace()
    test_keywords()
    test_identifier_tokens()
    test_error()