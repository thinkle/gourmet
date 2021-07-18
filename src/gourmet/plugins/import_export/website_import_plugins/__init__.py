from . import (about_dot_com_plugin, allrecipes_plugin,
               cooksillustrated_plugin, epicurious_plugin, foodnetwork_plugin,
               ica_se_plugin, nytimes_plugin)

plugins = [about_dot_com_plugin.AboutDotComPlugin,
           foodnetwork_plugin.FoodNetworkPlugin,
           allrecipes_plugin.AllRecipesPlugin,
           ica_se_plugin.IcaSePlugin,
           epicurious_plugin.EpicuriousPlugin,
           nytimes_plugin.NYTPlugin,
           cooksillustrated_plugin.WebImporterPlugin,
           cooksillustrated_plugin.CooksIllustratedPlugin,
           ]
