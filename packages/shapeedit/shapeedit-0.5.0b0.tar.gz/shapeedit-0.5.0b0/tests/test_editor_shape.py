"""
This file is part of ShapeEdit.

Copyright (C) 2025 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
from shapeio.shape import Point

from shapeedit import ShapeEditor
from shapeedit.editors.lodcontrol_editor import _LodControlEditor


def test_shape_editor_lod_controls(global_storage):
    shape = global_storage["shape_DK10f_A1tPnt5dLft"]
    editor = ShapeEditor(shape)

    lod_controls = editor.lod_controls()
    assert len(lod_controls) == 1


def test_shape_editor_lod_control_by_index(global_storage):
    shape = global_storage["shape_DK10f_A1tPnt5dLft"]
    editor = ShapeEditor(shape)

    lod_control = editor.lod_control(0)
    assert isinstance(lod_control, _LodControlEditor)


@pytest.mark.parametrize("bad_index", [
    1, -1, 100
])
def test_shape_editor_lod_control_by_index_raises(global_storage, bad_index):
    shape = global_storage["shape_DK10f_A1tPnt5dLft"]
    editor = ShapeEditor(shape)

    with pytest.raises(IndexError):
        editor.lod_control(bad_index)


@pytest.mark.parametrize("bad_input", [
    None, 1, Point(1, 2, 3)
])
def test_shape_editor_bad_input_raises(global_storage, bad_input):
    shape = global_storage["shape_DK10f_A1tPnt5dLft"]

    with pytest.raises(TypeError):
        ShapeEditor(bad_input)


@pytest.mark.parametrize("bad_input", [
    None, Point(1, 2, 3)
])
def test_shape_editor_lod_control_bad_input_raises(global_storage, bad_input):
    shape = global_storage["shape_DK10f_A1tPnt5dLft"]
    editor = ShapeEditor(shape)

    with pytest.raises(TypeError):
        editor.lod_control(bad_input)
