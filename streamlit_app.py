import streamlit as st
from chatbot_core import ChatbotCore
import os
from dotenv import load_dotenv
import sys

# Load environment variables from keys.env file
load_dotenv("keys.env")

def main():
    st.title("Demo")

    # Get API credentials from environment variables
    api_key = os.environ["LLM_API_KEY"]
    base_url = os.environ["LLM_BASE_URL"]

    # ---------------------------
    # 1) Initialize or retrieve from session
    # ---------------------------
    if "chatbot_core" not in st.session_state:
        st.session_state.chatbot_core = ChatbotCore(api_key=api_key, base_url=base_url)

    if "messages" not in st.session_state:
        # This will hold the entire list of messages for the conversation
        # Each item: { "role": "system"|"user"|"assistant", "content": "..."}
        st.session_state.messages = []

    # Shortcut
    chatbot_core = st.session_state.chatbot_core

    # ---------------------------
    # 2) Display existing messages
    # ---------------------------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # ---------------------------
    # 3) Chat input
    # ---------------------------
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user message to the UI & session
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Process the message using the core module
        with st.status("Processing...", expanded=True) as status:
            result = chatbot_core.process_message(user_input)
            
            # Update status when done
            status.update(label="✅ Processing complete!")
        
        # Display tool calls if any (moved outside the status component)
        if result["debug_info"].get("tool_calls"):
            with st.expander("🔧 Tool Calls & Processing Details", expanded=True):
                for i, tool_call in enumerate(result["debug_info"]["tool_calls"]):
                    st.info(f"📡 Calling function: **{tool_call['function']}**")
                    st.code(tool_call["arguments"], language='json')
                    
                    # Show result
                    st.success("✅ Function executed successfully")
                    if i < len(result["debug_info"]["tool_results"]):
                        st.json(result["debug_info"]["tool_results"][i])
        
        # Display assistant responses
        for response in result["responses"]:
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)
                
        if result.get("image_data"):
            st.session_state.messages.append({"role": "assistant", "content": result["image_data"]})
            with st.chat_message("assistant"):
                st.image(result["image_data"])

    # ---------------------------
    # 6) Show user info in the sidebar
    # ---------------------------
    st.sidebar.subheader("Current User Info State")
    st.sidebar.json(chatbot_core.conversation_manager.user_info_state)


if __name__ == "__main__":
    main()