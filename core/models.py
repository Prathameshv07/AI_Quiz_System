from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum
import json
import uuid
from datetime import datetime

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class KnowledgeArea(str, Enum):
    TRANSFORMERS = "transformers"
    GANS = "gans"
    PYTORCH = "pytorch"
    GENERATIVE_AI = "generative_ai"
    DEEP_LEARNING = "deep_learning"
    ML_BASICS = "ml_basics"

class Question(BaseModel):
    id: int
    question_text: str
    options: Dict[str, str]  # {"a": "option1", "b": "option2", ...}
    correct_answer: str
    knowledge_area: KnowledgeArea
    difficulty_level: DifficultyLevel
    explanation: Optional[str] = None
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        if 'options' in values and v not in values['options']:
            raise ValueError('correct_answer must be one of the option keys')
        return v

    def is_correct(self, answer: str) -> bool:
        return answer.lower() == self.correct_answer.lower()
    
    def to_dict(self) -> Dict:
        return self.dict()

class QuizSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    questions: List[Question]
    answers: Dict[int, str] = Field(default_factory=dict)
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    mode: str = "demo"  # "demo" or "full"
    
    def add_answer(self, question_id: int, answer: str):
        self.answers[question_id] = answer
    
    def get_progress(self) -> float:
        return len(self.answers) / len(self.questions) if self.questions else 0
    
    def complete_session(self):
        self.end_time = datetime.now().isoformat()

class QuizResult(BaseModel):
    session_id: str
    total_score: float
    area_scores: Dict[KnowledgeArea, float]
    knowledge_gaps: List[KnowledgeArea]
    performance_level: DifficultyLevel
    recommendations_needed: List[KnowledgeArea]
    total_questions: int
    correct_answers: int
    
    def get_percentage(self) -> float:
        return (self.total_score * 100) if self.total_score <= 1 else self.total_score

class Recommendation(BaseModel):
    area: KnowledgeArea
    priority: int = Field(ge=1, le=5)  # 1 = highest priority
    resources: List[str]
    estimated_time: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    personalized_advice: str
    
    def to_dict(self) -> Dict:
        return self.dict()

# Sample data generation for testing
def generate_sample_question() -> Question:
    return Question(
        id=1,
        question_text="What does tokenizer.encode() return?",
        options={"a": "Tokens", "b": "Token IDs", "c": "Strings", "d": "Vectors"},
        correct_answer="b",
        knowledge_area=KnowledgeArea.TRANSFORMERS,
        difficulty_level=DifficultyLevel.BEGINNER,
        explanation="tokenizer.encode() converts text into numerical token IDs that the model can process."
    )

def generate_sample_session() -> QuizSession:
    return QuizSession(
        user_id="test_user",
        questions=[generate_sample_question()],
        mode="demo"
    )

# JSON serialization helpers
def serialize_enum(obj):
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def model_to_json(model: BaseModel) -> str:
    return model.json(default=serialize_enum)

def json_to_model(json_str: str, model_class: type) -> BaseModel:
    return model_class.parse_raw(json_str)