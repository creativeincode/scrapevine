# --- How to Use for Debugging ---
#
# [1] Ensure that `debugpy` is installed on the machine running the Streamlit app / Python script:
#
#    > pip install debugpy
#
# [2] In your main streamlit app script (e.g. 'main.py'):
#
#    import streamlit_debug
#    streamlit_debug.set(flag=True, wait_for_client=True, host='localhost', port=8765)
#
# `flag=True` will initiate a debug session. `wait_for_client=True` will wait for a debug client to attach when
# the streamlit app is run before hitting your next debug breakpoint. `wait_for_client=False` will not wait.
#
# --- Debugging with VS CODE ---
#
# [1] You'll need a `.vscode/launch.json` config file with port numbers matching those in `streamlit_debug.set()`.
#     (it should NOT be the same port that streamlit is actually started up on!)
#
# [2] When `flag=True` and `wait_for_client=True`, select "Python: debugpy Remote Attach" as the "Run and Debug"
#     configuration within VS Code.

import streamlit as st
import logging

_DEBUG = False
def set(flag: bool=False, wait_for_client=False, host='localhost', port=8765):
    global _DEBUG
    _DEBUG = flag
    try:
        # To prevent debugpy loading again and again because of
        # Streamlit's execution model, we need to track debugging state 
        if 'debugging' not in st.session_state:
            st.session_state.debugging = None

        if _DEBUG and not st.session_state.debugging:
            # https://code.visualstudio.com/docs/python/debugging
            import debugpy
            if not debugpy.is_client_connected():
                debugpy.listen((host, port))
            if wait_for_client:
                logging.info(f'>>> Waiting for debug client attach... <<<')
                debugpy.wait_for_client() # Only include this line if you always want to manually attach the debugger
                logging.info(f'>>> ...attached! <<<')
            # debugpy.breakpoint()

            if st.session_state.debugging == None:
                logging.info(f'>>> Remote debugging activated (host={host}, port={port}) <<<')
            st.session_state.debugging = True
        
        if not _DEBUG:
            if st.session_state.debugging == None:
                logging.info(f'>>> Remote debugging in NOT active <<<')
            st.session_state.debugging = False
    except:
        # Ignore... e.g. for cloud deployments
        pass