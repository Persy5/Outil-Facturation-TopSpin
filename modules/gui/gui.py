from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QListView,
    QAbstractItemView, QTreeView, QDateTimeEdit , QDialog , QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QDateTime, Qt
from typing import Callable, List
from datetime import datetime

class GUI(QWidget):
    def __init__(self, program_loop: Callable[[List[str], datetime], None]):
        super().__init__()

        self.program_loop: Callable = program_loop
        self.selected_directories = []
        self.start_date = None
        self.end_date = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        #Folder selection
        self.folder_label = QLabel("Aucun dossier sélectionné")
        self.folder_label.setStyleSheet("color: red;")
        folder_button = QPushButton("Sélectionner au moins un dossier")
        folder_button.clicked.connect(self.select_folders)

        folder_button.setStyleSheet("""
                                   QPushButton { 
                                    color: blue;
                                    }
                                    QPushButton:hover {
                                    font-weight: bold;
                                    }

                                    """)

        layout.addWidget(folder_button)
        layout.addWidget(self.folder_label)

        #Start Datetime
        self.start_datetime_label = QLabel("Sélectionner la date et heure du début de la facturation:")
        self.start_datetime_label.setStyleSheet("color: blue;")
        self.start_datetime_edit = QDateTimeEdit(self)
        self.start_datetime_edit.setCalendarPopup(True)
        self.start_datetime_edit.setDateTime(QDateTime.currentDateTime())

        self.start_datetime_edit.dateTimeChanged.connect(self.set_start_datetime)

        layout.addWidget(self.start_datetime_label)
        layout.addWidget(self.start_datetime_edit)

        #End Datetime
        self.end_datetime_label = QLabel("Sélectionner la date et heure de fin de la facturation:")
        self.end_datetime_label.setStyleSheet("color: blue;")
        self.end_datetime_edit = QDateTimeEdit(self)
        self.end_datetime_edit.setCalendarPopup(True)
        self.end_datetime_edit.setDateTime(QDateTime.currentDateTime())

        # Connect the date-time change to update the selected end date
        self.end_datetime_edit.dateTimeChanged.connect(self.set_end_datetime)

        # Add to the layout
        layout.addWidget(self.end_datetime_label)
        layout.addWidget(self.end_datetime_edit)

        # Start Button
        self.start_button = QPushButton("Calculer")
        self.start_button.setFixedHeight(25)
        self.start_button.setStyleSheet("""
                                        QPushButton{
                                        color: blue;
                                        }
                                        QPushButton:hover {

                                        color: blue;  
                                        font-weight: bold;
                                        }
                                       """)
        self.start_button.setEnabled(False)  # Initially disabled
        self.start_button.clicked.connect(self.start_program)
        layout.addWidget(self.start_button)

        # Result Label
        self.result_label = QLabel("Nombre total de minutes: ")
        self.result_label.setStyleSheet("color: green;")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        self.setWindowTitle('Outil de facturation TopSpin')
        self.setGeometry(600, 400, 600, 400)

    def select_folders(self):
        dialog = QFileDialog(self, "Sélectionner au moins un dossier")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        # Enable multiple selection
        list_view = dialog.findChild(QListView, "listView")
        if list_view:
            list_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            tree_view.setSortingEnabled(True)
            tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            # Filter selections to include only the currently displayed level
            selected_files = dialog.selectedFiles()
            current_path = dialog.directory().absolutePath()
            
            # Ensure only directories at the current level are selected
            valid_directories = [
                path for path in selected_files if path.startswith(current_path) and path != current_path
            ]
            self.selected_directories = valid_directories

            # Set the filtered directories explicitly in the dialog
            if tree_view:
                tree_selection_model = tree_view.selectionModel()
                indexes = tree_selection_model.selectedIndexes()
                
                # Clear parent folder selections
                for index in indexes:
                    if index.data() == current_path:
                        tree_selection_model.select(
                            index, 
                            QAbstractItemView.SelectionMode.Deselect
                        )

            truncated_paths = [self.truncate_path(path) for path in self.selected_directories]
            self.folder_label.setText("Dossier(s) sélectionné(s):\n" + '\n'.join(truncated_paths))
        else:
            self.folder_label.setText("Aucun dossier sélectionné")

    def truncate_path(self, path, max_length=95):
        # Truncate the path if it exceeds max_length, adding "..." in the middle
        if len(path) > max_length:
            return path[:15] + "..." + path[-80:]
        return path
    
    def set_start_datetime(self, datetime):
        self.start_date = datetime
        self.check_complete()

    def set_end_datetime(self, datetime):
        self.end_date = datetime
        self.check_complete()

    def check_complete(self):
        # Enable Start button only if all conditions are met
        if self.selected_directories and self.start_date and self.end_date and self.start_date < self.end_date:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def start_program(self):
        # Logic to execute when the Start button is clicked
        totalTimeInMinutes = self.program_loop(self.selected_directories, self.start_date, self.end_date)

        self.result_label.setText(f"Nombre total de minutes: {totalTimeInMinutes}")
