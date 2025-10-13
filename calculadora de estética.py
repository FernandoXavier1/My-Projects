import tkinter as tk
from tkinter import messagebox
import math

# Dicionário global para armazenar os campos de entrada (Entry widgets)
entradas = {}

def formatar_float(entrada_str):
    """Converte string com vírgula ou ponto para float."""
    return float(entrada_str.replace(',', '.'))

def calcular_pontos(altura_m, peso, percentual_gordura, largura_ombro, largura_cintura):
    """Contém toda a lógica de cálculo do potencial estético."""
    
    # 1. Cálculo dos Indicadores
    try:
        if altura_m <= 0 or largura_cintura <= 0:
            raise ZeroDivisionError

        massa_magra = peso * (100 - percentual_gordura) / 100
        immf = massa_magra / (altura_m ** 2)
        proporcao_ombro_cintura = largura_ombro / largura_cintura
        
    except ZeroDivisionError:
        return "Erro: Altura e cintura devem ser maiores que zero."
    
    # 2. Cálculo dos Pontos
    pontos_altura = 2 * (1 - abs(altura_m - 1.85) / 1.85)
    pontos_gordura = 3 * (1 - abs(percentual_gordura - 12) / 12)
    pontos_immf = 3 * (1 - abs(immf - 23) / 23)
    pontos_proporcao = 2 * (1 - abs(proporcao_ombro_cintura - 1.6) / 1.6)

    # 3. Ajuste de Pontos para evitar valores negativos
    pontos_altura = max(0, pontos_altura)
    pontos_gordura = max(0, pontos_gordura)
    pontos_immf = max(0, pontos_immf)
    pontos_proporcao = max(0, pontos_proporcao)

    # 4. Cálculo Final do Potencial
    pontos_totais = pontos_altura + pontos_gordura + pontos_immf + pontos_proporcao
    pontos_maximos = 2 + 3 + 3 + 2
    potencial_estetico = (pontos_totais / pontos_maximos) * 100

    resultado_formatado = (
        f"--- Resultados ---\n"
        f"IMMF: {immf:.2f} | Proporção O/C: {proporcao_ombro_cintura:.2f}\n"
        f"Seu Potencial Estético é de {potencial_estetico:.2f}%"
    )
    return resultado_formatado

def calcular_e_exibir():
    """Função chamada pelo botão para pegar dados e mostrar o resultado."""
    try:
        # Pega os valores dos campos de entrada
        altura_cm = formatar_float(entradas['altura'].get())
        peso = formatar_float(entradas['peso'].get())
        percentual_gordura = formatar_float(entradas['gordura'].get())
        largura_ombro = formatar_float(entradas['ombro'].get())
        largura_cintura = formatar_float(entradas['cintura'].get())
        
        # Converte cm para metros
        altura_m = altura_cm / 100
        
        # Chama a função de cálculo
        resultado = calcular_pontos(altura_m, peso, percentual_gordura, largura_ombro, largura_cintura)
        
        # Atualiza o rótulo de resultado
        entradas['resultado_label'].config(text=resultado)

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira números válidos em todos os campos.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def criar_interface():
    """Configura e exibe a janela principal do Tkinter."""
    global entradas
    
    # Configuração básica da janela
    janela = tk.Tk()
    janela.title("Calculadora de Potencial Estético")
    janela.geometry("400x400")
    
    # Estilo de padding para facilitar o layout
    padx_val, pady_val = 10, 5
    
    # --- Widgets de Entrada de Dados ---
    
    # 1. Altura (em CM)
    tk.Label(janela, text="Altura (cm):").grid(row=0, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['altura'] = tk.Entry(janela)
    entradas['altura'].grid(row=0, column=1, padx=padx_val, pady=pady_val)

    # 2. Peso
    tk.Label(janela, text="Peso (kg):").grid(row=1, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['peso'] = tk.Entry(janela)
    entradas['peso'].grid(row=1, column=1, padx=padx_val, pady=pady_val)

    # 3. Percentual de Gordura
    tk.Label(janela, text="% Gordura:").grid(row=2, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['gordura'] = tk.Entry(janela)
    entradas['gordura'].grid(row=2, column=1, padx=padx_val, pady=pady_val)

    # 4. Largura do Ombro
    tk.Label(janela, text="Largura do Ombro (cm):").grid(row=3, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['ombro'] = tk.Entry(janela)
    entradas['ombro'].grid(row=3, column=1, padx=padx_val, pady=pady_val)

    # 5. Largura da Cintura
    tk.Label(janela, text="Largura da Cintura (cm):").grid(row=4, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['cintura'] = tk.Entry(janela)
    entradas['cintura'].grid(row=4, column=1, padx=padx_val, pady=pady_val)

    # --- Botão de Cálculo ---
    tk.Button(janela, text="CALCULAR POTENCIAL", command=calcular_e_exibir, bg='#4CAF50', fg='white').grid(row=5, column=0, columnspan=2, padx=padx_val, pady=15)

    # --- Label para Mostrar o Resultado ---
    entradas['resultado_label'] = tk.Label(janela, text="Aguardando dados...", justify=tk.LEFT, fg='blue')
    entradas['resultado_label'].grid(row=6, column=0, columnspan=2, padx=padx_val, pady=pady_val)

    janela.mainloop()

# Inicia a aplicação
criar_interface()