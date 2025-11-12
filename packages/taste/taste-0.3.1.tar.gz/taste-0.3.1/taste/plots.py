"""
Module for user-friendlier classes of basic plot shapes.
"""
from typing import Iterable
from taste import BarPlot, HT, VT


class HorizontalBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            plot_options=plot_options,
            orientation=HT, grid=False, legend=False, **kwargs
        )


class HorizontalGridBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            grid_options: dict = None,
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            grid_options=grid_options,
            plot_options=plot_options,
            orientation=HT, grid=True, legend=False, **kwargs
        )


class HorizontalLegendBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            legend_options: dict = None,
            legend_detect: str = "auto",
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            legend_options=legend_options,
            plot_options=plot_options,
            orientation=HT, grid=False, legend=True,
            legend_detect=legend_detect, **kwargs
        )


class VerticalBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            plot_options=plot_options,
            orientation=VT, grid=False, legend=False, **kwargs
        )


class VerticalGridBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            grid_options: dict = None,
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            grid_options=grid_options,
            plot_options=plot_options,
            orientation=VT, grid=True, legend=False, **kwargs
        )


class VerticalLegendBarPlot(BarPlot):
    def __init__(  # pylint: disable=too-many-arguments
            self, bars, values,
            bar_label: str = None, value_label: str = None,
            bar_axis_labels: Iterable = None,
            bar_axis_ticks: Iterable = None,
            value_axis_labels: Iterable = None,
            value_axis_ticks: Iterable = None,
            title: str = None, caption: str = None,
            legend_options: dict = None,
            legend_detect: str = "auto",
            plot_options: dict = None, **kwargs
    ):
        super().__init__(
            bars=bars, values=values,
            bar_label=bar_label, value_label=value_label,
            bar_axis_labels=bar_axis_labels,
            bar_axis_ticks=bar_axis_ticks,
            value_axis_labels=value_axis_labels,
            value_axis_ticks=value_axis_ticks,
            title=title, caption=caption,
            legend_options=legend_options,
            plot_options=plot_options,
            orientation=VT, grid=False, legend=True,
            legend_detect=legend_detect, **kwargs
        )
