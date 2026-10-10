from pydantic import BaseModel


class GenerationRequest(BaseModel):
    text: str
    voice_model_id: str
    output_format: str = "mp3"


class GenerationResult(BaseModel):
    job_id: str
    status: str
    output_path: str | None = None


def create_generation_request(text: str, voice_model_id: str) -> GenerationRequest:
    return GenerationRequest(text=text, voice_model_id=voice_model_id)
