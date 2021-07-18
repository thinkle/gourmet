import socket
import urllib.error
import urllib.parse
import urllib.request

import gourmet.threadManager
from gourmet.i18n import _

DEFAULT_SOCKET_TIMEOUT=45.0
URLOPEN_SOCKET_TIMEOUT=15.0

socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)

class URLReader (gourmet.threadManager.SuspendableThread):

    def __init__ (self, url):
        self.url = url
        gourmet.threadManager.SuspendableThread.__init__(
            self,
            name=_('Downloading %s'%url)
            )

    def do_run (self):
        self.read()

    def read (self):
        message = _('Retrieving %s'%self.url)
        socket.setdefaulttimeout(URLOPEN_SOCKET_TIMEOUT)
        sock = urllib.request.urlopen(self.url)
        socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)
        bs = 1024 * 8 # bite size...
        # Get file size so we can update progress correctly...
        self.content_type = None;
        if hasattr(sock,'headers'):
            fs = int(sock.headers.get('content-length',-1)) # file size..
            self.content_type = sock.headers.get('content-type')
            print('CONTENT TYPE = ',self.content_type)
        else:
            fs = -1
        block = sock.read(bs)
        self.data = block
        sofar = bs
        while block:
            if fs>0:
                self.emit('progress',float(sofar)/fs, message)
            else:
                self.emit('progress',-1, message)
            sofar += bs
            block = sock.read(bs)
            self.data += block
        sock.close()
        self.emit('progress',1, message)

def read_socket_w_progress (sock, suspendableThread=None, message=None):
    """Read piecemeal reporting progress via our suspendableThread
    instance (most likely an importer) as we go."""
    if not suspendableThread:
        data = sock.read()
    else:
        bs = 1024 * 8 # bite size...
        if hasattr(sock,'headers'):
            fs = int(sock.headers.get('content-length',-1)) # file size..
        else: fs = -1
        block = sock.read(bs)
        data = block
        sofar = bs
        print("FETCHING:",data)
        while block:
            if fs>0:
                suspendableThread.emit('progress',float(sofar)/fs, message)
            else:
                suspendableThread.emit('progress',-1, message)
            sofar += bs
            block = sock.read(bs)
            data += block
            print("FETCHED:",block)
    sock.close()
    print("FETCHED ",data)
    print("DONE FETCHING")
    suspendableThread.emit('progress',1, message)
    return data

def get_url (url, suspendableThread):
    """Return data from URL, possibly displaying progress."""
    if isinstance(url, str):
        socket.setdefaulttimeout(URLOPEN_SOCKET_TIMEOUT)
        sock = urllib.request.urlopen(url)
        socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)
        return read_socket_w_progress(sock,suspendableThread,_('Retrieving %s'%url))
    else:
        sock = url
        return read_socket_w_progress(sock,suspendableThread,_('Retrieving file'))
