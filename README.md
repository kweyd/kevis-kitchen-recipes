# Kevi's Kitchen – Recipe Catalog

Free recipes for the Kevi's Kitchen iOS app. Every app checks `index.json` (via the jsDelivr CDN)
at most every 6 hours and adds new recipes automatically. **Publishing a recipe here = it's in everyone's app,
no app update needed.**

The app reads this repository from `https://cdn.jsdelivr.net/gh/kweyd/kevis-kitchen-recipes@main/`.

## Contributing

Everyone is welcome to add or improve recipes, but **all changes go through a pull request**.
Nobody can push to this repository directly; the maintainer reviews every pull request and decides whether
to merge it. Only merged recipes reach the app.

Don't want to use Git? Use the app instead: see [Submitting a recipe from the app](#submitting-a-recipe-from-the-app).

### Adding a recipe

1. **Fork** this repository (button *Fork* at the top right on GitHub) and create a branch in your fork,
   e.g. `recipe/chili-con-carne`.
2. **Pick an id**: lowercase, words separated by `-`, no umlauts (`chili-con-carne`, `kaesespaetzle`).
   The id is the file name everywhere and must never change once published.
3. **Copy the template** [`template/recipe.json`](template/recipe.json):
   - `recipes/de/<id>.json` – German (the original, required)
   - `recipes/en/<id>.json` – English (optional; same id, same amounts, units and number of ingredients and steps)
4. **Fill in the fields** (see [Fields](#fields) below) and set `"id"` to your id.
5. **Add a photo** (optional): `images/<id>.jpg`, max. 1200 px on the long side, under 400 KB.
   Only photos you took yourself.
6. **Check it** locally:
   ```sh
   python3 scripts/validate_recipes.py <id>   # strict check of the recipe files
   ```
   Don't commit `index.json`, it's rebuilt automatically after the merge.
7. **Open a pull request** against `main` and fill in the checklist. The *Check recipes* workflow validates
   your files; fix anything it reports by pushing to the same branch.
8. The maintainer reviews it and may ask for changes. Once it's merged, the recipe is in everyone's app
   within a day.

One recipe per pull request, please. Pull requests that change anything outside `recipes/` and `images/`
(scripts, workflows, README) need a good explanation.

### Changing a recipe

Same as above, but edit the existing files and **raise `"version"` by one** in every language file.
Without that, apps don't download the change. Users who edited a catalog recipe in the app keep their own version.

### Removing a recipe

Open an issue or a pull request that deletes `recipes/*/<id>.json` and `images/<id>.jpg`. Apps remove the recipe
on their next update, unless the user changed it.

## Fields

| Field | Meaning |
|---|---|
| `id` | Same as the file name, without `.json` |
| `version` | Starts at `1`, raise it with every change |
| `title`, `summary` | Name and one or two sentences shown in the app |
| `emoji` | One emoji, shown when there is no photo |
| `servings` | Portions the amounts are for. The app scales from there |
| `prepMinutes` | Total time in minutes |
| `tags` | Optional. German: `vegetarisch`, `vegan`, `schnell` · English: `vegetarian`, `vegan`, `quick` |
| `author` | Your name, or `Kevi's Kitchen` |
| `license` | Always `CC0-1.0` |
| `nutritionPerServing` | `kcal`, `protein`, `fat`, `carbs` (grams) per portion, estimated is fine |
| `ingredients` | List of ingredients, see below |
| `steps` | List of `{ "text": "…" }`, optionally with `"timerMinutes"` for a timer button in cook mode |

### Ingredients

| Field | Meaning |
|---|---|
| `name` | As you'd write it on a shopping list (`Onion`, not `1 large onion, diced`) |
| `amount` | Number for the given `servings`. Leave it out when the unit is `to taste` |
| `unit` | `g`, `kg`, `ml`, `l`, `piece`, `tbsp`, `tsp`, `pinch`, `clove`, `can`, `bunch`, `pack`, `slice`, `to taste` |
| `category` | Supermarket aisle: `produce`, `bakery`, `meatFish`, `dairy`, `dryGoods`, `canned`, `spices`, `baking`, `breakfast`, `snacks`, `drinks`, `frozen`, `household`, `other` |
| `pantry` | `true` for staples most people have at home (salt, pepper, oil, flour, spices, onions, garlic …). They only go on the shopping list if the user taps them in the "Got these at home?" check |
| `note` | Optional, shown next to the ingredient (`large`, `drained`) |
| `shelfLifeDays` | Optional. How many days it stays fresh; decides which shopping trip it's bought on. Without it the category default is used; `0` means it keeps for a long time |
| `diet` | `plant`, `animal` (dairy, eggs, honey), `fish`, `meat` |
| `allergens` | Any of `gluten`, `crustaceans`, `eggs`, `fish`, `peanuts`, `soy`, `milk`, `lactose`, `nuts`, `celery`, `mustard`, `sesame`, `sulphites`, `lupin`, `molluscs`. Empty list if none |
| `alternatives` | Optional replacements for other diets or allergies (same fields, without `pantry`). An alternative must change the diet or remove an allergen |

## Submitting a recipe from the app

1. In the app: open your recipe → ⋯ → *Submit to community*.
2. Copy the recipe, save the photo, open the form, paste the recipe and drop the photo.
3. A maintainer reviews it. Once it's approved, it appears in everyone's app within a day (CDN cache).

Rules:
* Only recipes you wrote yourself, in your own words. Don't copy from cookbooks or websites.
* Only photos you took yourself. No photos from the internet, not even "free" stock photos.
* By submitting you release recipe and photo under CC0.

## For maintainers

**Pull requests**: check the *Check recipes* result and the content (own words, own photo, sensible amounts,
`pantry` set for staples), then merge. Pushing to `main` (also by merging) runs *Build index*, which rebuilds
`index.json`. jsDelivr caches for up to 12 hours; to publish immediately open
`https://purge.jsdelivr.net/gh/kweyd/kevis-kitchen-recipes@main/index.json`.

**Issues from the app**: review the issue, then add the label **`approved`**. Only people with write access can
add labels. The *Import recipe* workflow creates the files, rebuilds `index.json` and closes the issue.

**App snapshot**: after changing the catalog, also update the recipes bundled in the app, so it works offline from
the first launch: in the app repository run `python3 tools/build_snapshot.py`.

## Structure

```
index.json                 generated, list of all recipes (don't edit by hand)
recipes/de/<id>.json       recipe in German (same format as the app's .kkrecipe files, without photo)
recipes/en/<id>.json       English version with the same id
images/<id>.jpg            max. 1200 px, under 400 KB
template/recipe.json       starting point for a new recipe
scripts/                   validator, index builder and issue importer (used by GitHub Actions)
```

## License

**Everything in this repository is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)**
(public domain). Anyone can use it for anything, without attribution.
