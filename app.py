import streamlit as st
import time
from datetime import datetime
from core.models import QuizSession, QuizResult
from core.database import init_database, save_quiz_session, get_quiz_result, save_quiz_result, get_user_history
from core.quiz_engine import create_quiz_session, calculate_score
from core.recommendation_engine import generate_recommendations
from ui.components import (
    render_question_card, display_progress_bar, show_results_dashboard,
    render_recommendations_panel, show_motivational_message, create_loading_spinner
)
from ui.styles import load_css, apply_theme

# Page configuration
st.set_page_config(
    page_title="AI Quiz & Recommendation System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    
    if 'quiz_mode' not in st.session_state:
        st.session_state.quiz_mode = "demo"
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if 'theme' not in st.session_state:
        st.session_state.theme = "Light"

def calculate_current_score(session: QuizSession) -> float:
    """Calculate current score based on answered questions"""
    if not session.answers:
        return 0.0
    
    correct = 0
    for question in session.questions:
        if question.id in session.answers:
            if question.is_correct(session.answers[question.id]):
                correct += 1
    
    return correct / len(session.answers) if session.answers else 0.0

def landing_page():
    """Display landing page with quiz options"""
    st.markdown("# 🧠 AI Quiz & Recommendation System")
    st.markdown("### Personalized Learning Path Generator")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Welcome to the AI Quiz & Recommendation System! This intelligent platform:
        
        - **Assesses** your knowledge across key AI/ML domains
        - **Analyzes** your performance with advanced algorithms
        - **Recommends** personalized learning paths
        - **Tracks** your progress over time
        
        Choose your quiz mode to get started:
        """)
    
    with col2:
        try:
            st.image("hero_image.png", caption="AI-Powered Learning")
        except:
            st.markdown("### 🎓")
            st.markdown("*AI-Powered Learning*")
    
    # Quiz mode selection
    st.markdown("## Choose Your Quiz Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Quick Demo (10 questions)", use_container_width=True):
            st.session_state.quiz_mode = "demo"
            start_quiz()
    
    with col2:
        if st.button("📚 Full Assessment (63 questions)", use_container_width=True):
            st.session_state.quiz_mode = "full"
            start_quiz()
    
    # User history
    display_user_history()

def start_quiz():
    """Initialize and start a new quiz session"""
    with st.spinner("Preparing your personalized quiz..."):
        st.session_state.current_session = create_quiz_session(
            st.session_state.user_id,
            st.session_state.quiz_mode
        )
        st.session_state.current_question = 0
        st.session_state.quiz_completed = False
        st.session_state.results = None
        st.rerun()

def quiz_interface():
    """Main quiz interface"""
    session = st.session_state.current_session
    
    if not session or not session.questions:
        st.error("No quiz session found. Please start a new quiz.")
        if st.button("Return to Home"):
            st.session_state.current_session = None
            st.rerun()
        return
    
    current_q_idx = st.session_state.current_question
    total_questions = len(session.questions)
    
    # Header
    st.markdown("# 📝 AI Knowledge Assessment")
    
    # Progress tracking
    answered_count = len(session.answers)
    current_score = calculate_current_score(session)
    display_progress_bar(answered_count, total_questions, current_score)
    
    # Question display
    if current_q_idx < total_questions:
        question = session.questions[current_q_idx]
        
        st.markdown("---")
        
        # Render question card
        user_answer = render_question_card(question, current_q_idx + 1)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q_idx > 0:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if user_answer:
                if st.button("💾 Save Answer", use_container_width=True):
                    session.add_answer(question.id, user_answer)
                    save_quiz_session(session)
                    st.success("Answer saved!")
                    time.sleep(0.5)
                    st.rerun()
        
        with col3:
            if current_q_idx < total_questions - 1:
                if st.button("Next ➡️", use_container_width=True):
                    if user_answer:
                        session.add_answer(question.id, user_answer)
                        save_quiz_session(session)
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("🏁 Finish Quiz", use_container_width=True):
                    if user_answer:
                        session.add_answer(question.id, user_answer)
                    complete_quiz()
    
    # Sidebar with quiz info
    with st.sidebar:
        st.markdown("### Quiz Information")
        st.info(f"Mode: {session.mode.title()}")
        st.info(f"Questions: {answered_count}/{total_questions}")
        
        if answered_count > 0:
            st.metric("Current Score", f"{current_score:.1%}")
        
        # Question navigator
        st.markdown("### Question Navigator")
        for i, q in enumerate(session.questions):
            status = "✅" if q.id in session.answers else "⭕"
            if st.button(f"{status} Q{i+1}", key=f"nav_{i}"):
                st.session_state.current_question = i
                st.rerun()

def complete_quiz():
    """Complete the quiz and generate results"""
    session = st.session_state.current_session
    session.complete_session()
    
    # Save final session
    save_quiz_session(session)
    
    # Calculate results
    with st.spinner("Analyzing your performance..."):
        results = calculate_score(session)
        save_quiz_result(results)
        
        # Generate recommendations
        user_history = get_user_history(st.session_state.user_id)
        recommendations = generate_recommendations(results, user_history)
        
        st.session_state.results = results
        st.session_state.recommendations = recommendations
        st.session_state.quiz_completed = True
        st.rerun()

def results_page():
    """Display quiz results and recommendations"""
    if not st.session_state.results:
        st.error("No results found. Please complete a quiz first.")
        return
    
    results = st.session_state.results
    
    # Results dashboard
    show_results_dashboard(results)
    
    # Motivational message
    strengths = [area.value for area, score in results.area_scores.items() if score >= 0.8]
    improvements = [area.value for area in results.knowledge_gaps]
    show_motivational_message(results.total_score, strengths, improvements)
    
    # Recommendations
    if hasattr(st.session_state, 'recommendations'):
        st.markdown("---")
        render_recommendations_panel(st.session_state.recommendations)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.current_session = None
            st.session_state.quiz_completed = False
            st.rerun()
    
    with col2:
        if st.button("📈 View History", use_container_width=True):
            display_detailed_history()
    
    with col3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_session = None
            st.session_state.quiz_completed = False
            st.rerun()

def display_user_history():
    """Display user's quiz history"""
    history = get_user_history(st.session_state.user_id)
    
    if history:
        st.markdown("## 📊 Your Progress")
        
        # Recent performance
        recent_scores = [r.total_score for r in history[-5:]]
        if len(recent_scores) > 1:
            trend = "📈" if recent_scores[-1] > recent_scores[-2] else "📉"
            st.metric(
                "Recent Performance",
                f"{recent_scores[-1]:.1%}",
                delta=f"{trend} {(recent_scores[-1] - recent_scores[-2]):.1%}"
            )

def display_detailed_history():
    """Display detailed quiz history"""
    history = get_user_history(st.session_state.user_id)
    
    if not history:
        st.info("No quiz history found. Take a quiz to see your progress!")
        return
    
    st.markdown("## 📈 Quiz History")
    
    for i, result in enumerate(reversed(history[-10:]), 1):
        with st.expander(f"Quiz #{len(history) - i + 1} - {result.total_score:.1%}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Score:** {result.total_score:.1%}")
                st.write(f"**Questions:** {result.correct_answers}/{result.total_questions}")
                st.write(f"**Performance Level:** {result.performance_level.value.title()}")
            
            with col2:
                st.write("**Knowledge Gaps:**")
                for gap in result.knowledge_gaps:
                    st.write(f"• {gap.value.replace('_', ' ').title()}")

def main():
    """Main application flow"""
    # Initialize session state first
    initialize_session_state()
    
    # Load custom CSS
    load_css()
    
    # Initialize database
    init_database()
    
    # Theme selector in sidebar
    with st.sidebar:
        # Theme selection
        theme_options = ["Light", "Dark"]
        selected_theme = st.selectbox(
            "🎨 Theme", 
            theme_options, 
            index=theme_options.index(st.session_state.theme),
            key="theme_selector"
        )
        
        # Update theme if changed
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()
    
    # Apply theme
    apply_theme(st.session_state.theme.lower())
    
    # Main application logic
    if st.session_state.quiz_completed and st.session_state.results:
        results_page()
    elif st.session_state.current_session:
        quiz_interface()
    else:
        landing_page()

if __name__ == "__main__":
    main()