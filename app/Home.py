import streamlit as st
from pathlib import Path

def main():
    st.title('Home Page - Transcription / Translation')

    if 'D:' in str(Path.cwd()) or 'C:' in str(Path.cwd()):
        st.markdown('_No token_')
    else:
        st.markdown('_' + st.secrets['token'] + '_')

if __name__ == '__main__':
    st.set_page_config(
        page_title='Transcription / Translation',
        page_icon='💬',
        layout='wide',
        initial_sidebar_state='auto')
    
    main()

