"""Funções de validação e formatação usadas em todo o sistema."""

import re

PADRAO_CODIGO = re.compile(r"^(PA|SA|MP)-\d{3}$")


def codigo_valido(codigo):
    """Retorna True se o código segue o formato Tipo-Número (ex.: PA-001)."""
    return bool(PADRAO_CODIGO.match(codigo.strip().upper()))


def ler_texto(mensagem):
    """Lê um texto não vazio."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("ERRO: o campo não pode ficar vazio.")


def ler_codigo(mensagem):
    """Lê um código de item válido (ex.: PA-001) e o devolve em maiúsculas."""
    while True:
        valor = ler_texto(mensagem).upper()
        if codigo_valido(valor):
            return valor
        print("ERRO: código inválido. Use o formato PA-001, SA-010 ou MP-201.")


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


def formatar_numero(valor, casas=2):
    """Formata um número com vírgula decimal e sem zeros inúteis (0,5; 30)."""
    texto = f"{valor:.{casas}f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def formatar_fixo(valor, casas=2):
    """Formata um número com vírgula e número fixo de casas (15,0; 128,00)."""
    return f"{valor:.{casas}f}".replace(".", ",")


def formatar_moeda(valor):
    """Formata um valor em reais no padrão brasileiro (R$ 1.234,56)."""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
