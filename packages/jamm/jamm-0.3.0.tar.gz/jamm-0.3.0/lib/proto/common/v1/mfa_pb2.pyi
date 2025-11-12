from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InitiateErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INITIATE_ERROR_TYPE_UNSPECIFIED: _ClassVar[InitiateErrorType]
    INITIATE_ERROR_TYPE_RATE_LIMITED: _ClassVar[InitiateErrorType]
    INITIATE_ERROR_TYPE_INVALID_PHONE: _ClassVar[InitiateErrorType]
    INITIATE_ERROR_TYPE_SERVICE_UNAVAILABLE: _ClassVar[InitiateErrorType]
    INITIATE_ERROR_TYPE_INVALID_SESSION: _ClassVar[InitiateErrorType]
    INITIATE_ERROR_TYPE_ALREADY_VERIFIED: _ClassVar[InitiateErrorType]

class ResendErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESEND_ERROR_TYPE_UNSPECIFIED: _ClassVar[ResendErrorType]
    RESEND_ERROR_TYPE_TOO_SOON: _ClassVar[ResendErrorType]
    RESEND_ERROR_TYPE_INVALID_SESSION: _ClassVar[ResendErrorType]
    RESEND_ERROR_TYPE_MAX_ATTEMPTS: _ClassVar[ResendErrorType]
    RESEND_ERROR_TYPE_NO_PENDING_VERIFICATION: _ClassVar[ResendErrorType]
    RESEND_ERROR_TYPE_SERVICE_UNAVAILABLE: _ClassVar[ResendErrorType]

class VerifyErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VERIFY_ERROR_TYPE_UNSPECIFIED: _ClassVar[VerifyErrorType]
    VERIFY_ERROR_TYPE_INVALID_OTP: _ClassVar[VerifyErrorType]
    VERIFY_ERROR_TYPE_EXPIRED: _ClassVar[VerifyErrorType]
    VERIFY_ERROR_TYPE_MAX_ATTEMPTS: _ClassVar[VerifyErrorType]
    VERIFY_ERROR_TYPE_INVALID_SESSION: _ClassVar[VerifyErrorType]
    VERIFY_ERROR_TYPE_NO_PENDING_VERIFICATION: _ClassVar[VerifyErrorType]
INITIATE_ERROR_TYPE_UNSPECIFIED: InitiateErrorType
INITIATE_ERROR_TYPE_RATE_LIMITED: InitiateErrorType
INITIATE_ERROR_TYPE_INVALID_PHONE: InitiateErrorType
INITIATE_ERROR_TYPE_SERVICE_UNAVAILABLE: InitiateErrorType
INITIATE_ERROR_TYPE_INVALID_SESSION: InitiateErrorType
INITIATE_ERROR_TYPE_ALREADY_VERIFIED: InitiateErrorType
RESEND_ERROR_TYPE_UNSPECIFIED: ResendErrorType
RESEND_ERROR_TYPE_TOO_SOON: ResendErrorType
RESEND_ERROR_TYPE_INVALID_SESSION: ResendErrorType
RESEND_ERROR_TYPE_MAX_ATTEMPTS: ResendErrorType
RESEND_ERROR_TYPE_NO_PENDING_VERIFICATION: ResendErrorType
RESEND_ERROR_TYPE_SERVICE_UNAVAILABLE: ResendErrorType
VERIFY_ERROR_TYPE_UNSPECIFIED: VerifyErrorType
VERIFY_ERROR_TYPE_INVALID_OTP: VerifyErrorType
VERIFY_ERROR_TYPE_EXPIRED: VerifyErrorType
VERIFY_ERROR_TYPE_MAX_ATTEMPTS: VerifyErrorType
VERIFY_ERROR_TYPE_INVALID_SESSION: VerifyErrorType
VERIFY_ERROR_TYPE_NO_PENDING_VERIFICATION: VerifyErrorType

class InitiateSmsVerificationRequest(_message.Message):
    __slots__ = ("phone_number",)
    PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    phone_number: str
    def __init__(self, phone_number: _Optional[str] = ...) -> None: ...

class InitiateSmsVerificationResponse(_message.Message):
    __slots__ = ("expires_in_seconds", "resend_delay_seconds", "error_type", "error_message", "retry_after_seconds")
    EXPIRES_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    RESEND_DELAY_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RETRY_AFTER_SECONDS_FIELD_NUMBER: _ClassVar[int]
    expires_in_seconds: int
    resend_delay_seconds: int
    error_type: InitiateErrorType
    error_message: str
    retry_after_seconds: int
    def __init__(self, expires_in_seconds: _Optional[int] = ..., resend_delay_seconds: _Optional[int] = ..., error_type: _Optional[_Union[InitiateErrorType, str]] = ..., error_message: _Optional[str] = ..., retry_after_seconds: _Optional[int] = ...) -> None: ...

class ResendSmsVerificationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ResendSmsVerificationResponse(_message.Message):
    __slots__ = ("expires_in_seconds", "resend_delay_seconds", "error_type", "error_message", "retry_after_seconds")
    EXPIRES_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    RESEND_DELAY_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RETRY_AFTER_SECONDS_FIELD_NUMBER: _ClassVar[int]
    expires_in_seconds: int
    resend_delay_seconds: int
    error_type: ResendErrorType
    error_message: str
    retry_after_seconds: int
    def __init__(self, expires_in_seconds: _Optional[int] = ..., resend_delay_seconds: _Optional[int] = ..., error_type: _Optional[_Union[ResendErrorType, str]] = ..., error_message: _Optional[str] = ..., retry_after_seconds: _Optional[int] = ...) -> None: ...

class VerifySmsOtpRequest(_message.Message):
    __slots__ = ("otp",)
    OTP_FIELD_NUMBER: _ClassVar[int]
    otp: str
    def __init__(self, otp: _Optional[str] = ...) -> None: ...

class VerifySmsOtpResponse(_message.Message):
    __slots__ = ("verified", "error_type", "error_message", "attempts_remaining")
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_REMAINING_FIELD_NUMBER: _ClassVar[int]
    verified: bool
    error_type: VerifyErrorType
    error_message: str
    attempts_remaining: int
    def __init__(self, verified: bool = ..., error_type: _Optional[_Union[VerifyErrorType, str]] = ..., error_message: _Optional[str] = ..., attempts_remaining: _Optional[int] = ...) -> None: ...
