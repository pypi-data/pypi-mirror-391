# setup.py (Versão 1.0.1 - Com Entry Points)

from setuptools import setup, find_packages

setup(
    name="marcodb",
    version="1.0.2", # <-- MUDANÇA 1: Nova versão
    author="Marco Lago Pereira", 
    author_email="seu.email@exemplo.com", 
    description="Um motor de banco de dados Chave-Valor (B+ Tree) escrito em Python.",
    
    long_description=open('README.md').read(), # Lê o README
    long_description_content_type="text/markdown",
    
    url="https://github.com/marconeed/MarcoDB", # (Lembre-se de usar seu URL real)
    
    # --- MUDANÇA 2: Especifica os módulos ---
    py_modules=[
        "pager",
        "serialization",
        "btree",
        "gui",
        "shell_interativo"
    ],
    
    # --- MUDANÇA 3: Cria os comandos de terminal ---
    entry_points={
        'console_scripts': [
            'marcodb-shell = shell_interativo:main',
            'marcodb-gui = gui:main',
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
    ],
    python_requires='>=3.7',
)