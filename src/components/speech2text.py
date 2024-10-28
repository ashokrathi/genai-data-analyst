import streamlit as st
import speech_recognition as sr
from app_config import usr_prompt_txt_key

####################### Initialize Speech Recognizer
recognizer = sr.Recognizer()

recognized_text = ""

def show_speaker():
    if st.button("🎤 Speak LLM Prompt"):
        st.write("Listening... Please speak your prompt into the microphone.")
        try:
            # Capture audio from the microphone
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
            
            # Convert speech to text using Google Web Speech API
            st.write("Recognizing speech...")
            recognized_text = recognizer.recognize_google(audio)
            st.success(f"Recognized Speech: {recognized_text}")
            st.session_state[usr_prompt_txt_key] = recognized_text
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Web Speech; {e}")
    
