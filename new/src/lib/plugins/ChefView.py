import clutter

def main():
    stage = clutter.stage_get_default()
    stage.set_size(500, 500)
    stage.set_color(clutter.color_parse("#FFF"))

    rect1, rect2, rect3 = clutter.Rectangle(), clutter.Rectangle(), clutter.Rectangle()
    group1, group2, group3 = clutter.Group(), clutter.Group(), clutter.Group()

    group1.add(rect1, group2)
    group2.add(rect2, rect3)
    group1.set_position(100, 100)
    group2.set_position(100, 100)
    rect3.set_position(100, 100)

    rect1.set_position(0, 0)
    rect2.set_position(0, 0)

    rect1.set_size(150, 150)
    rect2.set_size(150, 150)
    rect3.set_size(150, 150)

    rect1.set_color(clutter.color_parse("#FF000090"))
    rect2.set_color(clutter.color_parse("#00FF0090"))
    rect3.set_color(clutter.color_parse("#0000FF90"))

    stage.add(group1)

    stage.show_all()
    group1.show_all()
    group2.show_all()

    stage.connect("key-press-event", clutter.main_quit)
    clutter.main()

if __name__ == '__main__':
    main()
