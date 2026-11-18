"""Leitura e gravação de arquivos JSON e CSV na pasta data/."""

import csv
import json
import os

PASTA_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _caminho(nome_arquivo):
    """Monta o caminho do arquivo e cria a pasta data/ se não existir."""
    os.makedirs(PASTA_DATA, exist_ok=True)
    return os.path.join(PASTA_DATA, nome_arquivo)


def carregar_json(nome_arquivo, padrao=None):
    """Lê um JSON; se o arquivo não existir ou estiver corrompido, devolve o padrão."""
    if padrao is None:
        padrao = {}
    caminho = _caminho(nome_arquivo)
    if not os.path.exists(caminho):
        return padrao
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        print(f"AVISO: não foi possível ler {nome_arquivo}. Usando dados vazios.")
        return padrao


def salvar_json(nome_arquivo, dados):
    """Grava os dados em JSON com acentos preservados e indentação."""
    with open(_caminho(nome_arquivo), "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar_csv(nome_arquivo):
    """Lê um CSV e devolve uma lista de dicionários (uma por linha)."""
    caminho = _caminho(nome_arquivo)
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def salvar_csv(nome_arquivo, linhas, campos):
    """Grava uma lista de dicionários em CSV, usando 'campos' como cabeçalho."""
    with open(_caminho(nome_arquivo), "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)