from app import app
import webbrowser
import threading
import time
import os

def open_browser():
    """Open the browser after a short delay to ensure server is up"""
    time.sleep(1.5)
    url = "http://localhost:5000"
    webbrowser.open(url)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    # Start a thread to open the browser
    threading.Thread(target=open_browser).start()
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=port, debug=True)