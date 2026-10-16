"""
Header definitions with SVG Icons for Repository, API Key and Chat interfaces 
"""

# Custom Repository header with SVG ICON
REPOSITORY_HEADER = """
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#2563EB"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
        style="flex-shrink: 0;"
    >
        <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.7-.9l-.8-1.2A2 2 0 0 0 8 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>
        <path d="M8 10v4"/>
        <path d="M16 10v4"/>
        <path d="M8 12h8"/>
    </svg>
    <h2 style="margin: 0; padding: 0; font-size: 1.6rem;">
        Repository
    </h2>
</div>
"""

# Custom API KEY header with SVG ICON
API_KEY_HEADER = """
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#2563EB"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
        style="flex-shrink: 0;"
    >
        <circle cx="8" cy="15" r="5"/>
        <path d="m10.85 12.15 7.65-7.65 3 3-2 2 2 2-3 3-2-2"/>
    </svg>
    <h2 style="margin: 0; padding: 0; font-size: 1.6rem;">
        API Key
    </h2>
</div>
"""

# Custom chat header with SVG ICON
CHAT_HEADER = """
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="28"
        height="28"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
        style="color: #2563EB; flex-shrink: 0;"
    >
        <path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7
                 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7
                 a8.4 8.4 0 0 1-.9-3.8
                 8.5 8.5 0 0 1 4.7-7.6
                 8.4 8.4 0 0 1 3.8-.9h.5
                 a8.5 8.5 0 0 1 8 8v.5z"/>
    </svg>
    <h2 style="margin: 0; padding: 0; font-size: 1.6rem;">
        Chat with the RAG Assistant
    </h2>
</div>
"""