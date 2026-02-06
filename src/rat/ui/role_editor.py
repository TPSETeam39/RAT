from dataclasses import dataclass
from typing import Callable, Optional, TypeAlias, override

import wx
import wx.dataview

from rat.io import Role as IoRole
from rat.io import RoleGender


ROOT = wx.dataview.DataViewItem(0)


# Imports for Role Editor
Role: TypeAlias = IoRole


# Data model for the Role Editor
class RoleEditorDataViewModel(wx.dataview.DataViewModel):
    """
    List model for roles shown in the Role Editor.
    """
    COL_ID = 0
    COL_NAME = 1
    COL_GENDER = 2

    def __init__(self, warn: Optional[Callable[[str], None]] = None):
        super().__init__()

        self.roles: dict[int, Role] = {}
        self.next_id = 0

        self.gender_label_by_value: dict[RoleGender, str] = {
            RoleGender.FEMALE: "Female",
            RoleGender.MALE: "Male",
            RoleGender.NON_BINARY: "Non-Binary",
            RoleGender.NEUTRAL: "Neutral",
        }
        self.gender_value_by_label: dict[str, RoleGender] = {
            "Female": RoleGender.FEMALE,
            "Male": RoleGender.MALE,
            "Non-Binary": RoleGender.NON_BINARY,
            "Neutral": RoleGender.NEUTRAL,
        }

        self.warn = warn or (lambda _msg: None)

        self._names_present: set[str] = set()
        self._name_by_id: dict[int, str] = {}

    def _normalize_name(self, name: str) -> str:
        """
        Normalize a role name for duplicate checking.
        """
        return name.casefold()

    # DataViewModel implementation (list model)
    @override
    def IsContainer(self, item: wx.dataview.DataViewItem) -> bool:
        """
        Only ROOT is a container.
        """
        return not item.IsOk()

    @override
    def GetParent(self, item: wx.dataview.DataViewItem) -> wx.dataview.DataViewItem:
        """
        All items have ROOT as parent.
        """
        return ROOT

    @override
    def GetChildren(
        self, item: wx.dataview.DataViewItem, children: list[wx.dataview.DataViewItem]
    ) -> int:
        """
        Return all role items as children of ROOT.
        """
        if not item.IsOk():
            for rid in self.roles.keys():
                children.append(self.role_id_to_dv_item(rid))
            return len(self.roles)
        return 0

    @override
    def GetValue(self, item: wx.dataview.DataViewItem, col: int):
        """
        Return the cell value for the given item and column.
        """
        rid = self.dv_item_to_role_id(item)
        role = self.roles[rid]

        match col:
            case self.COL_ID:
                return str(role.id)
            case self.COL_NAME:
                return role.name
            case self.COL_GENDER:
                return self.gender_label_by_value.get(role.gender, str(role.gender))
            case _:
                raise Exception("invalid column")

    @override
    def SetValue(self, variant, item: wx.dataview.DataViewItem, col: int) -> bool:
        """
        Validate and apply an edit. Returns True if accepted.
        """
        rid = self.dv_item_to_role_id(item)
        role = self.roles[rid]

        match col:
            case self.COL_ID:
                raise Exception("id cannot be set")

            case self.COL_NAME:
                new_name = (str(variant) if variant is not None else "").strip()
                if not new_name:
                    self.warn("Role name cannot be empty.")
                    return False

                new_norm = self._normalize_name(new_name)
                current_norm = self._normalize_name(self._name_by_id.get(rid, ""))
                if new_norm != current_norm and new_norm in self._names_present:
                    self.warn(
                        f"Warning: The name '{new_name}' is already used. Please choose a different name."
                    )
                    return False

                if rid in self._name_by_id:
                    self._names_present.discard(current_norm)

                self._name_by_id[rid] = new_name
                self._names_present.add(new_norm)

                self.roles[rid] = Role(id=role.id, name=new_name, gender=role.gender)
                return True

            case self.COL_GENDER:
                label = str(variant)
                if label not in self.gender_value_by_label:
                    self.warn(f"Unknown gender value: {label}")
                    return False

                new_gender = self.gender_value_by_label[label]
                self.roles[rid] = Role(id=role.id, name=role.name, gender=new_gender)
                return True

            case _:
                raise Exception("invalid column")

    # Check for duplicate names
    def _make_unique_default_name(self, base: str = "Role") -> str:
        """
        Return base or 'base N' not used yet.
        """
        if self._normalize_name(base) not in self._names_present:
            return base
        i = 2
        while self._normalize_name(f"{base} {i}") in self._names_present:
            i += 1
        return f"{base} {i}"

    def role_id_to_dv_item(self, rid: int) -> wx.dataview.DataViewItem:
        """
        Encode role id into a DataViewItem (rid + 1; 0 reserved for ROOT).
        """
        return wx.dataview.DataViewItem(rid + 1)

    def role_to_dv_item(self, role: Role) -> wx.dataview.DataViewItem:
        """
        Shortcut: role -> DataViewItem.
        """
        return self.role_id_to_dv_item(role.id)

    def dv_item_to_role_id(self, item: wx.dataview.DataViewItem) -> int:
        """
        Decode DataViewItem back to role id.
        """
        if not item.IsOk():
            raise Exception("invalid item")
        return int(item.ID) - 1

    def get_gender_choices(self) -> list[str]:
        """
        Labels for the gender dropdown.
        """
        return list(self.gender_value_by_label.keys())

    # Add/remove roles
    def add_role(self, role: Role) -> int:
        """
        Insert a role, fixing empty/duplicate names, and notify the view.
        """
        rid = role.id
        if rid in self.roles:
            raise Exception(f"role with id {rid} already exists")

        if rid >= self.next_id:
            self.next_id = rid + 1

        name = (role.name or "").strip()
        if not name or self._normalize_name(name) in self._names_present:
            name = self._make_unique_default_name("Role")

        role = Role(id=rid, name=name, gender=role.gender)
        self.roles[rid] = role

        norm = self._normalize_name(role.name)
        self._name_by_id[rid] = role.name
        self._names_present.add(norm)

        self.ItemAdded(ROOT, self.role_to_dv_item(role))
        return rid

    def remove_role_by_id(self, rid: int) -> None:
        """
        Remove a role and notify the view.
        """
        if rid not in self.roles:
            raise Exception(f"role with id {rid} not found")

        del self.roles[rid]

        old = self._name_by_id.pop(rid, None)
        if old is not None:
            self._names_present.discard(self._normalize_name(old))

        self.ItemDeleted(ROOT, self.role_id_to_dv_item(rid))


# UI Panel for Role Editor
class RoleEditorPanel(wx.Panel):
    """
    Panel showing roles in a DataViewCtrl with Add/Delete + context menu.
    """
    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        self.model = RoleEditorDataViewModel(warn=self._warn)
        self.dv = wx.dataview.DataViewCtrl(
            self, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_MULTIPLE
        )
        self.dv.AssociateModel(self.model)
        self.append_columns()

        self.init_layout()
        self.bind_event_handlers()

    def _warn(self, message: str) -> None:
        """
        Show validation warnings from the model.
        """
        wx.MessageBox(message, "Role Editor", wx.OK | wx.ICON_WARNING, parent=self)

    def init_layout(self) -> None:
        """
        Create layout: table + buttons.
        """
        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        top_sizer.Add(self.dv, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        button_add = wx.Button(self, id=wx.ID_ADD, label="Add")
        button_sizer.Add(button_add, 0, wx.RIGHT, 5)

        button_delete = wx.Button(self, id=wx.ID_DELETE, label="Delete")
        button_sizer.Add(button_delete, 0)

        top_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizerAndFit(top_sizer)

    def bind_event_handlers(self) -> None:
        """
        Bind DataView + button + context menu events.
        """
        self.Bind(
            wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED,
            self.on_dataview_item_activated,
            self.dv,
        )
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_context_menu, self.dv)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu, self.dv)
        self.Bind(wx.EVT_BUTTON, self.on_button)

    def append_columns(self) -> None:
        """
        Add ID, Name, Gender columns.
        """
        self.dv.AppendTextColumn("ID", RoleEditorDataViewModel.COL_ID)
        self.dv.AppendColumn(self.make_text_column("Name", RoleEditorDataViewModel.COL_NAME))
        self.dv.AppendColumn(
            self.make_choice_column(
                "Gender",
                self.model.get_gender_choices(),
                RoleEditorDataViewModel.COL_GENDER,
            )
        )

    @staticmethod
    def make_text_column(title: str, model_column: int) -> wx.dataview.DataViewColumn:
        """
        Editable text column.
        """
        return wx.dataview.DataViewColumn(
            title,
            wx.dataview.DataViewTextRenderer(mode=wx.dataview.DATAVIEW_CELL_EDITABLE),
            model_column,
            width=180,
            flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )

    @staticmethod
    def make_choice_column(
        title: str, choices: list[str], model_column: int
    ) -> wx.dataview.DataViewColumn:
        """
        Dropdown column.
        """
        return wx.dataview.DataViewColumn(
            title,
            wx.dataview.DataViewChoiceRenderer(choices),
            model_column,
            width=140,
            flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )

    def add_role(self, role: Role) -> int:
        """
        Add a role via the model.
        """
        return self.model.add_role(role)

    def remove_selection(self) -> None:
        """
        Delete all selected roles.
        """
        ids = [self.model.dv_item_to_role_id(item) for item in self.dv.Selections]
        for rid in ids:
            self.model.remove_role_by_id(rid)

    def on_dataview_item_activated(self, event: wx.dataview.DataViewEvent) -> None:
        """
        Double-click: edit the activated cell.
        """
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            self.dv.EditItem(item, column)

    def on_button(self, event: wx.Event) -> None:
        """
        Handle Add/Delete buttons.
        """
        match event.Id:
            case wx.ID_ADD:
                rid = self.add_role(Role(id=self.model.next_id, name="Role", gender=RoleGender.NEUTRAL))
                self.dv.EditItem(
                    self.model.role_id_to_dv_item(rid),
                    self.dv.GetColumn(RoleEditorDataViewModel.COL_NAME),
                )
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid button")

    def on_menu(self, event: wx.MenuEvent) -> None:
        """
        Handle context menu commands.
        """
        match event.Id:
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid menu item")

    def on_context_menu(self, event: wx.dataview.DataViewEvent) -> None:
        """
        Show context menu on right-click.
        """
        menu = wx.Menu()
        menu.Append(wx.ID_DELETE, "&Delete")
        menu.Bind(wx.EVT_MENU, self.on_menu)
        self.PopupMenu(menu, event.GetPosition())
