from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class GetPost(PostBase):
    id: int

    class Config:
        from_attributes = True


class CreatePost(PostBase):
    pass


class UpdatePost(BaseModel):
    title: str | None = None
    content: str | None = None


class DeletePost(PostBase):
    pass
