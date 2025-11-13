"""models for api"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, model_validator

from zih_models.tkdb.types import PhoneNumberType

from .history_models.base import TABLE, BaseSchemaModel, ChangeAction

TelephoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+49-\d{1,3}-\d{0,8}-\d{1,12}$",
        examples=[
            "+49-351-463-40000",
            "+49-351-463-50000",
            "+49-351-463-60000",
        ],
    ),
]


class TelephoneNumberAssignment(BaseModel):
    """Base class of all Phone number assignment classes."""

    telephone_number: TelephoneNumber


class FunctionalPhoneNumber(TelephoneNumberAssignment):
    """FunctionalPhone with base information"""

    organizational_unit: str


class FunctionalPhoneNumberWithDetails(FunctionalPhoneNumber):
    """FunctionalPhone with all information for a detailed view"""

    manager_cn: str
    voicemail_user: list[str]
    comment: str | None = None
    category_id: int | None = None
    dod_id: int | None
    created: datetime
    last_modified: datetime
    unused_since: datetime | None


class FunctionalPhoneNumberWrite(FunctionalPhoneNumber):
    """FunctionalPhone with all optional write arguments"""

    voicemail_user: list[str] | None = None
    comment: str | None = None
    category_id: int | None = None
    dod_id: int


class PersonalPhoneNumber(TelephoneNumberAssignment):
    pass


class PersonalPhoneNumberWithDetails(PersonalPhoneNumber):
    user_cn: str
    comment: str | None = None
    dod_id: int | None
    voicemail: bool
    created: datetime
    last_modified: datetime
    unused_since: datetime | None


class PersonalPhoneNumberWrite(PersonalPhoneNumber):
    comment: str | None
    voicemail: bool = False
    dod_id: int


class ExternalPhoneNumberWithDetails(TelephoneNumberAssignment):
    organization_id: int
    dod_id: int | None
    comment: str | None = None
    created: datetime
    last_modified: datetime
    unused_since: datetime | None


class UserAssignmentsBase[
    TIpPhone: (str, PersonalPhoneNumberWrite, PersonalPhoneNumberWithDetails),
    TManagerOfPhone: (
        FunctionalPhoneNumberWrite,
        FunctionalPhoneNumber,
        FunctionalPhoneNumberWithDetails,
    ),
](BaseModel):
    """UserAssignments base class"""

    ipPhone: TIpPhone | None
    otherIpPhone: list[TIpPhone]
    managerOfPhone: list[TManagerOfPhone]


class UserAssignmentsWrite(
    UserAssignmentsBase[PersonalPhoneNumberWrite, FunctionalPhoneNumberWrite]
):
    """UserAssignments without common_name to write to api and more validation"""

    @model_validator(mode="after")
    def validate_primary(self) -> Self:
        """validate that ipPhone is required if you want to set otherIpPhones"""
        if self.otherIpPhone and self.ipPhone is None:
            raise ValueError(
                "ipPhone is required if you want to set otherIpPhones"
            )
        return self

    @model_validator(mode="after")
    def check_unique_telephone_number_across_attributes(self) -> Self:
        """validate that ipPhone, otherIpPhones and managerOfPhone dont have duplicated telephone_numbers"""
        personal_numbers: list[
            PersonalPhoneNumberWrite | FunctionalPhoneNumberWrite
        ] = ([self.ipPhone, *self.otherIpPhone] if self.ipPhone else [])
        all_numbers = [
            item.telephone_number
            for item in personal_numbers + self.managerOfPhone
        ]
        if len(all_numbers) != len(set(all_numbers)):
            raise ValueError(
                "Telephone numbers must be unique across ipPhone, otherIpPhones and managerOfPhone."
            )
        return self


class UserAssignments(UserAssignmentsBase[str, FunctionalPhoneNumber]):
    """UserAssignments return for api"""

    common_name: str

    @property
    def telephone_numbers(self) -> list[str]:
        """return all telephone numbers of user. (no numbers where the user is manager)"""
        return (
            [
                self.ipPhone,
                *self.otherIpPhone,
            ]
            if self.ipPhone is not None
            else self.otherIpPhone
        )


class UserAssignmentsWithDetails(
    UserAssignmentsBase[
        PersonalPhoneNumberWithDetails, FunctionalPhoneNumberWithDetails
    ]
):
    """UserAssignments return for api"""

    common_name: str


class HistoryEntry[
    T: (dict[str, Any], BaseSchemaModel) = dict[str, Any],
    TAction: ChangeAction = ChangeAction,
](BaseModel):

    subject: str | None
    source: str
    timestamp: datetime
    entity_type: TABLE
    entity_identifier: str
    action: TAction
    data: T


class NewPrimaryBody(BaseModel):

    telephone_number: TelephoneNumber


class LegacyTKDBLink(BaseModel):
    """Object relation for an object that is currently not on the ssp display and is a link to old tkdb"""

    link: str
    display: str


class GatewayPort(BaseModel):
    gateway: LegacyTKDBLink
    port: int
    room: Annotated[
        str,
        Field(
            pattern=r"^TU-[A-Z]{2}-\d{3}-\d{4}-\d{2}-\d{4}$",
            examples=[
                "TU-DD-145-1231-00-5830",
            ],
        ),
    ]
    comment: str
    extra_comment: str


class IsdnCable(BaseModel):
    name: LegacyTKDBLink
    comment: str
    extra_comment: str


class VoipPhone(BaseModel):
    device: LegacyTKDBLink
    line: int


class PhoneNumberDetails(BaseModel):

    id: int
    number: str
    prefix: str
    dial_up: str
    extension: str
    type: PhoneNumberType
    use_id: int | None
    comment: str | None
    assignment: str | None
    partition: str | None
    isdn_system: int | None
    isdn_port: str | None

    # combined values
    # is set on personal and function numbers / also used for type legacy
    voicemail_users: list[str] | None = None

    # If the number has any active usage, this is False. Is None for blocked numbers.
    unused: bool | None = None

    # external number values / also used for type legacy
    external_organization_id: int | None = None

    # functional number values / also used for type legacy
    organization_unit: str | None = None
    manager: str | None = None
    functional_category: int | None = None

    # personal number values
    # for better implementation this None on all legacy numbers, even if they have an personal relation
    user: str | None = None

    functional_details: FunctionalPhoneNumberWithDetails | None = None
    personal_details: list[PersonalPhoneNumberWithDetails] | None = None
    external_details: ExternalPhoneNumberWithDetails | None = None

    gateway_ports: list[GatewayPort] | None = None
    isdn_cables: list[IsdnCable] | None = None
    voip_phones: list[VoipPhone] | None = None


class PhoneNumbersResponse(BaseModel):

    items: list[PhoneNumberDetails]
    total: int


class AllowedTelephoneFilterFields(StrEnum):

    ID = "id"
    NUMBER = "number"
    PREFIX = "prefix"
    DIAL_UP = "dial_up"
    EXTENSION = "extension"
    TYPE = "type"
    USE_ID = "use_id"
    COMMENT = "comment"
    ASSIGNMENT = "assignment"
    PARTITION = "partition"
    ISDN_SYSTEM = "isdn_system"
    ISDN_PORT = "isdn_port"
    VOICEMAIL_USERS = "voicemail_users"
    UNUSED = "unused"
    EXTERNAL_ORGANIZATION_ID = "external_organization_id"
    ORGANIZATION_UNIT = "organization_unit"
    MANAGER = "manager"
    FUNCTIONAL_CATEGORY = "functional_category"
    USER = "user"


class StatsResponse(BaseModel):

    # used states of automatic number ranges
    free_in_number_ranges: int
    used_in_number_ranges: int

    # type counts
    personal_numbers: int
    blocked_numbers: int
    external_numbers: int
    functional_numbers: int
    legacy_numbers: int

    # legacy count splitted in legacy reasons
    legacy_reasons: dict[str, int]

    # use categories
    isdn_numbers: int
    voip_numbers: int
