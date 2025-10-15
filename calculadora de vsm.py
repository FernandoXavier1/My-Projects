import tkinter as tk
from tkinter import messagebox

# ---- dicionário global para guardar os widgets de entrada ----
entradas = {}

# --- TEXTO DA AJUDA (ATUALIZADO) ---
TEXTO_EXPLICACAO = """
## Algoritmo de Pontuação Estética ##

Este cálculo atribui pontos (de um máximo de 10) às suas métricas corporais, baseando-se em proporções ideais.

MÉTRICAS E PESOS:
- Altura (Peso: 2): Atinge o máximo entre 1,82m e 1,87m. Pontuação é 0 abaixo de 1,65m ou acima de 2,05m.
- % Gordura (Peso: 3): Máximo entre 10% e 13%. Pontuação é 0 acima de 35%.
- IMMF (Peso: 3): Máximo em 23 kg/m² ou acima. Pontuação é 0 abaixo de 16 kg/m².
- Proporção Ombro/Cintura (Peso: 2): 
    • 1,6 a 1,7 → pontuação máxima. 
    • 1,0 a 1,6 → pontuação cresce linearmente até o máximo.
    • < 1,0 ou > 1,7 → pontuação zero.

CLASSIFICAÇÃO VSM (Valor Sociocultural da Métrica):
- 0% a 49.99%: Que pena, você é um subfive.
- 50% a 59.99%: Que pena, você está abaixo da média.
- 60% a 69.99%: Você é mediano.
- 70% a 79.99%: Legal, você está acima da média.
- 80% a 89.99%: Parabéns, você é um Chad Light!
- 90% a 99.99%: Parabéns, você é um Chad!
- 100%: Parabéns, você é um Deus Grego!
"""

def formatar_float(entrada_str):
    """Converte string com vírgula ou ponto para float."""
    return float(entrada_str.replace(',', '.'))

def classificar_potencial(potencial_estetico):
    """Retorna a mensagem de classificação com base na pontuação."""
    if potencial_estetico == 100.0:
        return "Parabéns, você é um Deus Grego!"
    elif potencial_estetico >= 90.0:
        return "Parabéns, você é um Chad!"
    elif potencial_estetico >= 80.0:
        return "Parabéns, você é um Chad Light!"
    elif potencial_estetico >= 70.0:
        return "Legal, você está acima da média."
    elif potencial_estetico >= 60.0:
        return "Você é mediano."
    elif potencial_estetico >= 50.0:
        return "Que pena, você está abaixo da média."
    else:  # 0.0 a 49.999...%
        return "Que pena, você é um subfive."

def calcular_pontos(altura_m, peso, percentual_gordura, largura_ombro, largura_cintura):
    """Contém toda a lógica de cálculo do potencial estético."""
    # Constantes
    PONTOS_MAX_ALTURA = 2.0
    PONTOS_MAX_GORDURA = 3.0
    PONTOS_MAX_IMMF = 3.0
    PONTOS_MAX_PROPORCAO = 2.0
    FAIXA_PROPORCIONAL_GORDURA = 35.0 - 13.0

    # 1. Cálculo dos Indicadores
    try:
        if altura_m <= 0 or largura_cintura <= 0:
            raise ZeroDivisionError

        massa_magra = peso * (100 - percentual_gordura) / 100
        immf = massa_magra / (altura_m ** 2)
        proporcao_ombro_cintura = largura_ombro / largura_cintura

    except ZeroDivisionError:
        return None, "Erro: Altura e cintura devem ser maiores que zero."

    # --- PONTUAÇÃO DA ALTURA ---
    pontos_altura = 0.0
    if altura_m < 1.65:
        pontos_altura = 0.0
    elif 1.65 <= altura_m <= 1.82:
        faixa_altura = 1.82 - 1.65
        progresso = altura_m - 1.65
        pontos_altura = PONTOS_MAX_ALTURA * (progresso / faixa_altura)
    elif 1.82 < altura_m <= 1.87:
        pontos_altura = PONTOS_MAX_ALTURA
    elif 1.87 < altura_m <= 2.05:
        altura_inicio_queda = 1.87
        faixa_queda = 2.05 - altura_inicio_queda
        distancia_percorrida = altura_m - altura_inicio_queda
        fator_pontuacao = 1.0 - (distancia_percorrida / faixa_queda)
        pontos_altura = PONTOS_MAX_ALTURA * fator_pontuacao
    elif altura_m > 2.05:
        pontos_altura = 0.0

    # --- PONTUAÇÃO DA GORDURA ---
    pontos_gordura = 0.0
    if percentual_gordura > 35.0:
        pontos_gordura = 0.0
    elif 13.0 <= percentual_gordura <= 35.0:
        progresso = percentual_gordura - 13.0
        pontos_gordura = PONTOS_MAX_GORDURA * (1.0 - (progresso / FAIXA_PROPORCIONAL_GORDURA))
    elif 10.0 <= percentual_gordura < 13.0:
        pontos_gordura = PONTOS_MAX_GORDURA
    elif percentual_gordura < 10.0:
        distancia = 10.0 - percentual_gordura
        pontos_gordura = PONTOS_MAX_GORDURA * (1.0 - (distancia / FAIXA_PROPORCIONAL_GORDURA))

    # --- NOVA REGRA: PONTUAÇÃO OMBRO/CINTURA ---
    # 1,6 a 1,7  -> máximo
    # 1,0 a 1,6  -> interpolação linear 0..máximo
    # < 1,0 e > 1,7 -> zero
    p = proporcao_ombro_cintura
    if 1.6 <= p <= 1.7:
        pontos_proporcao = PONTOS_MAX_PROPORCAO
    elif 1.0 <= p < 1.6:
        # Linear: p=1.0 -> 0; p=1.6 -> max
        pontos_proporcao = PONTOS_MAX_PROPORCAO * ((p - 1.0) / (1.6 - 1.0))
    else:
        pontos_proporcao = 0.0

    # --- PONTUAÇÃO DO IMMF ---
    pontos_immf = 0.0
    if immf >= 23.0:
        pontos_immf = PONTOS_MAX_IMMF
    elif 16.0 <= immf < 23.0:
        faixa_proporcional = 23.0 - 16.0
        progresso = immf - 16.0
        pontos_immf = PONTOS_MAX_IMMF * (progresso / faixa_proporcional)
    else:
        pontos_immf = 0.0

    # Clamp
    pontos_altura = max(0.0, pontos_altura)
    pontos_gordura = max(0.0, pontos_gordura)
    pontos_immf = max(0.0, pontos_immf)
    pontos_proporcao = max(0.0, pontos_proporcao)

    # Cálculo Final do Potencial
    pontos_totais = pontos_altura + pontos_gordura + pontos_immf + pontos_proporcao
    pontos_maximos = PONTOS_MAX_ALTURA + PONTOS_MAX_GORDURA + PONTOS_MAX_IMMF + PONTOS_MAX_PROPORCAO
    potencial_estetico = (pontos_totais / pontos_maximos) * 100

    dados_formatacao = {
        'immf': immf,
        'proporcao': proporcao_ombro_cintura,
        'pa': pontos_altura,
        'pg': pontos_gordura,
        'pi': pontos_immf,
        'pp': pontos_proporcao,
        'pt': pontos_totais,
        'pm': pontos_maximos,
        'percentual': potencial_estetico
    }
    return dados_formatacao, None

def mostrar_explicacao():
    """Exibe o texto de ajuda quando o botão de interrogação é clicado."""
    messagebox.showinfo("Algoritmo de Pontuação", TEXTO_EXPLICACAO)

def calcular_e_exibir():
    """Função chamada pelo botão para pegar dados e mostrar o resultado."""
    try:
        altura_cm = formatar_float(entradas['altura'].get())
        peso = formatar_float(entradas['peso'].get())
        percentual_gordura = formatar_float(entradas['gordura'].get())
        largura_ombro = formatar_float(entradas['ombro'].get())
        largura_cintura = formatar_float(entradas['cintura'].get())

        if any(v < 0 for v in [altura_cm, peso, percentual_gordura, largura_ombro, largura_cintura]):
            messagebox.showerror("Erro de Entrada", "Valores não podem ser negativos.")
            return

        altura_m = altura_cm / 100.0

        dados_calculo, erro = calcular_pontos(altura_m, peso, percentual_gordura, largura_ombro, largura_cintura)
        if erro:
            messagebox.showerror("Erro de Cálculo", erro)
            return

        percentual = dados_calculo['percentual']
        classificacao = classificar_potencial(percentual)
        pontos_max_total = dados_calculo['pm']

        resultado_formatado = (
            f"##### RESULTADO #####\n"
            f"\n"
            f"IMMF: {dados_calculo['immf']:.2f} | Proporção O/C: {dados_calculo['proporcao']:.2f}\n"
            f"\n"
            f"Pontuação Altura: {dados_calculo['pa']:.2f} / 2.00\n"
            f"Pontuação Gordura: {dados_calculo['pg']:.2f} / 3.00\n"
            f"Pontuação IMMF: {dados_calculo['pi']:.2f} / 3.00\n"
            f"Pontuação Proporção: {dados_calculo['pp']:.2f} / 2.00\n"
            f"\n"
            f"Pontuação Total VSM: {percentual:.2f}% ({dados_calculo['pt']:.2f} / {pontos_max_total:.2f})\n"
            f"\n"
            f"CLASSIFICAÇÃO: {classificacao}"
        )

        entradas['resultado_label'].config(text=resultado_formatado)

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira números válidos em todos os campos.")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def criar_interface():
    """Configura e exibe a janela principal do Tkinter."""
    global entradas

    janela = tk.Tk()
    janela.title("Calculadora de VSM")  # título solicitado
    janela.geometry("480x500")

    padx_val, pady_val = 10, 5

    # --- Título com Botão de Ajuda ---
    frame_titulo = tk.Frame(janela)
    frame_titulo.grid(row=0, column=0, columnspan=2, pady=5)

    tk.Label(frame_titulo, text="CALCULADORA DE POTENCIAL").pack(side=tk.LEFT)
    tk.Button(frame_titulo, text="❓", command=mostrar_explicacao, width=2).pack(side=tk.LEFT, padx=5)

    # --- Widgets de Entrada de Dados ---
    tk.Label(janela, text="Altura (cm):").grid(row=1, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['altura'] = tk.Entry(janela)
    entradas['altura'].grid(row=1, column=1, padx=padx_val, pady=pady_val)

    tk.Label(janela, text="Peso (kg):").grid(row=2, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['peso'] = tk.Entry(janela)
    entradas['peso'].grid(row=2, column=1, padx=padx_val, pady=pady_val)

    tk.Label(janela, text="% Gordura:").grid(row=3, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['gordura'] = tk.Entry(janela)
    entradas['gordura'].grid(row=3, column=1, padx=padx_val, pady=pady_val)

    tk.Label(janela, text="Largura do Ombro (cm):").grid(row=4, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['ombro'] = tk.Entry(janela)
    entradas['ombro'].grid(row=4, column=1, padx=padx_val, pady=pady_val)

    tk.Label(janela, text="Largura da Cintura (cm):").grid(row=5, column=0, padx=padx_val, pady=pady_val, sticky='w')
    entradas['cintura'] = tk.Entry(janela)
    entradas['cintura'].grid(row=5, column=1, padx=padx_val, pady=pady_val)

    # --- Botão de Cálculo ---
    tk.Button(janela, text="CALCULAR POTENCIAL", command=calcular_e_exibir,
              bg='#4CAF50', fg='white').grid(row=6, column=0, columnspan=2, padx=padx_val, pady=15)

    # --- Label para Mostrar o Resultado ---
    entradas['resultado_label'] = tk.Label(
        janela, text="Aguardando dados...", justify=tk.LEFT, fg='blue', font=('Courier', 10)
    )
    entradas['resultado_label'].grid(row=7, column=0, columnspan=2, padx=padx_val, pady=pady_val)

    janela.mainloop()

# iniciar
criar_interface()

