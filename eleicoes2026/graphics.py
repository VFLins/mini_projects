import matplotlib.pyplot as plt
from scipy import stats
from typing import Sequence


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Inter"]


class BasePlot:
    cfg: dict = {
        "font": {
            "size": {
                "legend": 13,
                "base": 16,
                "title": 32,
            },
        },
        "spines": {
            "line_width": 2.5,
        },
        "disclaimer": {
            "clearance": 0.3,
        }
    }

    def __init__(
        self,
        title: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        disclaimer: str | None = None,
    ):
        self.fig, self.ax = plt.subplots(figsize=(9, 7))
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.disclaimer = disclaimer

    def build_plot(self):
        self.fig.subplots_adjust(
            bottom=self.cfg["disclaimer"]["clearance"] if self.disclaimer else 0.12
        )
        if self.title:
            plt.title(
                self.title,
                fontsize=self.cfg["font"]["size"]["title"],
                fontname="Space Mono",
                loc="left",
                pad=14,
            )
        if self.x_label:
            plt.xlabel(
                self.x_label, fontsize=self.cfg["font"]["size"]["base"], labelpad=14
            )
        if self.y_label:
            plt.ylabel(
                self.y_label, fontsize=self.cfg["font"]["size"]["base"], labelpad=14
            )
        if self.disclaimer:
            self.fig.text(
                x=0.12, y=0.04,
                s=self.disclaimer,
                fontsize=self.cfg["font"]["size"]["legend"],
                color="#4b5865",
                ha="left",
                va="bottom",
                wrap=True
            )

        for k, v in self.ax.spines.items():
            if k in ["top", "right"]:
                v.set_visible(False)
            else:
                v.set_linewidth(self.cfg["spines"]["line_width"])
                v.set_color("#98a7b4")

    def resize(self, w: float, h: float):
        self.fig.set_size_inches(w, h)

    def show(self):
        self.build_plot()
        return self.fig, self.ax


class ScatterPlot(BasePlot):
    def __init__(
        self,
        x: Sequence,
        y: Sequence,
        with_regression: bool = False,
        title: str | None = None,
        x_label: str | None = None,
        y_label: str | None = None,
        disclaimer: str | None = None,
    ):
        super().__init__(
            title=title, x_label=x_label, y_label=y_label, disclaimer=disclaimer
        )
        self.x = x
        self.y = y
        self.with_regression = with_regression

    def build_plot(self):
        super().build_plot()
        self.ax.scatter(self.x, self.y, c="#008181", s=100)
        self.ax.tick_params(
            axis="both", labelsize=self.cfg["font"]["size"]["legend"], length=0, pad=6
        )

        if self.with_regression:
            res = stats.linregress(self.x, self.y)
            df = len(self.x) - 2
            slope = res.slope
            intercept = res.intercept
            t_intercept = intercept / res.intercept_stderr
            p_intercept = 2 * (1 - stats.t.cdf(abs(t_intercept), df))
            y_pred = slope * self.x + intercept
            label_reg = (
                f"Intercepto: {intercept:.2f} "
                f"(Conf.: {100 - (p_intercept * 100):.1f}%)\n"
                f"Inclinação: {slope:.2f} "
                f"(Conf.: {100 - (res.pvalue * 100):.1f}%)"
            )
            self.ax.plot(self.x, y_pred, color="#374451", linewidth=2, label=label_reg)
            self.ax.legend(frameon=False, fontsize=self.cfg["font"]["size"]["legend"])

