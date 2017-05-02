#!/usr/bin/env python3

"""NAME
    ngmake  -- new generation make


USAGE

    # to compile Ngmake source
    ngmake Ngmakefile > Makefile

    # to display this help message
    ngmake


DESCRIPTION

    Ngmake is a compiler to GNU Makefiles from a more sane language (a.k.a. "Yet another Makefile language").
    Supported features include function (target), macro, and variable declarations.
    Macros are small pieces of translation logic inlined inside functions.
    For example, a function may be used to compile a final target but a macro is used to encapsulate the
    generic logic actually used to perform required actions.


NGMAKEFILE SYNTAX

    Functions

            ('build/target', ['src/dependency0.c', 'src/dependency1.c']) -> (target, dependencies)
                'rm' '-f' target,
                'g++' '-o' target dependencies
            .

        Functions are used to encode steps required to make a target.
        They can contain arbitrary number of steps, separated by commas.
        A function definition ends with a period character.

    Macros

            remove(target) 'rm' '-f' target .
            compile(target, dependencies) 'g++' '-o' target dependencies .

            ('build/target', ['src/dependency0.c', 'src/dependency1.c']) -> (target, dependencies)
                remove(target),
                compile(target, dependencies)
            .

        Macros are smaller containers for making steps.
        They can be called inside functions.
        A call to a macro inlines it.

    Variables

            compiler = 'g++'.

            remove(target) 'rm' '-f' target .
            compile(target, dependencies) compiler '-o' target dependencies .

            ('build/target', ['src/dependency0.c', 'src/dependency1.c']) -> (target, dependencies)
                remove(target),
                compile(target, dependencies)
            .

        Variables are used to hold values used during making process.
        Variables can be shadowed by parameters of the same name passed to macro or a function:

            ('build/target', ['src/dependency0.c', 'src/dependency1.c'], 'clang++') -> (target, dependencies, compiler)
                remove(target),
                compile(target, dependencies)
            .

        Once shadowed, old value of a variable cannot be obtained.
"""

import re
import string
import sys


name_regex = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


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

def generic_lexer(source):
    line_no, byte_no, char_no = 0, 0, 0
    tokens = []
    token, c = '', ''
    punctuation = string.punctuation.replace('"', '').replace("'", '').replace('_', '')

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


def reduce_arrow_operator(tokens):
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


def split_list(delimiter, ls):
    sublists = []
    current = []
    for element in ls:
        if element == delimiter:
            sublists.append(current)
            current = []
            continue
        current.append(element)
    sublists.append(current)
    return sublists

def split_steps(steps):
    substeps = []
    current = []
    i = 0
    while i < len(steps):
        element = steps[i]
        if element == ',':
            substeps.append(current)
            current = []
        elif element == '(':
            current.append('(')
            i += 1
            while steps[i] != ')':
                current.append(steps[i])
                i += 1
            current.append(')')
        else:
            current.append(element)
        i += 1
    substeps.append(current)
    return substeps


def extract_list(tokens):
    extracted_list = []
    balance = 1
    i = 1
    while i < len(tokens) and balance:
        if tokens[i] == '[':
            balance += 1
        elif tokens[i] == ']':
            balance -= 1
        elif tokens[i] == ',':
            # skip commas
            pass
        else:
            extracted_list.append(tokens[i])
        i += 1
    return (extracted_list, i)

def extract_tuple(tokens):
    extracted_tuple = []
    balance = 1
    i = 1
    while i < len(tokens) and balance:
        if tokens[i] == '(':
            balance += 1
        elif tokens[i] == ')':
            balance -= 1
        elif tokens[i] == ',':
            # skip commas
            pass
        elif tokens[i] == '[':
            pt, inc = extract_list(tokens[i:])
            extracted_tuple.append(pt)
            i += inc-1
        else:
            extracted_tuple.append(tokens[i])
        i += 1
    return (extracted_tuple, i)

def process_rule(tokens):
    name, inc = '', 0

    i = 0
    while i < len(tokens):
        if tokens[i] == '.':
            break
        i += 1
    inc = i

    i = 0
    target_spec, adv = extract_tuple(tokens[i:])
    i += adv
    i += 1 # skip arrow operator
    arguments, adv = extract_tuple(tokens[i:])
    i += adv

    steps = []
    if inc:
        steps = split_steps(tokens[i:inc])

    args = {}
    for n, name in enumerate(arguments):
        args[name] = target_spec[n]

    return (args[arguments[0]][1:-1], {'arguments': args, 'steps': steps, 'dependencies': args[arguments[1]]}, inc)

def process_assignment(tokens):
    name, value, inc = '', None, 0

    i = 0
    name = tokens[i]
    i += 1
    i += 1 # skip '='
    value = tokens[i]

    return (name, value, inc)

def process_function(tokens):
    name, arguments, inc = '', [], 0

    i = 0
    while i < len(tokens):
        if tokens[i] == '.':
            break
        i += 1
    inc = i

    i = 0
    name = tokens[i]
    i += 1 # skip name
    arguments, adv = extract_tuple(tokens[i:])
    i += adv

    steps = split_list(',', tokens[i:inc])

    return (name, arguments, steps, inc)

def process_tokens(tokens):
    variables, functions, rules = {}, {}, {}
    i = 0
    while i < len(tokens):
        if tokens[i] == '(' and tokens[i+1][0] in ['"', "'"]:
            name, rule, inc = process_rule(tokens[i:])
            rules[name] = rule
            i += inc
        elif name_regex.match(tokens[i]) and tokens[i+1] == '(':
            name, arguments, steps, inc = process_function(tokens[i:])
            functions[name] = {'arguments': arguments, 'steps': steps,}
            i += inc
        elif name_regex.match(tokens[i]) and tokens[i+1] == '=':
            name, value, inc = process_assignment(tokens[i:])
            variables[name] = value
            i += inc
        i += 1
    return (variables, functions, rules)


def prepare_step(step, variables, arguments):
    parts = []
    for chunk in step:
        if chunk[0] in ["'", '"']:
            parts.append(chunk[1:-1])
        else:
            if chunk in arguments:
                pt = arguments[chunk]
                if type(pt) is list:
                    pt = ' '.join(map(lambda s: (s[1:-1] if s[0] in ['"', "'"] else s), pt))
                if pt[0] in ['"', "'"]:
                    pt = pt[1:-1]
                parts.append(pt)
            else:
                parts.append('$({0})'.format(chunk.upper()))
    return ' '.join(parts)

def prepare_extended_steps(step, variables, functions):
    extended_steps = []
    name = step[0]
    arguments, adv = extract_tuple(step[1:])
    args = {}
    for n, arg_name in enumerate(functions[name]['arguments']):
        args[arg_name] = arguments[n]
    for s in functions[name]['steps']:
        current = []
        for ss in s:
            if ss in args:
                ss = args[ss]
            current.append(ss)
        extended_steps.append(current)
    return extended_steps

def prepare_output(variables, functions, rules):
    output_text = ''
    for k in sorted(variables.keys()):
        output_text += '{0}={1}\n'.format(k.upper(), variables[k][1:-1])
    if output_text:
        output_text += '\n\n'
    for name in sorted(rules.keys()):
        output_text += '{0}: {1}\n'.format(name, ' '.join(map(lambda s: s[1:-1], rules[name]['dependencies'])))
        final_steps = []
        for step in rules[name]['steps']:
            if step[0] in functions and step[1] == '(':
                final_steps.extend(prepare_extended_steps(step, variables, functions))
            else:
                final_steps.append(step)
        for step in final_steps:
            output_text += '\t{0}\n'.format(prepare_step(step, variables, rules[name]['arguments']))
        output_text += '\n'
    return output_text.rstrip('\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        exit(1)

    source_text = ''
    with open(sys.argv[1]) as ifstream:
        source_text = ifstream.read()


    raw_tokens = generic_lexer(source_text)
    tokens = reduce_arrow_operator(raw_tokens)

    variables, functions, rules = process_tokens(tokens)

    output_text = prepare_output(variables, functions, rules)
    print(output_text)
