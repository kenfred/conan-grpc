from conans import ConanFile, CMake

class GrpcReuseConan(ConanFile):
    version = '1.6.6'
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_dir=self.conanfile_directory, build_dir=".")
        cmake.build()

    def imports(self):
        self.copy("*.dylib", "bin", src="lib")
        self.copy("*.dll",   "bin", src="bin")

    def test(self):
        self.run("bin/greeter_combined")
