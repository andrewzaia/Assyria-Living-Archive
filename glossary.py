"""A concise editorial glossary linked to the archive's longer, sourced entries."""
TERMS=[
('Akkadian','An ancient Semitic language; Assyrian and Babylonian are conventionally described as its varieties.','akkadian-and-cuneiform'),
('Aramaic','A language tradition with multiple ancient and modern varieties, including Syriac and Neo-Aramaic.','aramaic'),
('Assur / Ashur','The name used for an ancient city, its associated deity and other related ancient references; context matters.','ashur'),
('Assyriology','The study of ancient Mesopotamian languages, texts, societies and material remains.','research-guide'),
('Attribution','Identification of a source, author or rights holder, with the information needed to trace the material.','research-guide'),
('Canon','The collection of books recognised as Scripture by a religious tradition. Canonical lists differ.','bible-reading-guide'),
('Calah / Kalhu','The ancient city associated with the archaeological site now called Nimrud.','nimrud'),
('Classical Syriac','A literary and liturgical form of Aramaic associated in its origins with Edessa.','classical-syriac'),
('Cuneiform','A writing system using wedge-shaped signs, used for several languages.','akkadian-and-cuneiform'),
('Deuterocanonical books','Books whose canonical status differs among Christian traditions; the local Bible reader labels its additional collection.','bible-reading-guide'),
('Diaspora','Communities living beyond an ancestral or historical homeland, with varied experiences of migration and identity.','diaspora'),
('Dialect','A regional or social language variety; precise speaker and locality information matters when documenting speech.','sureth'),
('Dur-Sharrukin','The ancient royal city associated with Sargon II and the site of Khorsabad.','khorsabad'),
('East Syriac','A designation used for a Syriac liturgical tradition and related writing practices; specify the context.','faith-and-churches'),
('Edessa / Urhay','Historical names associated with the city now called Urfa and its Syriac literary heritage.','edessa'),
('Exile','Removal or displacement from a homeland; biblical and modern accounts require their own dates and contexts.','bible-deportation'),
('Inscription','Writing placed on an object or surface. Its wording, date, provenance and purpose form part of its evidence.','royal-reliefs'),
('Khigga','A name associated with a widespread Assyrian line or circle dance tradition.','dance'),
('Lamassu','A term associated with protective supernatural beings, including the monumental guardians displayed in this archive.','lamassu'),
('Manuscript','A handwritten text-bearing object; its physical date may differ from the date of the work it copies.','manuscripts'),
('Neo-Aramaic','A designation for modern Aramaic language varieties, rather than a single uniform spoken language.','aramaic'),
('Nineveh','An ancient Assyrian city, a biblical setting and an archaeological site near present-day Mosul.','nineveh'),
('Oral history','Recorded testimony about lived experience, preserved with attribution, consent and contextual information.','oral-history'),
('Peshitta','A Syriac biblical version and textual tradition; consult the retained reference for its different parts and transmission.','reference-peshitta'),
('Primary source','Material directly relevant to the subject being studied, such as a biblical passage, inscription or firsthand testimony.','research-guide'),
('Provenance','The documented origin and ownership or transmission history of an object or record.','heritage-stewardship'),
('Public domain','A rights status permitting reuse without copyright permission; it is distinct from merely being publicly accessible.','research-guide'),
('Revision','An identifiable version of a text; retained references record the source revision and a file checksum.','research-guide'),
('Sureth','A name used for several North-Eastern Neo-Aramaic varieties, with scope varying among speakers and publications.','sureth'),
('Surayt / Turoyo','Names associated with the Neo-Aramaic language tradition of Tur Abdin and its diaspora.','surayt'),
('Transliteration','Representation of writing in another script, distinct from translating its meaning into another language.','syriac-scripts'),
('Tur Abdin','A historical region associated with Syriac Christian communities, monasteries and the Surayt language.','tur-abdin'),
('West Syriac','A designation for a Syriac liturgical tradition and related writing practices; it does not automatically define ethnicity.','faith-and-churches'),
('Word count','A measurement of text volume, not a measure of historical reliability or independent scholarly review.','research-guide')]

def render(heading,escape):
    h=escape
    entries=''.join(f'<section id="term-{i}"><h2>{h(term)}</h2><p>{h(text)} <a class="text-link" href="/articles/{slug}/">Read the sourced entry &#8594;</a></p></section>' for i,(term,text,slug) in enumerate(sorted(TERMS)))
    return '<main id="main" class="wrap section narrow-page">'+heading('WORDS IN CONTEXT','A glossary for the journey.','Short explanations of recurring terms, each linked to a longer reading entry. These definitions introduce the subject; the linked articles carry sources and fuller context.')+'<div class="prose">'+entries+'</div></main>'
