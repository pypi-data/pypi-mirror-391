from setuptools import setup, find_packages

# description
with open ('README.md', 'r') as fh:
	long_description = fh.read()

desc = "PowerBlog Toolkit — a Python package to fetch keyword data from Google to analyze search results, and export insights directly to Google Sheets."

setup(
    name="powerblog-toolkit",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "requests",
        "numpy",
        "gspread",
        "gspread-dataframe",
        "google-auth",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samarth-agrawal-86/powerblog_toolkit",
    author="Samarth Agrawal",
    author_email="samarth.agrawal.86@gmail.com",
    description=desc,
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.6',
)
