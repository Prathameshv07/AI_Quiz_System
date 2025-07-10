import sqlite3
import json
import logging
from functools import lru_cache
from contextlib import contextmanager
from typing import List, Optional, Dict
# from .models import QuizSession, QuizResult, Question, Recommendation
from core.models import QuizSession, QuizResult, Question, Recommendation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "quiz_system.db"

@lru_cache(maxsize=1)
def get_db_connection():
    """Cached database connection for better performance"""
    return sqlite3.connect(DATABASE_PATH, check_same_thread=False)

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_database() -> None:
    """Initialize database tables with proper indexing"""
    with get_db_cursor() as cursor:
        # Quiz sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                questions TEXT NOT NULL,
                answers TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                mode TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Quiz results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                session_id TEXT PRIMARY KEY,
                total_score REAL NOT NULL,
                area_scores TEXT NOT NULL,
                knowledge_gaps TEXT NOT NULL,
                performance_level TEXT NOT NULL,
                recommendations_needed TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES quiz_sessions (session_id)
            )
        ''')
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                area TEXT NOT NULL,
                priority INTEGER NOT NULL,
                resources TEXT NOT NULL,
                estimated_time TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                personalized_advice TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES quiz_sessions (session_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON quiz_sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON quiz_results(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_rec_session ON recommendations(session_id)')
        
        logger.info("Database initialized successfully")

def save_quiz_session(session: QuizSession) -> bool:
    """Save quiz session to database"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO quiz_sessions 
                (session_id, user_id, questions, answers, start_time, end_time, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.user_id,
                json.dumps([q.dict() for q in session.questions]),
                json.dumps(session.answers),
                session.start_time,
                session.end_time,
                session.mode
            ))
            return True
    except Exception as e:
        logger.error(f"Error saving quiz session: {e}")
        return False

def get_quiz_result(session_id: str) -> Optional[QuizResult]:
    """Retrieve quiz result by session ID"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM quiz_results WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if row:
                return QuizResult(
                    session_id=row['session_id'],
                    total_score=row['total_score'],
                    area_scores=json.loads(row['area_scores']),
                    knowledge_gaps=json.loads(row['knowledge_gaps']),
                    performance_level=row['performance_level'],
                    recommendations_needed=json.loads(row['recommendations_needed']),
                    total_questions=row['total_questions'],
                    correct_answers=row['correct_answers']
                )
            return None
    except Exception as e:
        logger.error(f"Error retrieving quiz result: {e}")
        return None

def save_quiz_result(result: QuizResult) -> bool:
    """Save quiz result to database"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO quiz_results 
                (session_id, total_score, area_scores, knowledge_gaps, performance_level, 
                 recommendations_needed, total_questions, correct_answers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.session_id,
                result.total_score,
                json.dumps(result.area_scores),
                json.dumps(result.knowledge_gaps),
                result.performance_level,
                json.dumps(result.recommendations_needed),
                result.total_questions,
                result.correct_answers
            ))
            return True
    except Exception as e:
        logger.error(f"Error saving quiz result: {e}")
        return False

def save_recommendations(session_id: str, recommendations: List[Recommendation]) -> bool:
    """Save recommendations to database"""
    try:
        with get_db_cursor() as cursor:
            # Clear existing recommendations for this session
            cursor.execute('DELETE FROM recommendations WHERE session_id = ?', (session_id,))
            
            # Insert new recommendations
            for rec in recommendations:
                cursor.execute('''
                    INSERT INTO recommendations 
                    (session_id, area, priority, resources, estimated_time, confidence_score, personalized_advice)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    rec.area,
                    rec.priority,
                    json.dumps(rec.resources),
                    rec.estimated_time,
                    rec.confidence_score,
                    rec.personalized_advice
                ))
            return True
    except Exception as e:
        logger.error(f"Error saving recommendations: {e}")
        return False

def get_user_history(user_id: str) -> List[QuizResult]:
    """Get user's quiz history"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                SELECT r.* FROM quiz_results r 
                JOIN quiz_sessions s ON r.session_id = s.session_id 
                WHERE s.user_id = ? 
                ORDER BY r.created_at DESC
            ''', (user_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append(QuizResult(
                    session_id=row['session_id'],
                    total_score=row['total_score'],
                    area_scores=json.loads(row['area_scores']),
                    knowledge_gaps=json.loads(row['knowledge_gaps']),
                    performance_level=row['performance_level'],
                    recommendations_needed=json.loads(row['recommendations_needed']),
                    total_questions=row['total_questions'],
                    correct_answers=row['correct_answers']
                ))
            return results
    except Exception as e:
        logger.error(f"Error retrieving user history: {e}")
        return []