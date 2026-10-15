#!/usr/bin/env python3
"""Validates all recipes and writes index.json.

Layout: recipes/<language>/<id>.json, images/<id>.jpg
Every recipe file has a "version". Raise it when you change a recipe, so apps download the update.
"""
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parent.parent
recipes, errors = {}, []

for path in sorted((root / "recipes").glob("*/*.json")):
    language, recipe_id = path.parent.name, path.stem
    try:
        recipe = json.loads(path.read_text())
        assert recipe.get("title"), "title missing"
        assert recipe.get("ingredients"), "ingredients missing"
        assert recipe.get("steps"), "steps missing"
        assert recipe.get("license", "CC0-1.0") == "CC0-1.0", "license must be CC0-1.0"
    except Exception as error:  # noqa: BLE001
        errors.append(f"{language}/{path.name}: {error}")
        continue
    entry = recipes.setdefault(recipe_id, {"id": recipe_id, "version": 1, "image": None, "languages": {}})
    entry["version"] = max(entry["version"], int(recipe.get("version", 1)))
    entry["languages"][language] = f"recipes/{language}/{path.name}"

for recipe_id, entry in recipes.items():
    image = root / "images" / f"{recipe_id}.jpg"
    if image.exists():
        entry["image"] = f"images/{image.name}"
        if image.stat().st_size > 400_000:
            errors.append(f"images/{image.name}: larger than 400 KB, please shrink it")

index = {"version": 2, "recipes": sorted(recipes.values(), key=lambda e: e["id"])}
(root / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
print(f"{len(recipes)} recipes indexed")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
