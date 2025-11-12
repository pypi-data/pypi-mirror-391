from typing import (
    IO,
)

from fa_purity import Coproduct, FrozenList, Maybe, Result, ResultE, Unsafe
from fa_purity.date_time import DatetimeUTC
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    UnfoldedFactory,
    Unfolder,
)
from fluidattacks_etl_utils.decode import DecodeUtils
from fluidattacks_etl_utils.natural import Natural

from fluidattacks_zoho_sdk.auth import Credentials
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


def _decode_zoho_creds(raw: JsonObj) -> ResultE[Credentials]:
    client_id = JsonUnfolder.require(raw, "client_id", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    client_secret = JsonUnfolder.require(raw, "client_secret", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    refresh_token = JsonUnfolder.require(raw, "refresh_token", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    scopes_result = JsonUnfolder.require(
        raw,
        "scopes",
        lambda i: Unfolder.to_list_of(
            i,
            lambda x: Unfolder.to_primitive(x).bind(JsonPrimitiveUnfolder.to_str),
        ),
    )
    return client_id.bind(
        lambda cid: client_secret.bind(
            lambda secret: refresh_token.bind(
                lambda token: scopes_result.map(
                    lambda scopes: Credentials(cid, secret, token, frozenset(scopes)),
                ),
            ),
        ),
    )


def get_sub_json(raw: JsonObj, key: str) -> JsonObj:
    return (
        JsonUnfolder.require(raw, key, lambda v: Unfolder.to_json(v))
        .alt(Unsafe.raise_exception)
        .to_union()
    )


def decode_optional_date(raw: JsonObj, key: str) -> ResultE[Maybe[DatetimeUTC]]:
    return JsonUnfolder.optional(raw, key, DecodeUtils.to_opt_date_time).map(
        lambda v: v.bind(lambda j: j),
    )


def decode_require_date(raw: JsonObj, key: str) -> ResultE[DatetimeUTC]:
    return JsonUnfolder.require(raw, key, DecodeUtils.to_date_time)


def decode_maybe_str(raw: JsonObj, key: str) -> ResultE[Maybe[str]]:
    return JsonUnfolder.optional(raw, key, DecodeUtils.to_opt_str).map(
        lambda v: v.bind(lambda j: j),
    )


def decode_zoho_creds(auth_file: IO[str]) -> ResultE[Credentials]:
    return UnfoldedFactory.load(auth_file).bind(_decode_zoho_creds)


def decode_user_id(raw: JsonObj) -> ResultE[UserId]:
    return (
        JsonUnfolder.require(raw, "id", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(UserId)
    )


def decode_rol_id(raw: JsonObj) -> ResultE[RoleId]:
    return (
        JsonUnfolder.require(raw, "roleId", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(RoleId)
    )


def decode_profile_id(raw: JsonObj) -> ResultE[ProfileId]:
    return (
        JsonUnfolder.require(raw, "profileId", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(ProfileId)
    )


def decode_account_id(raw: JsonObj) -> ResultE[AccountId]:
    return (
        JsonUnfolder.require(raw, "accountId", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(AccountId)
    )


def decode_crm_id(raw: JsonObj) -> ResultE[CrmId]:
    return (
        JsonUnfolder.require(get_sub_json(raw, "zohoCRMContact"), "id", DecodeUtils.to_str)
        .bind(lambda v: Natural.from_int(int(v)))
        .map(lambda obj: CrmId(obj))
    )


def decode_deparment_id(raw: JsonObj) -> ResultE[DeparmentId]:
    return (
        JsonUnfolder.optional(raw, "departmentId", DecodeUtils.to_opt_str)
        .map(
            lambda v: v.bind(lambda x: x).map(
                lambda j: Natural.from_int(int(j)).alt(Unsafe.raise_exception).to_union(),
            ),
        )
        .map(lambda obj: DeparmentId(obj))
    )


def decode_product_id(raw: JsonObj) -> ResultE[ProductId]:
    return (
        JsonUnfolder.optional(raw, "productId", DecodeUtils.to_opt_str)
        .map(
            lambda v: v.bind(lambda x: x).map(
                lambda j: Natural.from_int(int(j)).alt(Unsafe.raise_exception).to_union(),
            ),
        )
        .map(lambda obj: ProductId(obj))
    )


def decode_team_id(raw: JsonObj) -> ResultE[TeamId]:
    return JsonUnfolder.require(raw, "teamId", DecodeUtils.to_str).bind(
        lambda v: Natural.from_int(int(v)).map(lambda obj: TeamId(obj)),
    )


def decode_ticket_id(raw: JsonObj) -> ResultE[TicketId]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_str).bind(
        lambda v: Natural.from_int(int(v)).map(lambda obj: TicketId(obj)),
    )


def decode_contact_id(raw: JsonObj) -> ResultE[ContactId]:
    return JsonUnfolder.require(get_sub_json(raw, "contact"), "id", DecodeUtils.to_str).bind(
        lambda v: Natural.from_int(int(v)).map(lambda obj: ContactId(obj)),
    )


def decode_account_id_ticket(raw: JsonObj) -> ResultE[AccountId]:
    account_obj = get_sub_json(raw, "contact")
    return JsonUnfolder.require(
        get_sub_json(account_obj, "account"),
        "id",
        DecodeUtils.to_str,
    ).bind(lambda v: Natural.from_int(int(v)).map(lambda obj: AccountId(obj)))


def decode_id_team(raw: JsonObj) -> ResultE[TeamId]:
    return JsonUnfolder.require(raw, "id", DecodeUtils.to_str).bind(
        lambda v: Natural.from_int(int(v)).map(lambda obj: TeamId(obj)),
    )


def assert_single(item: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[JsonObj]:
    return item.map(
        Result.success,
        lambda _: Result.failure(ValueError("Expected a json not a list")),
    )


def assert_multiple(item: Coproduct[JsonObj, FrozenList[JsonObj]]) -> ResultE[FrozenList[JsonObj]]:
    return item.map(
        lambda _: Result.failure(ValueError("Expected a json list not a single json")),
        Result.success,
    )
