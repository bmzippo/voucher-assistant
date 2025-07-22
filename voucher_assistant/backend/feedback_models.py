from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FeedbackType(str, Enum):
    SUMMARY_QUALITY = "summary_quality"
    ANSWER_ACCURACY = "answer_accuracy"
    UI_EXPERIENCE = "ui_experience"
    GENERAL = "general"

class Rating(int, Enum):
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5

class UserFeedback(BaseModel):
    """User feedback model"""
    feedback_type: FeedbackType
    rating: Rating
    comment: Optional[str] = None
    voucher_id: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    user_session_id: Optional[str] = None
    timestamp: datetime = datetime.now()

class FeedbackSummary(BaseModel):
    """Feedback summary model"""
    total_feedback: int
    average_rating: float
    rating_distribution: dict
    feedback_by_type: dict
    recent_comments: List[str]
    improvement_suggestions: List[str]
