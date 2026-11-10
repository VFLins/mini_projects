import marimo

__generated_with = "0.25.2"
app = marimo.App(
    app_title="Entendendo a transferência de votos entre o primeiro e segundo turno das eleições presidenciais de 2026",
    css_file="theme.css",
)


@app.cell
def _():
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
    import pandas as pd

    from datetime import date
    from pathlib import Path

    return date, np, ticker


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import formulas as f
    import datasets as d
    import graphics as g

    return d, f, g


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Entendendo a transferência de votos entre o primeiro e segundo turno das eleições presidenciais de 2026
    """)
    return


@app.cell
def _(date, mo):
    mo.hstack(
        items=[
            mo.md("Por: [Vitor Lins](https://vitorlins.com.br)"),
            mo.md(f"{date.today().strftime('%d/%m/%Y')}"),
        ],
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    O candidato Flávio Bolsonaro terminou o primeiro turno com uma votação maior que a do seu principal adversário Lula, isto levou os bolsonaristas a acreditar que a vitória no segundo turno seria certa, já que históricamente, o primeiro colocado no primeiro turno sempre acabava ganhando a disputa no segundo turno.

    Depois da derrota, já nos Estados Unidos, Flávio Bolsonaro alegou uma "impossibilidade matemática", que permitiu que o seu adversário Lula ganhasse mais de 10 Milhões de votos do primeiro para o segundo turno. O objetivo desta análise é combinar os dados de votação com os resultados de pesquisas de opinião anteriores às votações para entender se esta transferência é realmente impossível como alegado.
    """)
    return


@app.cell
def _(d):
    votos = d.VoteData()
    if not votos.file_exists:
        votos.ask_download
    return (votos,)


@app.cell
def _(mo, votos):
    mo.stop(
        not votos.file_exists,
        mo.md("Dados de votação não solicitados, pulando..."),
    )

    votos.download()
    votos.load()
    return


@app.cell
def _(mo, votos):
    mo.stop(not hasattr(votos, "df"))
    seg_turno = votos.df.loc[votos.df["NR_TURNO"] == 2]

    _is_valid = seg_turno["NR_VOTAVEL"].isin([13, 22])
    _voted_lula = seg_turno["NR_VOTAVEL"] == 13
    _voted_flavio = seg_turno["NR_VOTAVEL"] == 22

    n_votos = seg_turno["QT_VOTOS"].sum()
    n_votos_validos = seg_turno.loc[_is_valid]["QT_VOTOS"].sum()

    vote_stats = dict(
        lula={
            "n": seg_turno.loc[_voted_lula]["QT_VOTOS"].sum(),
            "p": seg_turno.loc[_voted_lula]["QT_VOTOS"].sum() / n_votos,
            "p_validos": seg_turno.loc[_voted_lula]["QT_VOTOS"].sum()
            / n_votos_validos,
        },
        flavio={
            "n": seg_turno.loc[_voted_flavio]["QT_VOTOS"].sum(),
            "p": seg_turno.loc[_voted_flavio]["QT_VOTOS"].sum() / n_votos,
            "p_validos": seg_turno.loc[_voted_flavio]["QT_VOTOS"].sum()
            / n_votos_validos,
        },
        votos={
            "n": n_votos,
            "n_validos": n_votos_validos,
        },
    )
    return (vote_stats,)


@app.cell
def _(d):
    _n = d.rpolls.df["n"]
    _nua = d.rpolls.df["n_unsure_a"]
    _nub = d.rpolls.df["n_unsure_b"]
    _w = d.rpolls.df["n"] / _n.sum()

    poll_stats = dict(
        lula={
            "p": d.rpolls.df["vote_b"].mean(), # avg. percentage
            "wp": (d.rpolls.df["vote_b"] * _w).sum(), # weighted avg. percentage
            "p_valid": (d.rpolls.df["n_vote_b"] / (_n - _nub)).mean(),
            "wp_valid": (d.rpolls.df["n_vote_b"] * _w / (_n - _nub)).sum(),
            "r": d.rpolls.df["reject_b"].mean(),
            "wr": (d.rpolls.df["reject_b"] * _w).sum(),
            "n": d.rpolls.df["n_vote_b"].sum().round(),
        },
        flavio={
            "p": d.rpolls.df["vote_a"].mean(),
            "wp": (d.rpolls.df["vote_a"] * _w).sum(),
            "p_valid": (d.rpolls.df["n_vote_a"] / (_n - _nua)).mean(),
            "wp_valid": (d.rpolls.df["n_vote_a"] * _w / (_n - _nua)).sum(),
            "r": d.rpolls.df["reject_a"].mean(),
            "wr": (d.rpolls.df["reject_a"] * _w).sum(),
            "n": d.rpolls.df["n_vote_a"].sum().round(),
        },
        votos={
            "n": d.rpolls.df["n"].sum(),
            "n_validos": (d.rpolls.df["n_vote_a"] + d.rpolls.df["n_vote_b"]).sum(),
        },
    )
    return (poll_stats,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## As pesquisas de intenções

    Se os números estiverem condizentes com o resultado das eleições, os dados devem estar prontos para a análise. Mas antes de começar, vamos buscar mais informações para suportar a análise, para entender a propensão dos eleitores a transferir vontos entre candidatos, vamos apoiar e guiar os testes nas intenções de votos das pesquisas independentes realizadas.

    Para esta análise, vamos considerar as pesquisas de segundo turno:

    - [CNT](https://cnt.org.br/pesquisas): BR-00652/2026 e BR-02136/2026
    - [Futura](https://www.futurainteligencia.com.br/pesquisas): BR-00650/2026, BR-00650/2026, BR-06715/2026
    - [Data Folha](https://datafolha.folha.uol.com.br/): BR-09709/2026 e BR-09540/2026
    - [Gerp](https://www.gerp.com.br/relatorios.html): BR-07877/2026, BR-05187/2026, BR-03835/2026, e BR-09327/2026
    - [Instituto França](https://www.instagram.com/institutofranca.br/): BR-07896/2026, BR-04863/2026 e BR-09459/2026
    - [Nexus](https://www.nexus.fsb.com.br/estudos-divulgados/): BR-07997/2026, BR-044499/2026 e BR-08234/2026
    - [Palver](https://www.palver.com.br/survey): BR-00198/2026, BR-08028/2026, BR-04612/2026, e BR-01794/2026
    - [Poder Data](https://www.poder360.com.br/poderdata/): BR-08134/2026, BR-07926/2026, BR-04258/2026, BR-02586/2026 e BR-01209/2026
    - [Quaest](https://quaest.com.br/relatorios-quaest/): BR-08535/2026 e BR-09158/2026
    - [Realtime Big Data](https://realtimebigdata.com.br/pesquisas/): BR-02952/2026 e BR-09670/2026
    - [Vox Brasil](https://voxbrasilpesquisas.com.br/imprensa/): BR-09623/2026, BR-04332/2026 e BR-03259/2026


    ## Rejeição do candidato

    A principal métrica para avaliar a capacidade de um candidato de receber votos transferidos de outros eleitores que não tinham votado nele no primeiro turno é o nível de rejeição. Se a rejeição a um candidato for maior que 50%, se torna, como dito pelo candidato derrotado, uma "impossibilidade matemática".

    Como veremos mais adiante, muitas pesquisas apontavam vantagem para Flávio Bolsonaro nas intenções de votos, e resultados similarmente favoráveis a ele na rejeição. A diferença entre intenções de votos e o resultado final das votações mostra que existia algum nível de viés nas pesquisas.

    Como já temos os resultados das eleições presidenciais, podemos medir o nível de viés das pesquisas, e ajustar a métrica de rejeição para um nível mais próximo do real. Mas vale ressaltar que o viés não representa necessariamente uma preferência do instituto de pesquisa por um candidato, e pode surgir naturalmente durante a seleção da amostra[^1].


    ### Metodologia

    Existe uma métrica popular, usada especificamente para pesquisas eleitorais baseada na razão de chances logarítmica[^2]

    $$
    A' = \ln \left( \frac{ \hat p_A / (1 - \hat p_A) }{ p_A / (1 - p_A) } \right) \tag 1
    $$

    - $\hat p_A$: Percentual das intenções de voto ao candidato A estimadas pela pesquisa
    - $p_A$: Percentual dos votos recebidos pelo candidato A na votação

    O resultado $A'$ obtido é a medida do viés da pesquisa, favorável ao candidato A, se o valor for positivo, o viés é favorável à este candidato, caso contrário, o viés é favorável ao seu adversário, caso $A' = 0$, a  pesquisa não apresenta viés.

    Mesmo que diferente de zero, valor da métrica ainda está sujeito à uma margem de erro para avaliar se o viés medido é estatisticamente significante, isto exige a medida do erro padrão aproximada pelo método-$\delta$[^3]:

    $$
    SE(A') = \sqrt{\frac{1}{n \times \hat p_A \times (1 - \hat p_A)}} \tag 2
    $$

    - $n$: Quantidade de pessoas entrevistadas na pesquisa

    Com isso nós podemos fazer um intervalo de 95% de confiança para o valor real de $A'$, se zero estiver dentro do intervalo, não podemos considerá-lo significativamente diferente de zero.

    $$
    IC(A') = A' \pm 1,96 \times SE(A') \tag 3
    $$

    Para encontrar a "taxa de rejeição real" removendo o viés da pesquisa, vamos usar $A'$ para ajustar o peso das respostas entre os votantes de cada candidato, reduzindo para os super representados ou aumentando para os sub representados.

    $$
    P' = P \times e^{-A'} \tag 4
    $$

    - $P'$: Taxa ajustada para o candidato A
    - $P$: Taxa medida pela pesquisa para o candidato A


    [^1]: **Jota**. ['House effects' explicam por que pesquisas eleitorais são tão diferentes](https://www.jota.info/opiniao-e-analise/colunas/coluna-daniel-marcelino/house-effects-explicam-por-que-pesquisas-eleitorais-sao-tao-diferentes) por Daniel Marcelino.

    [^2]: **Public Opinion Quarterly**. [A Review and Proposal for a New Measure of Poll Accuracy](https://doi.org/10.1093/poq/nfi044) por Elizabeth A. Martin, Michael W. Traugott e Courtney Kennedy

    [^3]: **Constantin Ahlmann-Eltze**. [What is the delta method?](https://const-ae.name/post/2023-02-10_delta_method/delta-method-explainer/)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Premissas

    Esta abordagem de análise se apoia em alguns pressupostos, os resultados expostos aqui se tornam inválidos caso ao menos um deles seja falso:

    1. O nível de rejeição é correlacionado com a intenção de voto;
    2. A rejeição aos candidatos não mudou significativamente entre a data da pesquisa e a data da votação;
    3. A votação registrada nas urnas eletrônicas é condizente com a realidade.

    Com os dados disponíveis, apenas o primeiro pressuposto pode ser testado, depois que este tenha sido verificado, o leitor baseará seu nível de confiança nos resultados deste estudo na sua crença sobre os outros pressupostos. Para testar a primeira hipótese, vamos verificar se existe uma correlação significativa entre o voto em um candidato, e a rejeição pelo seu adversário.

    Para fazer esta análise rapidamente, vamos usar os dados de diversas pesquisas eleitorais, comparando as pesquisas de intenção de voto estimuladas com o percentual de rejeição, onde o entrevistado responde "Não votaria em ___ de jeito nenhum".

    Todas a pesquisas eleitorais utilizadas foram realizadas após os resultados do primeiro turno, isto ajuda a normalizar o viés, já que foi encontrado em uma auditoria independente[^4] que as pesquisas eleitorais apresentaram, em conjunto, vieses para lados diferentes entre o primeiro e segundo turno.



    [^4]: **Jota**. [A eleição de 2026 terminou. Agora, abram seus dados](https://www.jota.info/opiniao-e-analise/colunas/lorena-barberia/a-eleicao-de-2026-terminou-agora-abram-seus-dados) por Lorena G. Barberia, Natália de Paula Moreira e Gustavo Fernandes de Paula
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    <br />
    """)
    return


@app.cell
def _(d, g, ticker):
    plot1 = g.ScatterPlot(
        x=d.rpolls.df["vote_a"],
        y=d.rpolls.df["reject_b"],
        x_label="Vota Flávio Bolsonaro",
        y_label="Rejeita Lula",
        with_regression=True,
        disclaimer=(
            f"Produzido com dados de {len(d.rpolls.polls)} pesquisas de 8 institutos "
            'diferentes realizadas\napós os resultados do primeiro turno. "Vota Flávio '
            'Bolsonaro" representa o\npercentual de entrevistados que responderam '
            '"vou votar no candidato com\ncerteza" na pesquisa estimulada, enquanto que '
            '"Rejeita Lula" representa os\nentrevistados que responderam "não '
            'votaria no candidato de jeito nenhum".'
        ),
    )
    plot1.cfg["disclaimer"]["clearance"] = 0.35
    (
        plot1.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        plot1.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )

    plot2 = g.ScatterPlot(
        x=d.rpolls.df["vote_b"],
        y=d.rpolls.df["reject_a"],
        x_label="Vota Lula",
        y_label="Rejeita Flávio Bolsonaro",
        with_regression=True,
        disclaimer=(
            f"Produzido com dados de {len(d.rpolls.polls)} pesquisas de 8 institutos "
            'diferentes realizadas\napós os resultados do primeiro turno. "Vota Lula" '
            'representa o percentual de\nentrevistados que responderam "vou votar no '
            'candidato com certeza" na\npesquisa estimulada, enquanto que "Rejeita '
            'Flávio Bolsonaro" representa os\nentrevistados que responderam "não '
            'votaria no candidato de jeito nenhum".'
        ),
    )
    plot2.cfg["disclaimer"]["clearance"] = 0.35
    (
        plot2.ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        plot2.ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )

    plot1.show()
    return (plot2,)


@app.cell
def _(plot2):
    plot2.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A análise de correlação indica uma correlação forte entre rejeição e intenção de  votos, mas apenas nas intenções de voto ao Flávio Bolsonaro, quando observamos a intenção de voto no Lula contra a rejeição ao Flávio, esta correlação passa a ser muito fraca para ser considerada relevante. Isto fica evidente no coeficiente de inclinação com confiança de 37,9%, que idealmente seria igual ou superior 95%, como nos demais.

    Este resultado é coerente com o resultado do questionário da pesquisa da Palver (BR-01794/2026, página 29), onde os entrevistados que votariam no Lula justificavam seu voto principalmente com a "Defesa da democracia e direitos", enquanto que os eleitores do Flávio justificaram principalmente com a "Rejeição ao Lula e o PT".

    Isso significa que podemos medir uma rejeição ao Lula ajustada pelo viés das pesquisas, mas não podemos fazer o mesmo para o seu adversário com segurança, já que a correlação com as intenções de voto ao Lula é muito fraca.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Ajustando as pesquisas eleitorais

    As pesquisas eleitorais apontavam um cenário favorável para o candidato Flávio Bolsonaro no segundo turno, agora vamos comparar o resultado previsto pelas pesquisas, o das pesquisas ajustado pela métrica $A'$ de Martin et al. (2005), e comparar com o resultado real das votações:
    """)
    return


@app.cell
def _(d, f, np, poll_stats, vote_stats):
    # Flávio
    Aa = f.a_metric(
        a=vote_stats["flavio"]["p_validos"],
        a_estimate=poll_stats["flavio"]["wp_valid"],
    )
    Aa_SE = f.a_std_error(
        n=d.rpolls.df["n"].sum(),
        a_estimate=poll_stats["flavio"]["wp_valid"],
    )
    ICa_HI, ICa_LO = (Aa + 1.96 * Aa_SE), (Aa - 1.96 * Aa_SE)
    ZERO_NOT_IN_ICa = np.sign(ICa_HI) * np.sign(ICa_LO) == 1

    # Lula
    Ab = f.a_metric(
        a=vote_stats["lula"]["p_validos"],
        a_estimate=poll_stats["lula"]["wp_valid"],
    )
    Ab_SE = f.a_std_error(
        n=d.rpolls.df["n"].sum(),
        a_estimate=poll_stats["lula"]["wp_valid"],
    )
    ICb_HI, ICb_LO = (Ab + 1.96 * Ab_SE), (Ab - 1.96 * Ab_SE)
    ZERO_NOT_IN_ICb = np.sign(ICb_HI) * np.sign(ICb_LO) == 1

    print(ZERO_NOT_IN_ICa, ZERO_NOT_IN_ICb)
    return Aa, Ab


@app.cell
def _(Aa, Ab, np, poll_stats):
    poll_stats["flavio"]["adj_wp_valid"] = poll_stats["flavio"]["wp_valid"] * np.exp(-Aa)
    poll_stats["lula"]["adj_wp_valid"] = poll_stats["lula"]["wp_valid"] * np.exp(-Ab)
    return


@app.cell
def _(poll_stats, vote_stats):
    poll_a = round(poll_stats["flavio"]["wp_valid"] * 100, 1)
    poll_b = round(poll_stats["lula"]["wp_valid"] * 100, 1)
    adj_poll_a = round(poll_stats["flavio"]["adj_wp_valid"] * 100, 1)
    adj_poll_b = round(poll_stats["lula"]["adj_wp_valid"] * 100, 1)
    vote_a = round(vote_stats["flavio"]["p_validos"] * 100, 1)
    vote_b = round(vote_stats["lula"]["p_validos"] * 100, 1)
    return adj_poll_a, poll_a, poll_b, vote_a, vote_b


@app.cell(hide_code=True)
def _(adj_poll_a, mo, poll_a, poll_b, vote_a, vote_b):
    def _f(v):
        return str(v).replace(".", ",")


    mo.md(rf"""
    |                         |       Flávio      |         Lula            |
    | :---                    |       :---:       |         :---:           |
    | **Pesquisas**           | {_f(poll_a)}%     | {_f(poll_b)}%           |
    | **Pesquisas ajustadas** | {_f(adj_poll_a)}% | {_f(100 - adj_poll_a)}% |
    | **Votação**             | {_f(vote_a)}%     | {_f(vote_b)}%           |


    """)
    return


@app.cell(hide_code=True)
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Estimando a transferência real de votos
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Argumentos comuns do Flávio e seus apoiadores
    """)
    return


if __name__ == "__main__":
    app.run()
