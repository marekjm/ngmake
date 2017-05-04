#!/usr/bin/env python3

"""NAME
    ngmake  -- new generation make


USAGE

    # to compile Ngmake source
    ngmake Ngmakefile > Makefile

    # to display this help message
    ngmake


DESCRIPTION

    Ngmake is a compiler from a free-form functional language to GNU Makefiles.
    It does not replicate any GNU Make logic.

    The language is declarative, and does not support any conditional logic.
    It operates on the assumption that all input is known at the compile time and
    can be manipulated by following a fixed set of rules without the need to make any
    decisions.

    Produced Makefiles are not fit for human consumption or manipulation.
    All variables are expanded by Ngmake so overriding variables like 'make CXX=g++ all' will
    not work.
    GNU Make is used by Ngmake *only* as a dependency solver; everything else happens on the Ngmake
    side.


CONCEPTS

    A brief explanation of Ngmake syntax, with some additional information.
    Ngmake files consist of variable, target, and macro definitions.

    VARIABLES

            let <name> = <value> .

        Variables are immutable; once defined they cannot change.
        The only rebindable variables are macro parameters - they can be bound to a new value when
        a macro is recursively expanded.

        Variables may hold strings, lists, and tuples.

            let cxx = 'g++' .
            let cxxoptions = [ '-Wall', '-Wextra', '-Werror' ] .
            let compilers = ( 'g++', 'clang++', ) .

        Sidenote: there is currently no distinction between lists and tuples.

    EXPRESSIONS

        An expression is either a macro expansion, or a seqence of terminals.
        A terminal is either a literal string, or a variable.

            /* sequence of two terminals; a single expression */
            'echo' message

            /* two macro expansions; two expressions */
            echo(message), stderr(message)

    MACROS

            macro <name> ( <parameters>... ) -> <body> .

        A body is one or more expressions separated by commas.

        Macros are used to abstract and encapsulate a detail of compilation process.
        Macros may contain a single step (e.g. "compile a file"), or many steps.

            macro compile ( target, source ) ->
                cxx cxxoptions '-o' target source
            .

            macro remove ( target ) ->
                'rm' '-f' target
            .

            macro recompile ( target, source ) ->
                remove(target),
                compile(target, source)
            .

    MACRO CLAUSES

            macro <name> ( <parameters-0> ) -> <body-0> ;
                  <name> ( <parameters-1> ) -> <body-1> ;
                  <name> ( <parameters-N> ) -> <body-N> .

        Ngmake decides which macro should be used in an expansion based on the name of the macro, and
        then tries to find a clause for which structures of parameter tuple in macro header and
        structure of argument list tuple match.

        For example, given this macro definition:

            macro compile ( source ) -> /* clause 0. */
                    cxx source ;
                  compile ( target, source ) -> /* clause 1. */
                    cxx '-o' target source .

        the expansions will match as follows:

            /* matches clause 0. */
            compile( 'foo.cpp' )

            /* matches clause 1. */
            compile( 'build/bin/foo', 'foo.cpp' )

            /* no match */
            compile( 'build/bin/bar', 'bar.cpp', 'build/lib/baz.o' )

        This is a very primitive form of pattern matching on macro arity.

    VARIADIC MACROS, LISTS, AND THE '...' (TRIPLE DOT) OPERATOR

            macro <name> ( <parameter-0>, <parameter-N>, ...<parameter-V>) -> <body> .
            macro <name> ( ...<parameter-V>) -> <body> .

        Last parameter of a macro may be "variadic" meaning it can match an unspecified number of
        arguments, and gather them into a single list.
        For example, given this macro definition:

            macro compile ( source ) -> /* clause 0. */
                    cxx source ;
                  compile ( target, source ) -> /* clause 1. */
                    cxx '-o' target source .
                  compile ( target, source, ...deps ) -> /* clause 2. */
                    cxx '-o' target source ...deps .

        the expansions will match as follows:

            /* matches clause 0. */
            compile( 'foo.cpp' )

            /* matches clause 1. */
            compile( 'build/bin/foo', 'foo.cpp' )

            /*
                matches clause 2. with:

                target = 'build/bin/bar'
                source = 'bar.cpp'
                deps = [ 'build/lib/baz.o' ]
            */
            compile( 'build/bin/bar', 'bar.cpp', 'build/lib/baz.o' )

        Using '...' operator in macro's body spreads it into individual elements of the list (or tuple).
        For example, given this macro definition:

            macro echo ( ...all ) -> 'echo' ...all .

        the expansion will work as follows:

            /* step 1. */
            echo( 'Hello', 'beautiful', 'World' )

            /* step 2. */
            echo ( ...all ) with all = [ 'Hello', 'beautiful', 'World' ]

            /* step 3. */
            'echo' ...[ 'Hello', 'beautiful', 'World' ]

            /* step 4. */
            'echo' 'Hello', 'beautiful', 'World'

    MACRO EXPANSION

        Macros are expanded in-place where they are called.
        For example, given these definitions:

            macro echo ( message ) -> 'echo' message .
            macro greeting() -> 'Hello World!' .

        this expression:

            echo( greeting() )

        will be expanded to:

            /* step 1. */
            echo( greeting() )

            /* step 2. */
            echo( 'Hello World!' )

            /* step 3. */
            'echo' 'Hello World!'

    TARGETS

            /* canonical version */
            do ( <target>, <dependencies> ) -> ( <bound-name-for-target>, <bound-name-for-deps> ) ->
                <body>
            .

            /* version with macro implementation */
            do ( <target>, <dependencies> ) -> <name-of-a-macro> .

        Targets can be implemented directly, or by a macro.
        The "implemented by macro" is way to reuse code and avoid writing the same expressions many times.
        Implementing macro must have two parameters.
        Example:

            macro head ( first, ...rest ) -> first .
            macro tail ( first, ...rest ) -> rest .

            macro compile ( target, source, dependencies ) ->
                cxx '-o' target source ...dependencies
            .

            macro compiled ( name, deps ) ->
                compile( name, head(...deps), tail(...deps) )
            .

            do ('build/bin/foo', [ 'src/foo.cpp' ]) -> (name, deps) ->
                compile( name, head(...deps), tail(...deps) )
            .
            do ('build/bin/bar', [ 'src/bar.cpp' ]) -> compiled .

        In target definition the '<target>' part is a string with the name of the target, and
        '<dependencies>' is a list of strings with names of the dependencies of the target.
        These two specifications are equivalent:

            # GNU Make
            build/bin/foo: src/foo.cpp

            /* Ngmake */
            do ('build/bin/foo', [ 'src/foo.cpp' ])


AUTHOR

    Ngmake is written and maintained by Marek Marecki.


COPYRIGHT

    Copyright (c) 2016-2017 Mareck Marecki

    Ngmake is free software; you can redistribute it and/or modify it under the terms of
    the GNU General Public License as published by the Free Software Foundation;
    either version 3 of the License, or (at your option) any later version.

    Ngmake is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program.
    If not, see http://www.gnu.org/licenses/.


SEE ALSO

    make(1)
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
        return str(type(self)).split('.')[-1][:-2] + ' ' + repr(self._value)

class List(NgmakeType):
    def __init__(self, something):
        self._value = something

    def __getitem__(self, i):
        return self._value[i]

class Tuple(NgmakeType):
    def __init__(self, something):
        self._value = something

class String(NgmakeType):
    def __init__(self, something):
        self._value = something

class Atom(NgmakeType):
    def __init__(self, something):
        self._value = something


def _match_group_from_to_dot(from_token):
    matches = []

    i = 0
    limit = len(tokens)

    while i < limit:
        if tokens[i] == from_token:
            part = []
            part.append(tokens[i])
            i += 1
            while i < limit:
                part.append(tokens[i])
                if tokens[i] == '.':
                    break
                i += 1
            matches.append(part)
        i += 1

    return matches

def match_targets(tokens):
    return _match_group_from_to_dot('do')

def match_variables(tokens):
    return _match_group_from_to_dot('let')

def match_macros(tokens):
    return _match_group_from_to_dot('macro')


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

def parse_expressions_list(tokens):
    expressions = []

    i = 0
    limit = len(tokens)

    part = []
    balance = 0
    while i < limit:
        part.append(tokens[i])
        if tokens[i] in ('(', '[',):
            balance += 1
        if tokens[i] in (')', ']',):
            balance -= 1
        if tokens[i] == ',' and balance == 0:
            expressions.append(part[:-1])  # push part without trailing ','
            part = []
        i += 1
    if part:
        expressions.append(part)

    return expressions

def parse_arguments_list(tokens, macros, global_variables, local_variables):
    arguments = []

    parts = parse_expressions_list(tokens)

    for each in parts:
        _, value = consume(each, macros, global_variables, local_variables)
        arguments.extend(value)

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
    target['dependencies'] = (elements[1] if len(elements) > 1 else [])

    # skip '->'
    i += 1

    names = []
    if tokens[i] != '(':
        macro_name = str(tokens[i])
        selected_macro = macros.get(macro_name)
        if selected_macro is None:
            raise Exception(tokens[i], 'could not find matching macro: {}'.format(macro_name))
        names = macros[macro_name][0]['parameters']
        if len(names) != len(elements):
            raise Exception(tokens[i], 'invalid number of parameters in macro: {}'.format(macro_name))
        tokens = tokens[:i] + macros[macro_name][0]['body']
        # unskip '->', reuse it as a parameters-from-body separator
        i -= 1
    else:
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

    if len(names) > 1:
        # set dependencies
        variables[str(names[1])] = list(map(lambda each: str(each)[1:-1], target['dependencies']))

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

def select_overload(macro_name, macros, arguments):
    selected_overload = None
    for clause in macros.get(macro_name, []):
        parameters_length = len(clause['parameters'])
        mismatched_lengths = parameters_length != len(arguments)
        last_parameter_packs = bool(parameters_length and str(clause['parameters'][-1]).startswith('...'))
        arguments_can_be_packed = ((len(arguments) >= parameters_length) and last_parameter_packs)
        if len(arguments) == 0 and parameters_length == 1 and last_parameter_packs:
            arguments_can_be_packed = True

        if mismatched_lengths and not arguments_can_be_packed:
            continue
        selected_overload = clause
        break
    if selected_overload is None:
        raise Exception(each, 'could not find matching macro: {}'.format(macro_name))
    return selected_overload

_evalueate_nest_level = -1
def consume(tokens, macros, global_variables, local_variables):
    value = []

    global _evalueate_nest_level
    _evalueate_nest_level += 1

    # print((_evalueate_nest_level * '|  ') + 'EXPRESSION:  ', list(map(str, tokens)))

    i = 0
    limit = len(tokens)

    each = tokens[i]
    i += 1

    if each == '...':
        skip, subvalue = consume(tokens[i:], macros, global_variables, local_variables)
        i += skip
        value.extend(subvalue[0])
    elif str(each) in macros or (i < limit-1 and tokens[i] == '('):
        macro_name = str(each)

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
        subsequence = parse_arguments_list(subsequence, macros, global_variables, local_variables)

        selected_overload = select_overload(macro_name, macros, subsequence)

        macro_parameters = {}
        for j, param in enumerate(selected_overload['parameters']):
            if param.startswith('...'):
                param = param[3:]
                macro_parameters[param] = subsequence[j:]
            else:
                macro_parameters[param] = subsequence[j]

        # print((_evalueate_nest_level * '|  ') + 'COMPILING-MACRO:', macro_name)

        compiled = compile_body({}, selected_overload, global_variables, macros, macro_parameters)
        value = compiled['body']
    else:
        value.append(resolve(each, global_variables, local_variables))

    # print((_evalueate_nest_level * '|  ') + 'EVALUATED-TO:', value)

    _evalueate_nest_level -= 1
    return i, value

def compile_body(target, source, global_variables, macros, local_variables = None):
    tokens = source['body'][:-1]  # without final '.'
    local_variables = source.get('variables', (local_variables or {}))
    body = []

    i = 0
    limit = len(tokens)

    while i < limit:
        each = tokens[i]

        # print('EACH:', str(each))

        if each == '...':
            i += 1
            skip, value = consume(tokens[i:], macros, global_variables, local_variables)
            body.extend(value[0])
            i += skip - 1
        elif each == ',':
            body.append('\n')
        elif str(each) in macros:
            skip, value = consume(tokens[i:], macros, global_variables, local_variables)
            i += skip
            body.extend(value)
        else:
            body.append(resolve(each, global_variables, local_variables))
        i += 1

        # print('BODY:', body)
        # print('TOKENS-LEFT:', list(map(str, tokens[i:])))

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
    selected_target = (sys.argv[2 + int(flag_debugging)] if len(sys.argv) > (2 + int(flag_debugging)) else None)

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

        compiled_targets = []
        if selected_target is None:
            compiled_targets = map(lambda each: compile(source = each, global_variables = variables, macros = macros), targets)
        else:
            targets = filter(lambda each: str(each['target'])[1:-1] == selected_target, targets)
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
        raise e
