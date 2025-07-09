from pydantic import BaseModel


class PortfolioSchema(BaseModel):
    name: str
