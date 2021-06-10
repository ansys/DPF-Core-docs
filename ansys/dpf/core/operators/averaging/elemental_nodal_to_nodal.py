"""
elemental_nodal_to_nodal
========================
"""
from ansys.dpf.core.dpf_operator import Operator
from ansys.dpf.core.inputs import Input, _Inputs
from ansys.dpf.core.outputs import Output, _Outputs, _modify_output_spec_with_one_type
from ansys.dpf.core.operators.specification import PinSpecification, Specification

"""Operators from Ans.Dpf.FEMutils plugin, from "averaging" category
"""

class elemental_nodal_to_nodal(Operator):
    """Transform ElementalNodal field into Nodal field using an averaging process, result is computed on a given node scoping.

      available inputs:
        - field (Field, FieldsContainer)
        - mesh_scoping (Scoping) (optional)
        - should_average (bool) (optional)
        - mesh (MeshedRegion) (optional)

      available outputs:
        - fields_container (FieldsContainer)

      Examples
      --------
      >>> from ansys.dpf import core as dpf

      >>> # Instantiate operator
      >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()

      >>> # Make input connections
      >>> my_field = dpf.Field()
      >>> op.inputs.field.connect(my_field)
      >>> my_mesh_scoping = dpf.Scoping()
      >>> op.inputs.mesh_scoping.connect(my_mesh_scoping)
      >>> my_should_average = bool()
      >>> op.inputs.should_average.connect(my_should_average)
      >>> my_mesh = dpf.MeshedRegion()
      >>> op.inputs.mesh.connect(my_mesh)

      >>> # Instantiate operator and connect inputs in one line
      >>> op = dpf.operators.averaging.elemental_nodal_to_nodal(field=my_field,mesh_scoping=my_mesh_scoping,should_average=my_should_average,mesh=my_mesh)

      >>> # Get output data
      >>> result_fields_container = op.outputs.fields_container()"""
    def __init__(self, field=None, mesh_scoping=None, should_average=None, mesh=None, config=None, server=None):
        super().__init__(name="elemental_nodal_To_nodal", config = config, server = server)
        self._inputs = InputsElementalNodalToNodal(self)
        self._outputs = OutputsElementalNodalToNodal(self)
        if field !=None:
            self.inputs.field.connect(field)
        if mesh_scoping !=None:
            self.inputs.mesh_scoping.connect(mesh_scoping)
        if should_average !=None:
            self.inputs.should_average.connect(should_average)
        if mesh !=None:
            self.inputs.mesh.connect(mesh)

    @staticmethod
    def _spec():
        spec = Specification(description="""Transform ElementalNodal field into Nodal field using an averaging process, result is computed on a given node scoping.""",
                             map_input_pin_spec={
                                 0 : PinSpecification(name = "field", type_names=["field","fields_container"], optional=False, document="""field or fields container with only one field is expected"""), 
                                 1 : PinSpecification(name = "mesh_scoping", type_names=["scoping"], optional=True, document="""average only on these entities"""), 
                                 2 : PinSpecification(name = "should_average", type_names=["bool"], optional=True, document="""each nodal value is divided by the number of elements linked to this node (default is true for discrete quantities)"""), 
                                 7 : PinSpecification(name = "mesh", type_names=["abstract_meshed_region"], optional=True, document="""""")},
                             map_output_pin_spec={
                                 0 : PinSpecification(name = "fields_container", type_names=["fields_container"], optional=False, document="""""")})
        return spec


    @staticmethod
    def default_config():
        return Operator.default_config(name = "elemental_nodal_To_nodal")

    @property
    def inputs(self):
        """Enables to connect inputs to the operator

        Returns
        --------
        inputs : InputsElementalNodalToNodal 
        """
        return super().inputs


    @property
    def outputs(self):
        """Enables to get outputs of the operator by evaluationg it

        Returns
        --------
        outputs : OutputsElementalNodalToNodal 
        """
        return super().outputs


#internal name: elemental_nodal_To_nodal
#scripting name: elemental_nodal_to_nodal
class InputsElementalNodalToNodal(_Inputs):
    """Intermediate class used to connect user inputs to elemental_nodal_to_nodal operator

      Examples
      --------
      >>> from ansys.dpf import core as dpf

      >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
      >>> my_field = dpf.Field()
      >>> op.inputs.field.connect(my_field)
      >>> my_mesh_scoping = dpf.Scoping()
      >>> op.inputs.mesh_scoping.connect(my_mesh_scoping)
      >>> my_should_average = bool()
      >>> op.inputs.should_average.connect(my_should_average)
      >>> my_mesh = dpf.MeshedRegion()
      >>> op.inputs.mesh.connect(my_mesh)
    """
    def __init__(self, op: Operator):
        super().__init__(elemental_nodal_to_nodal._spec().inputs, op)
        self._field = Input(elemental_nodal_to_nodal._spec().input_pin(0), 0, op, -1) 
        self._inputs.append(self._field)
        self._mesh_scoping = Input(elemental_nodal_to_nodal._spec().input_pin(1), 1, op, -1) 
        self._inputs.append(self._mesh_scoping)
        self._should_average = Input(elemental_nodal_to_nodal._spec().input_pin(2), 2, op, -1) 
        self._inputs.append(self._should_average)
        self._mesh = Input(elemental_nodal_to_nodal._spec().input_pin(7), 7, op, -1) 
        self._inputs.append(self._mesh)

    @property
    def field(self):
        """Allows to connect field input to the operator

        - pindoc: field or fields container with only one field is expected

        Parameters
        ----------
        my_field : Field, FieldsContainer, 

        Examples
        --------
        >>> from ansys.dpf import core as dpf

        >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
        >>> op.inputs.field.connect(my_field)
        >>> #or
        >>> op.inputs.field(my_field)

        """
        return self._field

    @property
    def mesh_scoping(self):
        """Allows to connect mesh_scoping input to the operator

        - pindoc: average only on these entities

        Parameters
        ----------
        my_mesh_scoping : Scoping, 

        Examples
        --------
        >>> from ansys.dpf import core as dpf

        >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
        >>> op.inputs.mesh_scoping.connect(my_mesh_scoping)
        >>> #or
        >>> op.inputs.mesh_scoping(my_mesh_scoping)

        """
        return self._mesh_scoping

    @property
    def should_average(self):
        """Allows to connect should_average input to the operator

        - pindoc: each nodal value is divided by the number of elements linked to this node (default is true for discrete quantities)

        Parameters
        ----------
        my_should_average : bool, 

        Examples
        --------
        >>> from ansys.dpf import core as dpf

        >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
        >>> op.inputs.should_average.connect(my_should_average)
        >>> #or
        >>> op.inputs.should_average(my_should_average)

        """
        return self._should_average

    @property
    def mesh(self):
        """Allows to connect mesh input to the operator

        Parameters
        ----------
        my_mesh : MeshedRegion, 

        Examples
        --------
        >>> from ansys.dpf import core as dpf

        >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
        >>> op.inputs.mesh.connect(my_mesh)
        >>> #or
        >>> op.inputs.mesh(my_mesh)

        """
        return self._mesh

class OutputsElementalNodalToNodal(_Outputs):
    """Intermediate class used to get outputs from elemental_nodal_to_nodal operator
      Examples
      --------
      >>> from ansys.dpf import core as dpf

      >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
      >>> # Connect inputs : op.inputs. ...
      >>> result_fields_container = op.outputs.fields_container()
    """
    def __init__(self, op: Operator):
        super().__init__(elemental_nodal_to_nodal._spec().outputs, op)
        self._fields_container = Output(elemental_nodal_to_nodal._spec().output_pin(0), 0, op) 
        self._outputs.append(self._fields_container)

    @property
    def fields_container(self):
        """Allows to get fields_container output of the operator


        Returns
        ----------
        my_fields_container : FieldsContainer, 

        Examples
        --------
        >>> from ansys.dpf import core as dpf

        >>> op = dpf.operators.averaging.elemental_nodal_to_nodal()
        >>> # Connect inputs : op.inputs. ...
        >>> result_fields_container = op.outputs.fields_container() 
        """
        return self._fields_container
