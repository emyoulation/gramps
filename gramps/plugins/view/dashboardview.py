#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
DashboardView interface.
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gui.views.pageview import PageView
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.widgets.grampletpane import GrampletPane
from .dashboardview_layouts import DashboardLayoutManager
from .dashboardview_layouts_ui import (
    LayoutSwitchMenu,
    LayoutManagementTab,
)

_ = glocale.translation.gettext
from gramps.gui.widgets.grampletpane import GrampletPane


class DashboardView(PageView):
    """Dashboard view for Gramps with switchable layout profiles."""

    def __init__(self, pdata, dbstate, uistate):
        """Initialize the Dashboard View."""
        PageView.__init__(self, _("Dashboard"), pdata, dbstate, uistate)
        self.ui_def = []

        # Initialize layout manager
        self.layout_manager = DashboardLayoutManager()
        self.current_layout = self.layout_manager.get_active_layout()
        self.layout_menu = None

        # Build the main widget
        self.widget = self._build_dashboard_widget()

    def _build_dashboard_widget(self):
        """Build the dashboard container with gramplets."""
        # Use standard naming for GrampletPane config
        config_name = "Gramplets_dashboardview_gramplets"
        return GrampletPane(
            config_name, self, self.dbstate, self.uistate
        )

    def build_interface(self):
        """Build the GTK interface."""
        top = self.build_widget()
        top.show_all()
        return top

    def build_widget(self):
        """Builds the container widget for the interface."""
        return self.widget

    def build_tree(self):
        """Rebuilds the current display."""
        pass

    def get_title(self):
        """Used to set the titlebar in the configuration window."""
        return _("Dashboard")

    def get_stock(self):
        """Return image associated with the view."""
        return "gramps-gramplet"

    def get_viewtype_stock(self):
        """Type of view in category."""
        return "gramps-gramplet"

    def define_actions(self):
        """Defines the UIManager actions."""
        pass

    def set_inactive(self):
        """Called when view is set inactive."""
        self.active = False
        self.widget.set_inactive()

    def set_active(self):
        """Called when view is set active."""
        new_title = "%s - %s - Gramps" % (
            self.dbstate.db.get_dbname(),
            self.get_title(),
        )
        self.uistate.window.set_title(new_title)
        self.active = True
        self.widget.set_active()

    def on_delete(self):
        """Called when view is closed."""
        self.widget.on_delete()
        self._config.save()

    def can_configure(self):
        """See :class:`~gui.views.pageview.PageView`."""
        return True

    def _get_configure_page_funcs(self):
        """Return a list of functions that create gtk elements."""
        # Standard gramplet pane config
        standard_funcs = self.widget._get_configure_page_funcs()

        # Add layout management tab
        layout_tab = LayoutManagementTab(self.layout_manager, self)
        layout_funcs = [layout_tab.create_widget]

        return layout_funcs + standard_funcs() if callable(
            standard_funcs
        ) else standard_funcs + layout_funcs

    def navigation_type(self):
        """Return the navigation type."""
        return (None,)

    def switch_layout(self, name: str) -> None:
        """Switch to a different layout profile."""
        if name not in self.layout_manager.list_layouts():
            return

        # Save current layout state
        if hasattr(self.widget, "on_delete"):
            self.widget.on_delete()

        # Load new layout
        self.current_layout = name
        self.layout_manager.set_active_layout(name)

        # Rebuild widget
        old_widget = self.widget
        self.widget = self._build_dashboard_widget()

        # Swap in UI
        parent = old_widget.get_parent()
        if parent:
            parent.remove(old_widget)
            parent.add(self.widget)
            self.widget.show_all()

        # Refresh menu
        if self.layout_menu:
            self.layout_menu.refresh_menu()
