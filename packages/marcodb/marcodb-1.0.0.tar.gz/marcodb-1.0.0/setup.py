# setup.py

from setuptools import setup, find_packages

setup(
    name="marcodb",  # O nome que as pessoas vão usar para 'pip install'
    version="1.0.0", # A primeira versão
    author="Marco Lago Pereira", # SEU NOME
    author_email="seu.email@exemplo.com", # SEU EMAIL
    description="Um motor de banco de dados Chave-Valor (B+ Tree) escrito em Python.",
    
    # (Texto longo - podemos copiar da sua descrição da Amazon)
    long_description="""
    MarcoDB é um banco de dados Chave-Valor leve, rápido e persistente,
    construído do zero em Python puro. Ele usa um motor B+ Tree para
    garantir buscas e inserções rápidas. Este pacote fornece o motor
    principal e as ferramentas de interface.
    """,
    long_description_content_type="text/markdown",
    
    # (EDITAR) Coloque o URL do SEU repositório GitHub aqui
    url="https://github.com/marconeed/MarcoDB", 
    
    # Encontra automaticamente os nossos ficheiros .py
    packages=find_packages(where="."),
    
    # Diz ao PyPI que este pacote funciona com Python 3
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # (Vamos assumir a licença MIT)
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7', # O requisito que definimos
)