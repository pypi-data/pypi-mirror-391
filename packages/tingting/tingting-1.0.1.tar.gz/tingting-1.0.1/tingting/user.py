from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import TingTingClient


class User:
    @classmethod
    def from_data(cls, client:"TingTingClient",data:dict) -> "User":
        return User(
            client = client,
            id = data.get("id"),
            firstName = data.get("user",{}).get("first_name"),
            lastName = data.get("user",{}).get("last_name"),
            username = data.get("user",{}).get("username"),
            email = data.get("user",{}).get("email"),
            profilePicture = data.get("profile_picture"),
            contactNo = data.get("contact_no"),
            address = data.get("address"),
            isVerifiedContact = data.get("is_verified_contact"),
        )

    def __init__(self,
        client:"TingTingClient",
        id:Optional[int] = None,
        firstName: str = "",
        lastName: str = "",
        username: str = "",
        email: str = "",
        profilePicture: str = "",
        contactNo: str = "",
        address: str = "",
        isVerifiedContact: bool = False,
    ):
        self._client = client
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.username = username
        self.email = email
        self.profilePicture = profilePicture
        self.contactNo = contactNo
        self.address = address
        self.isVerifiedContact = isVerifiedContact
    
    def __str__(self):
        return f"{self.username}"
    
    def json(self):
        return {
            "id": self.id,
            "first_name": self.firstName,
            "last_name": self.lastName,
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profilePicture,
            "contact_no": self.contactNo,
            "address": self.address,
            "is_verified_contact": self.isVerifiedContact,
        }
        