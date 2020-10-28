from dogtail import procedural
from dogtail import tree
from dogtail.utils import run


def test_unit_converter():
    """Dogtail integration test: Unit converter plugin behaves as intended."""

    cmd = "gourmet"

    pid = run(cmd, timeout=3)
    gourmet = None

    for app in tree.root.applications():
        if app.get_process_id() == pid:
            gourmet = app
            break

    assert gourmet is not None, "Could not find Gourmet instance!"

    # Open the unit converter plugin
    procedural.keyCombo("<Alt>T")
    procedural.keyCombo("U")
    procedural.focus.window("Unit Converter")

    # Enter source amount and unit (5 liters)
    procedural.keyCombo("<Alt>A")
    procedural.type("5")
    procedural.keyCombo("<Alt>U")
    procedural.keyCombo("<Enter>")
    procedural.click("liter (l)")

    # Enter target unit (ml)
    procedural.keyCombo("<Alt>U")
    procedural.keyCombo("<Enter>")
    procedural.keyCombo("Right")
    for _ in range(7):
        procedural.keyCombo("Down")
    procedural.keyCombo("<Enter>")

    # Check that the result is shown correctly
    assert procedural.focus.widget(name="5 l = 5000 ml", roleName="label")

    # There are now two windows, the unit converter, and main window
    # Close them successively to quit the application
    procedural.keyCombo("<Alt><F4>")
    procedural.keyCombo("<Alt><F4>")


if __name__ == "__main__":
    test_unit_converter()
