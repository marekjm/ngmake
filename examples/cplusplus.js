import 'std::cxx'.

let cxx = 'g++' .
let cxxflags = [].

do ('build/bin/foo', [ 'src/foo.cpp', 'include/foo/foo.h' ]) -> default_cxx_target.
