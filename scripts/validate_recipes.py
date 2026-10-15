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
             "mustard", "sesame", "sulphites", "lupin", "molluscs"}
TAGS = {"de": {"vegetarisch", "vegan", "schnell"}, "en": {"vegetarian", "vegan", "quick"}}


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
        for i, step in enumerate(r.get("steps", [])):
            if not isinstance(step.get("text"), str) or not step["text"].strip():
                errors.append(f"{p} step {i}: text missing")
            if "timerMinutes" in step and (not isinstance(step["timerMinutes"], int) or step["timerMinutes"] < 1):
                errors.append(f"{p} step {i}: timerMinutes must be an int ≥ 1")
            if "@" in step.get("text", ""):
                errors.append(f"{p} step {i}: contains an @mention")
    if len(data) == 2:
        de, en = data["de"], data["en"]
        for key in ("servings", "prepMinutes", "nutritionPerServing", "emoji"):
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
