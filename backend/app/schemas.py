from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    name: str = Field(default="", max_length=120)
class JobInput(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    company: str = Field(min_length=1, max_length=180)
    location: str = Field(default="Remote", max_length=180)
    description: str = Field(min_length=30, max_length=30000)
class ResumeEdit(BaseModel):
    parsed: dict
class ApplicationInput(BaseModel):
    job_id: int
    status: str = Field(default="Applied", pattern="^(Interested|Applied|Interview|Offer|Rejected)$")
    notes: str = Field(default="", max_length=3000)
class UserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str
