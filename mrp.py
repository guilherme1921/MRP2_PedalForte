"""Cálculo do MRP: necessidades, recebimentos e liberações por semana."""

from ordens import STATUS_RECEBIMENTO
from utils import formatar_numero

ORDEM_TIPOS = ("PA", "SA", "MP")
LINHAS_REGISTRO = (
    ("Necessidade bruta", "necessidade_bruta"),
    ("Receb. programados", "recebimentos_programados"),
    ("Estoque projetado", "estoque_projetado"),
    ("Necessidade liquida", "necessidade_liquida"),
    ("Receb. planejados", "recebimentos_planejados"),
    ("Liberacao planejada", "liberacoes_planejadas"),
)


class MRP:
    """Calcula o registro MRP de cada item, processando PA, SA e MP em ordem."""

    def __init__(self, cadastro_itens, estrutura, estoque, mps, ordens):
        """Guarda os módulos dos quais o cálculo depende."""
        self.cadastro_itens = cadastro_itens
        self.estrutura = estrutura
        self.estoque = estoque
        self.mps = mps
        self.ordens = ordens

    def _recebimentos_programados(self, codigo, semanas):
        """RN08: soma, por semana de entrega, as ordens FIRMES e LIBERADAS."""
        programados = [0.0] * semanas
        for ordem in self.ordens.ordens_do_item(codigo):
            if ordem.status not in STATUS_RECEBIMENTO:
                continue
            if 1 <= ordem.semana_entrega <= semanas:
                programados[ordem.semana_entrega - 1] += ordem.quantidade
        return programados

    def _liberacoes_firmes(self, codigo, semanas):
        """Soma, por semana de liberação, as ordens FIRMES e LIBERADAS."""
        liberacoes = [0.0] * semanas
        for ordem in self.ordens.ordens_do_item(codigo):
            if ordem.status not in STATUS_RECEBIMENTO:
                continue
            if 1 <= ordem.semana_liberacao <= semanas:
                liberacoes[ordem.semana_liberacao - 1] += ordem.quantidade
        return liberacoes

    def _necessidade_bruta(self, item, semanas, registros):
        """RN04: demanda do MPS (PA) ou liberações dos pais x quantidade (SA, MP)."""
        bruta = [0.0] * semanas
        if item.tipo == "PA":
            for semana in range(1, semanas + 1):
                bruta[semana - 1] = self.mps.obter_demanda(item.codigo, semana)
            return bruta

        for pai, componentes in self.estrutura.bom.items():
            if item.codigo not in componentes or pai not in registros:
                continue
            quantidade_por_unidade = componentes[item.codigo]
            planejadas = registros[pai]["liberacoes_planejadas"]
            firmes = self._liberacoes_firmes(pai, semanas)
            for i in range(semanas):
                bruta[i] += (planejadas[i] + firmes[i]) * quantidade_por_unidade
        return bruta

    def _calcular_item(self, item, semanas, bruta):
        """Aplica RN05, RN06 e RN07 semana a semana e monta o registro do item."""
        saldo_inicial = self.estoque.saldo(item.codigo)
        programados = self._recebimentos_programados(item.codigo, semanas)

        projetado = []
        liquida = []
        planejados = []
        liberacoes = [0.0] * semanas
        ordens_planejadas = []
        estoque_anterior = saldo_inicial

        for i in range(semanas):
            semana = i + 1
            disponivel = estoque_anterior + programados[i]
            necessidade = max(
                0.0, bruta[i] + item.estoque_seguranca - disponivel
            )
            recebimento = 0.0
            if necessidade > 1e-9:
                recebimento = max(necessidade, item.lote_minimo)
            estoque_atual = disponivel + recebimento - bruta[i]

            if recebimento > 0:
                semana_liberacao = semana - item.lead_time
                if semana_liberacao >= 1:
                    liberacoes[semana_liberacao - 1] += recebimento
                ordens_planejadas.append(
                    {
                        "quantidade": recebimento,
                        "semana_entrega": semana,
                        "semana_liberacao": semana_liberacao,
                    }
                )

            liquida.append(necessidade)
            planejados.append(recebimento)
            projetado.append(estoque_atual)
            estoque_anterior = estoque_atual

        return {
            "codigo": item.codigo,
            "estoque_inicial": saldo_inicial,
            "necessidade_bruta": bruta,
            "recebimentos_programados": programados,
            "estoque_projetado": projetado,
            "necessidade_liquida": liquida,
            "recebimentos_planejados": planejados,
            "liberacoes_planejadas": liberacoes,
            "ordens_planejadas": ordens_planejadas,
        }

    def calcular(self):
        """RN04: processa PA, depois SA, depois MP, e devolve {código: registro}."""
        semanas = self.mps.semanas
        registros = {}
        for tipo in ORDEM_TIPOS:
            for item in self.cadastro_itens.listar(tipo):
                bruta = self._necessidade_bruta(item, semanas, registros)
                registros[item.codigo] = self._calcular_item(item, semanas, bruta)
        return registros

    def formatar_registro(self, registro):
        """Gera o texto do registro MRP de um item, semana a semana."""
        item = self.cadastro_itens.obter(registro["codigo"])
        semanas = len(registro["necessidade_bruta"])
        linhas = [
            f"REGISTRO MRP - {item.codigo} {item.descricao}",
            f"Lead time: {item.lead_time} sem | "
            f"Est. seguranca: {formatar_numero(item.estoque_seguranca)} | "
            f"Lote min.: {formatar_numero(item.lote_minimo)} | "
            f"Estoque: {formatar_numero(registro['estoque_inicial'])}",
            "",
            "Semana".ljust(20)
            + "".join(f"{semana:>8}" for semana in range(1, semanas + 1)),
        ]
        for rotulo, chave in LINHAS_REGISTRO:
            valores = "".join(
                f"{formatar_numero(valor):>8}" for valor in registro[chave]
            )
            linhas.append(rotulo.ljust(20) + valores)
        return "\n".join(linhas)
