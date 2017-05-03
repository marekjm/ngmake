let cxx = 'g++' .
let cxxoptions = [
    '-Wall',
    '-Wextra',
    '-Werror',
].
let PHONY = (
    'build/bin/vm/cpu',
).

macro echo ( ...all ) ->
    'echo' ...all
.

do ('build/bin/vm/cpu', ['src/front/cpu.cpp', 'build/cpu.o',]) -> (name, deps) ->
    'g++' '-o' name ...deps ,
    echo ( ...deps, name )
.

let test = 'test' .
do (test, []) -> (name, deps) ->
    'g++' name ,
    echo ( 'Hello World!' ) ,
    echo ( ...deps )
.

do ('dafuq', ['foo', 'bar', 'bax', 'bay', 'baz',]) -> (name, deps) ->
    echo ( name, ...deps )
.

macro echo ( ...all ) ->
    'echo' ...all
.

/*
macro reverse ( first, ...rest ) ->
    ... reverse( ...rest ), first
.

do ('foo', []) -> (name, deps) ->
    echo(reverse( 'Hello', 'reversed', 'World' ))
.
*/
