# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) em Python para a
fábrica fictícia Pedal Forte Bicicletas, desenvolvido na disciplina de
Programação em Python (CEFET-MG, Campus Divinópolis).

O sistema responde, a cada execução: **o que produzir ou comprar, quanto,
quando e se há capacidade para isso.**

## Como executar

Requisitos: Python 3.10 ou superior (testado no Linux) e, para os gráficos,
`matplotlib`.

```
git clone https://github.com/guilherme1921/MRP2_PedalForte.git
cd MRP2_PedalForte
pip install matplotlib
python main.py
```

Os dados são carregados automaticamente da pasta `data/` ao iniciar e gravados
a cada operação (RF15). A pasta já traz a base de demonstração (2 PA, 3 SA,
9 MP e 4 centros de trabalho).

## Requisitos implementados

| Requisito | Onde | Menu |
|---|---|---|
| RF01 menu principal | `menu.py` | - |
| RF02 itens (cadastrar, listar, alterar) | `itens.py` | 1 |
| RF03 estrutura (BOM) e árvore indentada | `estrutura.py` | 1 |
| RF04 movimentações de estoque | `estoque.py` | 2 |
| RF05 saldo, kardex e alerta de segurança | `estoque.py` | 2 |
| RF06 centros de trabalho e roteiros | `capacidade.py` | 1 |
| RF07 MPS (8 semanas) | `mps.py` | 3 |
| RF08 cálculo e registro MRP | `mrp.py` | 4 |
| RF09 geração de OP e OC | `ordens.py` | 4 |
| RF10 firmar, liberar e encerrar ordens | `ordens.py` | 5 |
| RF11 apontamento de produção | `ordens.py` | 5 |
| RF12 carga x capacidade (CRP) | `capacidade.py` | 6 |
| RF13 custo padrão (recursivo) | `custos.py` | 7 |
| RF14 exportação CSV | `relatorios.py` | 8 |
| RF15 persistência em `data/` | `persistencia.py` | automático |
| RF16 gráficos (matplotlib) | `graficos.py` | 8 |

## Instruções de uso (ciclo completo)

1. **MPS (3):** lance a demanda semanal dos produtos acabados.
2. **Executar MRP (4):** calcula todos os itens, apaga as ordens planejadas
   antigas e gera as novas. Digite o código de um item para ver o registro MRP.
3. **Ordens (5):** `F` firma, `L` libera, `A` aponta a produção de uma OP
   liberada (baixa os componentes e dá entrada no produzido) e `R` recebe uma
   OC liberada. `T` mostra ou esconde as ordens encerradas.
4. **Estoque (2) e CRP (6):** confira o kardex atualizado e as semanas com
   sobrecarga. **Custo (7)** mostra o custo padrão de um item fabricado.
5. **Relatórios (8):** CSV e gráficos PNG, salvos em `data/`.

## Decisões de projeto

- **Regra na classe, tela só conversa:** as classes levantam `ValueError`; as
  telas de `menu.py` capturam e mostram `ERRO: ...` (RNF05).
- **Um único ponto de acesso a arquivos:** só `persistencia.py` lê e grava.
- **Dicionários:** itens `{código: Item}`, BOM `{pai: {filho: qtd}}`, MPS
  `{PA: {semana: qtd}}`, roteiros `{item: {centro, tempo}}`.
- **Regra RN03 por tipo:** PA aceita SA e MP; SA aceita só MP. Impede ciclos.
- **Kardex imutável (RN10):** movimentos só são acrescentados; correção por
  ajuste. O saldo é o do último movimento do item.
- **MRP com listas de N posições** (uma por semana), processando PA, SA e MP
  nessa ordem (RN04). Fórmulas: RN05 (necessidade líquida), RN06 (lote mínimo)
  e RN07 (liberação = recebimento - lead time).
- **Ordem ATRASADA:** é o status de uma ordem planejada cuja liberação cai
  antes da semana 1 (RN07). Ela pode ser firmada normalmente.
- **Ordens firmes e dependentes:** FIRME e LIBERADA contam como recebimentos
  programados (RN08) e suas liberações ainda geram necessidade nos componentes.
- **Numeração das ordens:** contadores gravados em `ordens.json`; um número
  nunca é reaproveitado, mesmo quando as planejadas são apagadas.
- **CRP:** a carga de uma semana soma qtd x tempo unitário das OPs ainda não
  encerradas cuja liberação cai naquela semana (RN09).

## Estrutura do projeto

```
MRP2_PedalForte/
├── main.py          # ponto de entrada e carga/gravação dos dados
├── menu.py          # menus e telas
├── itens.py         # cadastro de itens
├── estrutura.py     # BOM e árvore indentada
├── estoque.py       # movimentações, saldo e kardex
├── mps.py           # plano mestre de produção
├── mrp.py           # cálculo MRP
├── ordens.py        # OPs, OCs, status e apontamento
├── capacidade.py    # centros, roteiros e CRP
├── custos.py        # custo padrão
├── relatorios.py    # exportação CSV
├── graficos.py      # gráficos (matplotlib)
├── persistencia.py  # leitura e gravação de arquivos
├── utils.py         # validações e formatação
└── data/            # base de demonstração (JSON e CSV)
```

## Autor

Guilherme Maia Mascarenhas - CEFET-MG
