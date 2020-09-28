import pytest
from gourmet.prefs import Prefs


def test_singleton():
    prefs = Prefs.instance()
    pprefs = Prefs.instance()
    assert prefs == pprefs


def test_get_sets_default():
    """Test that using get with a default value adds it to the dictionnary"""
    prefs = Prefs.instance()

    val = prefs.get('key', 'value')
    assert val == val

    assert prefs['key'] == val  # The value was inserted

    val = prefs.get('anotherkey')
    assert val is None

    with pytest.raises(KeyError):
        prefs['anotherkey']
