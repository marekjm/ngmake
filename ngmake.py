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


class InvalidSyntax(Exception):
    pass


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

class Token:
    def __init__(self, text, line, character):
        self._text = text
        self._line = line
        self._character = character

    def __repr__(self):
        return super().__repr__()

    def __str__(self):
        return self._text

    def __getitem__(self, i):
        return self._text[i]

    def __eq__(self, other):
        if type(other) is str:
            return self._text == other
        elif type(other) is Token:
            return (
                (self._text == other._line) and
                (self._line == other._line) and
                (self._character == other._character)
            )
        else:
            return False

    def position(self):
        return (self._line, self._character,)


def generic_lexer(source):
    line_no, char_no = 0, 0
    tokens = []
    token, c = '', ''
    punctuation = string.punctuation.replace('"', '').replace("'", '').replace('_', '')

    i = 0
    while i < len(source):
        c = source[i]
        if c == ' ' or c == '\t':
            if token:
                tokens.append(Token(
                    text = token,
                    line = line_no,
                    character = (char_no - len(token)),
                ))
                token = ''
        elif c == '\n':
            if token:
                tokens.append(Token(
                    text = token,
                    line = line_no,
                    character = (char_no - len(token)),
                ))
                token = ''
            line_no += 1
            char_no = 0
        elif i < (len(source)-1) and c == '/' and source[i+1] == '*':
            i += 1
            while i < len(source)-1 and not (source[i] == '*' and source[i+1] == '/'):
                if source[i] == '\n':
                    line_no += 1
                i += 1
            i += 2
            continue
        elif c in punctuation:
            if token:
                tokens.append(Token(
                    text = token,
                    line = line_no,
                    character = (char_no - len(token)),
                ))
                token = ''
            tokens.append(Token(
                text = c,
                line = line_no,
                character = (char_no - len(token)),
            ))
        elif c == '"' or c == "'":
            if token:
                tokens.append(Token(
                    text = token,
                    line = line_no,
                    character = (char_no - len(token)),
                ))
                token = ''
            token = extract(source[i:])
            tokens.append(Token(
                text = token,
                line = line_no,
                character = (char_no - len(token)),
            ))
            i += len(token)-1
            token = ''
        else:
            token += c
        i += 1
        char_no += 1

    return tokens


def reduce_arrow_operator(tokens):
    reduced_tokens = []
    i = 0
    while i < len(tokens):
        if tokens[i] == '-' and tokens[i+1] == '>':
            reduced_tokens.append(Token('->', *(tokens[i].position())))
            i += 1
        else:
            reduced_tokens.append(tokens[i])
        i += 1
    return reduced_tokens

def reduce_spread_operator(tokens):
    reduced_tokens = []

    i = 0
    limit = len(tokens)

    while i < limit:
        if i < limit-3 and tokens[i] == '.' and tokens[i+1] == '.' and tokens[i+2] == '.':
            reduced_tokens.append(Token('...', *(tokens[i].position())))
            i += 2
        else:
            reduced_tokens.append(tokens[i])
        i += 1

    return reduced_tokens


class NgmakeType:
    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)

class List(NgmakeType):
    def __init__(self, something):
        self._value = something

class Tuple(NgmakeType):
    def __init__(self, something):
        self._value = something

class String(NgmakeType):
    def __init__(self, something):
        self._value = something

class Atom(NgmakeType):
    def __init__(self, something):
        self._value = something


def match_targets(tokens):
    targets = []

    i = 0
    limit = len(tokens)

    while i < limit:
        if tokens[i] == 'do':
            target = []
            target.append(tokens[i])
            i += 1
            while i < limit:
                target.append(tokens[i])
                if tokens[i] == '.':
                    break
                i += 1
            targets.append(target)
        i += 1

    return targets

def match_variables(tokens):
    variables = []

    i = 0
    limit = len(tokens)

    while i < limit:
        if tokens[i] == 'let':
            variable = []
            variable.append(tokens[i])
            i += 1
            while i < limit:
                variable.append(tokens[i])
                if tokens[i] == '.':
                    break
                i += 1
            variables.append(variable)
        i += 1

    return variables

def match_macros(tokens):
    targets = []

    i = 0
    limit = len(tokens)

    while i < limit:
        if tokens[i] == 'macro':
            target = []
            target.append(tokens[i])
            i += 1
            while i < limit:
                target.append(tokens[i])
                if tokens[i] == '.':
                    break
                i += 1
            targets.append(target)
        i += 1

    return targets


def parse_elements(tokens):
    elements = []

    i = 0
    limit = len(tokens)

    while i < len(tokens):
        if tokens[i] == '[':
            subsequence = [tokens[i]]
            i += 1
            balance = 1

            while i < limit and balance > 0:
                subsequence.append(tokens[i])
                if tokens[i] == '[':
                    balance += 1
                if tokens[i] == ']':
                    balance -= 1
                i += 1

            # strip '[' and ']'
            subsequence = subsequence[1:-1]

            elements.append(parse_elements(subsequence))

            if i < limit and tokens[i] != ',':
                raise InvalidSyntax(tokens[i], 'missing comma')
        else:
            elements.append(tokens[i])
            i += 1
            if i < limit and tokens[i] != ',':
                raise InvalidSyntax(tokens[i], 'missing comma')
        i += 1

    return elements

def parse_parameters_list(tokens):
    elements = []

    i = 0
    limit = len(tokens)

    while i < len(tokens):
        if tokens[i] == '...':
            elements.append(Token(('...' + str(tokens[i+1])), *(tokens[i].position())))
            i += 1
        else:
            elements.append(tokens[i])
        i += 1
        if i < limit and tokens[i] != ',':
            raise InvalidSyntax(tokens[i], 'missing comma')
        i += 1

    return elements

def parse_arguments_list(tokens, global_variables, local_variables):
    arguments = []

    i = 0
    limit = len(tokens)

    while i < len(tokens):
        if tokens[i] == '...':
            i += 1
            arguments.extend(resolve(tokens[i], global_variables, local_variables))
        else:
            arguments.append(resolve(tokens[i], global_variables, local_variables))
        i += 1
        if i < limit and tokens[i] != ',':
            raise InvalidSyntax(tokens[i], 'missing comma')
        i += 1

    return arguments

def prepare_target(tokens):
    target = {
        'target': None,
        'dependencies': [],
        'variables': {},
        'body': [],
    }

    i = 0
    limit = len(tokens)

    # skip 'do'
    i += 1

    # header runs until first '->'
    header = []
    while i < limit and tokens[i] != '->':
        header.append(tokens[i])
        i += 1

    # strip '(' and ')'
    header = header[1:-1]

    elements = parse_elements(header)

    target['target'] = elements[0]
    target['dependencies'] = elements[1]

    # skip '->'
    i += 1

    names = []
    while i < limit and tokens[i] != '->':
        names.append(tokens[i])
        i += 1

    # strip '(' and ')'
    names = names[1:-1]
    names = list(map(str, parse_elements(names)))
    target['names'] = names

    variables = {}

    # set name
    variables[str(names[0])] = str(elements[0])[1:-1]

    # set dependencies
    variables[str(names[1])] = list(map(lambda each: str(each)[1:-1], elements[1]))

    for i, name in enumerate(names[2:]):
        variables[str(name)[1:-1]] = elements[i+2]

    target['variables'] = variables

    # skip '->'
    i += 1

    target['body'] = tokens[i:]

    return target

def prepare_macro_clause(tokens):
    macro = {}

    i = 0
    limit = len(tokens)

    # skip name
    i += 1

    parameters = []
    while i < limit and tokens[i] != '->':
        parameters.append(tokens[i])
        i += 1

    # strip '(' and ')'
    parameters = parameters[1:-1]
    parameters = tuple(map(str, parse_parameters_list(parameters)))
    macro['parameters'] = parameters

    # skip '->'
    i += 1

    macro['body'] = tokens[i:]

    return macro

def split_macro_overloads(tokens):
    overloads = []

    clause = []
    i = 0
    limit = len(tokens)

    while i < limit:
        clause.append(tokens[i])
        if tokens[i] in (';', '.',):
            overloads.append(clause)
            clause = []
        i += 1

    return overloads

def prepare_macro(tokens):
    macro = {
        'name': None,
        'overloads': [],
    }

    i = 0
    limit = len(tokens)

    # strip 'macro'
    i += 1

    macro['name'] = str(tokens[i])

    overloads = split_macro_overloads(tokens[i:])
    macro['overloads'] = list(map(prepare_macro_clause, overloads))

    return macro

def despecialise(something):
    if type(something) is Token and str(something)[0] in ('"', "'",):
        return String(str(something)[1:-1])
    elif type(something) is Token and str(something)[0] not in ('"', "'",):
        return Atom(str(something))
    elif type(something) is list:
        return List(list(map(despecialise, something)))
    elif type(something) is tuple:
        return Tuple(tuple(map(despecialise, something)))
    else:
        raise TypeError(type(something))

SUBSEQUENCE_TYPES = { '[': list, '(': tuple, }

def prepare_variable(tokens):
    variable = {
        'name': None,
        'value': None,
    }

    i = 0
    limit = len(tokens)

    # skip 'let'
    i += 1

    variable['name'] = str(tokens[i])
    i += 1

    if tokens[i] != '=':
        raise InvalidSyntax(tokens[i], 'missing assignment')

    # skip '='
    i += 1

    if tokens[i] in ('[', '('):
        subsequence_type = SUBSEQUENCE_TYPES[str(tokens[i])]
        subsequence = tokens[i : -1]
        i += len(subsequence)

        # strip enclosing parentheses
        subsequence = subsequence[1:-1]

        variable['value'] = despecialise(subsequence_type(parse_elements(subsequence)))
    else:
        variable['value'] = despecialise(tokens[i])
        i += 1

    if tokens[i] != '.':
        raise InvalidSyntax(str(tokens[i]), 'invalid variable declaration ending')

    return variable

def resolve(something, global_variables, local_variables):
    value = None
    if something[0] in ('"', "'",):
        value = str(something)[1:-1]
    else:
        value = local_variables.get(str(something), global_variables.get(str(something)))
    if value is None:
        raise Exception(something, 'undefined variable: {}'.format(repr(str(something))))
    return value

def compile_header(source, global_variables):
    target = {
        'variables': source['variables'],
        'dependencies': source['dependencies'],
    }

    target['target'] = resolve(source['target'], global_variables, {})
    target['variables'][source['names'][0]] = target['target']

    return target

def evaluate(tokens, global_variables, local_variables):
    skip = 1
    value = []

    print('EVALUATE:', list(map(str, tokens)))

    i = 0
    limit = len(tokens)

    each = tokens[i]
    i += 1

    if str(each) in macros:
        pass
    else:
        value = [resolve(each, global_variables, local_variables)]

    return skip, value

def compile_body(target, source, global_variables, macros, local_variables = None):
    tokens = source['body'][:-1]  # without final '.'
    local_variables = source.get('variables', (local_variables or {}))
    body = []

    i = 0
    limit = len(tokens)

    while i < limit:
        each = tokens[i]

        if each == '...':
            i += 1
            skip, value = evaluate(tokens[i:], global_variables, local_variables)
            print(value)
            body.extend(value[0])
            i += skip
        elif each == ',':
            body.append('\n')
        elif str(each) in macros:
            macro_name = str(each)
            i += 1

            if tokens[i] != '(':
                raise InvalidSyntax(tokens[i-1], 'missing opening parentheses')

            subsequence = [tokens[i]]
            i += 1
            balance = 1
            while i < limit:
                subsequence.append(tokens[i])
                if tokens[i] == '(':
                    balance += 1
                if tokens[i] == ')':
                    balance -= 1
                if balance <= 0:
                    break
                i += 1

            # strip '(' and ')'
            subsequence = subsequence[1:-1]
            subsequence = parse_arguments_list(subsequence, global_variables, local_variables)

            selected_overload = None
            for clause in macros[macro_name]:
                parameters_length = len(clause['parameters'])
                mismatched_lengths = parameters_length != len(subsequence)
                last_parameter_packs = bool(parameters_length and str(clause['parameters'][-1]).startswith('...'))
                arguments_can_be_packed = ((len(subsequence) >= parameters_length) and last_parameter_packs)
                if len(subsequence) == 0 and parameters_length == 1 and last_parameter_packs:
                    arguments_can_be_packed = True

                if mismatched_lengths and not arguments_can_be_packed:
                    continue
                selected_overload = clause
                break
            if selected_overload is None:
                raise Exception(each, 'could not find matching macro')

            macro_parameters = {}
            for j, param in enumerate(selected_overload['parameters']):
                if param.startswith('...'):
                    param = param[3:]
                    macro_parameters[param] = subsequence[j:]
                else:
                    macro_parameters[param] = subsequence[j]

            compiled = compile_body({}, selected_overload, global_variables, macros, macro_parameters)
            body.extend(compiled['body'])
        else:
            body.append(resolve(each, global_variables, local_variables))
        i += 1

    target['body'] = body
    return target

def compile(source, global_variables, macros):
    target = compile_header(source, global_variables)
    target = compile_body(target, source, global_variables, macros)
    return target

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        exit(1)

    flag_debugging = False
    if sys.argv[1] == '--debug':
        flag_debugging = True

    source_file = sys.argv[1 + int(flag_debugging)]

    try:
        source_text = ''
        with open(source_file) as ifstream:
            source_text = ifstream.read()

        raw_tokens = generic_lexer(source_text)

        tokens = reduce_arrow_operator(raw_tokens)
        tokens = reduce_spread_operator(tokens)

        raw_targets = match_targets(tokens)

        raw_variables = match_variables(tokens)
        raw_macros = match_macros(tokens)

        macros = dict({ each['name']: each['overloads'] for each in map(prepare_macro, raw_macros) })

        targets = list(map(prepare_target, raw_targets))

        variables = dict({ each['name'] : each['value'] for each in map(prepare_variable, raw_variables) })

        compiled_targets = map(lambda each: compile(source = each, global_variables = variables, macros = macros), targets)
        if flag_debugging:
            list(compiled_targets)
        else:
            for i, each in enumerate(compiled_targets):
                lines = []
                line = []
                each['body'].append('\n')
                for part in each['body']:
                    line.append(part)
                    if part == '\n':
                        lines.append('\t' + ' '.join(map(str, line)))
                        line = []
                        continue
                print('{target}: {dependencies}\n{body}'.format(
                    target = each['target'],
                    dependencies = ' '.join(map(str, map(despecialise, each['dependencies']))),
                    body = ''.join(lines),
                ))
    except InvalidSyntax as e:
        token, message = e.args
        line, character = token.position()
        print('error: {}:{}:{}: {}: {}'.format(source_file, line+1, character+1, repr(str(token)), message))
