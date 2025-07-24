# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import os
import json
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from app.agent import root_agent
from app.config import config

# Set up the Streamlit page
st.set_page_config(page_title="News Podcast Agent Playground", page_icon="🎙️")
st.title("🎙️ News Podcast Agent Playground")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session"

if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("audio_file"):
            st.audio(message["audio_file"])

# Input form
with st.form(key="podcast_form"):
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City for local news:", value=config.default_city, placeholder="e.g., New York")
    with col2:
        podcast_length = st.slider("Podcast length (minutes):", 1, 10, 3)
    
    submit_button = st.form_submit_button(label="Generate Podcast")

# Process the form submission
if submit_button and city:
    # Add user message to chat
    user_message = f"Create a {podcast_length}-minute podcast for {city}."
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_message)
    
    # Show assistant response with a spinner
    with st.chat_message("assistant"):
        with st.spinner("Generating podcast..."):
            # Create message for the agent
            message = types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
            
            # Set up session and runner
            session_service = InMemorySessionService()
            session = session_service.create_session_sync(user_id="streamlit_user", app_name="streamlit_app")
            runner = Runner(agent=root_agent, session_service=session_service, app_name="streamlit_app")
            
            # Run the agent
            events = runner.run(new_message=message, user_id="streamlit_user", session_id=session.id)
            
            # Process events and extract results
            response_text = ""
            audio_file = None
            
            for event in events:
                # Extract text content
                if hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts"):
                        for part in event.content.parts:
                            if hasattr(part, "text"):
                                response_text += part.text + "\n"
                    elif hasattr(event.content, "text"):
                        response_text += event.content.text + "\n"
                elif hasattr(event, "text"):
                    response_text += event.text + "\n"
                
                # Check for audio file in state
                if hasattr(event, "state") and "podcast_audio_file" in event.state:
                    audio_file = event.state["podcast_audio_file"]
            
            # Display the response
            st.write(response_text)
            
            # Play audio if available
            if audio_file and os.path.exists(audio_file):
                st.audio(audio_file)
                st.session_state.audio_file = audio_file
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "audio_file": st.session_state.audio_file
    })

# Add a sidebar with information
with st.sidebar:
    st.header("About")
    st.write("""
    This playground allows you to test the News Podcast Agent.
    
    Enter a city and desired podcast length to generate a local news podcast.
    
    The agent will:
    1. Research the latest local news for your city
    2. Create a podcast script
    3. Generate an audio file using text-to-speech
    """)
    
    st.header("Settings")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.audio_file = None
        st.rerun()