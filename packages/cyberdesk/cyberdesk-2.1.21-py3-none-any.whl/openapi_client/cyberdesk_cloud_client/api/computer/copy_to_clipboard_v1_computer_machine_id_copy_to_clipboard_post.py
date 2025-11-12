from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.copy_to_clipboard_request import CopyToClipboardRequest
from ...models.copy_to_clipboard_v1_computer_machine_id_copy_to_clipboard_post_response_copy_to_clipboard_v1_computer_machine_id_copy_to_clipboard_post import (
    CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    machine_id: str,
    *,
    body: CopyToClipboardRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/v1/computer/{machine_id}/copy_to_clipboard",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    if response.status_code == 200:
        response_200 = CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost.from_dict(
            response.json()
        )

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: CopyToClipboardRequest,
) -> Response[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    """Copy to clipboard via Ctrl+C

     Execute Ctrl+C and return clipboard contents with the specified key name.

    Args:
        machine_id (str):
        body (CopyToClipboardRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: CopyToClipboardRequest,
) -> Optional[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    """Copy to clipboard via Ctrl+C

     Execute Ctrl+C and return clipboard contents with the specified key name.

    Args:
        machine_id (str):
        body (CopyToClipboardRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost, HTTPValidationError]
    """

    return sync_detailed(
        machine_id=machine_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: CopyToClipboardRequest,
) -> Response[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    """Copy to clipboard via Ctrl+C

     Execute Ctrl+C and return clipboard contents with the specified key name.

    Args:
        machine_id (str):
        body (CopyToClipboardRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        machine_id=machine_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    machine_id: str,
    *,
    client: AuthenticatedClient,
    body: CopyToClipboardRequest,
) -> Optional[
    Union[
        CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost,
        HTTPValidationError,
    ]
]:
    """Copy to clipboard via Ctrl+C

     Execute Ctrl+C and return clipboard contents with the specified key name.

    Args:
        machine_id (str):
        body (CopyToClipboardRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CopyToClipboardV1ComputerMachineIdCopyToClipboardPostResponseCopyToClipboardV1ComputerMachineIdCopyToClipboardPost, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            machine_id=machine_id,
            client=client,
            body=body,
        )
    ).parsed
