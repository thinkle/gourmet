import winsound

class Player:
    def __init__ (self):
        pass

    def play_file (self,path):
        winsound.PlaySound(path,winsound.SND_FILENAME)

    def stop_play (self,path):
        pass
