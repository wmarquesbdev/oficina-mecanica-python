"""
app.py - Interface grafica (Tkinter) do Sistema Oficina.
Login -> Menu principal (cards) -> CRUDs.
Rode 'python database.py' uma vez antes para criar o banco, ou rode este arquivo direto.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import database as db

# Paleta de cores
COR_FUNDO = "#f0f2f5"
COR_HEADER = "#1e3a5f"
COR_CARD = "#ffffff"
COR_BOTAO = "#2563eb"
COR_BOTAO_TXT = "#ffffff"
COR_PERIGO = "#dc2626"


# ===================== CRUD CLIENTES =====================
class TelaClientes(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Clientes")
        self.geometry("760x500")
        self.configure(bg=COR_FUNDO)
        self.id_sel = None

        tk.Label(self, text="Cadastro de Clientes", font=("Arial", 16, "bold"),
                 bg=COR_FUNDO, fg=COR_HEADER).pack(pady=10)

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=20)

        self.e_nome = self._campo(form, "Nome", 0)
        self.e_cpf = self._campo(form, "CPF", 1)
        self.e_tel = self._campo(form, "Telefone", 2)
        self.e_email = self._campo(form, "E-mail", 3)

        botoes = tk.Frame(self, bg=COR_FUNDO)
        botoes.pack(pady=10)
        self._btn(botoes, "Salvar", self.salvar, COR_BOTAO)
        self._btn(botoes, "Limpar", self.limpar, "#6b7280")
        self._btn(botoes, "Excluir", self.excluir, COR_PERIGO)

        cols = ("id", "nome", "cpf", "telefone", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, larg in zip(cols, (40, 200, 130, 130, 200)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=larg)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)

        self.carregar()

    def _campo(self, parent, label, row):
        tk.Label(parent, text=label, bg=COR_FUNDO, anchor="w", width=10).grid(
            row=row, column=0, sticky="w", pady=4)
        e = tk.Entry(parent, width=50)
        e.grid(row=row, column=1, sticky="w", pady=4)
        return e

    def _btn(self, parent, txt, cmd, cor):
        tk.Button(parent, text=txt, command=cmd, bg=cor, fg="white",
                  font=("Arial", 10, "bold"), width=12, relief="flat",
                  cursor="hand2").pack(side="left", padx=5)

    def carregar(self):
        self.tree.delete(*self.tree.get_children())
        for c in db.listar_clientes():
            self.tree.insert("", "end",
                             values=(c["id"], c["nome"], c["cpf"], c["telefone"], c["email"]))

    def selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.id_sel = v[0]
        self.limpar(manter_id=True)
        self.e_nome.insert(0, v[1]); self.e_cpf.insert(0, v[2])
        self.e_tel.insert(0, v[3]); self.e_email.insert(0, v[4])

    def salvar(self):
        nome = self.e_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atencao", "O nome e obrigatorio.")
            return
        dados = (nome, self.e_cpf.get().strip(), self.e_tel.get().strip(),
                 self.e_email.get().strip())
        if self.id_sel:
            db.atualizar_cliente(self.id_sel, *dados)
        else:
            db.inserir_cliente(*dados)
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atencao", "Selecione um cliente.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o cliente selecionado?"):
            try:
                db.excluir_cliente(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Nao foi possivel excluir",
                                     "Este cliente possui veiculos ou ordens de servico vinculados.")
                return
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        for e in (self.e_nome, self.e_cpf, self.e_tel, self.e_email):
            e.delete(0, "end")


# ===================== CRUD CARROS =====================
class TelaCarros(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Carros")
        self.geometry("820x520")
        self.configure(bg=COR_FUNDO)
        self.id_sel = None
        self.clientes = db.listar_clientes()

        tk.Label(self, text="Cadastro de Carros", font=("Arial", 16, "bold"),
                 bg=COR_FUNDO, fg=COR_HEADER).pack(pady=10)

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=20)

        tk.Label(form, text="Cliente", bg=COR_FUNDO, width=10, anchor="w").grid(
            row=0, column=0, sticky="w", pady=4)
        self.cb_cliente = ttk.Combobox(form, width=47, state="readonly",
                                        values=[f"{c['id']} - {c['nome']}" for c in self.clientes])
        self.cb_cliente.grid(row=0, column=1, sticky="w", pady=4)

        self.e_placa = self._campo(form, "Placa", 1)
        self.e_marca = self._campo(form, "Marca", 2)
        self.e_modelo = self._campo(form, "Modelo", 3)
        self.e_ano = self._campo(form, "Ano", 4)
        self.e_cor = self._campo(form, "Cor", 5)

        botoes = tk.Frame(self, bg=COR_FUNDO)
        botoes.pack(pady=10)
        self._btn(botoes, "Salvar", self.salvar, COR_BOTAO)
        self._btn(botoes, "Limpar", self.limpar, "#6b7280")
        self._btn(botoes, "Excluir", self.excluir, COR_PERIGO)

        cols = ("id", "cliente", "placa", "marca", "modelo", "ano", "cor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=9)
        for c, larg in zip(cols, (40, 160, 90, 100, 120, 60, 90)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=larg)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)

        self.carregar()

    def _campo(self, parent, label, row):
        tk.Label(parent, text=label, bg=COR_FUNDO, width=10, anchor="w").grid(
            row=row, column=0, sticky="w", pady=4)
        e = tk.Entry(parent, width=50)
        e.grid(row=row, column=1, sticky="w", pady=4)
        return e

    def _btn(self, parent, txt, cmd, cor):
        tk.Button(parent, text=txt, command=cmd, bg=cor, fg="white",
                  font=("Arial", 10, "bold"), width=12, relief="flat",
                  cursor="hand2").pack(side="left", padx=5)

    def _cliente_id_combo(self):
        if not self.cb_cliente.get():
            return None
        return int(self.cb_cliente.get().split(" - ")[0])

    def carregar(self):
        self.tree.delete(*self.tree.get_children())
        for c in db.listar_carros():
            self.tree.insert("", "end", values=(c["id"], c["cliente"], c["placa"],
                                                 c["marca"], c["modelo"], c["ano"], c["cor"]))

    def selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.id_sel = v[0]
        self.limpar(manter_id=True)
        # localiza o carro completo para pegar cliente_id
        for carro in db.listar_carros():
            if carro["id"] == v[0]:
                for c in self.clientes:
                    if c["id"] == carro["cliente_id"]:
                        self.cb_cliente.set(f"{c['id']} - {c['nome']}")
                break
        self.e_placa.insert(0, v[2]); self.e_marca.insert(0, v[3])
        self.e_modelo.insert(0, v[4]); self.e_ano.insert(0, v[5]); self.e_cor.insert(0, v[6])

    def salvar(self):
        cid = self._cliente_id_combo()
        placa = self.e_placa.get().strip()
        if not cid or not placa:
            messagebox.showwarning("Atencao", "Cliente e placa sao obrigatorios.")
            return
        ano = self.e_ano.get().strip()
        ano = int(ano) if ano.isdigit() else None
        dados = (cid, placa, self.e_marca.get().strip(), self.e_modelo.get().strip(),
                 ano, self.e_cor.get().strip())
        if self.id_sel:
            db.atualizar_carro(self.id_sel, *dados)
        else:
            db.inserir_carro(*dados)
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atencao", "Selecione um carro.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o carro selecionado?"):
            try:
                db.excluir_carro(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Nao foi possivel excluir",
                                     "Este carro possui ordens de servico vinculadas.")
                return
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        self.cb_cliente.set("")
        for e in (self.e_placa, self.e_marca, self.e_modelo, self.e_ano, self.e_cor):
            e.delete(0, "end")


# ===================== CRUD SERVICOS =====================
class TelaServicos(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Servicos")
        self.geometry("620x480")
        self.configure(bg=COR_FUNDO)
        self.id_sel = None

        tk.Label(self, text="Cadastro de Servicos", font=("Arial", 16, "bold"),
                 bg=COR_FUNDO, fg=COR_HEADER).pack(pady=10)

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=20)
        tk.Label(form, text="Descricao", bg=COR_FUNDO, width=10, anchor="w").grid(
            row=0, column=0, sticky="w", pady=4)
        self.e_desc = tk.Entry(form, width=45)
        self.e_desc.grid(row=0, column=1, sticky="w", pady=4)
        tk.Label(form, text="Preco (R$)", bg=COR_FUNDO, width=10, anchor="w").grid(
            row=1, column=0, sticky="w", pady=4)
        self.e_preco = tk.Entry(form, width=20)
        self.e_preco.grid(row=1, column=1, sticky="w", pady=4)

        botoes = tk.Frame(self, bg=COR_FUNDO)
        botoes.pack(pady=10)
        for txt, cmd, cor in (("Salvar", self.salvar, COR_BOTAO),
                              ("Limpar", self.limpar, "#6b7280"),
                              ("Excluir", self.excluir, COR_PERIGO)):
            tk.Button(botoes, text=txt, command=cmd, bg=cor, fg="white",
                      font=("Arial", 10, "bold"), width=12, relief="flat",
                      cursor="hand2").pack(side="left", padx=5)

        cols = ("id", "descricao", "preco")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=11)
        for c, larg in zip(cols, (40, 360, 120)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=larg)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)
        self.carregar()

    def carregar(self):
        self.tree.delete(*self.tree.get_children())
        for s in db.listar_servicos():
            self.tree.insert("", "end",
                             values=(s["id"], s["descricao"], f"R$ {s['preco']:.2f}"))

    def selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.id_sel = v[0]
        self.limpar(manter_id=True)
        self.e_desc.insert(0, v[1])
        self.e_preco.insert(0, str(v[2]).replace("R$ ", ""))

    def salvar(self):
        desc = self.e_desc.get().strip()
        try:
            preco = float(self.e_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atencao", "Preco invalido.")
            return
        if not desc:
            messagebox.showwarning("Atencao", "A descricao e obrigatoria.")
            return
        if self.id_sel:
            db.atualizar_servico(self.id_sel, desc, preco)
        else:
            db.inserir_servico(desc, preco)
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atencao", "Selecione um servico.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o servico selecionado?"):
            try:
                db.excluir_servico(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Nao foi possivel excluir",
                                     "Este servico esta sendo usado em ordens de servico.")
                return
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        self.e_desc.delete(0, "end")
        self.e_preco.delete(0, "end")


# ===================== CRUD ORDENS DE SERVICO =====================
class TelaOrdens(tk.Toplevel):
    STATUS = ["Aberta", "Em andamento", "Concluida", "Cancelada"]

    def __init__(self, master):
        super().__init__(master)
        self.title("Ordens de Servico")
        self.geometry("960x680")
        self.configure(bg=COR_FUNDO)
        self.id_sel = None
        self.itens = []          # itens da OS em edicao
        self.clientes = db.listar_clientes()
        self.servicos = db.listar_servicos()

        tk.Label(self, text="Ordens de Servico", font=("Arial", 16, "bold"),
                 bg=COR_FUNDO, fg=COR_HEADER).pack(pady=8)

        # --- dados da OS ---
        topo = tk.Frame(self, bg=COR_FUNDO)
        topo.pack(fill="x", padx=20)
        tk.Label(topo, text="Cliente", bg=COR_FUNDO, width=8, anchor="w").grid(row=0, column=0, sticky="w")
        self.cb_cliente = ttk.Combobox(topo, width=32, state="readonly",
                                       values=[f"{c['id']} - {c['nome']}" for c in self.clientes])
        self.cb_cliente.grid(row=0, column=1, padx=(0, 20), pady=4)
        self.cb_cliente.bind("<<ComboboxSelected>>", self.atualizar_carros)
        tk.Label(topo, text="Carro", bg=COR_FUNDO, width=6, anchor="w").grid(row=0, column=2, sticky="w")
        self.cb_carro = ttk.Combobox(topo, width=28, state="readonly", values=[])
        self.cb_carro.grid(row=0, column=3, pady=4)

        tk.Label(topo, text="Status", bg=COR_FUNDO, width=8, anchor="w").grid(row=1, column=0, sticky="w")
        self.cb_status = ttk.Combobox(topo, width=32, state="readonly", values=self.STATUS)
        self.cb_status.set("Aberta")
        self.cb_status.grid(row=1, column=1, padx=(0, 20), pady=4)
        tk.Label(topo, text="Obs.", bg=COR_FUNDO, width=6, anchor="w").grid(row=1, column=2, sticky="w")
        self.e_obs = tk.Entry(topo, width=31)
        self.e_obs.grid(row=1, column=3, pady=4)

        # --- adicionar itens ---
        add = tk.Frame(self, bg=COR_FUNDO)
        add.pack(fill="x", padx=20, pady=(10, 0))
        tk.Label(add, text="Servico", bg=COR_FUNDO, width=8, anchor="w").grid(row=0, column=0, sticky="w")
        self.cb_servico = ttk.Combobox(add, width=32, state="readonly",
                                       values=[f"{s['id']} - {s['descricao']} (R$ {s['preco']:.2f})"
                                               for s in self.servicos])
        self.cb_servico.grid(row=0, column=1, padx=(0, 10))
        tk.Label(add, text="Qtd", bg=COR_FUNDO).grid(row=0, column=2)
        self.e_qtd = tk.Entry(add, width=5)
        self.e_qtd.insert(0, "1")
        self.e_qtd.grid(row=0, column=3, padx=(0, 10))
        tk.Button(add, text="+ Adicionar item", command=self.adicionar_item, bg="#16a34a",
                  fg="white", font=("Arial", 10, "bold"), relief="flat",
                  cursor="hand2").grid(row=0, column=4)

        # --- treeview itens ---
        cols_i = ("descricao", "qtd", "preco", "subtotal")
        self.tree_itens = ttk.Treeview(self, columns=cols_i, show="headings", height=5)
        for c, larg in zip(cols_i, (380, 60, 120, 120)):
            self.tree_itens.heading(c, text=c.capitalize())
            self.tree_itens.column(c, width=larg)
        self.tree_itens.pack(fill="x", padx=20, pady=8)

        rodape = tk.Frame(self, bg=COR_FUNDO)
        rodape.pack(fill="x", padx=20)
        tk.Button(rodape, text="Remover item", command=self.remover_item, bg=COR_PERIGO,
                  fg="white", font=("Arial", 9, "bold"), relief="flat",
                  cursor="hand2").pack(side="left")
        self.lbl_total = tk.Label(rodape, text="Total: R$ 0,00", font=("Arial", 13, "bold"),
                                  bg=COR_FUNDO, fg=COR_HEADER)
        self.lbl_total.pack(side="right")

        botoes = tk.Frame(self, bg=COR_FUNDO)
        botoes.pack(pady=10)
        for txt, cmd, cor in (("Salvar OS", self.salvar, COR_BOTAO),
                              ("Limpar", self.limpar, "#6b7280"),
                              ("Excluir OS", self.excluir, COR_PERIGO)):
            tk.Button(botoes, text=txt, command=cmd, bg=cor, fg="white",
                      font=("Arial", 10, "bold"), width=14, relief="flat",
                      cursor="hand2").pack(side="left", padx=5)

        # --- treeview de OS existentes ---
        tk.Label(self, text="Ordens cadastradas (clique para editar)", bg=COR_FUNDO,
                 fg="#374151").pack(anchor="w", padx=20)
        cols_o = ("id", "cliente", "placa", "data", "status", "total")
        self.tree_os = ttk.Treeview(self, columns=cols_o, show="headings", height=6)
        for c, larg in zip(cols_o, (40, 160, 90, 130, 110, 110)):
            self.tree_os.heading(c, text=c.capitalize())
            self.tree_os.column(c, width=larg)
        self.tree_os.pack(fill="both", expand=True, padx=20, pady=(4, 12))
        self.tree_os.bind("<<TreeviewSelect>>", self.selecionar_os)

        self.carregar_os()

    # ---- helpers ----
    def atualizar_carros(self, _=None):
        cid = self._id_combo(self.cb_cliente)
        carros = db.listar_carros_por_cliente(cid) if cid else []
        self.cb_carro["values"] = [f"{c['id']} - {c['placa']} ({c['modelo']})" for c in carros]
        self.cb_carro.set("")

    def _id_combo(self, combo):
        return int(combo.get().split(" - ")[0]) if combo.get() else None

    def adicionar_item(self):
        if not self.cb_servico.get():
            messagebox.showwarning("Atencao", "Selecione um servico.")
            return
        try:
            qtd = int(self.e_qtd.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atencao", "Quantidade invalida.")
            return
        sid = self._id_combo(self.cb_servico)
        serv = next(s for s in self.servicos if s["id"] == sid)
        self.itens.append({"servico_id": sid, "descricao": serv["descricao"],
                           "quantidade": qtd, "preco_unit": serv["preco"]})
        self.cb_servico.set("")
        self.e_qtd.delete(0, "end"); self.e_qtd.insert(0, "1")
        self._render_itens()

    def remover_item(self):
        sel = self.tree_itens.selection()
        if not sel:
            return
        idx = self.tree_itens.index(sel[0])
        del self.itens[idx]
        self._render_itens()

    def _render_itens(self):
        self.tree_itens.delete(*self.tree_itens.get_children())
        total = 0
        for it in self.itens:
            sub = it["quantidade"] * it["preco_unit"]
            total += sub
            self.tree_itens.insert("", "end", values=(
                it["descricao"], it["quantidade"],
                f"R$ {it['preco_unit']:.2f}", f"R$ {sub:.2f}"))
        self.lbl_total.config(text=f"Total: R$ {total:.2f}".replace(".", ","))

    def carregar_os(self):
        self.tree_os.delete(*self.tree_os.get_children())
        for o in db.listar_ordens():
            self.tree_os.insert("", "end", values=(
                o["id"], o["cliente"], o["placa"], o["data_abertura"], o["status"],
                f"R$ {o['total']:.2f}"))

    def selecionar_os(self, _=None):
        sel = self.tree_os.selection()
        if not sel:
            return
        oid = self.tree_os.item(sel[0])["values"][0]
        self.id_sel = oid
        ordem = next(o for o in db.listar_ordens() if o["id"] == oid)
        # cliente e carro
        for c in self.clientes:
            if c["id"] == ordem["cliente_id"]:
                self.cb_cliente.set(f"{c['id']} - {c['nome']}")
        self.atualizar_carros()
        for c in db.listar_carros_por_cliente(ordem["cliente_id"]):
            if c["id"] == ordem["carro_id"]:
                self.cb_carro.set(f"{c['id']} - {c['placa']} ({c['modelo']})")
        self.cb_status.set(ordem["status"])
        self.e_obs.delete(0, "end")
        self.e_obs.insert(0, ordem["observacoes"] or "")
        # itens
        self.itens = [{"servico_id": i["servico_id"], "descricao": i["descricao"],
                       "quantidade": i["quantidade"], "preco_unit": i["preco_unit"]}
                      for i in db.listar_itens_da_ordem(oid)]
        self._render_itens()

    def salvar(self):
        cid = self._id_combo(self.cb_cliente)
        carid = self._id_combo(self.cb_carro)
        if not cid or not carid:
            messagebox.showwarning("Atencao", "Selecione cliente e carro.")
            return
        if not self.itens:
            messagebox.showwarning("Atencao", "Adicione ao menos um servico.")
            return
        status = self.cb_status.get() or "Aberta"
        obs = self.e_obs.get().strip()
        if self.id_sel:
            db.atualizar_ordem(self.id_sel, cid, carid, status, obs, self.itens)
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            db.inserir_ordem(cid, carid, data, status, obs, self.itens)
        self.limpar()
        self.carregar_os()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atencao", "Selecione uma OS na lista.")
            return
        if messagebox.askyesno("Confirmar", "Excluir a OS selecionada?"):
            db.excluir_ordem(self.id_sel)
            self.limpar()
            self.carregar_os()

    def limpar(self, _=None):
        self.id_sel = None
        self.itens = []
        self.cb_cliente.set(""); self.cb_carro.set(""); self.cb_carro["values"] = []
        self.cb_status.set("Aberta"); self.cb_servico.set("")
        self.e_obs.delete(0, "end")
        self.e_qtd.delete(0, "end"); self.e_qtd.insert(0, "1")
        self._render_itens()


# ===================== MENU PRINCIPAL =====================
class MenuPrincipal:
    def __init__(self, root, usuario):
        self.root = root
        self.root.deiconify()
        self.root.title("Sistema Oficina - Menu Principal")
        self.root.geometry("680x460")
        self.root.configure(bg=COR_FUNDO)

        header = tk.Frame(self.root, bg=COR_HEADER, height=70)
        header.pack(fill="x")
        tk.Label(header, text="  Sistema Oficina Mecanica", bg=COR_HEADER, fg="white",
                 font=("Arial", 18, "bold")).pack(side="left", pady=18)
        tk.Label(header, text=f"Usuario: {usuario}  ", bg=COR_HEADER, fg="#cbd5e1",
                 font=("Arial", 10)).pack(side="right", pady=24)

        grade = tk.Frame(self.root, bg=COR_FUNDO)
        grade.pack(expand=True)

        cards = [
            ("\U0001F464", "Clientes", lambda: TelaClientes(self.root)),
            ("\U0001F697", "Carros", lambda: TelaCarros(self.root)),
            ("\U0001F527", "Servicos", lambda: TelaServicos(self.root)),
            ("\U0001F4CB", "Ordens de Servico", lambda: TelaOrdens(self.root)),
        ]
        for i, (icone, titulo, cmd) in enumerate(cards):
            self._card(grade, icone, titulo, cmd, i // 2, i % 2)

    def _card(self, parent, icone, titulo, cmd, lin, col):
        card = tk.Frame(parent, bg=COR_CARD, width=280, height=140,
                        highlightbackground="#d1d5db", highlightthickness=1)
        card.grid(row=lin, column=col, padx=20, pady=20)
        card.pack_propagate(False)
        tk.Label(card, text=icone, font=("Arial", 34), bg=COR_CARD).pack(pady=(20, 5))
        tk.Label(card, text=titulo, font=("Arial", 13, "bold"), bg=COR_CARD,
                 fg=COR_HEADER).pack()
        for w in (card, *card.winfo_children()):
            w.bind("<Button-1>", lambda e, c=cmd: c())
            w.configure(cursor="hand2")


# ===================== LOGIN =====================
class TelaLogin(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Login - Sistema Oficina")
        self.geometry("340x260")
        self.configure(bg="white")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", root.destroy)

        tk.Label(self, text="Sistema Oficina", font=("Arial", 16, "bold"),
                 bg="white", fg=COR_HEADER).pack(pady=(30, 5))
        tk.Label(self, text="Acesse com seu usuario", bg="white", fg="#6b7280").pack()

        f = tk.Frame(self, bg="white")
        f.pack(pady=20)
        tk.Label(f, text="Login", bg="white").grid(row=0, column=0, sticky="w")
        self.e_login = tk.Entry(f, width=28)
        self.e_login.grid(row=1, column=0, pady=(0, 10))
        tk.Label(f, text="Senha", bg="white").grid(row=2, column=0, sticky="w")
        self.e_senha = tk.Entry(f, width=28, show="*")
        self.e_senha.grid(row=3, column=0)
        self.e_senha.bind("<Return>", lambda e: self.entrar())

        tk.Button(self, text="Entrar", command=self.entrar, bg=COR_BOTAO, fg="white",
                  font=("Arial", 11, "bold"), width=22, relief="flat",
                  cursor="hand2").pack(pady=15)
        self.e_login.focus()

    def entrar(self):
        user = db.autenticar(self.e_login.get().strip(), self.e_senha.get().strip())
        if user:
            self.destroy()
            MenuPrincipal(self.root, user["nome"])
        else:
            messagebox.showerror("Erro", "Login ou senha invalidos.")


def main():
    db.criar_tabelas()
    db.seed()
    root = tk.Tk()
    root.withdraw()  # esconde a janela principal ate o login (padrao do material)
    TelaLogin(root)
    root.mainloop()


if __name__ == "__main__":
    main()
