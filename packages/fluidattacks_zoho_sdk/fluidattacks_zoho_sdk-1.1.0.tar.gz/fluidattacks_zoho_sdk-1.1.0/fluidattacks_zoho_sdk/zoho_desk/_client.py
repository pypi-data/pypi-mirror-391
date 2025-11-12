import inspect
import logging

from fa_purity import Cmd, FrozenList, Maybe, ResultE, Stream, cast_exception
from fa_purity.json import Primitive, UnfoldedFactory
from fluidattacks_etl_utils.bug import Bug
from fluidattacks_etl_utils.decode import int_to_str
from fluidattacks_etl_utils.paginate import cursor_pagination

from fluidattacks_zoho_sdk._decoders import assert_single
from fluidattacks_zoho_sdk._http_client import HttpJsonClient, RelativeEndpoint
from fluidattacks_zoho_sdk._http_client.paginate import (
    FromIndex,
    Limit,
    get_page,
    validate_next_page,
)
from fluidattacks_zoho_sdk.auth import Token

from ._decode import decode_agents, decode_contacts, decode_teams, decode_tickets
from .core import AgentObj, ContactObj, TeamObj, TicketObj

LOG = logging.getLogger(__name__)

"""
    The Zoho Desk endpoint uses pagination based on `from` and `limit` parameters

    Docs:
        https://desk.zoho.com/DeskAPIDocument#Pagination
"""


def get_agents_endpoint(
    client: HttpJsonClient,
    acess_token: Token,
    start_from: Maybe[FromIndex],
    limit: Limit,
) -> Cmd[ResultE[tuple[FrozenList[AgentObj], Maybe[FromIndex]]]]:
    endpoint = RelativeEndpoint.new(
        "agents",
    )
    start_from_or_default = start_from.value_or(FromIndex(1))
    params: dict[str, Primitive] = {
        "from": int_to_str(start_from_or_default),
        "limit": int_to_str(limit),
    }
    return client.get(
        endpoint,
        acess_token,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda result: (
            result.alt(
                lambda e: cast_exception(Bug.new("_get_contact", inspect.currentframe(), e, ())),
            )
            .bind(assert_single)
            .bind(lambda agents: decode_agents(agents))
            .bind(lambda items: validate_next_page(start_from_or_default, items, limit))
        ),
    )


def get_agents(
    client: HttpJsonClient,
    token: Token,
    limit: Limit,
) -> Cmd[Stream[FrozenList[AgentObj]]]:
    stream = cursor_pagination(
        lambda next_batch: get_page(client, token, next_batch, limit, get_agents_endpoint),
    )
    return Cmd.wrap_value(stream)


def get_contacts_endpoint(
    client: HttpJsonClient,
    access_token: Token,
    start_from: Maybe[FromIndex],
    limit: Limit,
) -> Cmd[ResultE[tuple[FrozenList[ContactObj], Maybe[FromIndex]]]]:
    endpoint = RelativeEndpoint.new("contats")
    start_from_or_default = start_from.value_or(FromIndex(1))
    params: dict[str, Primitive] = {
        "from": int_to_str(start_from_or_default),
        "limit": int_to_str(limit),
    }
    return client.get(
        endpoint,
        access_token,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda result: (
            result.alt(
                lambda e: cast_exception(Bug.new("_get_contact", inspect.currentframe(), e, ())),
            )
            .bind(assert_single)
            .bind(lambda contacts: decode_contacts(contacts))
            .bind(lambda items: validate_next_page(start_from_or_default, items, limit))
        ),
    )


def get_contacts(
    client: HttpJsonClient,
    access_token: Token,
    limit: Limit,
) -> Cmd[Stream[FrozenList[ContactObj]]]:
    stream = cursor_pagination(
        lambda next_batch: get_page(client, access_token, next_batch, limit, get_contacts_endpoint),
    )
    return Cmd.wrap_value(stream)


def get_tickets_endpoint(
    client: HttpJsonClient,
    access_token: Token,
    start_from: Maybe[FromIndex],
    limit: Limit,
) -> Cmd[ResultE[tuple[FrozenList[TicketObj], Maybe[FromIndex]]]]:
    start_from_or_default = start_from.value_or(FromIndex(1))
    endpoint = RelativeEndpoint.new("tickets")
    params: dict[str, Primitive] = {
        "from": int_to_str(start_from_or_default),
        "limit": int_to_str(limit),
    }
    return client.get(
        endpoint,
        access_token,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda result: (
            result.alt(
                lambda e: cast_exception(Bug.new("_get_contact", inspect.currentframe(), e, ())),
            )
            .bind(assert_single)
            .bind(lambda tickets: decode_tickets(tickets))
            .bind(lambda items: validate_next_page(start_from_or_default, items, limit))
        ),
    )


def get_tickets(
    client: HttpJsonClient,
    token: Token,
    limit: Limit,
) -> Cmd[Stream[FrozenList[TicketObj]]]:
    stream = cursor_pagination(
        lambda next_batch: get_page(client, token, next_batch, limit, get_tickets_endpoint),
    )
    return Cmd.wrap_value(stream)


def get_teams(
    client: HttpJsonClient,
    access_token: Token,
) -> Cmd[ResultE[FrozenList[TeamObj]]]:
    endpoint = RelativeEndpoint.new("teams")
    params: dict[str, Primitive] = {}
    return client.get(
        endpoint,
        access_token,
        UnfoldedFactory.from_dict(params),
    ).map(
        lambda result: (
            result.alt(
                lambda e: cast_exception(Bug.new("_get_teams", inspect.currentframe(), e, ())),
            )
            .bind(assert_single)
            .bind(lambda teams: decode_teams(teams))
        ),
    )
