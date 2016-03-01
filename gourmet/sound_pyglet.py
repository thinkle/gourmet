import pyglet

class Player:
    def __init__ (self):
	pass

    def play_file (self,path):
        self.player = pyglet.media.Player()
        self.source = pyglet.media.load(path,streaming=False)
        self.player.queue(self.source)
        while not self.player._audio_finished:
            self.player.play()

    def stop_play (self,path):
        pass

if __name__ == '__main__':
    p = Player()
    p.play_file('../data/sound/phone.wav')
    
