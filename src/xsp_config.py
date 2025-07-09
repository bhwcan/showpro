import json
import os
import platform
from pathlib import Path

class AppConfig:
    """Handles application configuration with cross-platform support."""

    def __init__(self, app_name="showpro", config_filename="config.json"):
        self.app_name = app_name
        self.config_filename = config_filename
        self.config_dir = self.get_config_directory()
        self.config_path = os.path.join(self.config_dir, self.config_filename)

        self.settings = {}
        self.load_config()

    def get_config_directory(self):
        """Returns the correct config directory based on OS."""
        system = platform.system()
        print("System:", system)

        if system == "Windows":
            return os.path.join(os.getenv("APPDATA"), self.app_name)
        elif system == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", self.app_name)
        else:  # Linux & other Unix-based systems
            return os.path.join(os.path.expanduser("~"), ".config", self.app_name)

    def load_config(self):
        """Loads settings from the config file, creating defaults if necessary."""
        os.makedirs(self.config_dir, exist_ok=True)  # Ensure the directory exists

        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as file:
                self.settings = json.load(file)
                print(self.settings)
        else:
            self.settings = self.default_settings(self.app_name)
            self.save_config()

    def save_config(self):
        """Saves the current settings to the configuration file."""
        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(self.settings, file, indent=4)

    @staticmethod
    def default_settings(app_name):
        """Returns default settings."""
        newpath = os.path.join(Path.home(), "Documents", app_name)
        print(newpath)
        return {
            "tablet": False,
            "textsize": 20,
            "rootpath": newpath,
            "chordcolor": 2,
            "songtitles": True,
            "instrument": "ukulele"
       }

    def get(self, key, default=None):
        """Gets a configuration value."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Sets a configuration value and saves it."""
        self.settings[key] = value
        self.save_config()


# Example Usage
if __name__ == "__main__":
    config = AppConfig("showpro")  # Replace "YourApp" with your application name
    print(f"Config file path: {config.config_path}")
    print("Font Size:", config.get("textsize"))
    print("Root Path:", config.get("rootpath"))
    config.set("textsize", 16)  # Modify and save
