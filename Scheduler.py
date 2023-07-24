import pandas as pd
import streamlit as st
import time

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
#progress_bar in for-loop for usage with loading elements, styles.css for sugarcoating some visuals
#wide modes, dark modes are implemented by default, pandas support, altair for some visualization
#make a scheduler app?

#Or make a menu to help me automate some of mine work process> Need to think about it