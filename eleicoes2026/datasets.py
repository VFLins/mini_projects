from dataclasses import dataclass
import pandas as pd
import marimo as mo
import urllib.request
from pathlib import Path
import zipfile


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


class VoteData:
    def __init__(self):
        self.ask_download = (
            mo.ui.checkbox(value=True, label="Baixar os dados de votação (1,6 GB)")
            .form(submit_button_label="Continuar")
        )

    @property
    def file_exists(self) -> bool:
        return (DOWNLOADS_DIR / VOTOS_CSV).is_file()


    def download(self):
        if self.ask_download.value is False:
            print("Ignorando download como solicitado pelo usuário.")
            return

        if not self.file_exists:
            print("Fazendo download dos dados...")
            urllib.request.urlretrieve(VOTOS_URL, VOTOS_ZIP)
            print(f"Extraindo arquivos para {DOWNLOADS_DIR}")
            zipfile.ZipFile(PROJECT_ROOT / VOTOS_ZIP).extractall(DOWNLOADS_DIR)
            print(f"Excluindo arquivo compactado {PROJECT_ROOT / VOTOS_ZIP}")
            (PROJECT_ROOT / VOTOS_ZIP).unlink()
            print("Download concluído.")
        else:
            print("Dados já encontrados no diretório esperado, ignorando download.")

    def load(self):
        if not self.file_exists:
            print("Ignorando carregamento, dados não encontrados.")
            return

        print("Carregando dados...")
        self.df = pd.read_csv(
            DOWNLOADS_DIR / "votacao_secao_2026_BR.csv",
            sep=";",
            encoding="latin1",
            usecols=[
                "CD_CARGO",
                "CD_MUNICIPIO",
                "NR_ZONA",
                "NR_SECAO",
                "NR_VOTAVEL",
                "NM_VOTAVEL",
                "NR_TURNO",
                "QT_VOTOS",
                "NR_SECAO",
                "NR_ZONA"
            ],
            dtype={
                "CD_CARGO": "int16",
                "NR_VOTAVEL": "int16",
                "NM_VOTAVEL": "category",
                "NR_TURNO": "int16",
                "QT_VOTOS": "int64",
                "NR_SECAO": "int64",
                "NR_ZONA": "int64",
            }
        )
        print("Dados carregados.")


class RejectionPolls:
    @property
    def polls(self) -> list[pd.Series]:
        return self._polls

    def __init__(self):
        self._polls: list[pd.Series] = []

    def add(
        self,
        n: int,
        ic: float,
        name: str,
        vote_a: float,
        vote_b: float,
        reject_a: float,
        reject_b: float,
    ):
        """Adds a poll dataset with vote intentions and rejections.

        :param n: Poll sample size.
        :param ic: Poll estimated confidence interval in percentage points.
        :param name: Poll name, identifying it in the dataset.
        :param vote_flavio: Percentage of votes declared to candidate Flávio.
        :param vote_lula: Percentage of votes declared to candidate Lula.
        :paran reject_flavio: Percentage of voters declared not voting on candidate Flávio.
        :paran reject_lula: Percentage of voters declared not voting on candidate Lula.
        """
        vote_a_hi, vote_a_lo = vote_a + ic, vote_a - ic
        vote_b_hi, vote_b_lo = vote_b + ic, vote_b - ic
        reject_a_hi, reject_a_lo = reject_a + ic, reject_a - ic
        reject_b_hi, reject_b_lo = reject_b + ic, reject_b - ic
        n_va = n * vote_a
        n_vb = n * vote_b
        n_ra = n * reject_a
        n_rb = n * reject_b
        n_ua = n - n_va - n_ra
        n_ub = n - n_vb - n_rb
        unsure_a = n_ua / n
        unsure_b = n_ub / n
        unsure_a_hi, unsure_a_lo = unsure_a + ic, unsure_a - ic
        unsure_b_hi, unsure_b_lo = unsure_b + ic, unsure_b - ic

        colnames = [
            "n", "ic",
            "vote_a", "vote_a_hi", "vote_a_lo",
            "vote_b", "vote_b_hi", "vote_b_lo",
            "unsure_a", "unsure_a_hi", "unsure_a_lo",
            "unsure_b", "unsure_b_hi", "unsure_b_lo",
            "reject_a", "reject_a_hi", "reject_a_lo",
            "reject_b", "reject_b_hi", "reject_b_lo",
            "n_vote_a", "n_vote_b",
            "n_unsure_a", "n_unsure_b",
            "n_reject_a", "n_reject_b",
        ]

        self._polls.append(pd.Series(
            [
            n, ic,
            vote_a, vote_a_hi, vote_a_lo,
            vote_b, vote_b_hi, vote_b_lo,
            unsure_a, unsure_a_hi, unsure_a_lo,
            unsure_b, unsure_b_hi, unsure_b_lo,
            reject_a, reject_a_hi, reject_a_lo,
            reject_b, reject_b_hi, reject_b_lo,
            n_va, n_vb,
            n_ua, n_ub,
            n_ra, n_rb,
        ],
        name=name,
        index=colnames
        ))
        self.df = pd.DataFrame(data=self._polls)


# Usando:
# Candidato A: Flávio Bolsonaro
# Candidato B: Lula
rpolls = RejectionPolls()

rpolls.add(
    n=2000, ic=0.022,
    name="futura1_BR-00650/2026",
    vote_a=0.50, vote_b=0.466, reject_a=0.454, reject_b=0.486,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura2_BR-03761/2026",
    vote_a=0.49, vote_b=0.475, reject_a=0.461, reject_b=0.472,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura3_BR-06715/2026",
    vote_a=0.483, vote_b=0.475, reject_a=0.458, reject_b=0.474,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura4_BR-06614/2026",
    vote_a=0.489, vote_b=0.468, reject_a=0.452, reject_b=0.473,
)
rpolls.add(
    n=2000, ic=0.022,
    name="futura5_BR-09726/2026",
    vote_a=0.482, vote_b=0.479, reject_a=0.466, reject_b=0.4662,
)
rpolls.add(
    n=2154, ic=0.02, # revisar
    name="datafolha1", # revisar
    vote_a=0.49, vote_b=0.45, reject_a=0.43, reject_b=0.46,
)
rpolls.add(
    n=2154, ic=0.02, # revisar
    name="datafolha2", # revisar
    vote_a=0.47, vote_b=0.45, reject_a=0.44, reject_b=0.46,
)
rpolls.add(
    n=2154, ic=0.02,
    name="datafolha3_BR-09540/2026",
    vote_a=0.47, vote_b=0.46, reject_a=0.46, reject_b=0.45,
)
rpolls.add(
    n=4050, ic=0.02,
    name="datafolha4_BR-09540/2026",
    vote_a=0.46, vote_b=0.45, reject_a=0.48, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp1_BR-07877/2026",
    vote_a=0.53, vote_b=0.44, reject_a=0.42, reject_b=0.53,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp2_BR-05187/2026",
    vote_a=0.50, vote_b=0.45, reject_a=0.46, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp3_BR-03835/2026",
    vote_a=0.50, vote_b=0.45, reject_a=0.46, reject_b=0.49,
)
rpolls.add(
    n=2400, ic=0.02,
    name="gerp4_BR-09327/2026",
    vote_a=0.49, vote_b=0.46, reject_a=0.45, reject_b=0.48
)
rpolls.add(
    n=2002, ic=0.02,
    name="nexus1_BR-07997/2026",
    vote_a=0.48, vote_b=0.45, reject_a=0.47, reject_b=0.51,
)
rpolls.add(
    n=2002, ic=0.02,
    name="nexus2_BR-04499/2026",
    vote_a=0.465, vote_b=0.459, reject_a=0.468, reject_b=0.478,
)
rpolls.add(
    n=2000, ic=0.022,
    name="nexus2_BR-04499/2026",
    vote_a=0.47, vote_b=0.46, reject_a=0.465, reject_b=0.491,
)
rpolls.add(
    n=5000, ic=0.023,
    name="palverw7_BR-08028/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.48, reject_b=0.50,
)
rpolls.add(
    n=5000, ic=0.024,
    name="palverw8_BR-04612/2026,",
    vote_a=0.49, vote_b=0.49, reject_a=0.47, reject_b=0.47,
)
rpolls.add(
    n=5000, ic=0.022,
    name="palverw9_BR-01794/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.47, reject_b=0.48,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata1_BR-08134/2026",
    vote_a=0.49, vote_b=0.44, reject_a=0.43, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata2_BR-01209/2026",
    vote_a=0.48, vote_b=0.46, reject_a=0.44, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata3_BR-04258/2026",
    vote_a=0.47, vote_b=0.47, reject_a=0.45, reject_b=0.46,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata4_BR-07926/2026",
    vote_a=0.49, vote_b=0.48, reject_a=0.45, reject_b=0.47,
)
rpolls.add(
    n=3000, ic=0.018,
    name="poderdata5_BR-02586/2026",
    vote_a=0.49, vote_b=0.46, reject_a=0.44, reject_b=0.48,
)
rpolls.add(
    n=2154, ic=0.02,
    name="quaest1_BR-08535/2026",
    vote_a=0.45, vote_b=0.44, reject_a=0.52, reject_b=0.47,
)
rpolls.add(
    n=3702, ic=0.02,
    name="quaest2_BR-09158/2026",
    vote_a=0.46, vote_b=0.45, reject_a=0.49, reject_b=0.47,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox1_BR-09623/2026",
    vote_a=0.427, vote_b=0.442, reject_a=0.442, reject_b=0.452,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox2_BR-04332/2026",
    vote_a=0.446, vote_b=0.464, reject_a=0.453, reject_b=0.453,
)
rpolls.add(
    n=2100, ic=0.0215,
    name="vox3_BR-03259/2026",
    vote_a=0.443, vote_b=0.454, reject_a=0.471, reject_b=0.448,
)
