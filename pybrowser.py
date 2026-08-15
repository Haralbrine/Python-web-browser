import webview
import threading
import os
import sys

# Global handle for the window
window = None

def normalize_input(user_input):
    """Parses terminal input into a valid URL or local file path."""
    cleaned = user_input.strip()
    
    # Strip accidental brackets
    if cleaned.startswith("[") and cleaned.endswith("]"):
        cleaned = cleaned[1:-1].strip()

    # Local file path
    if cleaned.startswith("file://"):
        return cleaned
    elif os.path.exists(cleaned):
        return f"file://{os.path.abspath(cleaned)}"

    # Standard Web URL
    if cleaned.startswith(("http://", "https://")):
        return cleaned

    # Domain TLD fallback
    if "." in cleaned and " " not in cleaned:
        return f"https://{cleaned}"
    
    # Search engine fallback
    return f"https://www.google.com/search?q={cleaned.replace(' ', '+')}"

def terminal_control_loop():
    """Runs in a background thread to take continuous terminal input cleanly."""
    print("\n" + "="*60)
    print(" TERMINAL BROWSER CONTROLLER READY")
    print(" Type any URL (e.g., https://google.com)")
    print(" Type local files (e.g., file://C:/path/to/file.html)")
    print(" Type 'exit' or 'quit' to close.")
    print("="*60 + "\n")

    while True:
        try:
            cmd = input("Navigate > ")
            if not cmd.strip():
                continue

            if cmd.lower() in ["exit", "quit"]:
                if window:
                    window.destroy()
                sys.exit(0)

            target_url = normalize_input(cmd)
            print(f"--> Loading: {target_url}\n")
            
            # Catch non-fatal webview errors so the thread loop never crashes
            if window:
                try:
                    window.load_url(target_url)
                except webview.errors.WebViewException as err:
                    # Ignore non-fatal frame load warnings
                    pass
                except Exception as err:
                    # Catch any other generic UI thread quirks safely
                    pass

        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            if window:
                window.destroy()
            break

def start_terminal_thread():
    """Callback triggered ONLY after the GUI window engine has fully launched."""
    input_thread = threading.Thread(target=terminal_control_loop, daemon=True)
    input_thread.start()

def start_browser():
    global window
    
    start_url = "https://google.com"

    window = webview.create_window(
        title="Terminal Speed Browser",
        url=start_url,
        width=1024,
        height=768,
        resizable=True
    )

    # Trigger start_terminal_thread once webview is completely active
    webview.start(func=start_terminal_thread, gui='edgechromium')

if __name__ == "__main__":
    start_browser()