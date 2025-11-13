
from dataclasses import dataclass
from typing import Optional, Union
from simba_sdk.core.requests.client.credential import schemas as credential_schemas


@dataclass
class AdminListVcsQuery:
    page: int = 1
    size: int = 50
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__or__fields: Union[str, None] = None
    metadata__owner: Union[str, None] = None
    metadata__holder: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AdminListVpsQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    metadata__owner: Union[str, None] = None
    vp__type__in: Union[str, None] = None
    vp__validFrom__lte: Union[str, None] = None
    vp__validFrom__gte: Union[str, None] = None
    vp__validUntil__lte: Union[str, None] = None
    vp__validUntil__gte: Union[str, None] = None
    verifiableCredential__id: Union[str, None] = None
    verifiableCredential__issuer: Union[str, None] = None
    verifiableCredential__type__in: Union[str, None] = None
    verifiableCredential__validFrom__lte: Union[str, None] = None
    verifiableCredential__validFrom__gte: Union[str, None] = None
    verifiableCredential__validUntil__lte: Union[str, None] = None
    verifiableCredential__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AdminListTasksQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    owner: Union[str, None] = None
    order_by: Union[str, None] = None
    status__in: Union[str, None] = None
    type__in: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None


@dataclass
class AdminListCustodialAccountsQuery:
    target_owner: str
    trust_profile: Union[str, None] = None
    list_all_wallets: bool = False
    page: int = 1
    size: int = 50


@dataclass
class ListDidStringsQuery:
    page: int = 1
    size: int = 50
    order_by: Union[str, None] = None
    include_hidden: Union[bool, None] = False
    did_document__id: Union[str, None] = None
    did_document__id__like: Union[str, None] = None
    did_document__id__startswith: Union[str, None] = None
    metadata__domain: Union[str, None] = None


@dataclass
class GetDidDocumentQuery:
    force_resolve: Union[bool, None] = False


@dataclass
class ListCustodialAccountsQuery:
    domain: str
    trust_profile: Union[str, None] = None
    alias: Union[str, None] = None
    list_all_wallets: bool = False
    page: int = 1
    size: int = 50


@dataclass
class GetPublicVcQuery:
    vc_id: str


@dataclass
class ListPublicVcsQuery:
    size: int = 10
    page: int = 1
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class ListIdentityVcsQuery:
    size: int = 10
    page: int = 1
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    address__addressLocality: Union[str, None] = None
    address__addressRegion: Union[str, None] = None
    address__postalCode: Union[str, None] = None
    address__streetAddress: Union[str, None] = None
    address__streetAddress__like: Union[str, None] = None
    address__addressCountry: Union[str, None] = None
    identifier__type: Union[str, None] = None
    identifier__propertyID: Union[str, None] = None
    identifier__propertyID__in: Union[str, None] = None
    identifier__value: Union[str, int, None] = None
    identifier__value__in: Union[str, None] = None


@dataclass
class ListTrustProfilesQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    order_by: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None
    name: Union[str, None] = None
    name__ilike: Union[str, None] = None
    did_method: Union[str, None] = None
    cryptosuite: Union[str, None] = None
    blockchain: Union[str, None] = None
    registry_type: Union[str, None] = None
    contract_api: Union[str, None] = None


@dataclass
class ListDidsQuery:
    include_stats: Union[bool, None] = False
    output_format: Union[credential_schemas.DIDResponseType, None] = 'DETAILED'
    page: int = 1
    size: int = 50
    simba_id: Union[str, None] = None
    order_by: Union[str, None] = None
    include_hidden: Union[bool, None] = False
    metadata__search: Union[str, None] = None
    metadata__name__ilike: Union[str, None] = None
    metadata__permission: Union[credential_schemas.DidPermission, None] = None
    metadata__alias__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    did_document__id: Union[str, None] = None
    did_document__id__like: Union[str, None] = None
    did_document__id__startswith: Union[str, None] = None
    did_document__controller: Union[str, None] = None


@dataclass
class ListVcsQuery:
    my_vcs: Union[bool, None] = None
    issued_vcs: Union[bool, None] = None
    page: int = 1
    size: int = 50
    id__in: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__owner_alias: Union[str, None] = None
    metadata__issuer_name__ilike: Union[str, None] = None
    metadata__holder_alias: Union[str, None] = None
    metadata__subject_name__ilike: Union[str, None] = None
    metadata__tags__in: Union[str, None] = None
    metadata__status__in: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vc__id: Union[str, None] = None
    vc__issuer: Union[str, None] = None
    vc__type__in: Union[str, None] = None
    vc__validFrom__lte: Union[str, None] = None
    vc__validFrom__gte: Union[str, None] = None
    vc__validUntil__lte: Union[str, None] = None
    vc__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class AcceptVcQuery:
    accept: bool


@dataclass
class GetVpsQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    order_by: Union[str, None] = None
    metadata__created_at__lte: Union[str, None] = None
    metadata__created_at__gte: Union[str, None] = None
    metadata__updated_at__lte: Union[str, None] = None
    metadata__updated_at__gte: Union[str, None] = None
    vp__type__in: Union[str, None] = None
    vp__validFrom__lte: Union[str, None] = None
    vp__validFrom__gte: Union[str, None] = None
    vp__validUntil__lte: Union[str, None] = None
    vp__validUntil__gte: Union[str, None] = None
    verifiableCredential__id: Union[str, None] = None
    verifiableCredential__issuer: Union[str, None] = None
    verifiableCredential__type__in: Union[str, None] = None
    verifiableCredential__validFrom__lte: Union[str, None] = None
    verifiableCredential__validFrom__gte: Union[str, None] = None
    verifiableCredential__validUntil__lte: Union[str, None] = None
    verifiableCredential__validUntil__gte: Union[str, None] = None
    credentialSubject__id: Union[str, None] = None
    credentialSubject__claim__fields: Union[str, None] = None


@dataclass
class ListTasksQuery:
    page: int = 1
    size: int = 50
    id: Union[str, None] = None
    order_by: Union[str, None] = None
    status__in: Union[str, None] = None
    type__in: Union[str, None] = None
    created_at__lte: Union[str, None] = None
    created_at__gte: Union[str, None] = None
    updated_at__lte: Union[str, None] = None
    updated_at__gte: Union[str, None] = None

