import enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# OS-agnostic "never expires" timestamp (January 1, 2100 00:00:00 UTC)
# This is well within the safe range for all systems (32-bit timestamp limit is 2038)
NEVER_EXPIRES_TIMESTAMP = 4102444800


# ===============================
# Enums
# ===============================
class UserActionType(str, enum.Enum):
    CLICK = "click"
    SCROLL = "scroll"
    TYPE = "type"
    NONE = "none"


class ProfileTimeToLive(str, enum.Enum):
    ONE_DAY = "one_day"
    ONE_WEEK = "one_week"
    ONE_MONTH = "one_month"
    ONE_QUARTER = "one_quarter"
    ONE_YEAR = "one_year"
    INFINITY = "infinity"


class FeedbackStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ===============================
# Data Models
# ===============================
# information about the user interaction sent by the client
class Interaction(BaseModel):
    interaction_id: str
    user_id: str
    request_id: str
    created_at: int = int(datetime.utcnow().timestamp())
    role: str = "User"
    content: str = ""
    user_action: UserActionType = UserActionType.NONE
    user_action_description: str = ""
    interacted_image_url: str = ""
    image_encoding: str = ""  # base64 encoded image
    embedding: list[float] = []


class Request(BaseModel):
    request_id: str
    user_id: str
    created_at: int = int(datetime.utcnow().timestamp())
    source: str = ""
    agent_version: str = ""
    is_shadow_request: bool = False
    request_group: str = ""


# information about the user profile generated from the user interaction
# output of the profile generation service send back to the client
class UserProfile(BaseModel):
    profile_id: str
    user_id: str
    profile_content: str
    last_modified_timestamp: int
    generated_from_request_id: str
    profile_time_to_live: ProfileTimeToLive = ProfileTimeToLive.INFINITY
    # this is the expiration date calculated based on last modified timestamp and profile time to live instead of generated timestamp
    expiration_timestamp: int = NEVER_EXPIRES_TIMESTAMP
    custom_features: Optional[dict] = None
    source: Optional[str] = None
    embedding: list[float] = []


# raw feedback for agents
class RawFeedback(BaseModel):
    raw_feedback_id: int = 0
    agent_version: str
    request_id: str
    feedback_name: str = ""
    created_at: int = int(datetime.utcnow().timestamp())
    feedback_content: str = ""
    embedding: list[float] = []


class ProfileChangeLog(BaseModel):
    id: int
    user_id: str
    request_id: str
    created_at: int = int(datetime.utcnow().timestamp())
    added_profiles: list[UserProfile]
    removed_profiles: list[UserProfile]
    mentioned_profiles: list[UserProfile]


class Feedback(BaseModel):
    feedback_id: int = 0
    feedback_name: str = ""
    agent_version: str
    created_at: int = int(datetime.utcnow().timestamp())
    feedback_content: str
    feedback_status: FeedbackStatus
    feedback_metadata: str
    embedding: list[float] = []
    status: Optional[
        str
    ] = None  # used for tracking intermediate states during feedback aggregation


class AgentSuccessEvaluationResult(BaseModel):
    result_id: int = 0
    agent_version: str
    request_id: str
    is_success: bool
    failure_type: str
    failure_reason: str
    agent_prompt_update: str
    created_at: int = int(datetime.utcnow().timestamp())
    embedding: list[float] = []


# ===============================
# Request Models
# ===============================


# delete user profile request
class DeleteUserProfileRequest(BaseModel):
    user_id: str
    profile_id: str = ""
    search_query: str = ""


# delete user profile response
class DeleteUserProfileResponse(BaseModel):
    success: bool
    message: str = ""


# delete user interaction request
class DeleteUserInteractionRequest(BaseModel):
    user_id: str
    interaction_id: str


# delete user interaction response
class DeleteUserInteractionResponse(BaseModel):
    success: bool
    message: str = ""


# user provided interaction data from the request
class InteractionData(BaseModel):
    created_at: int = int(datetime.utcnow().timestamp())
    role: str = "User"
    content: str = ""
    user_action: UserActionType = UserActionType.NONE
    user_action_description: str = ""
    interacted_image_url: str = ""
    image_encoding: str = ""  # base64 encoded image


# publish user interaction request
class PublishUserInteractionRequest(BaseModel):
    user_id: str
    interaction_data_list: list[InteractionData]
    source: str = ""
    agent_version: str = (
        ""  # this is used for aggregating interactions for generating agent feedback
    )
    request_group: str = "" # used for grouping shadow requests together
    is_shadow_request: bool = False # if true, the request is a shadow request


# publish user interaction response
class PublishUserInteractionResponse(BaseModel):
    success: bool
    message: str = ""


class ProfileChangeLogResponse(BaseModel):
    success: bool
    profile_change_logs: list[ProfileChangeLog]


class RegenerateFeedbacksRequest(BaseModel):
    agent_version: str
    feedback_name: str


class RegenerateFeedbacksResponse(BaseModel):
    success: bool
    message: str = ""
