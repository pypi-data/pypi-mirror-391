from __future__ import (
    annotations,
)

import logging
from collections.abc import Callable
from dataclasses import (
    dataclass,
)
from typing import (
    TypeVar,
)

from fa_purity import (
    Cmd,
    Coproduct,
    FrozenDict,
    FrozenList,
    Maybe,
    Result,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveFactory,
    JsonUnfolder,
    JsonValue,
)
from fluidattacks_etl_utils.decode import int_to_str
from fluidattacks_etl_utils.smash import bind_chain
from pure_requests import (
    response,
)
from pure_requests import (
    retry as _retry,
)
from pure_requests.basic import (
    Endpoint,
    HttpClient,
    HttpClientFactory,
    Params,
)
from pure_requests.retry import (
    HandledError,
    MaxRetriesReached,
)

from fluidattacks_zoho_sdk.auth import AuthApiFactory, Credentials, Token
from fluidattacks_zoho_sdk.ids import OrgId

from ._core import (
    HandledErrors,
    HTTPError,
    HttpJsonClient,
    JSONDecodeError,
    RelativeEndpoint,
    RequestException,
    UnhandledErrors,
)

LOG = logging.getLogger(__name__)

_S = TypeVar("_S")
_F = TypeVar("_F")
HTTP_UNAUTHORIZED: int = 401


def _refresh_access_token(creds: Credentials) -> Cmd[Token]:
    return AuthApiFactory.auth_api(creds).new_access_token


def _is_404(error: Maybe[HTTPError]) -> tuple[bool, int]:
    status: int = error.map(
        lambda v: v.raw.response.status_code,  # type: ignore[misc]
    ).value_or(0)
    status_is_404: bool = (
        error.map(lambda e: e.raw.response.status_code == HTTP_UNAUTHORIZED).value_or(False)  # type: ignore[misc]
    )
    return (status_is_404, status)


def _extract_http_error(error: HandledError[HandledErrors, UnhandledErrors]) -> Maybe[HTTPError]:
    return error.value.map(
        lambda handled: handled.error.map(
            lambda http_err: Maybe.some(http_err),
            lambda _: Maybe.empty(),
        ),
        lambda _: Maybe.empty(),
    )


def _retry_cmd(
    retry: int,
    item: Result[_S, _F],
    client_zoho: Client,
    make_request: Callable[[HttpClient], Cmd[Result[_S, _F]]],
) -> Cmd[Result[_S, _F]]:
    def handle_401(
        error: _F,
    ) -> Cmd[Result[_S, _F]]:
        is_401 = _is_404(_extract_http_error(error))  # type: ignore[arg-type]
        if is_401[0]:
            return Cmd.wrap_impure(lambda: LOG.info("Refreshing token...")) + _refresh_access_token(
                client_zoho.creds,
            ).bind(
                lambda acess_token: make_request(
                    HttpClientFactory.new_client(
                        None,
                        client_zoho.build_headers(acess_token),
                        False,
                    ),
                ),
            )
        log = Cmd.wrap_impure(
            lambda: LOG.info(
                "retry #%2s waiting... ",
                retry,
            ),
        )
        return _retry.cmd_if_fail(item, log + _retry.sleep_cmd(retry**2))

    return item.map(lambda _: Cmd.wrap_value(item)).alt(handle_401).to_union()


def _http_error_handler(
    error: HTTPError,
) -> HandledError[HandledErrors, UnhandledErrors]:
    err_code: int = error.raw.response.status_code  # type: ignore[misc]
    handled = (
        401,
        429,
    )
    if err_code in range(500, 600) or err_code in handled:
        return HandledError.handled(HandledErrors(Coproduct.inl(error)))
    return HandledError.unhandled(UnhandledErrors(Coproduct.inr(Coproduct.inl(error))))


def _handled_request_exception(
    error: RequestException,
) -> HandledError[HandledErrors, UnhandledErrors]:
    return (
        error.to_chunk_error()
        .map(lambda e: HandledError.handled(HandledErrors(Coproduct.inr(Coproduct.inl(e)))))
        .lash(
            lambda _: error.to_connection_error().map(
                lambda e: HandledError.handled(HandledErrors(Coproduct.inr(Coproduct.inr(e)))),
            ),
        )
        .value_or(HandledError.unhandled(UnhandledErrors(Coproduct.inr(Coproduct.inr(error)))))
    )


def _handled_errors(
    error: Coproduct[JSONDecodeError, Coproduct[HTTPError, RequestException]],
) -> HandledError[HandledErrors, UnhandledErrors]:
    """Classify errors."""
    return error.map(
        lambda _: HandledError.unhandled(UnhandledErrors(error)),
        lambda c: c.map(
            _http_error_handler,
            _handled_request_exception,
        ),
    )


def _adjust_unhandled(
    error: UnhandledErrors | MaxRetriesReached,
) -> Coproduct[UnhandledErrors, MaxRetriesReached]:
    return Coproduct.inr(error) if isinstance(error, MaxRetriesReached) else Coproduct.inl(error)


@dataclass(frozen=True)
class Client:
    _creds: Credentials
    _max_retries: int
    _org_id: OrgId

    def _full_endpoint(self, endpoint: RelativeEndpoint) -> Endpoint:
        return Endpoint("/".join(("https://desk.zoho.com/api/v1", *endpoint.paths)))

    @staticmethod
    def new(creds: Credentials, org_id: OrgId) -> Client:
        return Client(creds, 3, org_id)

    def _headers(self, acess_token: Token) -> JsonObj:
        return FrozenDict(
            {
                "orgId": JsonValue.from_primitive(
                    JsonPrimitiveFactory.from_raw(int_to_str(self._org_id.org_id.value)),
                ),
                "Authorization": JsonValue.from_primitive(
                    JsonPrimitiveFactory.from_raw(f"Zoho-oauthtoken {acess_token.raw_token}"),
                ),
            },
        )

    def get(
        self,
        endpoint: RelativeEndpoint,
        acess_token: Token,
        params: JsonObj,
    ) -> Cmd[
        Result[
            Coproduct[JsonObj, FrozenList[JsonObj]],
            Coproduct[UnhandledErrors, MaxRetriesReached],
        ]
    ]:
        _full = self._full_endpoint(endpoint)
        log = Cmd.wrap_impure(
            lambda: LOG.info("[API] get: %s\nparams = %s", _full, JsonUnfolder.dumps(params)),
        )
        client = HttpClientFactory.new_client(None, self._headers(acess_token), False)

        def make_request(
            new_client: HttpClient,
        ) -> Cmd[
            Result[
                Coproduct[JsonObj, FrozenList[JsonObj]],
                HandledError[HandledErrors, UnhandledErrors],
            ]
        ]:
            return (
                new_client.get(_full, Params(params))
                .map(
                    lambda r: r.alt(RequestException),
                )
                .map(
                    lambda r: bind_chain(r, lambda i: response.handle_status(i).alt(HTTPError)),
                )
                .map(
                    lambda r: bind_chain(
                        r,
                        lambda i: response.json_decode(i).alt(JSONDecodeError),
                    ).alt(
                        _handled_errors,
                    ),
                )
            )

        handled = log + make_request(client)
        return _retry.retry_cmd(
            handled,
            lambda retry, item: _retry_cmd(retry, item, self, make_request),
            self._max_retries,
        ).map(lambda r: r.alt(_adjust_unhandled))

    @property
    def client(self) -> HttpJsonClient:
        return HttpJsonClient(self.get)

    @property
    def creds(self) -> Credentials:
        return self._creds

    def build_headers(self, access_token: Token) -> JsonObj:
        return self._headers(access_token)
