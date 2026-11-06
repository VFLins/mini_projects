import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import formulas as f
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import numpy as np
    import pandas as pd
    import urllib.request
    import zipfile

    from pathlib import Path

    return Path, f, pd, plt, ticker, urllib, zipfile


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(Path, urllib, zipfile):
    # Obtendo dados para a análise
    # ============================

    # Downloads na mesma pasta que o main.py
    PROJECT_ROOT = Path(__file__).parent.resolve()
    DOWNLOADS_DIR = PROJECT_ROOT / "data"

    # Presidente - Votação por seção eleitoral - 2026
    # https://dadosabertos.tse.jus.br/dataset/resultados-2026/resource/01ea4ccd-f443-469c-9f29-c69ff97f7d4c
    VOTOS_URL = (
        "https://cdn.tse.jus.br/estatistica/sead/odsele/"
        "votacao_secao/votacao_secao_2026_BR.zip"
    )
    VOTOS_ZIP = VOTOS_URL.split("/")[-1]
    VOTOS_CSV = Path(VOTOS_ZIP).with_suffix(".csv")

    if not (DOWNLOADS_DIR / VOTOS_CSV).is_file():
        print("Fazendo download dos dados...")
        urllib.request.urlretrieve(VOTOS_URL, VOTOS_ZIP)
        print(f"Extraindo arquivos para {DOWNLOADS_DIR}")
        zipfile.ZipFile(PROJECT_ROOT / VOTOS_ZIP).extractall(DOWNLOADS_DIR)
        print(f"Excluindo arquivo compactado {PROJECT_ROOT / VOTOS_ZIP}")
        (PROJECT_ROOT / VOTOS_ZIP).unlink()
        print("Concluído!")
    return (DOWNLOADS_DIR,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Entendendo a transferência de votos entre o primeiro e segundo turno das eleições presidenciais de 2026

    O candidato Flávio Bolsonaro terminou o primeiro turno com uma votação maior que a do seu principal adversário Lula, isto levou os bolsonaristas a acreditar que a vitória no segundo turno seria certa, já que históricamente, o primeiro colocado no primeiro turno sempre acabava ganhando a disputa no segundo turno.

    Depois da derrota, já nos Estados Unidos, Flávio Bolsonaro alegou uma "impossibilidade matemática", que permitiu que o seu adversário Lula ganhasse mais de 10 Milhões de votos do primeiro para o segundo turno. O objetivo desta análise é combinar os dados de votação com os resultados de pesquisas de opinião anteriores às votações para entender se esta transferência é realmente impossível como alegado.
    """)
    return


@app.cell
def _(DOWNLOADS_DIR, pd):
    votos = pd.read_csv(
        DOWNLOADS_DIR / "votacao_secao_2026_BR.csv",
        sep=";",
        encoding="latin1",
    )
    votos.dtypes
    return (votos,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A explicação dos códigos acima está no arquivo `"data/leiame.pdf"`.

    Para validar se os dados de votos foram coletados corretamente, vamos tentar reproduzir os resultados das votações em tabelas  abaixo:
    """)
    return


@app.cell
def _(votos):
    # eleições dos presidenciáveis: 1º turno
    prim_turno = votos.loc[votos["NR_TURNO"] == 1]
    prim_turno.groupby("NM_VOTAVEL")["QT_VOTOS"].sum().sort_values(ascending=False)
    return


@app.cell
def _(votos):
    # eleições dos presidenciáveis: 2º turno
    seg_turno = votos.loc[votos["NR_TURNO"] == 2]
    seg_turno.groupby("NM_VOTAVEL")["QT_VOTOS"].sum().sort_values(ascending=False)
    return (seg_turno,)


@app.cell
def _(seg_turno):
    seg_turno.loc[seg_turno["NR_VOTAVEL"] == 13]
    return


@app.cell
def _(seg_turno):
    n_votos = seg_turno["QT_VOTOS"].sum()
    n_votos_validos = seg_turno.loc[seg_turno["NR_VOTAVEL"] in (13, 22)]["QT_VOTOS"].sum()

    lula = {
        "n_votos": seg_turno.loc[seg_turno["NR_VOTAVEL"] == 13]["QT_VOTOS"].sum(),
        "p_votos": seg_turno.loc[seg_turno["NR_VOTAVEL"] == 13]["QT_VOTOS"].sum() / n_votos,
        "p_votos": seg_turno.loc[seg_turno["NR_VOTAVEL"] == 13]["QT_VOTOS"].sum() / n_votos_validos,
    }

    lula
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Talvez eu use

    $$
    B = \frac{1}{k} \sum_{i=1}^{k} \left| A'_i \right|
    $$
    """)
    return


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


    ### Premissas

    Esta abordagem de análise se apoia em alguns pressupostos, os resultados expostos aqui se tornam inválidos caso ao menos um deles seja falso:

    1. O nível de rejeição é correlacionado com a intenção de voto;
    2. A rejeição aos candidatos não mudou significativamente entre a data da pesquisa e a data da votação;
    3. A votação registrada nas urnas eletrônicas é condizente com a realidade.

    Com os dados disponíveis, apenas o primeiro pressuposto pode ser testado, depois que este tenha sido verificado, o leitor baseará seu nível de confiança nos resultados deste estudo na sua crença sobre os outros pressupostos.



    [^1]: Para saber mais sobre os vieses que podem aparecer em pesquisas eleitorais, veja [este artigo](https://www.jota.info/opiniao-e-analise/colunas/coluna-daniel-marcelino/house-effects-explicam-por-que-pesquisas-eleitorais-sao-tao-diferentes) do Daniel Marcelino.

    [^2]: **Public Opinion Quarterly**. [A Review and Proposal for a New Measure of Poll Accuracy](https://doi.org/10.1093/poq/nfi044)

    [^3]: **Constantin Ahlmann-Eltze**. [What is the delta method?](https://const-ae.name/post/2023-02-10_delta_method/delta-method-explainer/)
    """)
    return


@app.cell
def _(f):
    # Usando:
    # Candidato A: Flávio Bolsonaro
    # Candidato B: Lula

    polls = f.PollHandler()

    polls.add(
        n=2000, ic=0.022,
        name="futura1_BR-00650/2026",
        vote_a=0.50, vote_b=0.466,
        reject_a=0.454, reject_b=0.486,
    )
    polls.add(
        n=2000, ic=0.022,
        name="futura2_BR-03761/2026",
        vote_a=0.49, vote_b=0.475,
        reject_a=0.461, reject_b=0.472,
    )
    polls.add(
        n=2000, ic=0.022,
        name="futura3_BR-06715/2026",
        vote_a=0.483, vote_b=0.475,
        reject_a=0.458, reject_b=0.474,
    )
    polls.add(
        n=2000, ic=0.022,
        name="futura4_BR-06614/2026",
        vote_a=0.489, vote_b=0.468,
        reject_a=0.452, reject_b=0.473,
    )
    polls.add(
        n=2000, ic=0.022,
        name="futura5_BR-09726/2026",
        vote_a=0.482, vote_b=0.479,
        reject_a=0.466, reject_b=0.4662,
    )
    polls.add(
        n=2154, ic=0.02, # revisar
        name="datafolha1", # revisar
        vote_a=0.49, vote_b=0.45,
        reject_a=0.43, reject_b=0.46,
    )
    polls.add(
        n=2154, ic=0.02, # revisar
        name="datafolha2", # revisar
        vote_a=0.47, vote_b=0.45,
        reject_a=0.44, reject_b=0.46,
    )
    polls.add(
        n=2154, ic=0.02,
        name="datafolha3_BR-09540/2026",
        vote_a=0.47, vote_b=0.46,
        reject_a=0.46, reject_b=0.45,
    )
    polls.add(
        n=4050, ic=0.02,
        name="datafolha4_BR-09540/2026",
        vote_a=0.46, vote_b=0.45,
        reject_a=0.48, reject_b=0.49,
    )
    polls.add(
        n=2400, ic=0.02,
        name="gerp1_BR-07877/2026",
        vote_a=0.53, vote_b=0.44,
        reject_a=0.42, reject_b=0.53,
    )
    polls.add(
        n=2400, ic=0.02,
        name="gerp2_BR-05187/2026",
        vote_a=0.50, vote_b=0.45,
        reject_a=0.46, reject_b=0.49,
    )
    polls.add(
        n=2400, ic=0.02,
        name="gerp3_BR-03835/2026",
        vote_a=0.50, vote_b=0.45,
        reject_a=0.46, reject_b=0.49,
    )
    polls.add(
        n=2400, ic=0.02,
        name="gerp4_ BR-09327/2026",
        vote_a=0.49, vote_b=0.46,
        reject_a=0.45, reject_b=0.48
    )
    polls.add(
        n=2002, ic=0.02,
        name="nexus1_BR-07997/2026",
        vote_a=0.48, vote_b=0.45,
        reject_a=0.47, reject_b=0.51,
    )
    polls.add(
        n=2002, ic=0.02,
        name="nexus2_BR-04499/2026",
        vote_a=0.465, vote_b=0.459,
        reject_a=0.468, reject_b=0.478,
    )
    polls.add(
        n=2000, ic=0.022,
        name="nexus2_BR-04499/2026",
        vote_a=0.47, vote_b=0.46,
        reject_a=0.465, reject_b=0.491,
    )
    polls.add(
        n=5000, ic=0.023,
        name="palverw7_BR-08028/2026",
        vote_a=0.49, vote_b=0.48,
        reject_a=0.48, reject_b=0.50,
    )
    polls.add(
        n=5000, ic=0.024,
        name="palverw8_BR-04612/2026,",
        vote_a=0.49, vote_b=0.49,
        reject_a=0.47, reject_b=0.47,
    )
    polls.add(
        n=5000, ic=0.022,
        name="palverw9_BR-01794/2026",
        vote_a=0.49, vote_b=0.48,
        reject_a=0.47, reject_b=0.48,
    )
    polls.add(
        n=2100, ic=0.0215,
        name="vox_BR-09623/2026",
        vote_a=0.427, vote_b=0.442,
        reject_a=0.442, reject_b=0.452,
    )
    polls.add(
        n=2154, ic=0.02,
        name="quaest1_BR-08535/2026",
        vote_a=0.45, vote_b=0.44,
        reject_a=0.52, reject_b=0.47,
    )
    polls.add(
        n=3702, ic=0.02,
        name="quaest2_BR-09158/2026",
        vote_a=0.46, vote_b=0.45,
        reject_a=0.49, reject_b=0.47,
    )

    polls.df
    return (polls,)


@app.cell
def _(f, plt, polls, ticker):
    fig1, ax1 = f.scatterplot(
        x=polls.df["vote_a"],
        y=polls.df["reject_b"],
        x_label="Vota Flávio Bolsonaro",
        y_label="Rejeita Lula",
        with_regression=True,
    )
    (
        ax1
        .yaxis
        .set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        ax1
        .xaxis
        .set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    plt.show()
    return


@app.cell
def _(f, plt, polls, ticker):
    fig2, ax2 = f.scatterplot(
        x=polls.df["vote_b"],
        y=polls.df["reject_a"],
        x_label="Vota Lula",
        y_label="Rejeita Flávio Bolsonaro",
        with_regression=True,
    )
    (
        ax2
        .yaxis
        .set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    (
        ax2
        .xaxis
        .set_major_formatter(
            ticker.FuncFormatter(lambda x, pos: f"{int(x * 100)}%")
        )
    )
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Argumentos comuns do Flávio Bolsonaro e seus apoiadores
    """)
    return


if __name__ == "__main__":
    app.run()
