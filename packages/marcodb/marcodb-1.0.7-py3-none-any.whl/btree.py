# BPlusTree.py (Versão Completa, Final e Corrigida)

import serialization as srl
from pager import Pager
import sys
from serialization import NODE_TYPE_INTERNAL, NODE_TYPE_LEAF 

# --- Constantes ---
PAGE_SIZE = 4096 
MIN_SLOTS_THRESHOLD = 1 

class BPlusTree:
    def __init__(self, pager):
        self.pager = pager
        
        meta_page = self.pager.get_page(0)
        self.root_page_id = int.from_bytes(meta_page[0:4], 'little')

        if self.root_page_id == 0:
            print("INFO: Criando novo banco de dados...")
            root_page_id, root_page_data = self.pager.new_page()
            self.root_page_id = root_page_id 

            root_page_data[0] = NODE_TYPE_LEAF
            srl.set_num_slots(root_page_data, 0)
            srl.set_free_space_pointer(root_page_data, PAGE_SIZE)
            
            srl.set_parent_page_id(root_page_data, 0)
            srl.set_next_sibling_id(root_page_data, 0) 
            
            meta_page[0:4] = self.root_page_id.to_bytes(4, 'little')
            
            self.pager.mark_dirty(0) 
            self.pager.mark_dirty(self.root_page_id)
        else:
            print(f"INFO: Abrindo banco de dados existente. Raiz na página {self.root_page_id}")


    # --- FUNÇÃO DE BUSCA (search) ---
    def search(self, key):
        key_bytes = key.encode('utf-8') 
        value_bytes = self._search_recursive(self.root_page_id, key_bytes)
        
        if value_bytes:
            return value_bytes.decode('utf-8')
        else:
            return None

    def _search_recursive(self, page_id, key_bytes):
        page = self.pager.get_page(page_id)
        node_type = srl.get_node_type(page) 

        if node_type == NODE_TYPE_LEAF:
            return self._search_in_leaf_node(page, key_bytes)
        elif node_type == NODE_TYPE_INTERNAL:
            next_page_id = self._search_in_internal_node(page, key_bytes)
            if next_page_id == 0: 
                return None
            return self._search_recursive(next_page_id, key_bytes)
        else:
            raise Exception(f"Tipo de página desconhecido: {node_type}")

    def _search_in_leaf_node(self, page_data, key_bytes_to_find):
        num_slots = srl.get_num_slots(page_data)
        
        for slot_id in range(num_slots):
            key, value = srl.read_data_from_slot(page_data, slot_id)
            if key == key_bytes_to_find:
                return value
        return None 
    
    def _search_in_internal_node(self, page_data, key_bytes_to_find):
        num_slots = srl.get_num_slots(page_data)
        next_page_id = srl.get_left_most_child_id(page_data)
        
        for slot_id in range(num_slots):
            key, value_bytes = srl.read_data_from_slot(page_data, slot_id)
            child_page_id = int.from_bytes(value_bytes, 'little')
            
            if key_bytes_to_find >= key:
                next_page_id = child_page_id
            else:
                break
                
        return next_page_id
    
    def _get_page_real_data_size(self, page_data):
        """Calcula o tamanho REAL dos dados somando os slots."""
        total_size = 0
        num_slots = srl.get_num_slots(page_data)
        for i in range(num_slots):
            _offset, size = srl.get_slot(page_data, i)
            total_size += size
        
        total_size += (num_slots * srl.SLOT_SIZE) + srl.PAGE_HEADER_SIZE
        return total_size

    # --- FUNÇÕES DE INSERÇÃO (insert) ---
    
    def insert(self, key, value):
        key_bytes = key.encode('utf-8')
        value_bytes = value.encode('utf-8')
        
        try:
            self._insert_recursive(self.root_page_id, key_bytes, value_bytes)
        except Exception as e:
            print(f"ERRO ao inserir ('{key}', '{value}'): {e}")

    def _insert_recursive(self, page_id, key_bytes, value_bytes):
        page = self.pager.get_page(page_id)
        node_type = srl.get_node_type(page)

        if node_type == NODE_TYPE_LEAF:
            self._insert_into_leaf(page_id, page, key_bytes, value_bytes)
        else: 
            child_page_id = self._search_in_internal_node(page, key_bytes)
            self._insert_recursive(child_page_id, key_bytes, value_bytes)
            
    def _insert_into_leaf(self, page_id, page_data, key_bytes, value_bytes):
        key_size = len(key_bytes)
        value_size = len(value_bytes)
        data_block_size = 2 + key_size + 2 + value_size 
        
        num_slots = srl.get_num_slots(page_data)
        slot_size = srl.SLOT_SIZE
        
        free_space_pointer = srl.get_free_space_pointer(page_data)
        slot_directory_end = srl.PAGE_HEADER_SIZE + ((num_slots + 1) * slot_size)
        
        available_space = free_space_pointer - slot_directory_end
        
        if (data_block_size) > available_space: 
            self._split_leaf_node(page_id, page_data, key_bytes, value_bytes)
        else:
            self._insert_data_into_page(page_id, page_data, key_bytes, value_bytes, data_block_size)

    def _insert_data_into_page(self, page_id, page_data, key_bytes, value_bytes, data_block_size):
        num_slots = srl.get_num_slots(page_data)
        insertion_point = 0
        for i in range(num_slots):
            key, _ = srl.read_data_from_slot(page_data, i)
            if key == key_bytes:
                raise Exception(f"Chave '{key_bytes.decode()}' já existe.")
            if key > key_bytes:
                break
            insertion_point = i + 1
            
        new_offset, total_size = srl.write_data_to_heap(page_data, key_bytes, value_bytes)
        
        slot_dir_start = srl.PAGE_HEADER_SIZE
        slot_to_insert_at = slot_dir_start + (insertion_point * srl.SLOT_SIZE)
        end_of_slots = slot_dir_start + (num_slots * srl.SLOT_SIZE)
        
        page_data[slot_to_insert_at + srl.SLOT_SIZE : end_of_slots + srl.SLOT_SIZE] = \
            page_data[slot_to_insert_at : end_of_slots]

        srl.set_slot(page_data, insertion_point, new_offset, total_size)
        srl.set_num_slots(page_data, num_slots + 1)
        self.pager.mark_dirty(page_id)

    # --- FUNÇÕES DE SPLIT (Dividir) ---

    def _create_new_root(self, left_child_id, right_child_id, median_key):
        new_root_id, new_root_data = self.pager.new_page()
        print(f"INFO: Criando nova raiz na página {new_root_id}")

        new_root_data[0] = NODE_TYPE_INTERNAL
        srl.set_num_slots(new_root_data, 1) 
        srl.set_free_space_pointer(new_root_data, PAGE_SIZE)
        srl.set_parent_page_id(new_root_data, 0) 

        srl.set_left_most_child_id(new_root_data, left_child_id)
        
        child_id_bytes = right_child_id.to_bytes(4, 'little')
        
        offset, size = srl.write_data_to_heap(new_root_data, median_key, child_id_bytes)
        srl.set_slot(new_root_data, 0, offset, size)
        
        left_page = self.pager.get_page(left_child_id)
        srl.set_parent_page_id(left_page, new_root_id)
        
        right_page = self.pager.get_page(right_child_id)
        srl.set_parent_page_id(right_page, new_root_id)

        self.root_page_id = new_root_id
        meta_page = self.pager.get_page(0)
        meta_page[0:4] = self.root_page_id.to_bytes(4, 'little')
        
        self.pager.mark_dirty(0)
        self.pager.mark_dirty(self.root_page_id)
        self.pager.mark_dirty(left_child_id)
        self.pager.mark_dirty(right_child_id)

    def _split_leaf_node(self, old_page_id, old_page_data, key_to_insert, value_to_insert):
        all_data = []
        num_slots = srl.get_num_slots(old_page_data)
        
        for i in range(num_slots):
            all_data.append(srl.read_data_from_slot(old_page_data, i))
        all_data.append((key_to_insert, value_to_insert))
        all_data.sort(key=lambda item: item[0])
        
        new_page_id, new_page_data = self.pager.new_page()
        
        new_page_data[0] = NODE_TYPE_LEAF
        srl.set_num_slots(new_page_data, 0)
        srl.set_free_space_pointer(new_page_data, PAGE_SIZE)
        
        parent_page_id = srl.get_parent_page_id(old_page_data)
        srl.set_parent_page_id(new_page_data, parent_page_id)
        
        old_sibling_id = srl.get_next_sibling_id(old_page_data)
        srl.set_next_sibling_id(new_page_data, old_sibling_id)
        srl.set_next_sibling_id(old_page_data, new_page_id)

        srl.set_num_slots(old_page_data, 0)
        srl.set_free_space_pointer(old_page_data, PAGE_SIZE)
        
        split_point = len(all_data) // 2
        median_key = all_data[split_point][0] 
        
        for i in range(0, split_point):
            key, value = all_data[i]
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(old_page_id, old_page_data, key, value, data_size)
            
        for i in range(split_point, len(all_data)):
            key, value = all_data[i]
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(new_page_id, new_page_data, key, value, data_size)

        if parent_page_id == 0:
            self._create_new_root(old_page_id, new_page_id, median_key)
        else:
            self._insert_into_parent(parent_page_id, old_page_id, median_key, new_page_id)
            
        self.pager.mark_dirty(old_page_id)
        self.pager.mark_dirty(new_page_id)

    def _insert_into_internal_node(self, page_id, page_data, key_bytes, child_id):
        num_slots = srl.get_num_slots(page_data)
        value_bytes = child_id.to_bytes(4, 'little')
        
        insertion_point = 0
        for i in range(num_slots):
            key, _ = srl.read_data_from_slot(page_data, i)
            if key == key_bytes:
                raise Exception(f"Chave duplicada '{key_bytes.decode()}' no nó interno {page_id}")
            if key > key_bytes:
                break
            insertion_point = i + 1
            
        new_offset, total_size = srl.write_data_to_heap(page_data, key_bytes, value_bytes)
        
        slot_dir_start = srl.PAGE_HEADER_SIZE
        slot_to_insert_at = slot_dir_start + (insertion_point * srl.SLOT_SIZE)
        end_of_slots = slot_dir_start + (num_slots * srl.SLOT_SIZE)
        
        page_data[slot_to_insert_at + srl.SLOT_SIZE : end_of_slots + srl.SLOT_SIZE] = \
            page_data[slot_to_insert_at : end_of_slots]

        srl.set_slot(page_data, insertion_point, new_offset, total_size)
        srl.set_num_slots(page_data, num_slots + 1)
        self.pager.mark_dirty(page_id)

    def _insert_into_parent(self, parent_page_id, left_child_id, median_key, right_child_id):
        parent_page = self.pager.get_page(parent_page_id)
        
        key_size = len(median_key)
        value_size = 4 
        data_block_size = 2 + key_size + 2 + value_size
        slot_size = srl.SLOT_SIZE
        
        num_slots = srl.get_num_slots(parent_page)
        free_space_pointer = srl.get_free_space_pointer(parent_page)
        slot_directory_end = srl.PAGE_HEADER_SIZE + ((num_slots + 1) * slot_size)
        
        available_space = free_space_pointer - slot_directory_end
        
        if (data_block_size) <= available_space:
            self._insert_into_internal_node(parent_page_id, parent_page, median_key, right_child_id)
            right_child_page = self.pager.get_page(right_child_id)
            srl.set_parent_page_id(right_child_page, parent_page_id)
            self.pager.mark_dirty(right_child_id)
        else:
            self._split_internal_node(parent_page_id, parent_page, median_key, right_child_id)

    def _split_internal_node(self, old_page_id, old_page_data, key_to_insert, child_id_to_insert):
        all_pointers = []
        num_slots = srl.get_num_slots(old_page_data)
        
        for i in range(num_slots):
            key, value_bytes = srl.read_data_from_slot(old_page_data, i)
            child_id = int.from_bytes(value_bytes, 'little')
            all_pointers.append((key, child_id))
            
        all_pointers.append((key_to_insert, child_id_to_insert))
        all_pointers.sort(key=lambda item: item[0])

        new_page_id, new_page_data = self.pager.new_page()
        print(f"INFO: Nó Interno {old_page_id} cheio. Dividindo.")
        print(f"INFO: Página interna nova (irmã) criada em {new_page_id}")
        
        new_page_data[0] = NODE_TYPE_INTERNAL
        srl.set_num_slots(new_page_data, 0)
        srl.set_free_space_pointer(new_page_data, PAGE_SIZE)
        
        parent_page_id = srl.get_parent_page_id(old_page_data)
        srl.set_parent_page_id(new_page_data, parent_page_id)
        
        split_point = len(all_pointers) // 2
        
        median_key_promoted, median_child_id = all_pointers[split_point]
        
        left_pointers = all_pointers[:split_point]
        right_pointers = all_pointers[split_point + 1:] 
        
        srl.set_num_slots(old_page_data, 0)
        srl.set_free_space_pointer(old_page_data, PAGE_SIZE)
        
        for key, child_id in left_pointers:
            self._insert_into_internal_node(old_page_id, old_page_data, key, child_id)
            
        srl.set_left_most_child_id(new_page_data, median_child_id)
        
        for key, child_id in right_pointers:
            self._insert_into_internal_node(new_page_id, new_page_data, key, child_id)

        child_page = self.pager.get_page(median_child_id)
        srl.set_parent_page_id(child_page, new_page_id)
        self.pager.mark_dirty(median_child_id)
        
        for _, child_id in right_pointers:
            child_page = self.pager.get_page(child_id)
            srl.set_parent_page_id(child_page, new_page_id)
            self.pager.mark_dirty(child_id)

        if parent_page_id == 0:
            self._create_new_root(old_page_id, new_page_id, median_key_promoted)
        else:
            self._insert_into_parent(parent_page_id, old_page_id, median_key_promoted, new_page_id)
            
        self.pager.mark_dirty(old_page_id)
        self.pager.mark_dirty(new_page_id)

    # --- FUNÇÕES DE DELEÇÃO (delete) ---
    
    def delete(self, key):
        key_bytes = key.encode('utf-8')
        try:
            self._delete_recursive(self.root_page_id, key_bytes)
        except Exception as e:
            print(f"ERRO ao deletar ('{key}'): {e}")


    def _delete_recursive(self, page_id, key_bytes_to_delete):
        page = self.pager.get_page(page_id)
        node_type = srl.get_node_type(page)

        if node_type == NODE_TYPE_LEAF:
            return self._delete_from_leaf(page_id, page, key_bytes_to_delete)
        else: 
            child_page_id = self._search_in_internal_node(page, key_bytes_to_delete)
            if child_page_id == 0:
                 raise Exception(f"Chave '{key_bytes_to_delete.decode()}' não encontrada (ponteiro nulo).")
            self._delete_recursive(child_page_id, key_bytes_to_delete)
            
    def _delete_from_leaf(self, page_id, page_data, key_bytes_to_delete):
        num_slots = srl.get_num_slots(page_data)
        slot_to_delete = -1

        # Coleta dados para reescrever (CORREÇÃO PARA O BUG DO LIXO)
        all_data = []
        found = False
        for i in range(num_slots):
            key, value = srl.read_data_from_slot(page_data, i)
            if key == key_bytes_to_delete:
                slot_to_delete = i
                found = True
            else:
                all_data.append((key, value))
        
        if not found:
            raise Exception(f"Chave '{key_bytes_to_delete.decode()}' não encontrada para deletar.")

        # RECONSTRÓI a página para limpar o lixo
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        
        for key, value in all_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(page_id, page_data, key, value, data_size)
            
        self.pager.mark_dirty(page_id)
        
        # Pega o novo número de slots (depois de reconstruir)
        num_slots = srl.get_num_slots(page_data)
        
        if self.root_page_id == page_id:
             return 

        if num_slots < MIN_SLOTS_THRESHOLD:
            # print(f"INFO: Página {page_id} em UNDERFLOW. Corrigindo...")
            self._handle_leaf_underflow(page_id, page_data)
        
    def _find_sibling_info(self, parent_page_data, child_page_id):
        """
        Retorna: (left_sib_id, right_sib_id, 
                  index_of_key_LEFT_of_child, index_of_key_RIGHT_of_child)
        """
        num_slots = srl.get_num_slots(parent_page_data)
        left_most_child_id = srl.get_left_most_child_id(parent_page_data)
        
        if child_page_id == left_most_child_id:
            if num_slots == 0: 
                return (None, None, None, None)
            _key, right_sib_id_bytes = srl.read_data_from_slot(parent_page_data, 0)
            right_sib_id = int.from_bytes(right_sib_id_bytes, 'little')
            return (None, right_sib_id, None, 0)

        for i in range(num_slots):
            key_i, child_id_i_bytes = srl.read_data_from_slot(parent_page_data, i)
            child_id_i = int.from_bytes(child_id_i_bytes, 'little')
            
            if child_id_i == child_page_id:
                if i == 0:
                    left_sib_id = left_most_child_id
                else:
                    _key_left, left_sib_id_bytes = srl.read_data_from_slot(parent_page_data, i - 1)
                    left_sib_id = int.from_bytes(left_sib_id_bytes, 'little')

                right_sib_id = None
                index_right = None
                if i + 1 < num_slots:
                    _key_right, right_sib_id_bytes = srl.read_data_from_slot(parent_page_data, i + 1)
                    right_sib_id = int.from_bytes(right_sib_id_bytes, 'little')
                    index_right = i + 1
                    
                return (left_sib_id, right_sib_id, i, index_right) 

        raise Exception(f"Lógica de encontrar irmão falhou: filho {child_page_id} não encontrado no pai {srl.get_num_slots(parent_page_data)}.")

    def _handle_leaf_underflow(self, page_id, page_data):
        parent_page_id = srl.get_parent_page_id(page_data)
        if parent_page_id == 0: return

        parent_page_data = self.pager.get_page(parent_page_id)
        
        (left_sib_id, right_sib_id, 
         key_idx_left, key_idx_right) = self._find_sibling_info(parent_page_data, page_id)
        
        # 1. Tentar pegar do irmão da DIREITA
        if right_sib_id is not None:
            right_sib_data = self.pager.get_page(right_sib_id)
            if srl.get_num_slots(right_sib_data) > MIN_SLOTS_THRESHOLD:
                self._borrow_from_right_leaf(page_id, page_data, 
                                             right_sib_id, right_sib_data,
                                             parent_page_id, parent_page_data, 
                                             key_idx_right)
                return 

        # 2. Tentar pegar do irmão da ESQUERDA
        if left_sib_id is not None:
            left_sib_data = self.pager.get_page(left_sib_id)
            if srl.get_num_slots(left_sib_data) > MIN_SLOTS_THRESHOLD:
                self._borrow_from_left_leaf(page_id, page_data, 
                                            left_sib_id, left_sib_data,
                                            parent_page_id, parent_page_data, 
                                            key_idx_left)
                return
        
        # 3. Se não puder emprestar, TENTA FUNDIR (Merge)
        if right_sib_id is not None:
            right_sib_data = self.pager.get_page(right_sib_id)
            # CORREÇÃO: Não precisamos mais checar o tamanho, pois ambas as páginas estão
            # com o mínimo de slots (1), então elas *sempre* caberão.
            self._merge_leaf_nodes(page_id, page_data, 
                                   right_sib_id, right_sib_data, 
                                   parent_page_id, parent_page_data, 
                                   key_idx_right)
            return 
        
        if left_sib_id is not None:
             left_sib_data = self.pager.get_page(left_sib_id)
             self._merge_leaf_nodes(left_sib_id, left_sib_data,
                                    page_id, page_data, 
                                    parent_page_id, parent_page_data, 
                                    key_idx_left)
             return

    def _borrow_from_right_leaf(self, page_id, page_data, 
                                right_sib_id, right_sib_data,
                                parent_page_id, parent_page_data, 
                                parent_key_index_RIGHT):
        
        # (CORREÇÃO: Reconstruir páginas para evitar corrupção de heap)
        
        my_data = []
        for i in range(srl.get_num_slots(page_data)):
            my_data.append(srl.read_data_from_slot(page_data, i))
            
        right_data = []
        for i in range(srl.get_num_slots(right_sib_data)):
            right_data.append(srl.read_data_from_slot(right_sib_data, i))
            
        borrowed_item = right_data.pop(0)
        my_data.append(borrowed_item)
        
        new_separator_key = right_data[0][0]
        
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        srl.set_num_slots(right_sib_data, 0)
        srl.set_free_space_pointer(right_sib_data, PAGE_SIZE)

        for key, value in my_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(page_id, page_data, key, value, data_size)
            
        for key, value in right_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(right_sib_id, right_sib_data, key, value, data_size)

        old_key, old_child_id_bytes = srl.read_data_from_slot(parent_page_data, parent_key_index_RIGHT)
        old_child_id = int.from_bytes(old_child_id_bytes, 'little') 

        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, old_key, skip_underflow_check=True)
        self._insert_into_internal_node(parent_page_id, parent_page_data, new_separator_key, old_child_id)

        self.pager.mark_dirty(page_id)
        self.pager.mark_dirty(right_sib_id)
        self.pager.mark_dirty(parent_page_id)

    def _borrow_from_left_leaf(self, page_id, page_data, 
                               left_sib_id, left_sib_data,
                               parent_page_id, parent_page_data, 
                               parent_key_index_LEFT):
        
        my_data = []
        for i in range(srl.get_num_slots(page_data)):
            my_data.append(srl.read_data_from_slot(page_data, i))
            
        left_data = []
        for i in range(srl.get_num_slots(left_sib_data)):
            left_data.append(srl.read_data_from_slot(left_sib_data, i))
            
        borrowed_item = left_data.pop()
        my_data.insert(0, borrowed_item)
        
        new_separator_key = borrowed_item[0]
        
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        srl.set_num_slots(left_sib_data, 0)
        srl.set_free_space_pointer(left_sib_data, PAGE_SIZE)
        
        for key, value in my_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(page_id, page_data, key, value, data_size)
            
        for key, value in left_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(left_sib_id, left_sib_data, key, value, data_size)
        
        old_key, old_child_id_bytes = srl.read_data_from_slot(parent_page_data, parent_key_index_LEFT)
        old_child_id = int.from_bytes(old_child_id_bytes, 'little')

        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, old_key, skip_underflow_check=True)
        self._insert_into_internal_node(parent_page_id, parent_page_data, new_separator_key, old_child_id)

        self.pager.mark_dirty(page_id)
        self.pager.mark_dirty(left_sib_id)
        self.pager.mark_dirty(parent_page_id)


    def _merge_leaf_nodes(self, page_id, page_data, 
                          right_sib_id, right_sib_data, 
                          parent_page_id, parent_page_data, 
                          parent_key_index): 

        print(f"INFO: Fundindo (Merge) página {right_sib_id} -> {page_id}")
        
        all_data = []
        for i in range(srl.get_num_slots(page_data)):
            all_data.append(srl.read_data_from_slot(page_data, i))
        
        for i in range(srl.get_num_slots(right_sib_data)):
            all_data.append(srl.read_data_from_slot(right_sib_data, i))
            
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        
        for key, value in all_data:
            data_size = 2 + len(key) + 2 + len(value)
            self._insert_data_into_page(page_id, page_data, key, value, data_size)

        new_sibling_id = srl.get_next_sibling_id(right_sib_data)
        srl.set_next_sibling_id(page_data, new_sibling_id)
        
        key_to_delete, _ = srl.read_data_from_slot(parent_page_data, parent_key_index)
        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, key_to_delete)
        
        self.pager.mark_dirty(page_id)
        
    def _delete_entry_from_internal_node(self, page_id, page_data, key_to_delete, skip_underflow_check=False):
        num_slots = srl.get_num_slots(page_data)
        slot_to_delete = -1

        for i in range(num_slots):
            key, _ = srl.read_data_from_slot(page_data, i)
            if key == key_to_delete:
                slot_to_delete = i
                break
        
        if slot_to_delete == -1:
            raise Exception(f"Chave '{key_to_delete.decode()}' não encontrada no pai {page_id} para deletar.")
        
        # (CORREÇÃO: Reconstruir o nó interno para limpar o lixo)
        all_pointers = []
        
        left_most_child_id = srl.get_left_most_child_id(page_data)
        all_pointers.append((None, left_most_child_id)) # Adiciona o ponteiro da esquerda
        
        for i in range(num_slots):
            key, val_bytes = srl.read_data_from_slot(page_data, i)
            if key != key_to_delete:
                all_pointers.append((key, int.from_bytes(val_bytes, 'little')))
        
        # Limpa a página
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        
        # Reinsere os dados
        new_left_most = all_pointers.pop(0)[1]
        srl.set_left_most_child_id(page_data, new_left_most)
        
        for key, child_id in all_pointers:
            self._insert_into_internal_node(page_id, page_data, key, child_id)
            
        self.pager.mark_dirty(page_id)
        
        # Pega o novo número de slots
        num_slots = srl.get_num_slots(page_data)
        
        # print(f"INFO: Chave '{key_to_delete.decode()}' deletada do nó pai {page_id}")

        if skip_underflow_check:
            return

        if page_id == self.root_page_id:
            if num_slots == 0 and srl.get_node_type(page_data) == NODE_TYPE_INTERNAL:
                self._shrink_root(page_data)
            return

        if num_slots < MIN_SLOTS_THRESHOLD:
            # print(f"INFO: Nó Interno {page_id} em UNDERFLOW. Corrigindo...")
            self._handle_internal_underflow(page_id, page_data)

    def _handle_internal_underflow(self, page_id, page_data):
        parent_page_id = srl.get_parent_page_id(page_data)
        if parent_page_id == 0: return

        parent_page_data = self.pager.get_page(parent_page_id)
        
        (left_sib_id, right_sib_id, 
         key_idx_left, key_idx_right) = self._find_sibling_info(parent_page_data, page_id)
        
        if right_sib_id is not None:
            right_sib_data = self.pager.get_page(right_sib_id)
            if srl.get_num_slots(right_sib_data) > MIN_SLOTS_THRESHOLD:
                self._borrow_from_right_internal(page_id, page_data,
                                                 right_sib_id, right_sib_data,
                                                 parent_page_id, parent_page_data,
                                                 key_idx_right)
                return 

        if left_sib_id is not None:
            left_sib_data = self.pager.get_page(left_sib_id)
            if srl.get_num_slots(left_sib_data) > MIN_SLOTS_THRESHOLD:
                self._borrow_from_left_internal(page_id, page_data,
                                                left_sib_id, left_sib_data,
                                                parent_page_id, parent_page_data,
                                                key_idx_left)
                return
        
        if right_sib_id is not None:
            right_sib_data = self.pager.get_page(right_sib_id)
            self._merge_internal_nodes(page_id, page_data, 
                                       right_sib_id, right_sib_data, 
                                       parent_page_id, parent_page_data, 
                                       key_idx_right) 
            return 
                
        if left_sib_id is not None:
             left_sib_data = self.pager.get_page(left_sib_id)
             self._merge_internal_nodes(left_sib_id, left_sib_data,
                                        page_id, page_data,
                                        parent_page_id, parent_page_data,
                                        key_idx_left)
             return

    def _borrow_from_right_internal(self, page_id, page_data,
                                    right_sib_id, right_sib_data,
                                    parent_page_id, parent_page_data,
                                    parent_key_index_RIGHT): 
        
        # (CORREÇÃO: Reconstruir páginas para evitar corrupção de heap)
        
        # 1. Coleta dados
        my_pointers = [] # (key, child_id)
        my_pointers.append((None, srl.get_left_most_child_id(page_data)))
        for i in range(srl.get_num_slots(page_data)):
            key, val_bytes = srl.read_data_from_slot(page_data, i)
            my_pointers.append((key, int.from_bytes(val_bytes, 'little')))

        right_pointers = []
        right_pointers.append((None, srl.get_left_most_child_id(right_sib_data)))
        for i in range(srl.get_num_slots(right_sib_data)):
            key, val_bytes = srl.read_data_from_slot(right_sib_data, i)
            right_pointers.append((key, int.from_bytes(val_bytes, 'little')))
            
        # Pega a chave de separação do pai
        separator_key, separator_child_bytes = srl.read_data_from_slot(parent_page_data, parent_key_index_RIGHT)
        separator_child_id = int.from_bytes(separator_child_bytes, 'little')
        
        # 2. Move os dados
        borrowed_child = right_pointers.pop(0)[1] # Pega o left_most_child da direita
        my_pointers.append((separator_key, borrowed_child))
        
        new_separator_key = right_pointers[0][0] # A nova primeira chave da direita
        
        # 3. Limpa AMBAS as páginas
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        srl.set_num_slots(right_sib_data, 0)
        srl.set_free_space_pointer(right_sib_data, PAGE_SIZE)
        
        # 4. Reinsere os dados
        srl.set_left_most_child_id(page_data, my_pointers.pop(0)[1])
        for key, child_id in my_pointers:
            self._insert_into_internal_node(page_id, page_data, key, child_id)
            
        srl.set_left_most_child_id(right_sib_data, right_pointers.pop(0)[1])
        for key, child_id in right_pointers:
            self._insert_into_internal_node(right_sib_id, right_sib_data, key, child_id)

        # 5. Atualiza o pai
        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, separator_key, skip_underflow_check=True)
        self._insert_into_internal_node(parent_page_id, parent_page_data, new_separator_key, separator_child_id)
        
        self.pager.mark_dirty(page_id)
        self.pager.mark_dirty(right_sib_id)
        self.pager.mark_dirty(parent_page_id)
        
    def _borrow_from_left_internal(self, page_id, page_data,
                                   left_sib_id, left_sib_data,
                                   parent_page_id, parent_page_data,
                                   parent_key_index_LEFT):
        
        # (CORREÇÃO: Reconstruir páginas para evitar corrupção de heap)
        
        # 1. Coleta dados
        my_pointers = []
        my_pointers.append((None, srl.get_left_most_child_id(page_data)))
        for i in range(srl.get_num_slots(page_data)):
            key, val_bytes = srl.read_data_from_slot(page_data, i)
            my_pointers.append((key, int.from_bytes(val_bytes, 'little')))

        left_pointers = []
        left_pointers.append((None, srl.get_left_most_child_id(left_sib_data)))
        for i in range(srl.get_num_slots(left_sib_data)):
            key, val_bytes = srl.read_data_from_slot(left_sib_data, i)
            left_pointers.append((key, int.from_bytes(val_bytes, 'little')))
            
        separator_key, separator_child_bytes = srl.read_data_from_slot(parent_page_data, parent_key_index_LEFT)
        separator_child_id = int.from_bytes(separator_child_bytes, 'little')
        
        # 2. Move os dados
        borrowed_item = left_pointers.pop() # Pega o último item da esquerda
        borrowed_key, borrowed_child_id = borrowed_item
        
        # A chave de separação antiga do pai desce para a nossa página
        my_pointers.insert(0, (separator_key, my_pointers.pop(0)[1])) # Mantém o left_most
        srl.set_left_most_child_id(page_data, borrowed_child_id)
        
        new_separator_key = borrowed_key
        
        # 3. Limpa AMBAS as páginas
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        srl.set_num_slots(left_sib_data, 0)
        srl.set_free_space_pointer(left_sib_data, PAGE_SIZE)
        
        # 4. Reinsere os dados
        srl.set_left_most_child_id(page_data, my_pointers.pop(0)[1])
        for key, child_id in my_pointers:
            self._insert_into_internal_node(page_id, page_data, key, child_id)
            
        srl.set_left_most_child_id(left_sib_data, left_pointers.pop(0)[1])
        for key, child_id in left_pointers:
            self._insert_into_internal_node(left_sib_id, left_sib_data, key, child_id)

        # 5. Atualiza o pai
        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, separator_key, skip_underflow_check=True)
        self._insert_into_internal_node(parent_page_id, parent_page_data, new_separator_key, separator_child_id)

        self.pager.mark_dirty(page_id)
        self.pager.mark_dirty(left_sib_id)
        self.pager.mark_dirty(parent_page_id)


    def _merge_internal_nodes(self, page_id, page_data, 
                              right_sib_id, right_sib_data, 
                              parent_page_id, parent_page_data, 
                              parent_key_index_RIGHT): 

        print(f"INFO: Fundindo (Merge) Nó Interno {right_sib_id} -> {page_id}")
        
        key_to_pull_down, _ = srl.read_data_from_slot(parent_page_data, parent_key_index_RIGHT)

        # 1. Coleta dados
        all_data = [] # (key, child_id)
        
        all_data.append((None, srl.get_left_most_child_id(page_data)))
        for i in range(srl.get_num_slots(page_data)):
            key, val_bytes = srl.read_data_from_slot(page_data, i)
            all_data.append((key, int.from_bytes(val_bytes, 'little')))
            
        all_data.append((key_to_pull_down, srl.get_left_most_child_id(right_sib_data)))

        for i in range(srl.get_num_slots(right_sib_data)):
            key, val_bytes = srl.read_data_from_slot(right_sib_data, i)
            all_data.append((key, int.from_bytes(val_bytes, 'little')))

        # 2. Limpa a página da esquerda (page_id)
        srl.set_num_slots(page_data, 0)
        srl.set_free_space_pointer(page_data, PAGE_SIZE)
        
        # 3. Reinsere os dados
        new_left_most = all_data.pop(0)[1]
        srl.set_left_most_child_id(page_data, new_left_most)

        for key, child_id in all_data:
            self._insert_into_internal_node(page_id, page_data, key, child_id)
            child_page = self.pager.get_page(child_id)
            srl.set_parent_page_id(child_page, page_id)
            self.pager.mark_dirty(child_id)

        # 4. Deleta a chave do pai
        self._delete_entry_from_internal_node(parent_page_id, parent_page_data, key_to_pull_down)
        
        self.pager.mark_dirty(page_id)
        
    def _shrink_root(self, root_page_data):
        if srl.get_node_type(root_page_data) == NODE_TYPE_LEAF:
            return 
        
        if srl.get_num_slots(root_page_data) == 0:
            new_root_id = srl.get_left_most_child_id(root_page_data)
            old_root_id = self.root_page_id
            
            print(f"INFO: Raiz {old_root_id} vazia. Encolhendo. Nova raiz é {new_root_id}.")
            
            meta_page = self.pager.get_page(0)
            meta_page[0:4] = new_root_id.to_bytes(4, 'little')
            self.pager.mark_dirty(0)
            
            new_root_page = self.pager.get_page(new_root_id)
            srl.set_parent_page_id(new_root_page, 0)
            self.pager.mark_dirty(new_root_id)

            self.root_page_id = new_root_id