"""
Page to present the system architecture and technical design decisions of each
RAG component.
"""

import streamlit as st
from utils.resources import load_architecture_image

def render_info_card(
    title: str,
    icon_svg: str,
    text: str,
    theme: str = "blue",
):
    """Render an information card with an SVG icon and a color theme."""
    THEMES = {
        "blue": {
            "card_bg": "#DCEBFA",
            "icon_bg": "#24558A",
            "text": "#24496F",
            "highlight": "#173B65",
        },
        "green": {
            "card_bg": "#DDF3E4",
            "icon_bg": "#236642",
            "text": "#24563A",
            "highlight": "#174A30",
        },
        "pink": {
            "card_bg": "#F3E1F5",
            "icon_bg": "#6B2878",
            "text": "#593263",
            "highlight": "#461653",
        }
    }
    if theme not in THEMES:
        raise ValueError(
            f"Unknown theme '{theme}'. Available themes: {list(THEMES)}"
        )

    colors = THEMES[theme]

    # Template
    st.markdown(
        f"""
        <div style="
            background-color: {colors['card_bg']};
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 16px;
            font-family: sans-serif;
        "><div style="
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
            "><div style="
                    background-color: {colors['icon_bg']};
                    border-radius: 10px;
                    width: 44px;
                    height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                ">{icon_svg}</div>
                <h3 style="
                    color: {colors['highlight']};
                    margin: 0;
                    padding: 0;
                    font-size: 1.4rem;
                    font-weight: 650;
                    line-height: 1.3;
                ">{title}
                </h3>
            </div>
            <div style="
                color: {colors['text']};
                font-size: 1rem;
                line-height: 1.65;
                text-align: justify;
            ">{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_architecture_design():
    st.header("System Architecture")

    st.markdown(
        """
        The system follows an end-to-end RAG architecture organized into
        two main pipelines. The **Ingestion Pipeline** processes GitHub
        repositories and indexes their content in a ChromaDB vector store,
        while the **Query Pipeline** retrieves relevant context and generates
        source-grounded answers to user queries.
        """
    )

    st.image(load_architecture_image(), width='stretch')

    st.header("Technical Design & Key Decisions")

    st.markdown(
        """
        The main design constraint was to build an effective RAG system for repository-level question answering while ensuring efficient
        execution on *Streamlit Community Cloud*. The system therefore balances retrieval quality and answer reliability with computational
        efficiency and low response latency, enabling public access while maintaining a responsive user experience.
        """
    )

    ###########################
    ## REPOSITORY INGESTION ###
    ###########################
    REPOSITORY_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M10 10.5 8 13l2 2.5"/>
        <path d="m14 10.5 2 2.5-2 2.5"/>
        <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z"/>
    </svg>
    """
    render_info_card(
        title="Repository Ingestion",
        icon_svg=REPOSITORY_ICON,
        theme="blue",
        text="""
            <p style="margin: 0 0 12px 0;">
                Given a public GitHub repository URL, the ingestion
                component clones the repository, filters the allowed
                files, and converts their contents into LangChain
                <code style="
                    color: #173B65;
                    font-weight: 700;
                    background-color: #C5DDF5;
                    padding: 2px 5px;
                    border-radius: 4px;
                ">Document</code> objects.
            </p>
            <p style="margin: 0;">
                Each document preserves the raw file content and
                metadata identifying its origin, including the
                repository, branch, file name, and source URL.
            </p>
        """,
    )

    ###########################
    ## DOCUMENT PROCESSING ####
    ###########################
    DOCUMENT_PROCESSING_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M15 8a1 1 0 0 1-1-1V2a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8z"/>
        <path d="M20 8v12a2 2 0 0 1-2 2h-4.182"/>
        <path d="m3.305 19.53.923-.382"/>
        <path d="M4 10.592V4a2 2 0 0 1 2-2h8"/>
        <path d="m4.228 16.852-.924-.383"/>
        <path d="m5.852 15.228-.383-.923"/>
        <path d="m5.852 20.772-.383.924"/>
        <path d="m8.148 15.228.383-.923"/>
        <path d="m8.53 21.696-.382-.924"/>
        <path d="m9.773 16.852.922-.383"/>
        <path d="m9.773 19.148.922.383"/>
        <circle cx="7" cy="18" r="3"/>
    </svg>
    """
    render_info_card(
    title="Document Processing",
    icon_svg=DOCUMENT_PROCESSING_ICON,
    theme="blue",
    text="""
        <p style="margin: 0 0 16px 0;">
            A <strong>modular preprocessing stage</strong> applies
            file-specific transformations before chunking to preserve
            meaningful content structure and improve downstream processing.
        </p><ul style="margin: 0 0 16px 0; padding-left: 22px;">
            <li style="margin-bottom: 12px;">
                <strong>Jupyter notebooks (<code style="
                                    color: #173B65;
                                    font-weight: 700;
                                    background-color: #C5DDF5;
                                    padding: 2px 5px;
                                    border-radius: 4px;
                                ">.ipynb</code>):</strong>
                Notebooks are parsed into individual LangChain
                <code style="
                    color: #173B65;
                    font-weight: 700;
                    background-color: #C5DDF5;
                    padding: 2px 5px;
                    border-radius: 4px;
                ">Document</code> objects, one per non-empty Markdown
                or code cell. This replaces the original JSON representation
                with directly processable content, preserving cell-level
                granularity and avoiding the structural overhead of notebook
                metadata and serialization.
            </li><li>
                <strong>Extensible architecture:</strong>
                The preprocessing stage is designed to accommodate additional
                file-specific processors, making it straightforward to
                introduce tailored transformations as support for new content
                types evolves.
            </li></ul>
    """,
    )

    ###########################
    ####### CHUNKING ##########
    ###########################
    CHUNKING_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <circle cx="6" cy="6" r="3"/>
        <path d="M8.12 8.12 12 12"/>
        <path d="M20 4 8.12 15.88"/>
        <circle cx="6" cy="18" r="3"/>
        <path d="M14.8 14.8 20 20"/>
    </svg>
    """
    render_info_card(
        title="Chunking",
        icon_svg=CHUNKING_ICON,
        theme="blue",
        text="""
            <p style="margin: 0 0 16px 0;">
                A <strong>file-specific chunking strategy</strong> is used
                to preserve the structure and semantic coherence of different
                content types, improving the quality of the retrieved context:
            </p><ul style="margin: 0 0 16px 0; padding-left: 22px;">
                <li style="margin-bottom: 12px;">
                    <strong>Code:</strong>
                    Language-aware recursive splitting respects common code
                    boundaries, helping keep related statements and logical
                    blocks together whenever possible.
                </li><li style="margin-bottom: 12px;">
                    <strong>Markdown:</strong>
                    Heading-based splitting preserves document hierarchy and
                    section context, followed by recursive character splitting
                    to control chunk size while minimizing unnecessary
                    fragmentation.
                </li><li>
                    <strong>Plain text and structured files</strong>
                    (e.g., JSON and YAML): Recursive character splitting provides
                    a flexible approach to producing consistently sized chunks
                    while preserving local context and keeping related content
                    together whenever possible.
                </li></ul>
            <p style="margin: 0;">
                This tailored approach balances
                <strong>structural preservation, contextual coherence, and
                chunk-size control</strong>, making the resulting chunks better
                suited for semantic retrieval and downstream LLM generation.
            </p>
        """,
    )

    ###########################
    ####### EMBEDDING #########
    ###########################    
    EMBEDDING_GENERATION_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M12 20v2"/>
        <path d="M12 2v2"/>
        <path d="M17 20v2"/>
        <path d="M17 2v2"/>
        <path d="M2 12h2"/>
        <path d="M2 17h2"/>
        <path d="M2 7h2"/>
        <path d="M20 12h2"/>
        <path d="M20 17h2"/>
        <path d="M20 7h2"/>
        <path d="M7 20v2"/>
        <path d="M7 2v2"/>
        <rect x="4" y="4" width="16" height="16" rx="2"/>
        <rect x="8" y="8" width="8" height="8" rx="1"/>
    </svg>
    """
    render_info_card(
        title="Embedding Generation",
        icon_svg=EMBEDDING_GENERATION_ICON,
        theme="blue",
        text="""
            <p style="margin: 0;">
                The system uses Hugging Face's
                <code style="
                    color: #173B65;
                    font-weight: 700;
                    background-color: #C5DDF5;
                    padding: 2px 5px;
                    border-radius: 4px;
                ">paraphrase-multilingual-MiniLM-L12-v2</code> to generate
                dense vector representations for semantic retrieval. The model
                was selected for its
                <strong>balance between semantic quality, multilingual
                capabilities, and computational efficiency</strong>.
                Its 384-dimensional embeddings provide compact representations
                that limit storage requirements, while its lightweight
                architecture enables local CPU inference without relying on
                external embedding APIs. These characteristics make it a
                practical choice for resource-constrained deployment environments
                such as <em>Streamlit Community Cloud</em>, supporting a portable
                and cost-effective RAG architecture.
            </p>
        """,
    )

    ###########################
    ## VECTOR DATABASE ########
    ###########################   
    VECTOR_DATABASE_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <ellipse cx="12" cy="5" rx="9" ry="3"/>
        <path d="M3 5V19A9 3 0 0 0 21 19V5"/>
        <path d="M3 12A9 3 0 0 0 21 12"/>
    </svg>
    """
    render_info_card(
        title="Vector Database",
        icon_svg=VECTOR_DATABASE_ICON,
        theme="pink",
        text="""
            <p style="margin: 0;">
                <strong><em>ChromaDB</em></strong> was selected for its seamless integration
                with <strong><em>LangChain</em></strong>, support for metadata-based filtering,
                and flexible storage options. Its persistent local storage
                facilitates reproducible development and experimentation,
                while its in-memory mode simplifies deployment to
                <em>Streamlit Community Cloud</em> without requiring an external
                database service. This combination provides an efficient,
                lightweight solution for vector storage and retrieval, aligned
                with the project's portability and deployment constraints.
            </p>
        """,
    )

    ###########################
    ######## RETRIEVAL ########
    ###########################  
    ADAPTIVE_RETRIEVAL_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M21 11.693V5"/>
        <path d="m22 22-1.875-1.875"/>
        <path d="M3 12a9 3 0 0 0 8.697 2.998"/>
        <path d="M3 5v14a9 3 0 0 0 9.28 2.999"/>
        <circle cx="18" cy="18" r="3"/>
        <ellipse cx="12" cy="5" rx="9" ry="3"/>
    </svg>
    """
    render_info_card(
        title="Adaptive Retrieval",
        icon_svg=ADAPTIVE_RETRIEVAL_ICON,
        theme="green",
        text="""
            <p style="margin: 0 0 16px 0;">
                The system implements an <strong>adaptive retrieval strategy</strong>
                that identifies references to repository files in user queries
                and dynamically selects the retrieval method and number of chunks.
                This design combines precise context targeting with
                relevance-diversity trade-offs, avoiding a one-size-fits-all
                retrieval configuration.
            </p><ul style="margin: 0; padding-left: 22px;">
                <li style="margin-bottom: 12px;">
                    <strong>Single-file queries:</strong>
                    Metadata-filtered semantic similarity search retrieves the
                    top 5 chunks (<code style="
                        color: #174A30;
                        font-weight: 700;
                        background-color: #C4E6D0;
                        padding: 2px 5px;
                        border-radius: 4px;
                    ">k=5</code>) exclusively from the referenced
                    file. Restricting the search scope reduces interference from
                    unrelated repository content and prioritizes locally relevant
                    information.
                </li><li style="margin-bottom: 12px;">
                    <strong>Multi-file queries:</strong>
                    Metadata-filtered Maximal Marginal Relevance (<em>MMR</em>)
                    retrieves 10 chunks (<code style="
                        color: #174A30;
                        font-weight: 700;
                        background-color: #C4E6D0;
                        padding: 2px 5px;
                        border-radius: 4px;
                    ">k=10</code>) across the referenced
                    files. The larger context budget accommodates cross-file
                    dependencies, while MMR balances query relevance with
                    diversity to reduce redundant results and capture
                    complementary information.
                </li><li>
                    <strong>General queries:</strong>
                    Repository-wide MMR retrieves the top 5 chunks
                    (<code style="
                        color: #174A30;
                        font-weight: 700;
                        background-color: #C4E6D0;
                        padding: 2px 5px;
                        border-radius: 4px;
                    ">k=5</code>), encouraging coverage of different relevant
                    areas of the repository while keeping the context concise
                    and limiting redundant information.
                </li></ul>
            <p style="margin: 16px 0 0 0;">
            By adapting both the retrieval scope and the retrieval configuration
            to the query, the system balances
            <strong>precision, contextual coverage, and redundancy control</strong>.
            The strategy is also supported by retrieval evaluation experiments,
            which compare its performance against a fixed semantic-search baseline.
        </p>
        """,
    )

    ###########################
    ######## PROMPT ###########
    ###########################  
    PROMPT_ENGINEERING_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/>
        <path d="M12 11h.01"/>
        <path d="M16 11h.01"/>
        <path d="M8 11h.01"/>
    </svg>
    """

    render_info_card(
        title="Prompt Engineering",
        icon_svg=PROMPT_ENGINEERING_ICON,
        theme="green",
        text="""
        <p style="margin: 0 0 16px 0;">
            A <strong>custom prompt template</strong> defines the LLM's role as a
            <strong>repository-focused assistant</strong>, instructing it to answer
            user queries using the retrieved context rather than relying on unsupported
            assumptions or general knowledge.
        </p>
        <p style="margin: 0 0 16px 0;">
            The prompt establishes clear behavioral constraints, prioritizes
            <strong>factual consistency with the retrieved evidence</strong>, and
            enforces a standardized citation format. Each retrieved chunk is provided
            alongside its file name and source URL, enabling
            <strong>traceable, source-grounded answers</strong>.
        </p>
        <p style="margin: 0;">
            These instructions help align the generated responses with the system's
            intended purpose, reduce unsupported claims, and improve
            the transparency and reliability of the final answers.
        </p>
        """,
    )

    ###########################
    ########### LLM ###########
    ###########################  
    LLM_GENERATION_ICON = """
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#FFFFFF"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M12 20v2"/>
        <path d="M12 2v2"/>
        <path d="M16 9v6"/>
        <path d="M17 20v2"/>
        <path d="M17 2v2"/>
        <path d="M2 12h2"/>
        <path d="M2 17h2"/>
        <path d="M2 7h2"/>
        <path d="M20 12h2"/>
        <path d="M20 17h2"/>
        <path d="M20 7h2"/>
        <path d="M7 20v2"/>
        <path d="M7 2v2"/>
        <path d="M8 13h4"/>
        <path d="M8 15v-4a2 2 0 014 0v4"/>
        <rect x="4" y="4" width="16" height="16" rx="2"/>
    </svg>
    """
    render_info_card(
        title="LLM Generation",
        icon_svg=LLM_GENERATION_ICON,
        theme="green",
        text="""
            <p style="margin: 0 0 16px 0;">
                For deployment, the system uses the <strong>Groq API</strong> with
                <code style="
                    color: #174A30;
                    font-weight: 700;
                    background-color: #C4E6D0;
                    padding: 2px 5px;
                    border-radius: 4px;
                ">openai/gpt-oss-20b</code>, offloading inference to dedicated
                infrastructure rather than running the LLM locally. This avoids
                the substantial memory and computational requirements of hosting
                a generative model on <em>Streamlit Community Cloud</em>, while
                enabling responsive, interactive generation.
            </p><p style="margin: 0;">
                The selected model is an open-weight
                <strong>Mixture-of-Experts (MoE)</strong> model with 20 billion
                total parameters and approximately 3.6 billion active parameters
                per forward pass. Its capabilities in reasoning and code
                generation make it a suitable choice for understanding repository
                content and synthesizing answers from retrieved code and
                documentation. Combined with Groq's high-speed inference, it
                provides a practical balance between generation capabilities,
                responsiveness, and deployment simplicity.
            </p>
        """,
    )