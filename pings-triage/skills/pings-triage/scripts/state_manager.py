#!/usr/bin/env python3
"""
State and Config Manager for Pings Triage Plugin

Manages persistent state and configuration stored in the working folder's
.pings-triage directory. This ensures config is writable (not in read-only
plugin folder) and keeps all plugin data together.

Config: {base_path}/.pings-triage/config.json
State: {base_path}/.pings-triage/state.json
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigManager:
    """Manages plugin configuration stored in working folder."""

    DEFAULT_CONFIG = {
        "version": "2.0.0",
        "linear": {
            "team_id": "",
            "status_new": "Triage",
            "status_done": "Done"
        },
        "platforms": {
            "slack": {"enabled": True},
            "p2": {"enabled": True},
            "figma": {"enabled": False}
        },
        "user": {
            "name": "",
            "email": "",
            "role": "",
            "context": ""
        }
    }

    def __init__(self, base_path: str = None):
        """
        Initialize config manager.

        Args:
            base_path: Base directory for .pings-triage folder.
                       Defaults to current working directory.
        """
        if base_path is None:
            base_path = os.getcwd()

        self.base_path = Path(base_path)
        self.config_dir = self.base_path / ".pings-triage"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from JSON file, or return default if doesn't exist."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None

    def exists(self) -> bool:
        """Check if config file exists."""
        return self.config_file.exists()

    def is_valid(self) -> bool:
        """Check if config exists and has required fields."""
        if not self.exists():
            return False

        config = self.config
        if not config:
            return False

        # Must have Linear team configured
        if not config.get("linear", {}).get("team_id"):
            return False

        # Must have at least one platform enabled
        platforms = config.get("platforms", {})
        if not any(p.get("enabled") for p in platforms.values()):
            return False

        return True

    def save(self, config: Dict[str, Any] = None):
        """Save config to JSON file."""
        if config is not None:
            self.config = config

        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key (supports dot notation like 'linear.team_id')."""
        if not self.config:
            return default

        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set config value by key (supports dot notation)."""
        if self.config is None:
            self.config = self.DEFAULT_CONFIG.copy()

        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def create_default(self) -> Dict[str, Any]:
        """Create and save default config."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
        return self.config

    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platform names."""
        if not self.config:
            return []
        platforms = self.config.get("platforms", {})
        return [name for name, settings in platforms.items() if settings.get("enabled")]

    def get_user_context(self) -> str:
        """Get formatted user context for analysis prompt."""
        if not self.config:
            return "No user context configured."

        user = self.config.get("user", {})
        parts = []

        if user.get("role"):
            parts.append(f"- Role: {user['role']}")
        if user.get("context"):
            parts.append(f"- {user['context']}")

        return "\n".join(parts) if parts else "No specific context provided."


class StateManager:
    """Manages persistent state for ping triage system."""

    def __init__(self, base_path: str = None):
        """
        Initialize state manager.

        Args:
            base_path: Base directory for .pings-triage folder.
                       Defaults to current working directory.
        """
        if base_path is None:
            base_path = os.getcwd()

        self.base_path = Path(base_path)
        self.state_dir = self.base_path / ".pings-triage"
        self.state_file = self.state_dir / "state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from JSON file, or initialize if doesn't exist."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return self._create_default_state()

    def _create_default_state(self) -> Dict[str, Any]:
        """Create default state structure."""
        return {
            "last_fetch": {},
            "pings": {},
            "threads": {},
            "metadata": {
                "version": "2.0.0",
                "created_at": datetime.now().isoformat()
            }
        }

    def save_state(self):
        """Save current state to JSON file."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    @staticmethod
    def generate_ping_id(platform: str, message_id: str, timestamp: str) -> str:
        """Generate unique ping ID from platform, message ID, and timestamp."""
        content = f"{platform}:{message_id}:{timestamp}"
        return f"ping-{hashlib.sha256(content.encode()).hexdigest()[:32]}"

    @staticmethod
    def generate_thread_id(platform: str, thread_identifier: str) -> str:
        """Generate thread ID for grouping related pings."""
        return f"{platform}-{thread_identifier}"

    def get_last_fetch(self, platform: str) -> Optional[str]:
        """Get last fetch timestamp for a platform."""
        return self.state.get("last_fetch", {}).get(platform)

    def set_last_fetch(self, platform: str, timestamp: str = None):
        """Record last fetch time for a platform."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        if "last_fetch" not in self.state:
            self.state["last_fetch"] = {}

        self.state["last_fetch"][platform] = timestamp
        self.save_state()

    def get_fetch_start_date(self, platform: str, max_lookback_days: int = 30) -> str:
        """
        Get the start date for fetching pings.

        If last_fetch exists for platform, returns that date.
        Otherwise returns max_lookback_days ago (default 30 days).
        """
        last_fetch = self.get_last_fetch(platform)
        if last_fetch:
            return last_fetch

        # First run: look back max_lookback_days
        lookback_date = datetime.now() - timedelta(days=max_lookback_days)
        return lookback_date.isoformat()

    def add_ping(
        self,
        platform: str,
        message_id: str,
        timestamp: str,
        author: str,
        content: str,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add a new ping to state.

        Returns:
            ping_id: Unique identifier for this ping
        """
        ping_id = self.generate_ping_id(platform, message_id, timestamp)

        # Check if ping already exists
        if ping_id in self.state["pings"]:
            return ping_id

        self.state["pings"][ping_id] = {
            "id": ping_id,
            "platform": platform,
            "message_id": message_id,
            "timestamp": timestamp,
            "author": author,
            "content": content,
            "thread_id": thread_id,
            "status": "new",  # new, analyzed, synced
            "analysis": None,
            "linear_issue_id": None,
            "response_detected": False,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Add to thread if thread_id provided
        if thread_id:
            self._add_to_thread(thread_id, ping_id)

        self.save_state()
        return ping_id

    def _add_to_thread(self, thread_id: str, ping_id: str):
        """Add ping to thread group."""
        if thread_id not in self.state["threads"]:
            self.state["threads"][thread_id] = {
                "id": thread_id,
                "ping_ids": [],
                "linear_issue_id": None,
                "created_at": datetime.now().isoformat()
            }

        if ping_id not in self.state["threads"][thread_id]["ping_ids"]:
            self.state["threads"][thread_id]["ping_ids"].append(ping_id)

    def get_ping(self, ping_id: str) -> Optional[Dict]:
        """Get ping by ID."""
        return self.state["pings"].get(ping_id)

    def get_thread_pings(self, thread_id: str) -> List[Dict]:
        """Get all pings in a thread."""
        thread = self.state["threads"].get(thread_id)
        if not thread:
            return []

        return [
            self.state["pings"][pid]
            for pid in thread["ping_ids"]
            if pid in self.state["pings"]
        ]

    def get_thread_linear_issue(self, thread_id: str) -> Optional[str]:
        """Get Linear issue ID for a thread, if one exists."""
        thread = self.state["threads"].get(thread_id)
        if thread:
            return thread.get("linear_issue_id")
        return None

    def update_ping_analysis(self, ping_id: str, analysis: Dict):
        """Update ping with analysis results."""
        if ping_id in self.state["pings"]:
            self.state["pings"][ping_id]["analysis"] = analysis
            self.state["pings"][ping_id]["status"] = "analyzed"
            self.state["pings"][ping_id]["updated_at"] = datetime.now().isoformat()
            self.save_state()

    def mark_ping_responded(self, ping_id: str):
        """Mark ping as having been responded to."""
        if ping_id in self.state["pings"]:
            self.state["pings"][ping_id]["response_detected"] = True
            self.state["pings"][ping_id]["updated_at"] = datetime.now().isoformat()
            self.save_state()

    def link_linear_issue(self, ping_id: str, linear_issue_id: str):
        """Link ping to Linear issue."""
        if ping_id in self.state["pings"]:
            self.state["pings"][ping_id]["linear_issue_id"] = linear_issue_id
            self.state["pings"][ping_id]["status"] = "synced"
            self.state["pings"][ping_id]["updated_at"] = datetime.now().isoformat()

            # Also update thread if ping is part of thread
            thread_id = self.state["pings"][ping_id].get("thread_id")
            if thread_id and thread_id in self.state["threads"]:
                self.state["threads"][thread_id]["linear_issue_id"] = linear_issue_id

            self.save_state()

    def get_unanalyzed_pings(self) -> List[Dict]:
        """Get all pings that need analysis (status=new)."""
        return [
            ping for ping in self.state["pings"].values()
            if ping["status"] == "new"
        ]

    def get_analyzed_pings(self) -> List[Dict]:
        """Get all analyzed pings that haven't been synced yet."""
        return [
            ping for ping in self.state["pings"].values()
            if ping["status"] == "analyzed"
        ]

    def get_responded_pings(self) -> List[Dict]:
        """Get pings where response was detected."""
        return [
            ping for ping in self.state["pings"].values()
            if ping.get("response_detected") and ping.get("linear_issue_id")
        ]

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about current state."""
        pings = self.state["pings"].values()

        return {
            "total_pings": len(self.state["pings"]),
            "new_pings": len([p for p in pings if p["status"] == "new"]),
            "analyzed_pings": len([p for p in pings if p["status"] == "analyzed"]),
            "synced_pings": len([p for p in pings if p["status"] == "synced"]),
            "responded_pings": len([p for p in pings if p.get("response_detected")]),
            "total_threads": len(self.state["threads"])
        }


if __name__ == "__main__":
    # Example usage
    print("Testing ConfigManager...")
    cm = ConfigManager()
    print(f"Config exists: {cm.exists()}")
    print(f"Config valid: {cm.is_valid()}")

    print("\nTesting StateManager...")
    sm = StateManager()
    print(f"Stats: {sm.get_stats()}")

    # Test fetch date logic
    print(f"\nSlack fetch start (first run): {sm.get_fetch_start_date('slack')}")
