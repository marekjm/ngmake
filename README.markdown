# New generation Make

> Yet another would-be Makefile killer language.

New generation Make - `ngmake` for short - is a domain specific language designed for expressing
relationships between different files in a source code repository.
These relationships are then used to drive incremental compilations.

Ngmake source compiles to GNU Makefiles.
This is because Make is a good program, but the syntax of Makefiles is horrible.
Ngmake does not try to reinvent Make - it reinvents the language used by it.


----

## Features

Ngmake has a few features that can ease the life of programmers.


### Variables

No trickery. No guessing.
All variables are analysed before target and macro expansion, and
all variables are available to any target or macro.
Local variables shadow those in outer scopes.

```
let <name> = <value> .
```

For example:

```
/* a simple string */
let cxx = 'g++' .

/* or a list */
let cxxoptions = [ '-Wall', '-Werror', ] .

/* or a tuple */
let PHONY = ( 'all', ) .
```


### Targets

Targets specify output path and dependencies, bind them to local variable names, and expand macros.
They compile to Makefile rules.

```
do (<target>, [<dependencies>...]) -> (<bindings>) -> <body> .
```

For example:

```
do ( './build/bin/hello_world', [ './src/hello_world.cpp', ]) -> (name, deps) ->
    'g++' '-o' name ...deps  /* the '...' operator spreads list into individual items
.
```


### Macros

Don't repeat yourself.
Macros can span multiple steps, support recursion, and a very limited form of pattern matching.

```
macro <name> ( <parameters-0>... ) ->
    <body>
; <name> ( <parameters-1>... ) ->
    <body>
; <name> ( <parameters-N>... ) ->
    <body>
.
```

For example:

```
macro compile ( output, dependencies ) ->
    cxx ...cxxoptions '-o' output ...dependencies
; compile ( output ) ->
    cxx ...cxxoptions '-o' output
.
```


----


## License

The code is published under GNU GPL v3 license.
