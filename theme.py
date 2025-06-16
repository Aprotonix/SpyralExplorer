import os
import json
from log import log

THEMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")

class Theme():
    def __init__(self):
        self.template_theme = {}
        self.current_theme = {}
        self.initDefaultTheme()

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        

    def initDefaultTheme(self):
        self.template_theme = {
            

            "windowBG":"#232323",
            "textColor":"#FFF",
            "globalBorderRadius":"15px",

            "msgError":"#FF0000",
            "msgSuccess":"#00FF37",
            "msgInfo":"#00D9FF",

            "topWidgetButtonBG": "#3c3c3c",
            "topWidgetButtonBorder": "#555",
            "topWidgetButtonHoverBG": "#656565",
            "topWidgetButtonHoverBorder": "#555",

            "topWidgetInputBG": "#3c3c3c",
            "topWidgetInputBorder": "#555",
            "topWidgetInputHoverBG": "#656565",
            "topWidgetInputHoverBorder": "#555",

            "toolWidgetButtonBG": "#3c3c3c",
            "toolWidgetButtonBorder": "#555",
            "toolWidgetButtonHoverBG": "#656565",
            "toolWidgetButtonHoverBorder": "#555",

            "toolWidgetInputBG": "#3c3c3c",
            "toolWidgetInputBorder": "#555",
            "toolWidgetInputHoverBG": "#656565",
            "toolWidgetInputHoverBorder": "#555",

            "ObjItemWidgetBG": "#3c3c3c",
            "ObjItemWidgetBorder": "#555",
            "ObjItemWidgetHoverBG": "#656565",
            "ObjItemWidgetHoverBorder": "#555",

            "ObjItemWidgetSelectedBG": "#007aa8",
            "ObjItemWidgetSelectedBorder": "#3ec2ff",
            "ObjItemWidgetSelectedHoverBG": "#0093ca",
            "ObjItemWidgetSelectedHoverBorder": "#3ec2ff"
        }


    def applyThemeToStyle(self):
        with open(os.path.join( self.base_path,"style_template.qss"), "r")  as f:
            style_text = f.read()
  
        for key, value in self.current_theme.items():
            style_text = style_text.replace("@" + key, value)


        with open(os.path.join( self.base_path,"style.qss"), "w")  as f:
            f.write(style_text)

    def getThemesListName(self):
        list_theme = os.listdir(THEMES_PATH)
        list = []
        for theme_path in list_theme:
            with open(os.path.join(THEMES_PATH, theme_path), 'r', encoding='utf-8') as f:
               theme_json =  json.load(f)  # Retourne une liste de dictionnaires

            list.append(theme_json["name"])

        return list
    
    def setTheme(self, theme_index):
        list_theme = os.listdir(THEMES_PATH)
        with open(os.path.join(THEMES_PATH, list_theme[theme_index]), 'r', encoding='utf-8') as f:
            self.current_theme = self.template_theme.copy()
            for key, value in  json.load(f).items():
                self.current_theme[key] = value

        log("Current Theme set : "+self.current_theme["name"])


       

# theme = Theme()
# print(theme.getThemesListName())
# theme.setTheme(1)
# theme.applyThemeToStyle()