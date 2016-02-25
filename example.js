cxxflags = '-std=c++11 -Wall -Wextra -Wzero-as-null-pointer-constant -Wuseless-cast -Wconversion -Winline -pedantic -Wfatal-errors -g -I./include'.
cxxoptimizationflags = ''.
coptimizationflags = ''.
dynamic_syms = '-Wl,--dynamic-list-cpp-typeinfo'.
cxx = 'g++'.


function compile(output, compilation_members)
    cxx '-o' output compilation_members
.


('build/bin/vm/cpu', ['src/front/cpu.cpp', 'build/cpu.o'], 'clang++') -> (name, dependencies, cxx)
    cxx '-o' name dependencies,
    compile(name, dependencies)
.

('build/bin/vm/asm', ['src/front/asm.cpp',]) -> (name, dependencies)
    cxx 'build/bin/vm/asm'
.
