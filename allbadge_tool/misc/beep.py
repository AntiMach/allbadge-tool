import platform

if platform.system() == "Windows":
    import winsound

    def beep():
        winsound.MessageBeep()

elif platform.system() == "Linux":
    import os

    def beep():
        os.system("aplay -q /usr/share/sounds/freedesktop/stereo/complete.oga")

else:

    def beep():
        pass
