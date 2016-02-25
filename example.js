cxxflags = '-std=c++11 -Wall -Wextra -Wzero-as-null-pointer-constant -Wuseless-cast -Wconversion -Winline -pedantic -Wfatal-errors -g -I./include'.
cxxoptimizationflags = ''.
coptimizationflags = ''.
dynamic_syms = '-Wl,--dynamic-list-cpp-typeinfo'.
cxx = 'g++'.

('build/bin/vm/cpu', ['src/front/cpu.cpp',]) -> (name, dependencies)
    cxx '-o' name dependencies,
.

('build/bin/vm/asm', ['src/front/asm.cpp',]) -> (name, dependencies)
    cxx 'build/bin/vm/asm'
.
