cmake_minimum_required(VERSION 3.2)

find_program(NASM_PATH
        NAMES nasm nasm.exe
        PATHS ENV PATH)

if (NASM_PATH)
    message("Found NASM at ${NASM_PATH}")
else ()
    message(FATAL_ERROR "Cannot find NASM")
endif ()
