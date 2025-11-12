from collections.abc import Callable
from dataclasses import dataclass

from fa_purity import Cmd, FrozenList, Maybe, ResultE, Stream
from fa_purity.date_time import DatetimeUTC

from fluidattacks_zoho_sdk._http_client.paginate import Limit
from fluidattacks_zoho_sdk.auth import Token
from fluidattacks_zoho_sdk.ids import (
    AccountId,
    ContactId,
    CrmId,
    DeparmentId,
    ProductId,
    ProfileId,
    RoleId,
    TeamId,
    TicketId,
    UserId,
)


@dataclass(frozen=True)
class UserObj:
    id_user: UserId
    first_name: Maybe[str]
    last_name: str


@dataclass(frozen=True)
class AgentObj:
    user: UserObj
    is_confirmed: bool
    email: str
    profile: ProfileId
    role: RoleId
    status: str


@dataclass(frozen=True)
class ContactDates:
    created_time: DatetimeUTC
    modified_time: DatetimeUTC


@dataclass(frozen=True)
class ContactInfo:
    email: str
    facebook: Maybe[str]
    phone: str
    mobile: Maybe[str]
    secondary_email: Maybe[str]


@dataclass(frozen=True)
class ContactAddres:
    city: Maybe[str]
    country: Maybe[str]
    street: Maybe[str]


@dataclass(frozen=True)
class ContactObj:
    user: UserObj
    contact_info: ContactInfo
    contact_addres: ContactAddres
    contact_dates: ContactDates
    account_id: AccountId
    contact_owner: UserId
    crm_id: CrmId
    description: Maybe[str]
    state: Maybe[str]
    title: Maybe[str]
    type_contact: Maybe[str]
    zip_contact: Maybe[str]


@dataclass(frozen=True)
class TeamObj:
    id_deparment: DeparmentId
    id_team: TeamId
    description: str
    name: str


@dataclass(frozen=True)
class TicketDates:
    modified_time: Maybe[DatetimeUTC]
    created_time: DatetimeUTC
    closed_time: Maybe[DatetimeUTC]
    customer_response_time: Maybe[DatetimeUTC]


@dataclass(frozen=True)
class TicketProperties:
    id_ticket: TicketId
    ticket_number: str
    suject: Maybe[str]
    channel: Maybe[str]
    status: Maybe[str]
    category: Maybe[str]
    is_escalated: bool
    priority: str
    resolution: Maybe[str]
    classification: Maybe[str]
    description: Maybe[str]


@dataclass(frozen=True)
class TicketObj:
    account_id: AccountId
    deparment_id: DeparmentId
    team_id: TeamId
    product_id: ProductId
    ticket_date: TicketDates
    ticket_properties: TicketProperties
    contact_id: ContactId
    email: str
    phone: str
    onhold_time: Maybe[str]


@dataclass(frozen=True)
class DeskClient:
    get_agents: Callable[[Token, Limit], Cmd[Stream[FrozenList[AgentObj]]]]
    get_contacts: Callable[[Token, Limit], Cmd[Stream[FrozenList[ContactObj]]]]
    get_tickets: Callable[[Token, Limit], Cmd[Stream[FrozenList[TicketObj]]]]
    get_teams: Callable[[Token], Cmd[ResultE[FrozenList[TeamObj]]]]
