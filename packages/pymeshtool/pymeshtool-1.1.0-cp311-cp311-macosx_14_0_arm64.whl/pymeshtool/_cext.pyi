
from numpy import number, ndarray
from typing import Iterable

# This file was auto-generated
#   Date: 14/11/2025, 06:54
#   Version: 1.1.0


def create_image(shape:tuple[int, int, int], itk_dtype:int, *, num_comp:int=1, origin:tuple[float, float, float]=None, voxel_size:tuple[float, float, float]=None) -> Image:
    """
    create_image(shape, itk_dtype, *, num_comp=1, origin=None, voxel_size=None)

    Create an empty image from a given shape and type.

    Parameters
    ----------
        shape: tuple[int, int, int]
            Size in X, Y, and Z direction.
        itk_dtype: int
            Image data type.
        num_comp: int, optional, default=1
            Number of components per pixel (max: 4).
        origin: tuple[float, float, float], optional, default=None
            The X, Y, and Z coordinate of the image origin.
        voxel_size: tuple[float, float, float], optional, default=None
            Voxel size in X, Y, and Z direction.

    Returns
    -------
        Image
            The generated image object.

    Raises
    ------
        TypeError
            If the shape object is None.
        PyMeshToolError
            If the shape object can't be converted to the correct C++ container.
        ValueError
            If the shape object is has negative entries.
        ValueError
            If the data type is unknown.
        PyMeshToolError
            If the origin object can't be converted to the correct C++ container.
        PyMeshToolError
            If the voxel size object can't be converted to the correct C++ container.
        ValueError
            If the voxel size object is has negative entries.

    See Also
    --------
        ImageDType

    Example
    -------
    .. code-block:: python
        # create the image
        img = pymeshtool.create_image((10, 10, 10), pymeshtool.ImageDType.int8,
                                      origin=(-5.0, -5.0, -5.0),
                                      voxel_size=(1.0, 1.0, 1.0))

        # set voxel data
        img.voxels[:,:,5] = 17
        img.voxels[0,0,0] = 1
        img.voxels[1:3,0,0] = 2
        img.voxels[0,1:3,0] = 3
        img.voxels[0,0,1:3] = 4

        # save image
        img.save('image.nrrd')
    """
    ...


def create_mesh(points:ndarray[float], elem2node_dsp:ndarray[int], elem2node_con:ndarray[int], elem_types:ndarray[int], *, elem_tags:ndarray[int]=None, num_fibers:int=1, refine_uniform:int=0) -> Mesh:
    """
    create_mesh(points, elem2node_dsp, elem2node_con, elem_types, *, elem_tags=None, num_fibers=1, refine_uniform=0)

    Create a mesh from a point cloud and an element-to-node graph.
    The element-to-node graph is defined by the displacement array,
    `elem2node_dsp`, and the connectivity array, `elem2node_dsp`.
    The connectivity array contains the indices of the points that
    span each element, while the displacement array specifies the
    start index in the connectivity array.

    Parameters
    ----------
        points: ndarray[float]
            Nx3 points array.
        elem2node_dsp: ndarray[int]
            Element-to-node displacement array.
        elem2node_con: ndarray[int]
            Element-to-node connectivity array.
        elem_types: ndarray[int]
            Element type array.
        elem_tags: ndarray[int], optional, default=None
            Element tag array.
        num_fibers: int, optional, default=1
            Number of fibers per element, either 1 or 2.
        refine_uniform: int, optional, default=0
            Number of uniform refinement iterations.

    Returns
    -------
        Mesh
            The generated mesh object.

    Raises
    ------
        ValueError
            If the points array is empty of of wrong shape.
        ValueError
            If the element-to-node displacement array is empty.
        ValueError
            If the element-to-node connectivity array is empty.
        ValueError
            If the element type array is empty.
        PyMeshToolError
            If the points array can't be converted to the correct C++ container.
        PyMeshToolError
            If the element-to-node displacement array can't be converted to the correct C++ container.
        PyMeshToolError
            If the element-to-node connectivity array can't be converted to the correct C++ container.
        PyMeshToolError
            If the element type array can't be converted to the correct C++ container.
        PyMeshToolError
            If the element tags array can't be converted to the correct C++ container.
        ValueError
            If the element arrays are not consistent.

    Example
    -------
    .. code-block:: python
        # define 4 points in 3D
        points = [[0, 0, 0], [1, 0, 0],
                  [0, 1, 0], [1, 1, 0]]

        # define triangle connectivity array
        #   T0 = (0, 1, 2)
        #   T1 = (1, 3, 2)
        e2ncon = [0, 1, 2, 1, 3, 2]

        # start indices in the `e2ncon` array
        #   T0 starts at 0
        #   T1 starts at 3
        # followed by the the total number of
        # indices in the `e2ncon` array
        e2ndsp = [0, 3, 6]

        # the element types (2 triangles)
        etypes = [pymeshtool.ElementType.tri,
                  pymeshtool.ElementType.tri]

        # create the mesh
        mesh = pymeshtool.create_mesh(points, e2ndsp,
                                      e2ncon, etypes)
    """
    ...


def get_max_par_threads() -> int:
    """
    get_max_par_threads()

    Get the maximum number of parallel OpenMP threads.

    Returns
    -------
        int
            Maximum number of OpenMP threads.

    See Also
    --------
        set_num_par_threads, get_num_par_threads
    """
    ...


def get_meshtool_git_info() -> tuple[str, str, str]:
    """
    get_meshtool_git_info()

    Get git information about MeshTool.

    Returns
    -------
        tuple[str, str, str]
            The git hash, branch, and commit date of MeshTool.
    """
    ...


def get_num_par_threads() -> int:
    """
    get_num_par_threads()

    Get the number of parallel OpenMP threads used.

    Returns
    -------
        int
            Number of OpenMP threads used

    See Also
    --------
        set_num_par_threads, get_max_par_threads
    """
    ...


def load_fibers(filename:str) -> None | ndarray[float]:
    """
    load_fibers(filename)

    Read fibers from a CARP fiber file.
    Can be a text file (*.lon) or a binary
    binary file (*.blon).

    Parameters
    ----------
        filename: str
            Path to the fibers file.

    Returns
    -------
        None
            If the loaded data is empty or of wrong dimension.
        ndarray[float]
            The fibers array.

    Raises
    ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the format is neither a lon nor a blon file.
        IOError
            If an error occurred while reading the file.
        PyMeshToolError
            If the data can't be converted to a numpy array.
    """
    ...


def load_points(filename:str) -> None | ndarray[float]:
    """
    load_points(filename)

    Read points from a CARP points file.
    Can be a text file (*.pts) or a binary
    binary file (*.bpts).

    Parameters
    ----------
        filename: str
            Path to the points file.

    Returns
    -------
        None
            If the loaded data is empty.
        ndarray[float]
            The points array.

    Raises
    ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the format is neither a pts nor a bpts file.
        PyMeshToolError
            If the data can't be converted to a numpy array.
    """
    ...


def load_vtx(filename:str) -> None | tuple[ndarray[int], str]:
    """
    load_vtx(filename)

    Read vertex indices from a CARP vtx file.

    Parameters
    ----------
        filename: str
            Path to the vertex file.

    Returns
    -------
        None
            If the loaded data is empty.
        tuple[ndarray[int], str]
            The vertex indices and the domain
            the vertices are defined for.

    Raises
    ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the format is not a vtx file.
        IOError
            If an error occurred while reading the file.
        PyMeshToolError
            If the data can't be converted to a numpy array.
    """
    ...


def save_fibers(fibers:ndarray[float], filename:str) -> None:
    """
    save_fibers(fibers, filename)

    Save fibers to a CARP fiber file.
    Can be a text file (*.lon) or a binary
    binary file (*.blon).

    Parameters
    ----------
        fibers: ndarray[float]
            The fibers to save.
        filename: str
            Path to the fibers file.

    Returns
    -------
        None

    Raises
    ------
        ValueError
            If the format is neither a lon nor a blon file.
        PyMeshToolError
            If the data can't be converted to the correct C++ container.
    """
    ...


def save_points(pnts:ndarray[float], filename:str) -> None:
    """
    save_points(pnts, filename)

    Save points to a CARP points file.
    Can be a text file (*.pts) or a binary
    binary file (*.bpts).

    Parameters
    ----------
        pnts: ndarray[float]
            The points array.
        filename: str
            Path to the points file.

    Returns
    -------
        None

    Raises
    ------
        ValueError
            If the format is neither a pts nor a bpts file.
        PyMeshToolError
            If the data can't be converted to the correct C++ container.
    """
    ...


def save_vtx(vtxdata:ndarray[int], filename:str, *, domain:str='intra') -> None:
    """
    save_vtx(vtxdata, filename, *, domain='intra')

    Write vertex indices to a CARP vtx file.

    Parameters
    ----------
        vtxdata: ndarray[int]
            The vertex data to write.
        filename: str
            Path to the vertex file.
        domain: str, optional, default='intra'
            The domain the vertices are defined on.
            Choices are:
                intra .. intrintra-callular domain
                extra .. extra-cellular domain

    Returns
    -------
        None

    Raises
    ------
        ValueError
            If the format is not a vtx file.
        IOError
            If an error occurred while writing the file.
        PyMeshToolError
            If the data can't be converted to the correct C++ container.
    """
    ...


def set_num_par_threads(np:int) -> None:
    """
    set_num_par_threads(np)

    Set the number of parallel OpenMP threads
    to be used.

    Parameters
    ----------
        np: int
            Number of parallel threads.

    Returns
    -------
        None

    See Also
    --------
        get_max_par_threads, get_num_par_threads
    """
    ...



class Mesh:
    """
    PyMeshool Mesh object.
    Wrapper class for the meshtool mt_meshdata structure.
    """

    @property
    def element_tags(self) -> ndarray[int]:
        """
        Set or get the element tags in the mesh.

        Parameters
        ----------
            tags: ndarray[int]
                The new element tags of same size.

        Returns
        -------
            ndarray[int]
                Array of the element tags in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tag data can't converted to a numpy array.
            PyMeshToolError
                If the new tag data can't converted to the correct C++ container.
            ValueError
                If the new tag data array has the wrong shape.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing tag data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the tag data.
        """
        ...


    @element_tags.setter
    def element_tags(self, tags:ndarray[int]) -> None:
        """
        Set or get the element tags in the mesh.

        Parameters
        ----------
            tags: ndarray[int]
                The new element tags of same size.

        Returns
        -------
            ndarray[int]
                Array of the element tags in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tag data can't converted to a numpy array.
            PyMeshToolError
                If the new tag data can't converted to the correct C++ container.
            ValueError
                If the new tag data array has the wrong shape.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing tag data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the tag data.
        """
        ...


    @property
    def fibers(self) -> ndarray[float]:
        """
        Set or get the fibers in the mesh.

        Parameters
        ----------
            fibers: ndarray[float]
                The new fiber data of same size.

        Returns
        -------
            ndarray[float]
                Array of the fibers in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the fiber data can't converted to a numpy array.
            PyMeshToolError
                If the new fiber data can't converted to the correct C++ container.
            ValueError
                If the new fiber data array has the wrong shape.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing fiber data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the fiber data.
        """
        ...


    @fibers.setter
    def fibers(self, fibers:ndarray[float]) -> None:
        """
        Set or get the fibers in the mesh.

        Parameters
        ----------
            fibers: ndarray[float]
                The new fiber data of same size.

        Returns
        -------
            ndarray[float]
                Array of the fibers in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the fiber data can't converted to a numpy array.
            PyMeshToolError
                If the new fiber data can't converted to the correct C++ container.
            ValueError
                If the new fiber data array has the wrong shape.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing fiber data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the fiber data.
        """
        ...


    @property
    def num_elements(self) -> int:
        """
        Get the number of elements in the mesh.

        Returns
        -------
            int
                The number of elements in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    @property
    def num_fibers(self) -> int:
        """
        Get the number of fibers in the mesh.
        Should be a value in {0, 1, 2}.

        Returns
        -------
            int
                The number of fibers in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            RuntimeError
                If the fibers array has an invalid shape.
        """
        ...


    @property
    def num_points(self) -> int:
        """
        Get the number of points in the mesh.

        Returns
        -------
            int
                The number of points in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            RuntimeError
                If the points array has an invalid shape.
        """
        ...


    @property
    def points(self) -> ndarray[float]:
        """
        Set or get the points in the mesh.

        Parameters
        ----------
            points: ndarray[float]
                The new point data of same size.

        Returns
        -------
            ndarray[float]
                Array of the points in the mesh.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing point data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the point data.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the point data can't converted to a numpy array.
            PyMeshToolError
                If the new point data can't converted to the correct C++ container.
            ValueError
                If the new point data array has the wrong shape.

        Example
        -------
        .. code-block:: python
            # load mesh from file
            mesh = pymeshtool.Mesh('mesh', format='carp_txt')

            # get mesh points
            pnts = mesh.points

            # scale mesh points
            mesh.points *= 1000.0
        """
        ...


    @points.setter
    def points(self, points:ndarray[float]) -> None:
        """
        Set or get the points in the mesh.

        Parameters
        ----------
            points: ndarray[float]
                The new point data of same size.

        Returns
        -------
            ndarray[float]
                Array of the points in the mesh.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing point data of the underlying
            mesh structure without owning the data. This means
            that the mesh object is not deleted as long as there
            are numpy arrays pointing to the point data.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the point data can't converted to a numpy array.
            PyMeshToolError
                If the new point data can't converted to the correct C++ container.
            ValueError
                If the new point data array has the wrong shape.

        Example
        -------
        .. code-block:: python
            # load mesh from file
            mesh = pymeshtool.Mesh('mesh', format='carp_txt')

            # get mesh points
            pnts = mesh.points

            # scale mesh points
            mesh.points *= 1000.0
        """
        ...


    def __deepcopy__(self, ) -> Mesh:
        """
        __deepcopy__()

        Deep copy operator. This function is triggered
        by the `copy.deepcopy()` function.

        Returns
        -------
            Mesh
                A deepcopy of the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def __init__(self, basename:str, *, format:str='carp_txt', compute_connectivity:bool=True, num_fibers:int=0) -> Mesh:
        """
        __init__(basename, *, format='carp_txt', compute_connectivity=True, num_fibers=0)

        Create a new object mesh by loading from a file.

        Parameters
        ----------
            basename: str
                Basename of the file from which the mesh should
                be loaded from.
            format: str, optional, default='carp_txt'
                Format of the mesh file.
                Choices are:
                    carp_txt .. CARP text format
                    carp_bin .. CARP binary format
                    vtk      .. vtk text format
                    vtk_bin  .. vtk binary format
                    vtu      .. vtu format
                    mmg      .. mmg format
                    neu      .. ensight format
                    obj      .. object format
                    off      .. off format
                    gmsh     .. gmsh format
                    stellar  .. stellar format
                    purk     .. purkinje format
                    vcflow   .. vcflow format
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was loaded.
            num_fibers: int, optional, default=0
                Should be a value in {0, 1, 2}. Change
                the number of fibers in the the mesh.
                If `num_fibers` =0, the fiber number
                won't be changed. If `num_fibers` =1 and
                the number of fibers in the mesh is 2,
                then the sheet fibers are removed. If
                `num_fibers` =2 and the number of fibers
                in the mesh is 1, then sheet fibers are
                added and longitudinal-orthogonal fibers
                are assigned.

        Returns
        -------
            Mesh
                The new mesh object loaded from `basename`.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the mesh format is unknown.
            ValueError
                If the number of fibers is not valid.
            RuntimeError
                If changing the fiber number fails.

        See Also
        --------
            MeshInputFormat

        """
        ...


    def apply_split(self, splitop:str, *, return_mapping:bool=False) -> None | Mesh | tuple[Mesh, Mapping]:
        """
        apply_split(splitop, *, return_mapping=False)

        Apply a split to a given mesh that is defined by the
        split operation `splitop`. The format of the split
        operations is:
            tagA1,tagA2,..:tagB1,../tagA1,..:tagB1../..
        where
            ',' separates tags,
            ':' separates tag groups to split,
            '/' separates split operations.
        The splitting is applied to the elements
        defined by the 'tagA' tags, so these must not
        repeat between several split operations!

        Parameters
        ----------
            splitop: str
                String defining the split operation.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If `splitop` generates an empty split-list.
            Mesh
                The split mesh.
            tuple[Mesh, Mapping]
                If `return_mapping` is `True`, the split mesh
                and the corresponding mapping object.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the split operation is empty or the parsing fails.
        """
        ...


    def clean_topology(self, *, threshold:float=None) -> Mesh:
        """
        clean_topology(*, threshold=-1.0)

        Clean the mesh from bad topology definitions.
        This includes removing duplicate points and
        elements, as well as removing tetrahedrons with
        zero volume and/or triangles with zero area.

        Parameters
        ----------
            threshold: float, optional, default=None
                Distance threshold when checking co-location of vertices.

        Returns
        -------
            Mesh
                The cleaned mesh or the mesh itself.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def clear_full_connectivity(self, ) -> None:
        """
        clear_full_connectivity()

        Clear the node-to-element and the
        node-to-node connectivity graphs.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def compute_full_connectivity(self, ) -> None:
        """
        compute_full_connectivity()

        Compute node-to-element and the
        node-to-node connectivity graphs of the
        mesh.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def connected_vtx_components(self, selection:ndarray[int]) -> None | tuple[ndarray[int], ...]:
        """
        connected_vtx_components(selection)

        Split a vertex selection into it's connected
        components. Two components are connected if
        they share at least one common vertex. If a
        connected component can't be converted to a
        numpy array, `None` is inserted in the tuple
        instead.

        Parameters
        ----------
            selection: ndarray[int]
                List of selected vertices.

        Returns
        -------
            None
                If no connected components were found.
            tuple[ndarray[int], ...]
                Tuple of the connected vertex selections.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the selection data can't be converted to the correct C++ container.
        """
        ...


    def correspondence(self, mesh:Mesh, *, nodal:bool=True) -> tuple[ndarray[int], ndarray[float]]:
        """
        correspondence(mesh, *, nodal=True)

        Compute nodal or element correcpondance
        between two meshes.

        Parameters
        ----------
            mesh: Mesh
                Mesh to generate the correspondence for.
            nodal: bool, optional, default=True
                It `True`, the nodal correspondence will be generated,
                otherwise the element-wise correspondence with respect
                to their center points.

        Returns
        -------
            tuple[ndarray[int], ndarray[float]]
                Index of the corresponding entity in `mesh` and the
                Euclidean distance.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the index array can't be converted to a numpy array.
            PyMeshToolError
                If the distance array can't be converted to a numpy array.
        """
        ...


    def extract_element_nodes(self, ) -> None | ndarray[int]:
        """
        extract_element_nodes()

        Get a list of all nodes to which an element is attached.

        Returns
        -------
            None
                If the list of nodes is empty.
            ndarray[int]
                List of all nodes to which an element is attached.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the node data can't converted to a numpy array.
        """
        ...


    def extract_elements(self, indices:int | ndarray[int], *, compute_connectivity:bool=True, return_mapping:bool=False) -> None | Mesh | tuple[Mesh, Mapping]:
        """
        extract_elements(indices, *, compute_connectivity=False, return_mapping=False)

        Extract a sub-mesh defined by a list of element indices.

        Parameters
        ----------
            indices: int | ndarray[int]
                List of element indices to extract from the mesh.
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was extracted.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If no element indices are in the mesh or
                the entire mesh would be extracted.
            Mesh
                If a sub-mesh was extracted and `return_mapping`
                is `False`.
            tuple[Mesh, Mapping]
                If a sub-mesh was extracted and `return_mapping`
                is `True`.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tags object can't be converted to an integer nor to the correct C++ container.
            ValueError
                If the `tags` array is empty.

        See Also
        --------
            extract_mesh, extract_myocard
        """
        ...


    def extract_gradient(self, data:ndarray[float], *, nodal_input:bool=True, return_nodal:bool=False, normalize:bool=False, norm_threshold:float=0.0) -> tuple[ndarray[float], ndarray[float]]:
        """
        extract_gradient(data, *, nodal_input=True, return_nodal=False, normalize=False, norm_threshold=0.0)

        Compute gradient and gradient magnitude of
        a scalar function given for the mesh.

        Parameters
        ----------
            data: ndarray[float]
                Scalar input data.
            nodal_input: bool, optional, default=True
                `True` if `data` is defined on the points, `False` if defined on the elements.
            return_nodal: bool, optional, default=False
                `True` if nodal data should be returned, `False` for element data.
            normalize: bool, optional, default=False
                If `True`, the gradient vectors get normalized.
            norm_threshold: float, optional, default=0.0
                Threshold value for vector normalization.

        Returns
        -------
            tuple[ndarray[float], ndarray[float]]
                Magnitude of the gradient vectors and the gradient vectors.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the input data can't be converted to the correct C++ container.
            PyMeshToolError
                If the output data can't be converted to a numpy array.
        """
        ...


    def extract_mesh(self, tags:int | ndarray[int], *, compute_connectivity:bool=True, return_mapping:bool=False) -> None | Mesh | tuple[Mesh, Mapping]:
        """
        extract_mesh(tags, *, compute_connectivity=False, return_mapping=False)

        Extract a sub-mesh defined by a list of element tags
        from a given mesh.

        Parameters
        ----------
            tags: int | ndarray[int]
                List of element tags defining the sub-mesh.
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was extracted.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If no region tag was found in the mesh or
                the entire mesh would be extracted.
            Mesh
                If a sub-mesh was extracted and `return_mapping`
                is `False`.
            tuple[Mesh, Mapping]
                If a sub-mesh was extracted and `return_mapping`
                is `True`.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tags object can't be converted to an integer nor to the correct C++ container.
            ValueError
                If the `tags` array is empty.

        See Also
        --------
            extract_elements, extract_myocard
        """
        ...


    def extract_myocard(self, *, threshold:float=0.0, compute_connectivity:bool=True, return_mapping:bool=False) -> None | Mesh | tuple[Mesh, Mapping]:
        """
        extract_myocard(*, threshold=0.0, compute_connectivity=False, return_mapping=False)

        Extract the myocardial sub-mesh. All
        elements with non-zero fibers are
        considered to by myocardial tissue.

        Parameters
        ----------
            threshold: float, optional, default=0.0
                Fibers with a length greater than the
                `threshold` value are considered as myocardium.
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was extracted.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If no fibers are defined or no myocardial
                region was found in the mesh or the entire
                mesh defines the myocardial sub-mesh.
            Mesh
                If a myocardial region was extracted and
                `return_mapping` is `False`.
            tuple[Mesh, Mapping]
                If a myocardial region was extracted and
                `return_mapping` is `True`.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the threshold value is negative.

        See Also
        --------
            extract_elements, extract_mesh
        """
        ...


    def extract_surface(self, *, setops:str='', coords:ndarray[float]=None, edge_threshold:float=0.0, angle_threshold:float=0.0, distance:float=0.0, lower_distance:float=0.0, hybrid_meshes:bool=True, reindex_nodes:bool=True, return_mapping:bool=False) -> None | tuple[Mesh, ...] | tuple[tuple[Mesh, Mapping], ...]:
        """
        extract_surface(*, setops='', coords=None, edge_threshold=0.0, angle_threshold=0.0,
                        distance=0.0, lower_distance=0.0, hybrid_meshes=True, reindex_nodes=False,
                        return_mapping=False)

        Extract a sequence of surfaces defined by set operations on element tags.
        The format of the operations is:
           `tagA1,tagA2,[surfA1,surfA2..]..[+-:]tagB1,tagB2,[surfB1,surfB2..]..`
        where tag regions separated by ',' will be unified into sub-meshes and their
        surface is computed. Alternatively, surfaces can be provided directly by
        *.surf files (only basename, no extension). If two surfaces are separated
        by '-', the rhs surface will be removed from the lhs surface (set difference).
        Similarly, using '+' will compute the surface union and if the sub-meshes are
        separated by ':', the set intersection of the two sub-mesh surfaces will be
        computed. individual operations are separated by ';'.
        An empty set operation will extract the entire surface.
        If coordinates are provided by the `coords` argument, the extracted surfaces
        will be further restricted to those elements reachable by surface edge-traversal
        starting from the surface vertices closest to the given points. Blocking edges
        can be defined by setting the `edge_threshold` value. If `angle_threshold` is
        specified, vertices are blocked where the angle between the normal vector and
        the normal vector of the start vertex is greater than the threshold value.
        To restrict the size of the surface edge-traversal, the arguments `distance` and
        `lower_distance` can be specified.

        Parameters
        ----------
            setops: str, optional, default=''
                Set operations defining the surfaces.
            coords: ndarray[float], optional, default=None
                Start points for the surface edge-traversal.
            edge_threshold: float, optional, default=0.0
                Sharp edge angle blocking surface edge-traversal.
            angle_threshold: float, optional, default=0.0
                Normal vector angle blocking surface edge-traversal.
            distance: float, optional, default=0.0
                Edge-traversal upper distance.
            lower_distance: float, optional, default=0.0
                Edge-traversal lower distance.
            hybrid_meshes: bool, optional, default=True
                If `False`, hybrid surfaces are converted to
                triangular surfaces.
            reindex_nodes: bool, optional, default=True
                If `True`, nodes in the surface meshes are
                reindexed and their point arrays are
                restricted.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If no surface was extracted.
            tuple[Mesh, ...]
                Tuple of the extracted surface meshes.
            tuple[tuple[Mesh, Mapping], ...]
                If `return_mapping` is `True`, a tuple of pairs
                with the extracted surface meshes and the
                corresponding mapping objects is returned.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the coordinates can't be converted to the correct C++ container.
        """
        ...


    def extract_unreachable(self, *, mode:int, compute_connectivity:bool=True, return_mapping:bool=False) -> None | Mesh | tuple[Mesh, Mapping] | tuple[Mesh, ...] | tuple[tuple[Mesh, Mapping], ...]:
        """
        extract_unreachable(*, mode=0, compute_connectivity=False, return_mapping=False)

        Extract unreachable sub-meshes. A sub-mesh is
        considered unreachable if it has no common nodes
        with other sub-meshes.

        Parameters
        ----------
            mode: int
                Extraction mode.
                Choices are:
                    <0 .. extract smallest unreachable sub-mesh,
                    >0 .. extract largest unreachable sub-mesh,
                    =0 .. extract all unreachable sub-meshes.
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was extracted.
            return_mapping: bool, optional, default=False
                If `True`, the mapping object is returned.

        Returns
        -------
            None
                If no unreachable sub-mesh was found.
            Mesh
                If `mode` is not equal to zero and
                `return_mapping` is `False`.
            tuple[Mesh, Mapping]
                If `mode` is not equal to zero and
                `return_mapping` is `True`.
            tuple[Mesh, ...]
                If `mode` is equal to zero and
                `return_mapping` is `False`.
            tuple[tuple[Mesh, Mapping], ...]
                If `mode` is equal to zero and
                `return_mapping` is `True`.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            RuntimeError
                If the sub-mesh extraction fails.

        See Also
        --------
            extract_myocard, extract_mesh
        """
        ...


    def extract_vtx(self, tags:int | ndarray[int]) -> None | ndarray[int]:
        """
        extract_vtx(tags)

        Extract all vertices from a region
        defined by a list of element tags and
        return a list of their indices.

        Parameters
        ----------
            tags: int | ndarray[int]
                List of element tags from which
                the vertices should be extracted
                from.

        Returns
        -------
            None
                If no vertices were extracted.
            ndarray[int]
                Array of vertex indices.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tags data can't be converted to an integer nor to the correct C++ container.
            PyMeshToolError
                If the selection data can't be converted to a numpy array.
        """
        ...


    def extract_vtxhalo(self, block:ndarray[int]) -> None | tuple[ndarray[int], ...]:
        """
        extract_vtxhalo(block)

        Extract connected components from a vertex
        selection that is given as the halo of the
        provided vertex block.

        Parameters
        ----------
            block: ndarray[int]
                Indices defining the vertex block.

        Returns
        -------
            None
                If no components were found.
            tuple[ndarray[int], ...]
                Tuple of arrays holding the node indices
                of the connected halo components.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the block object can't be converted to the correct C++ container.
        """
        ...


    def generate_distancefield(self, start_vtx:ndarray[int], *, end_vtx:ndarray[int]=None) -> ndarray[float]:
        """
        generate_distancefield(start_vtx, *, end_vtx=None)

        Generate a distance field. If only `start_vtx` is
        given, the shortest topological distance between
        each mesh point and the points defined by `start_vtx`
        is computed. If `end_vtx` is also specified, the
        relative distance to both sets is computed. Points
        in the set defined by `start_vtx` have a value of 0,
        all points in the set defined by `end_vtx` have a value
        of 1, and all remaining points have a value between
        these two.

        Parameters
        ----------
            start_vtx: ndarray[int]
                Start vertices of the distance field.
            end_vtx: ndarray[int], optional, default=None
                Rnd vertices of the distance field.

        Returns
        -------
            ndarray[float]
                The nodal values of the computed distance field.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the mesh has not only tetrahedral, triangular, or line elements.
            PyMeshToolError
                If the vertex array can't be converted to the correct C++ container.
            PyMeshToolError
                If the distance field can't be converted to a numpy array.
        """
        ...


    def generate_fibers(self, *, bath_tags:ndarray[int]=None) -> Mesh:
        """
        generate_fibers(*, bath_tags=None)

        Generate default fibers for a given mesh.
        The optional element tags identify bath regions
        to which zero fibers are assigned.

        Parameters
        ----------
            bath_tags: ndarray[int], optional, default=None
                Bath region tags.

        Returns
        -------
            Mesh
                The modified input mesh with generated fibers.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the fiber dimension in the mesh is not supported.
            PyMeshToolError
                It the bath tags can't be converted to the correct C++ container.
        """
        ...


    def generate_split(self, splitop:str) -> ndarray[int]:
        """
        generate_split(splitop)

        Generate a split-list for a given mesh
        defined by the split operation `splitop`.
        The format of the split operations is:
            tagA1,tagA2,..:tagB1,../tagA1,..:tagB1../..
        where
            ',' separates tags,
            ':' separates tag groups to split,
            '/' separates split operations.
        The splitting is applied to the elements
        defined by the 'tagA' tags, so these must not
        repeat between several split operations!

        Parameters
        ----------
            splitop: str
                String defining the split operation.

        Returns
        -------
            ndarray[int]
                The split-list defined by `splitop`.
                The dimension is (N, 3) where the first
                column holds the element index, the second
                column the old node index, and the third
                column the new node index.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the split operation is empty or the parsing fails.
            PyMeshToolError
                If the split-list can't be converted to a numpy array.
        """
        ...


    def get_element_sizes(self, ) -> ndarray[float]:
        """
        get_element_sizes()

        Get the size of all the elements, for 1D elements
        the length is returned, for 2D elements the area is
        returned, and for 3D elements the volume is returned.

        Returns
        -------
            ndarray[float]
                List of the sizes of the elements.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the size data can't converted to a numpy array.
        """
        ...


    def get_elements_in_selection(self, selection:ndarray[int]) -> None | ndarray[int]:
        """
        get_elements_in_selection(selection)

        Get a list of indices of all the elements
        for which all nodes are in the provided nodal
        selection.

        Parameters
        ----------
            selection: ndarray[int]
                The nodale selection.

        Returns
        -------
            None
                If the list of selected elements is empty.
            ndarray[int]
                List of all elements within the nodal selection.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the selection data can't converted to a numpy array.
            PyMeshToolError
                If the index data can't converted to a numpy array.
        """
        ...


    def has_full_connectivity(self, ) -> bool:
        """
        has_full_connectivity()

        Check if the node-to-element and the
        node-to-node connectivity graphs of the
        mesh are computed.

        Returns
        -------
            bool
                `True` if the graphs are computed, `False` otherwise.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def interpolate_clouddata(self, points:ndarray[float], data:ndarray[float], *, mode:int=2) -> ndarray[float]:
        """
        interpolate_clouddata(points, data, *, mode=2)

        Interpolate data from a point cloud onto the
        mesh using radial basis function interpolation.

        Parameters
        ----------
            points: ndarray[float]
                Coordinates of the point cloud.
            data: ndarray[float]
                Input data.
            mode: int, optional, default=2
                Choose between different interpolation modes.
                Choices are:
                    0 .. localized Shepard
                    1 .. global Shepard
                    2 .. RBF interpolation

        Returns
        -------
            ndarray[float]
                The interpolated data on the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the interpolation mode is not supported.
            PyMeshToolError
                If the input points can't be converted to the correct C++ container.
            PyMeshToolError
                If the input data can't be converted to the correct C++ container.
            ValueError
                If the input data has a wrong shape.
            RuntimeError
                If the interpolation failed.
            PyMeshToolError
                If the interpolated data can't be converted to a numpy array.

        See Also
        --------
            ClouddataInterpolation
        """
        ...


    def interpolate_elem2node(self, data:ndarray[float], *, normalize:bool=False) -> ndarray[float]:
        """
        interpolate_elem2node(data, *, normalize=False)

        Interpolate data from elements onto nodes.

        Parameters
        ----------
            data: ndarray[float]
                Input data array of certain shape.
                Choices are:
                    (N)   .. for scalar data.
                    (N,3) .. for vector data.
                    (N,9) .. and (N,3,3) for tensor/matrix data.
            normalize: bool, optional, default=False
                If `True`, vector data is normalized.

        Returns
        -------
            ndarray[float]
                The interpolated data on the nodes.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the input data can't be converted to the correct C++ container.
            ValueError
                If the input data has a wrong shape.
            PyMeshToolError
                If the interpolated data can't be converted to a numpy array.
        """
        ...


    def interpolate_node2elem(self, data:ndarray[float], *, normalize:bool=False) -> ndarray[float]:
        """
        interpolate_node2elem(data, *, normalize=False)

        Interpolate data from nodes onto elements.

        Parameters
        ----------
            data: ndarray[float]
                Input data array of certain shape.
                Choices are:
                    (N)   .. for scalar data.
                    (N,3) .. for vector data.
                    (N,9) .. and (N,3,3) for tensor/matrix data.
            normalize: bool, optional, default=False
                If `True`, vector data is normalized.

        Returns
        -------
            ndarray[float]
                The interpolated data on the elements.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the input data can't be converted to the correct C++ container.
            ValueError
                If the input data has a wrong shape.
            PyMeshToolError
                If the interpolated data can't be converted to a numpy array.
        """
        ...


    def interpolate_nodes(self, data:ndarray[float], omesh:Mesh, *, norm:bool=False) -> ndarray[float]:
        """
        interpolate_nodes(data, omesh, *, norm=False)

        Interpolate nodal data from one mesh onto another.

        Parameters
        ----------
            data: ndarray[float]
                Input data array of certain shape.
                Choices are:
                    (N)   .. for scalar data.
                    (N,3) .. for vector data.
                    (N,9) .. and (N,3,3) for tensor/matrix data.
            omesh: Mesh
                Mesh we interpolate to.
            norm: bool, optional, default=False
                If `True`, vector data is normalized.

        Returns
        -------
            ndarray[float]
                The interpolated data on the target mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the input data can't be converted to the correct C++ container.
            ValueError
                If the input data has a wrong shape.
            PyMeshToolError
                If the interpolated data can't be converted to a numpy array.
        """
        ...


    def is_surface_mesh(self, ) -> bool:
        """
        is_surface_mesh()

        Check if mesh is surface mesh.

        Returns
        -------
            bool
                `True` if mesh is a surface mesh, `False` otherwise.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def merge(self, mesh:Mesh, *, ignore_empty_interface:bool=True) -> None | Mesh:
        """
        merge(mesh, *, ignore_empty_interface=True)

        Merge mesh with other mesh.

        Parameters
        ----------
            mesh: Mesh
                The mesh that gets merged into.
            ignore_empty_interface: bool, optional, default=True
                It `False`, an error is raised if the interface empty.

        Returns
        -------
            None
                If the mesh to be combined does not contain any elements.
            Mesh
                The combined mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            RuntimeError
                If the interface is empty and an empty interface is not ignored.
        """
        ...


    def query_bbox(self, ) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], float]:
        """
        query_bbox()

        Get the box bounding the mesh in.
        X-, Y-, and Z-direction.

        Returns
        -------
            tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], float]
                Tuple holding the XYZ-coordinates of the point
                defining the lower-left-back corner of the box,
                the XYZ-coordinates of the point defining the
                upper-right-front corner of the box, the sizes
                of the bounding box in XYZ-direction and the length
                of the diagonal.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
        """
        ...


    def query_curvature(self, radius:float) -> ndarray[float]:
        """
        query_curvature(radius)

        Calculate the curvature of the surface mesh.

        Parameters
        ----------
            radius: float
                Radius parameter influencing the curvature calculation.

        Returns
        -------
            ndarray[float]
                The computed curvature values.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            TypeError
                If the mesh is not a surface mesh.
            PyMeshToolError
                If the output data can't be converted to a numpy array.
        """
        ...


    def query_edges(self, *, tags:int | ndarray[int]=None) -> None | tuple[float, float, float]:
        """
        query_edges(*, tags=None)

        Get statistical parameters related
        to the edges in the given mesh or in
        a sub-region only.

        Parameters
        ----------
            tags: int | ndarray[int], optional, default=None
                Restrict query to elements of
                a certain tag region.

        Returns
        -------
            None
                If no edges are in the restricted region.
            tuple[float, float, float]
                The minimal, maximal and average edge length.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the tags object can't be converted to an integer nor to the correct C++ container.
        """
        ...


    def query_idx(self, coord:ndarray[float], *, threshold:float=0.0, vertices:ndarray[int]=None) -> ndarray[int]:
        """
        query_idx(coord, *, threshold=0.0, vertices=None)

        Get indices in proximity to a given coordinate.
        If the threshold value is less than or equal to zero,
        the closest vertex is returned.

        Parameters
        ----------
            coord: ndarray[float]
                XYZ-coordinates of the point for which the nearest
                vertex is to be found.
            threshold: float, optional, default=0.0
                Sets the proximity threshold for the coordinates.
            vertices: ndarray[int], optional, default=None
                Node indices for additional filtering.

        Returns
        -------
            ndarray[int]
                List of indices in proximity to the given coordinates.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the coordinate can't be converted to the correct C++ container.
            PyMeshToolError
                If the restricting vertex data can't be converted to the correct C++ container.
            PyMeshToolError
                If the queried index list can't be converted to a numpy array.
        """
        ...


    def query_idxlist(self, coords:ndarray[float], *, threshold:ndarray[float]=0.0, vertices:ndarray[float]=None) -> None | tuple[ndarray[int], ...]:
        """
        query_idxlist(coords, *, threshold=0.0, vertices=None)

        Get indices in proximity for all provided coordinates.
        If the threshold value is less than or equal to zero,
        the closest vertex is returned. If an index list can't
        be converted to a numpy array, `None` is inserted in the
        returned tuple instead.

        Parameters
        ----------
            coords: ndarray[float]
                List of the XYZ-coordinates of the points
                for which the nearest vertex is to be found.
            threshold: ndarray[float], optional, default=0.0
                Proximity threshold for each coordinate.
            vertices: ndarray[float], optional, default=None
                Restricts query to indices of specific vertices.

        Returns
        -------
            None
                If the queried index list is empty.
            tuple[ndarray[int], ...]
                Tuple of indices in proximity to the given coordinates.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the coordinates can't be converted to the correct C++ container.
            ValueError
                If the coordinates have a wrong shape.
            PyMeshToolError
                If the threshold values can't be converted to the correct C++ container.
            PyMeshToolError
                If the restricting vertex data can't be converted to the correct C++ container.
            ValueError
                If the threshold values have a wrong size.
        """
        ...


    def query_quality(self, ) -> ndarray[float]:
        """
        query_quality()

        Get the quality of the mesh elements.
        Only the quality of the tetrahedral and
        triangular elements is calculated; all
        other elements are assigned a value of 0.

        Returns
        -------
            ndarray[float]
                Array holding the quality for each element in the mesh.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the quality data can't be converted to a numpy array.
        """
        ...


    def query_tags(self, *, vtx:None | ndarray[int]=None, tolerance:float=0.01) -> tuple[dict[int, int], dict[int, int], int]:
        """
        query_tags(*, vtx=None, tolerance=0.01)

        Get information about the tags in the myocardial
        and non-myocardial areas, as well as the corresponding
        number of elements with these tags.

        Parameters
        ----------
            vtx: None | ndarray[int], optional, default=None
                Restrict query to elements connected
                to the vertices in the list.
            tolerance: float, optional, default=0.01
                Fibers with a length greater than this
                value are considered as myocardium.

        Returns
        -------
            tuple[dict[int, int], dict[int, int], int]
                Tuple, where the first entry is a
                dictionary mapping myocardial tags to the
                corresponding number of elements, the second
                entry is a dictionary mapping bath tags to the
                corresponding number of elements, and the
                third entry is number of elements considered.

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the vtx object can't be converted to the correct C++ container.
            ValueError
                If the fiber tolerance is negative.
        """
        ...


    def refine_uniformly(self, num_it:int) -> Mesh:
        """
        refine_uniformly(num_it)

        Uniformly refine the mesh.

        Parameters
        ----------
            num_it: int
                Number of refinement iterations.

        Returns
        -------
            Mesh
                The refined mesh

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the number of oterations is less thab one.
        """
        ...


    def rotate(self, axis:ndarray[float], angle:float, *, ignore_fibers:bool=False) -> None:
        """
        rotate(axis, angle, *, ignore_fibers=False)

        Rotate the mesh around a given vector and
        with a given angle. If `ignore_fibers` is
        `False`, the fibers are not rotated.

        Parameters
        ----------
            axis: ndarray[float]
                Axis vector the mesh is rotated around.
            angle: float
                Rotation angle.
            ignore_fibers: bool, optional, default=False
                If `True`, fibers won't be rotated.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the axis vector can't be converted to the correct C++ container.
            ValueError
                If the axis vector is zero.
            RuntimeError
                If the fiber data has a wrong shape.
        """
        ...


    def save(self, basename:str, *, format:str='carp_txt') -> None:
        """
        save(basename, *, format='carp_txt')

        Write the mesh to a file.

        Parameters
        ----------
            basename: str
                Basename of the file to which the mesh should
                be written to.
            format: str, optional, default='carp_txt'
                Format of the mesh file.
                Choices are:
                    carp_txt     .. CARP text format
                    carp_bin     .. CARP binary format
                    vtk          .. vtk text format
                    vtk_bin      .. vtk binary format
                    vtu          .. vtu format
                    vtk_polydata .. vtk polydata format
                    mmg          .. mmg format
                    neu          .. ensight format
                    obj          .. object format
                    off          .. off format
                    stellar      .. stellar format
                    vcflow       .. vcflow format

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            IOError
                If the mesh format is unknown.

        See Also
        --------
            MeshOutputFormat
        """
        ...


    def scale(self, scaling_factor:float | tuple[float, float, float]) -> None:
        """
        scale(scaling_factor)

        Scale mesh by a single scaling factor
        or each axis separately by a vector valued
        scaling factor. A negative scaling factor
        correspond to a mirroring of the mesh.

        Parameters
        ----------
            scaling_factor: float | tuple[float, float, float]
                The factor by which the mesh is scaled.
                Either a single scaling factor or a list of factors
                for the X, Y, and Z coordinate.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the scaling factor can't be converted to a double nor to the correct C++ container.
            ValueError
                If a scaling factor is zero.
        """
        ...


    def smooth_mesh(self, tags:Iterable[int | Iterable[int]], *, num_iterations:int=100, smoothing_coeff:float=0.15, num_laplace_levels:int=1, edge_threshold:float=0, max_quality_threshold:float=0.95) -> None:
        """
        smooth_mesh(tags, *, num_iterations=100, smoothing_coeff=0.15, num_laplace_levels=1,
                    edge_threshold=0.0, max_quality_threshold=0.95)

        Smooth surfaces and volume of a mesh.

        Parameters
        ----------
            tags: Iterable[int | Iterable[int]]
                List of tag sets. The tags in one set have a common surface.
                Surfaces between different tag sets will be smoothed.
            num_iterations: int, optional, default=100
                Number of smoothing iter.
            smoothing_coeff: float, optional, default=0.15
                Smoothing coefficient.
            num_laplace_levels: int, optional, default=1
                Number of laplace levels used.
            edge_threshold: float, optional, default=0
                Normal vector angle difference defining a sharp edge.
                If set to 0, edge detection is turned off. Negative values
                let meshtool skip edge vertices.
            max_quality_threshold: float, optional, default=0.95
                Maximum allowed element quality metric.
                Set to 0 to disable quality checking.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            ValueError
                If the tags object could not be iterated.
            TypeError
                If the tags can't be converted to an integer value.
        """
        ...


    def translate(self, displacement:ndarray[float]) -> None:
        """
        translate(displacement)

        Translates the mesh with a given displacement vector.

        Parameters
        ----------
            displacement: ndarray[float]
                Displacement vector in X, Y, and Z directions.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mesh object has not been initialized correctly.
            PyMeshToolError
                If the displacement vector can't be converted to the correct C++ container.
        """
        ...



class Mapping:
    """
    PyMeshool Mapping object.
    Helper class to ease mapping of data between mesh and submesh.
    """

    @property
    def element_map(self) -> None | ndarray[int]:
        """
        Get the element wise submesh-to-mesh index map.

        Returns
        -------
            None
                If the element index map is empty.
            ndarray[int]
                The element wise submesh-to-mesh index map.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing mapping data of the underlying
            mapping structure without owning the data. This means
            that the mapping object is not deleted as long as there
            are numpy arrays pointing to the mapping data.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            PyMeshToolError
                If the index map can't be converted to a numpy array.
        """
        ...


    @property
    def mesh(self) -> None | Mesh:
        """
        Get the mesh object the mapping object was created with.

        Returns
        -------
            None
                If no mesh is defined.
            Mesh
                The mesh to the mapping object.
        """
        ...


    @property
    def node_map(self) -> None | ndarray[int]:
        """
        Get the nodal submesh-to-mesh index map.

        Returns
        -------
            None
                If the node index map is empty.
            ndarray[int]
                The nodal submesh-to-mesh index map.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing mapping data of the underlying
            mapping structure without owning the data. This means
            that the mapping object is not deleted as long as there
            are numpy arrays pointing to the mapping data.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            PyMeshToolError
                If the index map can't be converted to a numpy array.
        """
        ...


    @property
    def submesh(self) -> None | Mesh:
        """
        Get the submesh object the mapping object was created with.

        Returns
        -------
            None
                If no submesh is defined.
            Mesh
                The submesh to the mapping object.
        """
        ...


    def __matmul__(self, other:Mapping) -> Mapping:
        """
        __matmul__(other)

        Create a new mapping object by concatenating two consecutive
        mappings.

        Parameters
        ----------
            other: Mapping
                Subsequent mapping object.

        Returns
        -------
            Mapping
                The concatenated mapping object.

        Raises
        ------
            TypeError
                If the either of two objects is not a Mapping object.
            ValueError
                If the two mapping objects are not subsequent.

        Example
        -------
        .. code-block:: python
            # load torso model
            tor_mesh = pymeshtool.Mesh("torso_mesh.elem")

            # extract bi-ventricular mesh and mapping object
            # from torso model
            biv_tags = [1, 2]
            biv_mesh, tor_biv_map = tor_mesh.extract_mesh(biv_tags,
                                                          return_mapping=True)

            # extract left-ventricular mesh and mapping object
            # from bi-ventricular model
            lv_tag = 1
            lv_mesh, biv_lv_map = biv_mesh.extract_mesh(lv_tag,
                                                        return_mapping=True)

            # create torso <-> lv map
            tor_lv_map = tor_biv_map @ biv_lv_map

            # map data from lv to torso
            lv_data = numpy.ones(lv_mesh.num_points, dtype=numpy.float32)
            tor_data = tor_lv_map.prolongate(lv_data)

        """
        ...


    def insert_back(self, ) -> None:
        """
        insert_back()

        Insert fiber and tag data from the submesh back to the mesh.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
        """
        ...


    def insert_data(self, subdata:ndarray[number], data:ndarray[number], *, nodal_data:bool=True) -> ndarray[number]:
        """
        insert_data(subdata, data, *, nodal_data=True)

        Insert data defined on the submesh into a data array
        given on the mesh.

        Parameters
        ----------
            subdata: ndarray[number]
                The data defined on the submesh.
            data: ndarray[number]
                The data defined on the mesh.
            nodal_data: bool, optional, default=True
                Set to `True` to insert nodal data, `False` for element data.

        Returns
        -------
            ndarray[number]
                The `data` array.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            TypeError
                If `subdata` and `data` array have different underlying data types.
            ValueError
                If data has incorrect size or dimensions.
            RuntimeError
                If the mapping object is not compatible to the submesh.
            ValueError
                If dimensions of `subdata` and `data` are not compatible.

        See Also
        --------
            restrict, prolongate
        """
        ...


    def map_selection(self, idx:ndarray[int], *, nodal_selection:bool=True, map_forward:bool=True) -> None | ndarray[int]:
        """
        map_selection(idx, *, nodal_selection=True, map_forward=True)

        Map nodal or element selections between the mesh and the submesh.

        Parameters
        ----------
            idx: ndarray[int]
                Input selection array.
            nodal_selection: bool, optional, default=True
                Set `True` to map a nodal selection, `False` for an element selection.
            map_forward: bool, optional, default=True
                Set to `True` to map from mesh to submesh, `False` to map from submesh to mesh.

        Returns
        -------
            None
                If the list of the mapped selection is empty.
            ndarray[int]
                Mapped selection array.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            PyMeshToolError
                If input selection can't be converted to the correct C++ container
            PyMeshToolError
                If input selection can't be converted to a numpy array.
        """
        ...


    def prolongate(self, data:ndarray[number], *, default:number=None, nodal_data:bool=True) -> ndarray[number]:
        """
        prolongate(data, *, default=None, nodal_data=True)

        Prolongate nodal or element data from the submesh to the mesh.
        Mesh entities that are not present in the submesh are assigned
        the value given by `default` or 0 if `default` is None.

        Parameters
        ----------
            data: ndarray[number]
                Input data array.
            default: number, optional, default=None
                Default value to use where mapping is undefined.
            nodal_data: bool, optional, default=True
                Set to `True` to map nodal data, `False` for element data.

        Returns
        -------
            ndarray[number]
                Mapped output data array.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            ValueError
                If data has incorrect size or dimensions.
            RuntimeError
                If the mapping object is not compatible to the submesh.
            RuntimeError
                If the default-value object can't be generated.
            ValueError
                If the default-value object has wrong shape.
            RuntimeError
                If the output numpy array can't be generated.

        See Also
        --------
            restrict, insert_data
        """
        ...


    def restrict(self, data:ndarray[number], *, nodal_data:bool=True) -> ndarray[number]:
        """
        restrict(data, *, nodal_data=True)

        Restrict nodal or element data from the mesh to the submesh.

        Parameters
        ----------
            data: ndarray[number]
                Input data array.
            nodal_data: bool, optional, default=True
                Set to `True` to map nodal data, `False` for element data.

        Returns
        -------
            ndarray[number]
                Mapped output data array.

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
            ValueError
                If data has incorrect size or dimensions.
            RuntimeError
                If the mapping object is not compatible to the submesh.
            PyMeshToolError
                If the index map can't be converted to a numpy array.
            RuntimeError
                If the data restriction failed.

        See Also
        --------
            prolongate, insert_data
        """
        ...


    def save(self, basename:str, *, binary:bool=True) -> None:
        """
        save(basename, *, binary=True)

        Save the mapping data. For the nodal mapping a file
        named `basename.nod` is written, for the element
        mapping the file `basename.eidx` is outputted.

        Parameters
        ----------
            basename: str
                Basename to the output files.
            binary: bool, optional, default=True
                Set to `True` to write binary data, `False` for text data.

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the mapping object has not been initialized correctly.
        """
        ...



class Image:
    """
    PyMeshool Image object.
    Wrapper class for the meshtool itk_image structure.
    """

    @property
    def data_type(self) -> int:
        """
        Get the data type of the image.

        Returns
        -------
            int
                The integer value representation
                of the image data type.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.

        See Also
        --------
            ImageDType
        """
        ...


    @property
    def dtype(self) -> type:
        """
        Get the numpy data type of the image.

        Returns
        -------
            type
                The numpy type representation
                of the image data type.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            ValueError
                It the image data type unknown.
        """
        ...


    @property
    def origin(self) -> tuple[float, float, float]:
        """
        Set or get the origin of the image.

        Parameters
        ----------
            origin: tuple[float, float, float]
                The X, Y, and Z position of the new origin.

        Returns
        -------
            tuple[float, float, float]
                The X, Y, and Z position of the origin.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the new origin can't be converted to the correct C++ container.
        """
        ...


    @origin.setter
    def origin(self, origin:tuple[float, float, float]) -> None:
        """
        Set or get the origin of the image.

        Parameters
        ----------
            origin: tuple[float, float, float]
                The X, Y, and Z position of the new origin.

        Returns
        -------
            tuple[float, float, float]
                The X, Y, and Z position of the origin.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the new origin can't be converted to the correct C++ container.
        """
        ...


    @property
    def shape(self) -> tuple[int, int, int, int]:
        """
        Get the shape of the image.

        Returns
        -------
            tuple[int, int, int, int]
                The dimension in X, Y, and Z directions
                and the number of components.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
        """
        ...


    @property
    def voxel_size(self) -> tuple[float, float, float]:
        """
        Set or get the voxel-size of the image.

        Parameters
        ----------
            size: tuple[float, float, float]
                The new size in X, Y, and Z direction
                of an image voxel.

        Returns
        -------
            tuple[float, float, float]
                The X, Y, and Z size of an image voxel.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the new size can't be converted to the correct C++ container.
        """
        ...


    @voxel_size.setter
    def voxel_size(self, size:tuple[float, float, float]) -> None:
        """
        Set or get the voxel-size of the image.

        Parameters
        ----------
            size: tuple[float, float, float]
                The new size in X, Y, and Z direction
                of an image voxel.

        Returns
        -------
            tuple[float, float, float]
                The X, Y, and Z size of an image voxel.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the new size can't be converted to the correct C++ container.
        """
        ...


    @property
    def voxels(self) -> ndarray[number]:
        """
        Set or get the voxels of the image.

        Parameters
        ----------
            voxels: ndarray[number]
                The new voxel data of same shape
                and data type.

        Returns
        -------
            ndarray[number]
                The voxel data.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing voxel data of the underlying
            image structure without owning the data. This means
            that the image object is not deleted as long as there
            are numpy arrays pointing to the voxel data.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the voxel data can't be converted to a numpy array.
            BufferError
                If the voxel data buffer is empty.
            ValueError
                It the image data type unknown.
            PyMeshToolError
                If the new voxel data can't be converted to the correct C++ container.
            ValueError
                If the new voxel data has the wrong shape.
        """
        ...


    @voxels.setter
    def voxels(self, voxels:ndarray[number]) -> None:
        """
        Set or get the voxels of the image.

        Parameters
        ----------
            voxels: ndarray[number]
                The new voxel data of same shape
                and data type.

        Returns
        -------
            ndarray[number]
                The voxel data.

        Attention
        ---------
            The attribute returns a numpy array that only
            accesses the existing voxel data of the underlying
            image structure without owning the data. This means
            that the image object is not deleted as long as there
            are numpy arrays pointing to the voxel data.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the voxel data can't be converted to a numpy array.
            BufferError
                If the voxel data buffer is empty.
            ValueError
                It the image data type unknown.
            PyMeshToolError
                If the new voxel data can't be converted to the correct C++ container.
            ValueError
                If the new voxel data has the wrong shape.
        """
        ...


    def __deepcopy__(self, ) -> Image:
        """
        __deepcopy__()

        Deep copy operator. This function is triggered
        by the `copy.deepcopy()` function.

        Returns
        -------
            Image
                A deep copy of the image.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
        """
        ...


    def __init__(self, filename:str) -> Image:
        """
        __init__(filename)

        Create a new image by loading from a file.

        Parameters
        ----------
            filename: str
                Filename of the image file from which the image should
                be loaded from.

        Returns
        -------
            Image
                The new image object loaded from `filename`.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            IOError
                If the image format is unknown.

        """
        ...


    def change_type(self, new_type:int) -> Image:
        """
        change_type(new_type)

        Change image data type of the image.

        Parameters
        ----------
            new_type: int
                Index of new data type.
                Choices are:
                    1  .. unsigned_char
                    2  .. char
                    3  .. unsigned_short
                    4  .. short
                    5  .. unsigned_int
                    6  .. int
                    7  .. unsigned_long
                    8  .. long
                    9  .. float
                    10 .. double
                    11 .. color scalars

        Returns
        -------
            Image
                The image with the new data type.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            ValueError
                If the new data type is unknown.

        See Also
        --------
            ImageDType
        """
        ...


    def crop(self, ) -> Image:
        """
        crop()

        Crop the image by removing the empty space around it.

        Returns
        -------
            Image
                The cropped image.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
        """
        ...


    def extract_mesh(self, *, surface_mesh:bool=False, tetrahedralize_mesh:bool=False, scale:float=1.0, compute_connectivity:bool=True, tags:ndarray[int]=None) -> Mesh:
        """
        extract_mesh(*, surface_mesh=False, tetrahedralize_mesh=False, scale=1.0,
                     compute_connectivity=False, tags=None)

        Extract a mesh from the image by generating a hexahedral
        element from each voxel. If a list of tags is provided,
        only the defined sub-image is extracted. To get a tetrahedral
        mesh, set `tetrahedralize_mesh` to `True` to sub-divide each
        hexahedral element into six tetrahedral elements.

        Parameters
        ----------
            surface_mesh: bool, optional, default=False
                If `True`, only a surface mesh is extracted.
            tetrahedralize_mesh: bool, optional, default=False
                If `True`, the volumetric hex elements are converted to tets.
            scale: float, optional, default=1.0
                Mesh scaling factor (> 0.0).
            compute_connectivity: bool, optional, default=True
                If `True`, the full mesh connectivity is
                computed after the mesh was extracted.
            tags: ndarray[int], optional, default=None
                List of tags of the regions to mesh. If
                `None`, the entire image is extracted.

        Returns
        -------
            Mesh
                The extracted mesh.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            PyMeshToolError
                If the `tags` object can't be converted to the correct C++ container.
            RuntimeError
                If the mesh extraction failed.
        """
        ...


    def extrude(self, mode:int, radius:int, region_tag:int, *, new_tag:int=-1, tags:ndarray[int]=None) -> Image:
        """
        extrude(mode, radius, region_tag, *, new_tag=-1, tags=None)

        Extrude a certain tag region in the image. If the
        extrusion mode is 'inwards', the tag region grows into
        itself. If the mode is set to 'outwards', the region
        grows away from itself. To grow in both directions
        pick extrusion mode 'both'. The newly grown region is
        then assigned a new tag, which is given by `new_tag`
        or that of the region to be grown. Growh can be further
        restricted by providing a list of tags the reagion can
        grow into.

        Parameters
        ----------
            mode: int
                Extrusion mode.
                Choices are:
                    <0 .. extrude inwards,
                    >0 .. extrude outwards,
                    =0 .. extrude in both directions.
            radius: int
                Extrusion radius (>0).
            region_tag: int
                Tag of the region to extrude.
            new_tag: int, optional, default=-1
                Tag of the new extruded region,
                if negative, `region_tag` is taken.
            tags: ndarray[int], optional, default=None
                List of tags, the region can grow into.

        Returns
        -------
            Image
                The extruded image.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            ValueError
                If the radius is not greater than zero.
            PyMeshToolError
                If the `tags` object can't be converted to the correct C++ container.

        See Also
        --------
            ImageExtrusionMode
        """
        ...


    def resample(self, refinement_factor:float | tuple[float, float, float]) -> Image:
        """
        resample(refinement_factor)

        Resample image data by refining each pixel while
        keeping the overall image size. In case of a
        single-valued refinement factor, the pixel size
        in each direction will be scaled by the same factor.
        In case of a multi-valued refinement factor, the
        pixel size will be scaled in X, Y, and Z direction
        separately.

        Parameters
        ----------
            refinement_factor: float | tuple[float, float, float]
                Voxel refinement factor.

        Returns
        -------
            Image
                The resampled image.

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            ValueError
                If the refinement factor is not greater than zero.
            PyMeshToolError
                If the multi-valued refinement factor can't be converted to the correct C++ container.
        """
        ...


    def save(self, filename:str) -> None:
        """
        save(filename)

        Write image to file.

        Parameters
        ----------
            filename: str
                Path to the output file. the format is
                specified by the file extension.
                Choices are:
                    vtk  .. vtk structured points format
                    nrrd .. nearly raw raster data format
                    raw  .. raw binary format (voxels only)

        Returns
        -------
            None

        Raises
        ------
            RuntimeError
                If the image object has not been initialized correctly.
            IOError
                If the file extension is unknown.
        """
        ...



class PyMeshToolError(Exception):
    """
    Base class for PyMeshTool related errors.
    """
    ...


