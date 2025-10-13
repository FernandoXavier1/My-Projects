# -*- coding: utf-8 -*-
# GUI para Locadora — Tkinter
# Copia este arquivo e execute com Python 3.x

from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ===== Bases de dados (em memória) =====
carros = []      # {"modelo": str, "placa": str, "cor": str, "valor_diaria": float}
clientes = []    # {"nome": str, "cpf": str, "celular": str}
locacoes = []    # {"cliente_nome": str, "cliente_cpf": str, "carro": dict, "data_inicio": "AAAA-MM-DD",
                 #  "data_fim": "AAAA-MM-DD", "valor_diaria": float, "valor_total": float, "status": "aberta|fechada",
                 #  "pagamento": str(optional)}

# ===== Utilitários =====
def parse_data(yyyy_mm_dd: str):
    return datetime.strptime(yyyy_mm_dd.strip(), "%Y-%m-%d").date()

def dias(inicio_str: str, fim_str: str) -> int:
    d1 = parse_data(inicio_str)
    d2 = parse_data(fim_str)
    return max((d2 - d1).days, 1)

# ===== Funções de domínio (sem I/O de console) =====
def cadastrar_carro(modelo, placa, cor, diaria_txt):
    if any(c['placa'].lower() == placa.lower() for c in carros):
        raise ValueError("Veículo com esta placa já cadastrado.")
    try:
        valor_diaria = float(str(diaria_txt).replace(",", "."))
    except ValueError:
        raise ValueError("Valor da diária inválido.")
    carros.append({"modelo": modelo, "placa": placa, "cor": cor, "valor_diaria": valor_diaria})

def cadastrar_cliente(nome, cpf, celular):
    if any(c['cpf'] == cpf for c in clientes):
        raise ValueError("Cliente com este CPF já cadastrado.")
    clientes.append({"nome": nome, "cpf": cpf, "celular": celular})

def agendar_locacao_gui(cpf, placa, data_inicio, data_prevista_fim):
    if not any(c['cpf'] == cpf for c in clientes):
        raise ValueError("Cliente não encontrado.")
    try:
        _ = parse_data(data_inicio); _ = parse_data(data_prevista_fim)
    except Exception:
        raise ValueError("Data inválida. Use AAAA-MM-DD.")
    if parse_data(data_prevista_fim) < parse_data(data_inicio):
        raise ValueError("Data de devolução não pode ser anterior ao início.")

    cli = next(c for c in clientes if c['cpf'] == cpf)

    idx_car = -1; car = None
    for i, c in enumerate(carros):
        if c['placa'].lower() == placa.lower():
            idx_car = i; car = c; break
    if car is None:
        raise ValueError("Carro não encontrado ou indisponível.")

    qtd_dias = dias(data_inicio, data_prevista_fim)
    valor_diaria = float(car["valor_diaria"])
    valor_total = round(qtd_dias * valor_diaria, 2)

    carro_removido = carros.pop(idx_car)
    locacoes.append({
        "cliente_nome": cli["nome"],
        "cliente_cpf": cli["cpf"],
        "carro": carro_removido,
        "data_inicio": data_inicio,
        "data_fim": data_prevista_fim,
        "valor_diaria": valor_diaria,
        "valor_total": valor_total,
        "status": "aberta"
    })
    return qtd_dias, valor_diaria, valor_total

def receber_carro_gui(idx_loc_aberta, data_real_fim, forma_pagamento, valor_dinheiro=None):
    # idx_loc_aberta é o índice dentro da lista filtrada de locações abertas
    abertas = [l for l in locacoes if l["status"] == "aberta"]
    if not abertas:
        raise ValueError("Não há locações em aberto.")
    try:
        loc = abertas[idx_loc_aberta]
    except Exception:
        raise ValueError("Seleção inválida.")
    try:
        _ = parse_data(data_real_fim)
    except Exception:
        raise ValueError("Data inválida. Use AAAA-MM-DD.")

    qtd_dias = dias(loc["data_inicio"], data_real_fim)
    novo_total = round(qtd_dias * float(loc["valor_diaria"]), 2)

    # pagamento
    if forma_pagamento == "Dinheiro":
        try:
            valor_pago = float(str(valor_dinheiro).replace(",", "."))
        except:
            raise ValueError("Valor em dinheiro inválido.")
        if valor_pago < novo_total:
            raise ValueError("Valor insuficiente para pagamento em dinheiro.")
        troco = round(valor_pago - novo_total, 2)
    else:
        troco = 0.0

    # atualizar locação e devolver carro
    for i, l in enumerate(locacoes):
        if l is loc:
            locacoes[i]["data_fim"] = data_real_fim
            locacoes[i]["valor_total"] = novo_total
            locacoes[i]["status"] = "fechada"
            locacoes[i]["pagamento"] = forma_pagamento
            carros.append(locacoes[i]["carro"])
            break

    return qtd_dias, novo_total, troco

# ===== GUI =====
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Locadora - Tkinter")
        self.geometry("980x640")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_carros = ttk.Frame(nb)
        self.tab_clientes = ttk.Frame(nb)
        self.tab_locacoes = ttk.Frame(nb)
        self.tab_relatorios = ttk.Frame(nb)

        nb.add(self.tab_carros, text="Carros")
        nb.add(self.tab_clientes, text="Clientes")
        nb.add(self.tab_locacoes, text="Locações")
        nb.add(self.tab_relatorios, text="Relatórios")

        self._build_carros()
        self._build_clientes()
        self._build_locacoes()
        self._build_relatorios()

        self.refresh_all()

    # ------ Carros ------
    def _build_carros(self):
        frm = ttk.LabelFrame(self.tab_carros, text="Cadastrar veículo")
        frm.pack(fill="x", padx=8, pady=8)

        self.ent_modelo = ttk.Entry(frm, width=30)
        self.ent_placa  = ttk.Entry(frm, width=20)
        self.ent_cor    = ttk.Entry(frm, width=20)
        self.ent_diaria = ttk.Entry(frm, width=12)

        ttk.Label(frm, text="Modelo:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.ent_modelo.grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="Placa:").grid(row=0, column=2, sticky="w", padx=4)
        self.ent_placa.grid(row=0, column=3, sticky="w")
        ttk.Label(frm, text="Cor:").grid(row=0, column=4, sticky="w", padx=4)
        self.ent_cor.grid(row=0, column=5, sticky="w")
        ttk.Label(frm, text="Diária (R$):").grid(row=0, column=6, sticky="w", padx=4)
        self.ent_diaria.grid(row=0, column=7, sticky="w")

        ttk.Button(frm, text="Adicionar", command=self.on_add_carro).grid(row=0, column=8, padx=8)

        # tabela
        self.tree_carros = ttk.Treeview(self.tab_carros, columns=("modelo","placa","cor","diaria"), show="headings", height=16)
        for i, (h, w) in enumerate([("Modelo",260),("Placa",120),("Cor",120),("Diária (R$)",120)]):
            self.tree_carros.heading(i, text=h)
            self.tree_carros.column(i, width=w, anchor="w")
        self.tree_carros.pack(fill="both", expand=True, padx=8, pady=4)

    def on_add_carro(self):
        try:
            cadastrar_carro(self.ent_modelo.get(), self.ent_placa.get(), self.ent_cor.get(), self.ent_diaria.get())
            self.ent_modelo.delete(0, tk.END); self.ent_placa.delete(0, tk.END)
            self.ent_cor.delete(0, tk.END); self.ent_diaria.delete(0, tk.END)
            self.refresh_all()
            messagebox.showinfo("OK", "Veículo cadastrado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ------ Clientes ------
    def _build_clientes(self):
        frm = ttk.LabelFrame(self.tab_clientes, text="Cadastrar cliente")
        frm.pack(fill="x", padx=8, pady=8)

        self.ent_nome = ttk.Entry(frm, width=30)
        self.ent_cpf  = ttk.Entry(frm, width=20)
        self.ent_cel  = ttk.Entry(frm, width=20)

        ttk.Label(frm, text="Nome:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.ent_nome.grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="CPF:").grid(row=0, column=2, sticky="w", padx=4)
        self.ent_cpf.grid(row=0, column=3, sticky="w")
        ttk.Label(frm, text="Celular:").grid(row=0, column=4, sticky="w", padx=4)
        self.ent_cel.grid(row=0, column=5, sticky="w")

        ttk.Button(frm, text="Adicionar", command=self.on_add_cliente).grid(row=0, column=6, padx=8)

        self.tree_clientes = ttk.Treeview(self.tab_clientes, columns=("nome","cpf","celular"), show="headings", height=18)
        for i, (h, w) in enumerate([("Nome",320),("CPF",160),("Celular",160)]):
            self.tree_clientes.heading(i, text=h)
            self.tree_clientes.column(i, width=w, anchor="w")
        self.tree_clientes.pack(fill="both", expand=True, padx=8, pady=4)

    def on_add_cliente(self):
        try:
            cadastrar_cliente(self.ent_nome.get(), self.ent_cpf.get(), self.ent_cel.get())
            self.ent_nome.delete(0, tk.END); self.ent_cpf.delete(0, tk.END); self.ent_cel.delete(0, tk.END)
            self.refresh_all()
            messagebox.showinfo("OK", "Cliente cadastrado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ------ Locações ------
    def _build_locacoes(self):
        frm = ttk.LabelFrame(self.tab_locacoes, text="Agendar locação")
        frm.pack(fill="x", padx=8, pady=8)

        self.cbo_cpf = ttk.Combobox(frm, width=25, state="readonly")
        self.cbo_placa = ttk.Combobox(frm, width=18, state="readonly")
        self.ent_data_ini = ttk.Entry(frm, width=12)
        self.ent_data_fim = ttk.Entry(frm, width=12)

        ttk.Label(frm, text="Cliente (CPF):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.cbo_cpf.grid(row=0, column=1, sticky="w")
        ttk.Label(frm, text="Carro (placa):").grid(row=0, column=2, sticky="w", padx=6)
        self.cbo_placa.grid(row=0, column=3, sticky="w")
        ttk.Label(frm, text="Início (AAAA-MM-DD):").grid(row=0, column=4, sticky="w", padx=6)
        self.ent_data_ini.grid(row=0, column=5, sticky="w")
        ttk.Label(frm, text="Fim previsto (AAAA-MM-DD):").grid(row=0, column=6, sticky="w", padx=6)
        self.ent_data_fim.grid(row=0, column=7, sticky="w")

        ttk.Button(frm, text="Agendar", command=self.on_agendar).grid(row=0, column=8, padx=8)

        # tabela locações
        cols = ("status","cliente","cpf","modelo","placa","inicio","fim","diaria","total","pgto")
        self.tree_loc = ttk.Treeview(self.tab_locacoes, columns=cols, show="headings", height=14)
        headers = [("Status",90),("Cliente",180),("CPF",120),("Modelo",180),("Placa",100),
                   ("Início",100),("Fim",100),("Diária",90),("Total",90),("Pagamento",120)]
        for i, (h, w) in enumerate(headers):
            self.tree_loc.heading(cols[i], text=h)
            self.tree_loc.column(cols[i], width=w, anchor="w")
        self.tree_loc.pack(fill="both", expand=True, padx=8, pady=4)

        # Receber devolução
        frm2 = ttk.LabelFrame(self.tab_locacoes, text="Receber devolução")
        frm2.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm2, text="Selecione uma locação ABERTA na tabela acima.").grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)
        ttk.Label(frm2, text="Data fim real (AAAA-MM-DD):").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.ent_data_real = ttk.Entry(frm2, width=14)
        self.ent_data_real.grid(row=1, column=1, sticky="w")

        ttk.Label(frm2, text="Pagamento:").grid(row=1, column=2, sticky="w", padx=12)
        self.cbo_pgto = ttk.Combobox(frm2, values=["Dinheiro","Pix","Cartão"], width=12, state="readonly")
        self.cbo_pgto.grid(row=1, column=3, sticky="w")
        self.ent_valor_din = ttk.Entry(frm2, width=12)
        ttk.Label(frm2, text="Valor recebido (se Dinheiro):").grid(row=1, column=4, sticky="w", padx=12)
        self.ent_valor_din.grid(row=1, column=5, sticky="w")

        ttk.Button(frm2, text="Confirmar devolução", command=self.on_receber).grid(row=1, column=6, padx=12)

    def on_agendar(self):
        cpf = self.cbo_cpf.get()
        placa = self.cbo_placa.get()
        ini = self.ent_data_ini.get().strip()
        fim = self.ent_data_fim.get().strip()
        try:
            qtd_dias, diaria, total = agendar_locacao_gui(cpf, placa, ini, fim)
            self.refresh_all()
            messagebox.showinfo("OK", f"Locação criada.\nDias: {qtd_dias}\nDiária: R$ {diaria:.2f}\nTotal: R$ {total:.2f}")
            self.ent_data_ini.delete(0, tk.END); self.ent_data_fim.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_receber(self):
        # pegar seleção que esteja ABERTA
        selecionados = self.tree_loc.selection()
        if not selecionados:
            messagebox.showwarning("Atenção", "Selecione uma locação ABERTA na tabela.")
            return
        item_id = selecionados[0]
        vals = self.tree_loc.item(item_id, "values")
        if vals[0].lower() != "aberta":
            messagebox.showwarning("Atenção", "A locação selecionada já está fechada.")
            return

        # localizar índice dentro da lista de abertas
        abertas = [l for l in locacoes if l["status"] == "aberta"]
        # mapeamos pela combinação cliente+placa+inicio
        cliente, placa, inicio = vals[1], vals[4], vals[5]
        idx = None
        for i, l in enumerate(abertas):
            if l["cliente_nome"] == cliente and l["carro"]["placa"] == placa and l["data_inicio"] == inicio:
                idx = i; break
        if idx is None:
            messagebox.showerror("Erro", "Não foi possível localizar a locação aberta selecionada.")
            return

        data_real = self.ent_data_real.get().strip()
        forma = self.cbo_pgto.get() or "Pix"
        valor_din = self.ent_valor_din.get().strip() if forma == "Dinheiro" else None

        try:
            qtd, total, troco = receber_carro_gui(idx, data_real, forma, valor_din)
            self.refresh_all()
            msg = f"Devolução registrada.\nDiárias: {qtd}\nTotal: R$ {total:.2f}"
            if forma == "Dinheiro":
                msg += f"\nTroco: R$ {troco:.2f}"
            messagebox.showinfo("OK", msg)
            self.ent_data_real.delete(0, tk.END); self.ent_valor_din.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ------ Relatórios ------
    def _build_relatorios(self):
        self.lbl_loc_abertas = ttk.Label(self.tab_relatorios, text="Abertas: 0")
        self.lbl_loc_fechadas = ttk.Label(self.tab_relatorios, text="Fechadas: 0")
        self.lbl_fat_real = ttk.Label(self.tab_relatorios, text="Faturamento realizado: R$ 0,00")
        self.lbl_fat_prev = ttk.Label(self.tab_relatorios, text="Faturamento previsto: R$ 0,00")
        self.lbl_total = ttk.Label(self.tab_relatorios, text="Total geral estimado: R$ 0,00")

        pad = {"padx": 12, "pady": 8, "sticky": "w"}
        ttk.Label(self.tab_relatorios, text="RELATÓRIOS", font=("TkDefaultFont", 12, "bold")).grid(row=0, column=0, **pad)
        self.lbl_loc_abertas.grid(row=1, column=0, **pad)
        self.lbl_loc_fechadas.grid(row=2, column=0, **pad)
        self.lbl_fat_real.grid(row=3, column=0, **pad)
        self.lbl_fat_prev.grid(row=4, column=0, **pad)
        self.lbl_total.grid(row=5, column=0, **pad)

        ttk.Button(self.tab_relatorios, text="Atualizar", command=self.refresh_relatorios)\
            .grid(row=6, column=0, padx=12, pady=12, sticky="w")

    # ------ Refresh helpers ------
    def refresh_carros(self):
        self.tree_carros.delete(*self.tree_carros.get_children())
        for c in carros:
            self.tree_carros.insert("", "end", values=(c["modelo"], c["placa"], c["cor"], f"{c['valor_diaria']:.2f}"))
        self.cbo_placa["values"] = [c["placa"] for c in carros]

    def refresh_clientes(self):
        self.tree_clientes.delete(*self.tree_clientes.get_children())
        for c in clientes:
            self.tree_clientes.insert("", "end", values=(c["nome"], c["cpf"], c["celular"]))
        self.cbo_cpf["values"] = [c["cpf"] for c in clientes]

    def refresh_locacoes(self):
        self.tree_loc.delete(*self.tree_loc.get_children())
        for l in locacoes:
            car = l["carro"]
            self.tree_loc.insert("", "end", values=(
                l["status"], l["cliente_nome"], l["cliente_cpf"],
                car["modelo"], car["placa"],
                l["data_inicio"], l["data_fim"],
                f"{l['valor_diaria']:.2f}", f"{l['valor_total']:.2f}",
                l.get("pagamento","-")
            ))

    def refresh_relatorios(self):
        abertas = [l for l in locacoes if l["status"] == "aberta"]
        fechadas = [l for l in locacoes if l["status"] == "fechada"]
        fat_real = sum(l["valor_total"] for l in fechadas)
        fat_prev = sum(l["valor_total"] for l in abertas)
        self.lbl_loc_abertas.configure(text=f"Abertas: {len(abertas)}")
        self.lbl_loc_fechadas.configure(text=f"Fechadas: {len(fechadas)}")
        self.lbl_fat_real.configure(text=f"Faturamento realizado: R$ {fat_real:.2f}")
        self.lbl_fat_prev.configure(text=f"Faturamento previsto: R$ {fat_prev:.2f}")
        self.lbl_total.configure(text=f"Total geral estimado: R$ {fat_real + fat_prev:.2f}")

    def refresh_all(self):
        self.refresh_carros()
        self.refresh_clientes()
        self.refresh_locacoes()
        self.refresh_relatorios()

if __name__ == "__main__":
    app = App()
    # Dados de exemplo (opcional)
    # cadastrar_carro("Uno 1.0", "ABC1234", "Branco", "120")
    # cadastrar_cliente("Maria", "11122233344", "71 99999-0000")
    app.mainloop()
