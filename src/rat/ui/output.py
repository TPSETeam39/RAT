import wx
import wx.dataview
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from rat.io import Student, Role


class OutputPanel(wx.Panel):
    """
    A simple output display for student-to-role assignments, grouped and displayed as a tree.
    """

    COL_ID = 0
    COL_LAST_NAME = 1
    COL_FIRST_NAME = 2
    COL_ROLE = 3
    COL_ROLE_GROUP = 4

    def __init__(self, parent: wx.Window):
        super().__init__(parent)

        self.list = wx.dataview.TreeListCtrl(self)
        self.list.AppendColumn(
            "Student ID",
            flags=wx.dataview.DATAVIEW_COL_SORTABLE
            | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )
        self.list.AppendColumn(
            "Last Name",
            flags=wx.dataview.DATAVIEW_COL_SORTABLE
            | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )
        self.list.AppendColumn(
            "First Name",
            flags=wx.dataview.DATAVIEW_COL_SORTABLE
            | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )
        self.list.AppendColumn(
            "Role",
            flags=wx.dataview.DATAVIEW_COL_SORTABLE
            | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )
        self.list.AppendColumn(
            "Role Group",
            flags=wx.dataview.DATAVIEW_COL_SORTABLE
            | wx.dataview.DATAVIEW_COL_RESIZABLE,
        )

        self._init_layout()
        self._bind_event_handlers()

    def _init_layout(self):
        main_sizer = wx.BoxSizer(orient=wx.VERTICAL)
        main_sizer.Add(self.list, 1, wx.EXPAND | wx.ALL, 5)

        self.export_btn = wx.Button(self, label="Export as PDF")

        main_sizer.Add(self.export_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizerAndFit(main_sizer)

    def _bind_event_handlers(self):
        self.export_btn.Bind(wx.EVT_BUTTON, self.on_export_pdf)

    def clear(self):
        """
        Clears all elements from the output display.
        """
        self.list.DeleteAllItems()

    def load_group(self, group_name: str, assignments: dict[Student, Role]):
        """
        Loads a list of assignments into the output display as a group.

        :param group_name: The name of the group.
        :type group_name: str
        :param assignments: The student-to-role assignments for the group.
        :type assignments: dict[Student, Role]
        """
        group_root = self.list.AppendItem(self.list.RootItem, group_name)

        for student, role in assignments.items():
            item = self.list.AppendItem(group_root, str(student.id))
            self.list.SetItemText(item, self.COL_LAST_NAME, student.last_name)
            self.list.SetItemText(item, self.COL_FIRST_NAME, student.first_name)
            self.list.SetItemText(item, self.COL_ROLE, role.name)
            self.list.SetItemText(item, self.COL_ROLE_GROUP, role.group)

        self.list.Expand(group_root)

    def on_export_pdf(self, event):

        # Öffnet einen Datei-Dialog, damit der Nutzer den Speicherort für die PDF-Datei auswählen kann
        with wx.FileDialog(
                self,
                "Save PDF",
                wildcard="PDF files (*.pdf)|*.pdf",
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,  # erlaubt Überschreiben
        ) as fileDialog:

            # Wenn der Nutzer den Dialog abbricht, abbrechen
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Pfad, den der Nutzer ausgewählt hat
            pathname = fileDialog.GetPath()

        # Erstellen eines ReportLab PDF-Dokuments mit A4-Seite
        doc = SimpleDocTemplate(pathname, pagesize=A4)
        elements = []  # Liste von Elementen, die in das PDF eingefügt werden

        # Styles für Text
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]  # Standard-Text
        bold_style = ParagraphStyle(
            name="BoldStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",  # fette Schrift
        )

        # -------------------------
        # Table Data vorbereiten
        # -------------------------
        data = []  # Liste für alle Zeilen der Tabelle

        # Header-Zeile der Tabelle
        data.append([
            Paragraph("Student ID", bold_style),
            Paragraph("Last Name", bold_style),
            Paragraph("First Name", bold_style),
            Paragraph("Role", bold_style),
            Paragraph("Role Group", bold_style),
        ])

        # -------------------------
        # Daten aus TreeListCtrl auslesen
        # -------------------------
        root = self.list.GetRootItem()  # Root-Element der TreeListCtrl
        group_item = self.list.GetFirstChild(root)  # erstes Gruppen-Item

        # Schleife über alle Gruppen
        while group_item.IsOk():

            group_name = self.list.GetItemText(group_item)  # Gruppenname

            # Group row (fett), als Platzhalter für Spalten
            data.append([
                Paragraph(group_name, bold_style),
                "", "", "", ""  # leere Zellen für die restlichen Spalten
            ])

            # Schleife über alle Studenten innerhalb der Gruppe
            student_item = self.list.GetFirstChild(group_item)

            while student_item.IsOk():
                row = [
                    Paragraph(self.list.GetItemText(student_item, self.COL_ID), normal_style),
                    Paragraph(self.list.GetItemText(student_item, self.COL_LAST_NAME), normal_style),
                    Paragraph(self.list.GetItemText(student_item, self.COL_FIRST_NAME), normal_style),
                    Paragraph(self.list.GetItemText(student_item, self.COL_ROLE), normal_style),
                    Paragraph(self.list.GetItemText(student_item, self.COL_ROLE_GROUP), normal_style),
                ]

                data.append(row)  # Zeile zur Tabelle hinzufügen
                student_item = self.list.GetNextSibling(student_item)  # nächsten Studenten holen

            group_item = self.list.GetNextSibling(group_item)  # nächste Gruppe holen

        # -------------------------
        # Tabelle bauen
        # -------------------------
        table = Table(data, repeatRows=1)  # repeatRows=1: Header wird auf jeder Seite wiederholt

        # Tabelle stylen
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # Hintergrund Header-Zeile
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),  # Rahmenlinien
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # vertikale Ausrichtung
            ])
        )

        # Tabelle zum PDF-Element hinzufügen
        elements.append(table)

        # PDF erstellen
        doc.build(elements)

        # Rückmeldung an Nutzer
        wx.MessageBox(
            "PDF successfully exported!",
            "Success",
            wx.OK | wx.ICON_INFORMATION
        )