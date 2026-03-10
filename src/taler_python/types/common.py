from enum import StrEnum
from typing import Literal, Union, TypeAlias, Dict, List, Optional
from pydantic import BaseModel

class TanChannel (StrEnum):
    SMS = "sms"
    EMAIL = "email"

class RelativeTime (BaseModel):
    d_us: Union[int, Literal["forever"]]

class RoundingInterval (StrEnum):
    NONE = "NONE"
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"

EddsaPublicKey: TypeAlias = str


class ExchangeConfigInfo (BaseModel):
    base_url: str
    currency: str
    master_pub: EddsaPublicKey

class CurrencySpecification (BaseModel):
    name: str
    currency: str
    num_fractional_input_digits: int
    num_fractional_normal_digits: int
    num_fractional_trailing_zero_digits: int
    alt_unit_names: Dict[str, str]
    common_amounts: List[str]

class MerchantVersionResponse (BaseModel):
    version: str
    name: Literal["taler-merchant"]
    implementation: Optional[str] = None
    currency: str
    default_persona: str
    currencies: Dict[str, CurrencySpecification]
    # report_generators: Dict[str, str]
    report_generators: Optional[Dict[str, str]] = None
    phone_regex: Optional[str] = None
    exchanges: List[ExchangeConfigInfo] 
    have_self_provisioning: bool
    have_donau: bool
    mandatory_tan_channels: Optional[List[TanChannel]] = None
    payment_target_types: str
    payment_target_regex: Optional[str] = None
    # default_pay_delay: RelativeTime
    # default_refund_delay: RelativeTime
    # default_wire_transfer_delay: RelativeTime
    # default_wire_transfer_rounding_interval: RoundingInterval
    default_pay_delay: Optional[RelativeTime] = None
    default_refund_delay: Optional[RelativeTime] = None
    default_wire_transfer_delay: Optional[RelativeTime] = None
    default_wire_transfer_rounding_interval: Optional[RoundingInterval] = None