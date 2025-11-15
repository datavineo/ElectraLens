import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import time
import os

# Production-ready API configuration
def get_api_base_url():
    """Determine the API base URL based on environment."""
    # Check environment variables first
    if os.getenv('BACKEND_URL'):
        return os.getenv('BACKEND_URL')
    
    # Check Streamlit secrets for production
    try:
        return st.secrets.get('API_BASE', 'https://electra-lens.vercel.app')
    except FileNotFoundError:
        pass
    
    # Auto-detection for local development
    LOCAL_API = os.getenv('LOCAL_BACKEND', 'http://localhost:8000')
    PROD_API = 'https://electra-lens.vercel.app'
    
    # Try to connect to local backend first
    try:
        response = requests.get(f"{LOCAL_API}/health", timeout=2)
        if response.status_code == 200:
            print(f"[STREAMLIT] Using local backend: {LOCAL_API}")
            return LOCAL_API
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass
    
    print(f"[STREAMLIT] Using production backend: {PROD_API}")
    return PROD_API

API_BASE = get_api_base_url()

# Configure session timeout and connection pooling
session = requests.Session()
from requests.adapters import HTTPAdapter  # type: ignore[import]
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)

st.set_page_config(
    page_title="ElectraLens - Voter Analysis",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

# Apply custom CSS based on theme with professional styling
def apply_theme():
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
            /* Dark Theme - Professional Design */
            .stApp {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #FAFAFA;
            }
            
            /* Remove white margins - Full width content */
            .block-container {
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                max-width: 100% !important;
            }
            
            .main .block-container {
                max-width: 100% !important;
                padding-top: 2rem !important;
            }
            .stSidebar {
                background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
            }
            .stSidebar [data-testid="stSidebarNav"] {
                background: transparent;
            }
            /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: #FAFAFA !important;
                font-weight: 600 !important;
            }
            h1 {
                background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            /* Form Labels */
            .stSelectbox label, .stTextInput label, .stTextArea label, 
            .stNumberInput label, .stDateInput label, .stFileUploader label {
                color: #E0E0E0 !important;
                font-weight: 500 !important;
            }
            /* Metrics */
            div[data-testid="stMetricValue"] {
                color: #4ECDC4 !important;
                font-weight: 700 !important;
            }
            div[data-testid="stMetricLabel"] {
                color: #B0B0B0 !important;
            }
            /* Dataframes and Tables */
            .stDataFrame, [data-testid="stTable"] {
                background-color: #1e2a3a !important;
                border-radius: 10px;
            }
            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            /* Download Button */
            .stDownloadButton > button {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            /* Select boxes and inputs */
            .stSelectbox > div > div {
                background-color: #1e2a3a;
                border-color: #4ECDC4;
                color: #FAFAFA;
            }
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            .stTextArea > div > div > textarea {
                background-color: #1e2a3a !important;
                color: #FAFAFA !important;
                border-color: #4ECDC4 !important;
            }
            /* Expander */
            .streamlit-expanderHeader {
                background-color: #1e2a3a;
                color: #FAFAFA !important;
                border-radius: 8px;
            }
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #1e2a3a;
                color: #B0B0B0;
                border-radius: 8px 8px 0 0;
                padding: 10px 20px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #667eea;
                color: white !important;
            }
            /* Spinner */
            .stSpinner > div {
                border-top-color: #4ECDC4 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            /* Light Theme - Professional Design */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                color: #262730;
            }
            
            /* Remove white margins - Full width content */
            .block-container {
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                max-width: 100% !important;
            }
            
            .main .block-container {
                max-width: 100% !important;
                padding-top: 2rem !important;
            }
            .stSidebar {
                background: linear-gradient(180deg, #ffffff 0%, #f0f2f6 100%);
                box-shadow: 2px 0 10px rgba(0,0,0,0.05);
            }
            /* Headers */
            h1 {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700 !important;
            }
            h2, h3, h4, h5, h6 {
                color: #2c3e50 !important;
                font-weight: 600 !important;
            }
            /* Metrics */
            div[data-testid="stMetricValue"] {
                color: #667eea !important;
                font-weight: 700 !important;
            }
            div[data-testid="stMetricLabel"] {
                color: #7f8c8d !important;
            }
            /* Buttons */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
            }
            /* Download Button */
            .stDownloadButton > button {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white !important;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            /* Dataframes */
            .stDataFrame {
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #e0e0e0;
                color: #666;
                border-radius: 8px 8px 0 0;
                padding: 10px 20px;
            }
            .stTabs [aria-selected="true"] {
                background-color: #667eea;
                color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)

apply_theme()


# ============= LOGIN & AUTHENTICATION =============

def login_page():
    """Display login page."""
    # Hide sidebar, header, and toolbar on login page
    st.markdown("""
    <style>
        /* Hide sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        section[data-testid="stSidebarNav"] {
            display: none;
        }
        
        /* Hide Streamlit header and toolbar */
        header[data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }
        
        /* Hide top toolbar completely */
        div[data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Hide hamburger menu */
        #MainMenu {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* Hide footer */
        footer {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* Hide decoration */
        .stDeployButton {
            display: none !important;
        }
        
        /* Remove ALL top padding and margins */
        .block-container {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        .stApp > header {
            display: none !important;
        }
        
        /* Full height background */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Remove iframe padding */
        iframe {
            margin-top: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom styling for login page
    header_bg = '#1e2936' if st.session_state.theme == 'dark' else '#ffffff'
    header_text = '#ffffff' if st.session_state.theme == 'dark' else '#2c3e50'
    
    st.markdown(f"""
    <style>
        .login-container {{
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: {"rgba(30, 42, 58, 0.95)" if st.session_state.theme == 'dark' else "rgba(255, 255, 255, 0.95)"};
            border-radius: 15px;
            box-shadow: 0 10px 40px {"rgba(0,0,0,0.5)" if st.session_state.theme == 'dark' else "rgba(0,0,0,0.1)"};
        }}
        .login-title {{
            text-align: center;
            color: {header_text};
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .login-subtitle {{
            text-align: center;
            color: {"#94a3b8" if st.session_state.theme == 'dark' else "#64748b"};
            margin-bottom: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">🗳️ ElectraLens</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Voter Management System</p>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    try:
                        # Call JWT login API
                        login_data = {
                            "username": username,
                            "password": password
                        }
                        response = session.post(
                            f'{API_BASE}/auth/login',
                            json=login_data,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            auth_data = response.json()
                            # Store JWT tokens and user info
                            st.session_state.logged_in = True
                            st.session_state.access_token = auth_data['access_token']
                            st.session_state.refresh_token = auth_data['refresh_token']
                            st.session_state.user = auth_data['user']
                            
                            user_name = auth_data['user'].get('full_name') or username
                            st.success(f"✅ Welcome back, {user_name}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    except requests.exceptions.RequestException as e:
                        st.error(f"🔌 Connection error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def logout():
    """Logout user and clear session."""
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.rerun()


def get_auth_headers():
    """Get authorization headers with JWT token."""
    if st.session_state.get('access_token'):
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def refresh_access_token():
    """Refresh access token using refresh token."""
    if not st.session_state.get('refresh_token'):
        return False
    
    try:
        response = session.post(
            f'{API_BASE}/auth/refresh',
            json={"refresh_token": st.session_state.refresh_token},
            timeout=5
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.access_token = token_data['access_token']
            return True
    except:
        pass
    
    return False


def check_permission(required_role='viewer'):
    """Check if user has required permission."""
    if not st.session_state.logged_in or not st.session_state.user:
        return False
    
    user_role = st.session_state.user.get('role', 'viewer')
    
    if required_role == 'admin':
        return user_role == 'admin'
    
    return True  # Viewer can access viewer-level content


# Helper function to style plotly charts based on theme
def style_plotly_chart(fig):
    if st.session_state.theme == 'dark':
        fig.update_layout(
            plot_bgcolor='rgba(30, 42, 58, 0.8)',
            paper_bgcolor='rgba(26, 26, 46, 0)',
            font=dict(color='#FAFAFA', family='Arial, sans-serif'),
            title_font=dict(color='#4ECDC4', size=18, family='Arial, sans-serif'),
            xaxis=dict(
                gridcolor='rgba(78, 205, 196, 0.1)',
                color='#E0E0E0',
                linecolor='#4ECDC4',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='rgba(78, 205, 196, 0.1)',
                color='#E0E0E0',
                linecolor='#4ECDC4',
                showgrid=True
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode='closest'
        )
    else:
        fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 0.9)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
            font=dict(color='#2c3e50', family='Arial, sans-serif'),
            title_font=dict(color='#667eea', size=18, family='Arial, sans-serif'),
            xaxis=dict(
                gridcolor='rgba(102, 126, 234, 0.1)',
                color='#2c3e50',
                linecolor='#667eea',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='rgba(102, 126, 234, 0.1)',
                color='#2c3e50',
                linecolor='#667eea',
                showgrid=True
            ),
            margin=dict(l=40, r=40, t=60, b=40),
            hovermode='closest'
        )
    return fig

# Enhanced Header Section
header_bg = 'rgba(30, 42, 58, 0.95)' if st.session_state.theme == 'dark' else 'rgba(255, 255, 255, 0.95)'
header_text = '#FAFAFA' if st.session_state.theme == 'dark' else '#2c3e50'
header_shadow = '0 4px 20px rgba(0, 0, 0, 0.3)' if st.session_state.theme == 'dark' else '0 2px 15px rgba(0, 0, 0, 0.1)'

st.markdown(f"""
<style>
    /* Enhanced Header Styling */
    [data-testid="stHeader"] {{
        background: {header_bg};
        backdrop-filter: blur(10px);
        box-shadow: {header_shadow};
        border-bottom: 2px solid {"#4ECDC4" if st.session_state.theme == 'dark' else "#667eea"};
    }}
    
    /* Main Title Enhancement */
    .main-header {{
        background: {header_bg};
        padding: 1.5rem 2rem;
        border-radius: 15px;
        box-shadow: {header_shadow};
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 2px solid {"#4ECDC4" if st.session_state.theme == 'dark' else "#667eea"};
    }}
    
    .title-text {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, {"#4ECDC4 0%, #FF6B6B 100%" if st.session_state.theme == 'dark' else "#667eea 0%, #764ba2 100%"});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    
    .title-icon {{
        font-size: 3rem;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
    }}
    
    /* Subheader Enhancement */
    .subtitle-text {{
        color: {"#B0B0B0" if st.session_state.theme == 'dark' else "#7f8c8d"};
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }}
</style>
""", unsafe_allow_html=True)

# Clean, Modern Sidebar Design (only shown after login)
with st.sidebar:
    # Cleaner sidebar styling
    sidebar_bg = '#1e2936' if st.session_state.theme == 'dark' else '#f8f9fa'
    sidebar_text = '#ffffff' if st.session_state.theme == 'dark' else '#2c3e50'
    accent_color = '#6366f1' if st.session_state.theme == 'dark' else '#6366f1'
    
    st.markdown(f"""
    <style>
        /* Clean Sidebar Background with Reduced Width */
        [data-testid="stSidebar"] {{
            background: {sidebar_bg};
            padding-top: 1rem;
            min-width: 240px !important;
            max-width: 240px !important;
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            width: 240px !important;
        }}
        
        /* Navigation Menu Buttons */
        .nav-button {{
            background: {"rgba(255,255,255,0.05)" if st.session_state.theme == 'dark' else "rgba(0,0,0,0.03)"};
            border-left: 4px solid transparent;
            padding: 1rem 1.2rem;
            margin: 0.4rem 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: {sidebar_text};
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .nav-button:hover {{
            background: {"rgba(99,102,241,0.15)" if st.session_state.theme == 'dark' else "rgba(99,102,241,0.1)"};
            border-left-color: {accent_color};
            transform: translateX(5px);
        }}
        
        .nav-button-active {{
            background: {"rgba(99,102,241,0.2)" if st.session_state.theme == 'dark' else "rgba(99,102,241,0.15)"};
            border-left-color: {accent_color};
            font-weight: 700;
        }}
        
        /* Theme Toggle - Compact and Clean */
        .theme-toggle-compact {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: calc(var(--sidebar-width) - 40px);
            max-width: 280px;
            z-index: 999;
        }}
        
        .stSidebar .stButton > button {{
            background: {accent_color};
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            font-weight: 600;
            font-size: 0.95rem;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(99,102,241,0.3);
        }}
        
        .stSidebar .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99,102,241,0.4);
            background: {"#7c3aed" if st.session_state.theme == 'dark' else "#4f46e5"};
        }}
        
        /* Hide default selectbox - we'll use radio instead */
        .stSidebar .stSelectbox {{
            display: none;
        }}
        
        /* Radio button styling for navigation - Enhanced visibility */
        .stSidebar .stRadio > label {{
            color: {sidebar_text};
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }}
        
        .stSidebar .stRadio [role="radiogroup"] {{
            gap: 0.5rem;
        }}
        
        .stSidebar .stRadio [role="radio"] {{
            background: {"rgba(255,255,255,0.1)" if st.session_state.theme == 'dark' else "rgba(0,0,0,0.03)"};
            padding: 0.9rem 1.1rem;
            border-radius: 10px;
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
            color: {"#ffffff" if st.session_state.theme == 'dark' else sidebar_text} !important;
            border: {"1px solid rgba(255,255,255,0.1)" if st.session_state.theme == 'dark' else "1px solid rgba(0,0,0,0.05)"};
        }}
        
        .stSidebar .stRadio [role="radio"] label {{
            color: {"#ffffff" if st.session_state.theme == 'dark' else sidebar_text} !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px !important;
            text-shadow: {"0 1px 2px rgba(0,0,0,0.5)" if st.session_state.theme == 'dark' else "none"} !important;
        }}
        
        .stSidebar .stRadio [role="radio"] * {{
            color: {"#ffffff" if st.session_state.theme == 'dark' else sidebar_text} !important;
            font-weight: 700 !important;
        }}
        
        .stSidebar .stRadio [role="radio"]:hover {{
            background: {"rgba(99,102,241,0.25)" if st.session_state.theme == 'dark' else "rgba(99,102,241,0.1)"};
            border-left-color: {accent_color};
            border-color: {accent_color};
            transform: translateX(3px);
        }}
        
        .stSidebar .stRadio [role="radio"][aria-checked="true"] {{
            background: {"rgba(99,102,241,0.35)" if st.session_state.theme == 'dark' else "rgba(99,102,241,0.15)"};
            border-left-color: {accent_color};
            border-color: {accent_color};
            font-weight: 700;
            box-shadow: 0 2px 8px {"rgba(99,102,241,0.3)" if st.session_state.theme == 'dark' else "rgba(99,102,241,0.2)"};
        }}
        
        .stSidebar .stRadio [role="radio"][aria-checked="true"] label {{
            color: {"#ffffff" if st.session_state.theme == 'dark' else sidebar_text} !important;
            font-weight: 700 !important;
        }}
        
        /* ===== RESPONSIVE DESIGN FOR ALL DEVICES ===== */
        
        /* Mobile Phones (Portrait) - up to 480px */
        @media only screen and (max-width: 480px) {{
            .stApp {{
                padding: 0 !important;
            }}
            
            /* Sidebar adjustments */
            .stSidebar {{
                width: 100% !important;
            }}
            
            /* Header text smaller */
            h1 {{
                font-size: 1.5rem !important;
            }}
            
            h2 {{
                font-size: 1.2rem !important;
            }}
            
            h3 {{
                font-size: 1rem !important;
            }}
            
            /* Metrics stack vertically */
            div[data-testid="stMetricValue"] {{
                font-size: 1.2rem !important;
            }}
            
            /* Radio buttons more compact */
            .stSidebar .stRadio [role="radio"] {{
                padding: 0.6rem 0.8rem !important;
                font-size: 0.85rem !important;
            }}
            
            /* Buttons full width */
            .stButton > button {{
                width: 100% !important;
                padding: 0.6rem 0.8rem !important;
                font-size: 0.9rem !important;
            }}
            
            /* Forms full width */
            .stTextInput, .stSelectbox, .stNumberInput {{
                width: 100% !important;
            }}
            
            /* Charts responsive */
            .js-plotly-plot {{
                width: 100% !important;
                height: auto !important;
            }}
            
            /* Dataframe scroll */
            .stDataFrame {{
                overflow-x: auto !important;
                max-width: 100vw !important;
            }}
            
            /* Column spacing */
            .row-widget.stHorizontal {{
                flex-direction: column !important;
            }}
            
            /* File uploader compact */
            .stFileUploader {{
                font-size: 0.85rem !important;
            }}
        }}
        
        /* Mobile Phones (Landscape) & Small Tablets - 481px to 768px */
        @media only screen and (min-width: 481px) and (max-width: 768px) {{
            .stApp {{
                padding: 0.5rem !important;
            }}
            
            h1 {{
                font-size: 1.8rem !important;
            }}
            
            h2 {{
                font-size: 1.4rem !important;
            }}
            
            /* Sidebar width */
            .stSidebar {{
                min-width: 250px !important;
            }}
            
            /* Radio buttons */
            .stSidebar .stRadio [role="radio"] {{
                padding: 0.7rem 0.9rem !important;
            }}
            
            /* Metrics */
            div[data-testid="stMetricValue"] {{
                font-size: 1.5rem !important;
            }}
            
            /* Buttons */
            .stButton > button {{
                padding: 0.65rem 1rem !important;
            }}
            
            /* Charts */
            .js-plotly-plot {{
                height: 350px !important;
            }}
            
            /* 2-column layout becomes 1 on smaller tablets */
            .row-widget.stHorizontal > div {{
                flex: 1 1 100% !important;
            }}
        }}
        
        /* Tablets (Portrait & Landscape) - 769px to 1024px */
        @media only screen and (min-width: 769px) and (max-width: 1024px) {{
            .stApp {{
                padding: 1rem !important;
            }}
            
            h1 {{
                font-size: 2rem !important;
            }}
            
            /* Sidebar */
            .stSidebar {{
                min-width: 280px !important;
            }}
            
            /* Metrics */
            div[data-testid="stMetricValue"] {{
                font-size: 1.8rem !important;
            }}
            
            /* Charts optimal height */
            .js-plotly-plot {{
                height: 400px !important;
            }}
            
            /* 2-column layout maintained */
            .row-widget.stHorizontal > div {{
                flex: 1 1 48% !important;
                margin: 0 1% !important;
            }}
        }}
        
        /* Laptops & Small Desktops - 1025px to 1366px */
        @media only screen and (min-width: 1025px) and (max-width: 1366px) {{
            .stApp {{
                padding: 1.5rem !important;
            }}
            
            /* Sidebar */
            .stSidebar {{
                min-width: 300px !important;
            }}
            
            /* Charts */
            .js-plotly-plot {{
                height: 450px !important;
            }}
            
            /* Maintain 2-column layout */
            .row-widget.stHorizontal > div {{
                flex: 1 1 48% !important;
            }}
        }}
        
        /* Large Desktops - 1367px and above */
        @media only screen and (min-width: 1367px) {{
            .stApp {{
                max-width: 1400px !important;
                margin: 0 auto !important;
                padding: 2rem !important;
            }}
            
            /* Sidebar optimal width */
            .stSidebar {{
                min-width: 320px !important;
            }}
            
            /* Charts large */
            .js-plotly-plot {{
                height: 500px !important;
            }}
        }}
        
        /* Universal responsive rules */
        @media only screen and (max-width: 768px) {{
            /* Collapse sidebar by default on mobile */
            [data-testid="collapsedControl"] {{
                display: block !important;
            }}
            
            /* Adjust padding for mobile */
            .block-container {{
                padding: 1rem !important;
            }}
            
            /* Tables scroll horizontally */
            table {{
                display: block !important;
                overflow-x: auto !important;
                white-space: nowrap !important;
            }}
            
            /* Images responsive */
            img {{
                max-width: 100% !important;
                height: auto !important;
            }}
        }}
        
        /* Touch-friendly interactions */
        @media (hover: none) and (pointer: coarse) {{
            /* Increase tap targets for mobile */
            .stButton > button,
            .stRadio [role="radio"],
            .stCheckbox {{
                min-height: 44px !important;
                min-width: 44px !important;
            }}
            
            /* Remove hover effects on touch devices */
            .stButton > button:hover {{
                transform: none !important;
            }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Clean Navigation Header
    st.markdown(f'<p style="color: {sidebar_text}; font-weight: 700; margin-top: 0.5rem; margin-bottom: 1rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; padding-left: 0.5rem;">📋 Menu</p>', unsafe_allow_html=True)


# ============= MAIN APP LOGIC =============

# Check if user is logged in
if not st.session_state.logged_in:
    # Show login page
    login_page()
    st.stop()

# User is logged in - show the app
user_role = st.session_state.user.get('role', 'viewer') if st.session_state.user else 'viewer'  # type: ignore
username = st.session_state.user.get('username', 'User') if st.session_state.user else 'User'  # type: ignore
full_name = st.session_state.user.get('full_name', username) if st.session_state.user else username  # type: ignore

# Sidebar navigation with user info
with st.sidebar:
    st.markdown(f"""
    <div style='padding: 1rem; background: {"rgba(255,255,255,0.05)" if st.session_state.theme == 'dark' else "rgba(0,0,0,0.03)"}; border-radius: 10px; margin-bottom: 1rem;'>
        <p style='margin: 0; color: {sidebar_text}; font-size: 0.85rem;'>👤 <strong>{full_name}</strong></p>
        <p style='margin: 0; color: {"#94a3b8" if st.session_state.theme == 'dark' else "#64748b"}; font-size: 0.75rem;'>Role: {user_role.title()}</p>
    </div>
    """, unsafe_allow_html=True)

# Navigation menu (admin sees all options, viewers see limited)
if user_role == 'admin':
    nav_options = ['📊 Summary', '👥 Voters', '📤 Upload PDF', '➕ Add Voter', '🔍 Search & Filter', '👥 User Management']
else:
    nav_options = ['📊 Summary', '👥 Voters', '🔍 Search & Filter']

tab = st.sidebar.radio(
    "nav",
    nav_options,
    label_visibility="collapsed"
)

# Logout button and Theme toggle at bottom of sidebar
with st.sidebar:
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Logout button
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        logout()
    
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Theme toggle
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_label = f"{theme_icon} {'Dark' if st.session_state.theme == 'light' else 'Light'} Mode"
    
    if st.button(theme_label, key="theme_toggle", use_container_width=True):
        st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
        st.rerun()

# Main content header
header_bg = '#1e2936' if st.session_state.theme == 'dark' else '#ffffff'
header_text = '#ffffff' if st.session_state.theme == 'dark' else '#2c3e50'
subtitle_text = '#94a3b8' if st.session_state.theme == 'dark' else '#64748b'

st.markdown(f"""
<div style="
    background: {header_bg};
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 5px solid #6366f1;
">
    <h1 style="
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: {header_text};
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <span style="font-size: 2rem;">🗳️</span>
        Voter Analysis Dashboard
    </h1>
    <p style="
        margin: 0.5rem 0 0 0;
        color: {subtitle_text};
        font-size: 0.95rem;
    ">
        Comprehensive voter data management & analytics
    </p>
</div>
""", unsafe_allow_html=True)

if tab == '📊 Summary':
    # Display key metrics at the top
    with st.spinner('Loading summary data...'):
        headers = get_auth_headers()
        resp = session.get(f'{API_BASE}/voters/summary', headers=headers, timeout=5)
        
        if resp.status_code == 401:
            if refresh_access_token():
                headers = get_auth_headers()
                resp = session.get(f'{API_BASE}/voters/summary', headers=headers, timeout=5)
        
        if resp.status_code != 200:
            st.error("Failed to load summary data. Please check your authentication.")
            st.stop()
            
        data = resp.json()
        df = pd.DataFrame(data)
        
        # Get total voters
        total_voters = df['count'].sum() if not df.empty else 0
        
        # Get gender data
        gr_resp = session.get(f'{API_BASE}/voters/gender-ratio', headers=headers, timeout=5)
        if gr_resp.status_code == 200:
            gr = gr_resp.json()
        else:
            gr = {}
        male_count = gr.get('M', 0)
        female_count = gr.get('F', 0)
        
        # Get age data
        ages = session.get(f'{API_BASE}/voters/age-distribution', timeout=5).json()
        youth_count = ages.get('18-30', 0)
    
    # Key metrics cards
    st.markdown("### 📊 Key Metrics")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(label="👥 Total Voters", value=f"{total_voters:,}")
    
    with metric_col2:
        st.metric(label="👨 Male Voters", value=f"{male_count:,}")
    
    with metric_col3:
        st.metric(label="👩 Female Voters", value=f"{female_count:,}")
    
    with metric_col4:
        st.metric(label="🎓 Youth (18-30)", value=f"{youth_count:,}")
    
    st.markdown("---")
    
    # Constituency chart - Full width
    st.markdown("### 📍 Voters by Constituency")
    if not df.empty:
        fig = px.bar(
            df, 
            x='constituency', 
            y='count',
            title='',
            labels={'constituency': 'Constituency', 'count': 'Number of Voters'},
            color='count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No constituency data available")
    
    st.markdown("---")
    
    # Two column layout for demographics
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### 👥 Gender Distribution")
        labels = list(gr.keys())
        values = list(gr.values())
        fig2 = px.pie(
            values=values, 
            names=labels,
            title='',
            hole=0.4,
            color_discrete_sequence=['#6366f1', '#ec4899', '#10b981']
        )
        fig2.update_layout(height=400)
        fig2 = style_plotly_chart(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("### 📅 Age Distribution")
        adf = pd.DataFrame(list(ages.items()), columns=['age_range','count'])
        # Sort age ranges
        age_order = ['0-17', '18-30', '31-45', '46-60', '61+']
        adf['age_range'] = pd.Categorical(adf['age_range'], categories=age_order, ordered=True)
        adf = adf.sort_values('age_range')
        
        fig3 = px.bar(
            adf, 
            x='age_range', 
            y='count',
            title='',
            labels={'age_range': 'Age Range', 'count': 'Number of Voters'},
            color='count',
            color_continuous_scale='Purples'
        )
        fig3.update_layout(height=400, showlegend=False)
        fig3 = style_plotly_chart(fig3)
        st.plotly_chart(fig3, use_container_width=True)

elif tab == '👥 Voters':
    # Fetch constituency options for filter
    if 'constituency_options' not in st.session_state:
        try:
            resp_summary = session.get(f'{API_BASE}/voters/summary', timeout=5)
            if resp_summary.status_code == 200:
                summary_data = resp_summary.json()
                st.session_state.constituency_options = ['All'] + [item['constituency'] for item in summary_data if item.get('constituency')]
            else:
                st.session_state.constituency_options = ['All']
        except:
            st.session_state.constituency_options = ['All']
    
    # Add advanced filters in expander
    with st.expander("🔍 Advanced Filters", expanded=False):
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            filter_constituency = st.multiselect('Constituency', options=st.session_state.constituency_options, default=['All'])
        
        with filter_col2:
            filter_gender = st.multiselect('Gender', options=['All', 'M', 'F'], default=['All'])
        
        with filter_col3:
            filter_age_min = st.number_input('Min Age', min_value=0, max_value=150, value=0)
            filter_age_max = st.number_input('Max Age', min_value=0, max_value=150, value=150)
        
        with filter_col4:
            filter_booth = st.text_input('Booth No (partial match)', value='')
            filter_voting_status = st.selectbox('Voting Status', ['All', 'Voted', 'Not Voted'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        page = st.number_input('Page', min_value=0, value=0)
    with col2:
        limit = st.number_input('Page size', min_value=10, max_value=100, value=50)
    with col3:
        search_query = st.text_input('🔍 Quick Search', placeholder='Name, constituency, booth...')
    
    # If search query is provided, use search endpoint
    if search_query and search_query.strip():
        with st.spinner('Searching...'):
            resp = session.get(f'{API_BASE}/voters/search', params={'q': search_query, 'limit': 500}, timeout=10)
            if resp.status_code == 200:
                voters = resp.json()
                st.info(f'Found {len(voters)} matching voters')
            else:
                st.error(f'Search error: {resp.json()}')
                voters = []
    else:
        # Normal pagination
        resp = session.get(f'{API_BASE}/voters', params={'skip': page*limit, 'limit': limit}, timeout=10)
        if resp.status_code == 200:
            voters = resp.json()
        else:
            st.error(f'Error fetching voters: {resp.json()}')
            voters = []
    
    df = pd.DataFrame(voters)
    
    if not df.empty:
        # Apply multiple filters
        filtered_df = df.copy()
        
        # Filter by constituency
        if 'All' not in filter_constituency and filter_constituency:
            filtered_df = filtered_df[filtered_df['constituency'].isin(filter_constituency)]
        
        # Filter by gender
        if 'All' not in filter_gender and filter_gender:
            filtered_df = filtered_df[filtered_df['gender'].isin(filter_gender)]
        
        # Filter by age range
        if filter_age_min > 0 or filter_age_max < 150:
            filtered_df = filtered_df[
                (filtered_df['age'].fillna(0) >= filter_age_min) & 
                (filtered_df['age'].fillna(0) <= filter_age_max)
            ]
        
        # Filter by booth number
        if filter_booth:
            filtered_df = filtered_df[filtered_df['booth_no'].str.contains(filter_booth, case=False, na=False)]
        
        # Filter by voting status
        if filter_voting_status == 'Voted':
            filtered_df = filtered_df[filtered_df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
        elif filter_voting_status == 'Not Voted':
            filtered_df = filtered_df[~filtered_df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
        
        df = filtered_df
        
        # Display summary stats
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric('Total Records', len(df))
        with col2:
            st.metric('Average Age', f"{df['age'].fillna(0).mean():.1f}")
        with col3:
            male_count = (df['gender'] == 'M').sum()
            st.metric('Males', male_count)
        with col4:
            female_count = (df['gender'] == 'F').sum()
            st.metric('Females', female_count)
        with col5:
            voted_count = df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes']).sum()
            st.metric('Voting Count', voted_count)
        
        st.divider()
        
        # Add Save All button
        col_header, col_save_all = st.columns([4, 1])
        with col_header:
            st.subheader(f'📋 Voters List (showing {len(df)} records)')
        with col_save_all:
            if st.button('💾 Save All Changes', use_container_width=True, type='primary'):
                with st.spinner('Saving all changes...'):
                    # Collect all updates
                    updates = []
                    for idx, row in df.iterrows():
                        vote_key = f"vote_{row['id']}"
                        if vote_key in st.session_state:
                            updates.append((row['id'], st.session_state[vote_key]))
                    
                    # Parallel execution for faster saves
                    def save_voter(voter_data):
                        voter_id, vote_status = voter_data
                        try:
                            r = session.put(f'{API_BASE}/voters/{voter_id}', 
                                          json={'vote': vote_status}, 
                                          timeout=5)
                            return r.status_code == 200
                        except:
                            return False
                    
                    success_count = 0
                    error_count = 0
                    
                    # Use ThreadPoolExecutor for parallel requests
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = list(executor.map(save_voter, updates))
                        success_count = sum(results)
                        error_count = len(results) - success_count
                    
                    if error_count == 0:
                        st.toast(f'✅ All {success_count} records saved successfully!', icon='✔️')
                    else:
                        st.toast(f'⚠️ Saved {success_count} records, {error_count} errors', icon='⚠️')
        
        # Display column headers
        col_id, col_name, col_age, col_gender, col_constituency, col_booth, col_address, col_vote = st.columns([0.6, 1.8, 0.7, 0.6, 1.2, 0.8, 1.5, 0.8])
        with col_id:
            st.markdown("**ID**")
        with col_name:
            st.markdown("**Name**")
        with col_age:
            st.markdown("**Age**")
        with col_gender:
            st.markdown("**Gender**")
        with col_constituency:
            st.markdown("**Constituency**")
        with col_booth:
            st.markdown("**Booth**")
        with col_address:
            st.markdown("**Address**")
        with col_vote:
            st.markdown("**Voted**")
        
        st.markdown("---")
        
        # Display inline editing rows
        for idx, row in df.iterrows():
            col_id, col_name, col_age, col_gender, col_constituency, col_booth, col_address, col_vote = st.columns([0.6, 1.8, 0.7, 0.6, 1.2, 0.8, 1.5, 0.8])
            
            with col_id:
                st.text(f"#{row['id']}")
            
            # Read-only fields (displayed as text)
            with col_name:
                st.text(row.get('name', ''))
            
            with col_age:
                st.text(str(int(row.get('age', 0)) if row.get('age') and not (isinstance(row.get('age'), float) and pd.isna(row.get('age'))) else 0))
            
            with col_gender:
                st.text(row.get('gender', ''))
            
            with col_constituency:
                st.text(row.get('constituency', ''))
            
            with col_booth:
                st.text(row.get('booth_no', ''))
            
            with col_address:
                st.text(row.get('address', ''))
            
            # Editable vote column - Use session state to track changes
            with col_vote:
                vote_key = f"vote_{row['id']}"
                if vote_key not in st.session_state:
                    vote_value = row.get('vote', False)
                    if isinstance(vote_value, str):
                        vote_value = vote_value.lower() in ['true', '1', 'yes']
                    st.session_state[vote_key] = bool(vote_value)
                
                new_vote = st.checkbox('✓', value=st.session_state[vote_key], key=vote_key, label_visibility='collapsed')
    else:
        st.info('No voters found')

elif tab == '📤 Upload PDF':
    st.subheader('Upload PDF with Voter Data')
    st.info('📋 Supported formats: PDF files with tables containing voter information')
    
    uploaded = st.file_uploader('Upload PDF', type=['pdf'])
    if uploaded:
        with st.spinner('Processing PDF...'):
            files = {'file': (uploaded.name, uploaded.getvalue(), 'application/pdf')}
            r = session.post(f'{API_BASE}/upload_pdf', files=files, timeout=60)
            if r.status_code == 200:
                st.success('✅ PDF uploaded and processed successfully!')
                st.json(r.json())
            else:
                st.error(f'❌ Error: {r.json()}')

elif tab == '➕ Add Voter':
    st.subheader('Add New Voter')
    with st.form('add_voter_form'):
        name = st.text_input('Full Name *')
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input('Age', min_value=18, max_value=130, value=30)
        with col2:
            gender = st.selectbox('Gender', ['M', 'F'])
        
        constituency = st.text_input('Constituency *')
        booth_no = st.text_input('Booth No *')
        address = st.text_area('Address')
        
        submitted = st.form_submit_button('✅ Create Voter', use_container_width=True)
        if submitted:
            if not name or not constituency or not booth_no:
                st.error('❌ Please fill in all required fields (marked with *)')
            else:
                payload = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'constituency': constituency,
                    'booth_no': booth_no,
                    'address': address
                }
                r = session.post(f'{API_BASE}/voters', json=payload, timeout=5)
                if r.status_code == 200:
                    st.success('✅ Voter created successfully!')
                    st.json(r.json())
                else:
                    st.error(f'❌ Error: {r.json()}')

elif tab == '🔍 Search & Filter':
    st.subheader('Search & Filter Voters')
    
    search_type = st.selectbox('Select operation:', [
        'Full Text Search', 
        'Find Duplicates by Name',
        'Multi-Filter Search',
        'Filter by Constituency', 
        'Filter by Gender', 
        'Filter by Age Range'
    ])
    
    if search_type == 'Full Text Search':
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input('Search by name, constituency, or booth number')
        with col2:
            search_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if query:
            with st.spinner('Searching...'):
                r = session.get(f'{API_BASE}/voters/search', params={'q': query, 'limit': search_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} results')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Find Duplicates by Name':
        st.info('🔍 This will find all voters with duplicate names (case-insensitive)')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button('🔎 Find Duplicates', type='primary', use_container_width=True):
                with st.spinner('Searching for duplicates...'):
                    # Fetch all voters
                    r = session.get(f'{API_BASE}/voters', params={'skip': 0, 'limit': 10000}, timeout=30)
                    if r.status_code == 200:
                        all_voters = r.json()
                        df = pd.DataFrame(all_voters)
                        
                        if not df.empty:
                            # Find duplicates based on name (case-insensitive)
                            df['name_lower'] = df['name'].str.lower().str.strip()
                            duplicates = df[df.duplicated(subset=['name_lower'], keep=False)].copy()
                            duplicates = duplicates.sort_values('name_lower')
                            duplicates = duplicates.drop(columns=['name_lower'])
                            
                            if not duplicates.empty:
                                st.warning(f'⚠️ Found {len(duplicates)} duplicate records ({len(duplicates["name"].unique())} unique names)')
                                
                                # Show summary
                                duplicate_summary = duplicates.groupby(duplicates['name'].str.lower()).size().reset_index(name='count')
                                duplicate_summary.columns = ['Name', 'Occurrences']
                                duplicate_summary = duplicate_summary.sort_values('Occurrences', ascending=False)
                                
                                st.subheader('📊 Duplicate Names Summary')
                                st.dataframe(duplicate_summary, use_container_width=True, hide_index=True)
                                
                                st.subheader('📋 All Duplicate Records')
                                st.dataframe(duplicates, use_container_width=True, hide_index=True)
                                
                                # Export option
                                csv = duplicates.to_csv(index=False)
                                st.download_button(
                                    label='📥 Download Duplicates as CSV',
                                    data=csv,
                                    file_name='duplicate_voters.csv',
                                    mime='text/csv'
                                )
                            else:
                                st.success('✅ No duplicate names found!')
                        else:
                            st.info('No voters found in database')
                    else:
                        st.error(f'Error fetching voters: {r.json()}')
        
        with col2:
            st.metric('Status', 'Ready')
    
    elif search_type == 'Multi-Filter Search':
        st.info('🎯 Apply multiple filters simultaneously')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_gender = st.selectbox('Gender', ['All', 'M', 'F'])
            filter_constituency = st.text_input('Constituency (partial)')
        
        with col2:
            filter_age_min = st.number_input('Min Age', min_value=0, max_value=150, value=0)
            filter_age_max = st.number_input('Max Age', min_value=0, max_value=150, value=150)
        
        with col3:
            filter_booth = st.text_input('Booth No (partial)')
            filter_vote_status = st.selectbox('Voting Status', ['All', 'Voted', 'Not Voted'])
        
        if st.button('🔍 Apply Filters', type='primary'):
            with st.spinner('Filtering...'):
                # Fetch voters
                r = session.get(f'{API_BASE}/voters', params={'skip': 0, 'limit': 5000}, timeout=20)
                if r.status_code == 200:
                    results = r.json()
                    df = pd.DataFrame(results)
                    
                    if not df.empty:
                        # Apply filters
                        if filter_gender != 'All':
                            df = df[df['gender'] == filter_gender]
                        
                        if filter_constituency:
                            df = df[df['constituency'].str.contains(filter_constituency, case=False, na=False)]
                        
                        if filter_age_min > 0 or filter_age_max < 150:
                            df = df[(df['age'].fillna(0) >= filter_age_min) & (df['age'].fillna(0) <= filter_age_max)]
                        
                        if filter_booth:
                            df = df[df['booth_no'].str.contains(filter_booth, case=False, na=False)]
                        
                        if filter_vote_status == 'Voted':
                            df = df[df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
                        elif filter_vote_status == 'Not Voted':
                            df = df[~df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
                        
                        st.success(f'✅ Found {len(df)} matching voters')
                        if not df.empty:
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # Export option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label='📥 Download Results as CSV',
                                data=csv,
                                file_name='filtered_voters.csv',
                                mime='text/csv'
                            )
                        else:
                            st.info('No voters match the selected criteria')
                    else:
                        st.info('No voters found')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Constituency':
        col1, col2 = st.columns([3, 1])
        with col1:
            constituency = st.text_input('Enter constituency name (partial match)')
        with col2:
            const_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if constituency:
            with st.spinner('Filtering...'):
                r = session.get(f'{API_BASE}/voters/filter/constituency', params={'constituency': constituency, 'limit': const_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} voters')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button('📥 Download CSV', csv, f'constituency_{constituency}.csv', 'text/csv')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Gender':
        col1, col2 = st.columns([3, 1])
        with col1:
            gender = st.selectbox('Select gender', ['M', 'F'])
        with col2:
            gender_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if st.button('🔍 Filter', type='primary'):
            with st.spinner('Filtering...'):
                r = session.get(f'{API_BASE}/voters/filter/gender', params={'gender': gender, 'limit': gender_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} voters')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button('📥 Download CSV', csv, f'gender_{gender}.csv', 'text/csv')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Age Range':
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            min_age = st.number_input('Minimum age', min_value=0, max_value=150, value=18)
        with col2:
            max_age = st.number_input('Maximum age', min_value=0, max_value=150, value=80)
        with col3:
            age_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if st.button('🔍 Apply Filter', type='primary'):
            if min_age > max_age:
                st.error('❌ Minimum age cannot be greater than maximum age')
            else:
                with st.spinner('Filtering...'):
                    r = session.get(f'{API_BASE}/voters/filter/age-range', 
                                   params={'min_age': min_age, 'max_age': max_age, 'limit': age_limit}, timeout=10)
                    if r.status_code == 200:
                        results = r.json()
                        st.success(f'Found {len(results)} voters')
                        if results:
                            df = pd.DataFrame(results)
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            csv = df.to_csv(index=False)
                            st.download_button('📥 Download CSV', csv, f'age_{min_age}-{max_age}.csv', 'text/csv')
                    else:
                        st.error(f'Error: {r.json()}')

elif tab == '👥 User Management':
    # Admin-only section
    if not check_permission('admin'):
        st.error("🚫 Access Denied: Admin privileges required")
        st.stop()
    
    st.subheader('👥 User Management')
    
    # Tabs for user management
    user_tab = st.tabs(['📋 All Users', '➕ Create User', '✏️ Edit Users'])
    
    # Tab 1: View All Users
    with user_tab[0]:
        st.markdown('### 📋 All Users')
        
        try:
            response = session.get(f'{API_BASE}/auth/users', timeout=5)
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    # Display as dataframe
                    df_users = pd.DataFrame(users)
                    
                    # Format columns
                    display_cols = ['id', 'username', 'full_name', 'role', 'is_active', 'created_at', 'last_login']
                    df_display = df_users[display_cols].copy()
                    
                    # Format datetime columns
                    if 'created_at' in df_display.columns:
                        df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                    if 'last_login' in df_display.columns:
                        df_display['last_login'] = pd.to_datetime(df_display['last_login']).dt.strftime('%Y-%m-%d %H:%M')
                    
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    st.metric("Total Users", len(users))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        admin_count = len([u for u in users if u['role'] == 'admin'])
                        st.metric("Admins", admin_count)
                    with col2:
                        viewer_count = len([u for u in users if u['role'] == 'viewer'])
                        st.metric("Viewers", viewer_count)
                    with col3:
                        active_count = len([u for u in users if u['is_active']])
                        st.metric("Active", active_count)
                else:
                    st.info("No users found")
            else:
                st.error(f"Failed to fetch users: {response.json()}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Tab 2: Create New User
    with user_tab[1]:
        st.markdown('### ➕ Create New User')
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username*", placeholder="Enter username")
                new_password = st.text_input("Password*", type="password", placeholder="Enter password")
            
            with col2:
                new_full_name = st.text_input("Full Name", placeholder="Enter full name (optional)")
                new_role = st.selectbox("Role*", options=['viewer', 'admin'])
            
            submit_create = st.form_submit_button("➕ Create User", type="primary", use_container_width=True)
            
            if submit_create:
                if not new_username or not new_password:
                    st.error("⚠️ Username and Password are required")
                elif len(new_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters")
                else:
                    try:
                        response = session.post(
                            f'{API_BASE}/auth/users',
                            params={
                                'username': new_username,
                                'password': new_password,
                                'full_name': new_full_name,
                                'role': new_role
                            },
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            st.success(f"✅ User '{new_username}' created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            error_msg = response.json().get('detail', 'Unknown error')
                            st.error(f"❌ Failed to create user: {error_msg}")
                    except Exception as e:
                        st.error(f"🔌 Connection error: {str(e)}")
    
    # Tab 3: Edit Users
    with user_tab[2]:
        st.markdown('### ✏️ Edit Users')
        
        try:
            response = session.get(f'{API_BASE}/auth/users', timeout=5)
            if response.status_code == 200:
                users = response.json()
                
                if users:
                    # Select user to edit
                    user_options = {f"{u['username']} ({u['role']})" : u for u in users}
                    selected_user_label = st.selectbox("Select User to Edit", options=list(user_options.keys()))
                    selected_user = user_options[selected_user_label]
                    
                    st.markdown("---")
                    
                    with st.form("edit_user_form"):
                        st.markdown(f"**Editing User:** {selected_user['username']}")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            edit_full_name = st.text_input("Full Name", value=selected_user.get('full_name', ''))
                        
                        with col2:
                            edit_role = st.selectbox("Role", options=['viewer', 'admin'], 
                                                    index=0 if selected_user['role'] == 'viewer' else 1)
                        
                        with col3:
                            edit_is_active = st.checkbox("Active", value=selected_user['is_active'])
                        
                        col_update, col_delete = st.columns([1, 1])
                        
                        with col_update:
                            submit_update = st.form_submit_button("💾 Update User", type="primary", use_container_width=True)
                        
                        with col_delete:
                            submit_delete = st.form_submit_button("🗑️ Delete User", use_container_width=True)
                        
                        if submit_update:
                            try:
                                response = session.put(
                                    f'{API_BASE}/auth/users/{selected_user["id"]}',
                                    params={
                                        'full_name': edit_full_name,
                                        'role': edit_role,
                                        'is_active': edit_is_active
                                    },
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    st.success(f"✅ User '{selected_user['username']}' updated successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to update user: {response.json()}")
                            except Exception as e:
                                st.error(f"🔌 Connection error: {str(e)}")
                        
                        if submit_delete:
                            current_username = st.session_state.user.get('username') if st.session_state.user else None  # type: ignore
                            if selected_user['username'] == current_username:
                                st.error("⚠️ You cannot delete your own account!")
                            else:
                                try:
                                    response = session.delete(
                                        f'{API_BASE}/auth/users/{selected_user["id"]}',
                                        timeout=5
                                    )
                                    
                                    if response.status_code == 200:
                                        st.success(f"✅ User '{selected_user['username']}' deleted successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to delete user: {response.json()}")
                                except Exception as e:
                                    st.error(f"🔌 Connection error: {str(e)}")
                else:
                    st.info("No users found")
            else:
                st.error(f"Failed to fetch users: {response.json()}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
