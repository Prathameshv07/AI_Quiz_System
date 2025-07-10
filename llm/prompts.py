from langchain.prompts import PromptTemplate

def get_recommendation_prompt() -> PromptTemplate:
    """Generate learning recommendations based on quiz performance"""
    template = """
    You are an AI learning advisor specializing in machine learning and AI education.
    
    Based on the following quiz performance data, provide personalized learning recommendations:
    
    Overall Score: {total_score}
    Performance Level: {performance_level}
    Knowledge Gaps: {knowledge_gaps}
    Area Scores: {area_scores}
    
    Please provide specific, actionable recommendations for each knowledge gap area.
    Focus on:
    1. Immediate next steps
    2. Specific resources or tutorials
    3. Practice exercises
    4. Estimated time commitment
    
    Format your response as clear, prioritized recommendations.
    """
    
    return PromptTemplate(
        input_variables=["total_score", "performance_level", "knowledge_gaps", "area_scores"],
        template=template
    )

def get_advice_prompt() -> PromptTemplate:
    """Generate personalized advice for specific knowledge area"""
    template = """
    You are an expert in {area} within machine learning and AI.
    
    A student has achieved {performance}% performance in this area at {level} level.
    
    Provide specific, encouraging advice that includes:
    1. What they're doing well
    2. Key concepts to focus on next
    3. Practical exercises to improve
    4. Common pitfalls to avoid
    
    Keep the advice motivational and actionable.
    """
    
    return PromptTemplate(
        input_variables=["area", "performance", "level"],
        template=template
    )

def get_explanation_prompt() -> PromptTemplate:
    """Explain complex concepts at appropriate difficulty level"""
    template = """
    Explain the concept of "{concept}" at {level} level.
    
    Guidelines:
    - For beginner: Use simple language, analogies, and basic examples
    - For intermediate: Include technical details and practical applications
    - For advanced: Discuss nuances, research developments, and complex implementations
    
    Provide a clear, engaging explanation that builds understanding progressively.
    """
    
    return PromptTemplate(
        input_variables=["concept", "level"],
        template=template
    )

def get_motivation_prompt() -> PromptTemplate:
    """Generate motivational content based on performance"""
    template = """
    A student has just completed a quiz with {score}% accuracy.
    Their strengths are in: {strengths}
    Areas for improvement: {improvements}
    
    Provide encouraging, personalized motivation that:
    1. Celebrates their achievements
    2. Frames challenges as opportunities
    3. Gives specific next steps
    4. Maintains optimism about their learning journey
    
    Keep it brief but impactful.
    """
    
    return PromptTemplate(
        input_variables=["score", "strengths", "improvements"],
        template=template
    )