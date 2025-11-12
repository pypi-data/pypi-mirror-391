import time
import logging
import requests
from typing import Any, Dict, List, Optional, Tuple, Type, Union, Callable
from requests.exceptions import RequestException
from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.message import Message

from ..version import VERSION
from ..errors import ApiError as LegacyApiError


class ApiError(LegacyApiError):
    """Exception raised for API errors.

    Extended to include `error_type` parsed from JSON error payload when available.
    Jamm's backend may embed structured details in a `details` array; entries with a
    `debug` field matching one of the enum values in `ErrorType` (proto) are surfaced.
    """

    def __init__(
        self,
        code: int = 0,
        message: str = "",
        response_headers: Optional[Dict] = None,
        response_body: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        debug_values: Optional[List[str]] = None,
        decoded_values: Optional[List[str]] = None,
    ):
        # Initialize legacy/base ApiError to unify exception hierarchy so `except jamm.ApiError` works.
        super().__init__(
            message=message,
            code=code,
            status=code,
            error_type=error_type,
            details=error_details,
            response_headers=response_headers,
            response_body=response_body,
        )
        # Additional enriched fields
        self.error_code = error_code  # connect-style string code, e.g. 'internal'
        self.debug_values = debug_values or []
        self.decoded_values = decoded_values or []

    @classmethod
    def from_error(cls, err: Exception) -> "ApiError":
        """Best-effort conversion of arbitrary exception to ApiError while preserving structured fields."""
        if isinstance(err, cls):
            return err
        # Fallback extraction
        code = getattr(err, "code", getattr(err, "status", 0)) or 0
        headers: Optional[Dict] = getattr(err, "response_headers", None)
        body: Optional[str] = getattr(err, "response_body", None)
        message: str = getattr(err, "message", str(err))
        details: Optional[Dict[str, Any]] = getattr(err, "details", None)
        return cls(
            code=code,
            message=message,
            response_headers=headers,
            response_body=body,
            error_details=details,
        )


class RequestInterceptor:
    """Interface for request interceptors."""

    def intercept(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        params: Dict[str, Any],
        body: Any,
    ) -> Tuple[str, str, Dict[str, str], Dict[str, Any], Any]:
        """
        Intercept and potentially modify a request before it's sent.

        Args:
            method: HTTP method
            url: Full request URL
            headers: Request headers
            params: Query parameters
            body: Request body

        Returns:
            Tuple of (method, url, headers, params, body)
        """
        return method, url, headers, params, body


class ResponseInterceptor:
    """Interface for response interceptors."""

    def intercept(
        self, response: requests.Response, request_data: Dict[str, Any]
    ) -> requests.Response:
        """
        Intercept and potentially modify a response before it's processed.

        Args:
            response: Response object
            request_data: Original request data

        Returns:
            Modified or original response
        """
        return response


class RetryConfiguration:
    """Configuration for API request retries."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_status_codes: List[int] = None,
        retry_methods: List[str] = None,
        initial_backoff_ms: int = 100,
        max_backoff_ms: int = 10000,
        backoff_factor: float = 2.0,
    ):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            retry_status_codes: List of HTTP status codes to retry on
            retry_methods: List of HTTP methods to retry
            initial_backoff_ms: Initial backoff time in milliseconds
            max_backoff_ms: Maximum backoff time in milliseconds
            backoff_factor: Multiplier for backoff time on each retry
        """
        self.max_retries = max_retries
        self.retry_status_codes = retry_status_codes or [408, 429, 500, 502, 503, 504]
        self.retry_methods = retry_methods or [
            "GET",
            "HEAD",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_factor = backoff_factor

    def should_retry(self, method: str, status_code: int, attempt: int) -> bool:
        """
        Determine if a request should be retried.

        Args:
            method: HTTP method
            status_code: Response status code
            attempt: Current attempt number (0-based)

        Returns:
            True if the request should be retried, False otherwise
        """
        return (
            attempt < self.max_retries
            and method.upper() in [m.upper() for m in self.retry_methods]
            and status_code in self.retry_status_codes
        )

    def get_backoff_time(self, attempt: int) -> float:
        """
        Calculate backoff time in seconds for a retry attempt.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Backoff time in seconds
        """
        backoff_ms = min(
            self.initial_backoff_ms * (self.backoff_factor**attempt),
            self.max_backoff_ms,
        )
        # Add true random jitter (±20%)
        import random

        jitter_factor = random.uniform(0.8, 1.2)
        return (backoff_ms * jitter_factor) / 1000  # Convert to seconds


class Configuration:
    """Configuration for the API client."""

    def __init__(self, host: str = "api.develop.jamm-pay.jp", scheme: str = "https"):
        self.host = host
        self.scheme = scheme
        self.timeout = (30, 90)  # (connect timeout, read timeout)
        self.verify_ssl = True
        self.verify_ssl_host = True
        self.ssl_ca_cert = None
        self.cert_file = None
        self.key_file = None
        self.debugging = False
        self.auth_settings = {}
        self.logger = logging.getLogger("jamm_sdk")
        self.retry = RetryConfiguration()

    def set_oauth_token(self, access_token: str):
        """Set OAuth access token for authentication"""
        self.auth_settings["oauth2"] = {
            "type": "oauth2",
            "in": "header",
            "key": "Authorization",
            "value": f"Bearer {access_token}",
        }


class ApiClient:
    """Base API client for making API requests."""

    def __init__(self, config: Configuration = None):
        """Initialize the API client."""
        self.config = config or Configuration()
        self._user_agent = f"Jamm-SDK/Python/{VERSION}"
        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": self._user_agent,
        }
        self.session = requests.Session()
        self.request_interceptors: List[RequestInterceptor] = []
        self.response_interceptors: List[ResponseInterceptor] = []

    def add_request_interceptor(self, interceptor: RequestInterceptor) -> None:
        """
        Add a request interceptor.

        Args:
            interceptor: RequestInterceptor instance
        """
        self.request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: ResponseInterceptor) -> None:
        """
        Add a response interceptor.

        Args:
            interceptor: ResponseInterceptor instance
        """
        self.response_interceptors.append(interceptor)

    def call_api(
        self, http_method: str, path: str, opts: Dict = None
    ) -> Tuple[Any, int, Dict]:
        """
        Call an API with given options.

        Args:
            http_method: HTTP method (GET, POST, etc.)
            path: URL path for the request
            opts: Dictionary of options including query_params, header_params,
                  body, auth_names, and return_type

        Returns:
            Tuple of (data, status_code, headers)
        """
        opts = opts or {}

        # Build the request URL
        url = self._build_request_url(path)

        # Build a single headers dict (avoid duplicate constructions later)
        header_params = self.default_headers.copy()
        if opts.get("header_params"):
            header_params.update(opts["header_params"])

        # Accept / Content-Type resolution (prefer JSON)
        accept = self.select_header_accept(opts.get("accepts", []))
        if accept:
            header_params["Accept"] = accept
        content_type = self.select_header_content_type(opts.get("content_types", []))
        if content_type:
            header_params["Content-Type"] = content_type

        # Query parameters
        query_params = opts.get("query_params", {})

        # Form parameters
        form_params = opts.get("form_params", {})

        # Authentication
        auth_names = opts.get("auth_names", [])
        self._update_params_for_auth(header_params, query_params, auth_names)

        # Set up body for POST, PUT, PATCH, DELETE methods
        body = None
        if http_method.lower() in ["post", "put", "patch", "delete"]:
            body = self._build_request_body(
                header_params, form_params, opts.get("body")
            )

        # Debug logging
        if self.config.debugging:
            self.config.logger.debug(f"Request URL: {url}")
            self.config.logger.debug(f"Request method: {http_method}")
            self.config.logger.debug(f"Request headers: {header_params}")
            self.config.logger.debug(f"Request query params: {query_params}")
            if body:
                self.config.logger.debug(f"Request body: {body}")

        # Apply authentication directly to header_params
        auth_names = opts.get("auth_names", [])
        for auth_name in auth_names:
            if auth_name in self.config.auth_settings:
                auth_setting = self.config.auth_settings[auth_name]
                if auth_setting.get("in") == "header":
                    value = auth_setting.get("value")
                    header_params[auth_setting["key"]] = (
                        value() if callable(value) else value
                    )

        # Debug the headers
        # print(f"DEBUG - API Request Headers: {headers}")
        # print(f"DEBUG - API Request URL: {url}")
        # print(f"DEBUG - API Request Method: {http_method}")
        # print(f"DEBUG - API Request Query Params: {query_params}")
        # print(f"DEBUG - API Request Body: {body}")

        # Apply request interceptors
        method, url, header_params, query_params, body = (
            self._apply_request_interceptors(
                http_method, url, header_params, query_params, body
            )
        )

        # Retry logic
        return self._execute_with_retry(
            method, url, header_params, query_params, body, opts
        )

    def _execute_with_retry(
        self, method: str, url: str, headers: Dict, params: Dict, body: Any, opts: Dict
    ) -> Tuple[Any, int, Dict]:
        """Execute request with retry logic."""
        attempt = 0
        last_exception = None

        while True:
            try:
                return self._execute_request(method, url, headers, params, body, opts)
            except ApiError as e:
                last_exception = e

                # Should we retry?
                if not self.config.retry.should_retry(method, e.code, attempt):
                    raise

                # Calculate backoff time
                backoff_time = self.config.retry.get_backoff_time(attempt)

                # Log retry attempt
                if self.config.debugging:
                    self.config.logger.debug(
                        f"Request failed with status {e.code}. Retrying in {backoff_time:.2f}s "
                        f"(attempt {attempt + 1}/{self.config.retry.max_retries})"
                    )

                # Wait before retrying
                time.sleep(backoff_time)

                # Increment attempt counter
                attempt += 1
            except RequestException as re:
                # Treat network exceptions as retryable with pseudo status code 0
                last_exception = ApiError(
                    code=0, message=str(re), error_details={"network_error": True}
                )
                if not self.config.retry.should_retry(method, 0, attempt):
                    raise last_exception
                backoff_time = self.config.retry.get_backoff_time(attempt)
                if self.config.debugging:
                    self.config.logger.debug(
                        f"Network error '{re}'. Retrying in {backoff_time:.2f}s (attempt {attempt + 1}/{self.config.retry.max_retries})"
                    )
                time.sleep(backoff_time)
                attempt += 1
            except Exception as e:
                self.config.logger.error(f"Non-retryable error: {e}")
                raise

        # This should never be reached due to the while True loop
        raise last_exception

    def _execute_request(
        self, method: str, url: str, headers: Dict, params: Dict, body: Any, opts: Dict
    ) -> Tuple[Any, int, Dict]:
        """Execute a single request without retry."""
        request_data = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "body": body,
            "opts": opts,
        }

        try:
            # Make the HTTP request
            # Handle request body
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
                "params": params,
                "timeout": self.config.timeout,
                "verify": (
                    self.config.ssl_ca_cert
                    if self.config.ssl_ca_cert
                    else self.config.verify_ssl
                ),
            }

            # Add certification if provided
            if self.config.cert_file and self.config.key_file:
                request_kwargs["cert"] = (self.config.cert_file, self.config.key_file)

            # Handle body based on type
            if body is not None:
                if isinstance(body, dict):
                    request_kwargs["json"] = body
                elif isinstance(body, (str, bytes)):
                    request_kwargs["data"] = body
                else:
                    # For other types, convert to string or handle specially
                    request_kwargs["data"] = body

            response = self.session.request(**request_kwargs)

            # Debug logging
            if self.config.debugging:
                self.config.logger.debug(f"Response status: {response.status_code}")
                self.config.logger.debug(f"Response headers: {response.headers}")
                self.config.logger.debug(f"Response body: {response.text}")

            # print(f"DEBUG - API Response Status: {response.status_code}")
            # print(f"DEBUG - API Response Headers: {response.headers}")
            # print(f"DEBUG - API Response Body: {response.text}")

            # Apply response interceptors
            response = self._apply_response_interceptors(response, request_data)

            # Check for errors
            if not (200 <= response.status_code < 300):
                error_details = None
                msg = f"Error {response.status_code}: {response.reason}"
                parsed_error_type = None
                parsed_error_code = None
                debug_values: List[str] = []
                decoded_values: List[str] = []
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type or response.text.startswith("{"):
                    try:
                        parsed = response.json()
                        if isinstance(parsed, dict):
                            error_details = parsed
                            # connect-style string error code
                            if isinstance(parsed.get("code"), str):
                                parsed_error_code = parsed["code"].strip()
                            for key in ("message", "error", "detail"):
                                val = parsed.get(key)
                                if isinstance(val, str) and val.strip():
                                    msg = val
                                    break
                            details_arr = (
                                parsed.get("details") or parsed.get("detail") or []
                            )
                            if isinstance(details_arr, list):
                                for d in details_arr:
                                    if isinstance(d, dict):
                                        # Collect debug markers
                                        if isinstance(d.get("debug"), str):
                                            dbg = d["debug"].strip()
                                            debug_values.append(dbg)
                                            if (
                                                dbg.startswith("ERROR_TYPE_")
                                                and parsed_error_type is None
                                            ):
                                                parsed_error_type = dbg
                                        # Decode base64 value if present
                                        val_field = d.get("value")
                                        if isinstance(val_field, str):
                                            import base64

                                            try:
                                                decoded = base64.b64decode(
                                                    val_field
                                                    + ("=" * (-len(val_field) % 4))
                                                )
                                                printable = decoded.decode(
                                                    "utf-8", errors="ignore"
                                                )
                                                if printable:
                                                    decoded_values.append(printable)
                                            except Exception as e:
                                                logging.debug(
                                                    "Failed to base64 or UTF-8 decode value '%s': %s",
                                                    val_field, e
                                                )
                    except ValueError:
                        pass
                # Fallback: derive error_type from any collected debug value containing pattern
                if parsed_error_type is None and debug_values:
                    # Choose the first debug value containing ERROR_TYPE_ substring
                    for dbg in debug_values:
                        if "ERROR_TYPE_" in dbg:
                            parsed_error_type = dbg
                            break
                # Absolute fallback: scan raw body for ERROR_TYPE_ token
                if parsed_error_type is None and "ERROR_TYPE_" in (response.text or ""):
                    import re

                    match = re.search(r"ERROR_TYPE_[A-Z0-9_]+", response.text)
                    if match:
                        parsed_error_type = match.group(0)
                raise ApiError(
                    code=response.status_code,
                    message=msg,
                    response_headers=response.headers,
                    response_body=response.text,
                    error_details=error_details,
                    error_type=parsed_error_type,
                    error_code=parsed_error_code,
                    debug_values=debug_values,
                    decoded_values=decoded_values,
                )

            # Deserialize response
            data = None
            if "return_type" in opts and opts["return_type"]:
                try:
                    data = self._deserialize(response, opts["return_type"])
                except Exception as deserialize_error:
                    # Use safe error handling with f-strings
                    error_msg = (
                        f"Failed to deserialize response: {str(deserialize_error)}"
                    )
                    # print(f"DEBUG - {error_msg}")
                    # Return the raw text or parsed JSON
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            return (
                                response.json(),
                                response.status_code,
                                response.headers,
                            )
                        except:
                            return response.text, response.status_code, response.headers
                    else:
                        return response.text, response.status_code, response.headers

            return data, response.status_code, response.headers

        except ApiError:
            raise
        except Exception as e:
            error_msg = f"API call failed: {str(e)}"
            raise ApiError(
                message=error_msg,
                error_details={"exception_type": type(e).__name__},
                error_type=None,
                error_code=None,
            )

    def _apply_request_interceptors(
        self, method: str, url: str, headers: Dict, params: Dict, body: Any
    ) -> Tuple[str, str, Dict, Dict, Any]:
        """Apply request interceptors to modify the request before sending."""
        for interceptor in self.request_interceptors:
            method, url, headers, params, body = interceptor.intercept(
                method, url, headers, params, body
            )
        return method, url, headers, params, body

    def _apply_response_interceptors(
        self, response: requests.Response, request_data: Dict
    ) -> requests.Response:
        """Apply response interceptors to modify the response after receiving."""
        for interceptor in self.response_interceptors:
            response = interceptor.intercept(response, request_data)
        return response

    def _build_request_url(self, path: str) -> str:
        """Build the full URL for a request."""
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path

        return f"{self.config.scheme}://{self.config.host}{path}"

    def _update_params_for_auth(
        self, header_params: Dict, query_params: Dict, auth_names: List[str]
    ) -> None:
        """Update header and query parameters based on authentication settings."""
        for auth_name in auth_names:
            auth_setting = self.config.auth_settings.get(auth_name, {})
            if not auth_setting:
                continue

            if auth_setting.get("in") == "header":
                if callable(auth_setting["value"]):
                    header_params[auth_setting["key"]] = auth_setting["value"]()
                else:
                    header_params[auth_setting["key"]] = auth_setting["value"]
            elif auth_setting.get("in") == "query":
                query_params[auth_setting["key"]] = auth_setting["value"]

    def _build_request_body(
        self, header_params: Dict, form_params: Dict, body: Any
    ) -> Any:
        """Build the HTTP request body."""
        if header_params.get("Content-Type") == "application/x-www-form-urlencoded":
            # Form URL-encoded body
            return form_params
        elif body is not None:
            # For protobuf messages
            if isinstance(body, Message):
                if header_params.get("Content-Type") == "application/x-protobuf":
                    return body.SerializeToString()
                else:
                    # Convert protobuf to Python dict (not raw JSON string) for json serialization
                    import json

                    json_str = MessageToJson(body)
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # Fallback to raw string if parsing fails
                        return json_str
            # For dict, already handled by requests json parameter
            elif isinstance(body, dict):
                return body
            # For objects with to_dict method (common in models)
            elif hasattr(body, "to_dict"):
                return body.to_dict()
            # Default: return as is
            return body
        return None

    def _deserialize(self, response, return_type):
        """Deserialize response to the specified type."""
        # Handle empty response bodies gracefully
        if not response.content:
            # For generic 'object' return types, normalize to empty dict instead of None
            if return_type == "object":
                return {}
            return None

        content_type = response.headers.get("Content-Type", "")

        # Protobuf deserialization
        if isinstance(return_type, type) and issubclass(return_type, Message):
            if "application/x-protobuf" in content_type:
                return return_type.FromString(response.content)
            else:
                # Try to parse JSON to protobuf
                try:
                    msg = return_type()
                    return Parse(response.text, msg)
                except Exception as e:
                    self.config.logger.error(
                        f"Failed to parse JSON to {return_type.__name__}: {e}"
                    )
                    raise ApiError(
                        message=f"Failed to parse response as {return_type.__name__}"
                    )

        # Handle JSON response
        if "application/json" in content_type:
            try:
                data = response.json()

                # Return as is if return_type is 'object'
                if return_type == "object":
                    return data

                # If return_type has a from_dict method
                if hasattr(return_type, "from_dict"):
                    return return_type.from_dict(data)

                # If return_type is a class, try to instantiate it
                if isinstance(return_type, type):
                    try:
                        return return_type(**data)
                    except (TypeError, ValueError) as e:
                        self.config.logger.warning(
                            f"Could not instantiate {return_type.__name__}: {e}"
                        )
                        return data  # Return raw data instead

                return data
            except ValueError:
                self.config.logger.error("Failed to parse response as JSON")
                return response.text

        # Other response types
        if return_type == "str":
            return response.text
        elif return_type == "bytes":
            return response.content
        elif return_type == "bool":
            return response.text.lower() == "true"

        # Default: return raw response
        return response.content

    def select_header_accept(self, accepts: List[str]) -> Optional[str]:
        """
        Select the Accept header from available options.

        Args:
            accepts: List of acceptable content types

        Returns:
            Selected Accept header value
        """
        if not accepts:
            return None

        # Prefer JSON if available
        for accept in accepts:
            if "application/json" in accept:
                return accept

        # Otherwise return the first one or join all
        return accepts[0] if len(accepts) == 1 else ",".join(accepts)

    def select_header_content_type(self, content_types: List[str]) -> str:
        """
        Select the Content-Type header from available options.

        Args:
            content_types: List of available content types

        Returns:
            Selected Content-Type header value
        """
        if not content_types:
            return "application/json"  # Default

        # Prefer JSON if available
        for content_type in content_types:
            if "application/json" in content_type:
                return content_type

        return content_types[0]

    @property
    def user_agent(self) -> str:
        """Get the user agent string."""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent: str):
        """Set the user agent string."""
        self._user_agent = user_agent
        self.default_headers["User-Agent"] = user_agent

    def _select_headers(
        self, content_types: List[str], accepts: List[str]
    ) -> Dict[str, str]:
        """
        Select headers based on content types and accept types.

        Args:
            content_types: List of content types from the user
            accepts: List of acceptable response types

        Returns:
            Dictionary of selected headers
        """
        headers = {}

        # Content-Type
        content_type = self.select_header_content_type(content_types)
        if content_type:
            headers["Content-Type"] = content_type

        # Accept
        accept = self.select_header_accept(accepts)
        if accept:
            headers["Accept"] = accept

        return headers
