"""Cálculo do Planejamento das Necessidades de Materiais (MRP)."""
import math

class MRP:
    """Calcula necessidades brutas, saldos projetados e necessidades líquidas por semana."""
    def __init__(self, cadastro_itens, estrutura, estoque, mps):
        """Inicializa o MRP com as dependências principais do sistema."""
        self.cadastro_itens = cadastro_itens
        self.estrutura = estrutura
        self.estoque = estoque
        self.mps = mps

def calcular(self):
        """Calcula necessidades brutas, projetadas e líquidas por item e semana."""
        semanas = self.mps.semanas
        necessidade_bruta = {}

        for codigo_pa, demandas_semana in self.mps.plano.items():
            for semana_str, qtd_demanda in demandas_semana.items():
                semana = int(semana_str)
                qtd = float(qtd_demanda)
                if semana < 1 or semana > semanas or qtd <= 0:
                    continue

                explosao = self.estrutura.explodir(codigo_pa, quantidade_pai=qtd)
                for no in explosao:
                    cod = no["codigo"]
                    qtd_no = float(no["quantidade"])
                    necessidade_bruta.setdefault(cod, {s: 0.0 for s in range(1, semanas + 1)})
                    necessidade_bruta[cod][semana] += qtd_no

        itens_ordenados = sorted(necessidade_bruta.keys())
        resultado = {}

        for cod in itens_ordenados:
            saldo_atual = float(self.estoque.saldo(cod)) if self.estoque else 0.0
            estoque_seg = 0.0
            lead_time = 0

            if self.cadastro_itens and cod in self.cadastro_itens.itens:
                item = self.cadastro_itens.itens[cod]
                estoque_seg = float(getattr(item, "estoque_seguranca", 0.0))
                lead_time = max(0, int(getattr(item, "lead_time", 0)))

            saldo_disponivel = max(0.0, saldo_atual - estoque_seg)
            projecao_estoque = {}
            necessidade_liquida = {}
            liberacao_planejada = {}

            for sem in range(1, semanas + 1):
                bruta = necessidade_bruta[cod][sem]
                consumo_estoque = min(saldo_disponivel, bruta)
                saldo_disponivel -= consumo_estoque
                liquida = max(0.0, bruta - consumo_estoque)

                projecao_estoque[sem] = saldo_disponivel + estoque_seg
                necessidade_liquida[sem] = liquida
                liberacao_planejada[sem] = 0.0

            for sem in range(1, semanas + 1):
                liq = necessidade_liquida[sem]
                if liq > 0:
                    sem_liberacao = max(1, sem - lead_time)
                    liberacao_planejada[sem_liberacao] += liq

            resultado[cod] = {
                "saldo_inicial": saldo_atual,
                "estoque_seguranca": estoque_seg,
                "lead_time": lead_time,
                "necessidade_bruta": necessidade_bruta[cod],
                "necessidade_liquida": necessidade_liquida,
                "liberacao_planejada": liberacao_planejada,
                "projecao_estoque": projecao_estoque,
            }

        return resultado

def resumo_tabela(self, resultado=None):
        """Formata um resumo textual semana a semana das necessidades do MRP."""
        dados = resultado if resultado is not None else self.calcular()
        if not dados:
            return "Nenhuma necessidade calculada no MRP."

        semanas = self.mps.semanas
        cabecalho_semanas = " | ".join(f"S{s}" for s in range(1, semanas + 1))
        linhas = []

        for codigo, info in dados.items():
            linhas.append(
                f"{codigo} (Saldo: {info['saldo_inicial']:g}, "
                f"ES: {info['estoque_seguranca']:g}, LT: {info['lead_time']}s)"
            )
            linhas.append(f"  Semanas : {cabecalho_semanas}")
            linhas.append(
                "  Bruta   : "
                + " | ".join(f"{info['necessidade_bruta'][s]:g}" for s in range(1, semanas + 1))
            )
            linhas.append(
                "  Líquida : "
                + " | ".join(f"{info['necessidade_liquida'][s]:g}" for s in range(1, semanas + 1))
            )
            linhas.append(
                "  Liberar : "
                + " | ".join(f"{info['liberacao_planejada'][s]:g}" for s in range(1, semanas + 1))
            )

        return "\n".join(linhas)