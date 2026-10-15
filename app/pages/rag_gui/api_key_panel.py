"""
Streamlit interface for configuring the Groq API key.

Displays the current LLM configuration status and allows users to configure
their own Groq API key to use their personal API quota.
"""

import streamlit as st

from src_app.api_key_management import (
    configure_custom_api_key,
    get_default_request_remaining,
)


def render_api_key_panel():
    """Render the Groq API configuration panel."""

    # Initialize the form visibility state on the first execution.
    # Session state preserves this value across Streamlit reruns.
    if "show_api_key_form" not in st.session_state:
        st.session_state.show_api_key_form = False

    # Retrieve the active LLM generator and the source of its API key.
    # The generator may be None if no default API key is configured.
    llm_generator = st.session_state.get("llm_generator")
    llm_source = st.session_state.get("llm_source", "default")

    st.subheader("GROQ API KEY CONFIGURATION")

    # Group the API status and configuration controls into a bordered panel.
    with st.container(border=True):

        # No generator means the assistant currently has no configured LLM.
        if llm_generator is None:
            st.warning(
                "No API Key is configured. "
                "Configure your own Groq API Key to use the assistant."
            )

        # A custom source means the user has configured their own API key.
        elif llm_source == "custom":
            st.success("**Using Your Own API Key**")
            st.caption(
                "Usage limits depend on your Groq account rate limits."
            )

        # Otherwise, the assistant is using the default free API access.
        else:
            requests_remaining = get_default_request_remaining()

            if requests_remaining > 0:
                st.info("**Using Free API Access**")
                st.caption(
                    "This service has a limited number of requests available."
                )
            else:
                # Inform the user that they must configure their own key
                # before they can continue using the assistant.
                st.warning(
                    "Free API Request Limit Reached"
                )
                st.caption(
                    "You have reached the request limit for free access." 
                    " Configure your own Groq API Key to continue using the assistant."
                )

        # Toggle the API key form between visible and hidden.
        # The button label reflects the current visibility state.
        if st.button(
            "**Configure your Groq API key**" if not st.session_state.show_api_key_form
            else "Cancel",
            use_container_width=True,
        ):
            st.session_state.show_api_key_form = (
                not st.session_state.show_api_key_form
            )

            # Rerun the script so the updated state is reflected immediately.
            st.rerun()

        # Display the form only when the user has requested it.
        if st.session_state.show_api_key_form:
            with st.form("api_key_form"):

                # Hide the API key while it is being entered.
                api_key = st.text_input(
                    "Enter your Groq API key to use your own API quota",
                    type="password",
                    placeholder="gsk_...",
                    help="Your key will be kept in your current session."
                )

                # Forms submit their inputs together when this button is pressed.
                submitted = st.form_submit_button(
                    "Save key",
                    type="primary",
                    use_container_width=True,
                )

                if submitted:
                    # Reject empty input before attempting configuration.
                    if not api_key.strip():
                        st.error("Please enter your Groq API key.")
                    else:
                        try:
                            # Remove surrounding whitespace and configure
                            # the LLM to use the user's API key.
                            configure_custom_api_key(api_key.strip())

                            # Close the form after successful configuration.
                            st.session_state.show_api_key_form = False

                            # Refresh the interface to display the new status.
                            st.rerun()

                        except Exception:
                            st.error(
                                "Could not configure the API KEY. "
                                "Please check your KEY and try again."
                            )