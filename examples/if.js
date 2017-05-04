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

do ('fancy', [ 'full', '', 'of', '', 'stuff', '']) -> (name, deps) ->
    boolean name,
    echo( boolean name ),
    echo( boolean '' ),
    echo( deps ),
    echo( ...deps ),
    echo( filter( ...deps ) ),
    echo( ...filter( ...deps ) )
.
