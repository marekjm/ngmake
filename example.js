cxx = 'g++'.

('build/bin/vm/cpu', ['src/front/cpu.cpp',]) -> (name, dependencies)
    cxx 'foo',
    cxx 'bar'
.

('build/bin/vm/asm', ['src/front/asm.cpp',]) -> (name, dependencies)
    cxx 'build/bin/vm/asm'
.
