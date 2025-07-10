import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
# from ..core.models import Question, QuizResult, Recommendation, KnowledgeArea
from core.models import Question, QuizResult, Recommendation, KnowledgeArea
import numpy as np

def render_question_card(question: Question, question_num: int) -> Optional[str]:
    """Render an interactive question card with modern styling"""
    st.markdown(f"""
    <div class="question-card">
        <div class="question-header">
            <span class="question-number">Question {question_num}</span>
            <span class="difficulty-badge {question.difficulty_level.value}">{question.difficulty_level.value.title()}</span>
        </div>
        <div class="question-text">{question.question_text}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create options with radio buttons
    options_text = [f"{key.upper()}: {value}" for key, value in question.options.items()]
    selected = st.radio(
        "Choose your answer:",
        options_text,
        key=f"question_{question.id}",
        label_visibility="collapsed"
    )
    
    if selected:
        return selected[0].lower()  # Return the key (a, b, c, d)
    return None

def display_progress_bar(current: int, total: int, score: float) -> None:
    """Display an animated progress bar with score information"""
    progress_percentage = current / total if total > 0 else 0
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(progress_percentage)
        st.caption(f"Progress: {current}/{total} questions")
    
    with col2:
        if current > 0:
            st.markdown(f"""
            <div class="metric-card">
                <p style="margin:0;font-weight:bold;">Current Score</p>
                <p style="font-size:20px;">{score:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if current > 0:
            st.markdown(f"""
            <div class="metric-card">
                <p style="margin:0;font-weight:bold;">Accuracy</p>
                <p style="font-size:20px;">{(score * current):.0f}/{current}</p>
            </div>
            """, unsafe_allow_html=True)

@st.cache_data
def show_results_dashboard(_result: QuizResult) -> None:
    """Display comprehensive results dashboard"""
    st.markdown("## 📊 Quiz Results")
    
    # Overall performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{_result.get_percentage():.1f}%",
            delta=f"{_result.correct_answers}/{_result.total_questions}"
        )
    
    with col2:
        st.metric(
            "Performance Level",
            _result.performance_level.value.title(),
            delta=f"{len(_result.knowledge_gaps)} gaps"
        )
    
    with col3:
        st.metric(
            "Areas Mastered",
            f"{len([s for s in _result.area_scores.values() if s >= 0.8])}",
            delta=f"of {len(_result.area_scores)}"
        )
    
    with col4:
        st.metric(
            "Improvement Areas",
            f"{len(_result.recommendations_needed)}",
            delta="recommendations"
        )
    
    # Performance visualization
    st.markdown("### 📈 Performance by Knowledge Area")
    fig = create_performance_chart(_result.area_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Knowledge gaps analysis
    if _result.knowledge_gaps:
        st.markdown("### 🎯 Knowledge Gaps Analysis")
        for gap in _result.knowledge_gaps:
            score = _result.area_scores.get(gap, 0)
            st.warning(f"**{gap.value.replace('_', ' ').title()}**: {score:.1%} accuracy - Focus needed")

def render_recommendations_panel(recommendations: List[Recommendation]) -> None:
    """Render personalized recommendations panel"""
    if not recommendations:
        st.info("No specific recommendations at this time. Great job!")
        return
    
    st.markdown("## 🎯 Personalized Learning Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"#{i} {rec.area.value.replace('_', ' ').title()} - Priority {rec.priority}"):
            
            st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)

            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Personalized Advice:**")
                st.write(rec.personalized_advice)
                
                st.markdown(f"**Recommended Resources:**")
                for resource in rec.resources:
                    st.write(f"• {resource}")
            
            with col2:
                st.metric("Confidence Score", f"{rec.confidence_score:.1%}")
                st.metric("Estimated Time", rec.estimated_time)
                
                # Priority indicator
                priority_color = ["🔴", "🟠", "🟡", "🟢", "🔵"][rec.priority - 1]
                st.write(f"Priority: {priority_color}")

            st.markdown('</div>', unsafe_allow_html=True)

def create_performance_chart(area_scores: Dict[str, float]) -> go.Figure:
    """Create interactive performance visualization"""
    if not area_scores:
        return go.Figure()
    
    # Convert enum keys to readable names
    areas = []
    scores = []
    colors = []
    
    for area, score in area_scores.items():
        area_name = area.value.replace('_', ' ').title() if hasattr(area, 'value') else str(area).replace('_', ' ').title()
        areas.append(area_name)
        scores.append(score * 100)  # Convert to percentage
        
        # Color coding based on performance
        if score >= 0.8:
            colors.append('#00C851')  # Green for excellent
        elif score >= 0.6:
            colors.append('#ffbb33')  # Orange for good
        else:
            colors.append('#ff4444')  # Red for needs improvement
    
    # Get current theme
    current_theme = st.session_state.get('theme', 'Light').lower()
    
    # Theme-specific colors
    theme_colors = {
        'light': {
            'text': '#000000',
            'paper_bg': '#ffffff',
            'plot_bg': '#ffffff',
            'grid_color': '#e0e0e0',
            'line_color': 'rgba(0, 100, 255, 0.8)',
            'fill_color': 'rgba(0, 100, 255, 0.1)',
            'benchmark_color': 'rgba(255, 0, 0, 0.8)'
        },
        'dark': {
            'text': '#ffffff',
            'paper_bg': '#000000',
            'plot_bg': '#000000',
            'grid_color': '#333333',
            'line_color': 'rgba(0, 150, 255, 0.9)',
            'fill_color': 'rgba(0, 150, 255, 0.2)',
            'benchmark_color': 'rgba(255, 100, 100, 0.9)'
        }
    }
    
    colors_theme = theme_colors.get(current_theme, theme_colors['light'])
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=areas,
        fill='toself',
        name='Performance',
        line=dict(color=colors_theme['line_color']),
        fillcolor=colors_theme['fill_color']
    ))
    
    # Add benchmark line at 70%
    fig.add_trace(go.Scatterpolar(
        r=[70] * len(areas),
        theta=areas,
        mode='lines',
        name='Target (70%)',
        line=dict(color=colors_theme['benchmark_color'], dash='dash')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%',
                tickcolor=colors_theme['text'],
                tickfont=dict(color=colors_theme['text']),
                gridcolor=colors_theme['grid_color']
            ),
            angularaxis=dict(
                tickcolor=colors_theme['text'],
                tickfont=dict(color=colors_theme['text']),
                gridcolor=colors_theme['grid_color']
            )
        ),
        showlegend=True,
        title=dict(
            text="Knowledge Area Performance",
            font=dict(size=16, color=colors_theme['text'])
        ),
        font=dict(size=14, color=colors_theme['text']),
        paper_bgcolor=colors_theme['paper_bg'],
        plot_bgcolor=colors_theme['plot_bg'],
        legend=dict(
            font=dict(color=colors_theme['text']),
            bgcolor=colors_theme['paper_bg']
        )
    )
    
    return fig

def create_loading_spinner(text: str = "Processing...") -> None:
    """Create a loading spinner with custom text"""
    with st.spinner(text):
        st.empty()

def show_motivational_message(score: float, strengths: List[str], improvements: List[str]) -> None:
    """Display motivational message based on performance"""
    if score >= 0.8:
        st.success("🎉 Excellent work! You've mastered most concepts!")
    elif score >= 0.6:
        st.info("👍 Good job! You're on the right track with solid understanding.")
    else:
        st.warning("💪 Keep going! Every expert was once a beginner.")
    
    if strengths:
        st.markdown(f"**Your strengths:** {', '.join(strengths)}")
    
    if improvements:
        st.markdown(f"**Focus areas:** {', '.join(improvements)}")

def render_question_explanation(question: Question, user_answer: str, is_correct: bool) -> None:
    """Render explanation after question is answered"""
    if is_correct:
        st.success("✅ Correct!")
    else:
        st.error(f"❌ Incorrect. The correct answer was: {question.correct_answer.upper()}")
    
    if question.explanation:
        st.info(f"💡 **Explanation:** {question.explanation}")

def create_comparison_chart(current_result: QuizResult, previous_results: List[QuizResult]) -> go.Figure:
    """Create performance comparison chart over time"""
    if not previous_results:
        return go.Figure()
    
    # Get current theme
    current_theme = st.session_state.get('theme', 'Light').lower()
    
    # Theme-specific colors
    theme_colors = {
        'light': {
            'text': '#000000',
            'paper_bg': '#ffffff',
            'plot_bg': '#ffffff',
            'grid_color': '#e0e0e0',
            'line_color': '#007bff',
            'current_color': '#28a745'
        },
        'dark': {
            'text': '#ffffff',
            'paper_bg': '#000000',
            'plot_bg': '#000000',
            'grid_color': '#333333',
            'line_color': '#4dabf7',
            'current_color': '#51cf66'
        }
    }
    
    colors_theme = theme_colors.get(current_theme, theme_colors['light'])
    
    # Extract scores over time
    sessions = [r.session_id[-8:] for r in previous_results]  # Last 8 chars of session ID
    total_scores = [r.total_score * 100 for r in previous_results]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=sessions,
        y=total_scores,
        mode='lines+markers',
        name='Performance Trend',
        line=dict(color=colors_theme['line_color'], width=3),
        marker=dict(size=8)
    ))
    
    # Add current result
    fig.add_trace(go.Scatter(
        x=[sessions[-1] if sessions else 'Current'],
        y=[current_result.total_score * 100],
        mode='markers',
        name='Current Result',
        marker=dict(size=12, color=colors_theme['current_color'])
    ))
    
    fig.update_layout(
        title=dict(
            text="Performance Trend Over Time",
            font=dict(color=colors_theme['text'])
        ),
        xaxis=dict(
            title="Quiz Sessions",
            titlefont=dict(color=colors_theme['text']),
            tickfont=dict(color=colors_theme['text']),
            gridcolor=colors_theme['grid_color']
        ),
        yaxis=dict(
            title="Score (%)",
            titlefont=dict(color=colors_theme['text']),
            tickfont=dict(color=colors_theme['text']),
            gridcolor=colors_theme['grid_color']
        ),
        showlegend=True,
        height=400,
        font=dict(color=colors_theme['text']),
        paper_bgcolor=colors_theme['paper_bg'],
        plot_bgcolor=colors_theme['plot_bg'],
        legend=dict(
            font=dict(color=colors_theme['text']),
            bgcolor=colors_theme['paper_bg']
        )
    )
    
    return fig