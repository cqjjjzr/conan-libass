cmake_minimum_required(VERSION 2.8.12)
project(libass)

option(LIBASS_SHARED "build shared library." OFF)
option(LIBASS_HARFBUZZ "use harfbuzz." OFF)
option(LIBASS_LIBICONV "use libiconv." OFF)
option(LIBASS_ASM "enable assembly optimizing." ON)
macro(setconfig)
set(CONFIG_${ARGV0} ${LIBASS_${ARGV0}})
endmacro()

if(EXISTS "${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
  include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
else()
  include(conanbuildinfo.cmake)
endif()
conan_basic_setup()

set(LIBASS_FRIBIDI ON)
set(LIBASS_FREETYPE ON)

set(LIBASS_BASIC_SOURCES libass/ass.c
                   libass/ass_utils.c
                   libass/ass_string.c
                   libass/ass_strtod.c
                   libass/ass_library.c
                   libass/ass_cache.c
                   libass/ass_font.c
                   libass/ass_fontselect.c
                   libass/ass_render.c
                   libass/ass_render_api.c
                   libass/ass_parse.c
                   libass/ass_shaper.c
                   libass/ass_outline.c
                   libass/ass_drawing.c
                   libass/ass_rasterizer.c
                   libass/ass_rasterizer_c.c
                   libass/ass_bitmap.c
                   libass/ass_blur.c)

if(WIN32 OR CYGWIN)
  set(LIBASS_DIRECTWRITE ON)
  set(LIBASS_FONT_SOURCE libass/ass_directwrite.c)
elseif(APPLE)
  set(LIBASS_CORETEXT ON)
  set(LIBASS_FONT_SOURCE libass/ass_coretext.c)
else()
  set(LIBASS_FONTCONFIG ON)
  set(LIBASS_FONT_SOURCE libass/ass_fontconfig.c)
endif ()

if(MSVC)
  list(APPEND LIBASS_BASIC_SOURCES msvc_compat/dirent.c)
  include_directories(msvc_compat/)
endif()

if (LIBASS_ASM)
  set(CMAKE_ASM_FLAGS "${CFLAGS} -x assembler-with-cpp")
  set(LIBASS_ASM_SOURCE libass/x86/rasterizer.asm
                        libass/x86/blend_bitmaps.asm
                        libass/x86/blur.asm
                        libass/x86/cpuid.asm)
  if (CMAKE_SIZEOF_VOID_P EQUAL 8)
    list(APPEND LIBASS_ASM_SOURCE libass/x86/be_blur.asm)
  endif()

  find_package(Nasm MODULE)

  # https://metricpanda.com/using-nasm-with-cmake-and-clang
  enable_language(ASM_NASM)

  if (CMAKE_ASM_NASM_COMPILER_LOADED)
      set(INTEL 1)

      if ("${CMAKE_SIZEOF_VOID_P}" STREQUAL "4")
          set(BITS 32)
          set(BITTYPE 32)
          set(ASM_FLAGS "-DARCH_X86_64=0")
      else ()
          set(BITS 64)
          set(BITTYPE 64)
          set(ASM_FLAGS "-DARCH_X86_64=1 -DPIC")
      endif ()

      set(ASM_FLAGS "${ASM_FLAGS} -i ${CMAKE_SOURCE_DIR}/libass/")

      if (${APPLE})
          set(ASM_FLAGS "${ASM_FLAGS} -f macho${BITTYPE} -DPREFIX -DHAVE_ALIGNED_STACK=1")
      elseif (${UNIX})
          set(ASM_FLAGS "${ASM_FLAGS} -f elf${BITTYPE} -DHAVE_ALIGNED_STACK=1")
      elseif (${WIN32})
          set(ASM_FLAGS "${ASM_FLAGS} -f win${BITTYPE}")

          if ("${BITS}" STREQUAL "64")
              set(ASM_FLAGS "${ASM_FLAGS} -DHAVE_ALIGNED_STACK=1")
          else ()
              set(ASM_FLAGS "${ASM_FLAGS} -DHAVE_ALIGNED_STACK=0 -DPREFIX")
          endif ()
      else ()
          message(FATAL_ERROR "OS not supported. Disable assembly optimization by using -DLIBASS_ASM=OFF!")
      endif ()

      set(ASM_FLAGS "${ASM_FLAGS} -DHAVE_CPUNOP=0 -Dprivate_prefix=ass")
  else ()
      message(FATAL_ERROR "Failed to enable NASM! Disable assembly optimization by using -DLIBASS_ASM=OFF.")
  endif ()

  set(CMAKE_ASM_NASM_FLAGS ${ASM_FLAGS})
endif()

setconfig(ASM)
setconfig(FREETYPE)
setconfig(FRIBIDI)
setconfig(FONTCONFIG)
setconfig(CORETEXT)
setconfig(DIRECTWRITE)
setconfig(HARFBUZZ)
set(CONFIG_ICONV ${LIBASS_LIBICONV})

list(APPEND LIBASS_SOURCES ${LIBASS_BASIC_SOURCES} ${LIBASS_FONT_SOURCE} ${LIBASS_ASM_SOURCE})

configure_file(config.h.in config.h)
include_directories(${PROJECT_BINARY_DIR})
if (LIBASS_SHARED)
add_library(libass SHARED ${LIBASS_SOURCES})
else()
add_library(libass STATIC ${LIBASS_SOURCES})
endif()
set_property(TARGET libass PROPERTY C_STANDARD 99)
target_link_libraries(libass ${CONAN_LIBS})

set_target_properties(libass PROPERTIES PUBLIC_HEADER "libass/ass.h;libass/ass_types.h")
INSTALL(TARGETS libass
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        PUBLIC_HEADER DESTINATION include
)