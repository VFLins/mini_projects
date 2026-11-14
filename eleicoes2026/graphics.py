import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

from scipy import stats
from typing import Sequence
import numpy as np


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


class SankeyPlot(BasePlot):
    """Two-column Sankey (origin -> destination).

    :param flows: Matrix of voters, origins in rows and destinations in columns.
    :param left_labels: Names of the origins (rows).
    :param right_labels: Names of the destinations (columns).
    :param right_colors: One color per destination; ribbons take the color of
        their destination.
    :param gap: Vertical gap between nodes, as a fraction of the height.
    :param title: Optional title.
    :param disclaimer: Optional footnote.
    """

    def __init__(
        self,
        flows,
        left_labels: list[str],
        right_labels: list[str],
        right_colors: list[str],
        gap: float = 0.03,
        title: str | None = None,
        disclaimer: str | None = None,
    ):
        super().__init__(title=title, disclaimer=disclaimer)
        self.flows = np.asarray(flows, float)
        if self.flows.shape != (len(left_labels), len(right_labels)):
            raise ValueError("flows shape must match the number of labels")
        if len(right_colors) != len(right_labels):
            raise ValueError("one color per destination is required")
        self.left_labels = left_labels
        self.right_labels = right_labels
        self.right_colors = right_colors
        self.gap = gap

    @staticmethod
    def _fmt(v: float) -> str:
        if v >= 1e6:
            return f"{v / 1e6:.2f} mi".replace(".", ",")
        else:
            return f"{v / 1e3:.0f} mil".replace(".", ",")

    def build_plot(self):
        super().build_plot()
        ax, F = self.ax, self.flows
        K, M = F.shape
        scale = (1 - self.gap * (max(K, M) - 1)) / F.sum()
        x0, x1, w = 0.0, 1.0, 0.03

        def tops(sizes):
            y, out = 0.0, []
            for s in sizes:
                out.append(y)
                y += s * scale + self.gap
            return out

        left_size, right_size = F.sum(axis=1), F.sum(axis=0)
        left_top, right_top = tops(left_size), tops(right_size)
        left_off, right_off = np.array(left_top), np.array(right_top)

        for j in range(K):
            for k in range(M):
                h = F[j, k] * scale
                yl, yr = left_off[j], right_off[k]
                left_off[j] += h
                right_off[k] += h
                xa, xb, xm = x0 + w, x1, (x0 + x1) / 2
                verts = [(xa, yl), (xm, yl), (xm, yr), (xb, yr),
                         (xb, yr + h), (xm, yr + h), (xm, yl + h), (xa, yl + h),
                         (xa, yl)]
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                         Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                         Path.CLOSEPOLY]
                ax.add_patch(PathPatch(Path(verts, codes),
                                       facecolor=self.right_colors[k],
                                       alpha=0.45, edgecolor="none"))

        fs = self.cfg["font"]["size"]["base"]
        for j in range(K):
            ax.add_patch(Rectangle((x0, left_top[j]), w, left_size[j] * scale,
                                   color="0.25"))
            ax.text(x0 - 0.01, left_top[j] + left_size[j] * scale / 2,
                    f"{self.left_labels[j]}\n{self._fmt(left_size[j])}",
                    ha="right", va="center", fontsize=fs)
        for k in range(M):
            ax.add_patch(Rectangle((x1, right_top[k]), w, right_size[k] * scale,
                                   color=self.right_colors[k]))
            ax.text(x1 + w + 0.01, right_top[k] + right_size[k] * scale / 2,
                    f"{self.right_labels[k]}\n{self._fmt(right_size[k])}",
                    ha="left", va="center", fontsize=fs)

        bottom = max(left_top[-1] + left_size[-1] * scale,
                     right_top[-1] + right_size[-1] * scale)
        ax.set_xlim(-0.3, 1.3)
        ax.set_ylim(bottom + 0.02, -0.02)
        ax.axis("off")
