"""Funções de validação e formatação usadas em todo o sistema."""

import re
from datetime import datetime

PADRAO_CODIGO = re.compile(r"^(PA|SA|MP)-\d{3}$")


def codigo_valido(codigo):
    """Retorna True se o código segue o formato Tipo-Número (ex.: PA-001)."""
    return bool(PADRAO_CODIGO.match(codigo))


def ler_texto(mensagem):
    """Lê um texto não vazio."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("ERRO: o campo não pode ficar vazio.")


def ler_float(mensagem, minimo=0.0):
    """Lê um número decimal maior ou igual ao mínimo (aceita vírgula)."""
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
        except ValueError:
            print("ERRO: digite um número válido.")
            continue
        if valor < minimo:
            print(f"ERRO: o valor deve ser maior ou igual a {minimo}.")
            continue
        return valor


def ler_inteiro(mensagem, minimo=0):
    """Lê um número inteiro maior ou igual ao mínimo."""
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("ERRO: digite um número inteiro.")
            continue
        if valor < minimo:
            print(f"ERRO: o valor deve ser maior ou igual a {minimo}.")
            continue
        return valor


def formatar_moeda(valor):
    """Formata um número como moeda brasileira: 1234.5 -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def data_hoje():
    """Retorna a data de hoje no formato dd/mm/aaaa."""
    return datetime.now().strftime("%d/%m/%Y")