import streamlit as st


def apply_custom_styles():
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }

        .stTextInput > div > div > input {
            border-radius: 10px;
        }

        .stButton > button {
            border-radius: 20px;
            padding: 0.5rem 2rem;
            background-color: #4A90E2;
            color: white;
            border: none;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #357ABD;
            transform: translateY(-2px);
        }

        .chat-message {
            padding: 1rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            max-width: 80%;
        }

        .user-message {
            background-color: #E3F2FD;
            margin-left: auto;
        }

        .assistant-message {
            background-color: #F0F7F4;
            margin-right: auto;
        }

        .mood-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }

        .section-title {
            color: #2C3E50;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)


def show_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌿 Mental Health Assistant")
        st.markdown("""
            <p style='font-size: 1.2rem; color: #666;'>
                Your daily companion for emotional well-being
            </p>
        """, unsafe_allow_html=True)
