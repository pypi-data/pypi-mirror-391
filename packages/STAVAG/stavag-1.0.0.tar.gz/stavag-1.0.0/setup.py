from setuptools import Command, find_packages, setup


setup(
    name = "STAVAG",
    version = "1.0.0",
    description = "Uncovering directionally and temporally variable genes with STAVAG",
    url = "https://github.com/Zhanglabtools/STAVAG",
    author = "Qunlun Shen",
    author_email = "knotnet@foxmail.com",
    license = "MIT",
    packages = ['STAVAG'],
    install_requires = ["requests",],
    zip_safe = False,
    include_package_data = True,
)
