"""Leitura e gravação de arquivos: único ponto de acesso à pasta data/."""

import csv
import json
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent / "data"

def caminho_arquivo(nome):
    """Devolve o caminho de um arquivo dentro de data/, criando a pasta."""
    PASTA_DADOS.mkdir(exist_ok=True)
    return PASTA_DADOS / nome

def carregar_json(nome, padrao):
    """Lê um arquivo JSON; se ele não existir, devolve o valor padrão."""
    caminho = caminho_arquivo(nome)
    if not caminho.exists():
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError:
        raise ValueError(f"o arquivo {nome} está corrompido ou mal formatado.")

def salvar_json(nome, dados):
    """Grava dados (dicionário ou lista) em um arquivo JSON legível."""
    caminho = caminho_arquivo(nome)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

def carregar_csv(nome):
    """Lê um CSV separado por ponto e vírgula e devolve lista de dicionários."""
    caminho = caminho_arquivo(nome)
    if not caminho.exists():
        return []
    with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))

def salvar_csv(nome, campos, linhas):
    """Grava uma lista de dicionários em CSV, com ; como separador."""
    caminho = caminho_arquivo(nome)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)