"""Gerenciamento do Plano Mestre de Produção (MPS) por semana."""

from persistencia import carregar_json, salvar_json


class MPS:
    """Armazena e valida a demanda semanal de produtos acabados (PA)."""

    def __init__(self, cadastro_itens=None, semanas=8, plano=None):
        """Inicializa o MPS com horizonte em semanas e estrutura {codigo_pa: {semana: qtd}}."""
        self.cadastro_itens = cadastro_itens
        self.semanas = int(semanas)
        if self.semanas <= 0:
            raise ValueError("O horizonte em semanas deve ser maior que zero.")
        self.plano = {}
        if plano:
            for codigo_pa, demandas in plano.items():
                for semana, quantidade in demandas.items():
                    self.definir_demanda(codigo_pa, semana, quantidade)

    def definir_demanda(self, codigo_pa, semana, quantidade):
        """Define ou atualiza a demanda de um produto acabado (PA) em uma semana."""
        codigo = str(codigo_pa).strip().upper()
        sem = int(semana)
        qtd = float(quantidade)

        if not codigo:
            raise ValueError("O código do produto acabado é obrigatório.")
        if sem < 1 or sem > self.semanas:
            raise ValueError(
                f"A semana {sem} está fora do horizonte de 1 a {self.semanas} semanas."
            )
        if qtd < 0:
            raise ValueError("A demanda não pode ser negativa.")

        if self.cadastro_itens is not None:
            item = self.cadastro_itens.obter(codigo)
            if item.tipo != "PA":
                raise ValueError(
                    f"Apenas itens do tipo PA podem entrar no MPS. {codigo} é do tipo {item.tipo}."
                )
        elif not codigo.startswith("PA"):
            raise ValueError(
                f"Apenas itens do tipo PA podem entrar no MPS. Código recebido: {codigo}."
            )

        if codigo not in self.plano:
            self.plano[codigo] = {}
        self.plano[codigo][sem] = qtd

    def obter_demanda(self, codigo_pa, semana):
        """Retorna a demanda de um produto acabado em uma semana específica."""
        codigo = str(codigo_pa).strip().upper()
        sem = int(semana)
        if sem < 1 or sem > self.semanas:
            raise ValueError(
                f"A semana {sem} está fora do horizonte de 1 a {self.semanas} semanas."
            )
        return float(self.plano.get(codigo, {}).get(sem, 0.0))

    def remover_demanda(self, codigo_pa, semana):
        """Remove o lançamento de demanda de um PA em uma semana específica."""
        codigo = str(codigo_pa).strip().upper()
        sem = int(semana)
        if codigo not in self.plano or sem not in self.plano[codigo]:
            raise ValueError(f"Demanda não encontrada para {codigo} na semana {sem}.")
        del self.plano[codigo][sem]
        if not self.plano[codigo]:
            del self.plano[codigo]

    def alterar_horizonte(self, novas_semanas):
        """Atualiza o horizonte em semanas e remove demandas fora do novo limite."""
        limite = int(novas_semanas)
        if limite <= 0:
            raise ValueError("O horizonte em semanas deve ser maior que zero.")
        self.semanas = limite
        for codigo in list(self.plano.keys()):
            self.plano[codigo] = {
                sem: qtd for sem, qtd in self.plano[codigo].items() if sem <= limite
            }
            if not self.plano[codigo]:
                del self.plano[codigo]

    def salvar(self, arquivo="mps.json"):
        """Grava o horizonte em semanas e o plano de demanda em JSON."""
        dados = {
            "semanas": self.semanas,
            "plano": self.plano,
        }
        salvar_json(arquivo, dados)

    def carregar(self, arquivo="mps.json"):
        """Carrega o horizonte em semanas e o plano de demanda a partir de JSON."""
        dados = carregar_json(arquivo, {"semanas": self.semanas, "plano": {}})
        semanas_salvas = int(dados.get("semanas", self.semanas))
        if semanas_salvas <= 0:
            raise ValueError("O horizonte em semanas salvo no arquivo é inválido.")

        self.semanas = semanas_salvas
        self.plano.clear()

        plano_salvo = dados.get("plano", {})
        for codigo_pa, demandas in plano_salvo.items():
            for semana, quantidade in demandas.items():
                self.definir_demanda(codigo_pa, semana, quantidade)