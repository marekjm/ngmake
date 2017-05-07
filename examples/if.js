import 'std::list'.
import 'std::bool'.

do ('test') -> (name) ->
    if boolean name -> echo( name ) else echo( 'Hello World!' )
.

do ('') -> (name) ->
    if boolean name -> echo( name ) else echo( 'Hello World!' )
.

macro list_to_boolean ( first, ...rest ) ->
    true
; list_to_boolean() ->
    false
.

do ('fancy', [ 'full', '', 'of', '', 'stuff', '']) -> (name, deps) ->
    boolean name,
    echo( boolean name ),
    echo( boolean '' ),
    echo( deps ),
    echo( ...deps ),
    echo( filter( bool, ...deps ) ),
    echo( ...filter( bool, ...deps ) ),
    echo( list_to_boolean( ...deps ) ),
    echo( 'all deps', all( bool, ...deps ) ),
    echo( 'all filtered deps', all( bool, ...filter( bool, ...deps ) ) ),
    echo( 'all', all() ),
    echo( 'not true', not( true ) ),
    echo( 'not false', not( false ) ),
    echo( boolean false ),
.
