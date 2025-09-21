# app.py (Modified Version)

import streamlit as st
from chatbot_logic import chatbot_instance # <-- IMPORT the centralized logic

st.set_page_config(page_title="🩺 Medical Assistant Chatbot", layout="wide")

st.title("🩺 Multilingual Medical Chatbot")
st.markdown("⚠️ **Disclaimer:** This chatbot is for informational purposes only. Please consult a doctor for real medical advice.")

user_query = st.text_input("Enter your symptoms or question:")

if st.button("Ask") and user_query.strip():
    with st.spinner("Thinking..."):
        # Use the single chatbot instance to get the answer
        result = chatbot_instance.get_answer(user_query)
        
        st.markdown(f"**🤖 Bot:** {result['result']}")
        with st.expander("📎 Sources"):
            for source in result["sources"]:
                st.write(source)