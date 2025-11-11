from setuptools import setup, find_packages

# Read README with UTF-8 encoding to avoid UnicodeDecodeError on Windows
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scrapery",  # Package name
    version="0.1.21",  # Current version
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="Scrapery: A fast, lightweight library to scrape HTML, XML, and JSON using XPath, CSS selectors, and intuitive DOM navigation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Natural Language :: English"
    ],
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "lxml",
        "cssselect",
        "ujson",
        "chardet",
        "jmespath",
        "ftfy",
        "ijson",
        "pandas",
        "tldextract",
        "openpyxl",
    ],
    keywords="web scraping, html parser, xml parser, json parser, lxml, ujson, data extraction, scraping tools",
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Documentation": "https://scrapery.readthedocs.io/en/latest/",
    },
)
