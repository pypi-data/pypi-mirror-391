from typing import Optional
from pydantic import BaseModel, Field


class ScoreResponse(BaseModel):
    """
    Response model for evaluation scores.
    """

    score: Optional[float] = Field(
        None,
        description="Evaluation score between 0 and 1. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")
