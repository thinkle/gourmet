import gourmet.recipeManager, gourmet.exporters

rm = gourmet.recipeManager.RecipeManager()
i=gourmet.exporters.gxml2_exporter.rview_to_xml(rm,rm.rview,'rescued_recipes.xml')
i.run()
