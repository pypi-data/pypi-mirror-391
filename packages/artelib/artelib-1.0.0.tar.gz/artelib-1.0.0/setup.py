from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="artelib",
    version="1.0.0",
    author="Artem057",
    author_email="justarockergame@gmail.com",
    description="A simple web framework inspired by Flask",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/artelib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pyttsx3>=2.90.0",
    ],
    keywords="web, framework, flask-like, http",
)