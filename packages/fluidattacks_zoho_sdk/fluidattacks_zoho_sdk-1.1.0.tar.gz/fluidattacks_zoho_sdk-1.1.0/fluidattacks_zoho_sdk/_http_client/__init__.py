from dataclasses import dataclass

from fluidattacks_zoho_sdk.auth import Credentials
from fluidattacks_zoho_sdk.ids import OrgId

from ._client import Client
from ._core import HttpJsonClient, RelativeEndpoint


@dataclass(frozen=True)
class ClientFactory:
    @staticmethod
    def new(creds: Credentials, org_id: OrgId) -> HttpJsonClient:
        return Client.new(creds, org_id).client


__all__ = ["Client", "HttpJsonClient", "RelativeEndpoint"]
