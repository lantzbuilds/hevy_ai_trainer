"""
Main application file for the AI Personal Trainer.
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from bootstrap_vectorstore import bootstrap_vectorstore
from config.database import Database
from models.user import FitnessGoal, Injury, InjurySeverity, Sex, UserProfile
from page_components.ai_recommendations import ai_recommendations_page
from page_components.dashboard import dashboard_page
from page_components.login import login_page
from page_components.profile import profile_page
from page_components.register import register_page
from page_components.routines import routines_page
from page_components.sync_hevy import sync_hevy_page
from page_components.workout_history import workout_history_page
from page_components.workout_preferences import workout_preferences_page
from services.hevy_api import HevyAPI
from services.openai_service import OpenAIService
from utils.crypto import decrypt_api_key, encrypt_api_key
from utils.units import (
    cm_to_inches,
    format_height_cm,
    format_weight_kg,
    inches_to_cm,
    kg_to_lbs,
    lbs_to_kg,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database connection
db = Database()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Personal Trainer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None,
)
st.set_option("client.showSidebarNavigation", False)

# Initialize session state for user authentication
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# Add a function to clear all caches
def clear_all_caches():
    """Clear all Streamlit caches."""
    st.cache_data.clear()
    st.cache_resource.clear()
    logger.info("Cleared all Streamlit caches")


def sidebar():
    """
    Render the sidebar navigation.
    """
    # Hide the default Streamlit navigation
    # hide_streamlit_style = """
    #     <style>
    #     #MainMenu {display: none !important;}
    #     footer {display: none !important;}
    #     header {display: none !important;}
    #     .stDeployButton {display: none !important;}
    #     .stApp > header {display: none !important;}
    #     .stApp > footer {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:first-child {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(2) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(3) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(4) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(5) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(6) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(7) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(8) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(9) {display: none !important;}
    #     .stApp > div[data-testid="stSidebar"] > div:nth-child(10) {display: none !important;}
    #     ul[data-testid="stSidebarNavItems"] {display: none !important;}
    #     </style>
    # """
    # st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    with st.sidebar:
        st.title("AI Personal Trainer")

        # Add a button to clear caches
        if st.button("Clear Caches"):
            clear_all_caches()
            st.success("Caches cleared!")
            st.rerun()

        # Check if user is logged in
        if "user_id" in st.session_state and st.session_state.user_id:
            # Navigation options for logged-in users
            selected = st.radio(
                "Navigation",
                [
                    "Dashboard",
                    "Workout History",
                    "AI Recommendations",
                    "Routines",
                    "Sync Hevy",
                    "Profile",
                    "Logout",
                ],
            )

            # Set the selected page in session state
            if selected == "Dashboard":
                st.session_state.page = "dashboard"
            elif selected == "Workout History":
                st.session_state.page = "workout_history"
            elif selected == "AI Recommendations":
                st.session_state.page = "ai_recommendations"
            elif selected == "Routines":
                st.session_state.page = "routines"
            elif selected == "Sync Hevy":
                st.session_state.page = "sync_hevy"
            elif selected == "Profile":
                st.session_state.page = "profile"
            elif selected == "Logout":
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            # Navigation options for non-logged-in users
            selected = st.radio(
                "Navigation",
                ["Login", "Register"],
            )

            # Set the selected page in session state
            if selected == "Login":
                st.session_state.page = "login"
            elif selected == "Register":
                st.session_state.page = "register"


def render_page():
    """
    Render the selected page based on session state.
    """
    if st.session_state.page == "dashboard":
        dashboard_page()
    elif st.session_state.page == "workout_history":
        workout_history_page()
    elif st.session_state.page == "ai_recommendations":
        ai_recommendations_page()
    elif st.session_state.page == "routines":
        routines_page()
    elif st.session_state.page == "sync_hevy":
        sync_hevy_page()
    elif st.session_state.page == "profile":
        profile_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()


def main():
    """
    Main application function.
    """
    if os.getenv("ENV") == "production":
        bootstrap_vectorstore()

    # Render the sidebar
    sidebar()

    # Render the selected page
    render_page()


if __name__ == "__main__":
    main()
