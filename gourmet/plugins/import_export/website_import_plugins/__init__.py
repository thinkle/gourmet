plugins = []
try:
    import about_dot_com_plugin
    plugins.append(about_dot_com_plugin.AboutDotComPlugin)
except ImportError:
    pass
try:
    import foodnetwork_plugin
    plugins.append(foodnetwork_plugin.FoodNetworkPlugin)
except ImportError:
    pass
try:
    import allrecipes_plugin
    plugins.append(allrecipes_plugin.AllRecipesPlugin)
except ImportError:
    pass
try:
    import ica_se_plugin
    plugins.append(ica_se_plugin.IcaSePlugin)
except ImportError:
    pass
try:
    import epicurious_plugin
    plugins.append(epicurious_plugin.EpicuriousPlugin)
except ImportError:
    pass
try:
    import nytimes_plugin
    plugins.append(nytimes_plugin.NYTPlugin)
except ImportError:
    pass
try:
    import cooksillustrated_plugin
    plugins.append(cooksillustrated_plugin.WebImporterPlugin)
    plugins.append(cooksillustrated_plugin.CooksIllustratedPlugin)
except ImportError:
    pass
