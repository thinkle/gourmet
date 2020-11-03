from . import (data_plugin, export_plugin, main_plugin, nutPrefsPlugin,
               reccard_plugin, shopping_plugin)

plugins = [
    data_plugin.NutritionDataPlugin,
    main_plugin.NutritionMainPlugin,
    reccard_plugin.NutritionDisplayPlugin,
    export_plugin.NutritionBaseExporterPlugin,
    shopping_plugin.ShoppingNutritionalInfoPlugin,
    nutPrefsPlugin.NutritionPrefs,
    ]
