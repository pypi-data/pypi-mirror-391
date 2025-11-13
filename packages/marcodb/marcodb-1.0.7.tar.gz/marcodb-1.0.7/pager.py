# Pager.py

import os

PAGE_SIZE = 4096 # 4KB

class Pager:
    def __init__(self, db_filename):
        """
        Abre o arquivo .db. Se não existir, cria um.
        Mantém um cache na memória (um dicionário) para as páginas.
        """
        # Abre o arquivo em modo 'r+b' (leitura/escrita binária).
        # Se não existir, 'w+b' (cria/trunca) e depois reabre com 'r+b'.
        # Isso garante que podemos ler e escrever sem apagar o conteúdo.
        
        file_exists = os.path.exists(db_filename)
        
        if not file_exists:
            # Cria o arquivo se não existir
            with open(db_filename, 'w+b') as f:
                # Aloca a Página 0 (Página de Metadados)
                f.write(b'\x00' * PAGE_SIZE)
        
        # Abre o arquivo para leitura e escrita binária
        self.db_file = open(db_filename, 'r+b')
        
        self.cache = {}  # Cache de páginas: { page_id: page_data_bytes }
        self.dirty_pages = set() # Quais páginas no cache foram modificadas
        self.db_filename = db_filename

    def get_page(self, page_id):
        """
        Busca uma página. Primeiro, procura no cache.
        Se não achar, lê do disco.
        """
        if page_id in self.cache:
            return self.cache[page_id]

        # Não está no cache, vamos ler do disco
        offset = page_id * PAGE_SIZE
        self.db_file.seek(offset)
        page_data = self.db_file.read(PAGE_SIZE)

        if not page_data:
            # Isso não deveria acontecer se o new_page for usado corretamente
            # Mas, como garantia, retorna uma página vazia
            page_data = b'\x00' * PAGE_SIZE

        # Converte para bytearray para que possa ser modificado
        self.cache[page_id] = bytearray(page_data) 
        return self.cache[page_id]

    def new_page(self):
        """
        Aloca espaço para uma nova página no final do arquivo.
        Retorna o ID da nova página e seus dados (em branco).
        """
        # Vai para o final do arquivo
        self.db_file.seek(0, 2) # 2 = Fim do arquivo
        file_size = self.db_file.tell()
        
        new_page_id = file_size // PAGE_SIZE
        
        try:
            # Escreve 4KB de zeros para "alocar" a página no disco
            self.db_file.write(b'\x00' * PAGE_SIZE)
        except OSError as e:
            print(f"Erro ao escrever nova página no disco: {e}")
            raise

        # Pega essa página nova (que agora está em branco) e a coloca no cache
        page_data = self.get_page(new_page_id)
        return new_page_id, page_data

    def mark_dirty(self, page_id):
        """
        Nossa Árvore B+ vai chamar isso sempre que modificar uma página no cache.
        """
        self.dirty_pages.add(page_id)

    def flush_all(self):
        """
        Escreve TODAS as páginas "sujas" do cache de volta para o disco.
        """
        if not self.dirty_pages:
            return # Nada para fazer

        # print(f"INFO (Pager): Salvando {len(self.dirty_pages)} páginas...")
        
        for page_id in self.dirty_pages:
            if page_id not in self.cache:
                continue # Página foi marcada como suja mas não está no cache? Estranho.
                
            offset = page_id * PAGE_SIZE
            self.db_file.seek(offset)
            self.db_file.write(self.cache[page_id])
        
        # Garante que o S.O. escreveu no disco (importante para durabilidade)
        self.db_file.flush()
        os.fsync(self.db_file.fileno()) 
        
        self.dirty_pages.clear()

    def close(self):
        """
        Fecha o banco de dados de forma segura.
        """
        self.flush_all()
        self.db_file.close()
        # print("INFO (Pager): Banco de dados fechado.")