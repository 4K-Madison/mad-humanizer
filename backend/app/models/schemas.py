from pydantic import BaseModel, Field


class HumanizeOptions(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=4096)


class HumanizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    options: HumanizeOptions | None = None


class HumanizeResponse(BaseModel):
    humanized_text: str
    input_length: int
    output_length: int
    processing_time_ms: int


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
