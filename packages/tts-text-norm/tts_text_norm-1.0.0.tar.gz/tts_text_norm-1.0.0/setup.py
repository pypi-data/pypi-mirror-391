from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tts-text-norm",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="多语言文本规范化库，支持中文、日语和英语",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/<group>/<project>",
    package_dir={
        '': '.',
        'tn': 'WeTextProcessing/tn',
        'itn': 'WeTextProcessing/itn',
    },
    packages=find_packages() + find_packages(where='WeTextProcessing'),
    include_package_data=True,
    package_data={
        '': ['*.fst', '*.tsv', '*.txt', '*.md'],
        'tn': [
            '*.fst', 
            'chinese/data/*/*.tsv', 
            'english/data/*/*.tsv',
            'english/data/*.tsv', 
            'english/data/*/*.far'
        ],
        'itn': ['*.fst', 'chinese/data/*/*.tsv'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="text normalization, nlp, chinese, japanese, english, text processing",
    project_urls={
        "Bug Reports": "https://gitlab.com/<group>/<project>/-/issues",
        "Source": "https://gitlab.com/<group>/<project>",
        "Documentation": "https://gitlab.com/<group>/<project>/-/blob/main/README.md",
    },
)

