"""Funções de validação e formatação usadas em todo o sistema."""

import re

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