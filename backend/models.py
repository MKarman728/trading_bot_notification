from pydantic import BaseModel


class User(BaseModel):
    email: str
    name: str
    image: str | None = None
    provider: str
    provider_id: str
