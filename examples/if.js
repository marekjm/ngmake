macro echo ( ...all ) -> 'echo' ...all .

do ('test') -> (name) ->
    if name -> echo( name ) else echo( 'Hello World!' )
.

do ('') -> (name) ->
    if name -> echo( name ) else echo( 'Hello World!' )
.

macro gather ( ...all ) -> all .

macro null ( ...all ) -> .

macro filter ( first, ...rest ) ->
    gather( if first -> first else null(), ...filter( ...rest ) )
; filter ( first ) ->
    gather( if first -> first else null() )
.

do ('fancy', [ 'full', '', 'of', '', 'stuff', '']) -> (name, deps) ->
    echo( deps ),
    echo( ...deps ),
    echo( filter( ...deps ) ),
    echo( ...filter( ...deps ) )
.
