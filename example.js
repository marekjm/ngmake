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

/*
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
*/

macro nope () ->
    'Hello World!'
.

macro gather ( ...all ) ->
    all
.

macro reverse ( first, ...rest ) ->
    gather( ...reverse( ...rest ), first )
; reverse ( only ) ->
    gather( only )
.

do ('what', ['foo', 'bar', 'bax']) -> (name, deps) ->
    echo( ...reverse( ...gather( name, ...deps ), name ) )
.

do ('heh', ['0', '1', '2', '3', '4']) -> (name, deps) ->
    echo( ...reverse( ...deps, nope() ) )
.

/*
macro compile ( output, ...deps ) ->
    cxx ...cxxoptions '-o' output ...deps
.
*/
/*
macro compile ( ...all ) ->
    cxx ...cxxoptions '-o' ...all
.

do ('build/bin/vm/kernel', ['src/front/cpu.cpp', 'build/cpu.o']) -> (name, deps) ->
    compile(name, ...deps)
.
*/
