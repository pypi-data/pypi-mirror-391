"""
CLI entry point for Memory Hub HTTP Server
Runs FastAPI server with uvicorn for authenticated HTTP access
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

import uvicorn
from .http_server import create_http_server
from .core.services import AppConfig, startup_event, shutdown_event
from .core.auth import AuthManager

# Configure file-based logging (HTTP server uses different log file than stdio MCP)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='/tmp/memory-hub-http.log',
    filemode='a'
)
logger = logging.getLogger(__name__)
logger.info("Memory Hub HTTP Server starting...")

def main():
    """Main CLI entry point for HTTP server"""
    parser = argparse.ArgumentParser(
        description="Memory Hub HTTP Server - REST API with authentication"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--users-config",
        type=str,
        default="config/users.yaml",
        help="Path to users configuration file (default: config/users.yaml)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--qdrant-url",
        type=str,
        default=None,
        help="URL for the Qdrant service (e.g., http://localhost:6333)"
    )
    parser.add_argument(
        "--lm-studio-url",
        type=str,
        default=None,
        help="Base URL for the LM Studio service (e.g., http://localhost:1234/v1)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Resolve users config path (support relative to project root)
    users_config_path = Path(args.users_config)
    if not users_config_path.is_absolute():
        # Try relative to current working directory first
        if not users_config_path.exists():
            # Try relative to this file's location (package root)
            package_root = Path(__file__).parent.parent.parent
            users_config_path = package_root / args.users_config

    if not users_config_path.exists():
        logger.error(f"Users config file not found: {users_config_path}")
        print(f"ERROR: Users config file not found: {users_config_path}")
        print(f"Please create {args.users_config} with user authentication configuration")
        sys.exit(1)

    # Create config object
    config = AppConfig(
        qdrant_url=args.qdrant_url,
        lm_studio_url=args.lm_studio_url
    )

    # Initialize auth manager
    try:
        auth_manager = AuthManager(str(users_config_path))
        logger.info(f"Loaded user authentication from {users_config_path}")
    except Exception as e:
        logger.error(f"Failed to initialize authentication: {e}")
        print(f"ERROR: Failed to load users configuration: {e}")
        sys.exit(1)

    # Run startup initialization
    try:
        asyncio.run(startup_event(config))
        logger.info(f"Memory Hub HTTP Server initialized with config: {config}")
    except Exception as e:
        logger.error(f"Failed to initialize Memory Hub services: {e}")
        print(f"ERROR: Failed to initialize Memory Hub: {e}")
        sys.exit(1)

    # Create HTTP server
    try:
        http_server = create_http_server(config, auth_manager)
        logger.info(f"HTTP server created, listening on {args.host}:{args.port}")
    except Exception as e:
        logger.error(f"Failed to create HTTP server: {e}")
        print(f"ERROR: Failed to create HTTP server: {e}")
        sys.exit(1)

    # Run uvicorn
    print(f"Starting Memory Hub HTTP Server on http://{args.host}:{args.port}")
    print(f"API documentation: http://{args.host}:{args.port}/docs")
    print(f"Logs: /tmp/memory-hub-http.log")

    try:
        uvicorn.run(
            http_server.app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower()
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown by user")
        print("\nShutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"ERROR: Server error: {e}")
        sys.exit(1)
    finally:
        # Run shutdown cleanup
        try:
            asyncio.run(shutdown_event(config))
            logger.info("Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    main()
