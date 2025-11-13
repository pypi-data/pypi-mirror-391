
from dataclasses import dataclass
from typing import Optional, Union
from simba_sdk.core.requests.client.operator import schemas as operator_schemas


@dataclass
class GetJobRequestsQuery:
    page: int = 1
    size: int = 50
    template: Union[str, None] = None
    user: Union[str, None] = None
    status: Union[operator_schemas.WorkloadState, None] = None
    requested_state: Union[operator_schemas.WorkloadRequestedState, None] = None
    order_by: Union[str, None] = 'created_on'


@dataclass
class GetOrgScopedSeeRequestsQuery:
    page: int = 1
    size: int = 50
    template: Union[str, None] = None
    user: Union[str, None] = None
    status: Union[operator_schemas.WorkloadState, None] = None
    requested_state: Union[operator_schemas.WorkloadRequestedState, None] = None
    order_by: Union[str, None] = 'created_on'

