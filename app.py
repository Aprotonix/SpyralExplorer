from log import *


from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton,QLabel,QScrollArea,QHBoxLayout,QFrame,QMenu,QProgressBar,QFileIconProvider,QGraphicsScene, QGraphicsPixmapItem, QGraphicsBlurEffect
from PySide6.QtCore import Signal, QTimer,Qt,QFileInfo, QUrl,QMimeData, QRectF
from PySide6.QtGui import QGuiApplication,QActionGroup, QAction, QIcon, QDrag, QPixmap ,QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from explorer import *
from theme import *
import time #Get date for files
import traceback #Debug Only
import sound
import subprocess # Open terminal
import pyperclip

# =========== INFO ==========
#    App Made by Aprotonix
#
# explorer Object == app ObjectItemWidget.object

# To select object do ObjectItemWidget.select()
# [ No ] exporer.path_content[i].object.selected = True : Don't Actualise




APP_NAME = "Spyral Files Explorator 0.5 (alpha)"



def formatSize(size):
        size_mode = 1024
        unit = "o"
        if size > size_mode**3:
            unit = "Go"
            size = size/size_mode**3
        elif size > size_mode**2:
            unit = "Mo"
            size = size / size_mode ** 2
        elif size > size_mode :
            unit = "Ko"
            size = size /size_mode

        return str(round(size,2)) + " " + unit

def apply_stylesheet(widget, path="style.qss"):
    try:
        with open(path, "r") as f:
            #widget.setStyleSheet("#window {background: " + widget.theme.current_theme["windowBG"]+";}")
            #widget.setStyleSheet("#frame {background: " + widget.theme.current_theme["windowBG"]+";}")
            widget.setStyleSheet(f.read())
    except Exception as e:
        log(f"Erreur lors du chargement du style : {e}", "E")



class ObjectItemWidget(QWidget):
    clicked = Signal()
    right_clicked = Signal()

    def __init__(self):

        super().__init__()
        self.fram_name = "object_item_widget"
        self.fram_name_selected = "object_item_widget_selected"
        self.frame = QFrame()
        

    def generateView(self, object):

        
        self.setFixedHeight(50)
        self.setFixedWidth(100)

        self.frame.setObjectName(self.fram_name)

        
        self.object = object
        self.label_name = QLabel(object.name)

        frame_layout = QHBoxLayout()

        frame_layout.addWidget(self.label_name)
        self.frame.setLayout(frame_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)


    def select(self):
        self.frame.setObjectName(self.fram_name_selected)
        self.object.selected = True

    def unselect(self):
        self.frame.setObjectName(self.fram_name)
        self.object.selected = False



    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            
        elif event.button() == Qt.RightButton:
 
            self.right_clicked.emit()  
        super().mousePressEvent(event)

class NormalObjectItemWidget(ObjectItemWidget):
 

    def __init__(self):

        super().__init__()
        

    def generateView(self, object, show_icon):

        self.setFixedHeight(50) #Forced, Need a solution

        self.frame.setObjectName(self.fram_name )
        self.frame_layout = QHBoxLayout()
        
        self.setContentsMargins(10, 0, 0, 0) 
        self.frame_layout.setContentsMargins(10, 0, 0, 0) 


        
        self.object = object
        
        if show_icon:

            self.label_icon = QLabel()
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(QFileInfo(object.path))

            pixmap = icon.pixmap(15, 15)
            self.label_icon.setPixmap(pixmap)
            
            
            self.frame_layout.addWidget(self.label_icon)
        else:

            self.label_type = QLabel(" " + getTextIcon(object))
            self.label_type.setStyleSheet("font-size: 20px")
            
            self.label_type.setObjectName("object_item_label")
            
            self.frame_layout.addWidget(self.label_type)
        

        self.label_name = QLabel(object.name)

        #Desactivated because block drag and drop
        #self.label_name.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) #Label became selectable
        
        self.label_name.setObjectName("object_item_label")
        self.frame_layout.addWidget(self.label_name)

       
        self.label_size = QLabel("--")
        self.label_size.setObjectName("object_item_label")
        if object.type != "DIR": self.label_size.setText(formatSize(object.size))

    
        
        
        self.frame_layout.addWidget(self.label_size)
        self.frame_layout.setSpacing(0)
       

        self.frame.setLayout(self.frame_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

class FavoriteObjectItemWidget(ObjectItemWidget):
    

    def __init__(self):

        super().__init__()
        self.fram_name = "item_favorite_widget"
        self.fram_name_selected = "item_favorite_widget_selected"

    def generateView(self, object):

        
        self.setFixedHeight(55)
        self.setFixedWidth(220)

        self.frame.setObjectName(self.fram_name)

        self.object = object
        
        self.label_name = QLabel(object.name)
        self.label_name.setObjectName("object_item_label")

        frame_layout = QHBoxLayout()

        frame_layout.addWidget(self.label_name)

       
        self.frame.setLayout(frame_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.frame)
        self.setLayout(main_layout)

#The code of this class is ugly
class FavoriteDriveItemWidget(ObjectItemWidget):
    

    def __init__(self):

        super().__init__()
        self.fram_name = "item_favorite_widget"
        self.fram_name_selected = "item_favorite_widget_selected"

    def generateView(self, object):

        
        self.setFixedHeight(90)
        self.setFixedWidth(220)
       
        self.frame.setObjectName(self.fram_name)
        self.frame_title = QFrame()
        

        self.object = object
        
        

        frame_layout = QVBoxLayout()


        fram_title_layout = QHBoxLayout()
        

        self.label_name = QLabel(object.name)
        self.label_name.setObjectName("object_item_label")
        
        self.label_size = QLabel(formatSize(object.usage.total))
        self.label_size.setAlignment(Qt.AlignmentFlag.AlignRight)

        fram_title_layout.addWidget(self.label_name)
        fram_title_layout.addWidget(self.label_size)
        
        self.progress = QProgressBar()
        
        self.progress.setValue(self.object.usage.percent + 0.5)# 0.5 to not have a bar not filled
        self.progress.setFixedWidth(180)
        self.progress.setFixedHeight(10)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 100px;
                padding: 0px;
                
                
               
            }
            QProgressBar::chunk {
                background-color: #3daee9;
                border-radius: 100px;
            }
        """)

       
        
        self.frame_title.setLayout(fram_title_layout)

        frame_layout.addWidget(self.frame_title)
        frame_layout.addWidget(self.progress)
        self.frame.setLayout(frame_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.frame)
        
        self.setLayout(main_layout)
 
class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event):
       
        if self.childAt(event.position().toPoint()) is None:
            self.clicked.emit()
        super().mousePressEvent(event)

class FileExplorerApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        
        self.resize(1000, 600)

        
        self.explorer = Explorer()
        
        self.theme = Theme()
        self.theme.setTheme(6)
        self.theme.applyThemeToStyle()
        self.refresh_window()
       
        self.message_timer = QTimer()
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.clearMessage)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        #Parameters
        self.show_icon = True
        self.show_button_text = True
        self.show_file_icon = True       #Heavy
        self.enable_blur = True          #Heavy
        self.enable_transparency = False


        self.multi_selecting_enabled = False
        self.range_selecting_enabled = False

        
        

        self.generateInterface()#GENERATION DES WIDGET
        
        self.generateFavorits()
        self.explorer.actualisePathContent()
        self.showPathContent()


    def generateInterface(self):
        ##Navigation Bar---------------------------------
        #Widgets
        self.navigation_widget = QFrame()
        self.navigation_widget.setObjectName("top_widget")

        
        self.button_go_back =  QPushButton("↑")
        self.button_go_back.clicked.connect(self.whenButtonGoBackCliked)
        self.button_go_back.setObjectName("navigation_widget")


        self.button_refresh =  QPushButton("↻")
        self.button_refresh.clicked.connect(self.whenButtonRefreshCliked)

        
        self.input_path = QLineEdit(self.explorer.current_path)
        self.input_path.returnPressed.connect(self.whenButtonOpenPathCliked)

        self.button_open_path = QPushButton("➜")
        self.button_open_path.clicked.connect(self.whenButtonOpenPathCliked)
        #Layout
        self.navigation_layout = QHBoxLayout(self.navigation_widget)
        self.navigation_layout.addWidget(self.button_go_back)
        self.navigation_layout.addWidget(self.button_refresh)
        self.navigation_layout.addWidget(self.input_path)
        self.navigation_layout.addWidget(self.button_open_path)

        
      
        ##Tool Bar---------------------------------------------------------
        self.toolbar_fram = QFrame()
        self.toolbar_fram.setObjectName("tool_widget")
        

        self.button_copy = QPushButton()
        self.button_copy.clicked.connect(self.whenButtonCopyClicked)
        if self.show_icon:self.button_copy.setIcon(self.getIcon("copy"))
        if self.show_button_text:self.button_copy.setText("Copy")

        self.button_cut = QPushButton()
        self.button_cut.clicked.connect(self.whenButtonCutClicked)
        if self.show_icon:self.button_cut.setIcon(self.getIcon("cut"))
        if self.show_button_text:self.button_cut.setText("Cut")


        self.button_paste = QPushButton()
        self.button_paste.clicked.connect(self.whenButtonPasteClicked)
        if self.show_icon:self.button_paste.setIcon(self.getIcon("paste"))
        if self.show_button_text:self.button_paste.setText("Paste")

        self.button_delete = QPushButton()
        self.button_delete.clicked.connect(self.whenButtonDeleteClicked)
        if self.show_icon:self.button_delete.setIcon(self.getIcon("delete"))
        if self.show_button_text:self.button_delete.setText("delete")

        self.label_separator = QLabel(" | ")#Optimize
      
        self.button_new_folder = QPushButton()
        self.button_new_folder.clicked.connect(self.whenButtoNewFolderClicked)
        if self.show_icon:self.button_new_folder.setIcon(self.getIcon("new_folder"))
        if self.show_button_text:self.button_new_folder.setText("New Folder")

        self.label_new_item_type = QLabel("New item type")

        self.input_new_item = QLineEdit()
        self.input_new_item.setPlaceholderText("New item name")
        self.input_new_item.returnPressed.connect(self.createItem)
        
       
        self.button_new_file = QPushButton()
        self.button_new_file.clicked.connect(self.whenButtoNewFileClicked)
        if self.show_icon:self.button_new_file.setIcon(self.getIcon("add"))
        if self.show_button_text:self.button_new_file.setText("Create")


        self.combo_type_new = QPushButton("File  ▼")#QComboBox()

        self.menu_files_type = QMenu()
        self.action_group_file_type = QActionGroup( self.menu_files_type)
        self.action_group_file_type.setExclusive(True)

        self.generateFilesTypeToComboList()
        self.combo_type_new.clicked.connect(self.show_menu)
        

        #Layout for tool bar
        self.toolbar_layout = QHBoxLayout(self.toolbar_fram)
        self.toolbar_layout.addWidget(self.button_copy)  
        self.toolbar_layout.addWidget(self.button_cut)  
        self.toolbar_layout.addWidget(self.button_paste)  
        self.toolbar_layout.addWidget(self.button_delete)  

        self.toolbar_layout.addWidget(self.label_separator)

        self.toolbar_layout.addWidget(self.button_new_folder)        
        self.toolbar_layout.addWidget(self.input_new_item)
        self.toolbar_layout.addWidget(self.label_new_item_type)
        self.toolbar_layout.addWidget(self.combo_type_new)
        self.toolbar_layout.addWidget(self.button_new_file)


        ###Explorer Zone ===================================================

        self.frame_explorer =  QFrame()
        self.frame_explorer.setObjectName("explorer_frame")
        self.frame_explorer_layout = QHBoxLayout()
    
        ##Favorits Zone-----------------------------------------------------

        self.frame_fav = QFrame()
        self.frame_fav_layout = QVBoxLayout()
        self.frame_fav.setLayout(self.frame_fav_layout)
        self.frame_fav.setFixedWidth(250)

        #


        #scroll list..................................
        self.scroll_area_fav = QScrollArea()
        self.scroll_area_fav.setWidgetResizable(True)
        self.scroll_area_fav.verticalScrollBar().setSingleStep(15)
        self.scroll_area_fav.setFixedWidth(240)

        self.list_fav_widget = []
        self.frame_list_fav = QFrame()
        self.frame_list_fav.setObjectName("fav_frame")
       
        self.frame_list_fav_layout =QVBoxLayout()
        self.frame_list_fav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.frame_list_fav_layout.setSpacing(0)                   # not work
        self.frame_list_fav_layout.setContentsMargins(0, 0, 0, 0)  # not work
        self.frame_list_fav.setLayout(self.frame_list_fav_layout)

        self.scroll_area_fav.setWidget(self.frame_list_fav)
        #.............................................

        self.frame_fav_layout.addWidget(self.scroll_area_fav)

        ##Files Zone--------------------------------------------------------
        self.list_wiget_object_item = []

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().setSingleStep(20)#Speed of scrolling
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
         
        

        self.files_container = ClickableFrame()
        self.files_container.clicked.connect(self.whenFilesFrameClicked)
        self.files_container.setObjectName("file_frame")
       
        self.files_container_layout =QVBoxLayout()
        self.files_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.files_container_layout.setSpacing(0)                     #Not work why ?
        self.files_container_layout.setContentsMargins(0, 0, 0, 0)    #Not work
        self.files_container.setLayout(self.files_container_layout)

        self.scroll_area.setWidget(self.files_container)
        #---------------------------------------------------------------
        ##Detail Zone
        self.frame_detail = QFrame()
        self.frame_detail_layout = QVBoxLayout()
        self.frame_detail_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.frame_detail.setFixedWidth(280)

        self.entry_detail_object_name = QLineEdit()
        self.entry_detail_object_name.setStyleSheet("font-size: 18px;font-weight: bold")
        self.entry_detail_object_name.returnPressed.connect(self.whenButtonRenamePressed)
        self.frame_detail_layout.addWidget(self.entry_detail_object_name)

        self.button_rename = QPushButton()
        self.button_rename.clicked.connect(self.whenButtonRenamePressed)
        self.frame_detail_layout.addWidget(self.button_rename)
        if self.show_icon:self.button_rename.setIcon(self.getIcon("edit"))
        if self.show_button_text:self.button_rename.setText("Rename")

        self.button_copy_path = QPushButton()
        self.button_copy_path.clicked.connect(self.whenButtonCopyPathPressed)
        self.frame_detail_layout.addWidget(self.button_copy_path)
        if self.show_icon:self.button_copy_path.setIcon(self.getIcon("copy"))
        if self.show_button_text:self.button_copy_path.setText("Copy path")

        self.button_open_terminal = QPushButton()
        self.button_open_terminal.clicked.connect(self.whenOpenTerminalButtonCliked)
        self.frame_detail_layout.addWidget(self.button_open_terminal)
        if self.show_icon:self.button_open_terminal.setIcon(self.getIcon("terminal"))
        if self.show_button_text:self.button_open_terminal.setText("Open in a terminal")

        self.frame_media = QFrame()
        self.frame_media_layout = QHBoxLayout()

        self.button_play_media = QPushButton()
        self.button_play_media.clicked.connect(self.playMedia)
        self.frame_media_layout.addWidget(self.button_play_media)
        if self.show_icon:self.button_play_media.setIcon(self.getIcon("play"))
        if self.show_button_text:self.button_play_media.setText("Play")

        self.button_stop_media = QPushButton()
        self.button_stop_media.clicked.connect(self.media_player.stop)
        self.frame_media_layout.addWidget(self.button_stop_media)
        if self.show_icon:self.button_stop_media.setIcon(self.getIcon("stop"))
        if self.show_button_text:self.button_stop_media.setText("Stop")

        self.frame_media.setLayout(self.frame_media_layout)
        self.frame_detail_layout.addWidget(self.frame_media)

        self.label_detail = QLabel()
        self.frame_detail_layout.addWidget(self.label_detail)


        self.frame_detail.setLayout(self.frame_detail_layout)
        #-------------------------------------------------------------

        self.frame_explorer_layout.addWidget(self.frame_fav)
        self.frame_explorer_layout.addWidget(self.scroll_area)
        self.frame_explorer_layout.addWidget(self.frame_detail)
        self.frame_explorer.setLayout(self.frame_explorer_layout)


       # ===================================================

        ##Info Frame ----------------------------------------

        self.frame_info = QFrame()
        self.frame_info.setObjectName("frame_info")

    
        self.label_info = QLabel("")
        self.label_info.setObjectName("info_label")
        self.label_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) #Label became selectable

        self.label_key = QLabel("")
        self.label_key.setObjectName("key_label")
        self.label_key.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.frame_info_layout = QHBoxLayout()
        self.frame_info_layout.addWidget(self.label_info)
        self.frame_info_layout.addWidget(self.label_key)
       
        self.frame_info.setLayout(self.frame_info_layout)

        ##Main Window----------------------------------------

        central_widget = QFrame()
        central_widget.setObjectName("window")
        # central_widget.setContentsMargins(0, 0, 0, 0) #
        # self.setContentsMargins(0, 0, 0, 0)
        #self.setWindowFlags(Qt.FramelessWindowHint)
    
        if self.enable_transparency :self.setWindowOpacity(0.95)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if self.enable_blur:
            self.applyBlurBackroundCustom(50)
            #self.applyBlurBackrounWindows()
           
        



        self.setCentralWidget(central_widget)  

        self.message_label = QLabel("")
        self.message_label.setObjectName("message_label")

        self.main_layout = QVBoxLayout(central_widget)  
        self.main_layout.addWidget(self.navigation_widget)
        self.main_layout.addWidget(self.toolbar_fram)
        self.main_layout.addWidget(self.message_label)
        self.main_layout.addWidget(self.frame_explorer)
        self.main_layout.addWidget(self.frame_info)  

        self.main_layout.setSpacing(5)



    # Combo list------------
    def generateFilesTypeToComboList(self):
        

        old_selected = self.getSelectedAction()
        old_selected = old_selected.data() if self.getSelectedAction() else None

       #Clear Menu
        for action in self.action_group_file_type.actions():
            self.menu_files_type.removeAction(action)     
            self.action_group_file_type.removeAction(action)    
            action.deleteLater()           

       
        action = self.addFileTypeChoiceOnMenu("File", self.menu_files_type, data="file")
        action.setChecked(True)
        self.addFileTypeChoiceOnMenu("Folder", self.menu_files_type, data="file")
        #self.combo_type_new.setMenu(self.menu_files_type) #Better but weird view
        menu =  self.menu_files_type.addMenu("Templates")
        for template in self.explorer.get_templates_list():
            self.addFileTypeChoiceOnMenu(template, menu, "template")
        
        self.loadFilesTypeToComboList(old_selected)

    def addFileTypeChoiceOnMenu(self, texte, menu, data):
        action = QAction(texte, menu)
        action.setCheckable(True)

        action.setData(data)
        menu.addAction(action)
        self.action_group_file_type.addAction(action)

        # Connexion du signal triggered à la méthode de gestion
        action.triggered.connect(lambda checked, a=action: self.whenFileTypeActionSelected(a))

        return action

    def getSelectedAction(self):
        try:
            for action in self.action_group_file_type.actions():
                if action.isChecked():
                    return action
        except: return None

    def loadFilesTypeToComboList(self,old_selected=None):
        #print("loadFilesTypeToComboList")
        #Sort by most used
        sorted_types = sorted(
            self.explorer.files_types,
            key=lambda x: x.get("using", 0),
            reverse=True
        )

    
        # Add to combo list
        for index, ftype in enumerate(sorted_types):
            # self.combo_type_new.addItem(
            #     f"{ftype['type'].upper()} - {ftype['description']}",
            #     userData=self.explorer.files_types.index(ftype)#Not Optized
            # )
            action = self.addFileTypeChoiceOnMenu(texte=f"{ftype['type'].upper()} - {ftype['description']}",
                                        menu=self.menu_files_type,
                                          data=self.explorer.files_types.index(ftype))#Not Optized
            if old_selected==action.data():
                action.setChecked(True)
        # #Restore old 
        # print(old_selected)
        # if old_selected :
        #     index = self.action_group_file_type.actions().index(old_selected)
        #     print(index)
        #     if index != -1:
        #         self.action_group_file_type.actions()[index].setChecked(True)


    def getIcon(self, icon_name):
        
        return QIcon(self.explorer.getIconPath(icon_name))
    ###KEY EVENT ==========================================================================================

    def keyPressEvent(self, event):
        key = event.key()
        ctrl_pressed = QGuiApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier
        shift_pressed = QGuiApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier

        if key == Qt.Key.Key_Control:
            if self.range_selecting_enabled or shift_pressed:
                self.disableMultiSelecting()
                self.disableRangeSelecting()
            else:
                self.enableMultiSelecting()
       
        if key == Qt.Key.Key_Shift:
            if self.range_selecting_enabled or ctrl_pressed:
                self.disableMultiSelecting()
                self.disableRangeSelecting()
            else:
                self.enableRangeSelecting()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key = event.key()

        ctrl_pressed = QGuiApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier
        shift_pressed = QGuiApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier


        if key == Qt.Key.Key_Control:
            self.disableMultiSelecting()
            if shift_pressed:
                self.enableRangeSelecting()
            else:
            
                self.disableRangeSelecting()
       
        if key == Qt.Key.Key_Shift:
            self.disableRangeSelecting()
            if ctrl_pressed:
                self.enableMultiSelecting()
            else:
            
                self.disableMultiSelecting()
        

        super().keyReleaseEvent(event)


    ###BUTTON EVENT   =====================================================================================

    ##Navigation Bar -----------------------
    def whenButtonOpenPathCliked(self):
        self.goInPath(self.input_path.text())
        self.showPathContent()

    def whenButtonGoBackCliked(self):
 
        self.explorer.goBackPath()
        self.showPathContent()

    def whenButtonRefreshCliked(self):
        self.refreshPathContent()

    ##Tool Bar ----------------------------
    def whenButtoNewFolderClicked(self):
        self.action_group_file_type.actions()[1].setChecked(True)
        self.whenFileTypeActionSelected(self.action_group_file_type.actions()[1])#Optimise
        self.createItem()

    def whenButtoNewFileClicked(self):
#        if self.combo_type_new.currentIndex == 1:self.combo_type_new.setCurrentIndex(0) #Select File Type
        self.createItem()

    def whenButtonCopyClicked(self):
        self.copySelected()

    def whenButtonCutClicked(self):
        self.cutSelected()

    def whenButtonPasteClicked(self):
        self.pasteCopied()
    
    def whenButtonDeleteClicked(self):
        self.deleteSelected()

    def whenFileTypeActionSelected(self, action):
        self.combo_type_new.setText(action.text() + "  ▼")


    ##Detail Zone

    def whenButtonRenamePressed(self):
        # Info : MultiRenaming is possible but not accesible yet
        try:
            self.explorer.renameSelected(self.entry_detail_object_name.text())
            self.raiseMessage(f"Succesfully rename {len(self.explorer.getSelectedItems())} item to : {self.entry_detail_object_name.text()}")
            self.explorer.actualisePathContent()
            self.showPathContent()
            
        except Exception as e:
            self.raiseError(e)
    
    def whenOpenTerminalButtonCliked(self):
        items_selected = self.explorer.getSelectedItems()
        if len(items_selected) == 0:
            self.openTerminal(self.explorer.current_path)

        elif len(items_selected) == 1 and items_selected[0].type == "DIR":
            self.openTerminal(items_selected[0].path)

    def whenButtonCopyPathPressed(self):
        items_selected = self.explorer.getSelectedItems()

        if len(items_selected) == 0:
            pyperclip.copy(self.explorer.current_path)
            self.raiseMessage(f"Path copied ! : {self.explorer.current_path}")


        elif len(items_selected) == 1:
            pyperclip.copy(items_selected[0].path)

            self.raiseMessage(f"Path copied ! : {items_selected[0].path}")

    #Files ItemObject
    def whenObjectItemWidgetClicked(self, widget):
        start_dragging = False
        if widget.object.selected :
          
            if len(self.explorer.getSelectedItems())  > 1:
                if self.multi_selecting_enabled:
                    widget.unselect()
                else:
                    self.unselectAll()
                    widget.select()
                   
                    
            else:

                widget.unselect()
        else:
            if not self.multi_selecting_enabled:
                
                if self.range_selecting_enabled:
                    widget.select()
                    self.rangeSelect()
                  
                else:
                    self.unselectAll()
            widget.select()
          

        count = len(self.explorer.getSelectedItems())
        
        self.refresh_window()
        self.refreshInfo()
        self.refreshDetail()
       
        if count  >0:
            self.raiseMessage(f"Selected {count} items", self.theme.current_theme['msgInfo'], 1000)
            start_dragging = True

        if start_dragging: self.startDragObject()

    def whenObjectItemWidgetRightClicked(self, widget):
        if widget.object.type == "DIR": 
            self.goInPath(widget.object.path)
        else:
            self.openPath(widget.object.path)
        
    def whenFilesFrameClicked(self):
       self.unselectAll()

    def show_menu(self):
        
        self.menu_files_type.exec(self.combo_type_new.mapToGlobal(self.combo_type_new.rect().bottomLeft()))
    #Favorits Object

    # def whenFavItemWidgetClicked(self, widget):
    #     if widget.object.selected:
    #         widget.unselect()
    #     else:
    #         widget.select()

    #     self.refresh_window()
    
    def whenFavItemWidgetRightClicked(self, widget):

        if widget.object.type == "DIR" or  widget.object.type == "DISK": 
            self.goInPath(widget.object.path)
        else:
            self.openPath(widget.object.path)

    ###EXLORER FUNCTION    =====================================================================================
    def goInPath(self, path):
        old_path = self.explorer.current_path
        try:
           
            self.explorer.goInPath(path)
            self.showPathContent()
        except Exception as e:
              self.raiseError(e)

              self.explorer.changeCurrenPath(old_path)

    def openPath(self, path):
        if self.explorer.getPathType(path)=="DIR":
            self.goInPath(path)
        else:
            try:
                self.raiseMessage(f"Opening {path}...", self.theme.current_theme['msgInfo'],1000)
                self.explorer.open(path)
            except Exception as e:
                 self.raiseError(e)

    def createItem(self):
        try:
            name = self.input_new_item.text()
            name_ok, error_reason = self.explorer.isValideName(name)
            if not  name_ok: 
                self.raiseError("Not a valide Name : "+ str(error_reason))
            
                return
        
           
            #if  self.combo_type_new.currentData() == "folder":
            if self.getSelectedAction().data() == "folder":
                self.explorer.createFolder(name)

            elif self.getSelectedAction().data() == "template":
                self.explorer.create_template(name,self.getSelectedAction().text())
            
            else:
                extension = ""
                if self.getSelectedAction().data()!="file":
                    extension =  "." + self.explorer.getFileTypeWithIndex(self.getSelectedAction().data()).lower()

                    self.explorer.addUsingToFileType(self.getSelectedAction().data())
                    self.generateFilesTypeToComboList()
                else:#File type custom seted so create it
                    custom_ext_chosen = name.split(".")
                    if len(custom_ext_chosen) >= 2:#No extension
                        custom_ext_chosen = custom_ext_chosen[-1]

                        self.explorer.addUsingToFileType(custom_ext_chosen.lower())
                        self.generateFilesTypeToComboList()
        
            

                name += extension
                self.explorer.createFile(name)

            self.refreshPathContent(select_new_item=True)
            self.input_new_item.setText("")
            self.raiseMessage("Item succesfully created : "+name)
        except Exception as e:
            self.raiseError(e)
            traceback.print_exc()
          
    def copySelected(self):
        if len(self.explorer.getSelectedItems()) == 0:
            self.raiseError("No Item Selected")
            return
        
        try:
            
            self.explorer.copySelectedItems()
            self.explorer.disableCutMode()
            self.raiseMessage(f"Copied {len(self.explorer.getCopiedItems())} items")
            self.refreshInfo()
        except Exception as e:
            self.raiseError(e)
            traceback.print_exc()

    def cutSelected(self):
        self.cutModeEnabled = True
        if len(self.explorer.getSelectedItems()) == 0:
            self.raiseError("No Item Selected")
            return
        
        try:
            self.explorer.copySelectedItems()
            self.explorer.enableCutMode()
            self.raiseMessage(f"Copied {len(self.explorer.getCopiedItems())} items. It will be removed when pasted")
            self.refreshInfo()
        except Exception as e:
            self.raiseError(e)
            traceback.print_exc()

    def pasteCopied(self):
        if len(self.explorer.getCopiedItems()) == 0:
            self.raiseError("No Item Copied")
            return
        
        try:
            count = len(self.explorer.getCopiedItems())
            self.explorer.pasteItems(self.explorer.current_path)
            self.refreshPathContent(select_new_item=True)
            self.explorer.disableCutMode()
            self.raiseMessage(f"Pasted {count} items")
        except Exception as e:
            self.raiseError(e)

    def deleteSelected(self):
        try:
            count = len(self.explorer.getSelectedItems())
         
            self.explorer.deleteSelectedItems()
            
            self.raiseMessage(f"Deleted {count} items")
            log(f"Deleted {count} items", "W")
            self.refreshPathContent()
        except Exception as e:
            self.raiseError(e)

    def unselectAll(self):
        for object in self.list_wiget_object_item:
            object.unselect()

        self.refresh_window()
        self.refreshInfo()
    
    def rangeSelect(self):
        #print("RangeSelect")
        selected_object = self.getSelectedObject()
 
        
        #if len(selected_object) == 1:return

        min_index = -1
        max_index = -1
        for index, ob in enumerate(self.list_wiget_object_item):
            if ob.object.selected and (min_index ==-1 or index < min_index):
                min_index = index
            if ob.object.selected and (max_index  ==-1  or index > max_index):
                max_index = index
        #print(min_index, max_index)
        for index, ob in enumerate(self.list_wiget_object_item):
            if index >= min_index and  index <= max_index:
                #print("Minux",index, min_index)
                ob.select()
   
    def enableMultiSelecting(self):
        self.multi_selecting_enabled = True
        self.keyLabelWrite("● Multi Selecting")

    def disableMultiSelecting(self):
        self.multi_selecting_enabled = False
        self.keyLabelWrite("")

    def enableRangeSelecting(self):
        self.range_selecting_enabled = True
        self.keyLabelWrite("● Range Selecting")

    def disableRangeSelecting(self):
        self.range_selecting_enabled = False
        self.keyLabelWrite("")
    
    def openTerminal(self, location):
       

        try:
            if self.explorer.os == "Windows":
                subprocess.Popen(f'start cmd', cwd=location, shell=True)
            else:#Linux Gnom
                subprocess.Popen(["gnome-terminal"], cwd=location)
        except Exception as e:
            self.raiseError(f"Can't open a termianl : {e}")


    #Heavy -> Less utilisation
    def getSelectedObject(self):
        return [o for o in self.list_wiget_object_item if o.object.selected]

    def playMedia(self):
        self.media_player.stop()
        self.media_player.play()

    #INTERFACE FUNCTION =====================================================================================

    def startDragObject(self):
         #Change the sensibility in main.py

        selected_items = self.explorer.getSelectedItems()

        #---------------------
        drag = QDrag(self)
        pixmap = QFileIconProvider().icon(QFileInfo(selected_items[0].path))

        pixmap = pixmap.pixmap(30, 30) #Size of icon
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center()) 

        mime_data = QMimeData()

       

        mime_data.setUrls([QUrl.fromLocalFile(object.path) for object in selected_items])  
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)
        #---------------------


    def refresh_window(self):
        apply_stylesheet(self)

    def refreshPathContent(self,select_new_item=False):
        try:
            self.explorer.actualisePathContent(select_new_item)
            self.showPathContent()
        except Exception as e:
            self.raiseError(e)

    def refreshInfo(self):
        info = self.explorer.getInfoOfPathContent()
        string = f"""|   {str(len(self.explorer.path_content))} Items : {str(info[0]) + " Folder" if info[0] > 0 else ""} {str(info[1]) + " Files (" + formatSize(info[2]) + ")" if info[1] > 0 else ""}   |"""
        len_selected = len(self.explorer.getSelectedItems())
        if len_selected > 0:
            info_selected = self.explorer.getInfoOfSelectedItem()
            string+= f"""   {len_selected} Items Selected : {str(info_selected[0]) + " Folder" if info_selected[0] > 0 else ""} {str(info_selected[1]) + " Files (" + formatSize(info_selected[2]) + ")" if info_selected[1] > 0 else ""}   |"""
        len_copied = len(self.explorer.getCopiedItems())
        if len_copied > 0:
            info_copied = self.explorer.getInfoOfCopiedItem()
            string+= f"""   {len_copied} Items {"Cuted" if self.explorer.cutModeEnabled else "Copied"} : {str(info_copied[0]) + " Folder" if info_copied[0] > 0 else ""} {str(info_copied[1]) + " Files (" + formatSize(info_copied[2]) + ")" if info_copied[1] > 0 else ""}   |"""
        self.label_info.setText(string)

    def refreshDetail(self):
        max_len = 20
        def format_detail_value(id, value):
            if len(value)>max_len:value = value[:max_len] + "..."
            return f"""<tr ><td align="left"  style="padding-bottom: 10px;"><b>{id} :</b></td><td align="right" >{value}</td></tr>"""

        items_selected = self.explorer.getSelectedItems()
        if len(items_selected) == 1:
            object = items_selected[0]
            self.frame_detail.show()
            self.entry_detail_object_name.setText(object.name)
            str_detail = """<table width="100%" style="font-size:13px; border-spacing: 0; border-collapse: separate;  ">"""
            
            if object.type != "DIR":
                self.button_open_terminal.hide()
                str_detail += format_detail_value("Size", formatSize(object.size))
                str_detail += format_detail_value("Type",f"{object.ext.upper()} - {self.explorer.getExtDescription(object.ext)}")

                file_class = self.explorer.getExtClass(object.ext)
                if file_class == "image":
                    width, height = self.explorer.getImageInfo(object.path)
                    str_detail += format_detail_value("Dimension", f"{width}x{height}, {round(( width* height)/1000000, 2)} MP")
                if file_class == "audio":
                    self.frame_media.show()
                    self.media_player.setSource(QUrl.fromLocalFile(object.path))
                   
                    duration_seconds, author, title, album = self.explorer.getAudioInfo(object.path)
                    str_detail += format_detail_value("Duration", f"{time.strftime('%M:%S', time.gmtime(duration_seconds))}")
                    str_detail += format_detail_value("Author", f"{author}")
                    str_detail += format_detail_value("Title", f"{title}")
                    str_detail += format_detail_value("Album", f"{album}")
                else:
                    self.frame_media.hide()
                



            else:
                self.frame_media.hide()
                self.button_open_terminal.show()
                str_detail += format_detail_value("Type","FOLDER")

            str_detail += format_detail_value("Created on",time.ctime(object.creation_date))
            str_detail += format_detail_value("Modified on",time.ctime(object.modification_date))
            str_detail += format_detail_value("Path ",object.path)
           
            self.label_detail.setText(str_detail + "</table>")
        elif len(items_selected) == 0:
            self.frame_media.hide()
            self.frame_detail.show()
            name = self.explorer.getNameOfPathContentDirectory()
            if name != "":
                self.entry_detail_object_name.setText(self.explorer.getNameOfPathContentDirectory())
            else:
                self.frame_detail.hide()
        else:
          
            self.frame_detail.hide()


    def raiseError(self, message):
        log(message, "E")# Good ideo ? or place for specific situation
        sound.play_error_sound()
        self.message_label.setStyleSheet(f"color: {self.theme.current_theme['msgError']};")
        self.message_label.setText(str(message))
        if self.message_timer.isActive():
            self.message_timer.stop()
        self.message_timer.start(3000)

    def raiseMessage(self, message, color =None, time = 3000):
            if not color: color = f"{self.theme.current_theme['msgSuccess']}"
            self.message_label.setStyleSheet(f"color: {color};")
            self.message_label.setText(message)
            if self.message_timer.isActive():
                self.message_timer.stop()
            self.message_timer.start(time)

    def clearMessage(self):
        self.message_label.setText("")

    def keyLabelWrite(self, message):
        
        self.label_key.setStyleSheet(f"color: {self.theme.current_theme['msgSuccess']};")
        self.label_key.setText(message)


    def clearWidgetList(self, list):

        #Old Version :
        # layout = self.files_container_layout
        # children = []
        # for i in range(layout.count()):
        #     child = layout.itemAt(i).widget()
        #     if child:
        #         children.append(child)
        # for child in children:
        #      child.deleteLater()
        for w in list:
              w.deleteLater()
        list.clear()
        
    def showPathContent(self):
        try:
            self.refreshInfo()
            self.refreshDetail()
            self.clearWidgetList(self.list_wiget_object_item)
            self.input_path.setText(self.explorer.current_path)

            self.file_list = self.explorer.getPathContent()
            self.current_index = 0

            self._loadNextFile()
            self.scroll_area.setWidget(self.files_container)

        except Exception as e:
            self.raiseError(e)

    def _loadNextFile(self):
        if self.current_index >= len(self.file_list):
            
            return

        ob = self.file_list[self.current_index]
        self.current_index += 1
        #Object Generation ----------------------------------------------------------
        widget = NormalObjectItemWidget()
        widget.generateView(ob,  self.show_file_icon)
        widget.clicked.connect(lambda w=widget: self.whenObjectItemWidgetClicked(w))
        widget.right_clicked.connect(lambda w=widget: self.whenObjectItemWidgetRightClicked(w))
        if ob.selected:
            widget.select()
        #-----------------------------------------------------------------

        self.list_wiget_object_item.append(widget)
        self.files_container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        self.files_container_layout.setSpacing(0)
        


       
        QTimer.singleShot(0, self._loadNextFile)

    def generateFavorits(self):
        try:
            self.clearWidgetList(self.list_fav_widget)
            fav_objects = []
            try:
                fav_objects += self.explorer.getFavObjectList()
            except Exception as e:
                log(f"Error during loading favorit : {e}", "E")

            try:
                fav_objects += self.explorer.getListObjectDrive()
            except Exception as e:
                log(f"Error during loading drive list : {e}", "E")
            for  ob in fav_objects:
                if ob.type == "DISK":widget = FavoriteDriveItemWidget()
                else:widget = FavoriteObjectItemWidget()
                widget.generateView(ob)
                #widget.clicked.connect(lambda w=widget: self.whenFavItemWidgetClicked(w))
                widget.right_clicked.connect(lambda w=widget: self.whenFavItemWidgetRightClicked(w))
                if ob.selected:widget.select()

                self.list_fav_widget.append(widget)
                self.frame_list_fav_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)


            self.scroll_area_fav.setWidget(self.frame_list_fav)
        except Exception as e:
            self.raiseError(e)
       
    #Slow
    def applyBlurBackrounWindows(self):
        import ctypes
        import sys
        class ACCENTPOLICY(ctypes.Structure):
            _fields_ = [
                ('AccentState', ctypes.c_int),
                ('AccentFlags', ctypes.c_int),
                ('GradientColor', ctypes.c_int),
                ('AnimationId', ctypes.c_int)
            ]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ('Attribute', ctypes.c_int),
                ('Data', ctypes.c_void_p),
                ('SizeOfData', ctypes.c_size_t)
            ]

        # Valeurs constantes
        ACCENT_ENABLE_BLURBEHIND = 3#6
        WCA_ACCENT_POLICY = 19

        accent = ACCENTPOLICY()
        accent.AccentState = ACCENT_ENABLE_BLURBEHIND
        accent.GradientColor = 0xAAFFFFFF   # Alpha = 0x99 #CHANGE NOTHING

        data = WINCOMPATTRDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
        data.SizeOfData = ctypes.sizeof(accent)

        hwnd = int(self.winId())
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))


    def applyBlurBackroundCustom(widget, blur_radius: float = 15):
        log(f"Applying blur background, force = {blur_radius}...")

        def blur_pixmap(pixmap: QPixmap, radius: float) -> QPixmap:
            item = QGraphicsPixmapItem(pixmap)
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(radius)
            item.setGraphicsEffect(blur)

            scene = QGraphicsScene()
            scene.addItem(item)

            result = QPixmap(pixmap.size())
            result.fill(Qt.transparent)

            painter = QPainter(result)
            scene.render(
                painter,
                QRectF(0, 0, pixmap.width(), pixmap.height()),
                QRectF(0, 0, pixmap.width(), pixmap.height())
            )
            painter.end()
            return result

        # Charger le fond d’écran
        path = widget.explorer.getWallpaper()
        if not path:
            raise Exception("Cannot find desktop wallpaper")

        log(f"Background found in : {path}")
        wallpaper = QPixmap(path)

        # Flouter AVANT de redimensionner
        blurred_wallpaper = blur_pixmap(wallpaper, blur_radius)

        # Ensuite on scale le fond flouté
        screen_geom = QGuiApplication.primaryScreen().geometry()
        scaled_wallpaper = blurred_wallpaper.scaled(
            screen_geom.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        # Fonction de dessin sur le widget
        def paintEvent(event):
            painter = QPainter(widget)
            pos = widget.mapToGlobal(widget.rect().topLeft())
            cropped = scaled_wallpaper.copy(pos.x(), pos.y(), widget.width(), widget.height())
            painter.drawPixmap(0, 0, cropped)

        def moveEvent(event):
            widget.update()

        # Injection dynamique
        widget.paintEvent = paintEvent
        widget.moveEvent = moveEvent
        
# def showPathContent(self):
#         try:
#             self.refreshInfo()
#             self.clearWidgetList(self.list_wiget_object_item)
#             self.input_path.setText(self.explorer.current_path)
#             for  ob in self.explorer.getPathContent():

#                 widget = NormalObjectItemWidget()
#                 widget.generateView(ob, self.explorer.getObjectIcon(ob))
#                 widget.clicked.connect(lambda w=widget: self.whenObjectItemWidgetClicked(w))
#                 widget.right_clicked.connect(lambda w=widget: self.whenObjectItemWidgetRightClicked(w))
#                 if ob.selected:widget.select()

#                 self.list_wiget_object_item.append(widget)
#                 self.files_container_layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)



#             self.scroll_area.setWidget(self.files_container)
#         except Exception as e:
#             self.raiseError(e)
