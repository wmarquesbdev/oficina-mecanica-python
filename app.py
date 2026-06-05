import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import csv
import re
import database as db

FONTE = "Segoe UI"
COR_FUNDO = "#F1F5F9"
COR_CARD = "#FFFFFF"
COR_SIDEBAR = "#1E293B"
COR_SIDEBAR_HOVER = "#334155"
COR_HEADER = "#1E3A5F"
COR_PRIMARIA = "#2563EB"
COR_PRIMARIA_HOVER = "#1D4ED8"
COR_SUCESSO = "#16A34A"
COR_SUCESSO_HOVER = "#15803D"
COR_PERIGO = "#DC2626"
COR_PERIGO_HOVER = "#B91C1C"
COR_NEUTRO = "#64748B"
COR_NEUTRO_HOVER = "#475569"
COR_TEXTO = "#0F172A"
COR_BORDA = "#E2E8F0"
COR_STATUS = {"Aberta": "#2563EB", "Em andamento": "#D97706",
              "Concluida": "#16A34A", "Cancelada": "#DC2626"}

def botao(parent, texto, comando, cor, hover, **kw):
    b = tk.Button(parent, text=texto, command=comando, bg=cor, fg="white",
                  font=(FONTE, 10, "bold"), relief="flat", cursor="hand2",
                  activebackground=hover, activeforeground="white",
                  padx=14, pady=7, bd=0, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=cor))
    return b

def cabecalho(parent, titulo, subtitulo):
    tk.Label(parent, text=titulo, font=(FONTE, 19, "bold"),
             bg=COR_FUNDO, fg=COR_HEADER).pack(anchor="w", padx=24, pady=(18, 0))
    tk.Label(parent, text=subtitulo, font=(FONTE, 10),
             bg=COR_FUNDO, fg=COR_NEUTRO).pack(anchor="w", padx=24, pady=(0, 8))

def campo(parent, label, row, largura=46):
    tk.Label(parent, text=label, font=(FONTE, 10), bg=COR_FUNDO, fg=COR_TEXTO,
             anchor="w", width=10).grid(row=row, column=0, sticky="w", pady=4)
    e = tk.Entry(parent, width=largura, font=(FONTE, 10), relief="solid", bd=1)
    e.grid(row=row, column=1, sticky="w", pady=4, ipady=2)
    return e

def barra_busca(parent, callback):
    f = tk.Frame(parent, bg=COR_FUNDO)
    tk.Label(f, text="🔍", font=(FONTE, 11), bg=COR_FUNDO).pack(side="left")
    e = tk.Entry(f, width=34, font=(FONTE, 10), relief="solid", bd=1)
    e.pack(side="left", ipady=3, padx=(4, 0))
    e.bind("<KeyRelease>", lambda ev: callback(e.get()))
    return f, e

def aplicar_zebra(tree):
    tree.tag_configure("par", background="#FFFFFF")
    tree.tag_configure("impar", background="#F8FAFC")

def _rezebra(tree):
    for i, k in enumerate(tree.get_children("")):
        tags = [t for t in tree.item(k, "tags") if t not in ("par", "impar")]
        tree.item(k, tags=tags + ["par" if i % 2 == 0 else "impar"])

def _valor_ordenacao(texto):
    limpo = re.sub(r"[^\d,.-]", "", texto)
    if limpo and re.search(r"\d", texto):
        try:
            return float(limpo.replace(".", "").replace(",", "."))
        except ValueError:
            pass
    return texto.lower()

def ordenavel(tree):
    def sort(col, reverse):
        linhas = [(tree.set(k, col), k) for k in tree.get_children("")]
        linhas.sort(key=lambda t: _valor_ordenacao(t[0]), reverse=reverse)
        for idx, (_, k) in enumerate(linhas):
            tree.move(k, "", idx)
        _rezebra(tree)
        tree.heading(col, command=lambda: sort(col, not reverse))
    for col in tree["columns"]:
        atual = tree.heading(col)["text"]
        tree.heading(col, command=lambda c=col: sort(c, False))
        tree.heading(col, text=atual)

def exportar_csv(tree, nome_base, status_cb=None):
    itens = tree.get_children("")
    if not itens:
        messagebox.showinfo("Exportar CSV", "Não há registros para exportar.")
        return
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv", initialfile=f"{nome_base}.csv",
        filetypes=[("CSV", "*.csv")])
    if not caminho:
        return
    cols = list(tree["columns"])
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([tree.heading(c)["text"] for c in cols])
        for k in itens:
            w.writerow([tree.set(k, c) for c in cols])
    if status_cb:
        status_cb(f"{len(itens)} registro(s) exportado(s) para CSV.")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Oficina Mecanica")
        self.geometry("1060x680")
        self.minsize(960, 620)
        self.configure(bg=COR_FUNDO)
        self._estilo()
        db.criar_tabelas()
        db.seed()
        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill="both", expand=True)
        self.show_login()

    def _estilo(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Treeview", font=(FONTE, 10), rowheight=28,
                    background="white", fieldbackground="white", borderwidth=0)
        s.configure("Treeview.Heading", font=(FONTE, 10, "bold"),
                    background=COR_HEADER, foreground="white", relief="flat", padding=6)
        s.map("Treeview.Heading", background=[("active", COR_HEADER)])
        s.map("Treeview", background=[("selected", "#BFDBFE")],
              foreground=[("selected", COR_TEXTO)])

    def _limpar(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self._limpar()
        LoginView(self.container, self)

    def show_main(self, usuario):
        self._limpar()
        MainView(self.container, self, usuario)

class LoginView(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=COR_FUNDO)
        self.app = app
        self.pack(fill="both", expand=True)

        cartao = tk.Frame(self, bg="white", highlightbackground=COR_BORDA,
                          highlightthickness=1)
        cartao.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(cartao, text="🔧", font=(FONTE, 30), bg="white").pack(padx=46, pady=(30, 4))
        tk.Label(cartao, text="Sistema Oficina", font=(FONTE, 18, "bold"),
                 bg="white", fg=COR_HEADER).pack()
        tk.Label(cartao, text="Acesse com seu usuário", font=(FONTE, 10),
                 bg="white", fg=COR_NEUTRO).pack(pady=(2, 18))

        frm = tk.Frame(cartao, bg="white")
        frm.pack(padx=36)
        tk.Label(frm, text="Login", font=(FONTE, 9, "bold"), bg="white",
                 fg=COR_TEXTO, anchor="w").pack(anchor="w")
        self.e_login = tk.Entry(frm, width=26, font=(FONTE, 11), relief="solid", bd=1)
        self.e_login.pack(ipady=5, pady=(2, 12))
        tk.Label(frm, text="Senha", font=(FONTE, 9, "bold"), bg="white",
                 fg=COR_TEXTO, anchor="w").pack(anchor="w")
        self.e_senha = tk.Entry(frm, width=26, font=(FONTE, 11), show="•",
                                relief="solid", bd=1)
        self.e_senha.pack(ipady=5, pady=(2, 0))
        self.e_login.bind("<Return>", lambda e: self.e_senha.focus())
        self.e_senha.bind("<Return>", lambda e: self.entrar())

        botao(cartao, "Entrar", self.entrar, COR_PRIMARIA,
              COR_PRIMARIA_HOVER).pack(fill="x", padx=36, pady=(20, 30))
        self.e_login.focus()

    def entrar(self):
        u = db.autenticar(self.e_login.get().strip(), self.e_senha.get().strip())
        if u:
            self.app.show_main(u)
        else:
            messagebox.showerror("Erro", "Login ou senha inválidos.")

class MainView(tk.Frame):
    def __init__(self, master, app, usuario):
        super().__init__(master, bg=COR_FUNDO)
        self.app = app
        self.usuario = usuario
        self.ativo = None
        self.botoes_nav = {}
        self.pack(fill="both", expand=True)

        side = tk.Frame(self, bg=COR_SIDEBAR, width=215)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="🔧 Oficina", font=(FONTE, 15, "bold"),
                 bg=COR_SIDEBAR, fg="white").pack(anchor="w", padx=18, pady=(22, 0))
        tk.Label(side, text="Mecânica", font=(FONTE, 10),
                 bg=COR_SIDEBAR, fg="#94A3B8").pack(anchor="w", padx=18)
        tk.Frame(side, bg=COR_SIDEBAR_HOVER, height=1).pack(fill="x", pady=14, padx=12)

        for chave, rotulo in [("dashboard", "🏠   Início"), ("clientes", "👤   Clientes"),
                              ("carros", "🚗   Carros"), ("servicos", "🔧   Serviços"),
                              ("ordens", "📋   Ordens de Serviço"),
                              ("usuarios", "👥   Usuários")]:
            b = tk.Button(side, text=rotulo, anchor="w", font=(FONTE, 11),
                          bg=COR_SIDEBAR, fg="#E2E8F0", relief="flat", cursor="hand2",
                          activebackground=COR_SIDEBAR_HOVER, activeforeground="white",
                          bd=0, padx=18, pady=11,
                          command=lambda c=chave: self.navegar(c))
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, bb=b, c=chave:
                   bb.config(bg=COR_SIDEBAR_HOVER) if self.ativo != c else None)
            b.bind("<Leave>", lambda e, bb=b, c=chave:
                   bb.config(bg=COR_SIDEBAR) if self.ativo != c else None)
            self.botoes_nav[chave] = b

        tk.Button(side, text="🚪   Sair", anchor="w", font=(FONTE, 11), bg=COR_SIDEBAR,
                  fg="#FCA5A5", relief="flat", cursor="hand2", bd=0, padx=18, pady=11,
                  activebackground=COR_SIDEBAR_HOVER, activeforeground="#FCA5A5",
                  command=self.sair).pack(side="bottom", fill="x", pady=(0, 8))
        tk.Label(side, text=f"  Usuário: {usuario['nome']}", font=(FONTE, 9),
                 bg=COR_SIDEBAR, fg="#64748B").pack(side="bottom", anchor="w", pady=(0, 2))

        direita = tk.Frame(self, bg=COR_FUNDO)
        direita.pack(side="left", fill="both", expand=True)
        self.content = tk.Frame(direita, bg=COR_FUNDO)
        self.content.pack(fill="both", expand=True)
        self.status = tk.Label(direita, text="Pronto", anchor="w", font=(FONTE, 9),
                               bg=COR_BORDA, fg=COR_NEUTRO, padx=12, pady=4)
        self.status.pack(side="bottom", fill="x")

        self.navegar("dashboard")

    def navegar(self, chave):
        self.ativo = chave
        for c, b in self.botoes_nav.items():
            if c == chave:
                b.config(bg=COR_PRIMARIA, fg="white")
            else:
                b.config(bg=COR_SIDEBAR, fg="#E2E8F0")
        for w in self.content.winfo_children():
            w.destroy()
        {"dashboard": DashboardView, "clientes": ClientesView, "carros": CarrosView,
         "servicos": ServicosView, "ordens": OrdensView,
         "usuarios": UsuariosView}[chave](self.content, self)

    def set_status(self, msg):
        self.status.config(text=msg)
        self.after(4000, lambda: self.status.config(text="Pronto")
                   if self.status.winfo_exists() else None)

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja sair do sistema?"):
            self.app.show_login()

class DashboardView(tk.Frame):
    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.pack(fill="both", expand=True)
        d = db.resumo_dashboard()

        cabecalho(self, "Início", "Visão geral da oficina")

        grid = tk.Frame(self, bg=COR_FUNDO)
        grid.pack(anchor="w", padx=18, pady=14)
        cards = [("👤", "Clientes", d["clientes"], "#2563EB", "clientes"),
                 ("🚗", "Carros", d["carros"], "#7C3AED", "carros"),
                 ("🔧", "Serviços", d["servicos"], "#0891B2", "servicos"),
                 ("📋", "Ordens", d["ordens"], "#D97706", "ordens")]
        for i, (ic, t, v, cor, destino) in enumerate(cards):
            c = tk.Frame(grid, bg="white", width=184, height=148,
                         highlightbackground=COR_BORDA, highlightthickness=1, cursor="hand2")
            c.grid(row=0, column=i, padx=7)
            c.pack_propagate(False)
            l_ic = tk.Label(c, text=ic, font=(FONTE, 16), bg="white")
            l_ic.pack(anchor="w", padx=16, pady=(16, 0))
            l_v = tk.Label(c, text=str(v), font=(FONTE, 22, "bold"), bg="white", fg=cor)
            l_v.pack(anchor="w", padx=16, pady=(4, 0))
            l_t = tk.Label(c, text=t, font=(FONTE, 11), bg="white", fg=COR_NEUTRO)
            l_t.pack(anchor="w", padx=16, pady=(4, 0))
            widgets = (c, l_ic, l_v, l_t)
            for w in widgets:
                w.bind("<Button-1>", lambda e, dest=destino: self.ctrl.navegar(dest))
                w.bind("<Enter>", lambda e, cc=c: cc.config(highlightbackground=COR_PRIMARIA))
                w.bind("<Leave>", lambda e, cc=c: cc.config(highlightbackground=COR_BORDA))

        fat = tk.Frame(self, bg=COR_HEADER)
        fat.pack(fill="x", padx=24, pady=(2, 16))
        tk.Label(fat, text="💰  Faturamento (OS concluídas)", font=(FONTE, 11),
                 bg=COR_HEADER, fg="#CBD5E1").pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(fat, text=("R$ %.2f" % d["faturamento"]).replace(".", ","),
                 font=(FONTE, 24, "bold"), bg=COR_HEADER, fg="white").pack(
            anchor="w", padx=20, pady=(0, 14))

        st = tk.Frame(self, bg=COR_FUNDO)
        st.pack(anchor="w", padx=24)
        tk.Label(st, text="Ordens por status", font=(FONTE, 11, "bold"),
                 bg=COR_FUNDO, fg=COR_TEXTO).pack(anchor="w")
        linha = tk.Frame(st, bg=COR_FUNDO)
        linha.pack(anchor="w", pady=8)
        for s in ["Aberta", "Em andamento", "Concluida", "Cancelada"]:
            n = d["por_status"].get(s, 0)
            chip = tk.Frame(linha, bg="white", highlightbackground=COR_STATUS[s],
                            highlightthickness=2)
            chip.pack(side="left", padx=(0, 10))
            tk.Label(chip, text=f"{s}: {n}", font=(FONTE, 10, "bold"),
                     bg="white", fg=COR_STATUS[s], padx=12, pady=6).pack()

class ClientesView(tk.Frame):
    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.id_sel = None
        self.pack(fill="both", expand=True)

        cabecalho(self, "Clientes", "Cadastro e consulta de clientes")
        f_busca, self.e_busca = barra_busca(self, self.carregar)
        botao(f_busca, "Exportar CSV",
              lambda: exportar_csv(self.tree, "clientes", self.ctrl.set_status),
              COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=(12, 0))
        f_busca.pack(anchor="w", padx=24, pady=(0, 8))

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=24)
        self.e_nome = campo(form, "Nome", 0)
        self.e_cpf = campo(form, "CPF", 1)
        self.e_tel = campo(form, "Telefone", 2)
        self.e_email = campo(form, "E-mail", 3)

        bar = tk.Frame(self, bg=COR_FUNDO)
        bar.pack(anchor="w", padx=24, pady=10)
        botao(bar, "Salvar", self.salvar, COR_PRIMARIA, COR_PRIMARIA_HOVER).pack(side="left", padx=(0, 8))
        botao(bar, "Limpar", self.limpar, COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=8)
        botao(bar, "Excluir", self.excluir, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left", padx=8)

        cols = ("id", "nome", "cpf", "telefone", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, larg in zip(cols, (40, 220, 130, 130, 230)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=larg, anchor="w")
        self.tree.column("id", anchor="center")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("email", text="E-mail")
        aplicar_zebra(self.tree)
        ordenavel(self.tree)
        self.tree.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)
        self.carregar()

    def carregar(self, filtro=""):
        termo = filtro.lower().strip()
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(db.listar_clientes()):
            campos = [c["nome"], c["cpf"], c["telefone"], c["email"]]
            if termo and not any(termo in (x or "").lower() for x in campos):
                continue
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", tags=(tag,),
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
            messagebox.showwarning("Atenção", "O nome é obrigatório.")
            return
        email = self.e_email.get().strip()
        if email and not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            messagebox.showwarning("Atenção", "E-mail em formato inválido.")
            return
        dados = (nome, self.e_cpf.get().strip(), self.e_tel.get().strip(), email)
        if self.id_sel:
            db.atualizar_cliente(self.id_sel, *dados)
            self.ctrl.set_status(f"Cliente '{nome}' atualizado.")
        else:
            db.inserir_cliente(*dados)
            self.ctrl.set_status(f"Cliente '{nome}' cadastrado.")
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione um cliente na lista.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o cliente selecionado?"):
            try:
                db.excluir_cliente(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Não foi possível excluir",
                                     "Este cliente possui veículos ou ordens de serviço vinculados.")
                return
            self.ctrl.set_status("Cliente excluído.")
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        for e in (self.e_nome, self.e_cpf, self.e_tel, self.e_email):
            e.delete(0, "end")

class CarrosView(tk.Frame):
    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.id_sel = None
        self.clientes = db.listar_clientes()
        self.pack(fill="both", expand=True)

        cabecalho(self, "Carros", "Veículos vinculados aos clientes")
        f_busca, self.e_busca = barra_busca(self, self.carregar)
        botao(f_busca, "Exportar CSV",
              lambda: exportar_csv(self.tree, "carros", self.ctrl.set_status),
              COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=(12, 0))
        f_busca.pack(anchor="w", padx=24, pady=(0, 8))

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=24)
        tk.Label(form, text="Cliente", font=(FONTE, 10), bg=COR_FUNDO, fg=COR_TEXTO,
                 anchor="w", width=10).grid(row=0, column=0, sticky="w", pady=4)
        self.cb_cliente = ttk.Combobox(form, width=44, state="readonly",
                                       values=[f"{c['id']} - {c['nome']}" for c in self.clientes])
        self.cb_cliente.grid(row=0, column=1, sticky="w", pady=4)
        self.e_placa = campo(form, "Placa", 1)
        self.e_marca = campo(form, "Marca", 2)
        self.e_modelo = campo(form, "Modelo", 3)
        self.e_ano = campo(form, "Ano", 4)
        self.e_cor = campo(form, "Cor", 5)

        bar = tk.Frame(self, bg=COR_FUNDO)
        bar.pack(anchor="w", padx=24, pady=10)
        botao(bar, "Salvar", self.salvar, COR_PRIMARIA, COR_PRIMARIA_HOVER).pack(side="left", padx=(0, 8))
        botao(bar, "Limpar", self.limpar, COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=8)
        botao(bar, "Excluir", self.excluir, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left", padx=8)

        cols = ("id", "cliente", "placa", "marca", "modelo", "ano", "cor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, larg in zip(cols, (40, 170, 90, 110, 120, 60, 90)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=larg, anchor="w")
        self.tree.column("id", anchor="center")
        aplicar_zebra(self.tree)
        ordenavel(self.tree)
        self.tree.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)
        self.carregar()

    def _cliente_id(self):
        return int(self.cb_cliente.get().split(" - ")[0]) if self.cb_cliente.get() else None

    def carregar(self, filtro=""):
        termo = filtro.lower().strip()
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(db.listar_carros()):
            campos = [c["cliente"], c["placa"], c["marca"], c["modelo"]]
            if termo and not any(termo in (str(x) or "").lower() for x in campos):
                continue
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", tags=(tag,),
                             values=(c["id"], c["cliente"], c["placa"], c["marca"],
                                     c["modelo"], c["ano"], c["cor"]))

    def selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.id_sel = v[0]
        self.limpar(manter_id=True)
        for carro in db.listar_carros():
            if carro["id"] == v[0]:
                for c in self.clientes:
                    if c["id"] == carro["cliente_id"]:
                        self.cb_cliente.set(f"{c['id']} - {c['nome']}")
                break
        self.e_placa.insert(0, v[2]); self.e_marca.insert(0, v[3])
        self.e_modelo.insert(0, v[4]); self.e_ano.insert(0, v[5]); self.e_cor.insert(0, v[6])

    def salvar(self):
        cid = self._cliente_id()
        placa = self.e_placa.get().strip()
        if not cid or not placa:
            messagebox.showwarning("Atenção", "Cliente e placa são obrigatórios.")
            return
        ano = self.e_ano.get().strip()
        ano = int(ano) if ano.isdigit() else None
        dados = (cid, placa, self.e_marca.get().strip(), self.e_modelo.get().strip(),
                 ano, self.e_cor.get().strip())
        if self.id_sel:
            db.atualizar_carro(self.id_sel, *dados)
            self.ctrl.set_status(f"Carro {placa} atualizado.")
        else:
            db.inserir_carro(*dados)
            self.ctrl.set_status(f"Carro {placa} cadastrado.")
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione um carro na lista.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o carro selecionado?"):
            try:
                db.excluir_carro(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Não foi possível excluir",
                                     "Este carro possui ordens de serviço vinculadas.")
                return
            self.ctrl.set_status("Carro excluído.")
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        self.cb_cliente.set("")
        for e in (self.e_placa, self.e_marca, self.e_modelo, self.e_ano, self.e_cor):
            e.delete(0, "end")

class ServicosView(tk.Frame):
    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.id_sel = None
        self.pack(fill="both", expand=True)

        cabecalho(self, "Serviços", "Catálogo de serviços e preços")
        f_busca, self.e_busca = barra_busca(self, self.carregar)
        botao(f_busca, "Exportar CSV",
              lambda: exportar_csv(self.tree, "servicos", self.ctrl.set_status),
              COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=(12, 0))
        f_busca.pack(anchor="w", padx=24, pady=(0, 8))

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=24)
        self.e_desc = campo(form, "Descrição", 0)
        tk.Label(form, text="Preço (R$)", font=(FONTE, 10), bg=COR_FUNDO, fg=COR_TEXTO,
                 anchor="w", width=10).grid(row=1, column=0, sticky="w", pady=4)
        self.e_preco = tk.Entry(form, width=18, font=(FONTE, 10), relief="solid", bd=1)
        self.e_preco.grid(row=1, column=1, sticky="w", pady=4, ipady=2)

        bar = tk.Frame(self, bg=COR_FUNDO)
        bar.pack(anchor="w", padx=24, pady=10)
        botao(bar, "Salvar", self.salvar, COR_PRIMARIA, COR_PRIMARIA_HOVER).pack(side="left", padx=(0, 8))
        botao(bar, "Limpar", self.limpar, COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=8)
        botao(bar, "Excluir", self.excluir, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left", padx=8)

        cols = ("id", "descricao", "preco")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.heading("id", text="Id"); self.tree.column("id", width=40, anchor="center")
        self.tree.heading("descricao", text="Descrição"); self.tree.column("descricao", width=380, anchor="w")
        self.tree.heading("preco", text="Preço"); self.tree.column("preco", width=120, anchor="e")
        aplicar_zebra(self.tree)
        ordenavel(self.tree)
        self.tree.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)
        self.carregar()

    def carregar(self, filtro=""):
        termo = filtro.lower().strip()
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(db.listar_servicos()):
            if termo and termo not in (s["descricao"] or "").lower():
                continue
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", tags=(tag,),
                             values=(s["id"], s["descricao"], "R$ %.2f" % s["preco"]))

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
            messagebox.showwarning("Atenção", "Preço inválido.")
            return
        if not desc:
            messagebox.showwarning("Atenção", "A descrição é obrigatória.")
            return
        if self.id_sel:
            db.atualizar_servico(self.id_sel, desc, preco)
            self.ctrl.set_status(f"Serviço '{desc}' atualizado.")
        else:
            db.inserir_servico(desc, preco)
            self.ctrl.set_status(f"Serviço '{desc}' cadastrado.")
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione um serviço na lista.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o serviço selecionado?"):
            try:
                db.excluir_servico(self.id_sel)
            except sqlite3.IntegrityError:
                messagebox.showerror("Não foi possível excluir",
                                     "Este serviço está sendo usado em ordens de serviço.")
                return
            self.ctrl.set_status("Serviço excluído.")
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
        self.e_desc.delete(0, "end")
        self.e_preco.delete(0, "end")

class OrdensView(tk.Frame):
    STATUS = ["Aberta", "Em andamento", "Concluida", "Cancelada"]

    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.id_sel = None
        self.itens = []
        self.clientes = db.listar_clientes()
        self.servicos = db.listar_servicos()
        self.pack(fill="both", expand=True)

        cabecalho(self, "Ordens de Serviço", "Abertura e acompanhamento das OS")

        topo = tk.Frame(self, bg=COR_FUNDO)
        topo.pack(fill="x", padx=24)
        tk.Label(topo, text="Cliente", font=(FONTE, 10), bg=COR_FUNDO, width=7, anchor="w").grid(row=0, column=0, sticky="w")
        self.cb_cliente = ttk.Combobox(topo, width=30, state="readonly",
                                       values=[f"{c['id']} - {c['nome']}" for c in self.clientes])
        self.cb_cliente.grid(row=0, column=1, padx=(0, 18), pady=3)
        self.cb_cliente.bind("<<ComboboxSelected>>", self.atualizar_carros)
        tk.Label(topo, text="Carro", font=(FONTE, 10), bg=COR_FUNDO, width=5, anchor="w").grid(row=0, column=2, sticky="w")
        self.cb_carro = ttk.Combobox(topo, width=28, state="readonly", values=[])
        self.cb_carro.grid(row=0, column=3, pady=3)
        tk.Label(topo, text="Status", font=(FONTE, 10), bg=COR_FUNDO, width=7, anchor="w").grid(row=1, column=0, sticky="w")
        self.cb_status = ttk.Combobox(topo, width=30, state="readonly", values=self.STATUS)
        self.cb_status.set("Aberta")
        self.cb_status.grid(row=1, column=1, padx=(0, 18), pady=3)
        tk.Label(topo, text="Obs.", font=(FONTE, 10), bg=COR_FUNDO, width=5, anchor="w").grid(row=1, column=2, sticky="w")
        self.e_obs = tk.Entry(topo, width=30, font=(FONTE, 10), relief="solid", bd=1)
        self.e_obs.grid(row=1, column=3, pady=3, ipady=2)

        add = tk.Frame(self, bg=COR_FUNDO)
        add.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(add, text="Serviço", font=(FONTE, 10), bg=COR_FUNDO, width=7, anchor="w").grid(row=0, column=0, sticky="w")
        self.cb_servico = ttk.Combobox(add, width=34, state="readonly",
                                       values=[f"{s['id']} - {s['descricao']} (R$ {s['preco']:.2f})"
                                               for s in self.servicos])
        self.cb_servico.grid(row=0, column=1, padx=(0, 10))
        tk.Label(add, text="Qtd", font=(FONTE, 10), bg=COR_FUNDO).grid(row=0, column=2)
        self.e_qtd = tk.Entry(add, width=5, font=(FONTE, 10), relief="solid", bd=1)
        self.e_qtd.insert(0, "1")
        self.e_qtd.grid(row=0, column=3, padx=(4, 10))
        botao(add, "+ Adicionar item", self.adicionar_item, COR_SUCESSO, COR_SUCESSO_HOVER).grid(row=0, column=4)

        cols_i = ("descricao", "qtd", "preco", "subtotal")
        self.tree_itens = ttk.Treeview(self, columns=cols_i, show="headings", height=4)
        for c, larg, anc in [("descricao", 360, "w"), ("qtd", 60, "center"),
                             ("preco", 120, "e"), ("subtotal", 120, "e")]:
            self.tree_itens.heading(c, text=c.capitalize())
            self.tree_itens.column(c, width=larg, anchor=anc)
        self.tree_itens.heading("descricao", text="Descrição")
        self.tree_itens.heading("preco", text="Preço")
        self.tree_itens.pack(fill="x", padx=24, pady=8)

        rod = tk.Frame(self, bg=COR_FUNDO)
        rod.pack(fill="x", padx=24)
        botao(rod, "Remover item", self.remover_item, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left")
        self.lbl_total = tk.Label(rod, text="Total: R$ 0,00", font=(FONTE, 14, "bold"),
                                  bg=COR_FUNDO, fg=COR_HEADER)
        self.lbl_total.pack(side="right")

        bar = tk.Frame(self, bg=COR_FUNDO)
        bar.pack(anchor="w", padx=24, pady=8)
        botao(bar, "Salvar OS", self.salvar, COR_PRIMARIA, COR_PRIMARIA_HOVER).pack(side="left", padx=(0, 8))
        botao(bar, "Limpar", self.limpar, COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=8)
        botao(bar, "Excluir OS", self.excluir, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left", padx=8)
        botao(bar, "Ver resumo", self.ver_resumo, "#0891B2", "#0E7490").pack(side="left", padx=8)
        botao(bar, "Exportar .txt", self.exportar, "#475569", "#334155").pack(side="left", padx=8)

        flt = tk.Frame(self, bg=COR_FUNDO)
        flt.pack(fill="x", padx=24, pady=(4, 0))
        tk.Label(flt, text="Ordens cadastradas", font=(FONTE, 10, "bold"),
                 bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left")
        tk.Label(flt, text="Filtrar status:", font=(FONTE, 9), bg=COR_FUNDO,
                 fg=COR_NEUTRO).pack(side="left", padx=(16, 4))
        self.cb_filtro = ttk.Combobox(flt, width=16, state="readonly",
                                      values=["Todos"] + self.STATUS)
        self.cb_filtro.set("Todos")
        self.cb_filtro.pack(side="left")
        self.cb_filtro.bind("<<ComboboxSelected>>", lambda e: self.carregar_os())
        botao(flt, "Exportar CSV",
              lambda: exportar_csv(self.tree_os, "ordens_servico", self.ctrl.set_status),
              COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="right")

        cols_o = ("id", "cliente", "placa", "data", "status", "total")
        self.tree_os = ttk.Treeview(self, columns=cols_o, show="headings", height=6)
        for c, larg, anc in [("id", 40, "center"), ("cliente", 170, "w"), ("placa", 90, "w"),
                             ("data", 130, "w"), ("status", 120, "w"), ("total", 110, "e")]:
            self.tree_os.heading(c, text=c.capitalize())
            self.tree_os.column(c, width=larg, anchor=anc)
        for s, cor in COR_STATUS.items():
            self.tree_os.tag_configure(s, foreground=cor)
        ordenavel(self.tree_os)
        self.tree_os.pack(fill="both", expand=True, padx=24, pady=(4, 12))
        self.tree_os.bind("<<TreeviewSelect>>", self.selecionar_os)
        self.carregar_os()

    def atualizar_carros(self, _=None):
        cid = self._id(self.cb_cliente)
        carros = db.listar_carros_por_cliente(cid) if cid else []
        self.cb_carro["values"] = [f"{c['id']} - {c['placa']} ({c['modelo']})" for c in carros]
        self.cb_carro.set("")

    def _id(self, combo):
        return int(combo.get().split(" - ")[0]) if combo.get() else None

    def adicionar_item(self):
        if not self.cb_servico.get():
            messagebox.showwarning("Atenção", "Selecione um serviço.")
            return
        try:
            qtd = int(self.e_qtd.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Quantidade inválida.")
            return
        sid = self._id(self.cb_servico)
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
        del self.itens[self.tree_itens.index(sel[0])]
        self._render_itens()

    def _render_itens(self):
        self.tree_itens.delete(*self.tree_itens.get_children())
        total = 0
        for it in self.itens:
            sub = it["quantidade"] * it["preco_unit"]
            total += sub
            self.tree_itens.insert("", "end", values=(
                it["descricao"], it["quantidade"], "R$ %.2f" % it["preco_unit"], "R$ %.2f" % sub))
        self.lbl_total.config(text=("Total: R$ %.2f" % total).replace(".", ","))

    def carregar_os(self):
        filtro = self.cb_filtro.get()
        self.tree_os.delete(*self.tree_os.get_children())
        for o in db.listar_ordens():
            if filtro != "Todos" and o["status"] != filtro:
                continue
            self.tree_os.insert("", "end", tags=(o["status"],), values=(
                o["id"], o["cliente"], o["placa"], o["data_abertura"], o["status"],
                "R$ %.2f" % o["total"]))

    def selecionar_os(self, _=None):
        sel = self.tree_os.selection()
        if not sel:
            return
        oid = self.tree_os.item(sel[0])["values"][0]
        self.id_sel = oid
        ordem = next(o for o in db.listar_ordens() if o["id"] == oid)
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
        self.itens = [{"servico_id": i["servico_id"], "descricao": i["descricao"],
                       "quantidade": i["quantidade"], "preco_unit": i["preco_unit"]}
                      for i in db.listar_itens_da_ordem(oid)]
        self._render_itens()

    def salvar(self):
        cid = self._id(self.cb_cliente)
        carid = self._id(self.cb_carro)
        if not cid or not carid:
            messagebox.showwarning("Atenção", "Selecione cliente e carro.")
            return
        if not self.itens:
            messagebox.showwarning("Atenção", "Adicione ao menos um serviço.")
            return
        status = self.cb_status.get() or "Aberta"
        obs = self.e_obs.get().strip()
        if self.id_sel:
            db.atualizar_ordem(self.id_sel, cid, carid, status, obs, self.itens)
            self.ctrl.set_status(f"OS #{self.id_sel} atualizada.")
        else:
            data = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo = db.inserir_ordem(cid, carid, data, status, obs, self.itens)
            self.ctrl.set_status(f"OS #{novo} criada.")
        self.limpar()
        self.carregar_os()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione uma OS na lista.")
            return
        if messagebox.askyesno("Confirmar", "Excluir a OS selecionada?"):
            db.excluir_ordem(self.id_sel)
            self.ctrl.set_status("OS excluída.")
            self.limpar()
            self.carregar_os()

    def ver_resumo(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione uma OS na lista.")
            return
        messagebox.showinfo(f"Resumo da OS #{self.id_sel}",
                            db.itens_resumo_texto(self.id_sel))

    def exportar(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione uma OS na lista.")
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=f"OS_{self.id_sel}.txt",
            filetypes=[("Texto", "*.txt")])
        if caminho:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(db.itens_resumo_texto(self.id_sel))
            self.ctrl.set_status(f"OS #{self.id_sel} exportada.")

    def limpar(self, _=None):
        self.id_sel = None
        self.itens = []
        self.cb_cliente.set(""); self.cb_carro.set(""); self.cb_carro["values"] = []
        self.cb_status.set("Aberta"); self.cb_servico.set("")
        self.e_obs.delete(0, "end")
        self.e_qtd.delete(0, "end"); self.e_qtd.insert(0, "1")
        self._render_itens()

class UsuariosView(tk.Frame):
    def __init__(self, master, ctrl):
        super().__init__(master, bg=COR_FUNDO)
        self.ctrl = ctrl
        self.id_sel = None
        self.pack(fill="both", expand=True)

        cabecalho(self, "Usuários", "Pessoas que podem acessar o sistema")
        f_busca, self.e_busca = barra_busca(self, self.carregar)
        f_busca.pack(anchor="w", padx=24, pady=(0, 8))

        form = tk.Frame(self, bg=COR_FUNDO)
        form.pack(fill="x", padx=24)
        self.e_nome = campo(form, "Nome", 0)
        self.e_login = campo(form, "Login", 1)
        self.e_senha = campo(form, "Senha", 2)
        self.dica = tk.Label(form, text="", font=(FONTE, 8), bg=COR_FUNDO, fg=COR_NEUTRO)
        self.dica.grid(row=3, column=1, sticky="w")

        bar = tk.Frame(self, bg=COR_FUNDO)
        bar.pack(anchor="w", padx=24, pady=10)
        botao(bar, "Salvar", self.salvar, COR_PRIMARIA, COR_PRIMARIA_HOVER).pack(side="left", padx=(0, 8))
        botao(bar, "Limpar", self.limpar, COR_NEUTRO, COR_NEUTRO_HOVER).pack(side="left", padx=8)
        botao(bar, "Excluir", self.excluir, COR_PERIGO, COR_PERIGO_HOVER).pack(side="left", padx=8)

        cols = ("id", "nome", "login")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        self.tree.heading("id", text="Id"); self.tree.column("id", width=50, anchor="center")
        self.tree.heading("nome", text="Nome"); self.tree.column("nome", width=300, anchor="w")
        self.tree.heading("login", text="Login"); self.tree.column("login", width=200, anchor="w")
        aplicar_zebra(self.tree)
        ordenavel(self.tree)
        self.tree.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)
        self.carregar()

    def carregar(self, filtro=""):
        termo = filtro.lower().strip()
        self.tree.delete(*self.tree.get_children())
        for i, u in enumerate(db.listar_usuarios()):
            if termo and termo not in u["nome"].lower() and termo not in u["login"].lower():
                continue
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", tags=(tag,), values=(u["id"], u["nome"], u["login"]))

    def selecionar(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0])["values"]
        self.id_sel = v[0]
        self.limpar(manter_id=True)
        self.e_nome.insert(0, v[1])
        self.e_login.insert(0, v[2])
        self.dica.config(text="Deixe a senha em branco para mantê-la.")

    def salvar(self):
        nome = self.e_nome.get().strip()
        login = self.e_login.get().strip()
        senha = self.e_senha.get().strip()
        if not nome or not login:
            messagebox.showwarning("Atenção", "Nome e login são obrigatórios.")
            return
        if not self.id_sel and not senha:
            messagebox.showwarning("Atenção", "Defina uma senha para o novo usuário.")
            return
        if senha and len(senha) < 4:
            messagebox.showwarning("Atenção", "A senha deve ter ao menos 4 caracteres.")
            return
        try:
            if self.id_sel:
                db.atualizar_usuario(self.id_sel, nome, login, senha or None)
                self.ctrl.set_status(f"Usuário '{login}' atualizado.")
            else:
                db.inserir_usuario(nome, login, senha)
                self.ctrl.set_status(f"Usuário '{login}' criado.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Login em uso", "Já existe um usuário com esse login.")
            return
        self.limpar()
        self.carregar()

    def excluir(self):
        if not self.id_sel:
            messagebox.showwarning("Atenção", "Selecione um usuário na lista.")
            return
        if self.id_sel == self.ctrl.usuario["id"]:
            messagebox.showwarning("Ação não permitida",
                                   "Você não pode excluir o usuário que está em uso.")
            return
        if db.contar_usuarios() <= 1:
            messagebox.showwarning("Ação não permitida",
                                   "Deve existir ao menos um usuário no sistema.")
            return
        if messagebox.askyesno("Confirmar", "Excluir o usuário selecionado?"):
            db.excluir_usuario(self.id_sel)
            self.ctrl.set_status("Usuário excluído.")
            self.limpar()
            self.carregar()

    def limpar(self, manter_id=False):
        if not manter_id:
            self.id_sel = None
            self.dica.config(text="")
        for e in (self.e_nome, self.e_login, self.e_senha):
            e.delete(0, "end")

if __name__ == "__main__":
    App().mainloop()