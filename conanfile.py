from conans import ConanFile, ConfigureEnvironment
import os
import shutil
from conans.tools import get, os_info, cpu_count


class IcuConan(ConanFile):
    name = "icu"
    description = "ICU with additional conversion tables"
    version = "58.2"
    url = "https://github.com/btolfa/awcpp-icu"
    license = "http://source.icu-project.org/repos/icu/icu/tags/release-58-1/LICENSE"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generator = "cmake"
    exports = "icu-additional-ucm*"

    def is_visual_studio(self):
        return self.settings.compiler == "Visual Studio"

    def source(self):
        if self.is_visual_studio():
            zip_name = "icu4c-%s-src.zip" % self.version.replace(".", "_")
        else:
            zip_name = "icu4c-%s-src.tgz" % self.version.replace(".", "_")

        get("http://download.icu-project.org/files/icu4c/%s/%s" % (self.version, zip_name))

        data_name = "icu4c-%s-data.zip" % self.version.replace(".", "_")
        get("http://download.icu-project.org/files/icu4c/%s/%s" % (self.version, data_name))

        shutil.rmtree("icu/source/data")
        shutil.move("data", "icu/source/data")

        ucm_path = os.path.join(self.conanfile_directory, "icu-additional-ucm")
        for fl in os.listdir(ucm_path):
            shutil.copy(os.path.join(ucm_path, fl), "icu/source/data/mapping")

    def configure(self):
        if self.is_visual_studio() and \
           self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

    def build(self):
        if self.is_visual_studio():
            self.build_windows()
        else:
            self.build_with_configure()

    def build_windows(self):
        pass

    def normalize_prefix_path(self, p):
        if os_info.is_windows:
            drive, path = os.path.splitdrive(p)
            msys_path = path.replace('\\', '/')
            if drive:
                return '/' + drive.replace(':', '') + msys_path
            else:
                return msys_path
        else:
            return p

    def build_with_configure(self):
        flags = "--prefix='%s' --enable-tests=no --enable-samples=no" % self.normalize_prefix_path(self.package_folder)
        if self.options.shared == 'True':
            flags += ' --disable-static --enable-shared'
        else:
            flags += ' --enable-static --disable-shared'

        if os_info.is_macos:
            conf_name = 'MacOSX'
        elif os_info.is_windows:
            conf_name = 'MinGW'
        elif os_info.is_linux and self.settings.compiler == "gcc":
            conf_name = 'Linux/gcc'
        else:
            conf_name = self.settings.os

        env = ConfigureEnvironment(self)
        command_env = env.command_line_env
        command_env += " CXXFLAGS=-std=c++11"
        if os_info.is_windows:
            command_env += " &&"

        self.run("%s sh icu/source/runConfigureICU %s %s" % (command_env, conf_name, flags))
        self.run("%s make -j %s" % (command_env, cpu_count()))
        self.run("%s make install" % command_env)

    def package(self):
        if not self.is_visual_studio():
            return

        self.copy("*.h", "include", src="icu/include", keep_path=True)
        if self.settings.arch == "x86_64":
            build_suffix = "64"
        else:
            build_suffix = ""

        self.copy(pattern="*.dll", dst="bin", src=("icu/bin%s" % build_suffix), keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=("icu/lib%s" % build_suffix), keep_path=False)

    def package_info(self):
        if os_info.is_windows:
            debug_suffix = ""
            if self.settings.build_type == "Debug":
                debug_suffix = "d"
            self.cpp_info.libs = ["icuin" + debug_suffix, "icuuc" + debug_suffix]
        else:
            self.cpp_info.libs = ["icui18n", "icuuc", "icudata"]
