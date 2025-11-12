import asyncio
import webbrowser
import json
import base64
from datetime import datetime, timezone
from typing import Optional, Tuple
from aiohttp import web
import httpx
from rich.console import Console


AUTH_LINK_URL = "http://apps.advancegroup.com/auth-link/login"
VERIFY_URL = "http://apps.advancegroup.com/auth-link/api/verify"
CALLBACK_PORT = 12345
CALLBACK_HOST = "127.0.0.1"


class LoginError(Exception):
    """Raised when login fails"""
    pass


class CallbackServer:
    """HTTP server that receives OAuth callback with JWT token"""

    def __init__(self, port: int = CALLBACK_PORT):
        self.port = port
        self.token: Optional[str] = None
        self.app = web.Application()
        self.app.router.add_post("/", self.handle_callback)
        self.app.router.add_options("/", self.handle_options)
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self._token_received = asyncio.Event()

    async def handle_options(self, request: web.Request) -> web.Response:
        """Handle CORS preflight OPTIONS request"""
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )

    async def handle_callback(self, request: web.Request) -> web.Response:
        """Handle POST callback from auth-link with JWT token"""
        try:
            data = await request.json()
            self.token = data.get("token")

            if not self.token:
                return web.Response(
                    text="Error: No token received",
                    status=400,
                    content_type="text/html",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "POST, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type",
                    }
                )

            self._token_received.set()

            html_response = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authentication Successful</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 3rem;
                        border-radius: 1rem;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                        max-width: 400px;
                    }
                    .success-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                    }
                    h1 {
                        color: #2d3748;
                        margin-bottom: 0.5rem;
                    }
                    p {
                        color: #718096;
                        margin-bottom: 2rem;
                    }
                    .close-text {
                        font-size: 0.9rem;
                        color: #a0aec0;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✓</div>
                    <h1>Authentication Successful!</h1>
                    <p>You have successfully logged in to JVS CLI.</p>
                    <p class="close-text">You can close this window and return to your terminal.</p>
                </div>
            </body>
            </html>
            """

            return web.Response(
                text=html_response,
                content_type="text/html",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                }
            )

        except Exception as e:
            return web.Response(
                text=f"Error processing callback: {str(e)}",
                status=500,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                }
            )

    async def start(self) -> None:
        """Start the callback server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, CALLBACK_HOST, self.port)
        await self.site.start()

    async def wait_for_token(self, timeout: float = 300.0) -> Optional[str]:
        """Wait for token to be received, with timeout"""
        try:
            await asyncio.wait_for(self._token_received.wait(), timeout=timeout)
            return self.token
        except asyncio.TimeoutError:
            return None

    async def stop(self) -> None:
        """Stop the callback server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()


def decode_jwt_expiry(token: str) -> Optional[datetime]:
    """
    Decode JWT token and extract expiration time.
    Returns datetime in UTC or None if unable to parse.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)

        exp_timestamp = payload_data.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        return None
    except Exception:
        return None


def is_token_valid(token_expires_at: Optional[str]) -> bool:
    """
    Check if token is still valid based on expiration time.
    Returns False if token is expired or expiration time is invalid.
    """
    if not token_expires_at:
        return False

    try:
        expires_at = datetime.fromisoformat(token_expires_at)
        now = datetime.now(timezone.utc)

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return now < expires_at
    except Exception:
        return False


async def verify_token(token: str, console: Optional[Console] = None) -> bool:
    """
    Verify JWT token with auth-link verify endpoint.
    Returns True if token is valid, False otherwise.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                VERIFY_URL,
                json={"token": token},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("success", False)
            else:
                if console:
                    console.print(f"[dim]Verify endpoint returned status {response.status_code}[/dim]")
                return False
    except Exception as e:
        if console:
            console.print(f"[dim]Token verification request failed: {e}[/dim]")
        return False


def open_browser(url: str, console: Console) -> bool:
    """
    Open URL in default browser.
    Returns True if successful, False otherwise.
    """
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        console.print(f"[yellow]Could not open browser automatically: {e}[/yellow]")
        console.print(f"\nPlease open this URL manually:\n[cyan]{url}[/cyan]\n")
        return False


async def login(console: Optional[Console] = None, port: int = CALLBACK_PORT) -> Tuple[str, datetime]:
    """
    Perform OAuth login flow with auth-link.

    Returns:
        Tuple of (jwt_token, expires_at)

    Raises:
        LoginError: If login fails
    """
    if console is None:
        console = Console()

    server = CallbackServer(port=port)

    try:
        console.print("[cyan]Starting authentication...[/cyan]")

        await server.start()
        console.print(f"[dim]Listening for callback on http://{CALLBACK_HOST}:{port}[/dim]")

        console.print(f"[cyan]Opening browser to: {AUTH_LINK_URL}[/cyan]")
        open_browser(AUTH_LINK_URL, console)

        console.print("\n[yellow]Waiting for authentication (timeout: 5 minutes)...[/yellow]")
        console.print("[dim]Please complete the login in your browser[/dim]\n")

        token = await server.wait_for_token(timeout=300.0)

        if not token:
            raise LoginError("Authentication timed out. Please try again.")

        console.print("[green]✓[/green] Token received")

        # Try to verify token, but don't fail if verification endpoint is down
        console.print("[cyan]Verifying token...[/cyan]")
        is_valid = await verify_token(token, console)

        if is_valid:
            console.print("[green]✓[/green] Token verified")
        else:
            console.print("[yellow]⚠[/yellow] Token verification endpoint unavailable, proceeding with JWT decode...")

        # Parse token expiration
        expires_at = decode_jwt_expiry(token)
        if not expires_at:
            # Token verification failed and can't parse expiration
            if not is_valid:
                raise LoginError("Token verification failed and could not parse token expiration")
            raise LoginError("Could not parse token expiration")

        console.print(f"[dim]Token expires at: {expires_at.isoformat()}[/dim]")

        return token, expires_at

    except LoginError:
        raise
    except Exception as e:
        raise LoginError(f"Login failed: {str(e)}")
    finally:
        await server.stop()


def extract_user_info(token: str) -> dict:
    """
    Extract user information from JWT token.
    Returns dict with user_id, name, email, avatar.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}

        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding

        decoded = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded)

        return {
            "user_id": payload_data.get("sub", ""),
            "name": payload_data.get("name", ""),
            "email": payload_data.get("email", ""),
            "avatar": payload_data.get("avatar", ""),
        }
    except Exception:
        return {}
