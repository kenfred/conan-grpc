import shutil
import os, sys

from conans import ConanFile
from conans import tools
from conans.errors import ConanException
from conans.tools import os_info, SystemPackageTool, download, untargz, replace_in_file, unzip
from conans import CMake

class GrpcConan(ConanFile):
    name = "grpc"
    version = "1.6.6"
    url = "https://github.com/sourcedelica/conan-grpc"
    repo_url = 'https://github.com/grpc/grpc.git'
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "use_proto_lite": [True, False],
        "build_tests": [True, False]
    }
    default_options = "shared=False", "use_proto_lite=False", "build_tests=False"

    license = "Apache License 2.0"
    requires = 'zlib/1.2.11@conan/stable', \
                'OpenSSL/1.0.2l@conan/stable', \
                'c-ares/1.13.0@lhcorralo/testing', \
                'Protobuf/3.4.0@kenfred/testing', \
                'gflags/2.2.0@kenfred/testing', \
                'benchmark/1.1.0@jjones646/stable'

    description = "An RPC library and framework"
    generators = "cmake", "txt"
    short_paths = True
    _source_dir = "grpc-%s" % version

    def source(self):
        file_name = "v%s.zip" % self.version if sys.platform == "win32" else "v%s.tar.gz" % self.version
        zip_name = "grpc-%s.zip" % self.version if sys.platform == "win32" else "grpc-%s.tar.gz" % self.version
        url = "https://github.com/grpc/grpc/archive/%s" % file_name
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        cmake = CMake(self)

        replace_in_file(os.path.join(self._source_dir, "CMakeLists.txt"), 'find_package(c-ares CONFIG)', 'find_package(cares MODULE)', strict=False)
        

        defs = dict()
        defs['gRPC_BUILD_TESTS'] = "ON" if self.options.build_tests else "OFF"
        defs['CMAKE_INSTALL_PREFIX'] = self.package_folder
        defs['gRPC_ZLIB_PROVIDER'] = "package"
        defs['gRPC_CARES_PROVIDER'] = "package"
        defs['gRPC_SSL_PROVIDER'] = "package"
        defs['gRPC_PROTOBUF_PROVIDER'] = "package"
        defs['gRPC_PROTOBUF_PACKAGE_TYPE'] = "CONFIG"
        defs['gRPC_GFLAGS_PROVIDER'] = "package"
        defs['gRPC_BENCHMARK_PROVIDER'] = "package"
        defs['gRPC_USE_PROTO_LITE'] = "ON" if self.options.use_proto_lite else "OFF"

        if self.settings.compiler == "Visual Studio":
            vs_runtime = "%s" % self.settings.compiler.runtime
            defs['gRPC_MSVC_STATIC_RUNTIME'] = "ON" if (vs_runtime[:2] == "MT") else "OFF"

        # defs['ZLIB_ROOT'] = self.deps_cpp_info['zlib'].rootpath   
        # defs['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['OpenSSL'].rootpath
        dirs = ';'.join(self.deps_cpp_info.builddirs)
        dirs = dirs.replace('\\','/')
        self.output.info(dirs)
        defs['CMAKE_MODULE_PATH'] = dirs
        defs['CMAKE_PREFIX_PATH'] = dirs 
            
        cmake.configure(source_dir=self._source_dir, build_dir=".", defs=defs)
        cmake.build()
        cmake.install()


    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["gpr", "grpc", "grpc_cronet", "grpc_csharp_ext",
                                "grpc_plugin_support", "grpc_unsecure", 
                                "grpc++", "grpc++_cronet", "grpc++_error_details",
                                "grpc++_reflection", "grpc++_unsecure"]
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
