let cxx = 'g++' .

macro null ( ...all ) -> .

macro gather ( ...all ) -> all .

macro without_headers ( first, ...rest ) ->
    gather( if match( first, '.*\.h$' ) -> null() else first, ...without_headers( ...rest ) )
; without_headers () ->
    gather()
.

macro compile ( target, source, ...deps ) ->
    cxx '-o' target source ...deps
.

do ('build/bin/foo', [ 'src/foo.cpp', 'include/foo/foo.h' ]) -> (name, deps) ->
    compile( name, ...without_headers( ...deps ) )
.
