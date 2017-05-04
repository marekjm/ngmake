/* Gather parameters into a list. */
macro gather ( ...all ) -> all .

/* Reverse parameters. */
macro reverse ( only ) ->
    gather( only )
; reverse ( first, ...rest ) ->
    gather( ...reverse( ...rest ), first )
.

/* Return head or tail of a list. */
macro head ( first, ...rest ) -> first .
macro tail ( first, ...rest ) -> rest .

/* Echo all parameters. */
macro echo ( ...all ) -> 'echo' ...all .

/* A test target to check output generation. */
do ('test', [ 'Hello', 'beautiful', 'World' ]) -> (name, deps) ->
    echo( name ),
    echo( ...deps ),
    echo( ...reverse( ...deps ) ),
    echo( head( ...deps ) ),
    echo( ...tail( ...deps ) )
.
