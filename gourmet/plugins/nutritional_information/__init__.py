import data_plugin, main_plugin, reccard_plugin, export_plugin, shopping_plugin
import nutPrefsPlugin
plugins = [
    data_plugin.NutritionDataPlugin,
    main_plugin.NutritionMainPlugin,
    reccard_plugin.NutritionDisplayPlugin,
    export_plugin.NutritionBaseExporterPlugin,
    shopping_plugin.ShoppingNutritionalInfoPlugin,
    nutPrefsPlugin.NutritionPrefs,
    ]
