import os
import asyncio
import logging
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from ..core.models import QuizResult, Recommendation, KnowledgeArea, DifficultyLevel
from core.models import QuizResult, Recommendation, KnowledgeArea, DifficultyLevel

load_dotenv()
logger = logging.getLogger(__name__)

class LLMProvider:
    """Unified LLM provider with fallback mechanisms"""
    
    def __init__(self):
        self.provider_type = os.getenv("LLM_PROVIDER", "ollama")
        self.llm = None
        self.fallback_active = False
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM with fallback support"""
        try:
            if self.provider_type == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm = OpenAI(
                        # temperature=0.7,
                        # max_tokens=500,
                        temperature=0.3,
                        max_tokens=300,
                        openai_api_key=api_key
                    )
                else:
                    logger.warning("OpenAI API key not found, using fallback")
                    self._activate_fallback()
            
            elif self.provider_type == "ollama":
                try:
                    from langchain.llms import Ollama
                    # self.llm = Ollama(model="llama2")
                    self.llm = Ollama(
                        model="qwen2.5:1.5b-instruct-q4_K_M",
                        temperature=0.3,
                        num_predict=200,
                        top_k=10,
                        top_p=0.9
                    )
                    
                except ImportError:
                    logger.warning("Ollama not available, using fallback")
                    self._activate_fallback()
            
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            self._activate_fallback()
    
    def _activate_fallback(self):
        """Activate rule-based fallback system"""
        self.fallback_active = True
        logger.info("Activated rule-based fallback system")

    def _get_cached_response(self, key: str) -> Optional[str]:
        """Simple in-memory caching for responses"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        return self._cache.get(key)

    def _cache_response(self, key: str, response: str):
        """Cache response for future use"""
        if not hasattr(self, '_cache'):
            self._cache = {}
        self._cache[key] = response

    def generate_recommendations(self, quiz_result: QuizResult) -> List[Recommendation]:
        """Generate personalized learning recommendations"""
        # Create cache key
        cache_key = f"rec_{quiz_result.total_score}_{len(quiz_result.knowledge_gaps)}"
        cached = self._get_cached_response(cache_key)
        
        if cached:
            return self._parse_recommendations(cached, quiz_result)

        if self.fallback_active:
            return self._generate_fallback_recommendations(quiz_result)
        
        try:
            from .prompts import get_recommendation_prompt
            prompt = get_recommendation_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Prepare context
            context = {
                "total_score": quiz_result.total_score,
                "knowledge_gaps": ", ".join(quiz_result.knowledge_gaps),
                "performance_level": quiz_result.performance_level,
                "area_scores": str(quiz_result.area_scores)
            }
            
            response = chain.run(**context)
            self._cache_response(cache_key, response)
            return self._parse_recommendations(response, quiz_result)
            
        except Exception as e:
            logger.error(f"LLM recommendation generation failed: {e}")
            return self._generate_fallback_recommendations(quiz_result)
    
    def get_personalized_advice(self, area: KnowledgeArea, performance: float) -> str:
        """Get personalized advice for specific knowledge area"""
        if self.fallback_active:
            return self._get_fallback_advice(area, performance)
        
        try:
            from .prompts import get_advice_prompt
            prompt = get_advice_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(
                area=area.value,
                performance=performance,
                level="beginner" if performance < 0.6 else "intermediate" if performance < 0.8 else "advanced"
            )
            return response.strip()
            
        except Exception as e:
            logger.error(f"Personalized advice generation failed: {e}")
            return self._get_fallback_advice(area, performance)
    
    def explain_concept(self, concept: str, level: str) -> str:
        """Explain a concept at specified difficulty level"""
        if self.fallback_active:
            return self._explain_concept_fallback(concept, level)
        
        try:
            from .prompts import get_explanation_prompt
            prompt = get_explanation_prompt()
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(concept=concept, level=level)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Concept explanation failed: {e}")
            return self._explain_concept_fallback(concept, level)
    
    def _generate_fallback_recommendations(self, quiz_result: QuizResult) -> List[Recommendation]:
        """Rule-based recommendation generation"""
        recommendations = []
        
        # Resource mappings
        resources = {
            KnowledgeArea.TRANSFORMERS: [
                "Attention Is All You Need paper",
                "Hugging Face Transformers tutorial",
                "The Illustrated Transformer blog post"
            ],
            KnowledgeArea.GANS: [
                "GAN paper by Ian Goodfellow",
                "PyTorch GAN tutorial",
                "DCGAN implementation guide"
            ],
            KnowledgeArea.PYTORCH: [
                "PyTorch official tutorials",
                "Deep Learning with PyTorch book",
                "PyTorch documentation"
            ],
            KnowledgeArea.GENERATIVE_AI: [
                "Generative AI overview course",
                "GPT and language models guide",
                "Stable Diffusion tutorial"
            ],
            KnowledgeArea.DEEP_LEARNING: [
                "Deep Learning book by Ian Goodfellow",
                "CS231n Stanford course",
                "Neural networks fundamentals"
            ],
            KnowledgeArea.ML_BASICS: [
                "Machine Learning course by Andrew Ng",
                "Pattern Recognition and Machine Learning",
                "Scikit-learn documentation"
            ]
        }
        
        for i, area in enumerate(quiz_result.recommendations_needed):
            score = quiz_result.area_scores.get(area, 0)
            
            recommendation = Recommendation(
                area=area,
                priority=i + 1,
                resources=resources.get(area, ["General ML resources"]),
                estimated_time=self._estimate_time(score),
                confidence_score=0.8,
                personalized_advice=self._get_fallback_advice(area, score)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _parse_recommendations(self, response: str, quiz_result: QuizResult) -> List[Recommendation]:
        """Parse LLM response into Recommendation objects"""
        recommendations = []
        
        # Simple parsing - in production, use more sophisticated parsing
        lines = response.split('\n')
        current_area = None
        
        for line in lines:
            line = line.strip()
            if any(area.value in line.lower() for area in KnowledgeArea):
                for area in KnowledgeArea:
                    if area.value in line.lower():
                        current_area = area
                        break
            
            if current_area and line:
                score = quiz_result.area_scores.get(current_area, 0)
                recommendation = Recommendation(
                    area=current_area,
                    priority=len(recommendations) + 1,
                    resources=["LLM generated resource"],
                    estimated_time=self._estimate_time(score),
                    confidence_score=0.9,
                    personalized_advice=line
                )
                recommendations.append(recommendation)
        
        return recommendations[:5]  # Limit to top 5
    
    def _estimate_time(self, score: float) -> str:
        """Estimate learning time based on performance"""
        if score < 0.3:
            return "2-3 weeks"
        elif score < 0.6:
            return "1-2 weeks"
        else:
            return "3-5 days"
    
    def _get_fallback_advice(self, area: KnowledgeArea, performance: float) -> str:
        """Generate fallback advice"""
        advice_templates = {
            KnowledgeArea.TRANSFORMERS: "Focus on understanding attention mechanisms and positional encoding",
            KnowledgeArea.GANS: "Start with basic GAN theory and gradually move to advanced architectures",
            KnowledgeArea.PYTORCH: "Practice tensor operations and autograd functionality",
            KnowledgeArea.GENERATIVE_AI: "Explore different generative models and their applications",
            KnowledgeArea.DEEP_LEARNING: "Strengthen fundamentals in neural network architectures",
            KnowledgeArea.ML_BASICS: "Review core concepts like supervised/unsupervised learning"
        }
        
        base_advice = advice_templates.get(area, "Focus on fundamental concepts")
        
        if performance < 0.4:
            return f"{base_advice}. Start with basic tutorials and hands-on practice."
        elif performance < 0.7:
            return f"{base_advice}. Try intermediate projects and real-world applications."
        else:
            return f"{base_advice}. Explore advanced topics and research papers."
    
    def _explain_concept_fallback(self, concept: str, level: str) -> str:
        """Fallback concept explanation"""
        return f"This concept relates to {concept}. For {level} level understanding, focus on practical applications and core principles."