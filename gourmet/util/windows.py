import ctypes

# From http://stackoverflow.com/questions/2608200/problems-with-umlauts-in-python-appdata-environvent-variable
def getenv(name):
    name = str(name) # make sure string argument is unicode
    n = ctypes.windll.kernel32.GetEnvironmentVariableW(name, None, 0)
    if n == 0:
        return None
    buf = ctypes.create_unicode_buffer('\0' * n)
    ctypes.windll.kernel32.GetEnvironmentVariableW(name, buf, n)
    return buf.value
