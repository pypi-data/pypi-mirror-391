from dataclasses import dataclass

from fluidattacks_zoho_sdk._http_client import ClientFactory, HttpJsonClient
from fluidattacks_zoho_sdk.auth import Credentials
from fluidattacks_zoho_sdk.ids import OrgId

from . import _client
from .core import AgentObj, ContactObj, DeskClient, UserObj


def _from_client(client: HttpJsonClient) -> DeskClient:
    return DeskClient(
        lambda t, li: _client.get_agents(client, t, li),
        lambda t, li: _client.get_contacts(client, t, li),
        lambda t, li: _client.get_tickets(client, t, li),
        lambda t: _client.get_teams(client, t),
    )


@dataclass(frozen=True)
class DeskAgentClientFactory:
    @staticmethod
    def new(creds: Credentials, org_id: OrgId) -> DeskClient:
        return _from_client(ClientFactory.new(creds, org_id))


__all__ = [
    "AgentObj",
    "ContactObj",
    "DeskAgentClient",
    "DeskAgentClientFactory",
    "UserObj",
]
