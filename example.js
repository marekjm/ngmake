/*
cxxflags = '-std=c++11 -Wall -Wextra -Wzero-as-null-pointer-constant -Wuseless-cast -Wconversion -Winline -pedantic -Wfatal-errors -g -I./include'.
cxxoptimizationflags = ''.
coptimizationflags = ''.
dynamic_syms = '-Wl,--dynamic-list-cpp-typeinfo'.
cxx = 'g++'.


compile(output, compilation_members)
    cxx '-o' output compilation_members
.


do ('build/bin/vm/cpu', ['src/front/cpu.cpp', 'build/cpu.o'],) -> (name, dependencies) ->
    compile(name, dependencies)
.

do ('build/bin/vm/asm', ['src/front/asm.cpp',],) -> (name, dependencies) ->
    cxx 'build/bin/vm/asm'
.

do ('build/bin/dummy',) -> (name) ->
.
*/

let cxx = 'g++' .

do ('build/bin/vm/cpu', ['src/front/cpu.cpp', 'build/cpu.o',]) -> (name, deps) ->
    'g++' '-o' name deps
.
