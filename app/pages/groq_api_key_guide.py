"""
Display a visual tutorial explaining how to configure a Groq API key.
"""

import streamlit as st

from utils.resources import load_groq_image

def display_image(image_name: str, width: int = 600):
    """Display a image aligned to the left with a controlled width."""
    st.image(
        load_groq_image(image_name),
        width=width,
    )

def render_groq_api_key_guide():
    """Render the Groq API key setup guide."""

    # --------------------------------------------------
    # Page header
    # --------------------------------------------------

    st.title("Groq API Key Guide")

    st.markdown(
        """
        You can use the RAG Assistant without configuring your own API key
        for up to **5 requests**. To continue using the assistant, configure
        your own free Groq API key by following the steps below.
        """
    )

    st.info(
        "You only need to configure your API key once per saved application "
        "configuration. Your key is private: never share it or publish it."
    )

    st.divider()

    # --------------------------------------------------
    # Step 1: Sign in to Groq Console
    # --------------------------------------------------

    st.subheader("1. Sign in to Groq Console")

    st.markdown(
        """
        Open the Groq Console and create a free account, or sign in to
        your existing account. You can register using your email address
        or sign in with Google or GitHub.
        """
    )

    st.markdown(
        "[**Open Groq Console ↗**](https://console.groq.com/home)"
    )

    st.caption(
        "A credit card is not required to access Groq's free tier."
    )

    # --------------------------------------------------
    # Step 2: Generate an API key
    # --------------------------------------------------

    st.subheader("2. Generate your API key")

    st.markdown(
        """
        Once signed in, open the **API Keys** section in the Groq Console.
        You can also access it directly using the link below.
        """
    )

    st.markdown(
        "[**Open API Keys ↗**](https://console.groq.com/keys)"
    )

    # Locate the API Keys section.
    st.markdown("**Step 2.1 — Open API Keys section**")

    display_image("groq_console_api_key_menu.png", width=950)

    # Create a new API key.
    st.markdown("**Step 2.2 — Create a new key**")

    st.markdown(
            "Click **Create API Key** to start generating your key."
    )

    display_image("api_key_button.png", width=900)

    # Name the API key.
    st.markdown("**Step 2.3 — Name your key**")

    st.markdown(
            """
            Enter a descriptive name, such as
            `test_RAG_assistant`, to identify your key later.
            Then click **Submit**.
            """
    )

    display_image("create_api_key.png", width=600)


    # --------------------------------------------------
    # Step 3: Copy and save the API key
    # --------------------------------------------------

    st.subheader("3. Copy and save your API key")

    st.markdown(
        """
        Copy the generated key as soon as it appears and store it securely.
        **Groq will only display the complete key once.** If you close the
        dialog without saving it, you will need to generate a new key.
        """
    )

    display_image("copy_api_key.png", width=600)

    st.warning(
        "Keep your API key secret. Do not commit it to Git, share it, "
        "or include it in screenshots or public code."
    )


    # --------------------------------------------------
    # Step 4: Configure the RAG Assistant
    # --------------------------------------------------

    st.subheader("4. Configure your RAG Assistant")

    st.markdown(
        """
        Return to the RAG Assistant and open its **Groq API Key** menu.
        Enter your key in the **Configure your Groq API Key** form and
        save it.
        """
    )

    display_image("save_api_key.png", width=500)

    st.success(
        "You're all set! The RAG Assistant can now use your Groq API key "
        "for subsequent requests."
    )

    st.markdown(
        """
        **Usage limits**

        Requests made through your own key are subject to Groq's API
        rate limits and usage policies. Review them here:

        [**Groq API Rate Limits ↗**](https://console.groq.com/docs/rate-limits)
        """
    )
