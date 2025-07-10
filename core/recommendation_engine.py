import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from .models import QuizResult, Recommendation, KnowledgeArea, DifficultyLevel
from .quiz_engine import analyze_knowledge_gaps
# from ..llm.providers import LLMProvider
from llm.providers import LLMProvider

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """ML-powered recommendation system with collaborative and content-based filtering"""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or LLMProvider()
        self.scaler = StandardScaler()
        self.user_clusters = {}
        self.content_similarity = {}
        self._initialize_content_features()
    
    def _initialize_content_features(self):
        """Initialize content-based similarity matrix"""
        # Knowledge area relationships (domain knowledge)
        area_relationships = {
            KnowledgeArea.ML_BASICS: [KnowledgeArea.DEEP_LEARNING, KnowledgeArea.PYTORCH],
            KnowledgeArea.DEEP_LEARNING: [KnowledgeArea.TRANSFORMERS, KnowledgeArea.GANS, KnowledgeArea.GENERATIVE_AI],
            KnowledgeArea.PYTORCH: [KnowledgeArea.DEEP_LEARNING, KnowledgeArea.GANS],
            KnowledgeArea.TRANSFORMERS: [KnowledgeArea.GENERATIVE_AI, KnowledgeArea.DEEP_LEARNING],
            KnowledgeArea.GANS: [KnowledgeArea.GENERATIVE_AI, KnowledgeArea.DEEP_LEARNING],
            KnowledgeArea.GENERATIVE_AI: [KnowledgeArea.TRANSFORMERS, KnowledgeArea.GANS]
        }
        
        # Create similarity matrix
        areas = list(KnowledgeArea)
        n_areas = len(areas)
        similarity_matrix = np.zeros((n_areas, n_areas))
        
        for i, area1 in enumerate(areas):
            for j, area2 in enumerate(areas):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                elif area2 in area_relationships.get(area1, []):
                    similarity_matrix[i][j] = 0.8
                elif area1 in area_relationships.get(area2, []):
                    similarity_matrix[i][j] = 0.8
                else:
                    similarity_matrix[i][j] = 0.2
        
        self.content_similarity = {
            areas[i]: {areas[j]: similarity_matrix[i][j] for j in range(n_areas)}
            for i in range(n_areas)
        }

def generate_recommendations(quiz_result: QuizResult, user_history: List[QuizResult]) -> List[Recommendation]:
    """Generate personalized recommendations using hybrid approach"""
    engine = RecommendationEngine()
    
    # Analyze knowledge gaps
    knowledge_gaps = analyze_knowledge_gaps(quiz_result)
    
    # Get collaborative filtering recommendations
    collaborative_recs = engine._get_collaborative_recommendations(quiz_result, user_history)
    
    # Get content-based recommendations
    content_recs = engine._get_content_based_recommendations(quiz_result)
    
    # Combine and rank recommendations
    combined_recs = engine._combine_recommendations(collaborative_recs, content_recs, quiz_result)
    
    # Generate personalized advice using LLM
    for rec in combined_recs:
        try:
            area_score = quiz_result.area_scores.get(rec.area, 0)
            rec.personalized_advice = engine.llm_provider.get_personalized_advice(rec.area, area_score)
        except Exception as e:
            logger.error(f"Failed to generate personalized advice for {rec.area}: {e}")
    
    logger.info(f"Generated {len(combined_recs)} recommendations for session {quiz_result.session_id}")
    return combined_recs

def prioritize_learning_areas(gaps: List[KnowledgeArea], performance: Dict[KnowledgeArea, float]) -> List[KnowledgeArea]:
    """Prioritize learning areas based on performance and dependencies"""
    if not gaps:
        return []
    
    # Create priority scores
    priority_scores = {}
    
    for area in gaps:
        score = performance.get(area, 0)
        
        # Lower performance = higher priority
        base_priority = 1.0 - score
        
        # Boost priority for foundational areas
        foundation_boost = {
            KnowledgeArea.ML_BASICS: 0.3,
            KnowledgeArea.DEEP_LEARNING: 0.2,
            KnowledgeArea.PYTORCH: 0.15,
            KnowledgeArea.TRANSFORMERS: 0.1,
            KnowledgeArea.GANS: 0.05,
            KnowledgeArea.GENERATIVE_AI: 0.05
        }
        
        priority_scores[area] = base_priority + foundation_boost.get(area, 0)
    
    # Sort by priority score (highest first)
    sorted_areas = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
    return [area for area, _ in sorted_areas]

def get_similar_learners(current_result: QuizResult, all_results: List[QuizResult]) -> List[str]:
    """Find similar learners using clustering"""
    if len(all_results) < 2:
        return []
    
    try:
        # Create feature vectors
        features = []
        session_ids = []
        
        for result in all_results:
            feature_vector = []
            for area in KnowledgeArea:
                feature_vector.append(result.area_scores.get(area, 0))
            features.append(feature_vector)
            session_ids.append(result.session_id)
        
        # Add current result
        current_features = []
        for area in KnowledgeArea:
            current_features.append(current_result.area_scores.get(area, 0))
        features.append(current_features)
        session_ids.append(current_result.session_id)
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Calculate similarities
        current_vector = scaled_features[-1].reshape(1, -1)
        similarities = cosine_similarity(current_vector, scaled_features[:-1])[0]
        
        # Find most similar learners
        similar_indices = np.argsort(similarities)[-3:][::-1]  # Top 3 most similar
        similar_sessions = [session_ids[i] for i in similar_indices if similarities[i] > 0.7]
        
        return similar_sessions
        
    except Exception as e:
        logger.error(f"Error finding similar learners: {e}")
        return []

def adaptive_difficulty_suggestion(history: List[QuizResult]) -> DifficultyLevel:
    """Suggest next difficulty level based on performance history"""
    if not history:
        return DifficultyLevel.BEGINNER
    
    # Analyze recent performance (last 3 results)
    recent_results = history[-3:]
    avg_score = np.mean([r.total_score for r in recent_results])
    
    # Check consistency
    scores = [r.total_score for r in recent_results]
    consistency = 1.0 - np.std(scores) if len(scores) > 1 else 1.0
    
    # Determine next level
    if avg_score >= 0.85 and consistency > 0.8:
        return DifficultyLevel.ADVANCED
    elif avg_score >= 0.7 and consistency > 0.6:
        return DifficultyLevel.INTERMEDIATE
    else:
        return DifficultyLevel.BEGINNER

class RecommendationEngine:
    """Extended recommendation engine with advanced ML techniques"""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or LLMProvider()
        self.scaler = StandardScaler()
        self.content_similarity = {}
        self._initialize_content_features()
    
    def _initialize_content_features(self):
        """Initialize content-based similarity matrix"""
        # Knowledge area relationships
        area_relationships = {
            KnowledgeArea.ML_BASICS: [KnowledgeArea.DEEP_LEARNING, KnowledgeArea.PYTORCH],
            KnowledgeArea.DEEP_LEARNING: [KnowledgeArea.TRANSFORMERS, KnowledgeArea.GANS],
            KnowledgeArea.PYTORCH: [KnowledgeArea.DEEP_LEARNING, KnowledgeArea.GANS],
            KnowledgeArea.TRANSFORMERS: [KnowledgeArea.GENERATIVE_AI],
            KnowledgeArea.GANS: [KnowledgeArea.GENERATIVE_AI],
            KnowledgeArea.GENERATIVE_AI: [KnowledgeArea.TRANSFORMERS, KnowledgeArea.GANS]
        }
        
        areas = list(KnowledgeArea)
        self.content_similarity = {
            area1: {
                area2: 0.8 if area2 in area_relationships.get(area1, []) else 0.2
                for area2 in areas
            }
            for area1 in areas
        }
    
    def _get_collaborative_recommendations(self, quiz_result: QuizResult, user_history: List[QuizResult]) -> List[Recommendation]:
        """Generate collaborative filtering recommendations"""
        recommendations = []
        
        # Find similar learners
        similar_learners = get_similar_learners(quiz_result, user_history)
        
        if similar_learners:
            # Analyze what similar learners improved on
            improvement_areas = self._analyze_improvement_patterns(similar_learners, user_history)
            
            for area, confidence in improvement_areas.items():
                if area in quiz_result.recommendations_needed:
                    rec = Recommendation(
                        area=area,
                        priority=len(recommendations) + 1,
                        resources=self._get_resources_for_area(area),
                        estimated_time=self._estimate_learning_time(quiz_result.area_scores.get(area, 0)),
                        confidence_score=confidence,
                        personalized_advice=f"Based on similar learners' success patterns"
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _get_content_based_recommendations(self, quiz_result: QuizResult) -> List[Recommendation]:
        """Generate content-based recommendations"""
        recommendations = []
        
        for area in quiz_result.recommendations_needed:
            # Find related areas where user performed well
            related_strengths = []
            for strength_area, score in quiz_result.area_scores.items():
                if score > 0.7:
                    similarity = self.content_similarity.get(area, {}).get(strength_area, 0)
                    if similarity > 0.5:
                        related_strengths.append((strength_area, similarity))
            
            # Calculate confidence based on related strengths
            confidence = min(0.9, sum(sim for _, sim in related_strengths) / len(related_strengths)) if related_strengths else 0.6
            
            rec = Recommendation(
                area=area,
                priority=len(recommendations) + 1,
                resources=self._get_resources_for_area(area),
                estimated_time=self._estimate_learning_time(quiz_result.area_scores.get(area, 0)),
                confidence_score=confidence,
                personalized_advice=f"Build on your strengths in {', '.join(area.value for area, _ in related_strengths[:2])}"
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _combine_recommendations(self, collaborative: List[Recommendation], content: List[Recommendation], quiz_result: QuizResult) -> List[Recommendation]:
        """Combine and rank recommendations from different sources"""
        all_recs = {}
        
        # Combine by area
        for rec in collaborative + content:
            if rec.area not in all_recs:
                all_recs[rec.area] = rec
            else:
                # Merge confidence scores
                existing = all_recs[rec.area]
                existing.confidence_score = (existing.confidence_score + rec.confidence_score) / 2
                existing.resources = list(set(existing.resources + rec.resources))
        
        # Sort by priority and confidence
        final_recs = list(all_recs.values())
        final_recs.sort(key=lambda x: (x.priority, -x.confidence_score))
        
        # Reassign priorities
        for i, rec in enumerate(final_recs):
            rec.priority = i + 1
        
        return final_recs[:5]  # Return top 5
    
    def _analyze_improvement_patterns(self, similar_sessions: List[str], history: List[QuizResult]) -> Dict[KnowledgeArea, float]:
        """Analyze improvement patterns from similar learners"""
        improvement_areas = defaultdict(float)
        
        for session_id in similar_sessions:
            # Find results for this session
            session_results = [r for r in history if r.session_id == session_id]
            if len(session_results) > 1:
                # Calculate improvements
                for i in range(1, len(session_results)):
                    current = session_results[i]
                    previous = session_results[i-1]
                    
                    for area in KnowledgeArea:
                        current_score = current.area_scores.get(area, 0)
                        previous_score = previous.area_scores.get(area, 0)
                        improvement = current_score - previous_score
                        
                        if improvement > 0.1:  # Significant improvement
                            improvement_areas[area] += improvement
        
        # Normalize by number of similar learners
        if similar_sessions:
            for area in improvement_areas:
                improvement_areas[area] /= len(similar_sessions)
        
        return dict(improvement_areas)
    
    def _get_resources_for_area(self, area: KnowledgeArea) -> List[str]:
        """Get curated resources for knowledge area"""
        resources = {
            KnowledgeArea.ML_BASICS: [
                "Machine Learning Yearning by Andrew Ng",
                "Hands-On Machine Learning with Scikit-Learn and TensorFlow",
                "ML Crash Course by Google"
            ],
            KnowledgeArea.DEEP_LEARNING: [
                "Deep Learning by Ian Goodfellow",
                "CS231n: Convolutional Neural Networks for Visual Recognition",
                "Fast.ai Deep Learning for Coders"
            ],
            KnowledgeArea.PYTORCH: [
                "PyTorch Tutorials (official documentation)",
                "Deep Learning with PyTorch by Eli Stevens",
                "PyTorch Lightning documentation"
            ],
            KnowledgeArea.TRANSFORMERS: [
                "Attention Is All You Need (original paper)",
                "The Illustrated Transformer by Jay Alammar",
                "Hugging Face Transformers course"
            ],
            KnowledgeArea.GANS: [
                "Generative Adversarial Networks (original paper)",
                "GAN Specialization on Coursera",
                "PyTorch GAN implementations"
            ],
            KnowledgeArea.GENERATIVE_AI: [
                "Introduction to Generative AI by Google",
                "Generative Deep Learning book",
                "OpenAI GPT papers and documentation"
            ]
        }
        return resources.get(area, ["General ML resources"])
    
    def _estimate_learning_time(self, current_score: float) -> str:
        """Estimate learning time based on current performance"""
        if current_score < 0.3:
            return "3-4 weeks"
        elif current_score < 0.5:
            return "2-3 weeks"
        elif current_score < 0.7:
            return "1-2 weeks"
        else:
            return "3-5 days"