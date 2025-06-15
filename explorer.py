from log import log

import os
import json# For Json data
import shutil#For folder action
from pathlib import Path# To test subdirectory
import psutil# Get list of drive
import platform #Get OS Name
import ctypes# Get drive name for windows

class Object:
    def __init__(self,path,type):

        self.type = type
        self.path = path
        self.name = os.path.basename(path)
        if self.name == "":self.name = path
        self.selected = False

  


        if type != "DIR":self.size =  os.path.getsize(path)

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
        self.current_path = "C:\\"#Path where whe are
        self.path_content = []  #Object in the path
        self.files_types = []
        self.paths_copied = []

        self.os = platform.system()




        self.last_created_items_path = []

        self.cutModeEnabled = False
        self.load_file_types_json()

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

        except Exception as e:
            raise e


    def open(self, path):
        os.startfile(path)

    def goInPath(self, path):
        self.changeCurrenPath(path)
        self.actualisePathContent()

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
                print(ftype)
                if ftype["type"] == index_type:
                    self.files_types[index]["using"]+=1
                    return #Break the loop
            #File type not exist and create it
            self.files_types.append({"type":index_type, "description": "", "using":1})
            self.save_file_types_json()

    def save_file_types_json(self):
        with open("filestypes.json", 'w', encoding='utf-8') as f:
                json.dump(self.files_types, f, indent=4)

    def getFileTypeWithIndex(self, index_type):
        return  self.files_types[index_type]["type"]
          
    def load_file_types_json(self):
        with open("filestypes.json", 'r', encoding='utf-8') as f:
            self.files_types =  json.load(f)  # Retourne une liste de dictionnaires

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
        if platform.system() == "Windows":
            drives = self.getVolumeListWindows()
        else:
            drives = self.getVolumeListLinux()
        drives_object_list = []
        for drive, name in drives:
            try:
                drives_object_list.append(DiskObject(drive, name))
            except Exception as e:
                log(f"Error during to get drive [{drive}] [{name}]", "E")

        return drives_object_list
    
    def getVolumeListLinux(self):
        volumes = []
        for p in psutil.disk_partitions(all=False):
            if "/media/" in p.mountpoint or "/run/media/" in p.mountpoint:
                label = os.path.basename(p.mountpoint)
            else:
                label = "Volume"
            volumes.append([p, label])  # Ex: "MyUSB (/media/user/MyUSB)"
        return volumes
    
    def getVolumeListWindows(self):
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
        with open("fav_list.txt", "r") as f:
            fav_list = f.read()

        fav_list = eval(fav_list)

        for ob_path in fav_list:
            try:
                list.append(self.getObject(ob_path))
            except Exception as e:
                log(f"Error during loading favorit [{ob_path}] : {e}", "E")

        return list




        
    

    



    
