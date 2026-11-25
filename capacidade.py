"""Centros de trabalho, roteiros de operação e carga x capacidade (CRP)."""

import re
from persistencia import carregar_json, salvar_json
from utils import formatar_fixo

PADRAO_CENTRO = re.compile(r"^CT-\d{2}$")


class CentroTrabalho:
    """Representa um centro de trabalho com capacidade e custo-hora."""

    def __init__(self, codigo, descricao, capacidade_horas, custo_hora):
        """Valida os dados e cria o centro (ex.: CT-03)."""
        codigo_limpo = str(codigo).strip().upper()
        descricao_limpa = str(descricao).strip()

        if not PADRAO_CENTRO.match(codigo_limpo):
            raise ValueError("Código de centro inválido. Use o formato CT-01.")
        if not descricao_limpa:
            raise ValueError("A descrição do centro não pode ficar vazia.")
        if float(capacidade_horas) <= 0:
            raise ValueError("A capacidade deve ser maior que zero.")
        if float(custo_hora) < 0:
            raise ValueError("O custo-hora não pode ser negativo.")

        self.codigo = codigo_limpo
        self.descricao = descricao_limpa
        self.capacidade_horas = float(capacidade_horas)
        self.custo_hora = float(custo_hora)

    def to_dict(self):
        """Converte o centro em dicionário para gravar em JSON."""
        return {
            "codigo": self.codigo,
            "descricao": self.descricao,
            "capacidade_horas": self.capacidade_horas,
            "custo_hora": self.custo_hora,
        }

    @classmethod
    def from_dict(cls, dados):
        """Recria o centro a partir de um dicionário lido do JSON."""
        return cls(
            dados["codigo"],
            dados["descricao"],
            dados["capacidade_horas"],
            dados["custo_hora"],
        )


class Capacidade:
    """Guarda centros e roteiros e calcula a carga x capacidade (CRP)."""

    def __init__(self, cadastro_itens=None):
        """Inicia os dicionários {centro: CentroTrabalho} e {item: roteiro}."""
        self.cadastro_itens = cadastro_itens
        self.centros = {}
        self.roteiros = {}

    def cadastrar_centro(self, centro):
        """Cadastra um centro de trabalho novo."""
        if not isinstance(centro, CentroTrabalho):
            raise ValueError("O objeto informado deve ser um CentroTrabalho.")
        if centro.codigo in self.centros:
            raise ValueError(f"Já existe o centro {centro.codigo}.")
        self.centros[centro.codigo] = centro

    def obter_centro(self, codigo):
        """Devolve o centro com o código informado."""
        codigo_limpo = str(codigo).strip().upper()
        if codigo_limpo not in self.centros:
            raise ValueError(f"Centro {codigo_limpo} não encontrado.")
        return self.centros[codigo_limpo]

    def listar_centros(self):
        """Lista os centros ordenados pelo código."""
        return sorted(self.centros.values(), key=lambda centro: centro.codigo)

    def definir_roteiro(self, codigo_item, codigo_centro, tempo_unitario):
        """RF06: define o centro e o tempo (h/un) de um item fabricado."""
        codigo = str(codigo_item).strip().upper()
        centro = self.obter_centro(codigo_centro)
        if float(tempo_unitario) <= 0:
            raise ValueError("O tempo por unidade deve ser maior que zero.")
        if self.cadastro_itens is not None:
            item = self.cadastro_itens.obter(codigo)
            if item.tipo == "MP":
                raise ValueError("Matéria-prima é comprada e não tem roteiro.")
        self.roteiros[codigo] = {
            "centro": centro.codigo,
            "tempo": float(tempo_unitario),
        }

    def obter_roteiro(self, codigo_item):
        """Devolve o roteiro {centro, tempo} do item, ou None se não houver."""
        return self.roteiros.get(str(codigo_item).strip().upper())

    def calcular_carga(self, gerenciador_ordens, semanas):
        """RN09: carga de cada centro por semana de liberação das OPs."""
        cargas = {codigo: [0.0] * semanas for codigo in self.centros}
        for ordem in gerenciador_ordens.ordens:
            if ordem.tipo != "OP" or ordem.status == "ENCERRADA":
                continue
            roteiro = self.roteiros.get(ordem.codigo_item)
            if roteiro is None:
                continue
            if 1 <= ordem.semana_liberacao <= semanas:
                horas = ordem.quantidade * roteiro["tempo"]
                cargas[roteiro["centro"]][ordem.semana_liberacao - 1] += horas
        return cargas

    def formatar_crp(self, codigo_centro, gerenciador_ordens, semanas):
        """RF12: gera o texto de carga x capacidade de um centro."""
        centro = self.obter_centro(codigo_centro)
        carga = self.calcular_carga(gerenciador_ordens, semanas)[centro.codigo]
        linhas = [
            f"CARGA x CAPACIDADE - {centro.codigo} {centro.descricao} "
            f"({formatar_fixo(centro.capacidade_horas, 1)} h/semana)",
            "Sem Carga(h) Uso(%)",
        ]
        sobrecarregadas = []
        for i, horas in enumerate(carga):
            uso = horas / centro.capacidade_horas * 100
            barra = "#" * round(uso / 10)
            marca = ""
            if horas > centro.capacidade_horas:
                marca = " SOBRECARGA"
                sobrecarregadas.append(str(i + 1))
            linhas.append(
                f"{i + 1:<4}{formatar_fixo(horas, 1):>6}{round(uso):>7} "
                f"{barra}{marca}"
            )
        if sobrecarregadas:
            linhas.append("")
            if len(sobrecarregadas) > 1:
                semanas_texto = (
                    ", ".join(sobrecarregadas[:-1]) + " e " + sobrecarregadas[-1]
                )
            else:
                semanas_texto = sobrecarregadas[0]
            linhas.append(
                "Sugestao: antecipar OPs ou programar hora extra nas semanas "
                + semanas_texto + "."
            )
        return "\n".join(linhas)

    def salvar(self, arquivo_centros="centros.json", arquivo_roteiros="roteiros.json"):
        """Grava centros e roteiros em JSON."""
        salvar_json(
            arquivo_centros, [c.to_dict() for c in self.listar_centros()]
        )
        salvar_json(arquivo_roteiros, self.roteiros)

    def carregar(self, arquivo_centros="centros.json", arquivo_roteiros="roteiros.json"):
        """Carrega centros e roteiros a partir de JSON."""
        self.centros.clear()
        self.roteiros.clear()
        for dados in carregar_json(arquivo_centros, []):
            self.cadastrar_centro(CentroTrabalho.from_dict(dados))
        for codigo, roteiro in carregar_json(arquivo_roteiros, {}).items():
            self.definir_roteiro(codigo, roteiro["centro"], roteiro["tempo"])
