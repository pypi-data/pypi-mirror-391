import pydantic_core
from pydantic import BaseModel
from dataclasses import asdict

from typing import Optional, Dict, Union, Any

from simba_sdk.core.requests.client.base import Client
from simba_sdk.core.requests.exception import EnsureException

from simba_sdk.core.requests.client.operator import queries as operator_queries
from simba_sdk.core.requests.client.operator import schemas as operator_schemas


class OperatorClient(Client):
    """
    This client is used as a context manager to interact with one of the SIMBAChain service APIs.
    e.g.
    ```
    my_dids: List[DidResponse] = await credential_client.dids_get_dids()
    ```
    Clients are generated with methods that have a 1:1 relationship with endpoints on the service's API. You can find the models from the api in ./schemas.py
    and query models in ./queries.py
    """
    async def _get_subscriptions(
        self,
    ) -> None:
        """
        
        """
        
        
        path_params: Dict[str, Any] = {}
        await self.get(
            "/dapr/subscribe/",
            params=path_params 
        )
        
        return
        
        

    async def health(
        self,
    ) -> object:
        """
        
        """
        
        
        path_params: Dict[str, Any] = {}
        resp = await self.get(
            "/healthz/",
            params=path_params 
        )
        
        try:
            resp_model = object.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(f"The response came back in an unexpected format: {resp.text}")
        return resp_model
        
        

    async def get_job_requests(
        self,query_arguments: operator_queries.GetJobRequestsQuery,
        
    ) -> operator_schemas.PageWorkloadRequestPublic:
        """
        List container requests

Returns a list of known container requests.
        """
        
        
        # get rid of items where None
        query_params = {k: v for k,v in asdict(query_arguments).items() if v is not None}
        
        path_params: Dict[str, Any] = {}
        resp = await self.get(
            "/v1/job-requests/",
            params=path_params  | query_params 
        )
        
        try:
            resp_model = operator_schemas.PageWorkloadRequestPublic.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(f"The response came back in an unexpected format: {resp.text}")
        return resp_model
        
        

    async def create_job_requests(
        self,
        workloadrequestcreate: operator_schemas.WorkloadRequestCreate,
    ) -> str:
        """
        Create container requests

Creates a new container request for the given input
        """
        
        
        path_params: Dict[str, Any] = {}
        resp = await self.post(
            "/v1/job-requests/",
            data=str(workloadrequestcreate) if not issubclass(type(workloadrequestcreate), BaseModel) else workloadrequestcreate.model_dump_json(),  # type: ignore
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def get_job_requests_by_id(
        self,
        job_request_id: str,
    ) -> operator_schemas.WorkloadRequestPublic:
        """
        Get container requests

Returns a container requests for the given ID.
        """
        
        
        path_params: Dict[str, Any] = {"job_request_id": job_request_id,}
        resp = await self.get(
            f"/v1/job-requests/{job_request_id}",
            params=path_params 
        )
        
        try:
            resp_model = operator_schemas.WorkloadRequestPublic.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(f"The response came back in an unexpected format: {resp.text}")
        return resp_model
        
        

    async def delete_job_requests(
        self,
        job_request_id: str,
    ) -> str:
        """
        Delete container requests

Deletes a container requests with the given ID
        """
        
        
        path_params: Dict[str, Any] = {"job_request_id": job_request_id,}
        resp = await self.delete(
            f"/v1/job-requests/{job_request_id}",
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def update_job_requests(
        self,
        job_requests_id: str,
        workloadrequestupdate: operator_schemas.WorkloadRequestUpdate,
    ) -> str:
        """
        Update container requests

Updates an existing container request with the given input
        """
        
        
        path_params: Dict[str, Any] = {"job_requests_id": job_requests_id,}
        resp = await self.put(
            f"/v1/job-requests/{job_requests_id}",
            data=str(workloadrequestupdate) if not issubclass(type(workloadrequestupdate), BaseModel) else workloadrequestupdate.model_dump_json(),  # type: ignore
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def version(
        self,
    ) -> str:
        """
        
        """
        
        
        path_params: Dict[str, Any] = {}
        resp = await self.get(
            "/v1/version/",
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def get_org_scoped_see_requests(
        self,query_arguments: operator_queries.GetOrgScopedSeeRequestsQuery,
        
        organisation_name: str,
    ) -> operator_schemas.PageWorkloadRequestPublic:
        """
        List container requests

Returns a list of known container requests; accessible only through VP login.
        """
        
        
        # get rid of items where None
        query_params = {k: v for k,v in asdict(query_arguments).items() if v is not None}
        
        path_params: Dict[str, Any] = {"organisation_name": organisation_name,}
        resp = await self.get(
            f"/v1/organisations/{organisation_name}/see/",
            params=path_params  | query_params 
        )
        
        try:
            resp_model = operator_schemas.PageWorkloadRequestPublic.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(f"The response came back in an unexpected format: {resp.text}")
        return resp_model
        
        

    async def create_org_scoped_see_requests(
        self,
        organisation_name: str,
        workloadrequestcreate: operator_schemas.WorkloadRequestCreate,
    ) -> str:
        """
        Create container requests

Provisions a new request based on the provided input; accessible only through VP login.
        """
        
        
        path_params: Dict[str, Any] = {"organisation_name": organisation_name,}
        resp = await self.post(
            f"/v1/organisations/{organisation_name}/see/",
            data=str(workloadrequestcreate) if not issubclass(type(workloadrequestcreate), BaseModel) else workloadrequestcreate.model_dump_json(),  # type: ignore
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def get_org_scoped_see_requests_by_id(
        self,
        organisation_name: str,
        see_request_id: str,
    ) -> operator_schemas.WorkloadRequestPublic:
        """
        Get container requests

Returns a container requests for the provided ID; accessible only through VP login.
        """
        
        
        path_params: Dict[str, Any] = {"organisation_name": organisation_name,"see_request_id": see_request_id,}
        resp = await self.get(
            f"/v1/organisations/{organisation_name}/see/{see_request_id}",
            params=path_params 
        )
        
        try:
            resp_model = operator_schemas.WorkloadRequestPublic.model_validate(resp.json())
        except pydantic_core.ValidationError:
            raise EnsureException(f"The response came back in an unexpected format: {resp.text}")
        return resp_model
        
        

    async def delete_org_scoped_see_requests(
        self,
        organisation_name: str,
        see_request_id: str,
    ) -> str:
        """
        Delete container requests

Deletes a container requests with the provided ID; accessible only through VP login.
        """
        
        
        path_params: Dict[str, Any] = {"organisation_name": organisation_name,"see_request_id": see_request_id,}
        resp = await self.delete(
            f"/v1/organisations/{organisation_name}/see/{see_request_id}",
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def update_org_scoped_see_requests(
        self,
        organisation_name: str,
        see_requests_id: str,
        workloadrequestupdate: operator_schemas.WorkloadRequestUpdate,
    ) -> str:
        """
        Update container requests

Updates an existing container request with the provided input; accessible only through VP login.
        """
        
        
        path_params: Dict[str, Any] = {"organisation_name": organisation_name,"see_requests_id": see_requests_id,}
        resp = await self.put(
            f"/v1/organisations/{organisation_name}/see/{see_requests_id}",
            data=str(workloadrequestupdate) if not issubclass(type(workloadrequestupdate), BaseModel) else workloadrequestupdate.model_dump_json(),  # type: ignore
            params=path_params 
        )
        
        
        resp_model = str(resp.json())  # type: ignore
        return resp_model
        
        

    async def job_request_status_event_handler(
        self,
        cloudeventmodelworkloadrequeststatusevent: operator_schemas.CloudEventModelWorkloadRequestStatusEvent,
    ) -> None:
        """
        
        """
        
        
        path_params: Dict[str, Any] = {}
        await self.post(
            "/events/simba-operator-pubsub/queuing.kube-resources.request-status/",
            data=str(cloudeventmodelworkloadrequeststatusevent) if not issubclass(type(cloudeventmodelworkloadrequeststatusevent), BaseModel) else cloudeventmodelworkloadrequeststatusevent.model_dump_json(),  # type: ignore
            params=path_params 
        )
        
        return
        
        
