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

macro compile ( name, ...all ) ->
    cxx ...cxxoptions '-o' name ...all ,
    'touch' name
.

do ('build/bin/vm/kernel', ['src/front/cpu.cpp', 'build/cpu.o']) -> (name, deps) ->
    compile(name, ...deps),
    compile(name, ...deps)
.

macro compiled_target (name) ->
    echo( name ),
    echo( name )
; compiled_target ( name, deps ) ->
    compile(name, ...deps),
    compile(name, ...deps)
.

macro null ( ...all ) -> .

do ('.PHONY', [ 'build/bin/vm/cpu' ]) -> null .

do ('build/bin/vm/dis', ['src/front/dis.cpp']) -> compiled_target .
do ('build/bin/vm/dis') -> compiled_target .
