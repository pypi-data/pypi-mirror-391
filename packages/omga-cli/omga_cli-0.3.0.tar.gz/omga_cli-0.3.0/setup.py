from setuptools import setup, Extension
from Cython.Build import cythonize
import os

extensions = []
for root, dirs, files in os.walk("core"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            module = path[:-3].replace(os.path.sep, ".")
            extensions.append(Extension(module, [path]))

setup(
    name="omga-cli",
    version="0.3.0",
    description="A CLI tool for code checking, explanation, and AI assistance",
    author="Pouria Hosseini",
    author_email="PouriaHosseini@outlook.com",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
    install_requires=[
        "click>=8.0.0",
        "prompt_toolkit>=3.0.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
        "python-dotenv>=0.20.0",
    ],
    entry_points={
        "console_scripts": [
            "omga-cli=core.cli:main"
        ]
    },
    zip_safe=False,
)
