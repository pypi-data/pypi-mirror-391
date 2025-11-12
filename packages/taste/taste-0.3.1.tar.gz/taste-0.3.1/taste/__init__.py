"""
Single module containing all Plot classes.
"""

from operator import itemgetter
from typing import Iterable, Optional, Union
from math import pi, sin, cos

import matplotlib.pyplot as plt
from matplotlib import rcParams as mpl_params
from matplotlib.axes import Axes
from matplotlib.patches import Wedge
from pint import Quantity, UnitRegistry

VT = "vertical"
HT = "horizontal"
PI_DIV_360 = pi / 360.0


def recalc_size(
        size: Union[Iterable[float], Iterable[int], Iterable[Quantity]],
        dpi: float
) -> Iterable[float]:
    ureg = UnitRegistry()
    nums = (float, int)
    qtt = Quantity

    # require consistent units i.e. inches or Pint quantities
    if isinstance(size[0], qtt) and isinstance(size[1], qtt):
        # use the same registry otherwise everything blows up
        wreg = size[0].units._REGISTRY
        hreg = size[1].units._REGISTRY
        if size[0].units == wreg.pixel and size[1].units == hreg.pixel:
            return (
                float(size[0].magnitude / dpi),
                float(size[1].magnitude / dpi)
            )
        else:
            return (
                float(size[0].to(ureg.inch).magnitude),
                float(size[1].to(ureg.inch).magnitude)
            )
    elif isinstance(size[0], nums) and isinstance(size[1], nums):
        return size


def resolve_text_pos(origin, value, pos):
    if pos == "top":
        value = f"{value}\n{origin}"
    elif pos == "bottom":
        value = f"{origin}\n{value}"
    elif pos == "left":
        value = f"{value} {origin}"
    elif pos == "right":
        value = f"{origin} {value}"
    else:
        raise Exception(
            f"Invalid slice percentage position {pos}."
            " Use 'top', 'bottom', 'left', 'right'."
        )
    return value


class AggBackend:
    def __init__(self):
        self.old_backend = None

    def __enter__(self):
        self.old_backend = plt.get_backend()
        plt.switch_backend("Agg")

    def __exit__(self, *_, **__):
        plt.switch_backend(self.old_backend)


class FigureContext:
    def __init__(self, figure=None, old_on_enter=False):
        self.old_on_enter = old_on_enter
        self.old_figure = None

        if not self.old_on_enter:
            self.old_figure = plt.gcf()

        self.figure = figure or plt.figure()

    def __enter__(self):
        if self.old_on_enter:
            self.old_figure = plt.gcf()
        plt.figure(self.figure.number)
        return self.figure

    def __exit__(self, *_, **__):
        plt.figure(self.old_figure.number)
        if self.old_on_enter:
            self.old_figure = None


class FigureCleanMixin:
    def __del__(self):
        if not hasattr(self, "figure"):
            return
        plt.close(self.figure)


class PiePlot(FigureCleanMixin):
    def __init__(
            self, slices, slice_edge_labels: Iterable = None,
            slice_percentage: Union[bool, str] = False,
            slice_percentage_format: str = "%1.1f%%",
            slice_percentage_pos: Union[str, Iterable[str]] = "bottom",
            slice_percentage_labels: Iterable = None,
            explode: Iterable = None, shadow: bool = False,
            title: str = None, title_options: dict = None,
            caption: str = None, caption_options: dict = None,
            legend: bool = False, legend_options: dict = None,
            labeldistance: float = 1.1, pctdistance: float = 0.6,
            legend_detect: str = "all_slices", center: Iterable = (0, 0),
            rotation: float = 0, plot_options: dict = None,
            radius: float = 1.0, scale: float = 1.0,
            dpi: float = mpl_params["figure.dpi"]
    ):
        # MPL discards multiple critical data in this plot such as center.
        # Not quite sure why would you discard such info as it's critical for
        # reconstructing the plot and scaling...
        self._center = center
        self._labeldistance = labeldistance
        self._pctdistance = pctdistance

        if explode is None:
            explode = [0] * len(slices)
        self._explode = explode

        self._scale = scale
        self._slice_percentage_format = slice_percentage_format
        self._slice_percentage_pos = slice_percentage_pos
        self._autopct_placeholder = "?" * 20
        self._autotexts = []
        self._texts = []

        # matplotlib.org/api/_as_gen/matplotlib.pyplot.pie.html
        plot_options = plot_options or {}

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.legend.html
        # auto          -> Doesn't work here, can't label in pie()
        # all_slices    -> 2nd option, fetch all slice refs in order,
        #                  map labels
        #                  -> "labels" key in legend_options is required now
        #                     but defaults to slice labels on axis
        # select_slices -> 2nd option, but allows selecting slices with index
        #               -> {"handles": [0, 2, 4], "labels": ["a", "b", "c"]}
        # manual        -> 3rd option, handles (refs) + labels passed directly
        legend_options = legend_options or {"labels": slice_edge_labels}

        if slice_percentage:
            plot_options["autopct"] = self.slice_percentage_format
        else:
            # well, it's stupid, but anything better failed
            plot_options["autopct"] = self._autopct_placeholder

        # matplotlib.org/api/_as_gen/matplotlib.pyplot.suptitle.html
        caption_options = caption_options or {
            "fontsize": 14, "fontweight": "bold"
        }

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.set_title.html
        title_options = title_options or {}

        with AggBackend(), FigureContext() as fig:
            self.figure = fig
            self.dpi = dpi

            patches, texts, autotexts = self.unpack_pie_return(plt.pie(
                x=slices, labels=slice_edge_labels, explode=explode,
                shadow=shadow, startangle=rotation, center=center,
                radius=radius, **plot_options
            ), bool(plot_options.get("autopct")))

            self._radius = radius

            # store plot properties, otherwise need to dig through slice
            # properties and calculate which text is for edge and for %
            # which will become error prone later with MPL code changes
            self._autotexts = autotexts
            self._texts = texts

            ax = self.figure.axes[0]
            ax.axis("equal")

            if slice_percentage_labels:
                self.draw_percentage_labels(
                    texts=autotexts, labels=slice_percentage_labels,
                    join_labels=bool(slice_percentage)
                )

            # major figure/plot title
            if caption:
                self.figure.suptitle(caption, **caption_options)

            # minor title for a single plot via Axes object
            if title:
                ax.set_title(title, **title_options)

            lopts = legend_options
            if legend and legend_detect == "auto":
                raise Exception(
                    "Auto-detection doesn't work for PiePlot."
                    " Use 'all_slices', 'select_slices' or 'manual'."
                )
            elif legend and legend_detect == "all_slices":
                ax.legend(handles=patches, **lopts)
            elif legend and legend_detect == "select_slices":
                ax.legend(
                    handles=itemgetter(*lopts["handles"])(ax.patches),
                    labels=lopts["labels"]
                )
            elif legend and legend_detect == "manual":
                ax.legend(**lopts)

    def draw_percentage_labels(
            self, texts, labels: Iterable, join_labels: bool = False
    ):
        raw_pos = self.slice_percentage_pos
        for idx, zipped in enumerate(zip(texts, labels)):
            item, label = zipped
            old_value = item.get_text()

            # initial values
            value = label
            pos = raw_pos

            if join_labels:
                if not isinstance(raw_pos, str):
                    pos = pos[idx]
                value = resolve_text_pos(old_value, label, pos)
            item.set_text(value)

    @staticmethod
    def unpack_pie_return(result, autopct_used: bool):
        autotexts = []
        patches, *texts = result

        if autopct_used:
            texts, autotexts = texts

        return patches, texts, autotexts

    @property
    def slice_percentage_format(self):
        return self._slice_percentage_format

    @slice_percentage_format.setter
    def slice_percentage_format(self, value):
        self._slice_percentage_format = value

    @property
    def slice_percentage_pos(self):
        return self._slice_percentage_pos

    @slice_percentage_pos.setter
    def slice_percentage_pos(self, value):
        self._slice_percentage_pos = value

    @property
    def dpi(self) -> float:
        return self.figure.get_dpi()

    @dpi.setter
    def dpi(self, value: float):
        self.figure.set_dpi(value)

    @property
    def center(self) -> Iterable:
        return self._center

    @center.setter
    def center(self, value: Iterable):
        raise NotImplementedError("Not yet.")

    @property
    def radius(self):
        return [
            float(item.r)
            for item in self.figure.axes[0].patches
            if isinstance(item, Wedge)  # can be Shadow as well
        ]

    @radius.setter
    def radius(self, value: Union[int, float, Iterable]):
        if not value:
            return

        dpi = self.dpi
        explode = self._explode
        center = self.center
        ax = self.figure.axes[0]
        patches = ax.patches
        inst = isinstance
        texts = (
            (self._autotexts, self._pctdistance),
            (self._texts, self._labeldistance)
        )

        if isinstance(value, (float, int)):
            value = [value] * len(patches)

        radii = []
        for val, patch in zip(value, patches):
            if inst(val, Quantity) or not inst(val, Iterable):
                inch_size = recalc_size(size=[val, val], dpi=dpi)
                patch.set_radius(inch_size[0])
                radii.append(inch_size[0])

        for text, distance in texts:
            for val, patch, txt, expl in zip(radii, patches, text, explode):
                dis_rad = distance * val  # just convenient caching
                if inst(val, Quantity) or not inst(val, Iterable):
                    self.handle_texts(val, center, patch, txt, dis_rad, expl)

    @staticmethod
    def handle_texts(radius, center, patch, text, dis_rad, explode):
        """
        Reposition texts on the slices (on circle arc & radius).
        """
        pie_center_x, pie_center_y = center

        # MPL: Wedge((x, y), radius, 360. * min(theta1, theta2), ...)
        #                            -------
        # pulling thetas from Wedge, need to remove that 360
        thetam = PI_DIV_360 * (patch.theta1 + patch.theta2)
        text.set_position((
            pie_center_x + explode + dis_rad * cos(thetam),
            pie_center_y + explode + dis_rad * sin(thetam)
        ))

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value: Union[int, float, Iterable[float]]):
        current = self.figure.get_size_inches()
        factor = [value, value]  # expect number

        if not isinstance(value, (float, int)):
            factor = [value[0], value[1]]

        self._scale = factor
        self.figure.set_size_inches(
            w=current[0] * factor[0], h=current[1] * factor[1]
        )


class BarPlot(FigureCleanMixin):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            grid: bool = False,
            grid_options: dict = None,
            origin_lines: bool = False,
            origin_lines_options: dict = None,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            bar_axis_rotation: float = 0,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            value_axis_rotation: float = 0,
            value_top_labels: Iterable = None,
            value_top_rotation: float = 0,
            value_top_offset: float = 0.2,
            title: str = None, title_options: dict = None,
            caption: str = None, caption_options: dict = None,
            legend: bool = False, legend_options: dict = None,
            legend_detect: str = "auto", plot_options: dict = None,
            orientation: str = VT, size: Optional[Iterable] = None,
            dpi: float = mpl_params["figure.dpi"], scale: float = 1.0
    ):
        self._scale = scale

        # matplotlib.org/api/_as_gen/matplotlib.pyplot.bar.html
        # matplotlib.org/api/_as_gen/matplotlib.pyplot.barh.html
        plot_options = plot_options or {"label": "BarPlot"}

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.grid.html
        grid_options = grid_options or {}

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.legend.html
        # but is kind of useless *before* the references are created in its
        # original shape, therefore legend_detect manipulates legend() calls:
        #
        # auto        -> 1st option, fetch label from plot instance
        # all_bars    -> 2nd option, fetch all bar refs in order, map labels
        #                -> "labels" key in legend_options is required now
        #                   but defaults to bar labels on axis
        # select_bars -> 2nd option, but allows selecting bars with index
        #                -> {"handles": [0, 2, 4], "labels": ["a", "b", "c"]}
        # manual -> 3rd option, handles (refs) + labels passed directly
        legend_options = legend_options or {"labels": bar_axis_labels}

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.axvline.html
        # matplotlib.org/api/_as_gen/matplotlib.lines.Line2D.html
        origin_lines_options = origin_lines_options or {"x": {}, "y": {}}

        # matplotlib.org/api/_as_gen/matplotlib.pyplot.suptitle.html
        caption_options = caption_options or {
            "fontsize": 14, "fontweight": "bold"
        }

        # matplotlib.org/api/_as_gen/matplotlib.axes.Axes.set_title.html
        title_options = title_options or {}

        with AggBackend(), FigureContext() as fig:
            self.figure = fig
            self.dpi = dpi
            self.size = size

            if orientation == VT:
                plt.bar(x=bars, height=values, **plot_options)
            elif orientation == HT:
                plt.barh(y=bars, width=values, **plot_options)
            else:
                raise Exception(f"Invalid orientation {orientation}")

            ax = self.figure.axes[0]

            # grid lines
            ax.grid(grid, **grid_options)

            # all labels
            self.draw_labels(
                ax=ax, bar=bar_label, value=value_label,
                bar_axis=bar_axis_labels, value_axis=value_axis_labels,
                bar_axis_ticks=bar_axis_ticks,
                value_axis_ticks=value_axis_ticks,
                bar_axis_rotation=bar_axis_rotation,
                value_axis_rotation=value_axis_rotation,
                value_top=value_top_labels, value_top_offset=value_top_offset,
                value_top_rotation=value_top_rotation, orientation=orientation
            )

            # major figure/plot title
            if caption:
                self.figure.suptitle(caption, **caption_options)

            # minor title for a single plot via Axes object
            if title:
                ax.set_title(title, **title_options)

            # lines crossed on [0, 0]
            if origin_lines:
                ax.axvline(x=0, **origin_lines_options["x"])
                ax.axhline(y=0, **origin_lines_options["y"])

            lopts = legend_options
            if legend and legend_detect == "auto":
                ax.legend()
            elif legend and legend_detect == "all_bars":
                ax.legend(handles=ax.patches, **lopts)
            elif legend and legend_detect == "select_bars":
                ax.legend(
                    handles=itemgetter(*lopts["handles"])(ax.patches),
                    labels=lopts["labels"]
                )
            elif legend and legend_detect == "manual":
                ax.legend(**lopts)

    def draw_labels(  # pylint: disable=too-many-arguments
            self, ax: Axes, bar: Optional[str], value: Optional[str],
            bar_axis: Optional[Iterable], value_axis: Optional[Iterable],
            bar_axis_rotation: float, value_axis_rotation: float,
            value_top: Optional[Iterable], value_top_offset: float,
            value_top_rotation: float,
            bar_axis_ticks: Optional[Iterable],
            value_axis_ticks: Optional[Iterable],
            orientation: str = VT
    ):
        # horizontal label
        if orientation == HT:
            if bar:
                ax.set_ylabel(bar)
            if value:
                ax.set_xlabel(value)
            if bar_axis:
                if bar_axis_ticks:
                    ax.set_yticks(bar_axis_ticks)
                else:
                    ax.set_yticks(range(len(bar_axis)))
                ax.set_yticklabels(bar_axis, rotation=bar_axis_rotation)
            if value_axis:
                if value_axis_ticks:
                    ax.set_xticks(value_axis_ticks)
                else:
                    ax.set_xticks(range(len(value_axis)))
                ax.set_xticklabels(value_axis, rotation=value_axis_rotation)

        # vertical label
        elif orientation == VT:
            if bar:
                ax.set_xlabel(bar)
            if value:
                ax.set_ylabel(value)
            if bar_axis:
                if bar_axis_ticks:
                    ax.set_xticks(bar_axis_ticks)
                else:
                    ax.set_xticks(range(len(bar_axis)))
                ax.set_xticklabels(bar_axis, rotation=bar_axis_rotation)
            if value_axis:
                if value_axis_ticks:
                    ax.set_yticks(value_axis_ticks)
                else:
                    ax.set_yticks(range(len(value_axis)))
                ax.set_yticklabels(value_axis, rotation=value_axis_rotation)

        if value_top:
            self.draw_bar_top(
                ax=ax, values=value_top, offset=value_top_offset,
                orientation=orientation, rotation=value_top_rotation
            )

    def draw_bar_top(  # pylint: disable=too-many-locals,too-many-arguments
            self, ax: Axes, values: Iterable, offset: float,
            rotation: float, orientation: str = VT
    ):
        attr_x = attr_x_start = attr_y = attr_y_start = None

        if orientation == VT:
            attr_y = "get_height"
            attr_y_start = "get_y"
            attr_x = "get_width"
            attr_x_start = "get_x"
        elif orientation == HT:
            attr_x = "get_height"
            attr_x_start = "get_y"
            attr_y = "get_width"
            attr_y_start = "get_x"

        for bar, val in zip(ax.patches, values):
            x_start = getattr(bar, attr_x_start)()
            y_start = getattr(bar, attr_y_start)()
            height = getattr(bar, attr_y)()

            pos = [
                x_start + getattr(bar, attr_x)() / 2.0,
                # offset mirrored on origin
                y_start + height + offset * height / abs(height)
            ]

            if orientation == HT:
                pos = pos[-1::-1]  # swap values

            ax.text(
                x=pos[0], y=pos[1], s=val, ha="center",
                va="center", rotation=rotation
            )

    @property
    def dpi(self) -> float:
        return self.figure.get_dpi()

    @dpi.setter
    def dpi(self, value: float):
        self.figure.set_dpi(value)

    @property
    def size(self):
        return [float(item) for item in self.figure.get_size_inches()]

    @size.setter
    def size(self, value):
        if not value:
            return
        inch_size = recalc_size(size=value, dpi=self.dpi)
        self.figure.set_size_inches(w=inch_size[0], h=inch_size[1])

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value: Union[int, float, Iterable[float]]):
        current = self.figure.get_size_inches()
        factor = [value, value]  # expect number

        if not isinstance(value, (float, int)):
            factor = [value[0], value[1]]

        self._scale = factor
        self.figure.set_size_inches(
            w=current[0] * factor[0], h=current[1] * factor[1]
        )
