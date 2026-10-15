#!/usr/bin/env python3
"""Turns an approved submission issue into recipes/<id>.json and images/<id>.jpg."""
import io
import json
import os
import pathlib
import re
import unicodedata
import urllib.request

from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent
body = os.environ["ISSUE_BODY"]

match = re.search(r"### Recipe\s+```(?:json)?\s*(.*?)```", body, re.S)
if not match:
    raise SystemExit("No recipe JSON found in the issue")
recipe = json.loads(match.group(1))
language = "en" if re.search(r"### Language\s+English", body) else "de"
recipe["version"] = 1
recipe.pop("image", None)
recipe["license"] = "CC0-1.0"
recipe["author"] = recipe.get("author") or os.environ.get("ISSUE_AUTHOR", "")

title = re.sub(r"['’]", "", recipe["title"]).replace("ß", "ss")
slug = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-") or "recipe"
recipe_id, n = slug, 2
while list((root / "recipes").glob(f"*/{recipe_id}.json")):
    recipe_id, n = f"{slug}-{n}", n + 1
recipe["id"] = recipe_id

(root / "recipes" / language).mkdir(parents=True, exist_ok=True)
(root / "recipes" / language / f"{recipe_id}.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n")

photo = re.search(r"### Photo.*?(https://github\.com/user-attachments/assets/[\w-]+|https://\S+?\.(?:jpe?g|png|heic|webp))", body, re.S | re.I)
if photo:
    with urllib.request.urlopen(photo.group(1)) as response:
        image = Image.open(io.BytesIO(response.read())).convert("RGB")
    image.thumbnail((1200, 1200))
    (root / "images").mkdir(exist_ok=True)
    image.save(root / "images" / f"{recipe_id}.jpg", "JPEG", quality=80, optimize=True)

print(f"Imported {recipe_id}")
