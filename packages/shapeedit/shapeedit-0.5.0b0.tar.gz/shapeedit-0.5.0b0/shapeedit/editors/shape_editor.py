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

from typing import List
from shapeio.shape import Shape

from .lodcontrol_editor import _LodControlEditor


class ShapeEditor:
    """
    Wrapper for safely editing the `Shape` data structure.

    The `ShapeEditor` class provides a high-level interface to safely edit
    the internal data of a `Shape` instance while maintaining the
    consistency and invariants required for the shape to remain
    valid and usable in Microsoft Train Simulator (MSTS) and
    Open Rails. It exposes operations such as accessing vertices,
    triangles, points, UV points and normals. It also allows you to
    modify, remove and add new geometry in an existing shape.

    Example:
        >>> import shapeio
        >>> from shapeedit import ShapeEditor
        >>>
        >>> my_shape = shapeio.load("./path/to/example.s")
        >>>
        >>> shape_editor = ShapeEditor(my_shape)
        >>> sub_object = shape_editor.lod_control(0).distance_level(200).sub_object(0)
        >>>
        >>> # Set point values of all vertices in the subobject.
        >>> for vertex in sub_object.vertices():
        ...     vertex.point.x = 0.0
        ...     vertex.point.y = 1.0
        ...     vertex.point.z = 2.0
        >>>
        >>> shapeio.dump(my_shape, "./path/to/output.s")
    """

    def __init__(self, shape: Shape):
        """
        Initializes a ShapeEditor instance.

        Wraps a `Shape` instance to provide safe editing operations.

        Args:
            shape (Shape): The shape instance to be edited.

        Raises:
            TypeError: If `shape` is None or not an instance of `Shape`.
        """
        if shape is None:
            raise TypeError("Parameter 'shape' must be a shape.Shape, not None")

        if not isinstance(shape, Shape):
            raise TypeError(f"Parameter 'shape' must be of type shape.Shape, but got {type(shape).__name__}")

        self._shape = shape
    
    def __repr__(self):
        return f"ShapeEditor({self._shape})"

    def lod_control(self, lod_control_index: int) -> _LodControlEditor:
        """
        Returns an editor for a specific LOD (Level of Detail) control.

        Provides access to a specific LOD control of the shape,
        allowing safe edits to its children.

        Args:
            lod_control_index (int): Index of the LOD control to edit.

        Returns:
            _LodControlEditor: An editor instance for the specified LOD control.

        Raises:
            TypeError: If `lod_control_index` is not an integer.
            IndexError: If `lod_control_index` is out of the valid range.
        """
        if not isinstance(lod_control_index, int):
            raise TypeError(f"Parameter 'lod_control_index' must be of type int, but got {type(lod_control_index).__name__}")
        
        if not (0 <= lod_control_index < len(self._shape.lod_controls)):
            raise IndexError(
                f"lod_control_index {lod_control_index} out of range "
                f"(valid range: 0 to {len(self._shape.lod_controls) - 1})"
            )

        lod_control = self._shape.lod_controls[lod_control_index]
        return _LodControlEditor(lod_control, _parent=self)

    def lod_controls(self) -> List[_LodControlEditor]:
        """
        Returns editors for all LOD (Level of Detail) controls of the shape.

        Each editor allows safe modifications to its respective LOD control.

        Returns:
            List[_LodControlEditor]: A list of editors, one for each LOD control.
        """
        return [
            _LodControlEditor(lod_control, _parent=self)
            for lod_control in self._shape.lod_controls
        ]