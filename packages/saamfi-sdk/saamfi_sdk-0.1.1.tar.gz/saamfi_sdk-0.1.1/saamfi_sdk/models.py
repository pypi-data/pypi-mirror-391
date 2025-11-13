"""
Data models for the Saamfi SDK.

This module defines the data classes used for communication with the Saamfi service.
All models use Pydantic for data validation.
"""

from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class LoginBody(BaseModel):
    """
    DTO for login requests.

    Equivalent to: LoginBody.java
    """

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True, extra="forbid")

    username: str = Field(..., description="Username")
    password: str = Field(..., description="User password")
    system_id: int = Field(
        ...,
        description="System/tenant ID",
        serialization_alias="sysid",
    )


class LoginResponse(BaseModel):
    """
    DTO for successful authentication response.

    Equivalent to: LoginResponse.java
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    name: str = Field(..., description="First name")
    lastname: str = Field(..., description="Last name")
    document_id: str = Field(
        ...,
        description="Document ID or ID card",
        validation_alias=AliasChoices("documentId", "document_id"),
        serialization_alias="documentId",
    )
    token: str = Field(
        ...,
        description="JWT access token",
        validation_alias=AliasChoices("accessToken", "token"),
        serialization_alias="accessToken",
    )
    token_type: str = Field(
        ...,
        description="Token type (e.g., Bearer)",
        validation_alias=AliasChoices("tokenType", "token_type"),
        serialization_alias="tokenType",
    )
    system_home_page: str = Field(
        ...,
        description="System home page URL",
        validation_alias=AliasChoices("systemHomePage", "system_home_page"),
        serialization_alias="systemHomePage",
    )

    @property
    def access_token(self) -> str:
        """Backwards compatibility with previous attribute name."""
        return self.token


class UserInfo(BaseModel):
    """
    DTO for detailed user information.

    Equivalent to: UserInfo.java
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: str = Field(..., description="Email address")
    document_id: str = Field(
        ...,
        description="Document ID or ID card",
        validation_alias=AliasChoices("documentId", "document_id"),
        serialization_alias="documentId",
    )
    username: str = Field(..., description="Username")
    name: str = Field(..., description="First name")
    lastname: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    password: Optional[str] = Field(None, description="Password (usually not returned)")
    institution: Optional[int] = Field(None, description="Institution ID")
    institution_name: Optional[str] = Field(
        None,
        description="Institution name",
        validation_alias=AliasChoices("institutionName", "institution_name"),
        serialization_alias="institutionName",
    )
    system: Optional[int] = Field(None, description="System ID")
    is_active: Optional[str] = Field(
        None,
        description="User active status",
        validation_alias=AliasChoices("isActive", "is_active"),
        serialization_alias="isActive",
    )


class UserDetailToken(BaseModel):
    """
    User information extracted from JWT token.

    Equivalent to: UserDetailToken.java (Spring Security UserDetails implementation)

    In Python we don't need to implement an interface like UserDetails,
    but we maintain the same data structure.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    username: str = Field(..., description="Username")
    system: int = Field(..., description="System ID")
    pers_id: str = Field(
        ...,
        description="Person ID",
        validation_alias=AliasChoices("persId", "pers_id"),
        serialization_alias="persId",
    )
    roles: List[str] = Field(default_factory=list, description="User roles and permissions")

    def __str__(self) -> str:
        """String representation of the object, equivalent to Java's toString()."""
        return (
            f"UserDetailToken [persId={self.pers_id}, roles={self.roles}, "
            f"system={self.system}, username={self.username}]"
        )
