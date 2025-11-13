from pydantic import BaseModel, Field


class WorkplaceUser(BaseModel):
    name: str | None = Field(default=None, description="Name of the user")
    status: str = Field(description="Status of the user")
    email_address: str = Field(description="Email address of the user")
    phone_number: str | None = Field(
        default=None, description="Phone number of the user"
    )
    is_admin: bool = Field(description="Whether the user is an admin")
    can_create_apps: bool = Field(description="Whether the user can create apps")
    role: str = Field(description="Role of the user")
