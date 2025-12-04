"""
Automatic MCP Server Management

This module provides automatic start/stop of the MCP server when needed.
No need to manually activate/deactivate - it handles everything for you.
"""

import os
import sys
import time
import signal
import subprocess
import requests
from pathlib import Path
from typing import Optional
import atexit


class MCPServerManager:
    """
    Manages automatic MCP server lifecycle.
    
    Usage:
        # Option 1: Context manager (auto cleanup)
        with MCPServerManager() as server:
            # Server is running here
            client = MCPClient()
            result = client.search_leads("cloud")
        # Server automatically stopped
        
        # Option 2: Singleton instance (auto cleanup on exit)
        server = MCPServerManager.get_instance()
        server.ensure_running()
        # Use MCP client...
        # Server automatically stopped when program exits
    """
    
    _instance = None
    _process = None
    _port = 8001
    _url = "http://localhost:8001/sse/"
    
    def __init__(self, port: int = 8001, auto_start: bool = True):
        """
        Initialize MCP server manager.
        
        Args:
            port: Port for MCP server (default: 8001)
            auto_start: Start server immediately if True
        """
        self.port = port
        self.url = f"http://localhost:{port}/sse/"
        self.process: Optional[subprocess.Popen] = None
        self.started_by_us = False
        
        if auto_start:
            self.ensure_running()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    @classmethod
    def get_instance(cls, port: int = 8001) -> 'MCPServerManager':
        """
        Get singleton instance of server manager.
        
        This ensures only one server manager exists and handles cleanup automatically.
        """
        if cls._instance is None:
            cls._instance = cls(port=port, auto_start=False)
        return cls._instance
    
    def is_running(self) -> bool:
        """Check if MCP server is already running."""
        try:
            # Try to connect to the SSE endpoint
            response = requests.get(
                f"http://localhost:{self.port}/sse",
                timeout=1,
                stream=True
            )
            # SSE endpoint may return 200 or start streaming
            return True
        except requests.exceptions.ConnectionError:
            # Server not reachable
            return False
        except requests.exceptions.Timeout:
            # Timeout might mean server is starting
            return False
        except Exception as e:
            # Any other error, assume not running
            return False
    
    def ensure_running(self) -> bool:
        """
        Ensure MCP server is running, start it if needed.
        
        Returns:
            True if server is running, False if failed to start
        """
        # Check if already running
        if self.is_running():
            if self.process is None:
                print(f"✓ MCP server already running on port {self.port}")
            return True
        
        # Start the server
        return self.start()
    
    def start(self) -> bool:
        """
        Start MCP server in background.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running():
            print(f"✓ MCP server already running on port {self.port}")
            return True
        
        print(f"🚀 Starting MCP server on port {self.port}...")
        
        # Get path to mcp_server.py
        project_root = Path(__file__).parent.parent
        server_script = project_root / "mcp_server.py"
        
        if not server_script.exists():
            print(f"❌ MCP server script not found: {server_script}")
            return False
        
        # Load .env file for environment variables
        env_file = project_root / ".env"
        env = os.environ.copy()
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            # Copy loaded env vars to subprocess env
            for key in ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']:
                if key in os.environ:
                    env[key] = os.environ[key]
        
        # Get Python executable (use venv if available)
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
        python_exe = str(venv_python) if venv_python.exists() else sys.executable
        
        # Start server as subprocess
        try:
            # Use CREATE_NEW_PROCESS_GROUP to allow graceful shutdown
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            
            self.process = subprocess.Popen(
                [python_exe, str(server_script)],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags,
                env=env,  # Pass environment variables
                # Detach from parent on Unix
                preexec_fn=None if sys.platform == 'win32' else os.setpgrp
            )
            
            self.started_by_us = True
            
            # Wait for server to be ready (max 15 seconds)
            print(f"⏳ Waiting for server to start (PID: {self.process.pid})...")
            for i in range(30):
                time.sleep(0.5)
                
                # Check if process died
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    print(f"❌ Server process exited unexpectedly")
                    if stderr:
                        print(f"Error: {stderr.decode()[:500]}")
                    self.started_by_us = False
                    return False
                
                if self.is_running():
                    print(f"✓ MCP server started successfully (PID: {self.process.pid})")
                    return True
            
            # Server didn't start in time
            print("❌ MCP server failed to start (timeout)")
            stdout, stderr = self.process.communicate(timeout=2)
            if stderr:
                print(f"Server stderr: {stderr.decode()[:500]}")
            self.stop()
            return False
            # Wait for server to be ready (max 10 seconds)
            for i in range(20):
                time.sleep(0.5)
                if self.is_running():
                    print(f"✓ MCP server started successfully (PID: {self.process.pid})")
                    return True
            
            # Server didn't start in time
            print("❌ MCP server failed to start (timeout)")
            self.stop()
            return False
            
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def stop(self):
        """Stop MCP server if we started it."""
        if self.process and self.started_by_us:
            print(f"🛑 Stopping MCP server (PID: {self.process.pid})...")
            try:
                if sys.platform == 'win32':
                    # On Windows, send CTRL_BREAK_EVENT
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    # On Unix, send SIGTERM
                    self.process.terminate()
                
                # Wait for graceful shutdown (max 5 seconds)
                try:
                    self.process.wait(timeout=5)
                    print("✓ MCP server stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if not stopped
                    self.process.kill()
                    self.process.wait()
                    print("✓ MCP server force stopped")
                
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
            
            finally:
                self.process = None
                self.started_by_us = False
    
    def cleanup(self):
        """Cleanup on exit."""
        if self.started_by_us:
            self.stop()
    
    def __enter__(self):
        """Context manager entry - ensure server is running."""
        self.ensure_running()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop server if we started it."""
        self.stop()
        return False


# Convenience function for quick usage
def with_mcp_server(func):
    """
    Decorator to automatically manage MCP server for a function.
    
    Usage:
        @with_mcp_server
        def my_function():
            client = MCPClient()
            result = client.search_leads("cloud")
            return result
    """
    def wrapper(*args, **kwargs):
        with MCPServerManager():
            return func(*args, **kwargs)
    return wrapper


# Example usage
if __name__ == "__main__":
    print("="*70)
    print("MCP SERVER MANAGER TEST")
    print("="*70)
    
    # Test 1: Context manager
    print("\nTest 1: Context Manager")
    print("-" * 70)
    with MCPServerManager() as server:
        print(f"Server running: {server.is_running()}")
        print("Doing work with MCP server...")
        time.sleep(2)
    print("Context exited - server should be stopped")
    
    print("\n" + "="*70)
    
    # Test 2: Singleton instance
    print("\nTest 2: Singleton Instance")
    print("-" * 70)
    manager = MCPServerManager.get_instance()
    manager.ensure_running()
    print(f"Server running: {manager.is_running()}")
    print("Doing work with MCP server...")
    time.sleep(2)
    manager.stop()
    print("Manager stopped - server should be stopped")
    
    print("\n" + "="*70)
    print("✅ Tests complete")
