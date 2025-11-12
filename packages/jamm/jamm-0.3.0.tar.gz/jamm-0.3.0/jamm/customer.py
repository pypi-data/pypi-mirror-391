from typing import Dict, Any, Optional
from .api.customer_api import CustomerApi
from .api.client import ApiClient
from .errors import ApiError


class Customer:
    """High-level customer operations"""

    def __init__(self, api_client: Optional[ApiClient] = None):
        self.api = CustomerApi(api_client)

    @property
    def KycStatus(self):
        """Access to KYC status enums"""
        try:
            from .models import KycStatus

            return KycStatus
        except ImportError:

            class MockKycStatus:
                APPROVED = "APPROVED"
                DENIED = "DENIED"
                IN_REVIEW = "IN_REVIEW"
                NOT_SUBMITTED = "NOT_SUBMITTED"

            return MockKycStatus

    @property
    def PaymentAuthorizationStatus(self):
        """Access to payment authorization status enums"""
        try:
            from .models import PaymentAuthorizationStatus

            return PaymentAuthorizationStatus
        except ImportError:

            class MockPaymentAuthorizationStatus:
                AUTHORIZED = "AUTHORIZED"
                NOT_AUTHORIZED = "NOT_AUTHORIZED"

            return MockPaymentAuthorizationStatus

    def _normalize_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a raw customer dict ensuring required convenience keys.

        Adds defaults:
          activated: False if missing
          linkInitialized: False if missing
          bankInformation: {} if present but None, else ensure key exists (None if absent)
          status: ensure object with payment & kyc keys (None if absent)
        """
        if not isinstance(data, dict):
            return data  # leave non-dict untouched
        if data.get("activated") is None:
            data["activated"] = False
        if data.get("linkInitialized") is None:
            data["linkInitialized"] = False
        # Only add key if definitely absent to avoid overwriting truthy/filled structures
        if "bankInformation" not in data:
            data["bankInformation"] = None
        elif data["bankInformation"] is None:
            # Provide empty dict instead of null for easier downstream usage (optional choice)
            data["bankInformation"] = {}
        # Normalize status (expects nested payment & kyc enums/strings)
        status = data.get("status")
        if status is None or not isinstance(status, dict):
            data["status"] = {"payment": None, "kyc": None}
        else:
            if "payment" not in status:
                status["payment"] = None
            if "kyc" not in status:
                status["kyc"] = None
        return data

    def create(self, buyer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a customer

        Args:
            buyer: Customer data

        Returns:
            Customer object

        Raises:
            ApiError: If API call fails
        """
        try:
            request_body = {"buyer": buyer}
            r = self.api.create(request_body)

            if isinstance(r, dict) and "customer" in r:
                # Some responses may nest again under 'customer'
                inner = r["customer"]
                if isinstance(inner, dict) and "customer" in inner:
                    inner = inner["customer"]
                return self._normalize_customer(inner)
            else:
                return self._normalize_customer(r)
        except Exception as e:
            raise ApiError.from_error(e)

    def get(self, id_or_email: str) -> Dict[str, Any]:
        """
        Get a customer by ID or email

        Args:
            id_or_email: Customer ID or email

        Returns:
            Customer object with activated flag properly set

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            r = self.api.get(id_or_email)

            if isinstance(r, dict) and "customer" in r:
                customer = r["customer"]
                if isinstance(customer, dict) and "customer" in customer:
                    # Handle nested structure
                    customer = customer["customer"]
            else:
                customer = r
            return self._normalize_customer(customer)
        except Exception as e:
            raise ApiError.from_error(e)

    def get_contract(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get customer contract

        Args:
            customer_id: Customer ID

        Returns:
            Contract data or None if not found
        """
        try:
            return self.api.get_contract(customer_id)
        except Exception as e:
            if hasattr(e, "status") and e.status == 404:
                return None
            elif hasattr(e, "code") and e.code == 404:
                return None
            elif "404" in str(e) or "not found" in str(e).lower():
                return None
            else:
                raise ApiError.from_error(e)

    def update(self, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a customer

        Args:
            customer_id: Customer ID
            data: Update data

        Returns:
            Updated customer object

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            r = self.api.update(customer_id, data)

            if isinstance(r, dict) and "customer" in r:
                inner = r["customer"]
                if isinstance(inner, dict) and "customer" in inner:
                    inner = inner["customer"]
                return self._normalize_customer(inner)
            else:
                return self._normalize_customer(r)
        except Exception as e:
            raise ApiError.from_error(e)

    def delete(self, customer_id: str) -> Dict[str, Any]:
        """
        Delete a customer

        Args:
            customer_id: Customer ID

        Returns:
            A response dictionary. Always contains an 'accepted' boolean key.
            If backend returns additional fields they are preserved.

        Raises:
            ApiError: If customer not found or API error occurs
        """
        try:
            raw = self.api.delete(customer_id)
            # Normalize to dict
            if isinstance(raw, dict):
                if "accepted" not in raw:
                    # Preserve other keys, ensure accepted present (default False)
                    raw["accepted"] = bool(raw.get("accepted", False))
                return raw
            elif isinstance(raw, bool):
                return {"accepted": raw}
            else:
                # Unexpected type – wrap in generic structure
                return {"accepted": False, "data": raw}
        except Exception as e:
            raise ApiError.from_error(e)

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


class CustomerClass:
    """Class-level access to Customer functionality and enums"""

    @property
    def KycStatus(self):
        try:
            from .models import KycStatus

            return KycStatus
        except ImportError:

            class MockKycStatus:
                APPROVED = "APPROVED"
                DENIED = "DENIED"
                IN_REVIEW = "IN_REVIEW"
                NOT_SUBMITTED = "NOT_SUBMITTED"

            return MockKycStatus

    @property
    def PaymentAuthorizationStatus(self):
        try:
            from .models import PaymentAuthorizationStatus

            return PaymentAuthorizationStatus
        except ImportError:

            class MockPaymentAuthorizationStatus:
                AUTHORIZED = "AUTHORIZED"
                NOT_AUTHORIZED = "NOT_AUTHORIZED"

            return MockPaymentAuthorizationStatus


Customer.KycStatus = CustomerClass().KycStatus
Customer.PaymentAuthorizationStatus = CustomerClass().PaymentAuthorizationStatus
