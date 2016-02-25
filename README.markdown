# New generation Make

> Yet another would-be Makefile killer language.

New generation Make - `ngmake` for short - is a domain specific language designed for expressing
relationships between different files in a source code repository.
These relationships are then used to drive incremental compilations.

Ngmake source compiles to GNU Makefiles.
This is because Make is a good-enough program, but the syntax of Makefiles is horrible.
Ngmake does not try to reinvent Make - it reinvents the language used by it.


----

## Features

Ngmake has a few features that can ease the life of programmers.


### Variables

Variables are processed before any further processing is performed.


### Targets

Targets specify output path and dependencies.
They compile to Makefile rules.


### Functions

Don't repeat yourself.
Ngmake supports multi-step functions that can do much more than plain Make `.X.Y:` rules.


----

## Syntax

Brief description of Ngmake syntax.


### Variables

```
variable_name = 'variable value'.
```

Variables consist of a name, followed by the `=` character, followed by a string.
A full stop ends a variable definition.
Variables can only hold strings.


### Targets

*Basic example*

```
('build/target/name', ['first/dependency.cpp', 'second/dependency.o']) -> (target, dependencies)
    'rm -f' target,
    cxx '-o' target dependencies
.
```

The example above has two parameters:

0. target's name (`'build/target/name'`) bound to `target` variable,
1. target's dependencies (`['first/dependency', 'second/dependency']`) bound to `dependencies` variable,

Bound variables are visible only inside target's body.
Steps are separate by commas.
Target body is terminated by a full stop.


*More advanced example*

```
cxx = 'g++'.

('build/target/name', ['first/dependency.cpp', 'second/dependency.o'], 'clang++') -> (target, dependencies, cxx)
    'rm -f' target,
    cxx '-o' target dependencies
.
```

The example above has two parameters:

0. target's name (`'build/target/name'`) bound to `target` variable,
1. target's dependencies (`['first/dependency', 'second/dependency']`) bound to `dependencies` variable,
2. alternative compiler's name given as a string bound to `cxx` variable,

In the compiled Makefile, `build/target/name` will be compiled with Clang++ instead of G++ because the global `cxx` variable
was shadowed.


### Functions

Functions act more like macros.
They are expanded in the place they are called.
Functions can only be called from targets to prevent infinite recursion as Ngmake has no control structures.

Steps are separate by commas.
Function body is terminated by a full stop.

```
compile(target, dependencies)
    cxx '-o' target dependencies
.

remove(file)
    'rm -f' file
.

('build/target/name', ['first/dependency.cpp', 'second/dependency.o']) -> (target, dependencies)
    remove(target),
    compile(target, dependencies)
.
```

The example above is expanded to the code below before final compilation:

```
('build/target/name', ['first/dependency.cpp', 'second/dependency.o']) -> (target, dependencies)
    'rm -f' target,
    cxx '-o' target dependencies
.
```

----


## License

The code is published under GNU GPL v3 license.
