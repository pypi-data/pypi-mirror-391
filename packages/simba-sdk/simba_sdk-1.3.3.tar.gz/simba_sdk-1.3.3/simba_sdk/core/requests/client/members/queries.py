
from dataclasses import dataclass
from typing import Optional, Union
from simba_sdk.core.requests.client.members import schemas as members_schemas


@dataclass
class GetClientCredentialsQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    name: Union[str, None] = None
    revoked: Union[bool, None] = None
    expire_at__gte: Union[str, None] = None
    expire_at__lte: Union[str, None] = None
    user_account_id: Union[str, None] = None
    organisation_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    expired: Union[bool, None] = None


@dataclass
class GetUserClientCredentialsQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    name: Union[str, None] = None
    revoked: Union[bool, None] = None
    expire_at__gte: Union[str, None] = None
    expire_at__lte: Union[str, None] = None
    organisation_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    expired: Union[bool, None] = None


@dataclass
class GetOrganisationsQuery:
    page: int = 1
    size: int = 50
    display_name: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    organisation_name: Union[str, None] = None
    user__id: Union[str, None] = None


@dataclass
class GetDomainsQuery:
    page: int = 1
    size: int = 50
    display_name: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    domain_name: Union[str, None] = None
    user__id: Union[str, None] = None


@dataclass
class GetPermissionsQuery:
    page: int = 1
    size: int = 50
    name: Union[str, None] = None
    description: Union[str, None] = None
    effect: Union[str, None] = None
    service: Union[str, None] = None
    resource: Union[str, None] = None
    action: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'


@dataclass
class GetRolesQuery:
    page: int = 1
    size: int = 50
    name: Union[str, None] = None
    organisation_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    permission__name: Union[str, None] = None
    permission__description: Union[str, None] = None
    permission__effect: Union[str, None] = None
    permission__service: Union[str, None] = None
    permission__resource: Union[str, None] = None
    permission__action: Union[str, None] = None
    permission__order_by: Union[str, None] = 'created_at'


@dataclass
class GetTemplatesQuery:
    page: int = 1
    size: int = 50
    name: Union[str, None] = None
    parent_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'


@dataclass
class GetUserAccountsQuery:
    page: int = 1
    size: int = 50
    email: Union[str, None] = None
    last_login__gte: Union[str, None] = None
    last_login__lte: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    default_organisation_id: Union[str, None] = None
    profile__first_name: Union[str, None] = None
    profile__last_name: Union[str, None] = None
    profile__user_id: Union[str, None] = None
    profile__order_by: Union[str, None] = 'created_at'
    role__id: Union[str, None] = None
    role__name: Union[str, None] = None
    organisations__display_name: Union[str, None] = None
    organisations__order_by: Union[str, None] = 'created_at'
    organisations__organisation_name: Union[str, None] = None
    organisations__name: Union[str, None] = None
    organisations__is_domain: bool = False
    user__id: Union[str, None] = None


@dataclass
class GetBulkUsersImportRequestsQuery:
    page: int = 1
    size: int = 50
    status: Union[str, None] = None
    submitted_by_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'


@dataclass
class GetOrganisationUsersQuery:
    email: Union[str, None] = None
    last_login__gte: Union[str, None] = None
    last_login__lte: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    profile__first_name: Union[str, None] = None
    profile__last_name: Union[str, None] = None
    profile__user_id: Union[str, None] = None
    profile__order_by: Union[str, None] = 'created_at'
    role__id: Union[str, None] = None
    role__name: Union[str, None] = None
    page: int = 1
    size: int = 50


@dataclass
class GetUserInvitesQuery:
    page: int = 1
    size: int = 50
    inviter_id: Union[str, None] = None
    invitee_email: Union[str, None] = None
    status: Union[str, None] = None
    system_type: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    expired: Union[bool, None] = None


@dataclass
class GetOrganisationInvitesQuery:
    page: int = 1
    size: int = 50
    inviter_id: Union[str, None] = None
    invitee_email: Union[str, None] = None
    status: Union[str, None] = None
    system_type: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'
    expired: Union[bool, None] = None


@dataclass
class GetDeviceAppsQuery:
    page: int = 1
    size: int = 50
    name: Union[str, None] = None
    organisation_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'


@dataclass
class GetDeviceAppRegistrationsQuery:
    page: int = 1
    size: int = 50
    device_info: Union[str, None] = None
    app_info: Union[str, None] = None
    registrant_pub_key: Union[str, None] = None
    registrant_did_task_id: Union[str, None] = None
    registrant_did_id: Union[str, None] = None
    registrant_public_key_multicodec: Union[str, None] = None
    device_pub_key: Union[str, None] = None
    device_did_id: Union[str, None] = None
    device_public_key_multicodec: Union[str, None] = None
    status: Union[str, None] = None
    vc_id: Union[str, None] = None
    order_by: Union[str, None] = 'created_at'

