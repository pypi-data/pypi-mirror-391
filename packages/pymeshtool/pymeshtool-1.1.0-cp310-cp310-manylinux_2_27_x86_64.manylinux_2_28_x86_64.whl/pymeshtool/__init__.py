# import the C-implementation
from pymeshtool._cext import *
import enum


__version__ = '1.1.0'


__author__ = (
  {'name': 'Matthias A.F. Gsell', 'email': 'matthias.gsell@medunigraz.at'},
  {'name': 'Benedikt Klöckl', 'email': 'benedikt.kloeckl@medunigraz.at'}
)


class MeshInputFormat(str, enum.Enum):
    """
    Enumeration of all supported mesh input formats.
    """
    carp_txt = 'carp_txt'
    carp_bin = 'carp_bin'
    vtk = 'vtk'
    vtk_bin = 'vtk_bin'
    vtu = 'vtu'
    mmg = 'mmg'
    netgen = 'neu'
    stellar = 'stellar'
    obj = 'obj'
    off = 'off'
    gmsh = 'gmsh'
    purk = 'purk'
    vcflow = 'vcflow'


class MeshOutputFormat(str, enum.Enum):
    """
    Enumeration of all supported mesh output formats.
    """
    carp_txt = 'carp_txt'
    carp_bin = 'carp_bin'
    vtk = 'vtk'
    vtk_bin = 'vtk_bin'
    vtu = 'vtu'
    vtk_polydata = 'vtk_polydata'
    mmg = 'mmg'
    netgen = 'neu'
    obj = 'obj'
    off = 'off'
    stellar = 'stellar'
    vcflow = 'vcflow'


class MeshElementType(int, enum.Enum):
    """
    Enumeration of all mesh element types.
    """
    tetra = 0
    hexa = 1
    octa = 2
    pyramid = 3
    prism = 4
    quad = 5
    tri = 6
    line = 7
    node = 8

class MeshClouddataInterpolationMode(int, enum.Enum):
    """
    Enumeration of available clouddata interpolation modes.
    """
    localized_shepard = 0
    global_shepard = 1
    radial_basis_function = 2


class MeshExtractUnreachableMode(int, enum.Enum):
    """
    Enumeration of mesh unreachable extraction modes.
    """
    smallest = -1
    largest = +1
    all = 0


class ImageDType(int, enum.Enum):
    """
    Enumeration of image voxel data types.
    """
    uint8 = 1
    int8 = 2
    uint16 = 3
    int16 = 4
    uint32 = 5
    int32 = 6
    uint64 = 7
    int64 = 8
    float32 = 9
    float64 = 10
    color_scalar = 11

class ImageExtrusionMode(int, enum.Enum):
    """
    Enumeration of image extrusion modes.
    """
    inwards = -1
    outwards = +1
    everywhere = 0