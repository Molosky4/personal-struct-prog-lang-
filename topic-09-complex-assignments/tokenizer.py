import re

patterns = [
    [r"//[^\n]*", "comment"],  # Comment
    [r"\s+", "whitespace"],  # Whitespace
    [r"\d*\.\d+|\d+\.\d*|\d+", "number"],  # numeric literals
    [r'"([^"]|"")*"', "string"],  # string literals
    [r"true|false", "boolean"],  # boolean literals
    [r"null", "null"],  # the null literal
    [r"function", "function"],  # function keyword
    [r"return", "return"],  # return keyword
    [r"extern", "extern"],  # extern keyword
    [r"if", "if"],  # if keyword
    [r"else", "else"],  # else keyword
    [r"while", "while"],  # while keyword
    [r"for", "for"],  # for keyword
    [r"break", "break"],  # for keyword
    [r"continue", "continue"],  # for keyword
    [r"print", "print"],  # print keyword
    [r"import", "import"],  # import keyword
    [r"exit", "exit"],  # exit keyword
    [r"and", "&&"],  # alternate for &&
    [r"or", "||"],  # alternate for ||
    [r"not", "!"],  # alternate for !
    [r"assert", "assert"],
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers
    [r"\+", "+"],
    [r"\-", "-"],
    [r"\*", "*"],
    [r"\/", "/"],
    [r"\%", "%"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"\&\&", "&&"],
    [r"\|\|", "||"],
    [r"\!", "!"],
    [r"\=", "="],
    [r"\.", "."],
    [r"\[", "["],
    [r"\]", "]"],
    [r"\,", ","],
    [r"\:", ":"],
    [r"\;", ";"],
    [r".", "error"],  # unexpected content
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0])

test_generated_tags = set()


# The lex/tokenize function
def tokenize(characters, generated_tags=test_generated_tags):
    line = 1
    tokens = []
    position = 0
    while position < len(characters):
        # find the first token pattern that matches
        for pattern, tag in patterns:
            match = pattern.match(characters, position)
            if match:
                break

        # this should never fail, since the last pattern matches everything.
        assert match

        # note that the tag was generated
        generated_tags.add(tag)

        # complain about errors and throw exception
        if tag == "error":
            raise Exception(f"Syntax error: illegal character : {[match.group(0)]}")

        # package the token
        token = {"tag": tag, "position": position}
        value = match.group(0)
        if token["tag"] == "identifier":
            token["value"] = value
        if token["tag"] == "string":
            token["value"] = value[1:-1].replace('""', '"')
        if token["tag"] == "number":
            if "." in value:
                token["value"] = float(value)
            else:
                token["value"] = int(value)
        if token["tag"] == "boolean":
            token["value"] = True if value == "true" else False

        # append token to stream, skipping whitespace and comments
        if tag == "whitespace":
            for c in value:
                if c == "\n":
                    line = line + 1
        
        token["line"] = line

        if tag not in ["comment", "whitespace"]:
            tokens.append(token)

        # update position for next match
        position = match.end()

    tokens.append({"tag": None, "position": position, "line":line})
    return tokens


def test_simple_tokens():
    print("testing simple tokens...")
    examples = ".,[,],+,-,*,/,(,),{,},;,:,!,&&,||,<,>,<=,>=,==,!=,=,%".split(",")
    examples.append(",")
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example
        assert t["position"] == 0
        assert "value" not in t
    example = "(*/ +-[]{})  //comment"
    t = tokenize(example)
    example = example.replace(" ", "").replace("//comment", "")
    n = len(example)
    assert len(t) == n + 1
    for i in range(0, n):
        assert t[i]["tag"] == example[i]
    t1 = tokenize("and or not")
    t2 = tokenize("&& || !")
    assert [t["tag"] for t in t1] == [t["tag"] for t in t2]


def test_number_tokens():
    print("testing number tokens...")
    for s in ["1", "22", "12.1", "0", "12.", "123145", ".1234"]:
        t = tokenize(s)
        assert len(t) == 2, f"got tokens = {t}"
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == float(s)

def remove_line_info(tokens):
    for token in tokens.copy():
        del token["line"]
    return tokens

def test_string_tokens():
    print("testing string tokens...")
    for s in ['"example"', '"this is a longer example"', '"an embedded "" quote"']:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "string"
        # adjust for the embedded quote behaviour
        assert t[0]["value"] == s[1:-1].replace('""', '"')


def test_boolean_tokens():
    print("testing boolean tokens...")
    for s in ["true", "false"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "boolean"
        assert t[0]["value"] == (
            s == "true"
        ), f"got {[t[0]['value']]} expected {[(s == 'true')]}"
    t = tokenize("null")
    assert len(t) == 2
    assert t[0]["tag"] == "null"


def test_identifier_tokens():
    print("testing identifier tokens...")
    for s in ["x", "y", "z", "alpha", "beta", "gamma", "input"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "identifier"
        assert "value" in t[0], f"Token for '{s}' should have a 'value' field."
        assert t[0]["value"] == s


def test_whitespace():
    print("testing whitespace...")
    for s in ["1", "1  ", "  1", "  1  "]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == 1


def verify_same_tokens(a, b):
    def remove_position(tokens):
        for t in tokens:
            del t["position"]
        return remove_line_info(tokens) 
    return remove_position(tokenize(a)) == remove_position(tokenize(b))


def test_multiple_tokens():
    print("testing multiple tokens...")
    assert remove_line_info(tokenize("1+2")) == [
        {"tag": "number", "value": 1, "position": 0},
        {"tag": "+", "position": 1},
        {"tag": "number", "value": 2, "position": 2},
        {"tag": None, "position": 3},
    ]
    assert remove_line_info(tokenize("1+2-3")) == [
        {"tag": "number", "value": 1, "position": 0},
        {"tag": "+", "position": 1},
        {"tag": "number", "value": 2, "position": 2},
        {"tag": "-", "position": 3},
        {"tag": "number", "value": 3, "position": 4},
        {"tag": None, "position": 5},
    ]

    assert remove_line_info(tokenize("3+4*(5-2)")) == [
        {"tag": "number", "value": 3, "position": 0},
        {"tag": "+",  "position": 1},
        {"tag": "number", "value": 4, "position": 2},
        {"tag": "*",  "position": 3},
        {"tag": "(",  "position": 4},
        {"tag": "number", "value": 5, "position": 5},
        {"tag": "-",  "position": 6},
        {"tag": "number", "value": 2, "position": 7},
        {"tag": ")",  "position": 8},
        {"tag": None, "position": 9},
    ]

    assert verify_same_tokens("3+4*(5-2)", "3 + 4 * (5 - 2)")
    assert verify_same_tokens("3+4*(5-2)", " 3 + 4 * (5 - 2) ")
    assert verify_same_tokens("3+4*(5-2)", "  3  +  4 * (5 - 2)  ")


def test_keywords():
    print("testing keywords...")
    for keyword in [
        "function",
        "return",
        "if",
        "else",
        "while",
        "for",
        "break",
        "continue",
        "assert",
        "extern",  # (reserved for future use)
        "import",  # (reserved for future use)
        "print",
        "exit",
    ]:
        t = remove_line_info(tokenize(keyword))
        assert len(t) == 2
        assert t[0]["tag"] == keyword, f"expected {keyword}, got {t[0]}"
        assert "value" not in t


def test_comments():
    print("testing comments...")
    assert verify_same_tokens("//comment", "\n")
    assert verify_same_tokens("//comment\n", "\n")
    assert verify_same_tokens("//alpha//comment\n", "//alpha\n")
    assert verify_same_tokens("1+5  //comment\n", "1+5  \n")
    assert verify_same_tokens('"beta"//comment\n', '"beta"\n')


def test_error():
    print("testing token errors...")
    try:
        t = remove_line_info(tokenize("$banana"))
        assert False, "Should have a token exception for '$$'."
    except Exception as e:
        error_string = str(e)
        assert "Syntax error" in error_string
        assert "illegal character" in error_string


def test_tag_coverage():
    print("testing tag coverage...")
    for pattern, tag in patterns:
        assert tag in test_generated_tags, f"Tag [ {tag} ] was not tested."


# Test for keyword followed by identifiers
def test_if_identifier_sequence():
    print("testing keyword followed by identifiers...")
    t = remove_line_info(tokenize("if alpha beta"))
    tags = [tok["tag"] for tok in t[:-1]]
    assert tags == ["if", "identifier", "identifier"], f"got {tags}"


if __name__ == "__main__":
    print("testing tokenizer.")
    test_simple_tokens()
    test_number_tokens()
    test_string_tokens()
    test_boolean_tokens()
    test_identifier_tokens()
    test_whitespace()
    test_multiple_tokens()
    test_keywords()
    test_comments()
    test_error()
    test_if_identifier_sequence()
    test_tag_coverage()
    print("done.")
