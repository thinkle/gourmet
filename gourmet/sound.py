try:
    from sound_gnome import Player
except ImportError:
    print 'No gnome player'
    try:
        from sound_windows import Player
    except ImportError:
        print 'No windows player'
        import sys
        class Player:
            """Fallback player"""
            def play_file (self,path):
                print 'No player installed -- beeping instead'
                for n in range(5): sys.stdout.write('\a'); sys.stdout.flush()

