# Biblical primary-source collection

The archive treats the Bible as the primary source for the biblical events and peoples it records. Guides cite book, chapter and verse before additional interpretation. Archaeology, inscriptions and scholarship are identified separately when used for dates, identifications or comparison. Faith statements in the biblical text, narrative details and interpretive claims should remain distinguishable.

## Retained edition and rights

World English Bible British Edition with Deuterocanon (WEBBE), from the publisher eBible.org: https://ebible.org/bible/details.php?id=eng-webbe . Retrieved 26 October 2026. The publisher dedicates this translation to the public domain. Its name is a trademark identifying faithful copies. The actual Scripture wording and punctuation are preserved, not rewritten by AI or harmonised between accounts.

All 81 books and 38,058 verse lines supplied in the publisher's verse-per-line edition are retained under `books/`. These include the 66 Old and New Testament books and an extended collection of 15 additional books. Inclusion in this source edition is not a statement that all Jewish or Christian traditions share one canon. The source code `4ES` is displayed as 2 Esdras, following the edition's English title.

The source format already omitted paragraph formatting, translator footnotes, introductions and section headings. Our reader places each verse in its own paragraph and adds stable verse links. It does not claim to preserve features absent from the downloaded format. Consult the publisher's other editions for translator notes and introductions.

`source-notice.htm` and `haiola.css` preserve the publisher notice and its stylesheet. `source-signature.asc` preserves the signature supplied in the ZIP. SHA-256 integrity is checked locally. OpenPGP signature authentication has not been performed or claimed.

## Reconstructing the complete source

`manifest.json` records the source ZIP URL, SHA-256 of the downloaded ZIP, the complete text hash, per-book byte lengths and hashes, and the book order. Concatenate `books/<code>.txt` in manifest order, without adding separators, to reconstruct `eng-webbe_vpl.txt` byte for byte. Equivalent XML and SQL serialisations in the original ZIP are not duplicated here. The ZIP itself is identified by its hash rather than copied as a second full serialisation of the same Bible.

Ordinary builds never download Scripture. `scripts/capture_bible.py` is the explicit acquisition step. To reuse a previously downloaded ZIP, pass `--archive /path/to/eng-webbe_vpl.zip`. Review source changes before replacing a retained edition. Do not silently substitute a different translation.

## Reproducible coverage

`concordance.json` is generated offline from every retained verse using the explicit case-insensitive, whole-name regular expressions in `bible_support.py`. One verse produces one index entry, even if multiple terms match. It includes Assyria/Assyrians, Asshur/Assur, Nineveh and spelling variants, Nimrod, named cities, kings and selected officials, plus Holofernes. Alias rules are included in the downloadable index. The filter does not treat words such as "assurance" as references to Assur.

The 267 entries are named-reference matches, not 267 independently identified Assyrians. Pul in Isaiah 66:19 occurs in a list of nations; Asshurim in Genesis 25:3 is not automatically the Asshur of Genesis 10:22. Shalman in Hosea 10:14 requires identification. Office titles may occur in other royal contexts. The results are a route to primary context, not an automatic ethnic classifier.

Twenty-six original reading guides add related passages without literal name matches. Complete chapters are generated for every named-reference match and every guide or existing article passage. The index does not claim completeness for every indirect allusion, every translation, or every theological interpretation. Guide notes identify parallel accounts, uncertain identifications and relevant canon differences.

## Editorial integrity

Bible wording is quoted exactly from the retained edition. Exact source quotations can retain source dash typography; new editorial prose follows the site's ASCII hyphen standard. Biblical quotations are visibly separated from commentary. The USCCB's discussion of Judith is cited as one named ecclesial interpretation; the text of Judith remains accessible in full and is not altered to fit an imperial chronology. Old Testament, New Testament and additional books are labelled in the reader and index.

Run `python scripts/validate_bible.py` for full-source reconstruction, reference integrity, concordance and generated chapter checks. The ordinary site validator also checks selected references. Browser checks cover live filtering, pagination, source downloads and verse links.
