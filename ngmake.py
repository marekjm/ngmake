#!/usr/bin/env python3

import string


def isLetter(c):
    return (c == '_' or c in string.ascii_letters)

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


print(string.ascii_letters)
print(string.punctuation)

source_text = ''
with open('./example.js') as ifstream:
    source_text = ifstream.read()

print(genericLexer(source_text))
