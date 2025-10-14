import streamlit as st
from api_utils import get_api_response
from google_sheets_utils import save_feedback_to_sheets

def display_chat_interface():
    st.markdown("""
        <style>
        .stButton > button {
            margin: 0 5px; /* Reduced margin for smaller gap */
        }
        .element-container {
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add like/dislike buttons after assistant messages
            if message["role"] == "assistant":
                # Initialize feedback state
                if f"show_feedback_{idx}" not in st.session_state:
                    st.session_state[f"show_feedback_{idx}"] = False
                if f"feedback_submitted_{idx}" not in st.session_state:
                    st.session_state[f"feedback_submitted_{idx}"] = False

                col1, col2 = st.columns([1, 1])  # Adjust column widths as needed

                with col1:
                    if st.button("👍", key=f"like_{idx}"):
                        st.session_state[f"show_feedback_{idx}"] = False
                        st.success("Thank you for your feedback!", icon="✅")
                        st.session_state[f"feedback_submitted_{idx}"] = True

                with col2:
                    if st.button("👎", key=f"dislike_{idx}"):
                        st.session_state[f"show_feedback_{idx}"] = True
                        st.session_state[f"feedback_submitted_{idx}"] = False

                if st.session_state[f"show_feedback_{idx}"]:
                    feedback_key = f"feedback_{idx}"
                    close_key = f"close_feedback_{idx}"
                    submit_key = f"submit_{idx}"
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        feedback = st.text_area("Please help us improve:", key=feedback_key)
                    with col2:
                        if st.button("❌", key=close_key):
                            st.session_state[f"show_feedback_{idx}"] = False
                            st.session_state[f"feedback_submitted_{idx}"] = False
                            st.rerun()
                    if st.button("Submit Feedback", key=f"submit_{idx}"):
                        if feedback:
                            # Save feedback to Google Sheets
                            if save_feedback_to_sheets(message["content"], feedback):
                                st.success("Thank you for your feedback!")
                                st.session_state[f"show_feedback_{idx}"] = False
                                st.session_state[f"feedback_submitted_{idx}"] = True
                            else:
                                st.error("Failed to save feedback.")
                        else:
                            st.warning("Please enter your feedback before submitting.")


    # Handle new user input
    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get API response
        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

            if response:
                st.session_state.session_id = response.get('session_id')
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})

                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                    # Initialize feedback state for the new assistant message
                    idx = len(st.session_state.messages) - 1
                    if f"show_feedback_{idx}" not in st.session_state:
                        st.session_state[f"show_feedback_{idx}"] = False
                    if f"feedback_submitted_{idx}" not in st.session_state:
                        st.session_state[f"feedback_submitted_{idx}"] = False

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if st.button("👍", key=f"like_{idx}"):
                            st.session_state[f"show_feedback_{idx}"] = False
                            st.success("Thank you for your feedback!", icon="✅")
                            st.session_state[f"feedback_submitted_{idx}"] = True

                    with col2:
                        if st.button("👎", key=f"dislike_{idx}"):
                            st.session_state[f"show_feedback_{idx}"] = True
                            st.session_state[f"feedback_submitted_{idx}"] = False

                    if st.session_state[f"show_feedback_{idx}"]:
                        feedback_key = f"feedback_{idx}"
                        close_key = f"close_feedback_{idx}"
                        submit_key = f"submit_{idx}"
                        col1, col2 = st.columns([10, 1])
                        with col1:
                            feedback = st.text_area("Please help us improve:", key=feedback_key)
                        with col2:
                            if st.button("❌", key=close_key):
                                st.session_state[f"show_feedback_{idx}"] = False
                                st.session_state[f"feedback_submitted_{idx}"] = False
                                st.rerun()  
                        if st.button("Submit Feedback", key=submit_key):
                            if feedback:
                                # Save feedback to Google Sheets
                                if save_feedback_to_sheets(response['answer'], feedback):
                                    st.success("Thank you for your feedback!")
                                    st.session_state[f"show_feedback_{idx}"] = False
                                    st.session_state[f"feedback_submitted_{idx}"] = True
                                else:
                                    st.error("Failed to save feedback.")
                            else:
                                st.warning("Please enter your feedback before submitting.")


                with st.expander("Details"):
                    st.subheader("Generated Answer")
                    st.code(response['answer'])
                    st.subheader("Model Used")
                    st.code(response['model'])
                    st.subheader("Session ID")
                    st.code(response['session_id'])
            else:
                st.error("Failed to get a response from the API. Please try again.")

   