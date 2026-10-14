import streamlit as st


def render_api_key_panel():
    st.subheader("API KEY Configuration")

    if st.button(
        "Configure your own Groq API Key",
        use_container_width=True,
    ):
        st.session_state.show_api_key_form = (
            not st.session_state.show_api_key_form
        )

    if st.session_state.show_api_key_form:
        with st.form("api_key_form"):
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Your key is used for your current session.",
            )

            submitted = st.form_submit_button(
                "Save API Key",
                type="primary",
                use_container_width=True,
            )

            if submitted:
                if not api_key.strip():
                    st.error("Please enter a valid API key.")
                else:
                    try:
                        # TO DO
                        print("TO DO: CARGAR LLM con nueva API KEY")
                        #configure_custom_api_key(api_key.strip())
                        #st.success("Your LLM configuration was updated.")
                        #st.rerun()
                    except Exception as exc:
                        st.error(
                            f"Could not initialize the LLM: {exc}"
                        )

    """
    # Current LLM status.
    st.divider()
    st.subheader("LLM status")

    llm_generator = st.session_state.llm_generator
    llm_source = st.session_state.llm_source

    if llm_generator is None:
        st.warning(
            "No default API key is configured. "
            "Configure your own Groq API key to continue."
        )
    elif llm_source == "custom":
        st.success("Using your own Groq API key.")
    else:
        requests_used = get_default_api_usage()
        requests_remaining = max(0, 10 - requests_used)

        if requests_remaining > 0:
            st.info(
                "Using the default Groq API key. "
                f"{requests_remaining} default requests remaining."
            )
        else:
            st.warning(
                "The default API request limit has been reached. "
                "Configure your own Groq API key to continue."
            )
    """