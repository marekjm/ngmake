import 'std::util'.
import 'std::list'.

/* A test target to check output generation. */
do ('test', [ 'Hello', 'beautiful', 'World' ]) -> (name, deps) ->
    echo( name ),
    echo( ...deps ),
    echo( ...reverse( ...deps ) ),
    echo( head( ...deps ) ),
    echo( ...tail( ...deps ) )
.
