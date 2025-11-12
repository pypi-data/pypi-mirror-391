from typing import Dict, Any, List, Optional
from .api.payment_api import PaymentApi
from .api.client import ApiClient
from .errors import ApiError


class Charge:
    """High-level charge operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = PaymentApi(api_client)

    def get(self, charge_id: str) -> Dict[str, Any]:
        """
        Get a specific charge

        Args:
            charge_id: Charge ID

        Returns:
            Charge data

        Raises:
            ApiError: If charge retrieval fails or charge not found
        """
        try:
            return self.api.get_charge(charge_id)
        except Exception as e:
            raise ApiError.from_error(e)

    def list(
        self,
        customer_id: str,
        page_size: Optional[int] = None,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List charges for a customer

        Args:
            customer_id: Customer ID
            page_size: Number of charges per page
            page_token: Pagination token

        Returns:
            List of charges with pagination info

        Raises:
            ApiError: If charge listing fails
        """
        try:
            return self.api.get_charges(customer_id, page_size, page_token)
        except Exception as e:
            raise ApiError.from_error(e)

    def iter(
        self,
        customer_id: str,
        page_size: int = 50,
        start_page_token: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        """Iterate through all charges for a customer.

        Args:
            customer_id: Customer ID.
            page_size: Page size per request (default 50).
            start_page_token: Optional starting page token.
            limit: Optional max number of charges to yield.

        Yields:
            Individual charge dicts.
        """
        yielded = 0
        token = start_page_token
        seen_tokens = set()

        while True:
            if token in seen_tokens:
                # Protect against accidental server token loops
                break
            if token:
                response = self.list(customer_id, page_size=page_size, page_token=token)
            else:
                response = self.list(customer_id, page_size=page_size)

            charges = []
            next_token = None

            if isinstance(response, dict):
                charges = response.get("charges", []) or []
                # Support pagination shape: response["pagination"]["nextPageToken"] or flat key
                pagination = response.get("pagination")
                if isinstance(pagination, dict):
                    next_token = pagination.get("nextPageToken") or pagination.get(
                        "next_page_token"
                    )
                else:
                    next_token = response.get("nextPageToken") or response.get(
                        "next_page_token"
                    )

            for charge in charges:
                yield charge
                yielded += 1
                if limit is not None and yielded >= limit:
                    return

            if not next_token:
                break
            seen_tokens.add(token)
            token = next_token

    def _get_auth_headers(self):
        """Debug method to check what authorization headers are being used"""
        if (
            hasattr(self.api, "api_client")
            and self.api.api_client
            and hasattr(self.api.api_client, "config")
        ):
            config = self.api.api_client.config
            if hasattr(config, "auth_settings") and "oauth2" in config.auth_settings:
                auth_setting = config.auth_settings["oauth2"]
                if callable(auth_setting.get("value")):
                    header_value = auth_setting["value"]()
                    return {auth_setting["key"]: header_value}
        return None
