import json
from collections.abc import Callable
from contextlib import contextmanager
from typing import Optional

import urllib3.exceptions

from dasl_api import ApiException


class ConflictError(Exception):
    """
    Simple exception wrapper for 409 errors returned from the API
    """

    def __init__(self, resource: str, identifier: str, message: str) -> None:
        self.resource = resource
        self.identifier = identifier
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Conflict: resource_type='{self.resource}' identifier='{self.identifier}' message='{self.message}'"


class NotFoundError(Exception):
    """
    Simple exception wrapper for 404 errors returned from the API
    """

    def __init__(
        self, identifier: str, message: str, resource_type: str = None
    ) -> None:
        self.identifier = identifier
        self.message = message
        self.resource_type = resource_type
        super().__init__(message)

    def __str__(self) -> str:
        if self.resource_type:
            return f"NotFound: resource_type='{self.resource_type}' identifier='{self.identifier}' message='{self.message}'"
        return f"NotFound: identifier='{self.identifier}' message='{self.message}'"


class BadRequestError(Exception):
    """
    Simple exception wrapper for 400 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"BadRequest: message='{self.message}'"


class UnauthorizedError(Exception):
    """
    Simple exception wrapper for 401 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Unauthorized: message='{self.message}'"


class ForbiddenError(Exception):
    """
    Simple exception wrapper for 403 errors returned from the API
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Forbidden: message='{self.message}'"


class WorkspaceLookupError(Exception):
    """Internal exception wrapper for workspace lookup errors"""

    def __init__(self, message: str, reason: Exception = None) -> None:
        self.message = message
        self.reason = reason
        super().__init__(message)

    def __str__(self) -> str:
        return f"Workspace lookup error: {self.message}"


class RegionMismatchError(Exception):
    """
    Exception raised when authentication fails due to cross-region communication issues.
    This typically occurs when the client is configured with a DASL host in a different
    cloud region than the Databricks workspace.
    """

    def __init__(
        self,
        workspace_url: str,
        current_host: Optional[str],
        expected_host: Optional[str],
        original_error: Exception = None,
    ) -> None:
        self.workspace_url = workspace_url
        self.current_host = current_host
        self.expected_host = expected_host
        self.original_error = original_error

        if current_host is not None and expected_host is not None:
            message = (
                f"Cannot authenticate workspace '{workspace_url}' using host '{current_host}'. "
                f"The workspace is located in a different cloud region. "
                f"Expected host: '{expected_host}'. "
                f"Please specify the correct region or dasl_host when creating the client, "
                f"or omit these parameters to allow auto-configuration."
            )
        else:
            from dasl_client.regions import Regions

            supported_regions = "\n  ".join(["", *Regions.list()])
            message = (
                f"Cannot authenticate workspace '{workspace_url}'. This workspace may be "
                f"located in an unsupported cloud region. Supported regions: {supported_regions}"
            )
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"Region mismatch: {self.message}"


def handle_errors(f: Callable) -> Callable:
    """
    A decorator that handles errors returned from the API.

    :param f: the function that could return an API error
    :return: The output from the callable 'f'. If an Api error was raise,
             re-cast it to a library error before re-raising.
    """

    def error_handler(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ApiException as e:
            body = json.loads(e.body)
            if e.status == 400:
                raise BadRequestError(body["message"])
            if e.status == 401:
                raise BadRequestError(body["message"])
            if e.status == 403:
                raise ForbiddenError(body["message"])
            if e.status == 404:
                raise NotFoundError(
                    body["identifier"], body["message"], body.get("resourceType")
                )
            if e.status == 409:
                raise ConflictError(
                    body["resourceType"], body["identifier"], body["message"]
                )
            else:
                raise e
        except Exception as e:
            raise e

    return error_handler


@contextmanager
def error_handler(**context):
    """
    A context manager that handles errors returned from the API.

    Within the context, if an API error is raised, it is re-cast to a library
    error before re-raising.

    :param context: Optional context including 'workspace_url' and 'host' for
                    better error messages in region mismatch scenarios.
    """

    workspace_url = context.get("workspace_url")
    current_host = context.get("host")

    try:
        yield
    except ApiException as e:
        body = json.loads(e.body)
        if e.status == 400:
            raise BadRequestError(body["message"])
        if e.status == 401:
            raise BadRequestError(body["message"])
        if e.status == 403:
            raise ForbiddenError(body["message"])
        if e.status == 404:
            raise NotFoundError(
                body["identifier"], body["message"], body.get("resourceType")
            )
        if e.status == 409:
            raise ConflictError(
                body["resourceType"], body["identifier"], body["message"]
            )
        else:
            raise e
    except (urllib3.exceptions.SSLError, urllib3.exceptions.MaxRetryError) as e:
        # Check if this is a region mismatch issue
        _raise_if_region_mismatch(e, workspace_url, current_host)

        # Raise the original error, if not
        raise e
    except Exception as e:
        raise e


def _raise_if_region_mismatch(
    e: Exception, workspace_url: Optional[str], current_host: Optional[str]
):
    if workspace_url:
        err = e

        # Unwrap a WorkspaceLookupError first
        if isinstance(err, WorkspaceLookupError):
            err = err.reason

        # Unwrap a MaxRetryError
        if isinstance(err, urllib3.exceptions.MaxRetryError):
            err = err.reason

        # Check if the error is SSL-related
        is_ssl_error = isinstance(err, urllib3.exceptions.SSLError)

        if is_ssl_error:
            try:
                from dasl_client.metadata import WorkspaceMetadata

                # We call into get_workspace_metadata, NOT get_endpoint_for_workspace because
                # we would risk creating a loop otherwise
                expected_host = WorkspaceMetadata.get_workspace_metadata(workspace_url)
                expected_host = expected_host and expected_host.api_url
                if expected_host and expected_host != current_host:
                    raise RegionMismatchError(
                        workspace_url, current_host, expected_host, e
                    )
            except RegionMismatchError:
                raise
            except Exception:
                # If we can't determine the expected host, but there was no provided host, this
                # region may not be supported
                if current_host is None:
                    raise RegionMismatchError(workspace_url, current_host, None, e)

                # Otherwise, let the caller re-raise original error
                pass
