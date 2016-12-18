from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager(username="btolfa", use_docker=True, gcc_versions=["4.8", "4.9", "5.2", "5.3"])
    builder.add_common_builds()
    builder.run()
