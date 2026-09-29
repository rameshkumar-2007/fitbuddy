from typing import Literal
from pydantic import BaseModel, Field, field_validator
Goal=Literal["weight loss","muscle gain","general wellness","flexibility"]
Intensity=Literal["low","medium","high"]

class UserInput(BaseModel):
    name:str=Field(min_length=2,max_length=100)
    user_id:str=Field(min_length=1,max_length=64)
    age:int=Field(ge=13,le=100)
    weight:float=Field(gt=20,lt=500)
    goal:Goal
    intensity:Intensity
    @field_validator("name","user_id")
    @classmethod
    def strip_text(cls,v):
        v=v.strip()
        if not v: raise ValueError("Value cannot be empty")
        return v

class FeedbackRequest(BaseModel):
    user_id:str=Field(min_length=1,max_length=64)
    feedback:str=Field(min_length=3,max_length=2000)
