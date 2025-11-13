from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

# Компилируем основной модуль
extensions = [
    Extension(
        "fake_useragxxx", 
        ["fake_useragxxx.py"],
    ),
]

setup(
    name="fake-useragxxx",
    version="0.0.4",
    description="Fake User-Agent Generator with Gray Randomization",
    author="Anonymous",
    author_email="m00263277@gmail.com", 
    license="Apache-2.0",
    packages=find_packages(include=["fake_useragxxx*"]),
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': 3}
    ),
    python_requires=">=3.7",
)