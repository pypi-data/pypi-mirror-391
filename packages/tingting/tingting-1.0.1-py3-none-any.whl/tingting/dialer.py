from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import TingTingClient
    
class Dialer:
    @classmethod
    def from_data(cls, client:"TingTingClient",data:dict) -> "Dialer":
        return Dialer(
            client = client,
            id = data.get("id"),
            phoneNumber = data.get("phone_number"),
        )

    def __init__(self,
        client:"TingTingClient",
        id: Optional[int] = None,
        phoneNumber: str = "",
    ):
        self._client = client
        self.id = id
        self.phoneNumber = phoneNumber
    
    def __str__(self) -> str:
        return f"{self.phoneNumber}"
    
    def json(self) -> dict:
        return {
            "id": self.id,
            "phone_number": self.phoneNumber,
        }