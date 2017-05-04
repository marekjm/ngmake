macro echo ( ...all ) -> 'echo' ...all .

do ('test') -> (name) ->
    if boolean name -> echo( name ) else echo( 'Hello World!' )
.

do ('') -> (name) ->
    if boolean name -> echo( name ) else echo( 'Hello World!' )
.

macro gather ( ...all ) -> all .

macro null ( ...all ) -> .

macro filter ( first, ...rest ) ->
    gather( if boolean first -> first else null(), ...filter( ...rest ) )
; filter ( first ) ->
    gather( if boolean first -> first else null() )
.

macro list_to_boolean ( first, ...rest ) ->
    true
; list_to_boolean() ->
    false
.

macro bool ( something ) -> if boolean something -> true else false .

macro this ( something ) -> something .

macro and ( lhs, rhs ) ->
    if lhs -> this( boolean rhs ) else false
.

macro or ( lhs, rhs ) ->
    if lhs -> true else this( boolean rhs )
.

macro all ( first, second, ...rest ) ->
    all( and( first, second ), ...rest )
; all ( first, second ) ->
    and( first, second )
; all ( only ) ->
    boolean only
.

macro and ( lhs, rhs ) ->
    if boolean lhs -> boolean rhs else false
.

do ('fancy', [ 'full', '', 'of', '', 'stuff', '']) -> (name, deps) ->
    boolean name,
    echo( boolean name ),
    echo( boolean '' ),
    echo( deps ),
    echo( ...deps ),
    echo( filter( ...deps ) ),
    echo( ...filter( ...deps ) ),
    echo( list_to_boolean( ...deps ) ),
    echo( 'all deps', all( ...deps ) ),
    echo( 'all filtered deps', all( ...filter( ...deps ) ) ),
.
