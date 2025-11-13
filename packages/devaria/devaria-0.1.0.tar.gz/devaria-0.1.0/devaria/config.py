"""Configuration management for the Devaria runner."""

import json
import os
import socket
import uuid
from pathlib import Path
from typing import Optional


# Hard-coded configuration
WORKER_URL = os.getenv("DEVARIA_WORKER_URL", "https://devaria-worker.neurosift.app")
POLL_INTERVAL = 30  # seconds
HEARTBEAT_INTERVAL = 30  # seconds
CONFIG_FILE = ".devaria_runner.json"
LOG_FILE = "devaria_runner.log"


class RunnerConfig:
    """Manages runner configuration persistence."""

    def __init__(self, config_file: str = CONFIG_FILE):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.runner_id: Optional[str] = None
        self.runner_name: Optional[str] = None

    def load(self) -> bool:
        """Load configuration from file if it exists.
        
        Returns:
            True if config was loaded, False if file doesn't exist
        """
        if not self.config_file.exists():
            return False

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.runner_id = data.get('runner_id')
                self.runner_name = data.get('runner_name')
                return True
        except (json.JSONDecodeError, IOError) as e:
            # If config file is corrupted, we'll create a new one
            return False

    def save(self) -> None:
        """Save configuration to file."""
        data = {
            'runner_id': self.runner_id,
            'runner_name': self.runner_name
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_name(self) -> str:
        """Generate a unique runner name.
        
        Returns:
            Generated runner name in format: runner-{hostname}-{uuid}
        """
        hostname = socket.gethostname()
        unique_id = str(uuid.uuid4())[:8]
        return f"runner-{hostname}-{unique_id}"

    def set_runner_info(self, runner_id: str, runner_name: str) -> None:
        """Set runner information and save to file.
        
        Args:
            runner_id: The runner ID from registration
            runner_name: The runner name
        """
        self.runner_id = runner_id
        self.runner_name = runner_name
        self.save()
