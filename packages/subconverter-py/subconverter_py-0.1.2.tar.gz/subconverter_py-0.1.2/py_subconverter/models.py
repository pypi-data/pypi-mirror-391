from pydantic import BaseModel, Field
from typing import List, Optional, Union


# --- Login Models ---
class LoginData(BaseModel):
    token: str
    token_expire: str


class LoginResponse(BaseModel):
    ret: int
    msg: str
    data: LoginData


# --- Account Models ---
class UserInformationData(BaseModel):
    plan: str
    plan_time: str
    money: str
    aff_money: str
    today_used: str
    used: str
    unused: str
    traffic: str
    integral: str  # The API returns '49 / 50' which is a string


class UserInformationResponse(BaseModel):
    ret: int
    msg: str
    data: UserInformationData


# --- Managed Models ---
class ManagedClashData(BaseModel):
    name: str
    smart: str
    ss: Optional[str] = None
    vmess: str
    trojan: Optional[str] = None
    ss2022: str


class ManagedClashResponse(BaseModel):
    ret: int
    msg: str
    data: ManagedClashData = Field(alias='name')  # The data is not in a 'data' field
    smart: str
    ss: str
    vmess: str
    trojan: str
    ss2022: str


# --- Nodes Models ---
class Node(BaseModel):
    node_id: int
    node_name: str
    node_host: str
    source_port: int


class NodeListResponse(BaseModel):
    ret: int
    msg: str
    data: List[Node]
