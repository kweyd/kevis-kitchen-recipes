#!/usr/bin/env python3
"""Strict check of catalog recipe files (stricter than the app, which tolerates missing fields).

    python3 scripts/validate_recipes.py              # all recipes
    python3 scripts/validate_recipes.py id1 id2 ...  # only these ids
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "recipes"
UNITS = {"g", "kg", "ml", "l", "piece", "tbsp", "tsp", "pinch", "clove", "can", "bunch", "pack", "slice", "to taste"}
CATEGORIES = {"produce", "bakery", "meatFish", "dairy", "dryGoods", "canned", "spices", "baking", "breakfast",
              "snacks", "drinks", "frozen", "household", "other"}
DIETS = {"plant", "animal", "fish", "meat"}
ALLERGENS = {"gluten", "crustaceans", "eggs", "fish", "peanuts", "soy", "milk", "lactose", "nuts", "celery",
             "mustard", "sesame", "sulphites", "lupin", "molluscs", "histamine"}
TAGS = {"de": {"vegetarisch", "vegan", "schnell"}, "en": {"vegetarian", "vegan", "quick"}}
# Cooking is the default and has no "kind". Baking recipes aren't suggested as daily meals (app 1.2+),
# breakfast and dinner recipes only for those meals (app 1.5+).
KINDS = {"breakfast", "dinner", "baking"}


def check_step_ingredients(step, where, ingredients, used, errors):
    """Ingredients a step uses (app 1.5+): position in the ingredient list, optional share of the amount."""
    uses = step.get("ingredients", [])
    if not isinstance(uses, list):
        errors.append(f"{where}: ingredients must be a list")
        return
    seen = set()
    for use in uses:
        index, share = use.get("ingredient") if isinstance(use, dict) else None, use.get("share", 1) if isinstance(use, dict) else None
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(ingredients):
            errors.append(f"{where}: ingredient {index!r} is not a position in the ingredient list")
            continue
        if index in seen:
            errors.append(f"{where}: ingredient {index} listed twice")
        seen.add(index)
        if not isinstance(share, (int, float)) or isinstance(share, bool) or not 0 < share <= 1:
            errors.append(f"{where}: share of ingredient {index} must be above 0 and at most 1")
            continue
        if "share" in use and share == 1:
            errors.append(f"{where}: leave out share 1 for ingredient {index}")
        used[index] = used.get(index, 0) + share


def check_ingredient(ing, where, errors):
    if not isinstance(ing.get("name"), str) or not ing["name"].strip():
        errors.append(f"{where}: name missing")
    if ing.get("unit") not in UNITS:
        errors.append(f"{where}: unit {ing.get('unit')!r} not in {sorted(UNITS)}")
    if ing.get("unit") != "to taste" and not isinstance(ing.get("amount"), (int, float)):
        errors.append(f"{where}: amount missing (use unit 'to taste' if there is no amount)")
    if ing.get("category") not in CATEGORIES:
        errors.append(f"{where}: category {ing.get('category')!r} invalid")
    if ing.get("diet") not in DIETS:
        errors.append(f"{where}: diet {ing.get('diet')!r} invalid")
    if not isinstance(ing.get("allergens"), list) or not set(ing["allergens"]) <= ALLERGENS:
        errors.append(f"{where}: allergens {ing.get('allergens')!r} invalid")
    if "shelfLifeDays" in ing and not isinstance(ing["shelfLifeDays"], int):
        errors.append(f"{where}: shelfLifeDays must be an int")


def check(recipe_id):
    errors = []
    files = {lang: ROOT / lang / f"{recipe_id}.json" for lang in ("de", "en")}
    data = {}
    for lang, path in files.items():
        if not path.exists():
            # German is the original and required, English is optional.
            if lang == "de":
                errors.append(f"{lang}: file missing")
            continue
        try:
            data[lang] = json.loads(path.read_text())
        except json.JSONDecodeError as error:
            errors.append(f"{lang}: invalid JSON: {error}")
    for lang, r in data.items():
        p = f"{lang}"
        if r.get("id") != recipe_id:
            errors.append(f"{p}: id must be {recipe_id!r}")
        for key in ("title", "summary", "emoji"):
            if not isinstance(r.get(key), str) or not r[key].strip():
                errors.append(f"{p}: {key} missing")
        if not isinstance(r.get("version"), int) or r["version"] < 1:
            errors.append(f"{p}: version must be an int ≥ 1")
        if r.get("license") != "CC0-1.0":
            errors.append(f"{p}: license must be CC0-1.0")
        if not isinstance(r.get("servings"), int) or r["servings"] < 1:
            errors.append(f"{p}: servings must be an int ≥ 1")
        if not isinstance(r.get("prepMinutes"), int) or r["prepMinutes"] < 1:
            errors.append(f"{p}: prepMinutes must be an int")
        if "kind" in r and r["kind"] not in KINDS:
            errors.append(f"{p}: kind must be one of {sorted(KINDS)}, or left out for cooking")
        if not set(r.get("tags", [])) <= TAGS[lang]:
            errors.append(f"{p}: tags must be from {sorted(TAGS[lang])}")
        n = r.get("nutritionPerServing", {})
        for key in ("kcal", "protein", "fat", "carbs"):
            if not isinstance(n.get(key), (int, float)):
                errors.append(f"{p}: nutritionPerServing.{key} missing")
        if not r.get("ingredients"):
            errors.append(f"{p}: no ingredients")
        for i, ing in enumerate(r.get("ingredients", [])):
            check_ingredient(ing, f"{p} ingredient {i} ({ing.get('name')})", errors)
            for j, alt in enumerate(ing.get("alternatives", [])):
                check_ingredient(alt, f"{p} ingredient {i} alternative {j}", errors)
                if alt.get("diet") == ing.get("diet") and set(alt.get("allergens", [])) >= set(ing.get("allergens", [])):
                    errors.append(f"{p} ingredient {i} alternative {j}: solves nothing (same diet, no allergen removed)")
        if not r.get("steps"):
            errors.append(f"{p}: no steps")
        used = {}
        for i, step in enumerate(r.get("steps", [])):
            check_step_ingredients(step, f"{p} step {i}", r.get("ingredients", []), used, errors)
            if not isinstance(step.get("text"), str) or not step["text"].strip():
                errors.append(f"{p} step {i}: text missing")
            if "timerMinutes" in step and (not isinstance(step["timerMinutes"], int) or step["timerMinutes"] < 1):
                errors.append(f"{p} step {i}: timerMinutes must be an int ≥ 1")
            if "@" in step.get("text", ""):
                errors.append(f"{p} step {i}: contains an @mention")
        # Shares are parts of the amount: together the steps can't use more than all of it. "To taste" has no amount.
        for index, total in used.items():
            if total > 1.01 and r["ingredients"][index].get("unit") != "to taste":
                errors.append(f"{p} ingredient {index}: steps use {total:.0%} of it, at most 100 %")
    if len(data) == 2:
        de, en = data["de"], data["en"]
        for key in ("servings", "prepMinutes", "kind", "nutritionPerServing", "emoji"):
            if de.get(key) != en.get(key):
                errors.append(f"de/en differ in {key}")
        if len(de.get("ingredients", [])) != len(en.get("ingredients", [])):
            errors.append("de/en have a different number of ingredients")
        else:
            for i, (a, b) in enumerate(zip(de["ingredients"], en["ingredients"])):
                for key in ("amount", "unit", "category", "diet", "allergens", "pantry", "shelfLifeDays"):
                    if a.get(key) != b.get(key):
                        errors.append(f"de/en ingredient {i} differ in {key}")
                if len(a.get("alternatives", [])) != len(b.get("alternatives", [])):
                    errors.append(f"de/en ingredient {i} differ in number of alternatives")
        if len(de.get("steps", [])) != len(en.get("steps", [])):
            errors.append("de/en have a different number of steps")
        else:
            for i, (a, b) in enumerate(zip(de["steps"], en["steps"])):
                if a.get("ingredients", []) != b.get("ingredients", []):
                    errors.append(f"de/en step {i} use different ingredients")
    return errors


if __name__ == "__main__":
    ids = sys.argv[1:] or sorted({p.stem for p in ROOT.glob("*/*.json")})
    failed = 0
    for recipe_id in ids:
        errors = check(recipe_id)
        if errors:
            failed += 1
            print(f"✗ {recipe_id}")
            for error in errors:
                print(f"    {error}")
    print(f"{len(ids) - failed}/{len(ids)} recipes OK")
    sys.exit(1 if failed else 0)
