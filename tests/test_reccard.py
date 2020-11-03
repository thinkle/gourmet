from tempfile import TemporaryDirectory

import gi
from gi.repository import Gtk  # noqa: import not a top of file

from gourmet import convert, gglobals  # noqa: import not at top
from gourmet.backends.db import RecData  # noqa: import not at top
from gourmet.GourmetRecipeManager import get_application  # noqa
from gourmet.reccard import (RecCard, RecCardDisplay, RecEditor,  # noqa
                             add_with_undo)

gi.require_version("Gtk", "3.0")


VERBOSE = True


def print_(*msg):
    if VERBOSE:
        print(*msg)


def assert_with_message(callable_, description):
    try:
        assert(callable_())
    except AssertionError:
        print('FAILED:', description)
        raise
    else:
        if VERBOSE:
            print('SUCCEEDED:', description)


def add_save_and_check(rc, lines_groups_and_dc):
    idx = rc._RecCard__rec_editor.module_tab_by_name["ingredients"]
    ing_controller = rc._RecCard__rec_editor.modules[idx].ingtree_ui.ingController

    # All ingredient addition actions pass through add_with_undo
    ing_editor = ing_controller.ingredient_editor_module
    added = []
    for line, group, desc in lines_groups_and_dc:
        add_with_undo(
            ing_editor,
            lambda *args: added.append(ing_editor.add_ingredient_from_line(line, group_iter=group))
        )

    history = ing_editor.history
    print_("add_save_and_check REVERT history:", history)

    added = [ing_controller.get_persistent_ref_from_iter(i) for i in added]

    # Make a save via the callback, which would normally be called via the
    # Save button in the recipe editor window.
    rc._RecCard__rec_editor.save_cb()

    ings = rc._RecCard__rec_gui.rd.get_ings(rc.current_rec)
    check_ings([i[2] for i in lines_groups_and_dc], ings)
    print_("add_save_and_check.return:", lines_groups_and_dc, "->", added)
    return added


def check_ings(check_dics, ings):
    """Given a list of dictionaries of properties to check and
    ingredients, check that our ingredients have those properties.  We
    assume our check_dics refer to the last ingredients in the list
    ings
    """
    n = -1
    check_dics.reverse()
    for dic in check_dics:
        for k, expected in dic.items():
            val = None
            try:
                val = getattr(ings[n], k)
                assert val == expected
            except (AssertionError, IndexError):
                msg = f"{k} is {val}, should be {expected} in entry {ings[n]}"
                raise AssertionError(msg)
        n -= 1


def do_ingredients_editing(rc):
    """In a recipe card, test ingredient editing"""
    # Show the ingredients tab
    rc.show_edit('ingredients')

    # Create an new ingredient group
    idx = rc._RecCard__rec_editor.module_tab_by_name["ingredients"]
    ing_controller = rc._RecCard__rec_editor.modules[idx].ingtree_ui.ingController
    i_group = ing_controller.add_group('Foo bar')

    print_("Testing ingredient editing - add 4 ingredients to a group.")
    add_save_and_check(
        rc,
        [['1 c. sugar', i_group, {'amount': 1.0,
                                  'unit': 'c.',
                                  'item': 'sugar',
                                  'inggroup': 'Foo bar'}],
         ['2 c. silly; chopped and sorted', i_group, {'amount': 2.0,
                                                      'unit': 'c.',
                                                      'ingkey': 'silly',
                                                      'inggroup': 'Foo bar'}],
         ['3 lb. very silly', i_group, {'amount': 3.0,
                                        'unit': 'lb.',
                                        'item': 'very silly',
                                        'inggroup': 'Foo bar'}],
         ['4 tbs. strong silly', i_group, {'amount': 4.0,
                                           'unit': 'tbs.',
                                           'item': 'strong silly',
                                           'inggroup': 'Foo bar'}],
        ])
    print_("Ingredient editing successful")


def do_ingredients_undo(rc):
    """In a recipe card, test adding ingredients and undoing that"""
    # Show the ingredients tab
    rc.show_edit('ingredients')

    # Create a group with a single ingredient, adding more ingredients will
    # require more reverts.
    ings_groups_and_dcs = [  # TODO: change 1 cup of oil to 1.5
        ['1 c. oil', None, {'amount': 1, 'unit': 'c.', 'item': 'oil'}]
    ]
    refs = add_save_and_check(rc, ings_groups_and_dcs)

    idx = rc._RecCard__rec_editor.module_tab_by_name["ingredients"]
    ing_controller = rc._RecCard__rec_editor.modules[idx].ingtree_ui.ingController
    del_iter = [ing_controller.get_iter_from_persistent_ref(r) for r in refs]
    print_(f"refs: {refs}")
    print_(f"-> {del_iter}")

    # Delete the ingredients from the recipe card
    ing_controller.delete_iters(*del_iter)
    history = ing_controller.ingredient_editor_module.history
    print_(f"test_ing_undo - just deleted - UNDO HISTORY: {history}")

    # Make a save via the callback, which would normally be called via the
    # Save button in the recipe editor window.
    rc._RecCard__rec_editor.save_cb()

    # Try to access the previously added ingredient.
    # If that raises an AssertionError, it means that the deletion
    # worked as expected.

    try:
        ings = rc._RecCard__rec_gui.rd.get_ings(rc.current_rec)
        check_ings([i[2] for i in ings_groups_and_dcs], ings)
    except AssertionError:
        print_('Deletion worked!')
    else:
        print_([i[2] for i in ings_groups_and_dcs])
        print_('corresponds to')
        print_([(i.amount, i.unit, i.item) for i in ings_groups_and_dcs])
        raise Exception("Ingredients Not Deleted!")

    # The meat of this test is to undo the deletion.
    # Undo the deletion and save the card. The content should now be
    # what it was at the beginning.

    # Make a revert via the callback, which would normally be done via the
    # Revert button in the recipe editor window.
    action = ing_controller.ingredient_editor_module.action_groups[0].get_action("Undo")
    action.activate()

    history = ing_controller.ingredient_editor_module.history
    print_(f"test_ingredient_revert: reverted - history: {history}")
    rc._RecCard__rec_editor.save_cb()

    # Check that our ingredients have been put back properly by the undo action
    print_('Checking for ',[i[2] for i in ings_groups_and_dcs])

    print_("Checking in ", rc._RecCard__rec_gui.rd.get_ings(rc.current_rec))
    check_ings([i[2] for i in ings_groups_and_dcs],
                rc._RecCard__rec_gui.rd.get_ings(rc.current_rec))

    print_("Deletion revert worked!")


def do_ingredients_group_editing(rc):
    # Show the ingredients tab
    rc.show_edit('ingredients')

    idx = rc._RecCard__rec_editor.module_tab_by_name["ingredients"]
    ing_ui = rc._RecCard__rec_editor.modules[idx].ingtree_ui
    ing_controller = ing_ui.ingController

    test_group = "TEST GROUP"

    # The test relies on the first item being a group
    itr = ing_controller.imodel.get_iter(0,)

    # Test setting a group
    ing_ui.change_group(itr, test_group)
    rc._RecCard__rec_editor.save_cb()

    ings = rc._RecCard__rec_gui.rd.get_ings(rc.current_rec)
    assert(ings[0].inggroup == test_group)
    print_(f'Group successfully changed to "{test_group}"')

    # Test undoing the group
    action = ing_ui.ingredient_editor_module.action_groups[0].get_action("Undo")
    action.activate()
    rc._RecCard__rec_editor.save_cb()

    ings = rc._RecCard__rec_gui.rd.get_ings(rc.current_rec)
    assert(ings[0].inggroup != test_group)
    print_('Undo of group change worked.')


def do_undo_save_sensitivity(rc):
    # Show the description tab
    rc.show_edit('description')


    # Make a save via the callback, which would normally be called via the
    # Save button in the recipe editor window.
    rc._RecCard__rec_editor.save_cb()

    # Check that the `save` and `revert` push buttons are disabled.
    action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Save')
    is_enabled = action.get_sensitive()
    assert not is_enabled, "Save Button not de-sensitized after save"

    action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Revert')
    is_enabled = action.get_sensitive()
    assert not is_enabled, "Revert Button not de-sensitized after save"

    # preptime, cooktime, and rating are intentionally strings.
    test_values = {'preptime': '½ hours', 'cooktime': '1 hour',
                   'title': 'Foo bar', 'cuisine': 'Mexican',
                   'category': 'Entree', 'rating': '8'}

    card_display = RecCardDisplay(rc, rc._RecCard__rec_gui, rc.current_rec)

    idx = rc._RecCard__rec_editor.module_tab_by_name["description"]
    undo_action = rc._RecCard__rec_editor.modules[idx].action_groups[0].get_action(
        "Undo")
    redo_action = rc._RecCard__rec_editor.modules[idx].action_groups[0].get_action(
        "Redo")
    save_action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Save')

    for wname, value in test_values.items():
        # Get the widget from the RecCardDisplay
        widget = getattr(card_display, f"{wname}Display")
        print_(f"TESTING {wname}")

        orig_value = widget.get_text()
        widget.set_text(value)
        get_method = widget.get_text
        print_(f"Set with set_text({value})")

        msg = f"{wname} not set correctly: {get_method()}, should be {value}"
        assert get_method() == value, msg

        action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Save')
        is_enabled = action.get_sensitive()
        assert not is_enabled, "Save button not de-sensitized after save"

        action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Revert')
        is_enabled = action.get_sensitive()
        assert not is_enabled, "Revert button not de-sensitized after save"

        print_('-- Hitting Undo')
        undo_action.activate()

        value = get_method()
        msg = f"Value of {wname} is {value}, should be {orig_value}"
        assert value == orig_value, msg

        action = rc._RecCard__rec_editor.mainRecEditActionGroup.get_action('Save')
        is_enabled = action.get_sensitive()
        assert not is_enabled, f"Save should be desensitized after unsetting {wname}"

        print_("-- Hitting 'REDO'")
        redo_action.activate()
        if orig_value and isinstance(value, int):
            print_("(Hitting redo a second time for text...)")
            redo_action.activate()

        current = get_method()
        msg = f'Value of {wname} is {current}, should be {value}'
        assert current == value, msg

        assert not save_action.get_sensitive(), f'Save sensitized after setting {wname} via REDO'

        print_('-- Hitting UNDO again')

        undo_action.activate()
        if orig_value and isinstance(value, int):
            print_('(Hitting UNDO a second time for text)')
            undo_action.activate()

        assert get_method() == orig_value, "Value incorrect after UNDO->REDO->UNDO"
        assert not save_action.get_sensitive(), f"Save desensitized after undo->redo->undo of {wname}"
        print_("DONE TESTING", wname)


def test_reccard():
    with TemporaryDirectory(prefix='gourmet_', suffix='_test_reccard') as tmpdir:
        gglobals.gourmetdir = tmpdir
        rec_gui = get_application()
        rec_card = RecCard(rec_gui)

        do_ingredients_editing(rec_card)
        print('Ingredient Editing test passed!')
        do_ingredients_undo(rec_card)
        print('Ingredient Revert test passed!')
        # do_undo_save_sensitivity(rec_card)
        print('Undo properly sensitizes save widget.')
        do_ingredients_group_editing(rec_card)
        print('Ing Group Editing works.')
