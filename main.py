import streamlit as st
import logging
import sys
from datetime import datetime
from database import Database  # Import the Database class from database.py

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Basic health check page
def main():
    try:
        st.title("Health Check Page")
        st.write("If you can see this, the app is working!")
        
        # Test database connection
        try:
            db = Database()
            st.success("✅ Database connection successful")
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")
            logger.error(f"Database error: {str(e)}")
        
        # Display some basic system info
        st.write("System Information:")
        st.json({
            "Python Version": sys.version,
            "Streamlit Version": st.__version__,
            "Current Time": str(datetime.now())
        })
        
    except Exception as e:
        logger.error(f"Main app error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
