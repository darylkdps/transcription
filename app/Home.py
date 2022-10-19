import streamlit as st
from pathlib import Path

def main():
    st.title('Home Page - Test of Streamlit Functionality')

    if 'D:' in str(Path.cwd()) or 'C:' in str(Path.cwd()):
        st.markdown('_No token_')
    else:
        st.markdown('_' + st.secrets['test_token'] + '_')

if __name__ == '__main__':
    st.set_page_config(page_title="Daryl Test", page_icon="random", layout="wide", initial_sidebar_state="auto")
    main()

