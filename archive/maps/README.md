# Assyria historical atlas

This directory is copied unchanged into the generated site. It contains all data required by `/map/`; no tile server or external JavaScript service is needed at runtime.

## Historical sketches

`assyria-atlas.json` contains eleven dated snapshots, original regional coordinate sketches, city coordinates, source metadata and explanations of uncertainty. Dates use negative integers for BCE. The slider advances through snapshots, not equally spaced calendar years. There is no interpolation and no calculation of historical area.

The sketches are original editorial interpretations of the cited regional histories. They are not surveyed boundaries, transcriptions of an archaeological GIS database or tracings from an authoritative published map. Their edges must not be used to assign individual sites to ancient provinces. Solid shading sketches broad territorial control; patterning separates indirect, contested or brief control. Political relationships varied within each region as well as between dates. Babylonia is treated separately from direct provincial annexation. Only Lower Egypt is sketched for 671 BCE. No territorial polygon is invented for the surviving forces at Harran in 612 BCE, or for 609 BCE.

The heartland and historical city markers concern an ancient state. They are not an exhaustive map of Assyrian settlement, a definition of modern identity or present-day territorial claims. The end of the imperial overlay does not imply the end of Assyrian people or culture.

Original atlas narrative and historical coordinate sketches: Assyria | The Living Archive, licensed under Creative Commons Attribution 4.0 International, https://creativecommons.org/licenses/by/4.0/. Attribute the project and identify changes when reusing. The cited authors retain rights in their scholarship; citations do not imply their approval of these sketches. The original scholarship is not reproduced wholesale in this directory. For the full licensed reference texts already retained elsewhere, see `archive/references.json`.

## Modern basemap

Made with Natural Earth. Tom Patterson, Nathaniel Vaughn Kelso and contributors. Natural Earth declares its vector and raster map data public domain: https://www.naturalearthdata.com/about/terms-of-use/ . Natural Earth's boundary conventions are used only for orientation and do not resolve current disputes. Modern river courses and coastlines are not reconstructions of ancient geography.

Land and countries are retained as complete downloads. The rivers file retains the full original features for the three displayed rivers:

- `natural-earth-land.geojson`: Natural Earth 1:110m land.
- `natural-earth-countries.geojson`: Natural Earth 1:110m administrative countries.
- `natural-earth-rivers.geojson`: Selected Natural Earth 1:50m river features for the Tigris, Euphrates and Nile. Coordinates and properties are unchanged; selection and JSON serialisation are documented in the manifest.

Upstream download URLs, byte lengths and SHA-256 hashes are recorded in `assyria-atlas.json`. Acquisition: 25-26 October 2026. Upstream URLs use the source repository's moving master branch; the checked-in bytes and hashes, rather than that branch's later state, identify this edition. No external map download occurs during a build.

## Editing and verification

Edit the JSON and add evidence for each changed date or region. Keep polygon rings closed and non-intersecting, use longitude then latitude in decimal degrees, retain source identifiers and explain uncertain relationships. Do not add precise-looking borders to fill gaps in the evidence.

Run `python scripts/validate_atlas.py`, `node --check static/map.js`, `python generate.py` and `python scripts/validate.py`. Also check the map in a browser, including timeline keyboard controls, playback, modern border toggles, comparison, zoom and the final two snapshots. The source and all assets must continue to work at both the root and a GitHub Pages project path.
