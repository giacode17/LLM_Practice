import streamlit as st
import re
import logging
from decimal import Decimal
from langchain_helper import get_few_shot_db_chain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inject custom CSS for styling
st.markdown(
    """
    <style>
    .answer-container {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f2f6; /* Lighter background color */
    }
    .answer-text {
        font-size: 25px; /* Larger font size */
        color: #333333; /* Darker text for readability */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Function to parse and format the response
def format_response(response_str):
    """
    Parses a string like "[(Decimal('26858'),)]" and formats the number.
    Returns the original string if the number is not found.
    """
    try:
        # Use a regular expression to find the number inside Decimal(...)
        match = re.search(r"Decimal\('(\d+)'\)", response_str)
        if match:
            # Extract the string, convert to Decimal, then format with commas
            number = Decimal(match.group(1))
            return f"{number:,}"
    except Exception as e:
        # Log parsing errors
        logger.error(f"Error parsing response: {e}")

    # Return the original response string if parsing fails
    return response_str


# ---------- Title ----------
st.title("Go T-Shirts shop Stock Checker")
st.caption(
    "Ask inventory or revenue questions in natural language. Example: *“How many white color Levi’s shirts do I have?”*")

question = st.text_input("Question: ")

if question:
    try:
        # Initialize the database chain
        chain, run = get_few_shot_db_chain()

        # Execute the query
        with st.spinner("Processing your question..."):
            raw_response = run(question)

        # Format the raw response before displaying
        formatted_response = format_response(raw_response)

        # Display the answer with the custom CSS
        st.header("Answer")
        st.markdown(f'<div class="answer-container"><p class="answer-text">{formatted_response}</p></div>',
                    unsafe_allow_html=True)

    except ValueError as e:
        # Handle missing environment variables
        st.error(f"Configuration Error: {str(e)}")
        logger.error(f"Configuration error: {e}")

    except Exception as e:
        # Handle any other errors gracefully
        st.error(f"Sorry, I couldn't process your question. Please try rephrasing it or check the application logs.")
        logger.error(f"Error processing question '{question}': {e}", exc_info=True)
