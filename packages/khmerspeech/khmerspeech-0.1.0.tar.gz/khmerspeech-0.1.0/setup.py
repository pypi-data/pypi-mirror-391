import setuptools

with open("README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
  name="khmerspeech",
  version="0.1.0",
  description="A Khmer Speech Toolkit.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/MetythornPenn/khmerspeech",
  author="Metythorn Penn",
  author_email="metythorn@gmail.com",
  license="Apache License 2.0",
  classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "Natural Language :: English",
  ],
  python_requires=">3.8",
  packages=setuptools.find_packages(),
  package_dir={"khmerspeech": "khmerspeech"},
  include_package_data=True,
  package_data={"khmerspeech": ["dict/*.tsv"]},
  install_requires=[
    "urlextract",
    "phonenumbers",
    "regex",
    "ftfy",
  ],
)
