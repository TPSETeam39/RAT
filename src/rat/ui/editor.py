from typing import Any, override
from itertools import combinations
from dataclasses import replace

import wx
import wx.dataview

from rat.io import StudentGender, RoleGender, Student, GenderVetoOption

# look at the wxWidgets dataview sample to understand this shit
class StudentInfoDataViewModel(wx.dataview.DataViewModel):
    """
    The DataViewModel used by the student editor.
    
    Stores a list of students with ID, last name, first name, gender and vetoes.
    Students can be added, removed and accesed.
    """

    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_GENDER = 3
    COL_VETOES = 4

    # item with ID 0 (an invalid ID) is the root here
    ROOT_ITEM = wx.dataview.DataViewItem(0)

    GENDER_MAP = {
        StudentGender.FEMALE: "Female",
        StudentGender.MALE: "Male",
        StudentGender.NON_BINARY: "Non-Binary"
    }

    GENDER_VETO_OPTION_MAP = {
        frozenset({ RoleGender.NON_BINARY }): GenderVetoOption.NON_BINARY_ONLY,
        frozenset({ RoleGender.MALE }): GenderVetoOption.MALE_ONLY,
        frozenset({ RoleGender.FEMALE }): GenderVetoOption.FEMALE_ONLY,
        frozenset({ RoleGender.MALE, RoleGender.NON_BINARY }): GenderVetoOption.MALE_AND_NON_BINARY,
        frozenset({ RoleGender.FEMALE, RoleGender.NON_BINARY }): GenderVetoOption.FEMALE_AND_NON_BINARY,
        frozenset({ RoleGender.FEMALE, RoleGender.MALE }): GenderVetoOption.FEMALE_AND_MALE,
        frozenset({}): GenderVetoOption.NO_VETOES
    }

    LIST_SEP = ", "

    def __init__(self):
        super().__init__()

        self.students: dict[int, Student] = {}
        self.next_id = 0

        self.inv_gender_map = {v: k for k, v in self.GENDER_MAP.items()}
    
    def student_id_to_dv_item(self, id: int) -> wx.dataview.DataViewItem:
        """
        Returns the DataViewItem representing the student with the given ID.
        
        :param id: The student ID.
        :type id: int
        :return: The matching DataViewItem.
        :rtype: DataViewItem
        """
        if id < 0:
            raise Exception(f"invalid student id {id}")

        # id is incremented by one because 0 represents an invalid item
        return wx.dataview.DataViewItem(id + 1)

    def student_to_dv_item(self, student: Student) -> wx.dataview.DataViewItem:
        """
        Returns the DataViewItem representing the given student.

        :param student: The student.
        :type student: Student
        :return: The matching DataViewItem.
        :rtype: DataViewItem
        """
        return self.student_id_to_dv_item(student.id)
    
    def dv_item_to_student_id(self, item: wx.dataview.DataViewItem) -> int:
        """
        Returns the ID of the student represented by the given DataViewItem.
        
        :param item: The DataViewItem.
        :type item: wx.dataview.DataViewItem
        :return: The represented student's ID.
        :rtype: int
        """
        if item == self.ROOT_ITEM:
            raise Exception("root item doesn't have a student id")

        # student id is one less than the item id, because 0 is an invalid item
        return int(item.ID) - 1
    
    def get_gender_choices(self) -> list[str]:
        """
        Gets the list of gender choices.
        
        :return: The list of gender choices.
        :rtype: list[str]
        """
        return list(self.GENDER_MAP.values())

    def get_vetoes_choices(self) -> list[str]:
        """
        Gets the list of gender veto choices.
        
        :return: The list of gender veto choices.
        :rtype: list[str]
        """
        choices = [""]
        choices.extend(self.get_gender_choices())
        for pair in combinations(self.GENDER_MAP, 2):
            choices.append(self._vetoes_to_string(pair))
        return choices

    def add_student(self, student: Student) -> int:
        """
        Adds the student given to the model.

        Make sure the student ID is valid and unique.
        
        :param student: The student to be added.
        :type student: Student
        :return: The ID of the added student.
        :rtype: int
        """
        if student.id < 0:
            raise Exception(f"invalid student id {student.id}")

        if student.id in self.students:
            raise Exception(f"student with id {student.id} already exists")
        
        if student.id >= self.next_id:
            self.next_id = student.id + 1

        self.students[student.id] = student

        self.ItemAdded(self.ROOT_ITEM, self.student_to_dv_item(student))
        return student.id
    
    def add_new_student(self) -> int:
        """
        Adds a new student, with default attributes, to the model.
        
        :return: The ID of the added student.
        :rtype: int
        """
        student = Student(self.next_id, StudentGender.NON_BINARY)
        self.next_id += 1
        
        return self.add_student(student)
    
    def remove_student_by_id(self, id: int) -> None:
        """
        Removes a student, specified by ID, from the model.
        
        :param id: The ID of the student to be removed.
        :type id: int
        """
        if id < 0:
            raise Exception(f"invalid student id {id}")

        if id not in self.students:
            raise Exception(f"student with id {id} not found")

        del self.students[id]

        self.ItemDeleted(self.ROOT_ITEM, self.student_id_to_dv_item(id))
    
    def get_students_map(self) -> dict[int, Student]:
        """
        Gets all students in this model as a map of student IDs to Students.
        
        :return: The map of student IDs to students.
        :rtype: dict[int, Student]
        """
        return self.students

    def get_students(self) -> set[Student]:
        """
        Gets all students in this model as a set.
        
        :return: The set of students.
        :rtype: set[Student]
        """
        return set(self.get_students_map().values())
    
    def _vetoes_to_string(self, vetoes: set[StudentGender]) -> str:
        return self.LIST_SEP.join([f"{self.GENDER_MAP[v]}" for v in vetoes])

    def _vetoes_from_string(self, string: str) -> set[StudentGender]:
        if not string:
            return set()

        vetoes = set()
        for veto in string.split(self.LIST_SEP):
            vetoes.add(self.inv_gender_map[veto])
        return vetoes

    @override
    def IsContainer(self, item: wx.dataview.DataViewItem) -> bool:
        # only the root item is a container, because this is a list
        return item == self.ROOT_ITEM

    @override
    def GetParent(self, item: wx.dataview.DataViewItem) -> wx.dataview.DataViewItem:
        # all items share a single parent, because this is a list
        return self.ROOT_ITEM

    @override
    def GetChildren(self, item: wx.dataview.DataViewItem, children: list[wx.dataview.DataViewItem]) -> int:
        if item == self.ROOT_ITEM:
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
            case self.COL_VETOES:
                return self._vetoes_to_string(student.get_vetoed_genders())
            case _:
                raise Exception("invalid column")

    @override
    def SetValue(self, variant: Any, item: wx.dataview.DataViewItem, col: int) -> bool:
        id = self.dv_item_to_student_id(item)

        match col:
            case self.COL_ID:
                raise Exception("id cannot be set")
            case self.COL_LAST_NAME:
                self.students[id] = replace(self.students[id], last_name=variant)
            case self.COL_FIRST_NAME:
                self.students[id] = replace(self.students[id], first_name=variant)
            case self.COL_GENDER:
                self.students[id] = replace(self.students[id], gender=self.inv_gender_map[variant])
            case self.COL_VETOES:
                self.students[id] = replace(self.students[id], gender_veto_option=self.GENDER_VETO_OPTION_MAP[frozenset(self._vetoes_from_string(variant))])
            case _:
                raise Exception("invalid column")
        
        return True


class StudentInfoEditorPanel(wx.Panel):
    """
    A student info editor, presented as an editable list.

    The columns for last name, first name, gender and vetoes can be edited by selecting them.
    Additionally there is an immutable ID column.

    Students can be added or removed using the buttons below the table or by using the context menu.
    This functionality is also exposed as part of the public API.

    The stored students can be accessed using the public API.
    """

    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        self.model = StudentInfoDataViewModel()
        self.dataview = wx.dataview.DataViewCtrl(self, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_MULTIPLE)
        self.dataview.AssociateModel(self.model)
        self._append_columns()
        
        self._init_layout()
        self._bind_event_handlers()

    def add_student(self, student: Student) -> int:
        """
        Adds the student given to the editor.

        Make sure the student ID is valid and unique.
        
        :param student: The student to be added.
        :type student: Student
        :return: The ID of the added student.
        :rtype: int
        """
        return self.model.add_student(student)
    
    def add_new_student(self) -> int:
        """
        Adds a new student, with default attributes, to the editor.
        
        :return: The ID of the added student.
        :rtype: int
        """
        return self.model.add_new_student()
    
    def remove_student_by_id(self, id: int) -> None:
        """
        Removes a student, specified by ID, from the editor.
        
        :param id: The ID of the student to be removed.
        :type id: int
        """
        self.model.remove_student_by_id(id)
    
    def get_students_map(self) -> dict[int, Student]:
        """
        Gets all students in this editor as a map of student IDs to Students.
        
        :return: The map of student IDs to students.
        :rtype: dict[int, Student]
        """
        return self.model.get_students_map()

    def get_students(self) -> set[Student]:
        """
        Gets all students in this editor as a set.
        
        :return: The set of students.
        :rtype: set[Student]
        """
        return self.model.get_students()

    def _init_layout(self):
        top_sizer = wx.BoxSizer(orient=wx.VERTICAL)

        top_sizer.Add(self.dataview, 1, wx.EXPAND | wx.ALL, 5)

        button_sizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        button_add = wx.Button(self, id=wx.ID_ADD, label="Add")
        button_sizer.Add(button_add, flag=wx.RIGHT, border=5)

        button_delete = wx.Button(self, id=wx.ID_DELETE, label="Delete")
        button_sizer.Add(button_delete)

        top_sizer.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)

        self.SetSizerAndFit(top_sizer)

    def _bind_event_handlers(self):
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self._on_dataview_item_activated, self.dataview)
        self.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self._on_context_menu, self.dataview)
        self.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu, self.dataview)

        self.Bind(wx.EVT_BUTTON, self._on_button)

    def _append_columns(self):
        self.dataview.AppendTextColumn("ID",
                                 StudentInfoDataViewModel.COL_ID)
        self.dataview.AppendColumn(
            StudentInfoEditorPanel._make_text_column("Last Name", StudentInfoDataViewModel.COL_LAST_NAME))
        self.dataview.AppendColumn(
            StudentInfoEditorPanel._make_text_column("First Name", StudentInfoDataViewModel.COL_FIRST_NAME))
        self.dataview.AppendColumn(
            StudentInfoEditorPanel._make_choice_column("Gender",
                                                      self.model.get_gender_choices(),
                                                      StudentInfoDataViewModel.COL_GENDER))
        self.dataview.AppendColumn(
            StudentInfoEditorPanel._make_choice_column("Vetoes",
                                                            self.model.get_vetoes_choices(),
                                                            StudentInfoDataViewModel.COL_VETOES))

    def _make_text_column(title: str, model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(title, wx.dataview.DataViewTextRenderer(mode=wx.dataview.DATAVIEW_CELL_EDITABLE), model_column, width=120, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)

    def _make_choice_column(title: str, choices: list[str], model_column: int) -> wx.dataview.DataViewColumn:
        return wx.dataview.DataViewColumn(title, wx.dataview.DataViewChoiceRenderer(choices), model_column, width=120, flags=wx.dataview.DATAVIEW_COL_SORTABLE | wx.dataview.DATAVIEW_COL_RESIZABLE)
    
    def _get_selections(self) -> list[int]:
        return [self.model.dv_item_to_student_id(item) for item in self.dataview.Selections]
    
    def _remove_selection(self) -> None:
        for id in self._get_selections():
            self.model.remove_student_by_id(id)
    
    def _on_dataview_item_activated(self, event: wx.dataview.DataViewEvent):
        item = event.GetItem()
        column = event.GetDataViewColumn()
        if column:
            self.dataview.EditItem(item, column)
    
    def _on_button(self, event: wx.Event):
        match event.Id:
            case wx.ID_ADD:
                id = self.add_new_student()
                
                # start editing in the first column automatically
                self.dataview.EditItem(self.model.student_id_to_dv_item(id), self.dataview.GetColumn(self.model.COL_LAST_NAME))
            case wx.ID_DELETE:
                self._remove_selection()
            case _:
                raise Exception("invalid button")

    def _on_menu(self, event: wx.MenuEvent, item: wx.dataview.DataViewItem):
        match event.Id:
            case wx.ID_DELETE:
                self._remove_selection()
            case _:
                raise Exception("invalid menu item")

    def _on_context_menu(self, event: wx.dataview.DataViewEvent):
        menu = wx.Menu()
        menu.Append(wx.ID_DELETE, "&Delete")
        menu.Bind(wx.EVT_MENU, lambda event, item=event.Item: self._on_menu(event, item))
        self.PopupMenu(menu, event.GetPosition())
