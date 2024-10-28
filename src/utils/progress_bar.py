import streamlit as st
import time
'''
class ProgressBar:
    def __init__(self):
        #self.progress_bar = st.progress(0)
        #self.progress_msg = st.empty()
        #self.progress_msg.write("State:")
        pass
    def set_progress(self, percent, msg):
        #self.progress_bar.progress(percent)
        #self.progress_msg.write(msg)
        pass
    def reset_progress(self):
        #self.progress_bar.progress(0)
        #self.progress_msg.write("")
        pass
'''
class ProgressBar:
    def __init__(self):
        # Placeholder for the slider
        with st.container():
            self.slider_placeholder = st.empty()
            self.slider_placeholder.slider("Progress", min_value=0, max_value=100, value=0, disabled=True)
    
    def set_progress(self, percent, msg):
        self.slider_placeholder.slider("Progress", min_value=0, max_value=100, value=percent, disabled=True)
        #self.progress_bar.progress(percent)
        #self.progress_msg.write(msg)
        #pass
    def reset_progress(self):
        self.slider_placeholder.slider("Progress", min_value=0, max_value=100, value=0, disabled=True)
        #self.progress_bar.progress(0)
        #self.progress_msg.write("")
        #pass
