import streamlit as st

# Assuming this is a function in the app.py file that renders the page layout
def render_page():
    # Other content above the grid

    # Create two columns
    col1, col2 = st.columns([3, 1])

    # Place buttons in the second column to the top right
    with col2:
        if st.button('Select'):
            # Functionality for select button
            pass
        if st.button('Deselect'):
            # Functionality for deselect button
            pass

    # The rest of your grid layout code
    # For example:
    st.write('Your pages grid content here.')