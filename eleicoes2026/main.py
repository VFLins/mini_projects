import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import formulas as f
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import urllib.request
    import zipfile

    from pathlib import Path

    return Path, f, np, pd, plt, urllib, zipfile


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

    - Data Folha: [BR-09709/2026](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/22/datafolha-presidente-segundo-turno-22-outubro.ghtml) e [BR-09540/2026](https://datafolha.folha.uol.com.br/eleicoes/2026/10/flavio-bolsonaro-51-e-lula-49-chegam-empatados-tecnicamente-ao-dia-da-eleicao.shtml)
    - Palver: [BR-00198/2026](https://www.palver.com.br/api/surveys/voting-intention-2026-october-w6/report), [BR-08028/2026](https://www.palver.com.br/api/surveys/voting-intention-2026-october-w7/report), [BR-04612/2026](https://www.palver.com.br/api/surveys/voting-intention-2026-october-w8/report), e [BR-01794/2026](https://www.palver.com.br/api/surveys/voting-intention-2026-october-w9/report)
    - Quaest: [BR-08535/2026](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/21/quaest-presidente-21-outubro.ghtml) e [BR-09158/2026](https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/10/24/quaest-2o-turno-votos-validos.ghtml)
    - Realtime Big Data: [BR-03490/2026](https://realtimebigdata.com.br/wp-content/uploads/2026/09/Brasil-BR-03490-2026-Set26.pdf) (set. 2026)
    - Vox Brasil: [BR-09623/2026](https://static.poder360.com.br/uploads/2026/10/pesquisa-vox-brasil-9out2026.pdf)


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
        n=2154, ic=0.02, # revisar
        name="datafolha1", # revisar
        vote_a=0.49, vote_b=0.45,
        reject_a=0.43, reject_b=0.46
    )
    polls.add(
        n=2154, ic=0.02, # revisar
        name="datafolha2", # revisar
        vote_a=0.47, vote_b=0.45,
        reject_a=0.44, reject_b=0.46
    )
    polls.add(
        n=2154, ic=0.02,
        name="datafolha3_BR-09540/2026",
        vote_a=0.47, vote_b=0.46,
        reject_a=0.46, reject_b=0.45
    )
    polls.add(
        n=4050, ic=0.02,
        name="datafolha4_BR-09540/2026",
        vote_a=0.46, vote_b=0.45,
        reject_a=0.48, reject_b=0.49
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
def _():
    return


@app.cell
def _(np, plt, polls):
    polls.df.plot.scatter(x="vote_a", y="reject_b")
    ma, ba = np.polyfit(polls.df["vote_a"], polls.df["reject_b"], 1)
    print()
    plt.plot(
        polls.df["vote_a"],
        (ma * polls.df["vote_a"] + ba),
        label=f"slope: {ma:.2f}, intercept: {ba:.2f}",
    )
    plt.legend()
    return


@app.cell
def _(np, plt, polls):
    polls.df.plot.scatter(x="vote_b", y="reject_a")
    mb, bb = np.polyfit(polls.df["vote_b"], polls.df["reject_a"], 1)
    plt.plot(
        polls.df["vote_b"],
        (mb * polls.df["vote_b"] + bb),
        label=f"slope: {mb:.2f}, intercept: {bb:.2f}",
    )
    plt.legend()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Argumentos comuns do Flávio Bolsonaro e seus apoiadores
    """)
    return


if __name__ == "__main__":
    app.run()
