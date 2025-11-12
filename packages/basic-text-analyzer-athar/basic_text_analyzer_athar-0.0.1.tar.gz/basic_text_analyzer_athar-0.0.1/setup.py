import setuptools

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    # IMPORTANT: Make sure this name is unique on PyPI
    # I've added your username to help.
    name="basic_text_analyzer_athar", 
    version="0.0.1",
    author="Athar", # <-- Change this to your full name
    author_email="you@example.com", # <-- Change this to your email
    description="A simple NLP library for basic text analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # This line finds your package folder ('basic_text_analyzer') automatically
    packages=setuptools.find_packages(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    license="MIT", # This simpler field is all setup.py needs
)