import streamlit as st
import hashlib
from datetime import datetime
import pandas as pd

from database import Database
from ai_helper import AIHelper
from visualizations import create_mood_trend, create_mood_distribution, create_weekly_summary, analyze_mood_patterns
from styles import apply_custom_styles, show_header
from quote_generator import QuoteGenerator

# Initialize database and AI helper
db = Database()
ai = AIHelper()
quote_gen = QuoteGenerator(ai)

# Apply custom styles
apply_custom_styles()

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'daily_quote' not in st.session_state:
    st.session_state.daily_quote = None
if 'quote_date' not in st.session_state:
    st.session_state.quote_date = None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_user():
    username = st.session_state.login_username
    password = st.session_state.login_password

    user = db.get_user(username)
    if user and user['password_hash'] == hash_password(password):
        st.session_state.user_id = user['id']
        st.session_state.username = username
        st.success("Successfully logged in!")
        st.rerun()
    else:
        st.error("Invalid username or password")


def register_user():
    username = st.session_state.register_username
    password = st.session_state.register_password

    if len(password) < 6:
        st.error("Password must be at least 6 characters long")
        return

    try:
        user_id = db.add_user(username, hash_password(password))
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.success("Successfully registered!")
        st.rerun()
    except Exception as e:
        st.error("Username already exists or registration failed")


def show_auth_page():
    st.markdown("### Welcome to Mental Health Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.text_input("Username", key="login_username")
        st.text_input("Password", type="password", key="login_password")
        st.button("Login", on_click=login_user)

    with tab2:
        st.text_input("Username", key="register_username")
        st.text_input("Password", type="password", key="register_password")
        st.button("Register", on_click=register_user)


def get_daily_quote(mood_history=None):
    """Get or generate daily quote"""
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Generate new quote if it's a new day or no quote exists
    if (st.session_state.quote_date != current_date or
            st.session_state.daily_quote is None):
        st.session_state.daily_quote = quote_gen.generate_daily_quote(mood_history)
        st.session_state.quote_date = current_date

    return st.session_state.daily_quote


def show_mood_tracker():
    st.markdown("### 📊 Daily Mood Check-in")

    # Get and display daily quote
    mood_history = db.get_mood_history(st.session_state.user_id, days=7)
    quote_data = get_daily_quote(mood_history)

    with st.expander("✨ Daily Inspiration", expanded=True):
        st.markdown(f"""
            > _{quote_data['quote']}_
            >
            > — {quote_data['author']}
        """)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Theme:** {quote_data['theme']}")
            st.markdown(f"**Reflection:** {quote_data['reflection']}")

        with col2:
            st.markdown("**Mood Boost Tips:**")
            for tip in quote_data['mood_boost_tips']:
                st.markdown(f"- {tip}")

    with st.form("mood_form"):
        col1, col2 = st.columns([1, 2])

        with col1:
            mood_score = st.slider(
                "How are you feeling today?",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Very Low, 5 = Excellent"
            )

            st.markdown("""
                ##### Mood Scale:
                - 5: Excellent
                - 4: Good
                - 3: Neutral
                - 2: Low
                - 1: Very Low
            """)

        with col2:
            notes = st.text_area(
                "What's on your mind?",
                height=150,
                help="Share your thoughts, feelings, or experiences. This helps provide more accurate and personalized support.",
                placeholder="Express yourself freely - your thoughts and feelings matter."
            )

        submitted = st.form_submit_button("Submit")

        if submitted:
            db.add_mood_entry(st.session_state.user_id, mood_score, notes)
            response = ai.get_mood_response(mood_score, notes)

            st.markdown("### 💭 AI Response")
            st.info(response["message"])

            if response.get("analyzed_mood"):
                mood_analysis = response["analyzed_mood"]
                st.markdown("#### 🔍 Mood Analysis")

                factors_col, score_col = st.columns([2, 1])
                with factors_col:
                    if mood_analysis.get("factors"):
                        st.markdown("**Key Factors:**")
                        for factor in mood_analysis["factors"]:
                            st.markdown(f"- {factor}")

                with score_col:
                    analyzed_score = mood_analysis.get("score", mood_score)
                    st.metric(
                        "Combined Mood Score",
                        f"{analyzed_score:.1f}",
                        delta=f"{analyzed_score - mood_score:+.1f} from reported"
                    )

            if response.get("suggestions"):
                st.markdown("### 💡 Suggestions")
                for suggestion in response["suggestions"]:
                    st.markdown(f"- {suggestion}")


def show_mood_analytics():
    st.markdown("### 📈 Mood Analytics")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox(
            "Select time range",
            options=[7, 14, 30, 90],
            format_func=lambda x: f"Last {x} days",
            key="mood_days"
        )

    mood_history = db.get_mood_history(st.session_state.user_id, days)

    if mood_history:
        # Summary statistics
        df = pd.DataFrame(mood_history)
        avg_mood = df['mood_score'].mean()
        most_common_mood = df['mood_score'].mode().iloc[0]
        mood_labels = {1: 'Very Low', 2: 'Low', 3: 'Neutral', 4: 'Good', 5: 'Excellent'}

        # Display summary metrics
        st.markdown("#### 📊 Summary")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Average Mood", f"{avg_mood:.1f}")
        with metric_col2:
            st.metric("Most Common Mood", mood_labels[most_common_mood])
        with metric_col3:
            st.metric("Total Entries", len(df))

        # Mood trend and distribution
        trend_col, dist_col = st.columns(2)
        with trend_col:
            trend_fig = create_mood_trend(mood_history)
            if trend_fig:
                st.plotly_chart(trend_fig, use_container_width=True)

        with dist_col:
            dist_fig = create_mood_distribution(mood_history)
            if dist_fig:
                st.plotly_chart(dist_fig, use_container_width=True)

        # Weekly summary
        st.markdown("#### 📅 Weekly Overview")
        weekly_fig = create_weekly_summary(mood_history)
        if weekly_fig:
            st.plotly_chart(weekly_fig, use_container_width=True)

        # Mood patterns
        st.markdown("#### 🕒 Mood Patterns")
        pattern_fig = analyze_mood_patterns(mood_history)
        if pattern_fig:
            st.plotly_chart(pattern_fig, use_container_width=True)

        # Display recent notes
        st.markdown("#### 📝 Recent Notes")
        notes_df = df.sort_values('created_at', ascending=False).head()
        for _, row in notes_df.iterrows():
            # Handle created_at as either string or datetime
            created_at = row['created_at']
            if isinstance(created_at, str):
                # If it's already a string, use it directly
                date_str = created_at
            else:
                # If it's a datetime object, format it
                date_str = created_at.strftime('%Y-%m-%d %H:%M')

            with st.expander(f"Mood: {mood_labels[row['mood_score']]} - {date_str}"):
                st.write(row['notes'])
    else:
        st.info("Start tracking your mood to see analytics!")


def show_chat_interface():
    st.markdown("### 💬 Chat Support")

    # Get chat history
    chat_history = db.get_chat_history(st.session_state.user_id)

    # Display chat history
    for chat in reversed(chat_history):
        st.markdown(
            f"""<div class="chat-message user-message">
                {chat['message']}
            </div>""",
            unsafe_allow_html=True
        )
        st.markdown(
            f"""<div class="chat-message assistant-message">
                {chat['response']}
            </div>""",
            unsafe_allow_html=True
        )

    # Chat input
    with st.form("chat_form"):
        message = st.text_area("Type your message...")
        submitted = st.form_submit_button("Send")

        if submitted and message:
            response = ai.get_chat_response(message, chat_history)
            db.add_chat_entry(st.session_state.user_id, message, response)
            st.rerun()


def main():
    show_header()

    if not st.session_state.user_id:
        show_auth_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["Mood Tracker", "Analytics", "Chat Support"])

        with tab1:
            show_mood_tracker()

        with tab2:
            show_mood_analytics()

        with tab3:
            show_chat_interface()


if __name__ == "__main__":
    main()