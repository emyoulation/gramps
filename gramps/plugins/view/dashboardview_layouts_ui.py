# gramps/plugins/view/dashboardview_layouts_ui.py
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Dashboard Layout Profiles Management UI System
#
# Copyright (C) 2026  Gramps Project Contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Generated-by: OpenAI GPT-4, API, March 2026
# Co-authored-by: <Your Name>

"""
Dashboard Layout UI Components.

Provides GTK widgets for layout switching, management dialogs,
and configuration tab.
"""

import logging
from typing import Callable, Optional

from gi.repository import Gio, Gtk

from gramps.gen.const import GRAMPS_LOCALE as glocale

LOG = logging.getLogger(__name__)
_ = glocale.translation.gettext


class LayoutSwitchMenu(Gtk.MenuToolButton):
    """Toolbar menu for switching between dashboard layouts."""

    def __init__(
        self,
        layout_manager,
        on_layout_selected: Callable[[str], None],
        on_add_layout: Callable[[], None],
        on_delete_layout: Callable[[], None],
        on_rename_layout: Callable[[], None],
        on_reset_layout: Callable[[], None],
    ) -> None:
        """
        Initialize the layout switch menu.

        Args:
            layout_manager: DashboardLayoutManager instance
            on_layout_selected: callback(layout_name) for layout selection
            on_add_layout: callback() for add operation
            on_delete_layout: callback() for delete operation
            on_rename_layout: callback() for rename operation
            on_reset_layout: callback() for reset operation
        """
        super().__init__()
        self.layout_manager = layout_manager
        self.on_layout_selected = on_layout_selected
        self.on_add_layout = on_add_layout
        self.on_delete_layout = on_delete_layout
        self.on_rename_layout = on_rename_layout
        self.on_reset_layout = on_reset_layout

        self.set_label(_("Layouts"))
        self.set_tooltip_text(_("Switch or manage dashboard layouts"))

        self._build_menu()
        self.connect("clicked", self._on_default_clicked)

    def _build_menu(self) -> None:
        """Build the dropdown menu with layout options."""
        menu = Gio.Menu.new()

        # Layouts section
        layouts_section = Gio.Menu.new()
        active = self.layout_manager.get_active_layout()

        for layout_name in self.layout_manager.list_layouts():
            is_active = layout_name == active
            action_name = f"layout_{layout_name}"
            label = f"{'✓ ' if is_active else '  '}{layout_name}"
            item = Gio.MenuItem.new(label, f"win.{action_name}")
            layouts_section.append_item(item)

        menu.append_section(None, layouts_section)

        # Management section
        mgmt_section = Gio.Menu.new()
        mgmt_section.append(_("Add Layout…"), "win.layout_add")
        mgmt_section.append(_("Rename Layout…"), "win.layout_rename")
        mgmt_section.append(_("Delete Layout"), "win.layout_delete")
        mgmt_section.append(_("Reset to Defaults"), "win.layout_reset")
        menu.append_section(None, mgmt_section)

        self.set_menu_model(menu)

    def _on_default_clicked(self, widget) -> None:
        """Handler when main button clicked (not menu item)."""
        # Refresh menu to show current active layout
        self.refresh_menu()

    def refresh_menu(self) -> None:
        """Rebuild menu after layout list changes."""
        self._build_menu()


class AddLayoutDialog(Gtk.Dialog):
    """Dialog for adding a new dashboard layout."""

    def __init__(self, parent_window, layout_manager) -> None:
        """
        Initialize add layout dialog.

        Args:
            parent_window: Parent GTK window
            layout_manager: DashboardLayoutManager instance
        """
        super().__init__(
            transient_for=parent_window, destroy_with_parent=True
        )
        self.layout_manager = layout_manager
        self.set_title(_("Add New Layout"))
        self.set_modal(True)
        self.set_default_size(400, 150)

        # Add standard buttons
        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )

        # Build content
        vbox = self.get_content_area()
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_spacing(12)

        # Name entry
        hbox_name = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label_name = Gtk.Label(label=_("Layout Name:"))
        label_name.set_halign(Gtk.Align.START)
        label_name.set_size_request(100, -1)
        self.entry_name = Gtk.Entry()
        hbox_name.pack_start(label_name, False, False, 0)
        hbox_name.pack_start(self.entry_name, True, True, 0)
        vbox.pack_start(hbox_name, False, False, 0)

        # Copy from selection
        hbox_copy = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label_copy = Gtk.Label(label=_("Copy From:"))
        label_copy.set_halign(Gtk.Align.START)
        label_copy.set_size_request(100, -1)
        self.combo_copy = Gtk.ComboBoxText()
        self.combo_copy.append_text(_("Default/Blank"))
        for layout in self.layout_manager.list_layouts():
            self.combo_copy.append_text(layout)
        self.combo_copy.set_active(0)
        hbox_copy.pack_start(label_copy, False, False, 0)
        hbox_copy.pack_start(self.combo_copy, True, True, 0)
        vbox.pack_start(hbox_copy, False, False, 0)

        vbox.show_all()

    def get_name(self) -> str:
        """Return the entered layout name."""
        return self.entry_name.get_text().strip()

    def get_copy_from(self) -> Optional[str]:
        """Return the selected layout to copy from, or None for default."""
        idx = self.combo_copy.get_active()
        if idx <= 0:
            return None
        return self.combo_copy.get_active_text()


class RenameLayoutDialog(Gtk.Dialog):
    """Dialog for renaming a dashboard layout."""

    def __init__(
        self, parent_window, layout_manager, current_name: str
    ) -> None:
        """
        Initialize rename layout dialog.

        Args:
            parent_window: Parent GTK window
            layout_manager: DashboardLayoutManager instance
            current_name: Current layout name
        """
        super().__init__(
            transient_for=parent_window, destroy_with_parent=True
        )
        self.layout_manager = layout_manager
        self.current_name = current_name
        self.set_title(_("Rename Layout"))
        self.set_modal(True)
        self.set_default_size(400, 100)

        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK,
            Gtk.ResponseType.OK,
        )

        vbox = self.get_content_area()
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_spacing(12)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=_("New Name:"))
        label.set_halign(Gtk.Align.START)
        label.set_size_request(100, -1)
        self.entry = Gtk.Entry()
        self.entry.set_text(current_name)
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(self.entry, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)

        vbox.show_all()

    def get_new_name(self) -> str:
        """Return the new layout name."""
        return self.entry.get_text().strip()


class DeleteLayoutDialog(Gtk.Dialog):
    """Dialog for selecting and deleting a layout."""

    def __init__(self, parent_window, layout_manager) -> None:
        """
        Initialize delete layout dialog.

        Args:
            parent_window: Parent GTK window
            layout_manager: DashboardLayoutManager instance
        """
        super().__init__(
            transient_for=parent_window, destroy_with_parent=True
        )
        self.layout_manager = layout_manager
        self.set_title(_("Delete Layout"))
        self.set_modal(True)
        self.set_default_size(300, 150)

        self.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            _("Delete"),
            Gtk.ResponseType.OK,
        )

        # Make delete button red/destructive
        delete_btn = self.get_widget_for_response(Gtk.ResponseType.OK)
        if delete_btn:
            delete_btn.get_style_context().add_class("destructive-action")

        vbox = self.get_content_area()
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_spacing(12)

        label = Gtk.Label(label=_("Select layout to delete:"))
        label.set_halign(Gtk.Align.START)
        vbox.pack_start(label, False, False, 0)

        self.combo = Gtk.ComboBoxText()
        for layout in self.layout_manager.list_layouts():
            self.combo.append_text(layout)
        if self.combo.get_model().iter_n_children(None) > 0:
            self.combo.set_active(0)
        vbox.pack_start(self.combo, False, False, 0)

        vbox.show_all()

    def get_selected_layout(self) -> Optional[str]:
        """Return the selected layout name."""
        text = self.combo.get_active_text()
        return text if text else None


class LayoutManagementTab:
    """Configuration tab widget for managing dashboard layouts."""

    def __init__(self, layout_manager, dashview) -> None:
        """
        Initialize the layout management tab.

        Args:
            layout_manager: DashboardLayoutManager instance
            dashview: Parent DashboardView instance (for callbacks)
        """
        self.layout_manager = layout_manager
        self.dashview = dashview
        self.layout_list = None

    def create_widget(self) -> tuple:
        """
        Create and return (tab_title, widget) for View Configure dialog.

        Returns:
            Tuple of (title_string, Gtk.Widget)
        """
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        # Title
        title = Gtk.Label()
        title.set_markup(
            f"<b>{_('Dashboard Layout Profiles')}</b>"
        )
        title.set_halign(Gtk.Align.START)
        vbox.pack_start(title, False, False, 0)

        # Description
        desc = Gtk.Label(
            label=_(
                "Manage your dashboard layout profiles. "
                "Each profile stores your gramplet arrangement "
                "and column configuration."
            )
        )
        desc.set_line_wrap(True)
        desc.set_halign(Gtk.Align.START)
        vbox.pack_start(desc, False, False, 0)

        # Separator
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep1, False, False, 0)

        # Layouts list
        hbox_list = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # ListBox for layouts
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        scrolled.set_min_content_height(150)

        self.layout_list = Gtk.ListBox()
        self.layout_list.connect("row-selected", self._on_layout_selected)
        scrolled.add(self.layout_list)

        hbox_list.pack_start(scrolled, True, True, 0)

        # Buttons column
        vbox_buttons = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        btn_add = Gtk.Button(label=_("Add"))
        btn_add.connect("clicked", self._on_add_clicked)
        vbox_buttons.pack_start(btn_add, False, False, 0)

        btn_rename = Gtk.Button(label=_("Rename"))
        btn_rename.connect("clicked", self._on_rename_clicked)
        vbox_buttons.pack_start(btn_rename, False, False, 0)

        btn_delete = Gtk.Button(label=_("Delete"))
        btn_delete.connect("clicked", self._on_delete_clicked)
        vbox_buttons.pack_start(btn_delete, False, False, 0)

        vbox_buttons.pack_start(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL),
            False,
            False,
            0,
        )

        btn_reset = Gtk.Button(label=_("Reset to Default"))
        btn_reset.connect("clicked", self._on_reset_clicked)
        vbox_buttons.pack_start(btn_reset, False, False, 0)

        hbox_list.pack_start(vbox_buttons, False, False, 0)

        vbox.pack_start(hbox_list, True, True, 0)

        # Separator
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(sep2, False, False, 0)

        # Active layout indicator
        hbox_active = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_active = Gtk.Label(label=_("Active Layout:"))
        self.lbl_active_val = Gtk.Label()
        self.lbl_active_val.set_halign(Gtk.Align.START)
        hbox_active.pack_start(lbl_active, False, False, 0)
        hbox_active.pack_start(self.lbl_active_val, True, True, 0)
        vbox.pack_start(hbox_active, False, False, 0)

        vbox.show_all()
        self._refresh_list()

        return (_("Gramplet Layout"), vbox)

    def _refresh_list(self) -> None:
        """Refresh the layout list display."""
        if self.layout_list is None:
            return

        # Clear existing
        for row in self.layout_list.get_children():
            self.layout_list.remove(row)

        active = self.layout_manager.get_active_layout()

        # Add layout rows
        for layout_name in sorted(self.layout_manager.list_layouts()):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            hbox.set_margin_start(6)
            hbox.set_margin_end(6)
            hbox.set_margin_top(3)
            hbox.set_margin_bottom(3)

            if layout_name == active:
                lbl = Gtk.Label(xalign=0)
                lbl.set_markup(f"<b>✓ {layout_name}</b>")
            else:
                lbl = Gtk.Label(label=f"  {layout_name}", xalign=0)

            hbox.pack_start(lbl, True, True, 0)
            row.add(hbox)
            row.layout_name = layout_name
            self.layout_list.add(row)

        self.layout_list.show_all()

        # Update active label
        self.lbl_active_val.set_text(active)

    def _on_layout_selected(self, widget, row) -> None:
        """Handle layout selection in list."""
        # Selection tracking for other operations

    def _on_add_clicked(self, widget) -> None:
        """Handle add layout button."""
        parent_window = self.dashview.uistate.window
        dialog = AddLayoutDialog(parent_window, self.layout_manager)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.get_name()
            copy_from = dialog.get_copy_from()

            if not name:
                self._show_error(
                    parent_window, _("Layout name cannot be empty.")
                )
            elif not self.layout_manager.create_layout(name, copy_from):
                self._show_error(
                    parent_window,
                    _("Layout '{0}' already exists.").format(name),
                )
            else:
                self._refresh_list()
                if self.dashview and hasattr(
                    self.dashview, "layout_menu"
                ):
                    self.dashview.layout_menu.refresh_menu()

        dialog.destroy()

    def _on_rename_clicked(self, widget) -> None:
        """Handle rename layout button."""
        row = self.layout_list.get_selected_row()
        if not row:
            self._show_error(
                self.dashview.uistate.window,
                _("Select a layout to rename."),
            )
            return

        old_name = row.layout_name
        parent_window = self.dashview.uistate.window
        dialog = RenameLayoutDialog(
            parent_window, self.layout_manager, old_name
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            new_name = dialog.get_new_name()

            if not new_name:
                self._show_error(
                    parent_window, _("Layout name cannot be empty.")
                )
            elif not self.layout_manager.rename_layout(old_name, new_name):
                self._show_error(
                    parent_window,
                    _("Could not rename layout. Name may already exist."),
                )
            else:
                self._refresh_list()
                if self.dashview and hasattr(
                    self.dashview, "layout_menu"
                ):
                    self.dashview.layout_menu.refresh_menu()

        dialog.destroy()

    def _on_delete_clicked(self, widget) -> None:
        """Handle delete layout button."""
        row = self.layout_list.get_selected_row()
        if not row:
            self._show_error(
                self.dashview.uistate.window,
                _("Select a layout to delete."),
            )
            return

        name = row.layout_name
        parent_window = self.dashview.uistate.window

        # Confirmation
        if not self._confirm_delete(parent_window, name):
            return

        if not self.layout_manager.delete_layout(name):
            self._show_error(
                parent_window,
                _(
                    "Could not delete layout. "
                    "(Must keep at least one layout.)"
                ),
            )
        else:
            self._refresh_list()
            if self.dashview and hasattr(
                self.dashview, "layout_menu"
            ):
                self.dashview.layout_menu.refresh_menu()
            # If we deleted the active layout, switch layout
            if self.dashview and hasattr(self.dashview, "switch_layout"):
                active = self.layout_manager.get_active_layout()
                self.dashview.switch_layout(active)

    def _on_reset_clicked(self, widget) -> None:
        """Handle reset to default button."""
        parent_window = self.dashview.uistate.window

        if not self._confirm_reset(parent_window):
            return

        self.layout_manager.reset_all()
        self._refresh_list()
        if self.dashview and hasattr(
            self.dashview, "layout_menu"
        ):
            self.dashview.layout_menu.refresh_menu()
        if self.dashview and hasattr(self.dashview, "switch_layout"):
            self.dashview.switch_layout("Default")

    def _show_error(self, parent_window, message: str) -> None:
        """Show error dialog."""
        dlg = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            type_=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            message_format=_("Error"),
        )
        dlg.format_secondary_text(message)
        dlg.run()
        dlg.destroy()

    def _confirm_delete(self, parent_window, name: str) -> bool:
        """Show confirmation dialog for delete."""
        dlg = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            type_=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=_("Delete Layout?"),
        )
        dlg.format_secondary_text(
            _("Are you sure you want to delete layout '{0}'?").format(name)
        )
        response = dlg.run()
        dlg.destroy()
        return response == Gtk.ResponseType.YES

    def _confirm_reset(self, parent_window) -> bool:
        """Show confirmation dialog for reset."""
        dlg = Gtk.MessageDialog(
            transient_for=parent_window,
            flags=0,
            type_=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=_("Reset All Layouts?"),
        )
        dlg.format_secondary_text(
            _(
                "This will delete all custom layouts and restore "
                "the default layout. Continue?"
            )
        )
        response = dlg.run()
        dlg.destroy()
        return response == Gtk.ResponseType.YES
