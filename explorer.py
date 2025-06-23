from log import log

import os
import json              # For Json data
import shutil            # For folder action
from pathlib import Path # To test subdirectory
import psutil            # Get list of drive
import platform          # Get OS Name
import ctypes            # Get drive name for windows, and wallpaper
import pyperclip
import subprocess        #Get linux desktop wallpaper
import sys               #Open file with linux
from PIL import Image    #Get Image Info
from mutagen import File #Get Audio Info

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.join(BASE_PATH,"templates")
FAV_LIST_PATH = os.path.join(BASE_PATH,"fav_list.txt")
FILES_TYPES_PATH = os.path.join(BASE_PATH,"filestypes.json")
ICONS_PATH = os.path.join(BASE_PATH,"icons")
CACHE_PATH = os.path.join(BASE_PATH,"cache")
TEXT_ICONS_PATH = os.path.join(BASE_PATH,"text_icons.json")

##TO Do

#Clean linux wallpaper getting
#transform filestypes.json in a dict
class Object:
    def __init__(self,path,type):

        self.type = type
        self.path = path
        self.name = os.path.basename(path)
        self.creation_date =  os.path.getctime(path)
        self.modification_date = os.path.getmtime(path)
        if self.name == "":self.name = path
        self.selected = False

        if type != "DIR":
            self.size =  os.path.getsize(path)
            self.ext = os.path.splitext(self.name)[1][1:].lower()

    def __str__(self):
        return f"TYPE : {self.type}\nPATH : {self.path}"
    
class DiskObject(Object):
    def __init__(self, sdiskpart, name):
        super().__init__(sdiskpart.mountpoint, "DISK")
        self.name = name + f" ({self.path})"
        self.file_system_type =  sdiskpart.fstype
        self.usage =  psutil.disk_usage(sdiskpart.mountpoint)

class Explorer():
    def __init__(self):
        self.current_path = "D:\\"#Path where whe are
        self.path_content = []  #Object in the path
        self.files_types = []
        self.paths_copied = []

        self.os = platform.system()


        #self.base_path = os.path.dirname(os.path.abspath(__file__))

        self.last_created_items_path = []

        self.cutModeEnabled = False
        self.load_file_types_json()

        self.order_method = self.orderPathContentByType

    def getObject(self, path):

        return Object(path, self.getPathType(path))
        
    def actualisePathContent(self, select_new_item= False):
        try:
            self.path_content.clear()

            for ob in os.listdir(self.current_path):
                path = os.path.join(self.current_path, ob)
                self.path_content.append(self.getObject(path))
               
                if select_new_item and self.path_content[-1].path in self.last_created_items_path :
                  
                    self.path_content[-1].selected = True

            self.order_method()

        except Exception as e:
            raise e


    def open(self, path):
        if self.os == "Windows":
            os.startfile(path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])

    def goInPath(self, path):
        self.changeCurrenPath(path)
        self.actualisePathContent()

    def orderPathContentByType(self):
        folders = []
        files = []
        for ob in self.path_content:
            if ob.type == "DIR":
                folders.append(ob)
            else:
                files.append(ob)

        self.path_content = folders + files

    def getPathContent(self):
        """Return the files and dir list from a path"""
        return self.path_content
        
    def changeCurrenPath(self, new_path):
        self.current_path = new_path

    def goBackPath(self):
        self.changeCurrenPath(os.path.dirname(self.current_path))
        self.actualisePathContent()

    def getPathType(self, path):
        if os.path.isdir(path):
            return "DIR"
        elif os.path.isfile(path):
            return "FILE"
        else:
            return "UNKNOW"

      
    #  FILE CREATION ==========================================================
    def isValideName(self, name):
            # Check if the name is empty or only contains whitespace
        if not name or name.strip() == "":
            return False, "The name is empty or contains only whitespace."

        # Forbidden characters on Windows
        forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\n', '\r', '\t']
        for char in name:
            if char in forbidden_chars:
                return False, f"The name contains a forbidden character: '{char}'"

        # Reserved names on Windows
        reserved_names = [
            "CON", "PRN", "AUX", "NUL",
            *(f"COM{i}" for i in range(1, 10)),
            *(f"LPT{i}" for i in range(1, 10))
        ]
        name_upper = name.split('.')[0].upper()  # Name without extension
        if name_upper in reserved_names:
            return False, f"The name '{name_upper}' is a reserved system name."

        # Max length
        if len(name) > 255:
            return False, "The name is too long (maximum 255 characters)."

        return True, None
    
    def createFolder(self, name):
       

        if not self.isValideName(name):raise Exception("Not Valide Folder Name")
        folder_path = os.path.join(self.current_path, name)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            self.last_created_items_path.clear()
            self.last_created_items_path = [folder_path]
        else:raise Exception("Folder Already Exist")

    def createFile(self, name):

        if not self.isValideName(name):
            raise Exception("Not Valide File Name")
        file_path = os.path.join(self.current_path, name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")
            self.last_created_items_path.clear()
            self.last_created_items_path = [file_path]
        else:raise Exception("File Already Exist")


    def addUsingToFileType(self, index_type): # Count the most used extension

        if type(index_type) == int :
            self.files_types[index_type]["using"]+=1
            self.save_file_types_json()

        else:#Not optimized
            for index, ftype in enumerate(self.files_types):
                #print(ftype)
                if ftype["type"] == index_type:
                    self.files_types[index]["using"]+=1
                    return #Break the loop
            #File type not exist and create it
            self.files_types.append({"type":index_type, "description": "", "using":1})
            self.save_file_types_json()

    def save_file_types_json(self):
        with open(FILES_TYPES_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.files_types, f, indent=4)

    def getFileTypeWithIndex(self, index_type):
        return  self.files_types[index_type]["type"]
    
    def getExtDescription(self, ext):
        for e in self.files_types:
            if e["type"] == ext:
                return e["description"]
        return "File"
   
    def getExtClass(self,ext):
        for e in self.files_types:
            if e["type"] == ext:
                return e.get("class", None)
       
    def getImageInfo(self, path):
        image = Image.open(path)
        width, height = image.size
        return width, height
    
    def getAudioInfo(self, path):
  
       
        


        try:
            audio = File(path, easy=True)
            if audio is None:
                return None, None, None, None

            author = audio.get("artist", ["Inconnu"])[0]
            title = audio.get("title", ["Inconnu"])[0]
            album = audio.get("album", ["Inconnu"])[0]
            duration_seconds = audio.info.length

            return duration_seconds, author, title, album

        except Exception as e:
           
            return None, None, None, None

        return duration_seconds
    
    def load_file_types_json(self):
        with open(FILES_TYPES_PATH, 'r', encoding='utf-8') as f:
            self.files_types =  json.load(f)  # Retourne une liste de dictionnaires

    # Templates ------------------------------------------
    def get_templates_list(self):
        return os.listdir(TEMPLATES_PATH)

    def create_template(self, name, selected_template_name):
        self.last_created_items_path.clear()
        destination_path = self.current_path
        template_name = self.renameIfExist(os.path.join(destination_path, name), destination_path)#WARN :if cut and paste in the same folder it will still rename it : file_name(1).ext
        dest = os.path.join(destination_path, template_name)
        
        shutil.copytree(os.path.join(TEMPLATES_PATH, selected_template_name) , dest, dirs_exist_ok=True)  # Pour dossiers                         
        self.last_created_items_path.append(dest)

    # FILES ACTION ============================================================

    # Error prevention -------------------------------------------------------
    def renameIfExist(self, path, dest):
        base_name = os.path.basename(path)
        name, ext = os.path.splitext(base_name)
        candidate = base_name
        index = 1

        # Boucle tant qu'un fichier/dossier avec ce nom existe
        while os.path.exists(os.path.join(dest, candidate)):
            if ext:
                candidate = f"{name} - copy ({index}){ext}"
            else:
                candidate = f"{name} - copy ({index})"
            index += 1

        return candidate

    def isSubdirectory(self, child_path, parent_path):
        child = Path(child_path).resolve()
        parent = Path(parent_path).resolve()
        return parent in child.parents
    # ------------------------------------------------------------------------
    def getSelectedItems(self):# Well Optimized
        return [f for f in self.path_content if f.selected]
    
    def getCopiedItems(self):# Well Optimized
        return [p for p in self.paths_copied]
    
    def enableCutMode(self):
        self.cutModeEnabled = True

    def disableCutMode(self):
        self.cutModeEnabled = False

    def copySelectedItems(self):
        selected = self.getSelectedItems()
        self.paths_copied.clear()
        for s in selected:
            pyperclip.copy(s.path)
            self.paths_copied.append(s.path)

    def pasteItems(self, destination_path):
        self.last_created_items_path.clear()
        for path in self.paths_copied:
            name = self.renameIfExist(path, destination_path)#WARN :if cut and paste in the same folder it will still rename it : file_name(1).ext
            dest = os.path.join(destination_path, name)
            self.last_created_items_path.append(dest)


            if os.path.isdir(path):
                shutil.copytree(path, dest, dirs_exist_ok=True)  # Pour dossiers                         
                if self.cutModeEnabled :
                    if not self.isSubdirectory(dest, path):
                        shutil.rmtree(path)
                    else: raise Exception("Impossible to delete : Destination directory is subdirectory of source directory")
                
            else:
                shutil.copy2(path, dest)
                if self.cutModeEnabled:os.remove(path)

        if self.cutModeEnabled :self.paths_copied.clear()

    def deleteSelectedItems(self):
        selected = self.getSelectedItems()
        for s in selected:
            path = s.path
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
                
    def renameSelected(self, new_name):
        is_valide_name, err = self.isValideName(new_name)
        if not is_valide_name:raise(Exception(err))

        selected_items = self.getSelectedItems()
        if selected_items == []:
            parent = self.getNameOfPathContentDirectory()
            if parent == "":
                raise(Exception("Can't rename parent : Name is Void"))
            selected_items.append(parent)

        for i in selected_items:
            if i.name == new_name:continue
            print(i.path, os.path.join(self.current_path, self.renameIfExist(os.path.join(self.current_path, new_name), self.current_path)))
            os.rename(i.path, os.path.join(self.current_path, self.renameIfExist(os.path.join(self.current_path, new_name), self.current_path)))

   
   #FILES INFO =============================================================
    def getInfoOfPathContent(self):
        size = 0
        file_count = 0
        folder_count = 0
        for f in self.path_content:
            if f.type != "DIR":
                file_count+=1
                size+=f.size
            else:
                folder_count+=1

        return folder_count,file_count, size
    
    def getNameOfPathContentDirectory(self):
        return os.path.basename(self.current_path)

    def getInfoOfSelectedItem(self):
        size = 0
        file_count = 0
        folder_count = 0
        for f in self.getSelectedItems():
            if f.type != "DIR":
                file_count+=1
                size+=f.size
            else:
                folder_count+=1

        return folder_count,file_count, size
    
    def getInfoOfCopiedItem(self):
        size = 0
        file_count = 0
        folder_count = 0
        for path in self.getCopiedItems():
            if not os.path.isdir(path):
                file_count+=1
                size+=os.path.getsize(path)
            else:
                folder_count+=1

        return folder_count,file_count, size
   


    #FAV GESTION ============================================================

    def getListObjectDrive(self):
        if self.os == "Windows":
            drives = self.Windows_getVolumeList()
        else:
            drives = self.Linux_getVolumeList()
        drives_object_list = []
        for drive, name in drives:
            try:
                drives_object_list.append(DiskObject(drive, name))
            except Exception as e:
                log(f"Error during to get drive [{drive}] [{name}]", "E")

        return drives_object_list
    
    def Linux_getVolumeList(self):
        volumes = []
        for p in psutil.disk_partitions(all=False):
            if "/media/" in p.mountpoint or "/run/media/" in p.mountpoint:
                label = os.path.basename(p.mountpoint)
            else:
                label = "Volume"
            volumes.append([p, label])  # Ex: "MyUSB (/media/user/MyUSB)"
        return volumes
    
    def Windows_getVolumeList(self):
        volumes = []
        for p in psutil.disk_partitions(all=False):
            buf = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(p.mountpoint), buf, ctypes.sizeof(buf),
                None, None, None, None, 0
            ):
                label = buf.value
            else:
                label = "Sans nom"
            
            volumes.append([p, label])  # Ex: "Clé USB (D:)"
        return volumes

    def getFavObjectList(self):
        list = []
        with open(FAV_LIST_PATH, "r") as f:
            fav_list = f.read()

        fav_list = eval(fav_list)

        for ob_path in fav_list:
            try:
                list.append(self.getObject(ob_path))
            except Exception as e:
                log(f"Error during loading favorit [{ob_path}] : {e}", "E")

        return list

#     #Unused ==========================
    def getIconPath(self, icon_name):
        return os.path.join(BASE_PATH, ICONS_PATH, icon_name + ".svg")

    def getObjectIcon(self, object):
        
        if object.type == "FILE":
            if object.ext == "exe":
                if platform.system() == "Windows":
                    return self.Windows_getExeIcon(object.path, object.name)
            
    #Unused
    def Windows_getExeIcon(self,icon_in_path,icon_name):
        icon_out_path=CACHE_PATH
        out_width = 100
        out_height = 100

        import win32ui
        import win32gui
        import win32con
        import win32api
        from PIL import Image

        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

        large, small = win32gui.ExtractIconEx(icon_in_path,0)
        if large==[]:return
        if small==[]:return
        win32gui.DestroyIcon(small[0])

        hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_x )
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject( hbmp )

        hdc.DrawIcon( (0,0), large[0] )

        bmpstr = hbmp.GetBitmapBits(True)
        icon = Image.frombuffer(
            'RGBA',
            (32,32),
            bmpstr, 'raw', 'BGRA', 0, 1
        )

        full_outpath = os.path.join(icon_out_path, "{}.png".format(icon_name))
        icon.resize((out_width, out_height))
        icon.save(full_outpath)
        #return the final path to the image
        return full_outpath
    
    def getWallpaper(self):
        log("Wallopaper")
        if self.os == "Windows":
            buf = ctypes.create_unicode_buffer(260)
            ctypes.windll.user32.SystemParametersInfoW(0x73, 260, buf, 0)
            return buf.value
        
        elif self.os == "Linux":
            

            def resolve_dynamic_wallpaper(xml_path):
                from xml.etree import ElementTree
                try:
                    tree = ElementTree.parse(xml_path)
                    root = tree.getroot()
                    static_path = None
                    for static in root.findall("static"):
                        file_elem = static.find("file")
                        if file_elem is not None:
                            static_path = file_elem.text
                            break
                    return static_path
                except Exception as e:
                    print("Erreur XML:", e)
                    return None
            def gnome():
                log("If you get an error with GLIBCXX_3.4.29 don't lauche your the program with a snap app (vscode...), use terminal")
                try:
                    # Vérifie si le mode sombre est actif
                    theme_output = subprocess.check_output(
                        ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                        universal_newlines=True
                    ).strip()

                    dark_mode = "dark" in theme_output.lower()

                    # Récupère l'URI du fond d'écran selon le mode
                    schema = "org.gnome.desktop.background"
                    key = "picture-uri-dark" if dark_mode else "picture-uri"

                    uri_output = subprocess.check_output(
                        ["gsettings", "get", schema, key],
                        universal_newlines=True
                    ).strip().strip("'")

                    if uri_output.startswith("file://"):
                        path = uri_output[7:]  # remove file://
                    else:
                        path = uri_output

                    # Vérifie que le fichier existe
                    if os.path.exists(path):
                        return path
                    else:
                        print("Le fichier spécifié n'existe pas :", path)
                        return None

                except Exception as e:
                    print("Erreur lors de la récupération du fond d'écran GNOME :", e)
                    return None
                

            def kde():
                try:
                    config_path = Path.home() / ".config" / "plasmarc"
                    if not config_path.exists():
                        return None
                    with config_path.open() as f:
                        for line in f:
                            if "Image=" in line:
                                return line.strip().split("=", 1)[-1]
                except Exception:
                    pass
                return None

            def xfce():
                try:
                    cmd = ["xfconf-query", "--channel", "xfce4-desktop", "--property", "/backdrop/screen0/monitor0/image-path"]
                    output = subprocess.check_output(cmd).decode().strip()
                    return output
                except Exception:
                    pass
                return None

            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
           
            if "gnome" in desktop_env or "unity" in desktop_env:
                return gnome()
            elif "kde" in desktop_env:
                return kde()
            elif "xfce" in desktop_env:
                return xfce()

with open(TEXT_ICONS_PATH, "r", encoding='utf-8') as f:
    text_icons = json.load(f)

def getTextIcon(object):
    if object.type == "DIR":

        return "📁" 
    else:
        for icon, exts in text_icons.items():
            if object.ext in exts:return icon         
       
        return "📄"
    





    
