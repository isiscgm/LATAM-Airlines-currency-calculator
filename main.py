import requests
import tkinter as tk
from tkinter import ttk
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def obter_cotacao_dolar():
    api_key = "fca_live_IVciBYaGzJLOC8OrfLbwoxUbcXzdCIn8PPYyOaCZ"  
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&currencies=BRL&base_currency=USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        cotacao = data["data"]["BRL"]
        return cotacao
    except Exception as e:
        print("Erro ao obter cotação do dólar:", e)
        return None

# Valores fixos nacionais
VALOR_ALMOCO = 77.63
VALOR_JANTA = 77.63

# Valores fixos internacionais (USD)
valores_internacionais = {
    "Argentina": 30, "Bolívia": 30, "Chile": 40, "Colômbia": 30, "Equador": 30,
    "Paraguai": 30, "Peru": 30, "Uruguai": 30, "Venezuela": 30, "Outros da América do Sul": 30,
    "República Dominicana": 40,
    "Canadá": 50, "EUA": 60, "México": 40,
    "Alemanha": 62, "Espanha": 62, "França": 62, "Inglaterra": 62, "Outros da Europa": 62,
    "Austrália": 70, "Nova Zelândia": 45, "Taiti": 90,
    "Hong Kong": 73, "Outros da Ásia": 73,
    "Toda África": 73
}

def calcular_valor():
    tipo = tipo_viagem.get()
    periodo = periodo_var.get()
    quantidade = quantidade_entry.get()

    try:
        quantidade = int(quantidade)
    except ValueError:
        resultado_var.set("Insira um número válido.")
        return

    total_dias = quantidade if periodo == "Dias" else quantidade * 30

    if tipo == "Nacional":
        incluir_cafe = cafe_check.get()
        valor_diario = VALOR_ALMOCO + VALOR_JANTA
        detalhes = f"almoço = R$ {VALOR_ALMOCO:.2f}\njanta = R$ {VALOR_JANTA:.2f}"
        if incluir_cafe:
            valor_diario += 19.40
            detalhes += "\ncafé = R$ 19.40"
        total = valor_diario * total_dias

        resumo = (
            f"Tipo de viagem: {tipo}\n"
            f"Período: {quantidade} {periodo.lower()} ({total_dias} dias)\n"
            f"Valor diário (alimentação): R$ {valor_diario:.2f}\n"
            f"====================\nVALORES FIXOS:\n{detalhes}\n====================\n"
            f"Total estimado: R$ {total:.2f}"
        )
        resultado_var.set(resumo)

    else:  # Internacional
        pais = pais_combo.get()
        valor_base = valores_internacionais.get(pais, 0)
        total = valor_base * total_dias
        detalhes = [f"Diária para {pais}: USD {valor_base:.2f}"]

        if cafe_check_internacional.get():
            total += 10 * total_dias
            detalhes.append("Café da manhã: USD 10/dia")

        if lavanderia_check.get():
            dias_lavagem = (total_dias // 5) + (1 if total_dias % 5 != 0 else 0)
            total += dias_lavagem * 30
            detalhes.append(f"Lavanderia: USD 30 a cada 5 dias ({dias_lavagem}x)")

        if telefonia_check.get():
            total += 10 * total_dias
            detalhes.append("Telefonia: USD 10/dia")

        valor_aluguel = 0
        aluguel_detalhe = ""
        if pais == "EUA" and aluguel_carro_check.get():
            tipo_aluguel = tipo_aluguel_combo.get()
            if tipo_aluguel == "MIA":
                valor_aluguel = 100 * total_dias
                aluguel_detalhe = "Aluguel de carro (MIA): USD 100/dia"
            elif tipo_aluguel in ["NYC", "LAX"]:
                valor_aluguel = 130 * total_dias
                aluguel_detalhe = "Aluguel de carro (NYC/LAX): USD 130/dia"
            else:
                valor_aluguel = 80 * total_dias
                aluguel_detalhe = "Aluguel de carro (OUTROS): USD 80/dia"

        total_geral = total + valor_aluguel

        # Conversão para reais
        cotacao = obter_cotacao_dolar()
        if cotacao:
            valor_em_reais = total_geral * cotacao
            conversao_texto = f"\nConversão estimada em reais (USD 1 = R$ {cotacao:.2f}):\nR$ {valor_em_reais:.2f}"
        else:
            conversao_texto = "\nConversão indisponível no momento."

        resumo = (
            f"Tipo de viagem: {tipo}\n"
            f"País: {pais}\n"
            f"Período: {quantidade} {periodo.lower()} ({total_dias} dias)\n"
            f"====================\n" +
            "\n".join(detalhes) +
            f"\n====================\nTotal estimado: USD {total:.2f}"
        )

        if valor_aluguel > 0:
            resumo += (
                f"\n\n===== Aluguel de Carro =====\n"
                f"{aluguel_detalhe}\n"
                f"Valor: USD {valor_aluguel:.2f}"
                f"\n============================"
            )

        resumo += conversao_texto

        resultado_var.set(resumo)

def alternar_opcoes(*args):
    tipo = tipo_viagem.get()
    if tipo == "Nacional":
        frame_nacional.pack(fill="x", pady=5)
        frame_internacional.pack_forget()
    else:
        frame_internacional.pack(fill="x", pady=5)
        frame_nacional.pack_forget()

def alternar_tipo_aluguel():
    if aluguel_carro_check.get():
        tipo_aluguel_label.pack(anchor="w")
        tipo_aluguel_combo.pack(fill="x", pady=(0,10))
    else:
        tipo_aluguel_label.pack_forget()
        tipo_aluguel_combo.pack_forget()

# ===== INTERFACE =====
root = tk.Tk()
root.title("Calculadora de Viagem LATAM")
root.geometry("500x600")

# Logo
logo_path = resource_path("Latam-logo_.png")
logo_img = tk.PhotoImage(file=logo_path)
logo_label = tk.Label(root, image=logo_img)
logo_label.pack(pady=10)

# Tipo de viagem
tk.Label(root, text="Tipo de Viagem:").pack()
tipo_viagem = ttk.Combobox(root, values=["Nacional", "Internacional"], state="readonly")
tipo_viagem.pack()
tipo_viagem.current(0)
tipo_viagem.bind("<<ComboboxSelected>>", alternar_opcoes)

# Período
tk.Label(root, text="Escolha o período:").pack()
periodo_var = ttk.Combobox(root, values=["Dias", "Meses"], state="readonly")
periodo_var.pack()
periodo_var.current(0)

# Quantidade
tk.Label(root, text="Quantidade:").pack()
quantidade_entry = tk.Entry(root)
quantidade_entry.pack()

# Container para opções e botão calcular
frame_opcoes = tk.Frame(root)
frame_opcoes.pack(fill="x", pady=5)

# Grupo Nacional
frame_nacional = tk.Frame(frame_opcoes)
frame_nacional.pack(fill="x", pady=5)

cafe_check = tk.BooleanVar(value=True)
tk.Checkbutton(frame_nacional, text="Incluir Café da Manhã (Nacional)", variable=cafe_check).pack(pady=5)

# Grupo Internacional
frame_internacional = tk.Frame(frame_opcoes)

tk.Label(frame_internacional, text="País de destino (Internacional):").pack(anchor="w")
pais_combo = ttk.Combobox(frame_internacional, values=list(valores_internacionais.keys()), state="readonly")
pais_combo.pack(fill="x")
pais_combo.set("EUA")

cafe_check_internacional = tk.BooleanVar()
tk.Checkbutton(frame_internacional, text="Incluir Café da Manhã (USD 10/dia)", variable=cafe_check_internacional).pack(anchor="w")

lavanderia_check = tk.BooleanVar()
tk.Checkbutton(frame_internacional, text="Incluir Lavanderia (USD 30/5 dias)", variable=lavanderia_check).pack(anchor="w")

telefonia_check = tk.BooleanVar()
tk.Checkbutton(frame_internacional, text="Incluir Telefonia (USD 10/dia)", variable=telefonia_check).pack(anchor="w")

aluguel_carro_check = tk.BooleanVar()
tk.Checkbutton(frame_internacional, text="Incluir Aluguel de Carro (EUA)", variable=aluguel_carro_check, command=alternar_tipo_aluguel).pack(anchor="w")

tipo_aluguel_label = tk.Label(frame_internacional, text="Tipo de Aluguel de Carro (se EUA):")
tipo_aluguel_combo = ttk.Combobox(frame_internacional, values=["MIA", "NYC", "LAX", "OUTROS"], state="readonly")
tipo_aluguel_combo.set("MIA")

# Botão calcular
btn_calcular = tk.Button(frame_opcoes, text="Calcular", command=calcular_valor)
btn_calcular.pack(pady=10)

# Resultado
resultado_var = tk.StringVar()
tk.Label(root, textvariable=resultado_var, justify="left", font=("Arial", 10)).pack(pady=10)

# Rodapé
rodape = tk.Label(root, text="by: Isis Cagliumi", font=("Arial", 8), fg="gray")
rodape.pack(side="bottom", pady=10)

# Inicializações
alternar_opcoes()
alternar_tipo_aluguel()

root.mainloop()
