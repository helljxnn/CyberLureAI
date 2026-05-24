import csv
import logging
import os
from datetime import datetime
from pathlib import Path

from backend.app.schemas.feedback import FeedbackRequest

logger = logging.getLogger(__name__)

# Absolute path to data/feedback directory
FEEDBACK_DIR = Path(__file__).resolve().parents[3] / "data" / "feedback"
FEEDBACK_FILE = FEEDBACK_DIR / "user_feedback.csv"

def save_feedback(feedback: FeedbackRequest) -> None:
    """Guarda la retroalimentación del usuario en un archivo CSV local."""
    try:
        if not FEEDBACK_DIR.exists():
            FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
            
        file_exists = FEEDBACK_FILE.exists()
        
        with open(FEEDBACK_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "sample_type", "input_data", "verdict_given", "user_feedback", "comments"])
                
            writer.writerow([
                datetime.utcnow().isoformat(),
                feedback.sample_type,
                feedback.input_data,
                feedback.verdict_given,
                feedback.user_feedback,
                feedback.comments or ""
            ])
            
        logger.info(f"Feedback guardado correctamente para {feedback.sample_type}.")
    except Exception as e:
        logger.error(f"Error al guardar feedback: {e}")
        raise
