# setup.py

from setuptools import setup, find_packages

setup(
    name="marcodb",  # O nome que as pessoas vão usar para 'pip install'
    version="1.0.1", # A primeira versão
    author="Marco Lago Pereira", # SEU NOME
    author_email="seu.email@exemplo.com", # SEU EMAIL
    description="Um motor de banco de dados Chave-Valor (B+ Tree) escrito em Python.",
    
    # (Texto longo - podemos copiar da sua descrição da Amazon)
    long_description="""
    [MarcoDB (O Manual)](https://www.amazon.com.br/dp/B0FRYP8P7C)

    [Projetos Práticos com MarcoDB](https://www.amazon.com.br/dp/B0G1NJ3BKC)

    [MarcoDB - pypi org](https://pypi.org/project/marcodb)

    [MarcoDB - GitHub](https://github.com/marconeed/MarcoDB)

    [Sponsor](https://github.com/sponsors/marconeed)

    ______________________________________________________________________________________________

    Existem duas formas principais de interagir com o
    seu banco de dados MarcoDB: através do Shell
    Interativo (MQL) ou da Interface Gráfica (GUI).

    ## O Shell Interativo (shell_interativo.py):

    Como Iniciar:
    1. Abra seu terminal (PowerShell, CMD, etc.).
    2. Navegue até a pasta do projeto.
    3. Execute o script Python:
    Bash
    C:\..._banco_de_dados> python shell_interativo.py
    O que você verá:
    O shell será iniciado, informando qual arquivo de
    banco de dados está sendo usado.
    Bash
    INFO: Criando novo banco de dados
    'MarcoDB.db'...
    INFO: Criando novo banco de dados...
    Bem-vindo ao MarcoDB. Banco 'MarcoDB.db'
    aberto.
    Use a linguagem MQL (set, get, del) ou 'exit' para
    sair.
    MarcoDB> _
    O MarcoDB> é o prompt. Ele está aguardando que
    você digite um comando da linguagem MQL.

    ## A Interface Gráfica (gui.py):

    A GUI (Graphical User Interface) é uma forma
    visual e mais amigável de manipular os dados,
    ideal para quando você quer inspecionar ou
    modificar chaves rapidamente sem digitar
    comandos.
    Como Iniciar:
    1. Abra seu terminal.
    2. Navegue até a pasta do projeto.
    3. Execute o script Python:
    Bash
    C:\..._banco_de_dados> python gui.py
    O que você verá:
    Uma janela será aberta, intitulada "MarcoDB
    Explorer".
    Diferente do shell, a GUI não abre um banco de
    dados automaticamente.
    1. Clique no botão "Abrir/Criar Banco".
    2. Uma caixa de diálogo pedirá o nome do
    arquivo. Digite MarcoDB.db (ou qualquer
    outro nome).
    3. Uma vez aberto, os botões "Inserir (Set)",
    "Buscar (Get)" e "Deletar" ficarão ativos.
    • Para Inserir: Digite a chave e o valor e
    clique em "Inserir".
    • Para Buscar: Digite apenas a chave e clique
    em "Buscar". O valor aparecerá na caixa
    "Valor".
    • Para Deletar: Digite a chave que deseja
    remover e clique em "Deletar"

    ## O Arquivo de Banco de Dados (.db):

    É importante entender que tanto o
    shell_interativo.py quanto o gui.py estão
    trabalhando no mesmo arquivo.
    Se você usar o shell para set chave_A valor_shell e
    depois abrir a GUI e buscar por chave_A, ela
    encontrará o valor_shell.
    O arquivo (MarcoDB.db) é o seu banco de dados.
    As ferramentas são apenas as "portas" para
    acessá-lo.

    _____________________________________________________________________________________________________________________________________________________________________________

    ## Apoie o Projeto

    A Lucida-Flow é um projeto independente e de código aberto. Se você gosta da linguagem e quer ver o seu desenvolvimento continuar, considere [tornar-se um patrocinador no GitHub Sponsors](https://github.com/sponsors/marconeed)! O seu apoio é fundamental para a manutenção e evolução do projeto.

    _____________________________________________________________________________________________________________________________________________________________________________

    # MarcoDB v1.0.0

    Bem-vindo ao MarcoDB, um motor de banco de dados Chave-Valor (B+ Tree) leve e persistente, escrito inteiramente em Python.

    Este projeto foi construído do zero como um exercício prático de ciência da computação.

    ## O Que é Isto?

    * **`btree.py`**: O motor principal da B+ Tree (CRUD, Splits, Merges).
    * **`pager.py`**: O gerenciador de páginas de 4KB.
    * **`serialization.py`**: O tradutor de bytes.
    * **`gui.py`**: Uma interface gráfica (GUI) em Tkinter.
    * **`shell_interativo.py`**: Um shell interativo para a linguagem MQL.

    ## Aviso

    Este é um projeto educacional e não é recomendado para uso em produção (não possui ACID ou concorrência).

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