from enum import Enum
from itertools import chain


class ModelClass(str, Enum):
    ALIGN = "align"
    ALIGN_LIGHTNING = "align-lightning"


class ModelCore(str, Enum):
    ALIGN_20250529 = "align-20250529"
    ALIGN_LIGHTNING_20250731 = "align-lightning-20250731"

    def model_class(self) -> ModelClass:
        class_name = self.value.rsplit("-", 1)[0]
        return ModelClass(class_name)


class EvaluationTarget(Enum):
    LATEST_RESPONSE = "latest"
    ALL_RESPONSES = "all"


class ScoreType(str, Enum):
    REWARD = "reward"
    BINARY = "binary"


criteria_starts = {
    "reward": [
        "Reward",
        "Penalize",
    ],
    "binary": [
        "Passes if",
        "Fails if",
    ],
}

eval_response_error_codes = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the bad request error",
                        }
                    },
                }
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the unauthorized error",
                        }
                    },
                }
            }
        },
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the internal server error",
                        }
                    },
                }
            }
        },
    },
    429: {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the rate limiting error",
                        }
                    },
                }
            }
        },
    },
    524: {
        "description": "Request Timeout",
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "detail": {
                            "type": "string",
                            "description": "Details about the gateway timeout error",
                        }
                    },
                }
            }
        },
    },
}


class InternalServerError(Exception):
    pass


class OverloadedError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class BadRequestError(Exception):
    pass
