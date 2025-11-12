from fa_purity import FrozenList, ResultE
from fa_purity.json import (
    JsonObj,
    JsonUnfolder,
    Unfolder,
)
from fluidattacks_etl_utils import smash
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_zoho_sdk._decoders import (
    decode_account_id,
    decode_account_id_ticket,
    decode_contact_id,
    decode_crm_id,
    decode_deparment_id,
    decode_id_team,
    decode_maybe_str,
    decode_optional_date,
    decode_product_id,
    decode_profile_id,
    decode_require_date,
    decode_rol_id,
    decode_team_id,
    decode_ticket_id,
    decode_user_id,
)
from fluidattacks_zoho_sdk.ids import UserId
from fluidattacks_zoho_sdk.zoho_desk.core import (
    AgentObj,
    ContactAddres,
    ContactDates,
    ContactInfo,
    ContactObj,
    TeamObj,
    TicketDates,
    TicketObj,
    TicketProperties,
    UserObj,
)


def decode_user(raw: JsonObj) -> ResultE[UserObj]:
    return smash.smash_result_3(
        decode_user_id(raw),
        JsonUnfolder.optional(raw, "firstName", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.require(raw, "lastName", DecodeUtils.to_str),
    ).map(lambda obj: UserObj(*obj))


def decode_agent(raw: JsonObj) -> ResultE[AgentObj]:
    values = smash.smash_result_5(
        decode_user(raw),
        JsonUnfolder.require(raw, "isConfirmed", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "emailId", DecodeUtils.to_str),
        decode_profile_id(raw),
        decode_rol_id(raw),
    )

    return (
        smash.bind_chain(
            values,
            lambda vals: JsonUnfolder.require(raw, "status", DecodeUtils.to_str).map(
                lambda status: (*vals, status),
            ),
        )
        .alt(lambda v: v.map(lambda le: le, lambda r: r))
        .map(lambda obj: AgentObj(*obj))
    )


def decode_agents(raw: JsonObj) -> ResultE[FrozenList[AgentObj]]:
    return JsonUnfolder.require(
        raw,
        "data",
        lambda v: Unfolder.to_list_of(v, lambda j: Unfolder.to_json(j).bind(decode_agent)),
    )


def decode_contact_addres(raw: JsonObj) -> ResultE[ContactAddres]:
    return smash.smash_result_3(
        JsonUnfolder.optional(raw, "city", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "country", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "street", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
    ).map(lambda obj: ContactAddres(*obj))


def decode_contact_dates(raw: JsonObj) -> ResultE[ContactDates]:
    return smash.smash_result_2(
        JsonUnfolder.require(raw, "createdTime", DecodeUtils.to_date_time),
        JsonUnfolder.require(raw, "modifiedTime", DecodeUtils.to_date_time),
    ).map(lambda obj: ContactDates(*obj))


def decode_contact_info(raw: JsonObj) -> ResultE[ContactInfo]:
    return smash.smash_result_5(
        JsonUnfolder.require(raw, "email", DecodeUtils.to_str),
        JsonUnfolder.optional(raw, "facebook", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
        JsonUnfolder.require(raw, "phone", DecodeUtils.to_str),
        JsonUnfolder.optional(raw, "mobile", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
        JsonUnfolder.optional(raw, "secondaryEmail", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda x: x),
        ),
    ).map(lambda obj: ContactInfo(*obj))


def decode_contact_obj(raw: JsonObj) -> ResultE[ContactObj]:
    first = smash.smash_result_5(
        decode_user(raw),
        decode_contact_info(raw),
        decode_contact_addres(raw),
        decode_contact_dates(raw),
        decode_account_id(raw),
    )

    second = smash.smash_result_4(
        JsonUnfolder.require(raw, "ownerId", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(lambda j: UserId(j)),
        decode_crm_id(raw),
        JsonUnfolder.optional(raw, "description", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.optional(raw, "state", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
    )

    three = smash.smash_result_3(
        JsonUnfolder.optional(raw, "title", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.optional(raw, "type", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
        JsonUnfolder.optional(raw, "zip", DecodeUtils.to_opt_str).map(
            lambda v: v.bind(lambda j: j),
        ),
    )

    return smash.smash_result_3(first, second, three).map(lambda v: ContactObj(*v[0], *v[1], *v[2]))


def decode_contacts(raw: JsonObj) -> ResultE[FrozenList[ContactObj]]:
    return JsonUnfolder.require(
        raw,
        "data",
        lambda v: Unfolder.to_list_of(v, lambda j: Unfolder.to_json(j).bind(decode_contact_obj)),
    )


def decode_ticket_dates(raw: JsonObj) -> ResultE[TicketDates]:
    return smash.smash_result_4(
        decode_optional_date(raw, "modifiedTime"),
        decode_require_date(raw, "createdTime"),
        decode_optional_date(raw, "closedTime"),
        decode_optional_date(raw, "customerResponseTime"),
    ).map(lambda v: TicketDates(*v))


def decode_ticket_properties(raw: JsonObj) -> ResultE[TicketProperties]:
    first = smash.smash_result_5(
        decode_ticket_id(raw),
        JsonUnfolder.require(raw, "ticketNumber", DecodeUtils.to_str),
        decode_maybe_str(raw, "subject"),
        decode_maybe_str(raw, "channel"),
        decode_maybe_str(raw, "status"),
    )

    second = smash.smash_result_4(
        decode_maybe_str(raw, "category"),
        JsonUnfolder.require(raw, "isEscalated", DecodeUtils.to_bool),
        JsonUnfolder.require(raw, "priority", DecodeUtils.to_str),
        decode_maybe_str(raw, "resolution"),
    )

    three = smash.smash_result_2(
        decode_maybe_str(raw, "clasification"),
        decode_maybe_str(raw, "description"),
    )
    return smash.smash_result_3(first, second, three).map(
        lambda v: TicketProperties(*v[0], *v[1], *v[2]),
    )


def decode_ticket_obj(raw: JsonObj) -> ResultE[TicketObj]:
    first = smash.smash_result_5(
        decode_account_id_ticket(raw),
        decode_deparment_id(raw),
        decode_team_id(raw),
        decode_product_id(raw),
        decode_ticket_dates(raw),
    )
    second = smash.smash_result_5(
        decode_ticket_properties(raw),
        decode_contact_id(raw),
        JsonUnfolder.require(raw, "email", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "phone", DecodeUtils.to_str),
        decode_maybe_str(raw, "onholdTime"),
    )
    return smash.smash_result_2(first, second).map(lambda v: TicketObj(*v[0], *v[1]))


def decode_tickets(raw: JsonObj) -> ResultE[FrozenList[TicketObj]]:
    return JsonUnfolder.require(
        raw,
        "data",
        lambda v: Unfolder.to_list_of(v, lambda j: Unfolder.to_json(j).bind(decode_ticket_obj)),
    )


def decode_team_obj(raw: JsonObj) -> ResultE[TeamObj]:
    return smash.smash_result_4(
        decode_deparment_id(raw),
        decode_id_team(raw),
        JsonUnfolder.require(raw, "description", DecodeUtils.to_str),
        JsonUnfolder.require(raw, "name", DecodeUtils.to_str),
    ).map(lambda team: TeamObj(*team))


def decode_teams(raw: JsonObj) -> ResultE[FrozenList[TeamObj]]:
    return JsonUnfolder.require(
        raw,
        "teams",
        lambda v: Unfolder.to_list_of(v, lambda j: Unfolder.to_json(j).bind(decode_team_obj)),
    )
