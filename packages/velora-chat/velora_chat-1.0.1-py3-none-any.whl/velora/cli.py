#!/usr/bin/env python3
"""
Velora CLI - Command line interface for Velora chat and file sharing
"""

import sys
import argparse
from .client import VeloraClient
from .server import VeloraServer
from .share import quick_share


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="velora",
        description="Velora - Simple file sharing and chat over TCP sockets"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start chat client")
    chat_parser.add_argument("--host", default=None, help="Server host to connect to")
    chat_parser.add_argument("--port", type=int, default=5003, help="Server port")
    chat_parser.add_argument("--name", default=None, help="Your display name")
    
    # Share command  
    share_parser = subparsers.add_parser("share", help="Quick share a file")
    share_parser.add_argument("file", help="File path to share")
    share_parser.add_argument("server", nargs="?", default=None, 
                             help="Server address (IP:port or ngrok URL)")
    share_parser.add_argument("--name", default="Anonymous", help="Your display name")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Start Velora server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    server_parser.add_argument("--port", type=int, default=5003, help="Port to bind to")
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        # No subcommand, show help
        parser.print_help()
        return
    
    # Execute commands
    if args.command == "chat":
        chat_main(args)
    elif args.command == "share":
        share_main(args)
    elif args.command == "server":
        server_main(args)
    elif args.command == "version":
        from . import __version__
        print(f"Velora {__version__}")


def chat_main(args=None):
    """Start chat client"""
    if args and args.host:
        # Direct connection mode
        client = VeloraClient()
        client.connect_and_chat(args.host, args.port, args.name)
    else:
        # Interactive mode
        client = VeloraClient()
        client.start_interactive()


def share_main(args=None):
    """Quick share a file"""
    if args:
        quick_share(args.file, args.server, args.name)
    else:
        # Called from command line without argparse
        import sys
        if len(sys.argv) < 2:
            print("Usage: velora-share <file_path> [server_address]")
            return
        
        file_path = sys.argv[1]
        server = sys.argv[2] if len(sys.argv) > 2 else None
        name = sys.argv[3] if len(sys.argv) > 3 else "Anonymous"
        
        quick_share(file_path, server, name)


def server_main(args=None):
    """Start Velora server"""
    if args:
        server = VeloraServer(host=args.host, port=args.port)
    else:
        server = VeloraServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")


if __name__ == "__main__":
    main()
