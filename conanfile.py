from conans import ConanFile, CMake, tools
import os
import shutil
from distutils.dir_util import copy_tree

class LibasseConan(ConanFile):
    name = "libass"
    version = "0.14.0"
    description = "LibASS is an SSA/ASS subtitles rendering library."
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("conan", "libass", "ass", "subtitle")
    url = "https://github.com/cqjjjzr/conan-libass"
    homepage = "https://github.com/original_author/original_lib"
    author = "Charlie Jiang <cqjjjzr@126.com>"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]      # Packages the license for the conanfile.py
    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt", "config.h.in", "msvc_compat/*", "FindNasm.cmake"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "harfbuzz": [True, False]}
    default_options = {"shared": False, "fPIC": True, "harfbuzz": False}

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "fribidi/1.0.5@bincrafters/stable",
        "freetype/2.10.0@bincrafters/stable"
    )
    build_requires = ("yasm_installer/1.3.0@bincrafters/stable")

    @property
    def _use_fontconfig(self):
        return self.settings.os != 'Windows' and self.settings.os != "Macos"

    def requirements(self):
        if self.options.harfbuzz:
            self.requires("harfbuzz/2.4.0@bincrafters/stable")
        if self._use_fontconfig:
            self.requires("fontconfig/2.13.91@conan/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/libass/libass"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version),
                  sha256="82e70ee1f9afe2e54ab4bf6510b83bb563fcb2af978f0f9da82e2dbc9ae0fd72")
        extracted_dir = self.name + "-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)
        shutil.copy("config.h.in", os.path.join(self._source_subfolder, "config.h.in"))
        shutil.copy("FindNasm.cmake", os.path.join(
            self._source_subfolder, "FindNasm.cmake"))
        shutil.copy("CMakeLists.txt", os.path.join(
            self._source_subfolder, "CMakeLists.txt"))
        copy_tree("msvc_compat", os.path.join(
            self._source_subfolder, "msvc_compat"))

        tools.replace_in_file(os.path.join(
            self._source_subfolder, "libass", "ass_render.c"), "ASS_Outline outline[n_outlines];", "ASS_Outline outline[3];")
        tools.replace_in_file(os.path.join(
            self._source_subfolder, "libass", "ass_outline.c"), "max_subdiv + 1", "16")

    def _configure_cmake(self):
        shutil.copy("conanbuildinfo.cmake", os.path.join(
            self._source_subfolder, "conanbuildinfo.cmake"))
        cmake = CMake(self)
        if self.options.harfbuzz:
            cmake.definitions["ENABLE_HARFBUZZ"] = True
        cmake.configure(source_folder=self._source_subfolder,
                        build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
