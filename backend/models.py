from typing import Optional, Literal
from pydantic import BaseModel


class Athlete(BaseModel):
	id: Optional[int] = None
	name: str
	email: str
	password_hash: str
	created_at: Optional[str] = None


class AthleteCreate(BaseModel):
	name: str
	email: str
	password: str


class AthleteLogin(BaseModel):
	email: str
	password: str


class Result(BaseModel):
	id: Optional[int] = None
	athlete_id: int
	test_type: Literal["situps", "jump"]
	metrics_json: str
	video_path: Optional[str] = None
	status: Literal["pending", "accepted", "rejected"] = "pending"
	created_at: Optional[str] = None


class AdminDecision(BaseModel):
	result_id: int
	action: Literal["accept", "reject"]
