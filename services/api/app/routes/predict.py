from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ml.pipeline import predict_message

router = APIRouter()


class PredictRequest(BaseModel):
    message: str


class PredictResponse(BaseModel):
    label: str
    confidence: float


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    """
    Predict if an SMS message is spam or ham.
    """
    try:
        label, confidence = predict_message(req.message)
        return PredictResponse(label=label, confidence=confidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
