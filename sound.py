from playsound import playsound
import platform
import os






def play_error_sound(custom_default=False):
    system = platform.system()

    if system == "Windows" and not custom_default:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONHAND)

    else:
         playsound(os.path.join("sounds", "error.mp3"))#Not work sometime + Improve Sound