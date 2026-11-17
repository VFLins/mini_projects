import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Rectangle

from scipy import stats
from typing import Sequence
import numpy as np
import copy


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
    """Two-column Sankey plot (origin -> destination).

    :param flows: Flow matrix, origins in rows and destinations in columns.
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
                verts = [
                    (xa, yl), (xm, yl), (xm, yr), (xb, yr),
                    (xb, yr + h), (xm, yr + h), (xm, yl + h), (xa, yl + h),
                    (xa, yl),
                ]
                codes = [
                    Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                    Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                    Path.CLOSEPOLY,
                ]
                ax.add_patch(
                    PathPatch(
                        Path(verts, codes),
                        facecolor=self.right_colors[k],
                        alpha=0.55,
                        edgecolor="none",
                    )
                )

        fs = self.cfg["font"]["size"]["legend"]
        for j in range(K):
            ax.add_patch(
                Rectangle((x0, left_top[j]), w, left_size[j] * scale, color="#212c38")
            )
            ax.text(
                x0 - 0.01,
                left_top[j] + left_size[j] * scale / 2,
                f"{self.left_labels[j]}\n{self._fmt(left_size[j])}",
                ha="right", va="center", fontsize=fs
            )
        for k in range(M):
            ax.add_patch(
                Rectangle(
                    (x1, right_top[k]),
                    w,
                    right_size[k] * scale,
                    color=self.right_colors[k]
                )
            )
            ax.text(
                x1 + w + 0.01,
                right_top[k] + right_size[k] * scale / 2,
                f"{self.right_labels[k]}\n{self._fmt(right_size[k])}",
                ha="left", va="center", fontsize=fs
            )

        bottom = max(
            left_top[-1] + left_size[-1] * scale,
            right_top[-1] + right_size[-1] * scale,
        )
        ax.set_xlim(-0.3, 1.3)
        ax.set_ylim(bottom + 0.02, -0.02)
        ax.axis("off")


class BarPlot(BasePlot):
    """Bar plot with error bars shown only for grouped categories.

    Bar colors come from ``cfg["bar"]["colors"]``: one color is applied to
    each bar in order, cycling through the list if there are more bars than
    colors. Error bar colors (lines and caps) come from
    ``cfg["bar"]["error_colors"]`` and work the same way: one color per bar,
    cycling through the list.

    If every category is unique, each value is drawn as its own bar, without
    error bars. If any category repeats, values are grouped by category: each
    bar shows the mean of its group and the error bars extend from the mean
    to the group's minimum and maximum.

    :param categories: Category of each value. Repeats trigger grouping.
    :param values: One value per entry in ``categories``.
    :param horizontal: If ``True``, draw horizontal bars.
    :param show_values: If ``True``, write each bar's value next to it.
    :param kwargs: Forwarded to :class:`BasePlot` (``title``, ``x_label``,
        ``y_label``, ``disclaimer``).
    :raises ValueError: If ``values`` does not match the number of categories.
    """

    cfg: dict = {
        **BasePlot.cfg,
        "bar": {
            "width": 0.7,
            "colors": ["#212c38", "#008181", "#98a7b4", "#32d6d0"],
            "capsize": 5,
            "error_line_width": 2,
            "error_colors": ["#708090", "#212c38", "#212c38", "#212c38"],
        },
    }

    def __init__(
        self,
        categories: Sequence[str],
        values: Sequence[float],
        horizontal: bool = False,
        show_values: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.horizontal = horizontal
        self.show_values = show_values

        categories = list(categories)
        values = np.asarray(values, dtype=float)
        n = len(categories)
        if values.shape != (n,):
            raise ValueError(f"Got {values.size} values, but there are {n} categories.")

        if len(set(categories)) == n:
            self.categories = categories
            self.values = values
            self.errors = None
        else:
            self.categories, self.values, self.errors = self._group(categories, values)

    @staticmethod
    def _group(
        categories: list[str], values: np.ndarray
    ) -> tuple[list[str], np.ndarray, np.ndarray]:
        """Group values by category.

        :param categories: Category of each value (may contain repeats).
        :param values: One value per entry in ``categories``.
        :return: Unique categories (in order of first appearance), the mean of
            each group, and asymmetric errors of shape ``(2, n_groups)`` that
            reach from the mean down to the group minimum and up to the
            group maximum.
        """
        groups: dict[str, list[float]] = {}
        for c, v in zip(categories, values):
            groups.setdefault(c, []).append(v)

        means = np.array([np.mean(g) for g in groups.values()])
        lower = means - np.array([np.min(g) for g in groups.values()])
        upper = np.array([np.max(g) for g in groups.values()]) - means
        return list(groups), means, np.array([lower, upper])

    def build_plot(self):
        bcfg = self.cfg["bar"]
        positions = np.arange(len(self.categories))

        colors = [bcfg["colors"][i % len(bcfg["colors"])] for i in positions]
        error_colors = [
            bcfg["error_colors"][i % len(bcfg["error_colors"])] for i in positions
        ]

        if self.horizontal:
            self.ax.barh(
                positions, self.values, height=bcfg["width"], color=colors, zorder=3
            )
            self.ax.set_yticks(positions, self.categories)
            self.ax.invert_yaxis()
            self.ax.xaxis.grid(True, color="#e3e8ec", zorder=0)
        else:
            self.ax.bar(
                positions, self.values, width=bcfg["width"], color=colors, zorder=3
            )
            self.ax.set_xticks(positions, self.categories)
            self.ax.yaxis.grid(True, color="#e3e8ec", zorder=0)

        # Error bars are drawn one by one so each can have its own color
        if self.errors is not None:
            for i, color in enumerate(error_colors):
                err = self.errors[:, i : i + 1]
                kw = dict(
                    fmt="none",
                    ecolor=color,
                    elinewidth=bcfg["error_line_width"],
                    capsize=bcfg["capsize"],
                    capthick=bcfg["error_line_width"],
                    zorder=4,
                )
                if self.horizontal:
                    self.ax.errorbar(self.values[i], positions[i], xerr=err, **kw)
                else:
                    self.ax.errorbar(positions[i], self.values[i], yerr=err, **kw)

        if self.show_values:
            for i, v in enumerate(self.values):
                sign = 1 if v >= 0 else -1
                reach = 0.0
                if self.errors is not None:
                    reach = self.errors[0 if sign < 0 else 1, i]
                tip = v + sign * reach
                xy = (tip, positions[i]) if self.horizontal else (positions[i], tip)
                offset = (4 * sign, 0) if self.horizontal else (0, 4 * sign)
                if self.horizontal:
                    ha, va = ("left" if sign > 0 else "right"), "center"
                else:
                    ha, va = "center", ("bottom" if sign > 0 else "top")
                self.ax.annotate(
                    f"{v:g}",
                    xy=xy,
                    xytext=offset,
                    textcoords="offset points",
                    ha=ha,
                    va=va,
                    fontsize=self.cfg["font"]["size"]["legend"],
                )
        self.ax.tick_params(
            labelsize=self.cfg["font"]["size"]["base"] - 2, length=0, pad=8
        )
        super().build_plot()


class GroupedBarPlot(BasePlot):
    """Bar chart that splits the bars of each category into groups.

    Each value is identified by a ``(category, group)`` pair. Pairs that repeat
    are aggregated: the bar shows their mean and, in grouped (side by side)
    mode, error bars extend from the mean to the minimum and maximum. Error
    bars are drawn only for pairs with more than one value.

    With ``stacked=True`` the groups are stacked on top of each other instead
    of placed side by side, and error bars are omitted. A missing
    ``(category, group)`` pair counts as zero when stacking.

    Colors come from ``cfg["bar"]["colors"]`` (one per group, cycling) and
    error bar colors from ``cfg["bar"]["error_colors"]`` (one per group,
    cycling). This class has its own copy of the configuration, so changing
    :class:`BarPlot`'s ``cfg`` does not affect it.

    :param categories: Category of each value (one tick on the categorical
        axis per distinct category).
    :param values: One value per entry in ``categories``.
    :param groups: Group of each value; distinct groups get distinct colors
        and legend entries.
    :param stacked: If ``True``, stack the groups and omit error bars.
    :param horizontal: If ``True``, draw horizontal bars.
    :param show_values: If ``True``, write each bar's value on or next to it.
    :param kwargs: Forwarded to :class:`BasePlot` (``title``, ``x_label``,
        ``y_label``, ``disclaimer``).
    :raises ValueError: If ``categories``, ``values`` and ``groups`` do not
        have the same length.
    """

    cfg: dict = copy.deepcopy(BarPlot.cfg)

    def __init__(
        self,
        categories: Sequence[Hashable],
        values: Sequence[float],
        groups: Sequence[Hashable],
        stacked: bool = False,
        horizontal: bool = False,
        show_values: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.stacked = stacked
        self.horizontal = horizontal
        self.show_values = show_values

        categories = list(categories)
        groups = list(groups)
        values = np.asarray(values, dtype=float)
        if not (len(categories) == len(groups) == values.size):
            raise ValueError(
                f"`categories` ({len(categories)}), `values` ({values.size}) and "
                f"`groups` ({len(groups)}) must have the same length."
            )

        # Distinct labels, in order of first appearance
        self.categories = list(dict.fromkeys(categories))
        self.groups = list(dict.fromkeys(groups))

        cells: dict[tuple, list[float]] = {}
        for c, g, v in zip(categories, groups, values):
            cells.setdefault((g, c), []).append(v)

        shape = (len(self.groups), len(self.categories))
        self.means = np.full(shape, np.nan)
        self.lower = np.zeros(shape)
        self.upper = np.zeros(shape)
        self.counts = np.zeros(shape, dtype=int)
        for j, g in enumerate(self.groups):
            for i, c in enumerate(self.categories):
                cell = cells.get((g, c))
                if cell:
                    mean = np.mean(cell)
                    self.means[j, i] = mean
                    self.lower[j, i] = mean - np.min(cell)
                    self.upper[j, i] = np.max(cell) - mean
                    self.counts[j, i] = len(cell)

    def build_plot(self):
        bcfg = self.cfg["bar"]
        n_groups = len(self.groups)
        positions = np.arange(len(self.categories))
        draw = self.ax.barh if self.horizontal else self.ax.bar
        size_key = "height" if self.horizontal else "width"
        base_key = "left" if self.horizontal else "bottom"

        bar_size = bcfg["width"] if self.stacked else bcfg["width"] / n_groups
        base = np.zeros(len(self.categories))

        for j, group in enumerate(self.groups):
            color = bcfg["colors"][j % len(bcfg["colors"])]
            error_color = bcfg["error_colors"][j % len(bcfg["error_colors"])]
            vals = self.means[j]
            present = ~np.isnan(vals)
            offset = 0.0 if self.stacked else (j - (n_groups - 1) / 2) * bar_size
            pos = positions + offset

            kwargs = {size_key: bar_size, "color": color, "zorder": 3}
            if self.stacked:
                kwargs[base_key] = base[present]
            draw(pos[present], vals[present], label=str(group), **kwargs)

            for i in np.flatnonzero(present):
                v = vals[i]
                tip = v
                if not self.stacked and self.counts[j, i] > 1:
                    err = np.array([[self.lower[j, i]], [self.upper[j, i]]])
                    ekw = dict(
                        fmt="none",
                        ecolor=error_color,
                        elinewidth=bcfg["error_line_width"],
                        capsize=bcfg["capsize"],
                        capthick=bcfg["error_line_width"],
                        zorder=4,
                    )
                    if self.horizontal:
                        self.ax.errorbar(v, pos[i], xerr=err, **ekw)
                    else:
                        self.ax.errorbar(pos[i], v, yerr=err, **ekw)
                    tip = v + (self.upper[j, i] if v >= 0 else -self.lower[j, i])

                if self.show_values:
                    self._annotate(v, pos[i], tip, base[i])

            if self.stacked:
                base = base + np.nan_to_num(vals)

        if self.horizontal:
            self.ax.set_yticks(positions, [str(c) for c in self.categories])
            self.ax.invert_yaxis()
            self.ax.xaxis.grid(True, color="#e3e8ec", zorder=0)
        else:
            self.ax.set_xticks(positions, [str(c) for c in self.categories])
            self.ax.yaxis.grid(True, color="#e3e8ec", zorder=0)

        self.ax.tick_params(
            labelsize=self.cfg["font"]["size"]["base"] - 2, length=0, pad=8
        )
        self.ax.legend(fontsize=self.cfg["font"]["size"]["legend"], frameon=False)

        super().build_plot()

    def _annotate(self, value: float, pos: float, tip: float, base: float):
        """Write a bar's value on it (stacked) or just past its tip (grouped).

        :param value: Value of the bar.
        :param pos: Position of the bar along the categorical axis.
        :param tip: Where the bar, including its error bar, ends.
        :param base: Where the bar starts (non-zero only when stacked).
        """
        fontsize = self.cfg["font"]["size"]["legend"]
        if self.stacked:
            center = base + value / 2
            xy = (center, pos) if self.horizontal else (pos, center)
            self.ax.annotate(
                f"{value:g}", xy=xy, ha="center", va="center", fontsize=fontsize
            )
            return

        sign = 1 if value >= 0 else -1
        xy = (tip, pos) if self.horizontal else (pos, tip)
        if self.horizontal:
            offset, ha, va = (4 * sign, 0), "left" if sign > 0 else "right", "center"
        else:
            offset, ha, va = (0, 4 * sign), "center", "bottom" if sign > 0 else "top"
        self.ax.annotate(
            f"{value:g}",
            xy=xy,
            xytext=offset,
            textcoords="offset points",
            ha=ha,
            va=va,
            fontsize=fontsize,
        )