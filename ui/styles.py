import streamlit as st

def load_css():
    """Load custom CSS styles for the application"""
    st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        min-height: 100vh;
        transition: all 0.3s ease;
    }
                
    .recommendation-card {
        background-color: var(--card-bg);
        color: var(--text-color);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .metric-card {
        padding: 10px;
        border-radius: 6px;
        background-color: var(--card-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    /* Question card styling */
    .question-card {
        background: var(--card-bg);
        color: var(--text-color);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 6px var(--shadow-color);
        border-left: 4px solid #007bff;
        transition: all 0.3s ease;
    }   
    
    .question-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px var(--shadow-color-hover);
    }
    
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .question-number {
        font-size: 14px;
        font-weight: 600;
        color: var(--secondary-text);
        background: var(--badge-bg);
        padding: 4px 12px;
        border-radius: 20px;
    }
    
    .difficulty-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .difficulty-badge.beginner {
        background: var(--success-bg);
        color: var(--success-text);
    }
    
    .difficulty-badge.intermediate {
        background: var(--warning-bg);
        color: var(--warning-text);
    }
    
    .difficulty-badge.advanced {
        background: var(--danger-bg);
        color: var(--danger-text);
    }
    
    .question-text {
        font-size: 18px;
        line-height: 1.6;
        color: var(--text-color);
        font-weight: 500;
    }
    
    /* Results dashboard */
    .results-header {
        text-align: center;
        padding: 32px 0;
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #007bff;
        margin: 8px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--secondary-text);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Recommendations panel */
    .priority-high {
        border-left-color: #dc3545;
    }
    
    .priority-medium {
        border-left-color: #ffc107;
    }
    
    .priority-low {
        border-left-color: #28a745;
    }
    
    .recommendation-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 12px;
    }
    
    .recommendation-advice {
        font-size: 14px;
        line-height: 1.6;
        color: var(--secondary-text);
        margin-bottom: 16px;
    }
    
    .resource-list {
        list-style: none;
        padding: 0;
    }
    
    .resource-item {
        background: var(--resource-bg);
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 4px;
        border-left: 3px solid #007bff;
        color: var(--text-color);
    }
    
    /* Progress indicators */
    .progress-container {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 2px 4px var(--shadow-color);
    }
    
    .progress-bar {
        height: 8px;
        background: var(--progress-bg);
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #007bff, #28a745);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Navigation */
    .nav-button {
        background: var(--btn-bg);
        color: var(--btn-text);
        border: 1px solid var(--border-color);
        padding: 12px 24px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        margin: 8px;
    }
    
    .nav-button:hover {
        background: var(--btn-hover);
        transform: translateY(-1px);
    }
    
    .nav-button:disabled {
        background: #6c757d;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .question-card {
            padding: 16px;
            margin: 8px 0;
        }
        
        .question-text {
            font-size: 16px;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .nav-button {
            padding: 10px 20px;
            font-size: 14px;
        }
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    /* Success/Error states */
    .success-message {
        background: var(--success-bg);
        color: var(--success-text);
        padding: 12px 16px;
        border-radius: 6px;
        border-left: 4px solid #28a745;
        margin: 8px 0;
    }
    
    .error-message {
        background: var(--danger-bg);
        color: var(--danger-text);
        padding: 12px 16px;
        border-radius: 6px;
        border-left: 4px solid #dc3545;
        margin: 8px 0;
    }
    
    .info-message {
        background: var(--info-bg);
        color: var(--info-text);
        padding: 12px 16px;
        border-radius: 6px;
        border-left: 4px solid #17a2b8;
        margin: 8px 0;
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 3px solid var(--spinner-bg);
        border-top: 3px solid #007bff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def apply_theme(theme: str = "light"):
    """Apply light or dark theme styling to the app"""
    
    colors = {
        "dark": {
            "bg": "#000000",
            "text": "#ffffff",
            "secondary_text": "#b0b0b0",
            "card_bg": "#1a1a1a",
            "border_color": "#333333",
            "btn_bg": "#2a2a2a",
            "btn_text": "#ffffff",
            "btn_hover": "#3a3a3a",
            "input_bg": "#2a2a2a",
            "badge_bg": "#2a2a2a",
            "resource_bg": "#2a2a2a",
            "progress_bg": "#2a2a2a",
            "spinner_bg": "#333333",
            "shadow_color": "rgba(255, 255, 255, 0.1)",
            "shadow_color_hover": "rgba(255, 255, 255, 0.2)",
            "success_bg": "#1a4a1a",
            "success_text": "#66ff66",
            "warning_bg": "#4a4a1a",
            "warning_text": "#ffff66",
            "danger_bg": "#4a1a1a",
            "danger_text": "#ff6666",
            "info_bg": "#1a3a4a",
            "info_text": "#66ccff"
        },
        "light": {
            "bg": "#ffffff",
            "text": "#000000",
            "secondary_text": "#666666",
            "card_bg": "#ffffff",
            "border_color": "#e0e0e0",
            "btn_bg": "#f8f9fa",
            "btn_text": "#000000",
            "btn_hover": "#e9ecef",
            "input_bg": "#ffffff",
            "badge_bg": "#f8f9fa",
            "resource_bg": "#f8f9fa",
            "progress_bg": "#e9ecef",
            "spinner_bg": "#f3f3f3",
            "shadow_color": "rgba(0, 0, 0, 0.1)",
            "shadow_color_hover": "rgba(0, 0, 0, 0.15)",
            "success_bg": "#d4edda",
            "success_text": "#155724",
            "warning_bg": "#fff3cd",
            "warning_text": "#856404",
            "danger_bg": "#f8d7da",
            "danger_text": "#721c24",
            "info_bg": "#d1ecf1",
            "info_text": "#0c5460"
        }
    }[theme]

    st.markdown(f"""
    <style>
    /* Main app background */
    .stApp {{
        background-color: {colors["bg"]} !important;
        color: {colors["text"]} !important;
    }}
    
    /* CSS Variables for consistent theming */
    :root {{
        --bg-color: {colors["bg"]};
        --text-color: {colors["text"]};
        --secondary-text: {colors["secondary_text"]};
        --card-bg: {colors["card_bg"]};
        --border-color: {colors["border_color"]};
        --btn-bg: {colors["btn_bg"]};
        --btn-text: {colors["btn_text"]};
        --btn-hover: {colors["btn_hover"]};
        --input-bg: {colors["input_bg"]};
        --badge-bg: {colors["badge_bg"]};
        --resource-bg: {colors["resource_bg"]};
        --progress-bg: {colors["progress_bg"]};
        --spinner-bg: {colors["spinner_bg"]};
        --shadow-color: {colors["shadow_color"]};
        --shadow-color-hover: {colors["shadow_color_hover"]};
        --success-bg: {colors["success_bg"]};
        --success-text: {colors["success_text"]};
        --warning-bg: {colors["warning_bg"]};
        --warning-text: {colors["warning_text"]};
        --danger-bg: {colors["danger_bg"]};
        --danger-text: {colors["danger_text"]};
        --info-bg: {colors["info_bg"]};
        --info-text: {colors["info_text"]};
    }}
    
    /* Sidebar styling */
    .css-1d391kg, .css-1544g2n {{
        background-color: {colors["card_bg"]} !important;
        color: {colors["text"]} !important;
    }}
    
    /* Main content area */
    .css-18e3th9, .css-1d391kg {{
        background-color: {colors["bg"]} !important;
        color: {colors["text"]} !important;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {colors["text"]} !important;
    }}
    
    /* Paragraphs and text */
    p, div, span {{
        color: {colors["text"]} !important;
    }}
    
    /* Metrics styling */
    [data-testid="metric-container"] {{
        background-color: {colors["card_bg"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border_color"]} !important;
        padding: 10px !important;
        border-radius: 6px !important;
        box-shadow: 0 2px 4px {colors["shadow_color"]} !important;
    }}
    
    [data-testid="metric-container"] > div {{
        color: {colors["text"]} !important;
    }}
    
    [data-testid="metric-container"] label {{
        color: {colors["secondary_text"]} !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: {colors["btn_bg"]} !important;
        color: {colors["btn_text"]} !important;
        border: 1px solid {colors["border_color"]} !important;
        border-radius: 5px !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        background-color: {colors["btn_hover"]} !important;
        color: {colors["btn_text"]} !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* Radio button styling */
    .stRadio > div {{
        background-color: {colors["card_bg"]} !important;
        color: {colors["text"]} !important;
        border-radius: 5px !important;
        padding: 8px !important;
        border: 1px solid {colors["border_color"]} !important;
    }}
    
    .stRadio > div label {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["text"]} !important;
        padding: 8px 12px !important;
        border-radius: 5px !important;
        margin-bottom: 4px !important;
        border: 1px solid {colors["border_color"]} !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}
    
    .stRadio > div label:hover {{
        background-color: {colors["btn_hover"]} !important;
    }}
    
    /* Progress bar styling */
    .stProgress > div > div {{
        background-color: {colors["progress_bg"]} !important;
        border-radius: 10px !important;
    }}
    
    .stProgress > div > div > div {{
        background: #2a3e57;
        border-radius: 10px !important;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background-color: {colors["card_bg"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border_color"]} !important;
        border-radius: 5px !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {colors["card_bg"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border_color"]} !important;
        border-top: none !important;
        border-radius: 0 0 5px 5px !important;
    }}
    
    /* Success/Error/Info boxes */
    .stSuccess {{
        background-color: {colors["success_bg"]} !important;
        color: {colors["success_text"]} !important;
        border: 1px solid {colors["success_text"]} !important;
        border-radius: 5px !important;
    }}
    
    .stError {{
        background-color: {colors["danger_bg"]} !important;
        color: {colors["danger_text"]} !important;
        border: 1px solid {colors["danger_text"]} !important;
        border-radius: 5px !important;
    }}
    
    .stInfo {{
        background-color: {colors["info_bg"]} !important;
        color: {colors["info_text"]} !important;
        border: 1px solid {colors["info_text"]} !important;
        border-radius: 5px !important;
    }}
    
    .stWarning {{
        background-color: {colors["warning_bg"]} !important;
        color: {colors["warning_text"]} !important;
        border: 1px solid {colors["warning_text"]} !important;
        border-radius: 5px !important;
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["text"]} !important;
        border: 1px solid {colors["border_color"]} !important;
    }}
    
    /* Caption text */
    .css-1kyxreq {{
        color: {colors["secondary_text"]} !important;
    }}
    
    /* Spinner styling */
    .stSpinner > div {{
        border-top-color: #007bff !important;
    }}
    
    /* Markdown content */
    .stMarkdown {{
        color: {colors["text"]} !important;
    }}
    
    /* Images */
    .stImage {{
        border-radius: 8px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_performance_color(score: float) -> str:
    """Get color based on performance score"""
    if score >= 0.8:
        return "#28a745"  # Green
    elif score >= 0.6:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def create_gradient_background(color1: str, color2: str) -> str:
    """Create CSS gradient background"""
    return f"background: linear-gradient(135deg, {color1} 0%, {color2} 100%);"