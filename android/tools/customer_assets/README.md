# Character asset factory

This offline factory converts **still images only** into the exact hero atlas
used by Family Force. It never calls Higgsfield, never creates video, and never
writes into the app runtime asset directory.

Input layout:

```text
character-input/
  portrait.png
  model_sheet.png
  actions/
    idle/01.png ... 08.png
    walk/01.png ... 08.png
    ...all 11 contract actions...
```

An action may instead be a single horizontal eight-frame sheet such as
`actions/walk.png`. Action frames must be transparent PNG/WebP; the factory
deliberately does not guess or remove photographic backgrounds. Portrait and
model-sheet references may also be JPEG because they are not copied to the
runtime atlas.

Run:

```sh
python3 android/tools/customer_assets/character_asset_factory.py \
  --character customer_hero \
  --input customers/order-0001/work/customer_hero \
  --output customers/order-0001/staging/customer_hero
```

Exit `0` means strict QA passed, `2` means files were built for visual review
but animation QA failed, and `1` means invalid/missing input. Output includes
the `1536x2112` RGBA atlas, a labelled contact sheet, and machine-readable QA.
Nothing may be copied into an APK unless `passed` is true and the contact sheet
has human approval.

Keep `style_formula.template.json` frozen for an order. Each action receives at
most three still-image generation attempts. Retrying never permits regeneration
of an approved portrait, model sheet, or action; after the third failure use a
manual art correction. This caps credit use and prevents identity/style drift.
