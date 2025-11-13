# gui.py (Atualizado com MarcoDB)

import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import os

from pager import Pager
from btree import BPlusTree

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- MUDANÇA 1: Título Principal ---
        self.title("MarcoDB Explorer")
        self.geometry("400x250")

        self.pager = None
        self.tree = None

        # --- Widgets ---
        
        frame_file = tk.Frame(self)
        frame_file.pack(pady=10)

        self.btn_open = tk.Button(frame_file, text="Abrir/Criar Banco", command=self.open_database)
        self.btn_open.pack()

        frame_ops = tk.Frame(self)
        frame_ops.pack(pady=5, padx=20, fill="x")

        lbl_key = tk.Label(frame_ops, text="Chave (Key):")
        lbl_key.pack()
        self.entry_key = tk.Entry(frame_ops, width=50)
        self.entry_key.pack()

        lbl_value = tk.Label(frame_ops, text="Valor (Value):")
        lbl_value.pack()
        self.entry_value = tk.Entry(frame_ops, width=50)
        self.entry_value.pack()

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        self.btn_insert = tk.Button(frame_buttons, text="Inserir (Set)", command=self.on_insert, state="disabled")
        self.btn_insert.pack(side="left", padx=5)
        
        self.btn_search = tk.Button(frame_buttons, text="Buscar (Get)", command=self.on_search, state="disabled")
        self.btn_search.pack(side="left", padx=5)
        
        self.btn_delete = tk.Button(frame_buttons, text="Deletar", command=self.on_delete, state="disabled", fg="red")
        self.btn_delete.pack(side="left", padx=5)

        # --- MUDANÇA 2: Texto da Barra de Status ---
        self.lbl_status = tk.Label(self, text="Abra ou crie um banco MarcoDB (.db)", relief="sunken", anchor="w")
        self.lbl_status.pack(side="bottom", fill="x")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_database(self):
        # --- MUDANÇA 3: Nome do Arquivo Padrão ---
        filename = simpledialog.askstring("Abrir Banco", "Digite o nome do arquivo .db:",
                                          initialvalue="MarcoDB.db")
        if not filename:
            return

        try:
            if self.pager:
                self.pager.close()

            self.pager = Pager(filename)
            self.tree = BPlusTree(self.pager)
            
            self.lbl_status.config(text=f"Banco '{filename}' aberto com sucesso.")
            self.btn_insert.config(state="normal")
            self.btn_search.config(state="normal")
            self.btn_delete.config(state="normal")
            # --- MUDANÇA 4: Título da Janela Ativa ---
            self.title(f"MarcoDB Explorer - [{filename}]")

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o banco: {e}")

    def on_insert(self):
        key = self.entry_key.get()
        value = self.entry_value.get()

        if not key or not value:
            messagebox.showwarning("Entrada Inválida", "Chave e Valor não podem estar vazios.")
            return

        try:
            self.tree.insert(key, value)
            self.lbl_status.config(text=f"Inserido: ('{key}', '{value}')")
            self.entry_key.delete(0, "end")
            self.entry_value.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Erro de Inserção", f"Não foi possível inserir: {e}")

    def on_search(self):
        key = self.entry_key.get()
        if not key:
            messagebox.showwarning("Entrada Inválida", "A Chave não pode estar vazia.")
            return
        
        self.entry_value.delete(0, "end")

        try:
            value = self.tree.search(key)
            if value is not None:
                self.entry_value.insert(0, value)
                self.lbl_status.config(text=f"Encontrado: ('{key}', '{value}')")
            else:
                self.lbl_status.config(text=f"Chave '{key}' não encontrada.")
                messagebox.showinfo("Busca", f"Chave '{key}' não foi encontrada.")
        except Exception as e:
            messagebox.showerror("Erro de Busca", f"Ocorreu um erro ao buscar: {e}")

    def on_delete(self):
        key = self.entry_key.get()
        if not key:
            messagebox.showwarning("Entrada Inválida", "A Chave para deletar não pode estar vazia.")
            return

        if not messagebox.askyesno("Confirmar Deleção", f"Tem certeza que quer deletar a chave '{key}'?"):
            return

        try:
            self.tree.delete(key) 
            self.lbl_status.config(text=f"Chave '{key}' deletada com sucesso.")
            self.entry_key.delete(0, "end")
            self.entry_value.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Erro de Deleção", f"Não foi possível deletar: {e}")

    def on_close(self):
        if self.pager:
            print("INFO: Fechando e salvando o MarcoDB...")
            self.pager.close()
        self.destroy()

def main():
        app = App()
        app.mainloop()

if __name__ == "__main__":
        main()