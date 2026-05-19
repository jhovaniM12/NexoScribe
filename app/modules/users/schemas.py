from pydantic import BaseModel, ConfigDict, Field


class UpdateMeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str | None = Field(default=None, min_length=2, max_length=100)
    image_url: str | None = Field(default=None, alias="imageUrl")

