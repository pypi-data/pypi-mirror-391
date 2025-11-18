






from __future__ import annotations
from typing import TYPE_CHECKING
from tbapi.common.decorators import tb_class, tb_interface
from tbapi.common.converters import to_python_datetime, to_net_datetime
from datetime import datetime
import Tickblaze.Scripts.Api.Bases as Bases
_BandShading = Bases.Indicator.BandShading
from typing import Any, overload
from abc import ABC, abstractmethod

@tb_class(_BandShading)
class BandShading():
    """Represents a shading between two values or plot series."""

    @overload
    @staticmethod
    def new(FirstSource: Any, SecondSource: Any, FirstColor: Color | None, SecondColor: Color | None) -> "BandShading":
        """Constructor overload with arguments: FirstSource, SecondSource, FirstColor, SecondColor"""
        ...
    @staticmethod
    def new(*args, **kwargs):
        """Generic factory method for BandShading. Use overloads for IDE type hints."""
        return BandShading(*args, **kwargs)

    @property
    def first_source(self) -> Any:
        val = self._value.FirstSource
        return val
    @first_source.setter
    def first_source(self, val: Any):
        tmp = self._value
        tmp.FirstSource = val
        self._value = tmp
    @property
    def second_source(self) -> Any:
        val = self._value.SecondSource
        return val
    @second_source.setter
    def second_source(self, val: Any):
        tmp = self._value
        tmp.SecondSource = val
        self._value = tmp
    @property
    def first_color(self) -> Color | None:
        val = self._value.FirstColor
        return val
    @first_color.setter
    def first_color(self, val: Color | None):
        tmp = self._value
        tmp.FirstColor = val
        self._value = tmp
    @property
    def second_color(self) -> Color | None:
        val = self._value.SecondColor
        return val
    @second_color.setter
    def second_color(self, val: Color | None):
        tmp = self._value
        tmp.SecondColor = val
        self._value = tmp



