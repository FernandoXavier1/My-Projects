import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ==========================
# Dados/Modelo (Listas e Dicionários)
# ==========================

# Lista de classes (1º ao 9º ano) com matérias padrão
MATERIAS_PADRAO = [
    "Português", "Matemática", "Inglês", "Espanhol",
    "História", "Geografia", "Ciências", "Ed. Física", "Ed. Artística"
]

CLASSES = [
    {"classe": f"{i}º ano", "materias": list(MATERIAS_PADRAO)} for i in range(1, 10)
]

# Dicionário de alunos (cada chave é o 'nome' curto único)
# Estrutura do aluno:
# {
#   "nome": str,
#   "nome_completo": str,
#   "pais": str (opcional),
#   "idade": int,
#   "aniversario": str (opcional, formato DD/MM/AAAA),
#   "classe": str (ex: "5º ano"),
#   "materias_opc": [str, ...],
#   "boletim": {
#       materia: {"b1": float|None, "b2": float|None, "b3": float|None, "b4": float|None}
#   }
# }
ALUNOS: dict[str, dict] = {}

# ==========================
# Funções de domínio (CRUD e regras)
# ==========================

def _materias_da_classe(classe: str) -> list[str]:
    for c in CLASSES:
        if c["classe"] == classe:
            return list(c["materias"])  # cópia
    return list(MATERIAS_PADRAO)


def _cria_boletim_inicial(classe: str, materias_opc: list[str] | None = None) -> dict:
    materias = _materias_da_classe(classe)
    if materias_opc:
        materias += [m for m in materias_opc if m not in materias]
    return {m: {"b1": None, "b2": None, "b3": None, "b4": None} for m in materias}


def incluir_aluno(nome_curto: str, nome_completo: str, idade: int,
                   classe: str, pais: str = "", aniversario: str = ""):
    if not nome_curto or not nome_completo or not idade or not classe:
        raise ValueError("Campos obrigatórios: nome (curto), nome completo, idade e classe.")
    if nome_curto in ALUNOS:
        raise ValueError("Já existe um aluno com esse nome (curto). Use outro identificador.")

    aluno = {
        "nome": nome_curto,
        "nome_completo": nome_completo,
        "pais": pais or "",
        "idade": int(idade),
        "aniversario": aniversario or "",
        "classe": classe,
        "materias_opc": [],
        "boletim": _cria_boletim_inicial(classe)
    }
    ALUNOS[nome_curto] = aluno


def excluir_aluno(nome_curto: str):
    if nome_curto in ALUNOS:
        del ALUNOS[nome_curto]
    else:
        raise KeyError("Aluno não encontrado.")


def incluir_materia_opcional(nome_curto: str, materia: str):
    if nome_curto not in ALUNOS:
        raise KeyError("Aluno não encontrado.")
    materia = materia.strip()
    if not materia:
        raise ValueError("Matéria inválida.")
    a = ALUNOS[nome_curto]
    if materia not in a["materias_opc"]:
        a["materias_opc"].append(materia)
    if materia not in a["boletim"]:
        a["boletim"][materia] = {"b1": None, "b2": None, "b3": None, "b4": None}


def excluir_materia_opcional(nome_curto: str, materia: str):
    if nome_curto not in ALUNOS:
        raise KeyError("Aluno não encontrado.")
    a = ALUNOS[nome_curto]
    if materia in a["materias_opc"]:
        a["materias_opc"].remove(materia)
    # Ao remover opcional, também removemos do boletim (não removemos matérias padrão)
    if materia in a["boletim"] and materia not in _materias_da_classe(a["classe"]):
        del a["boletim"][materia]


def set_nota(nome_curto: str, materia: str, bimestre: int, nota: float | None):
    if nome_curto not in ALUNOS:
        raise KeyError("Aluno não encontrado.")
    if bimestre not in (1, 2, 3, 4):
        raise ValueError("Bimestre deve ser 1, 2, 3 ou 4.")
    a = ALUNOS[nome_curto]
    if materia not in a["boletim"]:
        # caso a matéria não exista ainda, cria com base no padrão (situação rara)
        a["boletim"][materia] = {"b1": None, "b2": None, "b3": None, "b4": None}
    chave = f"b{bimestre}"
    a["boletim"][materia][chave] = (None if nota is None else float(nota))


def excluir_nota(nome_curto: str, materia: str, bimestre: int):
    set_nota(nome_curto, materia, bimestre, None)


def media_materia(registro_materia: dict) -> float | None:
    notas = [registro_materia.get(f"b{i}") for i in range(1, 5)]
    notas_presentes = [n for n in notas if n is not None]
    if not notas_presentes:
        return None
    return sum(notas_presentes) / len(notas_presentes)


def status_aluno(nome_curto: str) -> tuple[str, int]:
    """Retorna (status, qtd_materias_abaixo_7).
    Aprovado: nenhuma média < 7
    Recuperação: 1 ou 2 médias < 7
    Reprovado: 3 ou mais médias < 7
    """
    if nome_curto not in ALUNOS:
        raise KeyError("Aluno não encontrado.")
    a = ALUNOS[nome_curto]
    abaixo7 = 0
    for materia, registros in a["boletim"].items():
        m = media_materia(registros)
        if m is not None and m < 7:
            abaixo7 += 1
    if abaixo7 == 0:
        return ("ALUNO APROVADO", abaixo7)
    elif abaixo7 in (1, 2):
        return ("ALUNO EM RECUPERAÇÃO", abaixo7)
    else:
        return ("ALUNO REPROVADO", abaixo7)


def materias_do_aluno(nome_curto: str) -> list[str]:
    a = ALUNOS[nome_curto]
    base = _materias_da_classe(a["classe"])
    # Garantir união com opcionais já existentes no boletim
    extras = [m for m in a["boletim"].keys() if m not in base]
    return base + sorted(set(extras))

# ==========================
# Interface Tkinter
# ==========================

class BoletimApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Boletim Escolar – Tkinter")
        self.geometry("1080x680")
        self.minsize(980, 620)

        self._build_ui()

    # ---------- UI Builders ----------
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        self.tab_alunos = ttk.Frame(nb)
        self.tab_notas = ttk.Frame(nb)
        self.tab_boletim = ttk.Frame(nb)

        nb.add(self.tab_alunos, text="Alunos")
        nb.add(self.tab_notas, text="Notas")
        nb.add(self.tab_boletim, text="Boletim")

        self._build_tab_alunos()
        self._build_tab_notas()
        self._build_tab_boletim()

    def _build_tab_alunos(self):
        frm = self.tab_alunos

        # Esquerda: Lista de alunos
        left = ttk.Frame(frm)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(left, text="Alunos (selecione para editar)").pack(anchor=tk.W)
        self.lb_alunos = tk.Listbox(left, height=20)
        self.lb_alunos.pack(fill=tk.BOTH, expand=True)
        self.lb_alunos.bind("<<ListboxSelect>>", self._on_select_aluno)

        btns_left = ttk.Frame(left)
        btns_left.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(btns_left, text="Excluir Aluno", command=self._excluir_aluno).pack(side=tk.LEFT)

        # Direita: Formulário
        right = ttk.Frame(frm)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        frm_form = ttk.LabelFrame(right, text="Cadastro/Atualização de Aluno")
        frm_form.pack(fill=tk.X, padx=4, pady=4)

        # Linha 1
        row = ttk.Frame(frm_form)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Nome curto (chave):").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.ent_nome = ttk.Entry(row, width=20)
        self.ent_nome.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(row, text="Nome completo:").grid(row=0, column=2, sticky=tk.W, padx=12)
        self.ent_nome_completo = ttk.Entry(row)
        self.ent_nome_completo.grid(row=0, column=3, sticky=tk.EW)
        row.columnconfigure(3, weight=1)

        # Linha 2
        row2 = ttk.Frame(frm_form)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Idade:").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.ent_idade = ttk.Entry(row2, width=8)
        self.ent_idade.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(row2, text="Pais/Responsáveis (opcional):").grid(row=0, column=2, sticky=tk.W, padx=12)
        self.ent_pais = ttk.Entry(row2)
        self.ent_pais.grid(row=0, column=3, sticky=tk.EW)
        row2.columnconfigure(3, weight=1)

        # Linha 3
        row3 = ttk.Frame(frm_form)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Aniversário (DD/MM/AAAA, opcional):").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.ent_aniv = ttk.Entry(row3, width=14)
        self.ent_aniv.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(row3, text="Classe:").grid(row=0, column=2, sticky=tk.W, padx=12)
        self.cmb_classe = ttk.Combobox(row3, values=[c["classe"] for c in CLASSES], state="readonly")
        self.cmb_classe.grid(row=0, column=3, sticky=tk.W)
        self.cmb_classe.current(0)

        # Botões
        btns = ttk.Frame(frm_form)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Incluir / Atualizar", command=self._incluir_ou_atualizar_aluno).pack(side=tk.LEFT)

        # Materias Opcionais
        frm_opc = ttk.LabelFrame(right, text="Matérias Opcionais do Aluno Selecionado")
        frm_opc.pack(fill=tk.BOTH, expand=True, padx=4, pady=6)

        top_opc = ttk.Frame(frm_opc)
        top_opc.pack(fill=tk.X, pady=4)
        ttk.Label(top_opc, text="Nova matéria opcional:").pack(side=tk.LEFT)
        self.ent_materia_opc = ttk.Entry(top_opc)
        self.ent_materia_opc.pack(side=tk.LEFT, padx=6)
        ttk.Button(top_opc, text="Adicionar", command=self._adicionar_materia_opc).pack(side=tk.LEFT)
        ttk.Button(top_opc, text="Remover selecionada", command=self._remover_materia_opc).pack(side=tk.LEFT, padx=6)

        self.lb_materias_opc = tk.Listbox(frm_opc, height=8)
        self.lb_materias_opc.pack(fill=tk.BOTH, expand=True)

    def _build_tab_notas(self):
        frm = self.tab_notas

        top = ttk.Frame(frm)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(top, text="Aluno:").pack(side=tk.LEFT)
        self.cmb_aluno_notas = ttk.Combobox(top, values=[], state="readonly")
        self.cmb_aluno_notas.pack(side=tk.LEFT, padx=6)
        self.cmb_aluno_notas.bind("<<ComboboxSelected>>", self._on_select_aluno_notas)

        ttk.Label(top, text="Matéria:").pack(side=tk.LEFT, padx=(16, 0))
        self.cmb_materia = ttk.Combobox(top, values=[], state="readonly", width=24)
        self.cmb_materia.pack(side=tk.LEFT, padx=6)

        ttk.Label(top, text="Bimestre:").pack(side=tk.LEFT, padx=(16, 0))
        self.cmb_bim = ttk.Combobox(top, values=[1, 2, 3, 4], state="readonly", width=5)
        self.cmb_bim.pack(side=tk.LEFT, padx=6)
        self.cmb_bim.current(0)

        ttk.Label(top, text="Nota:").pack(side=tk.LEFT, padx=(16, 0))
        self.ent_nota = ttk.Entry(top, width=8)
        self.ent_nota.pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Incluir/Atualizar Nota", command=self._incluir_nota).pack(side=tk.LEFT, padx=(16, 6))
        ttk.Button(top, text="Excluir Nota", command=self._excluir_nota).pack(side=tk.LEFT)

        # Tabela simples das notas da matéria selecionada
        self.frm_grid_notas = ttk.LabelFrame(frm, text="Notas da Matéria (bimestres)")
        self.frm_grid_notas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.grid_labels = []  # [(row_labels)] para redesenho

    def _build_tab_boletim(self):
        frm = self.tab_boletim

        top = ttk.Frame(frm)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(top, text="Aluno:").pack(side=tk.LEFT)
        self.cmb_aluno_boletim = ttk.Combobox(top, values=[], state="readonly")
        self.cmb_aluno_boletim.pack(side=tk.LEFT, padx=6)
        self.cmb_aluno_boletim.bind("<<ComboboxSelected>>", self._desenhar_boletim)

        self.lbl_status = ttk.Label(top, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_status.pack(side=tk.RIGHT)

        self.canvas_boletim = tk.Canvas(frm)
        self.canvas_boletim.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.inner_boletim = ttk.Frame(self.canvas_boletim)
        self.canvas_boletim.create_window((0, 0), window=self.inner_boletim, anchor="nw")

        self.inner_boletim.bind("<Configure>", lambda e: self.canvas_boletim.configure(scrollregion=self.canvas_boletim.bbox("all")))

    # ---------- Helpers UI ----------
    def _refresh_comboboxes(self):
        alunos = sorted(ALUNOS.keys())
        for cmb in (self.cmb_aluno_notas, self.cmb_aluno_boletim):
            sel = cmb.get()
            cmb["values"] = alunos
            if sel in alunos:
                cmb.set(sel)
            elif alunos:
                cmb.current(0)

    def _refresh_lista_alunos(self):
        self.lb_alunos.delete(0, tk.END)
        for k in sorted(ALUNOS.keys()):
            a = ALUNOS[k]
            self.lb_alunos.insert(tk.END, f"{a['nome']} – {a['nome_completo']} ({a['classe']})")

    def _get_selected_aluno_key(self) -> str | None:
        sel = self.lb_alunos.curselection()
        if not sel:
            return None
        texto = self.lb_alunos.get(sel[0])
        # antes do ' – ' está o nome curto
        key = texto.split(" – ")[0]
        return key

    def _carregar_aluno_no_form(self, key: str):
        a = ALUNOS[key]
        self.ent_nome.delete(0, tk.END); self.ent_nome.insert(0, a["nome"])
        self.ent_nome_completo.delete(0, tk.END); self.ent_nome_completo.insert(0, a["nome_completo"])
        self.ent_idade.delete(0, tk.END); self.ent_idade.insert(0, str(a["idade"]))
        self.ent_pais.delete(0, tk.END); self.ent_pais.insert(0, a["pais"]) 
        self.ent_aniv.delete(0, tk.END); self.ent_aniv.insert(0, a["aniversario"]) 
        try:
            idx = [c["classe"] for c in CLASSES].index(a["classe"]) 
        except ValueError:
            idx = 0
        self.cmb_classe.current(idx)
        # materias opcionais
        self.lb_materias_opc.delete(0, tk.END)
        for m in a["materias_opc"]:
            self.lb_materias_opc.insert(tk.END, m)

    def _on_select_aluno(self, _evt=None):
        key = self._get_selected_aluno_key()
        if key:
            self._carregar_aluno_no_form(key)
            self._refresh_comboboxes()
            # também atualiza combo de matérias na aba Notas, se aluno estiver selecionado
            self._update_materias_combo_for_aluno(key)

    def _update_materias_combo_for_aluno(self, key: str):
        mats = materias_do_aluno(key)
        self.cmb_materia["values"] = mats
        if mats:
            self.cmb_materia.current(0)
        self._desenha_grid_notas()

    # ---------- Ações (callbacks) ----------
    def _incluir_ou_atualizar_aluno(self):
        try:
            nome = self.ent_nome.get().strip()
            nome_completo = self.ent_nome_completo.get().strip()
            idade_txt = self.ent_idade.get().strip()
            idade = int(idade_txt)
            pais = self.ent_pais.get().strip()
            aniversario = self.ent_aniv.get().strip()
            classe = self.cmb_classe.get()

            if nome in ALUNOS:
                # atualizar
                a = ALUNOS[nome]
                a["nome_completo"] = nome_completo or a["nome_completo"]
                a["idade"] = idade
                a["pais"] = pais
                a["aniversario"] = aniversario
                if classe != a["classe"]:
                    # mudou de classe -> reconstruir boletim com matérias da nova classe + opcionais atuais
                    a["classe"] = classe
                    a["boletim"] = _cria_boletim_inicial(classe, a["materias_opc"])
                messagebox.showinfo("OK", "Aluno atualizado.")
            else:
                incluir_aluno(nome, nome_completo, idade, classe, pais, aniversario)
                messagebox.showinfo("OK", "Aluno incluído.")

            self._refresh_lista_alunos()
            self._refresh_comboboxes()
            if nome in ALUNOS:
                self._update_materias_combo_for_aluno(nome)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_aluno(self):
        key = self._get_selected_aluno_key()
        if not key:
            messagebox.showwarning("Atenção", "Selecione um aluno na lista.")
            return
        if messagebox.askyesno("Confirmar", f"Excluir o aluno '{key}'?"):
            try:
                excluir_aluno(key)
                self._refresh_lista_alunos()
                self._refresh_comboboxes()
                self.lb_materias_opc.delete(0, tk.END)
                messagebox.showinfo("OK", "Aluno excluído.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _adicionar_materia_opc(self):
        key = self._get_selected_aluno_key()
        if not key:
            messagebox.showwarning("Atenção", "Selecione um aluno na lista.")
            return
        materia = self.ent_materia_opc.get().strip()
        if not materia:
            messagebox.showwarning("Atenção", "Informe o nome da matéria opcional.")
            return
        try:
            incluir_materia_opcional(key, materia)
            self.lb_materias_opc.insert(tk.END, materia)
            self._update_materias_combo_for_aluno(key)
            messagebox.showinfo("OK", f"Matéria '{materia}' adicionada.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _remover_materia_opc(self):
        key = self._get_selected_aluno_key()
        if not key:
            messagebox.showwarning("Atenção", "Selecione um aluno na lista.")
            return
        sel = self.lb_materias_opc.curselection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione a matéria opcional a remover.")
            return
        materia = self.lb_materias_opc.get(sel[0])
        try:
            excluir_materia_opcional(key, materia)
            self.lb_materias_opc.delete(sel[0])
            self._update_materias_combo_for_aluno(key)
            messagebox.showinfo("OK", f"Matéria '{materia}' removida.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _on_select_aluno_notas(self, _evt=None):
        key = self.cmb_aluno_notas.get()
        if key:
            self._update_materias_combo_for_aluno(key)

    def _incluir_nota(self):
        key = self.cmb_aluno_notas.get()
        materia = self.cmb_materia.get()
        try:
            b = int(self.cmb_bim.get())
        except Exception:
            b = 1
        txt = self.ent_nota.get().strip()
        if not key or not materia:
            messagebox.showwarning("Atenção", "Selecione aluno e matéria.")
            return
        if not txt:
            messagebox.showwarning("Atenção", "Informe a nota.")
            return
        try:
            nota = float(txt)
            if nota < 0 or nota > 10:
                raise ValueError("Nota deve estar entre 0 e 10.")
            set_nota(key, materia, b, nota)
            self._desenha_grid_notas()
            if self.cmb_aluno_boletim.get() == key:
                self._desenhar_boletim()
            messagebox.showinfo("OK", "Nota registrada.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_nota(self):
        key = self.cmb_aluno_notas.get()
        materia = self.cmb_materia.get()
        try:
            b = int(self.cmb_bim.get())
        except Exception:
            b = 1
        if not key or not materia:
            messagebox.showwarning("Atenção", "Selecione aluno e matéria.")
            return
        try:
            excluir_nota(key, materia, b)
            self._desenha_grid_notas()
            if self.cmb_aluno_boletim.get() == key:
                self._desenhar_boletim()
            messagebox.showinfo("OK", "Nota excluída.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ---------- Grids/Tabelas desenhadas com Labels (permite cores por célula) ----------
    def _clear_grid_labels(self):
        for row in self.grid_labels:
            for w in row:
                w.destroy()
        self.grid_labels.clear()

    def _desenha_grid_notas(self):
        self._clear_grid_labels()
        for w in self.frm_grid_notas.winfo_children():
            if isinstance(w, ttk.Frame) and w is not self.frm_grid_notas:
                w.destroy()
        # Cabeçalho
        header = ttk.Frame(self.frm_grid_notas)
        header.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(header, text="B1", width=6, anchor="center").grid(row=0, column=0)
        ttk.Label(header, text="B2", width=6, anchor="center").grid(row=0, column=1)
        ttk.Label(header, text="B3", width=6, anchor="center").grid(row=0, column=2)
        ttk.Label(header, text="B4", width=6, anchor="center").grid(row=0, column=3)
        ttk.Label(header, text="Média", width=8, anchor="center").grid(row=0, column=4)

        key = self.cmb_aluno_notas.get()
        materia = self.cmb_materia.get()
        if not key or not materia or key not in ALUNOS:
            return
        a = ALUNOS[key]
        reg = a["boletim"].get(materia, {"b1": None, "b2": None, "b3": None, "b4": None})

        rowf = ttk.Frame(self.frm_grid_notas)
        rowf.pack(fill=tk.X, padx=6, pady=4)
        row_widgets = []
        for i in range(1, 5):
            val = reg.get(f"b{i}")
            txt = "" if val is None else f"{val:.1f}"
            color = ("red" if (val is not None and val < 7) else "blue") if val is not None else "black"
            lbl = tk.Label(rowf, text=txt, width=6, anchor="center", fg=color)
            lbl.grid(row=0, column=i-1, padx=2)
            row_widgets.append(lbl)
        med = media_materia(reg)
        txtm = "" if med is None else f"{med:.2f}"
        colm = ("red" if (med is not None and med < 7) else "blue") if med is not None else "black"
        lblm = tk.Label(rowf, text=txtm, width=8, anchor="center", fg=colm, font=("Segoe UI", 10, "bold"))
        lblm.grid(row=0, column=4, padx=2)
        row_widgets.append(lblm)
        self.grid_labels.append(row_widgets)

    # ---------- Boletim Completo (por aluno) ----------
    def _desenhar_boletim(self, _evt=None):
        for w in self.inner_boletim.winfo_children():
            w.destroy()
        key = self.cmb_aluno_boletim.get()
        if not key or key not in ALUNOS:
            self.lbl_status.config(text="")
            return

        a = ALUNOS[key]
        materias = materias_do_aluno(key)

        # Cabeçalho
        header = ttk.Frame(self.inner_boletim)
        header.grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Label(header, text="Matéria", width=22).grid(row=0, column=0, padx=4)
        for i, title in enumerate(["B1", "B2", "B3", "B4", "Média"]):
            ttk.Label(header, text=title, width=8, anchor="center").grid(row=0, column=i+1, padx=2)

        # Linhas por matéria
        r = 1
        for materia in materias:
            reg = a["boletim"].get(materia, {"b1": None, "b2": None, "b3": None, "b4": None})
            ttk.Label(self.inner_boletim, text=materia, width=22).grid(row=r, column=0, sticky="w", padx=4, pady=1)
            for i in range(1, 5):
                val = reg.get(f"b{i}")
                txt = "" if val is None else f"{val:.1f}"
                color = ("red" if (val is not None and val < 7) else "blue") if val is not None else "black"
                tk.Label(self.inner_boletim, text=txt, width=8, anchor="center", fg=color).grid(row=r, column=i, padx=2)
            med = media_materia(reg)
            txtm = "" if med is None else f"{med:.2f}"
            colm = ("red" if (med is not None and med < 7) else "blue") if med is not None else "black"
            tk.Label(self.inner_boletim, text=txtm, width=8, anchor="center", fg=colm, font=("Segoe UI", 10, "bold")).grid(row=r, column=5, padx=2)
            r += 1

        # Status final
        st, q = status_aluno(key)
        self.lbl_status.config(text=f"{st}  |  Médias < 7: {q}")

    # ---------- Inicialização visual ----------
    def popular_exemplo(self):
        # Alguns exemplos para testar rapidamente
        try:
            incluir_aluno("joao", "João da Silva", 11, "5º ano", "Maria/Paulo", "12/03/2014")
            incluir_aluno("ana", "Ana Pereira", 13, "7º ano", "Carla/Rafael", "05/09/2012")
            incluir_materia_opcional("ana", "Robótica")
            set_nota("joao", "Português", 1, 6.5)
            set_nota("joao", "Matemática", 1, 8.0)
            set_nota("joao", "Matemática", 2, 7.0)
            set_nota("ana", "Robótica", 1, 9.5)
            set_nota("ana", "História", 1, 6.0)
        except Exception:
            pass
        self._refresh_lista_alunos()
        self._refresh_comboboxes()
        if self.cmb_aluno_notas.get():
            self._update_materias_combo_for_aluno(self.cmb_aluno_notas.get())


if __name__ == "__main__":
    app = BoletimApp()
    app.popular_exemplo()
    app.mainloop()
