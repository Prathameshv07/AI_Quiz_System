import json
import random
import numpy as np
from functools import lru_cache
from typing import List, Dict, Optional
from collections import defaultdict, Counter
# from .models import Question, QuizSession, QuizResult, KnowledgeArea, DifficultyLevel
from core.models import Question, QuizSession, QuizResult, KnowledgeArea, DifficultyLevel
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=2)
def load_questions(mode: str = "demo") -> List[Question]:
    """Load questions from JSON file with caching for performance"""
    try:
        with open("data/questions.json", "r") as f:
            data = json.load(f)
        
        # Select questions based on mode
        if mode == "demo":
            demo_ids = data.get("demo_questions", [])
            selected_questions = [q for q in data["questions"] if q["id"] in demo_ids]
        else:
            selected_questions = data["questions"]
        
        # Convert to Pydantic models and add explanations
        questions = []
        for q_data in selected_questions:
            # Add explanation if missing
            if not q_data.get("explanation"):
                q_data["explanation"] = _generate_explanation(q_data)
            
            questions.append(Question(**q_data))
        
        logger.info(f"Loaded {len(questions)} questions in {mode} mode")
        return questions
    
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

def _generate_explanation(question_data: Dict) -> str:
    """Generate explanation for questions that don't have one"""
    explanations = {
        "transformers": "This relates to transformer architecture and tokenization concepts.",
        "gans": "This involves understanding GAN components and training dynamics.",
        "pytorch": "This covers PyTorch framework operations and tensor manipulations.",
        "generative_ai": "This pertains to generative AI models and their applications.",
        "deep_learning": "This involves fundamental deep learning concepts and architectures.",
        "ml_basics": "This covers basic machine learning principles and evaluation metrics."
    }
    
    area = question_data.get("knowledge_area", "ml_basics")
    correct_option = question_data.get("correct_answer", "a")
    correct_text = question_data.get("options", {}).get(correct_option, "")
    
    base_explanation = explanations.get(area, "This is a fundamental concept in machine learning.")
    return f"{base_explanation} The correct answer is '{correct_text}' because it represents the standard approach in this domain."

def create_quiz_session(user_id: str, mode: str = "demo") -> QuizSession:
    """Create a new quiz session with selected questions"""
    questions = load_questions(mode)
    
    # Shuffle questions for variety
    shuffled_questions = random.sample(questions, len(questions))
    
    session = QuizSession(
        user_id=user_id,
        questions=shuffled_questions,
        mode=mode
    )
    
    logger.info(f"Created quiz session {session.session_id} for user {user_id}")
    return session

def calculate_score(session: QuizSession) -> QuizResult:
    """Calculate comprehensive quiz results with vectorized operations"""
    if not session.questions:
        return _create_empty_result(session.session_id)
    
    # Vectorized scoring using numpy
    total_questions = len(session.questions)
    correct_answers = 0
    area_performance = defaultdict(lambda: {"correct": 0, "total": 0})
    
    # Process all answers at once
    for question in session.questions:
        area = question.knowledge_area
        area_performance[area]["total"] += 1
        
        user_answer = session.answers.get(question.id)
        if user_answer and question.is_correct(user_answer):
            correct_answers += 1
            area_performance[area]["correct"] += 1
    
    # Calculate scores
    total_score = correct_answers / total_questions if total_questions > 0 else 0
    
    # Area-specific scores
    area_scores = {}
    for area, perf in area_performance.items():
        area_scores[area] = perf["correct"] / perf["total"] if perf["total"] > 0 else 0
    
    # Identify knowledge gaps (areas with score < 0.6)
    knowledge_gaps = [area for area, score in area_scores.items() if score < 0.6]
    
    # Determine performance level
    performance_level = _determine_performance_level(total_score, area_scores)
    
    # Areas needing recommendations
    recommendations_needed = [area for area, score in area_scores.items() if score < 0.7]
    
    result = QuizResult(
        session_id=session.session_id,
        total_score=total_score,
        area_scores=area_scores,
        knowledge_gaps=knowledge_gaps,
        performance_level=performance_level,
        recommendations_needed=recommendations_needed,
        total_questions=total_questions,
        correct_answers=correct_answers
    )
    
    logger.info(f"Calculated score: {total_score:.2f} for session {session.session_id}")
    return result

def analyze_knowledge_gaps(result: QuizResult) -> List[KnowledgeArea]:
    """Analyze and prioritize knowledge gaps"""
    if not result.area_scores:
        return []
    
    # Sort areas by score (lowest first) and filter gaps
    sorted_gaps = sorted(
        [(area, score) for area, score in result.area_scores.items() if score < 0.6],
        key=lambda x: x[1]
    )
    
    return [area for area, _ in sorted_gaps]

def get_difficulty_progression(results: List[QuizResult]) -> Dict[str, float]:
    """Analyze difficulty progression over time"""
    if not results:
        return {}
    
    # Sort by session time (most recent first)
    sorted_results = sorted(results, key=lambda x: x.session_id, reverse=True)
    
    progression = {
        "latest_score": sorted_results[0].total_score,
        "average_score": np.mean([r.total_score for r in sorted_results]),
        "improvement_trend": 0.0,
        "consistency": 0.0
    }
    
    if len(sorted_results) > 1:
        scores = [r.total_score for r in sorted_results]
        # Calculate trend (positive = improving)
        progression["improvement_trend"] = np.polyfit(range(len(scores)), scores, 1)[0]
        # Calculate consistency (lower std = more consistent)
        progression["consistency"] = 1.0 - np.std(scores)
    
    return progression

def _determine_performance_level(total_score: float, area_scores: Dict) -> DifficultyLevel:
    """Determine user's performance level based on scores"""
    if total_score >= 0.8:
        return DifficultyLevel.ADVANCED
    elif total_score >= 0.6:
        return DifficultyLevel.INTERMEDIATE
    else:
        return DifficultyLevel.BEGINNER

def _create_empty_result(session_id: str) -> QuizResult:
    """Create empty result for edge cases"""
    return QuizResult(
        session_id=session_id,
        total_score=0.0,
        area_scores={},
        knowledge_gaps=[],
        performance_level=DifficultyLevel.BEGINNER,
        recommendations_needed=[],
        total_questions=0,
        correct_answers=0
    )

def get_question_statistics(questions: List[Question]) -> Dict[str, any]:
    """Get statistics about question distribution"""
    if not questions:
        return {}
    
    area_counts = Counter(q.knowledge_area for q in questions)
    difficulty_counts = Counter(q.difficulty_level for q in questions)
    
    return {
        "total_questions": len(questions),
        "area_distribution": dict(area_counts),
        "difficulty_distribution": dict(difficulty_counts),
        "coverage": len(area_counts) / len(KnowledgeArea)
    }