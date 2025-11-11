from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .client import TingTingClient
    
class Voice:
    @classmethod
    def from_data(cls, client:"TingTingClient",data:dict) -> "Voice":
        return Voice(
            client = client,
            id = data.get("id"),
            displayName = data.get("voice_display_name"),
            internalName = data.get("voice_internal_name"),
            isPremium = data.get("is_premium"),
        )

    def __init__(self,
        client:"TingTingClient",
        id: Optional[int] = None,
        displayName: str = "",
        internalName: str = "",
        isPremium: bool = False,
    ):
        self._client = client
        self.id = id
        self.displayName = displayName
        self.internalName = internalName
        self.isPremium = isPremium
    
    def __str__(self) -> str:
        return f"{self.displayName}"
    
    def json(self) -> dict:
        return {
            "id": self.id,
            "voice_display_name": self.displayName,
            "voice_internal_name": self.internalName,
            "is_premium": self.isPremium,
        }