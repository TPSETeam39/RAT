from dataclasses import dataclass
from typing import Any, Callable, Optional

import wx
import wx.dataview

from rat.role_assignment_calculator.genders import Gender


# Contains data classes and UI panel for Role Editor
@dataclass
class Role:
    id: Optional[int]
    name: str
    gender: Any


# Data model for the Role Editor
class RoleEditorDataViewModel(wx.dataview.DataViewModel):
    COL_ID = 0
    COL_NAME = 1
    COL_GENDER = 2

    def __init__(self, warn: Optional[Callable[[str], None]] = None):
        super().__init__()

        self.roles: dict[int, Role] = {}
        self.next_id = 0

        self.gender_label_by_value: dict[Any, str] = {}
        self.gender_value_by_label: dict[str, Any] = {}

        self._register_gender("FEMALE", "Female")
        self._register_gender("MALE", "Male")
        self._register_gender("NON_BINARY", "Non-Binary")

        self.warn = warn or (lambda _msg: None)

    def _register_gender(self, attr: str, label: str) -> None:
        if hasattr(Gender, attr):
            value = getattr(Gender, attr)
            self.gender_label_by_value[value] = label
            self.gender_value_by_label[label] = value

    # DataViewModel implementation (list model)
    def IsContainer(self, item: wx.dataview.DataViewItem) -> bool:
        return not item.IsOk()

    def GetParent(self, item: wx.dataview.DataViewItem) -> wx.dataview.DataViewItem:
        return wx.dataview.DataViewItem(0)

    def GetChildren(self, item: wx.dataview.DataViewItem, children: list[wx.dataview.DataViewItem]) -> int:
        if not item.IsOk():
            for rid in self.roles.keys():
                children.append(self.role_id_to_dv_item(rid))
            return len(self.roles)
        return 0

    def GetValue(self, item: wx.dataview.DataViewItem, col: int) -> Any:
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

    def SetValue(self, variant: Any, item: wx.dataview.DataViewItem, col: int) -> bool:
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

                if self._is_duplicate_name(new_name, exclude_id=rid):
                    self.warn(
                        f"Warning: The name '{new_name}' is already used. Please choose a different name."
                    )
                    return False

                role.name = new_name
                return True

            case self.COL_GENDER:
                label = str(variant)
                if label not in self.gender_value_by_label:
                    self.warn(f"Unknown gender value: {label}")
                    return False
                role.gender = self.gender_value_by_label[label]
                return True

            case _:
                raise Exception("invalid column")

    # Check for duplicate names
    def _is_duplicate_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        needle = name.casefold()
        for rid, role in self.roles.items():
            if exclude_id is not None and rid == exclude_id:
                continue
            if role.name.casefold() == needle:
                return True
        return False

    def role_id_to_dv_item(self, rid: int) -> wx.dataview.DataViewItem:
        return wx.dataview.DataViewItem(rid + 1)

    def role_to_dv_item(self, role: Role) -> wx.dataview.DataViewItem:
        return self.role_id_to_dv_item(role.id)

    def dv_item_to_role_id(self, item: wx.dataview.DataViewItem) -> int:
        if not item.IsOk():
            raise Exception("invalid item")
        return int(item.ID) - 1

    def get_gender_choices(self) -> list[str]:
        return list(self.gender_value_by_label.keys())

    def _make_unique_default_name(self, base: str = "Role") -> str:
        if not self._is_duplicate_name(base):
            return base
        i = 2
        while self._is_duplicate_name(f"{base} {i}"):
            i += 1
        return f"{base} {i}"

    # Add/remove roles
    def add_role(self, role: Role) -> int:
        if role.id is None:
            role.id = self.next_id

        if role.id in self.roles:
            raise Exception(f"role with id {role.id} already exists")

        if role.id >= self.next_id:
            self.next_id = role.id + 1

        role.name = (role.name or "").strip()
        if not role.name or self._is_duplicate_name(role.name):
            role.name = self._make_unique_default_name("Role")

        self.roles[role.id] = role
        self.ItemAdded(wx.dataview.DataViewItem(0), self.role_to_dv_item(role))
        return role.id

    def remove_role_by_id(self, rid: int) -> None:
        if rid not in self.roles:
            raise Exception(f"role with id {rid} not found")
        del self.roles[rid]
        self.ItemDeleted(wx.dataview.DataViewItem(0), self.role_id_to_dv_item(rid))


# UI Panel for Role Editor
class RoleEditorPanel(wx.Panel):
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
        wx.MessageBox(message, "Role Editor", wx.OK | wx.ICON_WARNING, parent=self)

    def init_layout(self) -> None:
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
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dataview_item_activated, self.dv)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_context_menu, self.dv)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu, self.dv)
        self.Bind(wx.EVT_BUTTON, self.on_button)

    def append_columns(self) -> None:
        self.dv.AppendTextColumn("ID", RoleEditorDataViewModel.COL_ID)
        self.dv.AppendColumn(self.make_text_column("Name", RoleEditorDataViewModel.COL_NAME))
        self.dv.AppendColumn(
            self.make_choice_column("Gender", self.model.get_gender_choices(), RoleEditorDataViewModel.COL_GENDER)
        )

    @staticmethod
    def make_text_column(title: str, model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(
            title,
            wx.dataview.DataViewTextRenderer(mode=wx.dataview.DATAVIEW_CELL_EDITABLE),
            model_column,
            width=180,
            flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )

    @staticmethod
    def make_choice_column(title: str, choices: list[str], model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(
            title,
            wx.dataview.DataViewChoiceRenderer(choices),
            model_column,
            width=140,
            flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )

    def add_role(self, role: Role) -> int:
        return self.model.add_role(role)

    def remove_selection(self) -> None:
        ids = [self.model.dv_item_to_role_id(item) for item in self.dv.Selections]
        for rid in ids:
            self.model.remove_role_by_id(rid)

    def on_dataview_item_activated(self, event: wx.dataview.DataViewEvent) -> None:
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            self.dv.EditItem(item, column)

    def on_button(self, event: wx.Event) -> None:
        match event.Id:
            case wx.ID_ADD:
                default_gender = next(iter(self.model.gender_label_by_value))
                rid = self.add_role(Role(None, "Role", default_gender))
                self.dv.EditItem(self.model.role_id_to_dv_item(rid), self.dv.GetColumn(1))
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid button")

    def on_menu(self, event: wx.MenuEvent) -> None:
        match event.Id:
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid menu item")

    def on_context_menu(self, event: wx.dataview.DataViewEvent) -> None:
        menu = wx.Menu()
        menu.Append(wx.ID_DELETE, "&Delete")
        menu.Bind(wx.EVT_MENU, self.on_menu)
        self.PopupMenu(menu, event.GetPosition())
