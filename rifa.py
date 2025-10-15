# -*- coding: utf-8 -*-
import random
import tkinter as tk
from tkinter import messagebox, scrolledtext

# -----------------------------
# Estado do sistema
# -----------------------------
RIFA = {}  # {numero:int -> nome:str}
NUMEROS_DISPONIVEIS = list(range(1, 101))

root = None
status_label = None

# -----------------------------
# Lógica de negócio
# -----------------------------
def get_status_vendas() -> str:
    if not RIFA:
        return "Nenhuma rifa vendida ainda."

    status_str = "--- STATUS DAS VENDAS ---\n"
    compradores = {}
    for numero, nome in RIFA.items():
        compradores.setdefault(nome, []).append(numero)

    for nome, nums in sorted(compradores.items(), key=lambda x: x[0].lower()):
        nums.sort()
        status_str += f"Comprador: {nome:<20} | Números: {', '.join(map(str, nums))}\n"

    status_str += f"\nNúmeros vendidos: {len(RIFA)} de 100."
    return status_str


def sortear_ganhador() -> str:
    if not RIFA:
        return "Nenhum número vendido. Sorteio cancelado."
    numero_sorteado = random.choice(list(RIFA.keys()))
    ganhador = RIFA[numero_sorteado]
    return f"=== SORTEIO ===\nNúmero sorteado: {numero_sorteado}\n🎉 Ganhador: {ganhador} 🎉"


# -----------------------------
# Utilidades GUI
# -----------------------------
def atualizar_status_principal():
    if status_label is not None:
        status_label.config(text=f"Números vendidos: {len(RIFA)} de 100")


# -----------------------------
# Telas
# -----------------------------
def abrir_janela_cadastro():
    janela = tk.Toplevel(root)
    janela.title("Cadastrar Comprador")
    janela.resizable(False, False)

    nome_var = tk.StringVar()
    numeros_var = tk.StringVar()

    def realizar_cadastro():
        nome = nome_var.get().strip()
        entrada = numeros_var.get().strip()

        if not nome or not entrada:
            messagebox.showerror("Erro", "Preencha o nome e os números.")
            return

        # normaliza, elimina vazios e repetidos
        try:
            numeros_escolhidos = [int(x) for x in {p.strip() for p in entrada.split(',')} if x != ""]
        except ValueError:
            messagebox.showerror("Erro", "Números inválidos. Use apenas inteiros separados por vírgula.")
            return

        if not numeros_escolhidos:
            messagebox.showerror("Erro", "Nenhum número válido informado.")
            return

        erros = []
        vendidos = 0

        for numero in numeros_escolhidos:
            if numero < 1 or numero > 100:
                erros.append(f"{numero} (fora do intervalo 1–100)")
                continue
            if numero not in NUMEROS_DISPONIVEIS:
                erros.append(f"{numero} (já vendido)")
                continue

            RIFA[numero] = nome
            NUMEROS_DISPONIVEIS.remove(numero)
            vendidos += 1

        if vendidos:
            messagebox.showinfo("Sucesso", f"{vendidos} número(s) cadastrado(s) para {nome}.")
        if erros:
            messagebox.showwarning("Atenção", "Alguns números não foram cadastrados: " + ", ".join(erros))

        numeros_var.set("")
        atualizar_status_principal()

        # Atualiza label de disponíveis desta janela
        lbl_disp.config(text=f"Disponíveis: {len(NUMEROS_DISPONIVEIS)}")

    # Layout
    frm = tk.Frame(janela, padx=10, pady=10)
    frm.pack(fill="both", expand=True)

    tk.Label(frm, text="Nome do Comprador:").grid(row=0, column=0, sticky="w")
    tk.Entry(frm, textvariable=nome_var, width=38).grid(row=0, column=1, pady=4)

    tk.Label(frm, text="Números (1–100, vírgula):").grid(row=1, column=0, sticky="w")
    tk.Entry(frm, textvariable=numeros_var, width=38).grid(row=1, column=1, pady=4)

    tk.Button(frm, text="Cadastrar",
              command=realizar_cadastro, bg="#4CAF50", fg="white").grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")

    # Disponíveis (contador)
    lbl_disp = tk.Label(frm, text=f"Disponíveis: {len(NUMEROS_DISPONIVEIS)}")
    lbl_disp.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

    # Lista de disponíveis (opcional)
    caixa = scrolledtext.ScrolledText(frm, width=44, height=6)
    caixa.grid(row=4, column=0, columnspan=2, pady=6)
    caixa.insert(tk.END, ", ".join(map(str, NUMEROS_DISPONIVEIS)))
    caixa.config(state=tk.DISABLED)


def abrir_janela_edicao():
    if not RIFA:
        messagebox.showinfo("Aviso", "Não há números vendidos para editar.")
        return

    janela = tk.Toplevel(root)
    janela.title("Editar / Transferir")
    janela.resizable(False, False)

    # --- Alterar nome de um comprador (troca todos os números desse nome)
    tk.Label(janela, text="[1] Alterar Nome de Comprador", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=(10, 4))
    nome_antigo_var = tk.StringVar()
    nome_novo_var = tk.StringVar()

    def alterar_nome():
        antigo = nome_antigo_var.get().strip()
        novo = nome_novo_var.get().strip()
        if not antigo or not novo:
            messagebox.showerror("Erro", "Informe nome atual e novo nome.")
            return

        alterado = False
        for numero, nome in list(RIFA.items()):
            if nome.lower() == antigo.lower():
                RIFA[numero] = novo
                alterado = True
        if alterado:
            messagebox.showinfo("Sucesso", f"Números de '{antigo}' atualizados para '{novo}'.")
            nome_antigo_var.set(""); nome_novo_var.set("")
        else:
            messagebox.showerror("Erro", f"Comprador '{antigo}' não encontrado.")

    tk.Label(janela, text="Nome atual:").grid(row=1, column=0, sticky="w", padx=10)
    tk.Entry(janela, textvariable=nome_antigo_var, width=28).grid(row=1, column=1, pady=3, padx=(0,10))

    tk.Label(janela, text="Novo nome:").grid(row=2, column=0, sticky="w", padx=10)
    tk.Entry(janela, textvariable=nome_novo_var, width=28).grid(row=2, column=1, pady=3, padx=(0,10))

    tk.Button(janela, text="Mudar Nome", command=alterar_nome).grid(row=3, column=0, columnspan=2, pady=8)

    # --- Transferir número para outro comprador
    tk.Label(janela, text="[2] Transferir Número", font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=(12, 4))
    numero_transferir_var = tk.StringVar()
    novo_comprador_var = tk.StringVar()

    def transferir_numero():
        try:
            numero = int(numero_transferir_var.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "Informe um número válido.")
            return

        novo_nome = novo_comprador_var.get().strip()
        if numero not in RIFA:
            messagebox.showerror("Erro", f"O número {numero} não foi vendido.")
            return
        if not novo_nome:
            messagebox.showerror("Erro", "Informe o novo comprador.")
            return

        antigo = RIFA[numero]
        RIFA[numero] = novo_nome
        messagebox.showinfo("Sucesso", f"Número {numero} transferido de '{antigo}' para '{novo_nome}'.")
        numero_transferir_var.set(""); novo_comprador_var.set("")

    tk.Label(janela, text="Número:").grid(row=5, column=0, sticky="w", padx=10)
    tk.Entry(janela, textvariable=numero_transferir_var, width=28).grid(row=5, column=1, pady=3, padx=(0,10))

    tk.Label(janela, text="Novo comprador:").grid(row=6, column=0, sticky="w", padx=10)
    tk.Entry(janela, textvariable=novo_comprador_var, width=28).grid(row=6, column=1, pady=3, padx=(0,10))

    tk.Button(janela, text="Transferir Número", command=transferir_numero).grid(row=7, column=0, columnspan=2, pady=8)


def abrir_janela_status():
    janela = tk.Toplevel(root)
    janela.title("Status das Vendas")
    janela.resizable(False, False)

    txt = scrolledtext.ScrolledText(janela, width=60, height=20, font=("Arial", 10))
    txt.pack(padx=10, pady=10)
    txt.insert(tk.END, get_status_vendas())
    txt.config(state=tk.DISABLED)


def realizar_sorteio_gui():
    resultado = sortear_ganhador()
    if "Ganhador" in resultado:
        messagebox.showinfo("Sorteio Realizado", resultado)
    else:
        messagebox.showwarning("Sorteio Cancelado", resultado)


# -----------------------------
# Janela principal
# -----------------------------
def criar_menu_principal():
    global root, status_label
    root = tk.Tk()
    root.title("Sistema de Rifas")
    root.geometry("420x360")
    root.resizable(False, False)

    tk.Label(root, text="GERENCIAMENTO DE RIFA", font=("Arial", 16, "bold")).pack(pady=12)

    tk.Button(root, text="1. Cadastrar Compradores", width=36, command=abrir_janela_cadastro).pack(pady=5)
    tk.Button(root, text="2. Listar Status das Vendas", width=36, command=abrir_janela_status).pack(pady=5)
    tk.Button(root, text="3. Editar Comprador / Transferir", width=36, command=abrir_janela_edicao).pack(pady=5)
    tk.Button(root, text="4. REALIZAR SORTEIO", width=36, command=realizar_sorteio_gui, bg="orange").pack(pady=12)

    status_label = tk.Label(root, text=f"Números vendidos: {len(RIFA)} de 100", fg="blue")
    status_label.pack(pady=6)

    tk.Button(root, text="Sair", width=36, command=root.quit, bg="#cc0000", fg="white").pack(pady=6)

    root.mainloop()


if __name__ == "__main__":
    criar_menu_principal()
