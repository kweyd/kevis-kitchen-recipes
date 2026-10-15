# Kevi's Kitchen – Recipe Catalog

Free recipes for the Kevi's Kitchen iOS app. Every app checks `index.json` (via the jsDelivr CDN)
at most every 6 hours and adds new recipes automatically. **Publishing a recipe here = it's in everyone's app,
no app update needed.**

The app reads this repository from `https://cdn.jsdelivr.net/gh/kweyd/kevis-kitchen-recipes@main/`.

## Adding a recipe

1. **Pick an id**: lowercase, words separated by `-`, no umlauts (`chili-con-carne`, `kaesespaetzle`).
   The id is the file name everywhere and must never change once published.
2. **Copy the template** [`template/recipe.json`](template/recipe.json) twice:
   - `recipes/de/<id>.json` – German (the original, required)
   - `recipes/en/<id>.json` – English (same id, same amounts, units and number of ingredients and steps)
3. **Fill in the fields** (see [Fields](#fields) below) and set `"id"` to your id in both files.
4. **Add a photo** (optional): `images/<id>.jpg`, max. 1200 px on the long side, under 400 KB.
   Only photos you took yourself.
5. **Check it**:
   ```sh
   python3 scripts/validate_recipes.py <id>   # strict check of both language files
   python3 scripts/build_index.py             # rebuilds index.json, fails on broken files
   ```
6. **Commit & push.** The *Build index* workflow rebuilds `index.json` on GitHub as well.
   jsDelivr caches for up to 12 hours; to publish immediately open
   `https://purge.jsdelivr.net/gh/kweyd/kevis-kitchen-recipes@main/index.json`.

## Changing a recipe

Edit both language files and **raise `"version"` by one** in both. Without that, apps don't download the change.
Users who edited a catalog recipe in the app keep their own version.

## Removing a recipe

Delete `recipes/*/<id>.json` and `images/<id>.jpg`, then push. Apps remove it on their next update,
unless the user changed it.

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

## Submitting a recipe (for app users)

1. In the app: open your recipe → ⋯ → *Submit to community*.
2. Copy the recipe, save the photo, open the form, paste the recipe and drop the photo.
3. A maintainer reviews it. Once it's approved, it appears in everyone's app within a day (CDN cache).

Rules:
* Only recipes you wrote yourself, in your own words. Don't copy from cookbooks or websites.
* Only photos you took yourself. No photos from the internet, not even "free" stock photos.
* By submitting you release recipe and photo under CC0.

## For maintainers

Review the issue, then add the label **`approved`**. The *Import recipe* workflow creates the files,
rebuilds `index.json` and closes the issue. Imported recipes only have one language; add the other one
by hand and run `scripts/validate_recipes.py`. Manual changes in `recipes/` rebuild the index automatically.

After changing the catalog, also update the snapshot bundled in the app, so it works offline from the first
launch: in the app repository run `python3 tools/build_snapshot.py`.

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
