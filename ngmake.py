#!/usr/bin/env python3

import string


def extract(source):
    quote = source[0]
    i = 1
    backs = 0
    while i < len(source):
        if source[i] == quote and backs == 0:
            break
        if source[i] == quote and backs != 0:
            backs = 0
            i += 1
            continue
        if source[i] == '\\':
            backs += 1
        i += 1
    return source[:i+1]

def genericLexer(source):
    line_no, byte_no, char_no = 0, 0, 0
    tokens = []
    token, c = '', ''
    punctuation = string.punctuation.replace('"', '').replace("'", '')

    i = 0
    while i < len(source):
        c = source[i]
        if c == ' ' or c == '\t':
            if token:
                tokens.append(token)
                token = ''
        elif c == '\n':
            if token:
                tokens.append(token)
                token = ''
            line_no += 1
            char_no = 0
        elif c in punctuation:
            if token:
                tokens.append(token)
                token = ''
            tokens.append(c)
        elif c == '"' or c == "'":
            if token:
                tokens.append(token)
                token = ''
            token = extract(source[i:])
            tokens.append(token)
            i += len(token)-1
            token = ''
        else:
            token += c
        i += 1
        byte_no += 1
        char_no += 1

    return tokens


def reduceArrowOperator(tokens):
    reduced_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i] == '-' and tokens[i+1] == '>':
            reduced_tokens.append('->')
            i += 1
        else:
            reduced_tokens.append(tokens[i])
        i += 1
    return reduced_tokens


def processTokens(tokens):
    variables, rules = {}, {}
    i = 0
    while i < len(tokens):
        i += 1
    return (variables, rules)


source_text = ''
with open('./example.js') as ifstream:
    source_text = ifstream.read()


raw_tokens = genericLexer(source_text)
tokens = reduceArrowOperator(raw_tokens)
print(tokens)


variables, rules = processTokens(tokens)
