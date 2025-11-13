# serialization.py (Versão Final Corrigida)

import struct

# Constantes de Tipo de Nó
NODE_TYPE_INTERNAL = 0x01
NODE_TYPE_LEAF = 0x02

PAGE_HEADER_SIZE = 13 # bytes
SLOT_SIZE = 4 # 2 bytes para offset, 2 bytes para tamanho

# --- Funções do Cabeçalho ---

def get_node_type(page_data):
    """Lê o byte 0: Tipo de Nó (Folha ou Interno)."""
    return page_data[0]

def get_num_slots(page_data):
    """Lê os bytes 1-2: Número de slots na página."""
    return struct.unpack('<H', page_data[1:3])[0] 

def set_num_slots(page_data, num):
    """Escreve nos bytes 1-2: Número de slots na página."""
    page_data[1:3] = struct.pack('<H', num)

def get_free_space_pointer(page_data):
    """Lê os bytes 3-4: Onde o 'heap' de dados começa."""
    return struct.unpack('<H', page_data[3:5])[0]

def set_free_space_pointer(page_data, offset):
    """Atualiza os bytes 3-4: Onde o 'heap' de dados começa."""
    page_data[3:5] = struct.pack('<H', offset)

def get_parent_page_id(page_data):
    """Lê os bytes 5-8: ID da página Pai."""
    return struct.unpack('<L', page_data[5:9])[0] # L = 4 bytes

def set_parent_page_id(page_data, page_id):
    """Escreve nos bytes 5-8: ID da página Pai."""
    page_data[5:9] = struct.pack('<L', page_id)

def get_next_sibling_id(page_data):
    """(APENAS NÓS FOLHA) Lê os bytes 9-12: ID da próxima página folha."""
    return struct.unpack('<L', page_data[9:13])[0]

def set_next_sibling_id(page_data, page_id):
    """(APENAS NÓS FOLHA) Escreve nos bytes 9-12: ID da próxima página folha."""
    page_data[9:13] = struct.pack('<L', page_id)

def get_left_most_child_id(page_data):
    """(APENAS NÓS INTERNOS) Lê os bytes 9-12: ID do filho mais à esquerda."""
    return struct.unpack('<L', page_data[9:13])[0]

def set_left_most_child_id(page_data, page_id):
    """(APENAS NÓS INTERNOS) Escreve nos bytes 9-12: ID do filho mais à esquerda."""
    page_data[9:13] = struct.pack('<L', page_id)

# --- Funções de Manipulação de Slots ---

def get_slot(page_data, slot_id):
    """
    Lê um slot (offset e tamanho) do Diretório de Slots.
    """
    slot_start = PAGE_HEADER_SIZE + (slot_id * SLOT_SIZE)
    slot_end = slot_start + SLOT_SIZE
    (offset, size) = struct.unpack('<HH', page_data[slot_start:slot_end])
    return offset, size

def set_slot(page_data, slot_id, offset, size):
    """
    Escreve um slot (offset e tamanho) no Diretório de Slots.
    """
    slot_start = PAGE_HEADER_SIZE + (slot_id * SLOT_SIZE)
    page_data[slot_start : slot_start + 4] = struct.pack('<HH', offset, size)


# --- Funções de Leitura/Escrita de Dados (Chave/Valor) ---

def read_data_from_slot(page_data, slot_id):
    """
    Lê a chave e o valor reais apontados por um slot.
    """
    offset, size = get_slot(page_data, slot_id)
    
    if offset == 0 or size == 0:
        raise Exception(f"Slot {slot_id} inválido (offset/size nulos).")

    data_bytes = page_data[offset : offset + size]
    
    if len(data_bytes) < 4: 
        raise Exception(f"Corrupção de dados: Slot {slot_id} aponta para bloco de dados com tamanho {len(data_bytes)}")

    key_size = struct.unpack('<H', data_bytes[0:2])[0]
    key_start = 2
    key_end = key_start + key_size
    
    if key_end > size:
        raise Exception(f"Corrupção de dados: Tamanho da chave ({key_size}) excede o tamanho do bloco ({size}).")
        
    key = data_bytes[key_start:key_end]
    
    value_size_start = key_end
    value_size_end = value_size_start + 2
    
    if value_size_end > size:
         raise Exception(f"Corrupção de dados: Bloco de dados terminou antes de ler o tamanho do valor.")

    value_size = struct.unpack('<H', data_bytes[value_size_start:value_size_end])[0]
    
    value_start = value_size_end
    value_end = value_start + value_size
    
    if value_end > size:
         raise Exception(f"Corrupção de dados: Tamanho do valor ({value_size}) excede o tamanho do bloco ({size}).")

    value = data_bytes[value_start:value_end]
    
    return key, value

def write_data_to_heap(page_data, key_bytes, value_bytes):
    """
    (VERSÃO CORRIGIDA) Escreve um novo bloco (chave/valor) no 'heap' de dados.
    """
    key_size = len(key_bytes)
    value_size = len(value_bytes)
    total_size = 2 + key_size + 2 + value_size
    
    free_offset = get_free_space_pointer(page_data)
    new_offset = free_offset - total_size
    
    current_num_slots = get_num_slots(page_data)
    slot_directory_end = PAGE_HEADER_SIZE + ((current_num_slots + 1) * SLOT_SIZE)
    
    if new_offset < slot_directory_end:
         raise Exception(f"Página cheia (heap colidiu com slots em {new_offset} vs {slot_directory_end})")

    pos = new_offset
    struct.pack_into('<H', page_data, pos, key_size)
    pos += 2
    page_data[pos : pos + key_size] = key_bytes
    pos += key_size
    struct.pack_into('<H', page_data, pos, value_size)
    pos += 2
    page_data[pos : pos + value_size] = value_bytes
    
    set_free_space_pointer(page_data, new_offset)
    
    return new_offset, total_size