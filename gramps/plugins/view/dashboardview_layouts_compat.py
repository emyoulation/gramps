# gramps/plugins/view/dashboardview_layouts.py
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Dashboard Layout Profiles Management System
#
# Copyright (C) 2026  Gramps Project Contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Generated-by: OpenAI GPT-4, API, March 2026
# Co-authored-by: Brian McCullough emyoulation@yahoo.com

"""
DashboardLayoutManager for Gramps Dashboard View Profile System.

Provides management and validation for multiple Dashboard layouts with
minimal metadata footprint and cross-platform support.
"""

import logging
import os
import shutil
from configparser import ConfigParser, ParsingError
from typing import List, Optional

from dashboardview_layouts_compat import (
    CompatibilityChecker,
    EnvironmentMetadata,
)

LOG = logging.getLogger(__name__)

# Version control for layout INI files
LAYOUTS_VERSION = "1.0"
LAYOUTS_DIR = os.path.expanduser("~/.gramps/gramplets/dashboard_layouts")
CONFIG_FILE = os.path.join(LAYOUTS_DIR, "dashboard_layouts.conf")
INI_NAME_PREFIX = "dashboard_"
INI_NAME_SUFFIX = ".ini"

# INI file structure constants
SECTION_ENVIRONMENT = "GrampsEnvironment"
SECTION_LAYOUT = "DashboardLayout"
SECTION_GRAMPLET_CONFIG = "GrampletConfiguration"
SECTION_DOCKED = "DockedGramplets"
SECTION_UNDOCKED = "UndockedGramplets"
KEY_VERSION = "version"
KEY_COLUMNS = "columns"
KEY_REQUIRED_GRAMPLETS = "required_gramplet_ids"
KEY_ORDER = "order"

# Default layout template
_DEFAULT_LAYOUT = f"""[{SECTION_ENVIRONMENT}]
gramps_version = 
os_name = 
locale_language = 
locale_encoding = 

[{SECTION_LAYOUT}]
{KEY_VERSION} = {LAYOUTS_VERSION}
{KEY_COLUMNS} = 2

[{SECTION_GRAMPLET_CONFIG}]
{KEY_REQUIRED_GRAMPLETS} = 

[{SECTION_DOCKED}]
{KEY_ORDER} = Welcome,Top Surnames,Calendar

[{SECTION_UNDOCKED}]
{KEY_ORDER} =
"""


class LayoutValidationError(Exception):
    """Exception raised for layout validation failures."""

    pass


class DashboardLayoutManager:
    """
    Manages Dashboard layout profiles for Gramps DashboardView.

    Each profile is a versioned INI file (.ini) stored in the layouts
    directory. Handles validation, CRUD operations, and active profile
    selection. Can be reused by other dashboard-style views (e.g., CardView).

    Attributes:
        config (ConfigParser): Configuration for active layout tracking
    """

    def __init__(self) -> None:
        """Initialize the layout manager with directory setup."""
        os.makedirs(LAYOUTS_DIR, exist_ok=True)
        self.config = ConfigParser()
        self.compat_checker = CompatibilityChecker()
        self._load_config()

    def list_layouts(self) -> List[str]:
        """
        Return list of available layout names.

        Returns:
            List of layout names sorted alphabetically
        """
        try:
            layouts = [
                fname[len(INI_NAME_PREFIX) : -len(INI_NAME_SUFFIX)]
                for fname in os.listdir(LAYOUTS_DIR)
                if fname.startswith(INI_NAME_PREFIX)
                and fname.endswith(INI_NAME_SUFFIX)
            ]
            return sorted(layouts)
        except OSError as err:
            LOG.warning("Error listing layouts: %s", err)
            return []

    def ini_path(self, name: str) -> str:
        """
        Get the absolute path to a layout INI file by name.

        Args:
            name: Layout name (without prefix/suffix)

        Returns:
            Absolute path to the INI file
        """
        return os.path.join(
            LAYOUTS_DIR, f"{INI_NAME_PREFIX}{name}{INI_NAME_SUFFIX}"
        )

    def validate_ini(self, filepath: str) -> bool:
        """
        Validate INI file for correct version and structure.

        Args:
            filepath: Path to INI file to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                return False

            cp = ConfigParser()
            cp.read(filepath)

            # Check for required sections
            if SECTION_LAYOUT not in cp:
                LOG.warning("Missing %s section in %s", SECTION_LAYOUT, filepath)
                return False

            # Check version match
            version = cp.get(SECTION_LAYOUT, KEY_VERSION, fallback=None)
            if version != LAYOUTS_VERSION:
                LOG.warning(
                    "Version mismatch in %s: expected %s, got %s",
                    filepath,
                    LAYOUTS_VERSION,
                    version,
                )
                return False

            return True

        except ParsingError as err:
            LOG.warning("Error parsing %s: %s", filepath, err)
            return False

    def create_layout(
        self, name: str, from_name: Optional[str] = None
    ) -> bool:
        """
        Add a new layout by copying from another or using default.

        Args:
            name: Name for the new layout
            from_name: Optional name of layout to copy from

        Returns:
            True if created successfully, False if name exists or error
        """
        path = self.ini_path(name)

        # Check if name already exists
        if os.path.exists(path):
            LOG.warning("Layout %s already exists", name)
            return False

        try:
            if from_name and from_name in self.list_layouts():
                # Copy from existing layout
                src_path = self.ini_path(from_name)
                if not self.validate_ini(src_path):
                    LOG.warning("Source layout %s is invalid", from_name)
                    return False
                shutil.copyfile(src_path, path)
                # Update environment metadata
                cp = ConfigParser()
                cp.read(path)
                self._update_environment_metadata(cp)
                self.save_ini(name, cp)
            else:
                # Create from default template with current environment
                cp = ConfigParser()
                cp.read_string(_DEFAULT_LAYOUT)
                self._update_environment_metadata(cp)
                self.save_ini(name, cp)

            LOG.info("Created layout: %s", name)
            return True

        except OSError as err:
            LOG.error("Error creating layout %s: %s", name, err)
            return False

    def delete_layout(self, name: str) -> bool:
        """
        Remove a layout (cannot remove if it's the only one).

        Args:
            name: Name of layout to delete

        Returns:
            True if deleted successfully, False otherwise

        Note:
            If deleted layout is active, switches to another available layout
        """
        layouts = self.list_layouts()

        # Prevent deletion of last layout
        if name not in layouts or len(layouts) < 2:
            LOG.warning("Cannot delete layout %s (last or non-existent)", name)
            return False

        try:
            path = self.ini_path(name)
            os.remove(path)

            # Switch to another layout if deleted is active
            active = self.get_active_layout()
            if active == name:
                others = [n for n in layouts if n != name]
                if others:
                    self.set_active_layout(others[0])
                    LOG.info("Switched to layout %s after deletion", others[0])

            LOG.info("Deleted layout: %s", name)
            return True

        except OSError as err:
            LOG.error("Error deleting layout %s: %s", name, err)
            return False

    def rename_layout(self, old: str, new: str) -> bool:
        """
        Rename a layout from old to new.

        Args:
            old: Current layout name
            new: New layout name

        Returns:
            True if renamed successfully, False if new name exists or error
        """
        if old == new:
            LOG.warning("Cannot rename layout to same name")
            return False

        if new in self.list_layouts():
            LOG.warning("Layout %s already exists", new)
            return False

        try:
            old_path = self.ini_path(old)
            new_path = self.ini_path(new)

            os.rename(old_path, new_path)

            # Update active layout tracking if necessary
            if self.get_active_layout() == old:
                self.set_active_layout(new)

            LOG.info("Renamed layout from %s to %s", old, new)
            return True

        except OSError as err:
            LOG.error("Error renaming layout %s to %s: %s", old, new, err)
            return False

    def reset_layout(self, name: str) -> bool:
        """
        Restore a layout to the default template.

        Args:
            name: Name of layout to reset

        Returns:
            True if reset successfully, False otherwise
        """
        path = self.ini_path(name)

        try:
            cp = ConfigParser()
            cp.read_string(_DEFAULT_LAYOUT)
            self._update_environment_metadata(cp)
            self.save_ini(name, cp)

            LOG.info("Reset layout to default: %s", name)
            return True

        except OSError as err:
            LOG.error("Error resetting layout %s: %s", name, err)
            return False

    def reset_all(self) -> None:
        """
        Remove all user layouts and restore the shipped default.

        This is a destructive operation and should be confirmed by user.
        """
        try:
            # Remove all existing layouts
            for name in self.list_layouts():
                try:
                    os.remove(self.ini_path(name))
                except OSError as err:
                    LOG.warning("Error removing layout %s: %s", name, err)

            # Ensure at least one default layout exists
            self.create_layout("Default")
            self.set_active_layout("Default")

            LOG.info("Reset all layouts to defaults")

        except Exception as err:
            LOG.error("Error during reset_all: %s", err)

    def get_active_layout(self) -> str:
        """
        Get the currently selected layout name.

        Returns:
            Active layout name, with fallback to first available or "Default"
        """
        if (
            "dashboard" in self.config
            and "active_layout" in self.config["dashboard"]
        ):
            value = self.config["dashboard"]["active_layout"]
            if value in self.list_layouts():
                return value

        # Fallback logic
        layouts = self.list_layouts()
        if layouts:
            return layouts[0]

        return "Default"

    def set_active_layout(self, name: str) -> None:
        """
        Set the currently selected layout name.

        Args:
            name: Name of layout to make active
        """
        if "dashboard" not in self.config:
            self.config["dashboard"] = {}

        self.config["dashboard"]["active_layout"] = name
        self._save_config()
        LOG.debug("Set active layout to: %s", name)

    def load_ini(self, name: str) -> Optional[ConfigParser]:
        """
        Load a layout INI file as ConfigParser.

        Args:
            name: Layout name to load

        Returns:
            ConfigParser object if valid, None if parse error or invalid version
        """
        path = self.ini_path(name)

        try:
            if not self.validate_ini(path):
                return None

            cp = ConfigParser()
            cp.read(path)
            return cp

        except ParsingError as err:
            LOG.error("Error parsing layout %s: %s", name, err)
            return None

    def save_ini(self, name: str, cp: ConfigParser) -> bool:
        """
        Save a ConfigParser object to a layout INI file.

        Ensures version header and environment metadata are set correctly.

        Args:
            name: Layout name to save
            cp: ConfigParser object to write

        Returns:
            True if saved successfully, False otherwise
        """
        path = self.ini_path(name)

        try:
            # Ensure version header is correct
            if SECTION_LAYOUT not in cp:
                cp[SECTION_LAYOUT] = {}

            cp[SECTION_LAYOUT][KEY_VERSION] = LAYOUTS_VERSION

            # Update environment metadata
            self._update_environment_metadata(cp)

            with open(path, "w", encoding="utf-8") as f:
                cp.write(f)

            LOG.info("Saved layout: %s", name)
            return True

        except OSError as err:
            LOG.error("Error saving layout %s: %s", name, err)
            return False

    def check_compatibility(
        self, name: str
    ) -> tuple:
        """
        Check layout compatibility with current environment.

        Args:
            name: Layout name to check

        Returns:
            Tuple of (is_compatible, issues_list)
        """
        cp = self.load_ini(name)
        if cp is None:
            return (False, [])

        return self.compat_checker.check_compatibility(cp)

    def _update_environment_metadata(self, cp: ConfigParser) -> None:
        """Update environment metadata in ConfigParser."""
        metadata = EnvironmentMetadata()

        if SECTION_ENVIRONMENT not in cp:
            cp[SECTION_ENVIRONMENT] = {}

        for key, value in metadata.to_dict().items():
            cp[SECTION_ENVIRONMENT][key] = value

    def _load_config(self) -> None:
        """Load main configuration file (active layout tracking)."""
        try:
            if os.path.exists(CONFIG_FILE):
                self.config.read(CONFIG_FILE)
            else:
                self.config["dashboard"] = {}
                self.config["dashboard"]["active_layout"] = "Default"
                self._save_config()

            # Ensure at least one layout exists
            if not self.list_layouts():
                self.create_layout("Default")

        except (OSError, ParsingError) as err:
            LOG.warning("Error loading config: %s", err)
            self.config["dashboard"] = {}
            self.config["dashboard"]["active_layout"] = "Default"

    def _save_config(self) -> None:
        """Save main configuration file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                self.config.write(f)
        except OSError as err:
            LOG.error("Error saving config: %s", err)
