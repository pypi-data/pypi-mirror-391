"""Dataclasses that mirror the ChatAds FastAPI request/response models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

FUNCTION_ITEM_OPTIONAL_FIELDS = (
    "page_url",
    "page_title",
    "referrer",
    "address",
    "email",
    "type",
    "domain",
    "user_agent",
    "ip",
    "reason",
    "company",
    "name",
    "country",
    "language",
    "website",
)

_CAMELCASE_ALIASES = {
    "pageurl": "page_url",
    "pagetitle": "page_title",
    "useragent": "user_agent",
}

FUNCTION_ITEM_FIELD_ALIASES = {
    **{field: field for field in FUNCTION_ITEM_OPTIONAL_FIELDS},
    **_CAMELCASE_ALIASES,
}

_FIELD_TO_PAYLOAD_KEY = {
    "page_url": "pageUrl",
    "page_title": "pageTitle",
    "referrer": "referrer",
    "address": "address",
    "email": "email",
    "type": "type",
    "domain": "domain",
    "user_agent": "userAgent",
    "ip": "ip",
    "reason": "reason",
    "company": "company",
    "name": "name",
    "country": "country",
    "language": "language",
    "website": "website",
}

RESERVED_PAYLOAD_KEYS = frozenset({"message", *(_FIELD_TO_PAYLOAD_KEY.values())})


@dataclass
class ChatAdsAd:
    product: str
    link: str
    message: str
    category: str

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsAd"]:
        if not data:
            return None
        return cls(
            product=data.get("product", ""),
            link=data.get("link", ""),
            message=data.get("message", ""),
            category=data.get("category", ""),
        )


@dataclass
class ChatAdsData:
    matched: bool
    ad: Optional[ChatAdsAd] = None
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsData"]:
        if not data:
            return None
        return cls(
            matched=bool(data.get("matched", False)),
            ad=ChatAdsAd.from_dict(data.get("ad")),
            reason=data.get("reason"),
        )


@dataclass
class ChatAdsError:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ChatAdsError"]:
        if not data:
            return None
        return cls(
            code=data.get("code", "UNKNOWN"),
            message=data.get("message", ""),
            details=data.get("details") or {},
        )


@dataclass
class UsageInfo:
    monthly_requests: int
    free_tier_limit: int
    free_tier_remaining: int
    is_free_tier: bool
    has_credit_card: bool
    daily_requests: Optional[int] = None
    daily_limit: Optional[int] = None
    minute_requests: Optional[int] = None
    minute_limit: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["UsageInfo"]:
        if not data:
            return None
        return cls(
            monthly_requests=int(data.get("monthly_requests") or 0),
            free_tier_limit=int(data.get("free_tier_limit") or 0),
            free_tier_remaining=int(data.get("free_tier_remaining") or 0),
            is_free_tier=bool(data.get("is_free_tier", False)),
            has_credit_card=bool(data.get("has_credit_card", False)),
            daily_requests=_maybe_int(data.get("daily_requests")),
            daily_limit=_maybe_int(data.get("daily_limit")),
            minute_requests=_maybe_int(data.get("minute_requests")),
            minute_limit=_maybe_int(data.get("minute_limit")),
        )


@dataclass
class ChatAdsMeta:
    request_id: str
    user_id: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    processing_time_ms: Optional[float] = None
    usage: Optional[UsageInfo] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ChatAdsMeta":
        data = data or {}
        return cls(
            request_id=data.get("request_id", ""),
            user_id=data.get("user_id"),
            country=data.get("country"),
            language=data.get("language"),
            processing_time_ms=data.get("processing_time_ms"),
            usage=UsageInfo.from_dict(data.get("usage")),
            raw=data,
        )


@dataclass
class ChatAdsResponse:
    success: bool
    meta: ChatAdsMeta
    data: Optional[ChatAdsData] = None
    error: Optional[ChatAdsError] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatAdsResponse":
        data = data or {}
        return cls(
            success=bool(data.get("success", False)),
            data=ChatAdsData.from_dict(data.get("data")),
            error=ChatAdsError.from_dict(data.get("error")),
            meta=ChatAdsMeta.from_dict(data.get("meta")),
            raw=data,
        )


@dataclass
class FunctionItemPayload:
    """Subset of the server's FunctionItem pydantic model."""

    message: str
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    referrer: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    domain: Optional[str] = None
    user_agent: Optional[str] = None
    ip: Optional[str] = None
    reason: Optional[str] = None
    company: Optional[str] = None
    name: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    website: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        payload = {"message": self.message}
        for field_name, payload_key in _FIELD_TO_PAYLOAD_KEY.items():
            value = getattr(self, field_name)
            if value is not None:
                payload[payload_key] = value

        conflicts = RESERVED_PAYLOAD_KEYS.intersection(self.extra_fields.keys())
        if conflicts:
            conflict_list = ", ".join(sorted(conflicts))
            raise ValueError(
                f"extra_fields contains reserved keys that would override core payload data: {conflict_list}"
            )
        payload.update(self.extra_fields)
        return payload


def _maybe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
