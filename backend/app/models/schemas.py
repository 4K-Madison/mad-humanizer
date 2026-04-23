from pydantic import BaseModel, Field


class HumanizeOptions(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=2048)
    enable_detector_gate: bool = True
    max_attempts: int | None = Field(default=None, ge=1, le=10)


class HumanizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    options: HumanizeOptions | None = None


class HumanizeAttempt(BaseModel):
    attempt: int
    humanized_text: str
    ai_score: float | None
    detector: str
    detector_error: str | None = None
    temperature_used: float


class HumanizeResponse(BaseModel):
    humanized_text: str
    input_length: int
    output_length: int
    processing_time_ms: int
    ai_score: float | None = None
    threshold_met: bool = False
    attempts: list[HumanizeAttempt] = []
    threshold: float | None = None
    warning: str | None = None


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    detectors: list[str] | None = None


class DetectorResult(BaseModel):
    detector: str
    score: float | None
    label: str | None
    details: dict | None
    error: str | None


class DetectResponse(BaseModel):
    results: list[DetectorResult]
    processing_time_ms: int


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database_connected: bool
    detectors_available: int


class DetectorInfo(BaseModel):
    name: str
    display_name: str
    available: bool
    description: str


class DetectorListResponse(BaseModel):
    detectors: list[DetectorInfo]
