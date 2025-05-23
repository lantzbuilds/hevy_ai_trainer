"""
Run script for the AI Personal Trainer application with improved hot-reloading support.
"""

import os
import subprocess
import sys
import time
from typing import List

import streamlit as st
from dotenv import load_dotenv


def run_streamlit(args: List[str] = None):
    """Run Streamlit with hot-reloading enabled."""
    if args is None:
        args = []

    # Base command with hot-reloading enabled
    cmd = [
        "streamlit",
        "run",
        "app.py",
        "--server.runOnSave=true",
        "--server.fileWatcherType=watchdog",
        "--logger.level=debug",
        "--client.showSidebarNavigation=false",
    ]

    # Add any additional arguments
    cmd.extend(args)

    # Run the command
    subprocess.run(cmd)


def check_couchdb_running():
    """Check if CouchDB container is running using docker-compose."""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "couchdb"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "up" in result.stdout
    except subprocess.TimeoutExpired:
        print("Timeout checking CouchDB container status")
        return False
    except subprocess.CalledProcessError:
        return False


def check_couchdb_exists():
    """Check if CouchDB container exists (running or stopped) using docker-compose."""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "-a", "couchdb"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "couchdb" in result.stdout
    except subprocess.TimeoutExpired:
        print("Timeout checking CouchDB container existence")
        return False
    except subprocess.CalledProcessError:
        return False


def start_couchdb():
    """Start CouchDB container using docker-compose if not already running."""
    if not check_couchdb_running():
        print("Starting CouchDB container using docker-compose...")
        try:
            subprocess.run(
                ["docker-compose", "up", "-d", "couchdb"],
                check=True,
            )
            # Wait for CouchDB to be ready
            print("Waiting for CouchDB to be ready...")
            time.sleep(5)  # Give CouchDB time to start
        except subprocess.CalledProcessError as e:
            print(f"Error starting CouchDB container: {e}")
            raise


def check_docker_running():
    """Check if Docker Desktop is running."""
    try:
        # Try to get Docker version - this will fail if Docker Desktop isn't running
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return False


def main():
    """Main function to run the application."""
    # Load environment variables
    load_dotenv()

    # Check if Docker Desktop is running
    if not check_docker_running():
        print(
            "Docker Desktop is not running. Please start Docker Desktop and try again."
        )
        return

    # Check and start CouchDB if needed
    start_couchdb()

    # Run the Streamlit app
    run_streamlit()


if __name__ == "__main__":
    # Get any additional arguments passed to the script
    args = sys.argv[1:]
    main()
