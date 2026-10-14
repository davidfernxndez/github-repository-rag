export default function(component) {
    const { parentElement, setTriggerValue } = component;

    // Retrieve the DOM elements managed by this component.
    const input = parentElement.querySelector("#message");
    const button = parentElement.querySelector("#send");
    const suggestionsBox = parentElement.querySelector("#suggestions");

    // Remove listeners from any previous initialization to prevent duplicates.
    parentElement.__chatComposerCleanup?.();

    // Available repository files are provided by the Streamlit component.
    const files = component.data?.available_files ?? [];

    // State used to manage file autocomplete and message submission.
    let matches = [];
    let activeIndex = 0;
    let mentionStart = -1;
    let selectedFiles = [];

    // Intercept keyboard events originating from the input to prevent them
    // from reaching Streamlit's global keyboard shortcuts.
    function preventGlobalShortcuts(event) {
        if (event.target === input) {
            event.stopImmediatePropagation();
        }
    }

    // Register the listener in the capture phase to intercept events early.
    window.addEventListener(
        "keydown",
        preventGlobalShortcuts,
        true
    );

    // Adjust the input height to fit its content, up to the CSS maximum.
    function resizeInput() {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 180) + "px";
    }

    // Reset autocomplete state and hide the suggestions dropdown.
    function closeSuggestions() {
        matches = [];
        mentionStart = -1;
        suggestionsBox.hidden = true;
        suggestionsBox.replaceChildren();
    }

    // Replace the active @mention with the selected repository file path.
    function selectFile(file) {
        // Ignore selection if no active @mention has been detected.
        if (mentionStart === -1) return;

        const cursor = input.selectionStart;
        const before = input.value.slice(0, mentionStart);
        const after = input.value.slice(cursor);
        const insertion = "@" + file + " ";

        // Preserve the surrounding text and place the cursor after the insertion.
        input.value = before + insertion + after;

        // Track selected files without adding duplicates.
        if (!selectedFiles.includes(file)) {
            selectedFiles.push(file);
        }

        const newCursor = before.length + insertion.length;

        input.focus();
        input.setSelectionRange(newCursor, newCursor);

        closeSuggestions();
        resizeInput();
    }

    // Render the current file matches as interactive autocomplete options.
    function renderSuggestions() {
        // Rebuild the dropdown to reflect the latest matches and active option.
        suggestionsBox.replaceChildren();

        if (matches.length === 0) {
            suggestionsBox.hidden = true;
            return;
        }

        matches.forEach((file, index) => {
            const option = document.createElement("button");
            option.type = "button";
            option.className =
                "suggestion" + (index === activeIndex ? " active" : "");
            option.textContent = file;

            // Expose the option and its selection state to assistive technologies.
            option.setAttribute("role", "option");
            option.setAttribute("aria-selected", String(index === activeIndex));

            // Handle selection before the pointer interaction changes input focus.
            option.addEventListener("pointerdown", event => {
                event.preventDefault();
                selectFile(file);
            });

            suggestionsBox.appendChild(option);
        });

        suggestionsBox.hidden = false;
    }

    // Detect the active @mention and filter the available repository files.
    function updateSuggestions() {
        const cursor = input.selectionStart;
        const beforeCursor = input.value.slice(0, cursor);
        const atIndex = beforeCursor.lastIndexOf("@");

        // No @ symbol before the cursor means there is no active mention.
        if (atIndex === -1) {
            closeSuggestions();
            return;
        }

        // Only recognize @mentions at the beginning of the input or after whitespace.
        if (atIndex > 0 && !/\s/.test(beforeCursor[atIndex - 1])) {
            closeSuggestions();
            return;
        }

        // Extract the text between @ and the current cursor position.
        const query = beforeCursor.slice(atIndex + 1);

        // Close autocomplete when the mention contains whitespace.
        if (/\s/.test(query)) {
            closeSuggestions();
            return;
        }

        mentionStart = atIndex;

        // Perform case-insensitive substring matching and limit the results.
        matches = files
            .filter(file =>
                file.toLowerCase().includes(query.toLowerCase())
            )
            .slice(0, 8);

        // Start keyboard navigation from the first matching file.
        activeIndex = 0;
        renderSuggestions();
    }

    // Validate and send the message and its selected repository files to Streamlit.
    function submit() {
        const text = input.value.trim();

        // Ignore empty messages.
        if (!text) return;

        // Trigger the Streamlit-side submission handler with the current payload.
        setTriggerValue("submit", {
            text,
            selected_files: [...selectedFiles]
        });

        // Reset the composer after submission.
        input.value = "";
        selectedFiles = [];

        closeSuggestions();
        resizeInput();
    }

    // Handle autocomplete navigation and message submission from the keyboard.
    function handleKeydown(event) {
        // Prevent the keyboard event from propagating beyond this handler.
        event.stopPropagation();

        const hasSuggestions =
            !suggestionsBox.hidden && matches.length > 0;

        if (hasSuggestions) {
            if (event.key === "ArrowDown") {
                // Move to the next option, wrapping to the first at the end.
                event.preventDefault();
                activeIndex = (activeIndex + 1) % matches.length;
                renderSuggestions();
                return;
            }

            if (event.key === "ArrowUp") {
                // Move to the previous option, wrapping to the last at the beginning.
                event.preventDefault();
                activeIndex =
                    (activeIndex - 1 + matches.length) % matches.length;
                renderSuggestions();
                return;
            }

            if (
                (event.key === "Enter" || event.key === "Tab") &&
                !event.shiftKey
            ) {
                // Select the active suggestion instead of submitting the message.
                event.preventDefault();
                selectFile(matches[activeIndex]);
                return;
            }

            if (event.key === "Escape") {
                // Dismiss autocomplete without modifying the input text.
                event.preventDefault();
                closeSuggestions();
                return;
            }
        }

        if (event.key === "Enter" && !event.shiftKey) {
            // Submit on Enter when autocomplete has no active suggestions.
            // Shift+Enter retains the textarea's default newline behavior.
            event.preventDefault();
            submit();
        }
    }

    // Resize the input and refresh autocomplete whenever its content changes.
    function handleInput() {
        resizeInput();
        updateSuggestions();
    }

    // Register the event handlers for input changes, keyboard interactions,
    // and clicks on the send button.
    input.addEventListener("input", handleInput);
    input.addEventListener("keydown", handleKeydown);
    button.addEventListener("click", submit);

    // Remove registered listeners when the component is unmounted or reinitialized.
    const cleanup = () => {
        input.removeEventListener("input", handleInput);
        input.removeEventListener("keydown", handleKeydown);
        button.removeEventListener("click", submit);

        window.removeEventListener(
            "keydown",
            preventGlobalShortcuts,
            true
        );

        // Clear the stored cleanup callback only if it still refers to this instance.
        if (parentElement.__chatComposerCleanup === cleanup) {
            parentElement.__chatComposerCleanup = null;
        }
    };

    // Store the cleanup callback so a subsequent initialization can reuse it.
    parentElement.__chatComposerCleanup = cleanup;

    // Return the cleanup function for the component lifecycle.
    return cleanup;
}
