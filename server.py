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
import urllib.request
import urllib.error
import json

# Port to listen on
# Frontend must be accessible at http://0.0.0.0:5000/
PORT = 5000
BACKEND_URL = "http://localhost:8000"

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
    
    def do_GET(self):
        """
        Handle GET requests.
        Proxy /api/* requests to backend, serve static files normally.
        """
        if self.path.startswith('/api/'):
            self._proxy_api_request('GET')
        else:
            super().do_GET()
    
    def do_POST(self):
        """
        Handle POST requests.
        Proxy /api/* requests to backend.
        """
        if self.path.startswith('/api/'):
            self._proxy_api_request('POST')
        else:
            super().do_POST()
    
    def do_PUT(self):
        """Handle PUT requests (proxy to backend)."""
        if self.path.startswith('/api/'):
            self._proxy_api_request('PUT')
        else:
            super().do_PUT()
    
    def do_DELETE(self):
        """Handle DELETE requests (proxy to backend)."""
        if self.path.startswith('/api/'):
            self._proxy_api_request('DELETE')
        else:
            super().do_DELETE()
    
    def _proxy_api_request(self, method):
        """
        Proxy API requests to backend server on port 8000.
        This allows /api/* requests to work from the frontend server on port 5000.
        """
        try:
            # Build full URL for backend (self.path already includes query string)
            full_url = BACKEND_URL + self.path
            
            # Read request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Create request with proper headers
            req = urllib.request.Request(
                full_url,
                data=body,
                method=method,
                headers={k: v for k, v in self.headers.items() if k.lower() != 'host'}
            )
            req.add_header('Host', 'localhost:8000')
            
            # Send request to backend
            with urllib.request.urlopen(req) as response:
                status = response.status
                headers = dict(response.headers)
                content = response.read()
        except urllib.error.HTTPError as e:
            status = e.code
            headers = dict(e.headers)
            content = e.read()
        except Exception as e:
            # Return 502 Bad Gateway if connection fails
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': str(e)}).encode())
            return
        
        # Send response
        self.send_response(status)
        for header, value in headers.items():
            if header.lower() not in ['connection', 'transfer-encoding']:
                self.send_header(header, value)
        self.end_headers()
        self.wfile.write(content)
    
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
