#!/usr/bin/env python3
"""
FRONTEND HTTP SERVER
====================
This is a simple HTTP server that serves the static frontend files.

WHAT IT DOES:
- Listens on port 5000 (0.0.0.0 means all network interfaces)
- Serves HTML, CSS, JavaScript, and image files
- Adds cache-control headers to prevent caching issues

WHY NOT JUST USE A BROWSER?
- We need a web server so the frontend can:
  1. Load HTML files correctly
  2. Serve files with proper MIME types
  3. Make relative path requests work
  4. Be accessible from the network (0.0.0.0:5000)

HOW IT WORKS:
1. Start listening on 0.0.0.0:5000
2. When browser requests index.html → serve it
3. When browser requests style.css → serve it with CSS headers
4. When browser requests image.jpg → serve it with image headers
5. For development, disable caching to see changes immediately
"""

import http.server
import socketserver
import os

# Port to listen on
# Frontend must be accessible at http://0.0.0.0:5000/
PORT = 5000

# =============================================================================
# CUSTOM REQUEST HANDLER
# =============================================================================
# Extend SimpleHTTPRequestHandler to add cache control headers
class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler that disables caching.
    
    WHY DISABLE CACHING?
    - During development, changes aren't visible if browser caches files
    - Cache-Control headers tell browser not to cache
    - Ensures users always get latest version
    - Safe to disable during development, should be enabled in production
    
    HEADERS SENT:
    - Cache-Control: no-cache, no-store, must-revalidate
      → Don't cache, don't store, revalidate with server every time
    - Pragma: no-cache (for HTTP/1.0 compatibility)
    - Expires: 0 (already expired)
    """
    
    def end_headers(self):
        """
        Override end_headers to add cache control headers.
        
        This is called right before the response body is sent.
        We add headers here so they apply to all responses.
        """
        # Tell browser not to cache
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        # Call parent class to send remaining headers
        super().end_headers()

# =============================================================================
# SERVER STARTUP
# =============================================================================

# Change to the directory where this script is located
# This ensures we serve files from the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Allow port reuse (helpful during development when restarting server)
# Without this, might get "Address already in use" error
socketserver.TCPServer.allow_reuse_address = True

# Create and start the server
# TCPServer(address, request_handler)
# - (0.0.0.0, 5000): Listen on all interfaces, port 5000
# - NoCacheHTTPRequestHandler: Use our custom handler
with socketserver.TCPServer(("0.0.0.0", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Frontend Server running at http://0.0.0.0:{PORT}/")
    print(f"Serving files from: {os.getcwd()}")
    print("Press Ctrl+C to stop the server")
    
    # Keep server running indefinitely
    # serve_forever() blocks until server is stopped
    httpd.serve_forever()
