"""
Scoping
=======
"""

from ansys.grpc.dpf import scoping_pb2, scoping_pb2_grpc, base_pb2
from ansys.dpf.core.common import locations,_common_progress_bar
from ansys.dpf.core.misc import DEFAULT_FILE_CHUNK_SIZE
from ansys.dpf.core import errors as dpf_errors
from ansys.dpf.core.check_version import version_requires, server_meet_version
import numpy as np
import array


import sys

class Scoping:
    """A class used to represent a Scoping which is a subset of a
    model support.

    Parameters
    ----------
    scoping : ansys.grpc.dpf.scoping_pb2.Scoping message, optional

    server : DPFServer, optional
        Server with channel connected to the remote or local instance. When
        ``None``, attempts to use the the global server.

    Attributes
    ----------
    ids : list of int

    location : str
        Location of the ids.  For example ``"Nodal"`` or ``"Elemental"``.
        
    Examples
    --------    
    Create a mesh scoping

    >>> from ansys.dpf import core as dpf
    >>> # 1. using the mesh_scoping_factory
    >>> from ansys.dpf.core import mesh_scoping_factory
    >>> # a. scoping with elemental location that targets the elements with id 2, 7 and 11
    >>> my_elemental_scoping = mesh_scoping_factory.elemental_scoping([2, 7, 11])
    >>> # b. scoping with nodal location that targets the elements with id 4 and 6
    >>> my_nodal_scoping = mesh_scoping_factory.nodal_scoping([4, 6])
    >>> #2. using the classic API
    >>> my_scoping = dpf.Scoping()
    >>> my_scoping.location = "Nodal" #optional
    >>> my_scoping.ids = list(range(1,11))
    
    """

    def __init__(self, scoping=None, server=None, ids = None, location= None):
        """Initialize the scoping with either optional scoping message, or
        by connecting to a stub.
        """
        if server is None:
            import ansys.dpf.core.server as serverlib
            server = serverlib._global_server()

        self._server = server
        self._stub = self._connect()

        if scoping is None:
            request = base_pb2.Empty()
            self._message = self._stub.Create(request)
        else:
            self._message = scoping
        
        if ids:
            self.ids=ids
        if location:
            self.location=location

    def _count(self):
        """
        Returns
        -------
        count : int
            The number of scoping ids
        """
        request = scoping_pb2.CountRequest()
        request.entity = base_pb2.NUM_ELEMENTARY_DATA
        request.scoping.CopyFrom(self._message)
        return self._stub.Count(request).count

    def _get_location(self):
        """
        Returns
        -------
        location : str
            location of the ids
        """
        sloc = self._stub.GetLocation(self._message).loc.location
        return sloc

    def _set_location(self, loc=locations.nodal):
        """
        Parameters
        ----------
        loc : str or core.locations enum
            The location needed

        """
        request = scoping_pb2.UpdateRequest()
        request.location.location = loc
        request.scoping.CopyFrom(self._message)
        self._stub.Update(request)
        
    @version_requires("2.1")
    def _set_ids(self, ids):
        """
        Parameters
        ----------
        ids : list of int
            The ids to set
        
        Notes
        -----
        Print a progress bar
        """
        # must convert to a list for gRPC
        if isinstance(ids, range):
            ids = np.array(list(ids), dtype=np.int32)
        elif not isinstance(ids,(np.ndarray, np.generic)):            
            ids= np.array(ids, dtype=np.int32)
        else:
            ids = np.array(list(ids), dtype=np.int32)
        
        metadata=[(u"size_int", f"{len(ids)}")]
        request = scoping_pb2.UpdateIdsRequest()
        request.scoping.CopyFrom(self._message)
        if server_meet_version("2.1", self._server):
            self._stub.UpdateIds(_data_chunk_yielder(request, ids), metadata=metadata)
        else:
            self._stub.UpdateIds(_data_chunk_yielder(request, ids, 8.0e6), metadata=metadata)
        

    def _get_ids(self, np_array=False):
        """
        Returns
        -------
        ids : list[int], numpy.array (if np_array==True)
            List of ids.    
        
        Notes
        -----
        Print a progress bar
        """
        if server_meet_version("2.1", self._server):  
            service = self._stub.List(self._message)
            dtype = np.int32
            return _data_get_chunk_(dtype, service,np_array)
        else:
            out = []
                    
            service = self._stub.List(self._message)
            for chunk in service:
                out.extend(chunk.ids.rep_int)
            if np_array:
                return np.array(out, dtype = np.int32)
            else:
                return out

    def set_id(self, index, scopingid):
        """Set the id of an index of the scoping

        Parameters
        ----------
        index : int
        
        scopingid : int
        """
        request = scoping_pb2.UpdateRequest()
        request.index_id.id = scopingid
        request.index_id.index = index
        request.scoping.CopyFrom(self._message)
        self._stub.Update(request)

    def _get_id(self, index):
        """Returns on which index is located an id in the scoping

        Parameters
        ----------
        index : int

        Returns
        -------
        id : int
        """
        request = scoping_pb2.GetRequest()
        request.index = index
        request.scoping.CopyFrom(self._message)
        return self._stub.Get(request).id

    def _get_index(self, scopingid):
        """Returns on which id is corresponding to an id in the
        scoping.

        Parameters
        ----------
        id : int

        Returns
        -------
        index : int
        """
        request = scoping_pb2.GetRequest()
        request.id = scopingid
        request.scoping.CopyFrom(self._message)
        return self._stub.Get(request).index

    def id(self, index:int):
        """Get the id at a given index
        
        Returns
        -------
        size : int
    
        """
        return self._get_id(index)

    def index(self, id:int):
        """Get the index of a given id
        
        Returns
        -------
        size : int
    
        """
        return self._get_index(id)

    @property
    def ids(self):
        """Get the list of ids in the scoping
 
        Returns
        -------
        ids : list of int    
        
        Notes
        -----
        Print a progress bar
        """
        return self._get_ids()

    @ids.setter
    def ids(self, value):
        self._set_ids(value)

    @property
    def location(self):
        """The location of the ids as a string (e.g. nodal, elemental,
        time_freq, etc...)

        Returns
        -------
        location : str
    
        """
        return self._get_location()

    @location.setter
    def location(self, value):
        self._set_location(value)

    def _connect(self):
        """Connect to the grpc service containing the reader"""
        return scoping_pb2_grpc.ScopingServiceStub(self._server.channel)

    def __len__(self):
        return self._count()

    def __del__(self):
        try:
            self._stub.Delete(self._message)
        except:
            pass
        
    def __iter__(self):
        return self.ids.__iter__()
    
    def __getitem__(self, key):
        """Returns the id at a requested index"""
        return self.id(key)

    @property
    def size(self):
        """lenght of the ids list

        Returns
        -------
        size : int
    
        """
        return self._count()

    def __str__(self):
        """describe the entity
        
        Returns
        -------
        description : str
        """
        from ansys.dpf.core.core import _description
        return _description(self._message, self._server)
    
    def deep_copy(self,server=None):
        """Creates a deep copy of the scoping's data on a given server.
        This can be usefull to pass data from one server instance to another.
        
        Parameters
        ----------
        server : DPFServer, optional
            Server with channel connected to the remote or local instance. When
            ``None``, attempts to use the the global server.
        
        Returns
        -------
        scoping_copy : Scoping
        """
        scop = Scoping(server=server)
        scop.ids = self.ids
        scop.location =self.location
        return scop


def _data_chunk_yielder(request, data, chunk_size=DEFAULT_FILE_CHUNK_SIZE): 
    length = data.size
    need_progress_bar = length>1e6
    if need_progress_bar:
        bar =_common_progress_bar("Sending data...", unit=data.dtype.name, tot_size =length)
        bar.start()
    sent_length =0
    if length == 0:
        yield request
        return
    unitary_size =int(chunk_size//sys.getsizeof(data[0]))
    if length-sent_length<unitary_size:
        unitary_size= length-sent_length
    while sent_length<length:
        currentcopy = data.take(range(sent_length,sent_length+unitary_size))
        request.array= currentcopy.tobytes()
        sent_length=sent_length+unitary_size
        if length-sent_length<unitary_size:
            unitary_size= length-sent_length
        yield request
        try:
            if need_progress_bar:
                bar.update(sent_length)
        except:
            pass
    try:
        if need_progress_bar:
            bar.finish()
    except:
        pass
    
    


def _data_get_chunk_(dtype, service, np_array=True):
    tupleMetaData = service.initial_metadata()
    
    need_progress_bar = False
    for iMeta in range(len(tupleMetaData)):
        if tupleMetaData[iMeta].key == u"size_tot":
            size = int(tupleMetaData[iMeta].value)
    need_progress_bar = size>1e6
    itemsize = np.dtype(dtype).itemsize
    if need_progress_bar:
        bar =_common_progress_bar("Receiving data...", unit=dtype.__name__+"s", tot_size = size//itemsize)
        bar.start()
        
        
    if np_array:
        arr = np.empty(size//itemsize, dtype)
        i = 0
        for chunk in service:
            curr_size = len(chunk.array)//itemsize
            arr[i:i + curr_size] = np.frombuffer(chunk.array, dtype)
            i += curr_size
            try:
                if need_progress_bar:
                    bar.update(i)
            except:
                pass

    else:
        arr=[]
        if dtype==np.float:
            dtype = 'd'
        else:
            dtype='i'
        for chunk in service:
            arr.extend(array.array(dtype,chunk.array))
            try:
                if need_progress_bar:
                    bar.update(len(arr))
            except:
                pass
    try:
        if need_progress_bar:
            bar.finish()
    except:
        pass
    return arr