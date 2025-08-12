from django.core.management.base import BaseCommand
from django.conf import settings
import sys
import os
import json
import webbrowser
import time
from pathlib import Path
from urllib.parse import urlencode, parse_qs
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import socket

class Command(BaseCommand):
    help = 'Generate Amazon SP API refresh token using OAuth flow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env-file',
            type=str,
            default='.env.local',
            help='Path to environment file (default: .env.local)'
        )
        parser.add_argument(
            '--output-file',
            type=str,
            default='amazon_refresh_token.json',
            help='Output file to save the refresh token (default: amazon_refresh_token.json)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=8080,
            help='Port for OAuth callback server (default: 8080)'
        )
        parser.add_argument(
            '--no-browser',
            action='store_true',
            help='Do not automatically open browser for OAuth'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Amazon SP API Refresh Token Generator")
        self.stdout.write("=" * 50)
        
        # Load environment variables
        if not self.load_env_file(options['env_file']):
            sys.exit(1)
        
        # Check required credentials
        if not self.check_required_credentials():
            sys.exit(1)
        
        # Generate refresh token
        refresh_token = self.generate_refresh_token(options)
        
        if refresh_token:
            self.save_refresh_token(refresh_token, options['output_file'])
            self.stdout.write(
                self.style.SUCCESS("✅ Refresh token generated successfully!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Failed to generate refresh token")
            )
            sys.exit(1)

    def load_env_file(self, env_file_path):
        """Load environment variables from .env file"""
        env_file = Path.cwd() / env_file_path
        
        if not env_file.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Environment file not found: {env_file}")
            )
            return False
        
        loaded_vars = []
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
                    loaded_vars.append(key)
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Loaded {len(loaded_vars)} environment variables from {env_file}")
        )
        return True

    def check_required_credentials(self):
        """Check if required LWA credentials are present"""
        required_vars = [
            'LWA_APP_ID',
            'LWA_CLIENT_SECRET'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in os.environ:
                missing_vars.append(var)
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f"❌ Missing required credentials: {', '.join(missing_vars)}")
            )
            self.stdout.write("💡 Make sure your .env.local file contains:")
            self.stdout.write("   - LWA_APP_ID (from Amazon Seller Central)")
            self.stdout.write("   - LWA_CLIENT_SECRET (from Amazon Seller Central)")
            return False
        
        self.stdout.write("✅ Required credentials found")
        return True

    def generate_refresh_token(self, options):
        """Generate refresh token using OAuth flow"""
        self.stdout.write("\n🔐 Starting OAuth flow for Amazon SP API...")
        
        # OAuth configuration
        client_id = os.environ['LWA_APP_ID']
        client_secret = os.environ['LWA_CLIENT_SECRET']
        redirect_uri = f"http://localhost:{options['port']}/callback"
        
        # Step 1: Generate authorization URL
        auth_url = self.generate_auth_url(client_id, redirect_uri)
        
        # Step 2: Start local server to handle callback
        auth_code = self.start_oauth_server(auth_url, options['port'], options['no_browser'])
        
        if not auth_code:
            return None
        
        # Step 3: Exchange authorization code for refresh token
        refresh_token = self.exchange_code_for_token(auth_code, client_id, client_secret, redirect_uri)
        
        return refresh_token

    def generate_auth_url(self, client_id, redirect_uri):
        """Generate Amazon OAuth authorization URL"""
        auth_params = {
            'application_id': client_id,
            'state': 'amazon-sp-api-auth',
            'version': 'beta'
        }
        
        auth_url = "https://sellercentral.amazon.com/apps/authorize/consent?" + urlencode(auth_params)
        
        self.stdout.write(f"�� Authorization URL: {auth_url}")
        return auth_url

    def start_oauth_server(self, auth_url, port, no_browser):
        """Start local server to handle OAuth callback"""
        self.stdout.write(f"\n🌐 Starting OAuth callback server on port {port}...")
        
        # Create a simple HTTP server to handle the callback
        callback_data = {'auth_code': None, 'error': None}
        
        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/callback'):
                    # Parse query parameters
                    query = self.path.split('?', 1)[1] if '?' in self.path else ''
                    params = parse_qs(query)
                    
                    if 'code' in params:
                        callback_data['auth_code'] = params['code'][0]
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        success_html = """
                        <html>
                        <head><title>OAuth Success</title></head>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: #28a745;">✅ Authorization Successful!</h1>
                            <p>You can close this window now.</p>
                            <p>The refresh token will be generated automatically.</p>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    elif 'error' in params:
                        callback_data['error'] = params['error'][0]
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        error_html = """
                        <html>
                        <head><title>OAuth Error</title></head>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: #dc3545;">❌ Authorization Failed</h1>
                            <p>Error: {error}</p>
                            <p>Please try again.</p>
                        </body>
                        </html>
                        """.format(error=callback_data['error'])
                        self.wfile.write(error_html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not Found")
                
                # Stop the server after handling the request
                threading.Thread(target=self.server.shutdown).start()
            
            def log_message(self, format, *args):
                # Suppress server logs
                pass
        
        try:
            # Start server in a separate thread
            server = HTTPServer(('localhost', port), OAuthCallbackHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Wait a moment for server to start
            time.sleep(1)
            
            # Open browser if not disabled
            if not no_browser:
                self.stdout.write("🌐 Opening browser for OAuth authorization...")
                webbrowser.open(auth_url)
            else:
                self.stdout.write(f"🌐 Please open this URL in your browser: {auth_url}")
            
            # Wait for callback
            self.stdout.write("⏳ Waiting for OAuth callback...")
            while callback_data['auth_code'] is None and callback_data['error'] is None:
                time.sleep(1)
            
            if callback_data['error']:
                self.stdout.write(
                    self.style.ERROR(f"❌ OAuth error: {callback_data['error']}")
                )
                return None
            
            auth_code = callback_data['auth_code']
            self.stdout.write("✅ Authorization code received")
            return auth_code
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to start OAuth server: {e}")
            )
            return None

    def exchange_code_for_token(self, auth_code, client_id, client_secret, redirect_uri):
        """Exchange authorization code for refresh token"""
        self.stdout.write("\n🔄 Exchanging authorization code for refresh token...")
        
        token_url = "https://api.amazon.com/auth/o2/token"
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            token_response = response.json()
            
            if 'refresh_token' in token_response:
                refresh_token = token_response['refresh_token']
                self.stdout.write("✅ Refresh token received from Amazon")
                return refresh_token
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ No refresh token in response: {token_response}")
                )
                return None
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to exchange code for token: {e}")
            )
            return None

    def save_refresh_token(self, refresh_token, output_file):
        """Save refresh token to output file"""
        output_path = Path.cwd() / output_file
        
        token_data = {
            'refresh_token': refresh_token,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'note': 'Generated using Django management command'
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            self.stdout.write(f"💾 Refresh token saved to: {output_path}")
            
            # Also show the token
            self.stdout.write("\n🔑 Your new refresh token:")
            self.stdout.write(f"   {refresh_token}")
            
            # Show how to use it
            self.stdout.write("\n�� To use this token, add it to your .env.local file:")
            self.stdout.write(f"   SP_API_REFRESH_TOKEN={refresh_token}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to save refresh token: {e}")
            )

    def get_available_port(self, start_port=8080):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port
