# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:         common/types.py
# Purpose:      Music21 Typing aids
#
# Authors:      Michael Scott Asato Cuthbert
#
# Copyright:    Copyright © 2021 Michael Scott Asato Cuthbert and the music21 Project
# License:      BSD, see license.txt
# ------------------------------------------------------------------------------
from fractions import Fraction
import typing as t

from music21.common.enums import OffsetSpecial

if t.TYPE_CHECKING:
    import music21  # pylint: disable=unused-import

DocOrder = t.List[t.Union[str, t.Callable]]
OffsetQL = t.Union[float, Fraction]
OffsetQLSpecial = t.Union[float, Fraction, OffsetSpecial]
OffsetQLIn = t.Union[int, float, Fraction]

StreamType = t.TypeVar('StreamType', bound='music21.stream.Stream')
StreamType2 = t.TypeVar('StreamType2', bound='music21.stream.Stream')
M21ObjType = t.TypeVar('M21ObjType', bound='music21.base.Music21Object')
M21ObjType2 = t.TypeVar('M21ObjType2', bound='music21.base.Music21Object')  # when you need another

ClassListType = t.Union[str, t.Iterable[str], t.Type[M21ObjType], t.Iterable[t.Type[M21ObjType]]]
StepName = t.Literal['C', 'D', 'E', 'F', 'G', 'A', 'B']
