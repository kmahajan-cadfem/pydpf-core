"""
RemoteWorkflow
==============
Interface to underlying gRPC Remote Workflow
"""
import logging

from ansys import dpf
from ansys.grpc.dpf import remote_workflow_pb2, remote_workflow_pb2_grpc, base_pb2
from ansys.dpf.core.errors import protect_grpc

LOG = logging.getLogger(__name__)
LOG.setLevel('DEBUG')


class RemoteWorkflow:
    """A class used to represent a RemoteWorkflow:
        a local instance representing a workflow on a different process. 
        The local process being connected through gprc to the remote process.

    Parameters
    ----------
    server : server.DPFServer, optional
        Server with channel connected to the remote or local instance. When
        ``None``, attempts to use the global server.
        
    remote_workflow :  workflow_message_pb2.RemoteWorkflow

    """

    def __init__(self, remote_workflow, server=None):
        """Initialize the workflow by connecting to a stub.
        """
        if server is None:
            server = dpf.core._global_server()

        self._server = server
        self._stub = self._connect()

        self._message = remote_workflow
        
    def chain_with(self, workflow, input_output_names=None):
        """Chain 2 workflows together so that they become one workflow
        with all the operators, inputs and outputs exposed in both workflows
        
        Parameters
        ----------
        workflow : core.Workflow
            This second workflow's inputs will be chained with this workflow's outputs
            
        input_output_names : str tuple, optional
            the input name of this workflow will be chained with the output name of the second workflow
            If nothing is specified, this workflow's outputs with the same names as the second workflow's inputs will be chained
        
        Examples
        --------
        ::
            
            +-------------------------------------------------------------------------------------------------+
            |  INPUT:                                                                                         |
            |                                                                                                 |
            |input_output_names = ("output","field" )                                                          |
            |                      ____                                  ______________________                |
    	    |  "data_sources"  -> |this| ->  "stuff"        "field" -> |workflow_to_chain_with| -> "contour"  |
    	    |"time_scoping"    -> |    |             "mesh_scoping" -> |                      |               |
    	    |                     |____| ->  "output"                  |______________________|               |
            |  OUTPUT                                                                                         |
    	    |                    ____                                                                         |
    	    |"data_sources"  -> |this| ->  "stuff"                                                            |
    	    |"time_scoping" ->  |    | ->  "contour"                                                           |
    	    |"mesh_scoping" ->  |____| -> "output"                                                             |
            +-------------------------------------------------------------------------------------------------+
           
        
        """
        request = remote_workflow_pb2.ChainRequest()
        request.wf.CopyFrom(self._message)
        request.wf_to_chain_with.CopyFrom(workflow._message)
        if input_output_names:
            request.input_to_output.output_name = input_output_names[0]
            request.input_to_output.input_name = input_output_names[1]
        self._stub.Chain(request)            
    
        
    def _connect(self):
        """Connect to the grpc service"""
        return remote_workflow_pb2_grpc.RemoteWorkflowServiceStub(self._server.channel)

    def __del__(self):
        try:
            self._stub.Delete(self._message)
        except:
            pass

