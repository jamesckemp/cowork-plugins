#!/usr/bin/env python3
"""
Config Manager for Pings Triage Plugin

Manages persistent configuration and state stored in the working folder's
.pings-triage directory. This ensures config is writable (not in read-only
plugin folder) and keeps all plugin data together.

Config: {base_path}/.pings-triage/config.json
"""

import json
import hashlib
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages plugin configuration and state stored in working folder."""

    DEFAULT_CONFIG = {
        "version": "3.2.1",
        "linear": {
            "team_id": "",
            "user_id": "",
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
        },
        "state": {
            "last_fetch": {},
            "pings": {},
            "threads": {},
            "synced_urls": [],
            "metadata": {
                "version": "3.2.1",
                "created_at": None
            }
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
        self._session_timestamp = None  # Lazy initialized for session folders

        # Migrate from state.json if it exists
        self._migrate_from_state_json()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from JSON file, or return default if doesn't exist."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                loaded = json.load(f)
                # Ensure state key exists for older configs
                if "state" not in loaded:
                    loaded["state"] = self.DEFAULT_CONFIG["state"].copy()
                    loaded["state"]["metadata"]["created_at"] = datetime.now().isoformat()
                return loaded
        return None

    def _migrate_from_state_json(self):
        """Migrate data from state.json to config.json (one-time migration)."""
        state_file = self.config_dir / "state.json"
        migrated_file = self.config_dir / "state.json.migrated"

        if not state_file.exists() or migrated_file.exists():
            return

        try:
            with open(state_file, 'r') as f:
                old_state = json.load(f)

            if self.config is None:
                self.config = self.DEFAULT_CONFIG.copy()
                self.config["state"]["metadata"]["created_at"] = datetime.now().isoformat()

            # Migrate state data
            self.config["state"]["last_fetch"] = old_state.get("last_fetch", {})
            self.config["state"]["pings"] = old_state.get("pings", {})
            self.config["state"]["threads"] = old_state.get("threads", {})

            # Build synced_urls from existing pings
            synced_urls = []
            for ping in self.config["state"]["pings"].values():
                if ping.get("status") == "synced":
                    url = ping.get("metadata", {}).get("permalink")
                    if url:
                        synced_urls.append(url)
            self.config["state"]["synced_urls"] = synced_urls

            # Save the migrated config
            self._safe_save()

            # Rename state.json to state.json.migrated (preserve, don't delete)
            state_file.rename(migrated_file)
            logger.info(f"Migrated state.json to config.json, renamed to {migrated_file}")

        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to migrate state.json: {e}")

    def _safe_save(self):
        """Save config with permission error handling."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except PermissionError as e:
            logger.warning(f"Permission denied saving config: {e}. Changes may not persist.")
        except IOError as e:
            logger.warning(f"IO error saving config: {e}. Changes may not persist.")

    def get_session_path(self) -> Path:
        """
        Get or create current session folder in working directory.

        Session folders are created at the working folder root (not inside
        .pings-triage) with timestamp format YYYY-MM-DD_HHMM. The timestamp
        is set once per ConfigManager instance, so all files from one triage
        run go in the same folder.

        Returns:
            Path to the session folder (created if it doesn't exist)
        """
        if self._session_timestamp is None:
            self._session_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        session_dir = self.base_path / self._session_timestamp
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def get_session_file(self, filename: str) -> Path:
        """
        Get path for a file in the current session folder.

        Args:
            filename: Name of the file (e.g., "triage_summary.md")

        Returns:
            Full path to the file in the session folder
        """
        return self.get_session_path() / filename

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
        self._safe_save()

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
            self.config["state"]["metadata"]["created_at"] = datetime.now().isoformat()

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
        self.config["state"]["metadata"]["created_at"] = datetime.now().isoformat()
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

    # ========== State Management Methods ==========

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
        return self.get(f"state.last_fetch.{platform}")

    def set_last_fetch(self, platform: str, timestamp: str = None):
        """Record last fetch time for a platform."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        if self.config is None:
            self.config = self.DEFAULT_CONFIG.copy()
            self.config["state"]["metadata"]["created_at"] = datetime.now().isoformat()

        if "state" not in self.config:
            self.config["state"] = self.DEFAULT_CONFIG["state"].copy()

        if "last_fetch" not in self.config["state"]:
            self.config["state"]["last_fetch"] = {}

        self.config["state"]["last_fetch"][platform] = timestamp
        self._safe_save()

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

        if self.config is None:
            self.config = self.DEFAULT_CONFIG.copy()
            self.config["state"]["metadata"]["created_at"] = datetime.now().isoformat()

        if "state" not in self.config:
            self.config["state"] = self.DEFAULT_CONFIG["state"].copy()

        # Check if ping already exists
        if ping_id in self.config["state"]["pings"]:
            return ping_id

        self.config["state"]["pings"][ping_id] = {
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

        self._safe_save()
        return ping_id

    def _add_to_thread(self, thread_id: str, ping_id: str):
        """Add ping to thread group."""
        if "threads" not in self.config["state"]:
            self.config["state"]["threads"] = {}

        if thread_id not in self.config["state"]["threads"]:
            self.config["state"]["threads"][thread_id] = {
                "id": thread_id,
                "ping_ids": [],
                "linear_issue_id": None,
                "created_at": datetime.now().isoformat()
            }

        if ping_id not in self.config["state"]["threads"][thread_id]["ping_ids"]:
            self.config["state"]["threads"][thread_id]["ping_ids"].append(ping_id)

    def get_ping(self, ping_id: str) -> Optional[Dict]:
        """Get ping by ID."""
        return self.get(f"state.pings.{ping_id}")

    def get_thread_pings(self, thread_id: str) -> List[Dict]:
        """Get all pings in a thread."""
        thread = self.get(f"state.threads.{thread_id}")
        if not thread:
            return []

        pings = self.config["state"]["pings"]
        return [
            pings[pid]
            for pid in thread["ping_ids"]
            if pid in pings
        ]

    def get_thread_linear_issue(self, thread_id: str) -> Optional[str]:
        """Get Linear issue ID for a thread, if one exists."""
        thread = self.get(f"state.threads.{thread_id}")
        if thread:
            return thread.get("linear_issue_id")
        return None

    def update_ping_analysis(self, ping_id: str, analysis: Dict):
        """Update ping with analysis results."""
        if self.config and "state" in self.config:
            if ping_id in self.config["state"]["pings"]:
                self.config["state"]["pings"][ping_id]["analysis"] = analysis
                self.config["state"]["pings"][ping_id]["status"] = "analyzed"
                self.config["state"]["pings"][ping_id]["updated_at"] = datetime.now().isoformat()
                self._safe_save()

    def mark_ping_responded(self, ping_id: str):
        """Mark ping as having been responded to."""
        if self.config and "state" in self.config:
            if ping_id in self.config["state"]["pings"]:
                self.config["state"]["pings"][ping_id]["response_detected"] = True
                self.config["state"]["pings"][ping_id]["updated_at"] = datetime.now().isoformat()
                self._safe_save()

    def link_linear_issue(self, ping_id: str, linear_issue_id: str):
        """Link ping to Linear issue."""
        if self.config and "state" in self.config:
            if ping_id in self.config["state"]["pings"]:
                self.config["state"]["pings"][ping_id]["linear_issue_id"] = linear_issue_id
                self.config["state"]["pings"][ping_id]["status"] = "synced"
                self.config["state"]["pings"][ping_id]["updated_at"] = datetime.now().isoformat()

                # Also update thread if ping is part of thread
                thread_id = self.config["state"]["pings"][ping_id].get("thread_id")
                if thread_id and thread_id in self.config["state"]["threads"]:
                    self.config["state"]["threads"][thread_id]["linear_issue_id"] = linear_issue_id

                # Add URL to synced_urls for fast deduplication
                url = self.config["state"]["pings"][ping_id].get("metadata", {}).get("permalink")
                if url:
                    self.mark_url_synced(url)

                self._safe_save()

    def get_unanalyzed_pings(self) -> List[Dict]:
        """Get all pings that need analysis (status=new)."""
        if not self.config or "state" not in self.config:
            return []
        return [
            ping for ping in self.config["state"]["pings"].values()
            if ping["status"] == "new"
        ]

    def get_analyzed_pings(self) -> List[Dict]:
        """Get all analyzed pings that haven't been synced yet."""
        if not self.config or "state" not in self.config:
            return []
        return [
            ping for ping in self.config["state"]["pings"].values()
            if ping["status"] == "analyzed"
        ]

    def get_responded_pings(self) -> List[Dict]:
        """Get pings where response was detected."""
        if not self.config or "state" not in self.config:
            return []
        return [
            ping for ping in self.config["state"]["pings"].values()
            if ping.get("response_detected") and ping.get("linear_issue_id")
        ]

    def is_url_synced(self, url: str) -> bool:
        """Check if a URL has already been synced to Linear."""
        if not self.config or "state" not in self.config:
            return False
        synced_urls = self.config["state"].get("synced_urls", [])
        return url in synced_urls

    def mark_url_synced(self, url: str):
        """Mark a URL as synced to Linear."""
        if self.config is None:
            return

        if "state" not in self.config:
            self.config["state"] = self.DEFAULT_CONFIG["state"].copy()

        if "synced_urls" not in self.config["state"]:
            self.config["state"]["synced_urls"] = []

        if url not in self.config["state"]["synced_urls"]:
            self.config["state"]["synced_urls"].append(url)

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about current state."""
        if not self.config or "state" not in self.config:
            return {
                "total_pings": 0,
                "new_pings": 0,
                "analyzed_pings": 0,
                "synced_pings": 0,
                "responded_pings": 0,
                "total_threads": 0
            }

        pings = self.config["state"]["pings"].values()

        return {
            "total_pings": len(self.config["state"]["pings"]),
            "new_pings": len([p for p in pings if p["status"] == "new"]),
            "analyzed_pings": len([p for p in pings if p["status"] == "analyzed"]),
            "synced_pings": len([p for p in pings if p["status"] == "synced"]),
            "responded_pings": len([p for p in pings if p.get("response_detected")]),
            "total_threads": len(self.config["state"].get("threads", {}))
        }


if __name__ == "__main__":
    # Example usage
    print("Testing ConfigManager...")
    cm = ConfigManager()
    print(f"Config exists: {cm.exists()}")
    print(f"Config valid: {cm.is_valid()}")
    print(f"\nStats: {cm.get_stats()}")

    # Test fetch date logic
    print(f"\nSlack fetch start (first run): {cm.get_fetch_start_date('slack')}")
