from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional, override
from itertools import combinations

import wx
import wx.dataview

#meine import
import csv


# eventually move data structures to UI/backend code interface
class Gender(Enum):
    FEMALE = auto()
    MALE = auto()
    NON_BINARY = auto()


@dataclass
class Student:
    id: Optional[int]
    last_name: str
    first_name: str
    gender: Gender
    vetos: set[Gender]


# look at the wxWidgets dataview sample to understand this shit
class StudentInfoDataViewModel(wx.dataview.DataViewModel):
    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_GENDER = 3
    COL_VETOS = 4

    GENDER_MAP = {
        Gender.FEMALE: "Female",
        Gender.MALE: "Male",
        Gender.NON_BINARY: "Non-Binary"
    }

    LIST_SEP = ", "

    def __init__(self):
        super().__init__()

        self.students: dict[int, Student] = {}
        self.next_id = 0

        self.inv_gender_map = {v: k for k, v in self.GENDER_MAP.items()}

    @override
    def IsContainer(self, item: wx.dataview.DataViewItem) -> bool:
        # only the root node is a container because this is a list
        if not item.IsOk(): # root node
            return True

        return False

    @override
    def GetParent(self, item: wx.dataview.DataViewItem) -> wx.dataview.DataViewItem:
        return wx.dataview.DataViewItem(0)

    @override
    def GetChildren(self, item: wx.dataview.DataViewItem, children: list[wx.dataview.DataViewItem]) -> int:
        if not item.IsOk(): # root node
            for id in self.students.keys():
                children.append(self.student_id_to_dv_item(id))
            return len(self.students)

        return 0

    @override
    def GetValue(self, item: wx.dataview.DataViewItem, col: int) -> Any:
        id = self.dv_item_to_student_id(item)
        student: Student = self.students[id]

        match col:
            case self.COL_ID:
                return str(student.id)
            case self.COL_LAST_NAME:
                return student.last_name
            case self.COL_FIRST_NAME:
                return student.first_name
            case self.COL_GENDER:
                return self.GENDER_MAP[student.gender]
            case self.COL_VETOS:
                return self.vetos_to_string(student.vetos)
            case _:
                raise Exception("invalid column")

    @override
    def SetValue(self, variant: Any, item: wx.dataview.DataViewItem, col: int) -> bool:
        id = self.dv_item_to_student_id(item)

        match col:
            case self.COL_ID:
                raise Exception("id cannot be set")
            case self.COL_LAST_NAME:
                self.students[id].last_name = variant
            case self.COL_FIRST_NAME:
                self.students[id].first_name = variant
            case self.COL_GENDER:
                self.students[id].gender = self.inv_gender_map[variant]
            case self.COL_VETOS:
                self.students[id].vetos = self.vetos_from_string(variant)
            case _:
                raise Exception("invalid column")
        
        return True

    def vetos_to_string(self, vetos: set[Gender]) -> str:
        return self.LIST_SEP.join([f"{self.GENDER_MAP[v]}" for v in vetos])

    def vetos_from_string(self, string: str) -> set[Gender]:
        if not string:
            return set()

        vetos = set()
        for veto in string.split(self.LIST_SEP):
            vetos.add(self.inv_gender_map[veto])
        return vetos

    def student_id_to_dv_item(self, id: int) -> wx.dataview.DataViewItem:
        # id is incremented by one because 0 represents an invalid node
        return wx.dataview.DataViewItem(id + 1)

    def student_to_dv_item(self, student: Student) -> wx.dataview.DataViewItem:
        return self.student_id_to_dv_item(student.id)
    
    def dv_item_to_student_id(self, item: wx.dataview.DataViewItem) -> int:
        if not item.IsOk():
            return None

        return int(item.ID) - 1
    
    def get_gender_choices(self) -> list[str]:
        return list(self.GENDER_MAP.values())

    def get_vetos_choices(self) -> list[str]:
        choices = [""]
        choices.extend(self.get_gender_choices())
        for pair in combinations(self.GENDER_MAP, 2):
            choices.append(self.vetos_to_string(pair))
        return choices

    def add_student(self, student: Student) -> int:
        if student.id in self.students:
            raise Exception(f"student with id {student.id} already exists")
        
        if not student.id:
            student.id = self.next_id
        
        if student.id >= self.next_id:
            self.next_id = student.id + 1

        self.students[student.id] = student

        self.ItemAdded(wx.dataview.DataViewItem(0), self.student_to_dv_item(student))
        return student.id
    
    def remove_student_by_id(self, id: int) -> None:
        if id not in self.students:
            raise Exception(f"student with id {id} not found")

        del self.students[id]

        self.ItemDeleted(wx.dataview.DataViewItem(0), self.student_id_to_dv_item(id))
    
    def get_students(self) -> list[Student]:
        return list(self.students.values())


class StudentInfoEditorPanel(wx.Panel):
    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        #meine
        self.button_import = None

        self.model = StudentInfoDataViewModel()
        self.dv = wx.dataview.DataViewCtrl(self, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_MULTIPLE)
        self.dv.AssociateModel(self.model)
        self.model.DecRef()
        self.append_columns()
        
        self.init_layout()
        self.bind_event_handlers()

    def init_layout(self):
        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        top_sizer.Add(self.dv, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        button_add = wx.Button(self, id=wx.ID_ADD, label="Add")
        button_sizer.Add(button_add, flag=wx.RIGHT, border=5)

        button_delete = wx.Button(self, id=wx.ID_DELETE, label="Delete")
        button_sizer.Add(button_delete)

        top_sizer.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        self.SetSizerAndFit(top_sizer)
        # import button
        button_import = wx.Button(self, label="Import CSV")
        button_sizer.Add(button_import, flag=wx.RIGHT, border=5)
        self.button_import = button_import

    def bind_event_handlers(self):
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dataview_item_activated, self.dv)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_context_menu, self.dv)
        self.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu, self.dv)

        self.Bind(wx.EVT_BUTTON, self.on_button)

        #button import binden
        self.button_import.Bind(wx.EVT_BUTTON, self.on_import_csv)

    def append_columns(self):
        self.dv.AppendTextColumn("ID",
                                 StudentInfoDataViewModel.COL_ID)
        self.dv.AppendColumn(
            StudentInfoEditorPanel.make_text_column("Last Name", StudentInfoDataViewModel.COL_LAST_NAME))
        self.dv.AppendColumn(
            StudentInfoEditorPanel.make_text_column("First Name", StudentInfoDataViewModel.COL_FIRST_NAME))
        self.dv.AppendColumn(
            StudentInfoEditorPanel.make_choice_column("Gender",
                                                      self.model.get_gender_choices(),
                                                      StudentInfoDataViewModel.COL_GENDER))
        self.dv.AppendColumn(
            StudentInfoEditorPanel.make_choice_column("Vetos",
                                                            self.model.get_vetos_choices(),
                                                            StudentInfoDataViewModel.COL_VETOS))

    def make_text_column(title: str, model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(title, wx.dataview.DataViewTextRenderer(mode=wx.dataview.DATAVIEW_CELL_EDITABLE), model_column, width=120, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)

    def make_choice_column(title: str, choices: list[str], model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(title, wx.dataview.DataViewChoiceRenderer(choices), model_column, width=120, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)

    def add_student(self, student: Student) -> int:
        return self.model.add_student(student)
    
    def remove_student_by_id(self, id: int) -> None:
        self.model.remove_student_by_id(id)
    
    def get_selections(self) -> list[int]:
        return [self.model.dv_item_to_student_id(item) for item in self.dv.Selections]
    
    def remove_selection(self) -> None:
        for id in self.get_selections():
            self.model.remove_student_by_id(id)
    
    def on_dataview_item_activated(self, event: wx.dataview.DataViewEvent):
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            self.dv.EditItem(item, column)
    
    def on_button(self, event: wx.Event):
        match event.Id:
            case wx.ID_ADD:
                student = Student(None, "?", "?", Gender.NON_BINARY, set())
                id = self.add_student(student)

                self.dv.EditItem(self.model.student_id_to_dv_item(id), self.dv.GetColumn(1))
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid button")

    def on_menu(self, event: wx.MenuEvent, id: Optional[int]):
        match event.Id:
            case wx.ID_DELETE:
                self.remove_selection()
            case _:
                raise Exception("invalid menu item")

    def on_context_menu(self, event: wx.dataview.DataViewEvent):
        id = self.model.dv_item_to_student_id(event.Item)

        menu = wx.Menu()
        menu.Append(wx.ID_DELETE, "&Delete")
        menu.Bind(wx.EVT_MENU, lambda event, id=id: self.on_menu(event, id))
        self.PopupMenu(menu, event.GetPosition())

    #csv import Dialog
    def on_import_csv(self, event):
        with wx.FileDialog(self,"csv-Datei auswählen",
                           wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path=dialog.GetPath()

        self.import_csv_file(path)

    # csv lesen und student erzeugen
    def import_csv_file(self, path: str):
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                student = self.student_from_csv_row(row)
                self.add_student(student)

    # csv zu student format konvertieren
    def student_from_csv_row(self, row: dict) -> Student:
        last_name = row["LastName"].strip()
        first_name = row["FirstName"].strip()

        gender_str = row["Gender"].strip()
        gender = self.model.inv_gender_map.get(gender_str)

      #  if gender is None:
        #    raise ValueError(f"Unbekanntes Gender: {gender_str}")

        vetos = set()
        vetos_str= []
        if row.get("Vetos [MALE]") == "Ja":
          vetos_str.append("Male")
        if row.get("Vetos [FEMALE]") == "Ja":
          vetos_str.append("Female")
        if row.get("Vetos [NON_BINARY]") == "Ja":
          vetos_str.append("Non-Binary")

        if vetos_str:
            for veto in vetos_str:
                vetos.add(self.model.inv_gender_map[veto.strip()])

        return Student(
            last_name=last_name,
            first_name=first_name,
            gender=gender,
            vetos=vetos
        )
