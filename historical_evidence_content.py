"""Original biblical-primary and artefact-anchored historical comparison studies.

Scripture is primary evidence for what the biblical account says. Royal objects,
chronicles and scholarly editions are independent but differently situated sources.
Citations and limitations are mapped separately in data/section-evidence.json.
"""
ARTICLES = []

def add(slug, title, summary, sections, sources, related, passages, note):
    ARTICLES.append({
        'slug': slug,
        'title': title,
        'category': 'History & archaeology',
        'summary': summary,
        'sections': [dict(title=title, text=text) for title, text in sections],
        'sources': sources,
        'related': related,
        'passages': passages,
        'note': note,
    })


add(
    'black-obelisk-jehu',
    'The Black Obelisk and Jehu of Israel',
    'Read the named Jehu tribute on Shalmaneser III\'s monument alongside the biblical record of Jehu\'s accession.',
    [
        ('A monument with a precise identity',
         'The Black Obelisk is a carved limestone royal monument of Shalmaneser III discovered at Kalhu, the site now known as Nimrud. The British Museum identifies it with inventory number 1848,1104.1 and describes five registers of tribute bearers. It was made late in the king\'s reign, around 825 BCE, although the tribute episodes depicted cover earlier campaigns. Its physical existence and royal inscription are separate from later interpretations of the king\'s historical achievements.'),
        ('The name Jehu and the House of Omri',
         'The second register names Jehu in connection with tribute from Israel, using the Assyrian designation House of Omri. The directly edited tribute caption is RIAo Q004693, obverse line 1, and the museum interprets the scene as tribute around 841 BCE. The designation need not mean that Jehu was the biological son of Omri: dynastic or territorial labels could persist when a ruler replaced his predecessor. The monument provides an independent Assyrian reference to Jehu and Israel in a specific imperial context, not a transcript of conversations in the Israelite palace.'),
        ('Begin with the biblical accession',
         '2 Kings 9:1-13 recounts the anointing of Jehu and his proclamation as king, while 2 Kings 9:14-37 and chapter 10 narrate the overthrow of the house of Ahab and Jehu\'s subsequent actions. Those chapters are the Bible\'s primary testimony about his accession and conduct. The Black Obelisk addresses tribute to Assyria instead; it does not repeat the prophetic commission or corroborate every event reported in Kings.'),
        ('Royal spectacle and missing voices',
         'The relief presents foreign tribute in the king\'s chosen visual language of dominance. A kneeling figure, officials and gifts are part of an official image programme, so it is not certain that the depicted person can be identified as an observed portrait of Jehu himself. Neither the visual scene nor its caption supplies the views of the tribute bearers, ordinary Israelites or Assyrian subjects compelled to fund campaigns. The objects and their omissions should be described together.'),
        ('A repeatable comparison',
         'For a sound comparison, record the monument accession number, king and approximate display date, the specific tribute register, then read the full cited passages in 2 Kings 9-10. The supportable shared frame is a king called Jehu associated with Israel in the ninth century BCE. Whether Assyrian tribute occurred before or after any particular episode in Kings requires an explicit chronological argument, not an assumed one.')
    ],
    ['bible-webbe','bm-black-obelisk','oracc-shalmaneser','oracc-riao-jehu-caption','aebp-israel'],
    ['shalmaneser-iii','bible-reading-guide','assyrian-governance','sennacherib-prism-hezekiah'],
    [('2KI',9,1,13),('2KI',9,14,37),('2KI',10,1,36)],
    'Biblical passages and royal-monument descriptions are distinct witnesses. The museum interpretation is linked, not copied; no imagery is reproduced.'
)

add(
    'sennacherib-prism-hezekiah',
    'Sennacherib\'s prism and the biblical Hezekiah',
    'An object-level guide to royal annals, Hezekiah\'s tribute, Jerusalem and the differences in source perspective.',
    [
        ('The object and the composition',
         'The British Museum catalogues the Taylor Prism as object 91032, a six-sided clay text of Sennacherib\'s campaigns dated to 691 BCE. The Israel Museum describes another prism of the annals, with an Akkadian cuneiform inscription of the same royal tradition. These are historical objects preserving Assyrian royal self-presentation. The 691 BCE date of a particular prism must not be mistaken for the 701 BCE date assigned to the Judah campaign it recounts.'),
        ('The Bible supplies its own narrative',
         '2 Kings 18:13-16 reports Sennacherib\'s attack on fortified cities of Judah and Hezekiah\'s payment of silver and gold. The following narrative, from 2 Kings 18:17 through chapter 19, presents the Assyrian envoy\'s address, the prayer of Hezekiah, Isaiah\'s response and the account of deliverance. Isaiah 36-37 provides a connected prophetic presentation; 2 Chronicles 32 gives another narrative framing. Read the distinctions among these passages before importing the language of the prisms.'),
        ('What the Assyrian annals claim',
         'The Assyrian annals boast that Sennacherib overcame rebellious Judah, received tribute and confined Hezekiah in Jerusalem. RINAP 3 Q003496, column iii lines 18-37, preserves the linked royal campaign and confinement accounts in a composite edition. The Israel Museum points out that the inscription does not explicitly describe a siege of Jerusalem. This observation is narrower than saying Jerusalem was not threatened, and it differs from a claim that the Assyrian text narrates the biblical deliverance. Comparing the sources requires attention to both what they positively report and what they leave unsaid.'),
        ('Campaign, composition and outcome',
         'A palace text composed after the campaign is a royal retrospective, shaped to display authority and success. The biblical record has its own theological and historiographical purposes. An Assyrian record of a Judah campaign and tribute supports the ancient setting of the biblical account, but agreement about those elements does not settle the reported destruction of the Assyrian force, Hezekiah\'s prayers, the chronology of every event or the precise motive for withdrawal.'),
        ('Check the right evidence',
         'Keep the prism accession number, inscription edition, campaign date and cited chapter together. RINAP 3 Q003496, column iii lines 41-42, records thirty talents of gold and eight hundred talents of silver, whereas 2 Kings 18:14 records thirty talents of gold and three hundred talents of silver. Both figures must remain separately visible. A future independent collation should check exemplar variants and translation choices. Until such collation and outside review are documented, this is an evidence-led introduction rather than a certified line-by-line historical verification.')
    ],
    ['bible-webbe','bm-taylor-prism','imj-sennacherib-prism','oracc-rinap','oracc-rinap3-sennacherib22','bm-lachish-panel'],
    ['sennacherib','bible-sennacherib-invasion','bible-hezekiah-deliverance','lachish-reliefs-context'],
    [('2KI',18,13,37),('2KI',19,1,37),('ISA',36,1,22),('ISA',37,1,38),('2CH',32,1,23)],
    'The Israel Museum distinguishes the Jerusalem confinement boast from an explicit Assyrian siege description. No object image or unlicensed translation is mirrored.'
)

add(
    'lachish-reliefs-context',
    'Lachish: war pictured on Sennacherib\'s walls',
    'From physical museum panels to the biblical campaign, distinguishing royal imagery from the experiences of displaced people.',
    [
        ('An archaeological sequence, not a photograph',
         'The British Museum records gypsum panels excavated from Room XXXVI of Sennacherib\'s Southwest Palace at Nineveh. Panel 124904 represents the beginning of the assault on Lachish, with slingers and archers. The preserved sequence was made for a palace audience and shaped to celebrate a royal military success. Its date of manufacture in the early seventh century BCE and its subject, a campaign normally dated to 701 BCE, are related but not identical.'),
        ('Prisoners and the city after assault',
         'British Museum panel 124908 depicts prisoners, carried goods and a landscape with vines, fig trees and olive trees. The catalogue makes clear that captives and spoil were essential components of this official story. Depiction supplies valuable evidence about the kinds of scenes Assyrian rulers chose to display; it does not give us named testimonies from the captured families or prove the treatment of every prisoner. A historical study must not erase those unheard people.'),
        ('The military camp and supporting cast',
         'A further panel, British Museum 124913, places royal bodyguards, horses and a camp near the conquest scene. The depiction includes logistical and ceremonial features, not merely combat. This helps researchers ask about food, transport, military preparation and the work of servants, while remaining alert to stylisation in palace art. A detailed image must not be mistaken for a measured map or a neutral operational report.'),
        ('Read Kings before harmonising',
         '2 Kings 18:13-14 describes Sennacherib moving against fortified cities of Judah and Hezekiah sending to the Assyrian king at Lachish. Verse 17 describes Assyrian officials travelling onward to Jerusalem. 2 Chronicles 32:1-9 also frames the military threat. These chapters are the primary biblical accounts; the palace reliefs support the historical existence and Assyrian commemoration of the Lachish campaign, not every sentence about Jerusalem or divine deliverance.'),
        ('A precise citation trail',
         'An object-based comparison records the museum number and palace room: 124904 for the opening assault, 124908 for prisoners and 124913 for the camp. Link the relevant chapter and verses instead of citing a generic phrase such as Assyrian relief. Reproducing the actual museum photographs requires a separate rights decision. This archive links to catalogue records and presents original prose, not copies of protected images.')
    ],
    ['bible-webbe','bm-lachish-panel','bm-lachish-deportees','bm-lachish-camp','imj-sennacherib-prism'],
    ['sennacherib-prism-hezekiah','royal-reliefs','bible-sennacherib-invasion','assyrian-deportations-texts'],
    [('2KI',18,13,17),('2CH',32,1,9)],
    'Accession-level image interpretation uses the British Museum object catalogue. No photograph or relief cast is copied.'
)

add(
    'sargon-ashdod-isaiah',
    'Sargon II, Ashdod and Isaiah 20',
    'A closely bounded comparison between a named biblical king, an official at Ashdod and Assyrian royal annals.',
    [
        ('The named king in Scripture',
         'Isaiah 20:1 names Sargon king of Assyria and says that the Tartan came to Ashdod and fought against it. This is an unusually explicit biblical reference to a named Assyrian monarch in connection with a particular western city. Isaiah 20:2-6 then describes a prophetic sign involving Egypt and Cush. The account must be read on its own terms rather than turned into an assumed copy of a palace inscription.'),
        ('The Tartan and imperial command',
         'The biblical text describes an officer associated with the army rather than explicitly placing Sargon at the head of the force in Ashdod. Tartan is a title used for a high Assyrian military office in historical discussion. Identifying the office does not give a personal name for the commander, and the text does not by itself fix the route of the campaign or the precise date of the prophet\'s sign.'),
        ('Assyrian records of Sargon',
         'The RINAP 2 corpus catalogues numerous inscriptions of Sargon II, including annals from Khorsabad. Specialist editions connect the Ashdod campaign with the late eighth-century western operations, commonly placed in 711 BCE. These royal sources give independent evidence for Sargon\'s campaigns and political claims, but readers should not treat every catalogue entry as a direct witness to the Ashdod incident; inscriptions have distinct places, states of preservation and editorial dates.'),
        ('Prophecy and a campaign are different claims',
         'Isaiah uses the Ashdod event to introduce a prophetic warning about reliance on Egypt and Cush. A royal campaign narrative and a prophetic oracle are not the same genre. Evidence for the military action does not directly verify the enacted sign, and the sign\'s interpretation cannot be derived from an Assyrian victory notice alone. The Bible remains the primary account for what Isaiah says.'),
        ('A cautious comparison route',
         'Start with Isaiah 20:1-6, identify Sargon II in the specialist king profile, then consult the RINAP 2 inscriptions relevant to the Ashdod operation. The direct Ashdod account is identified in RINAP 2 Q006488, edited lines 90-109, including the changes of ruler at Ashdod and an expedition narrative. A closer specialist study must still collate the preserved signs and assess chronology before making a sentence-level correspondence. This guide supplies the first object and corpus route without claiming that independent peer review is complete.')
    ],
    ['bible-webbe','rinap-sargon-corpus','oracc-rinap2-ashdod','aebp-sargon','bible-official-titles','oracc-rinap'],
    ['bible-sargon','sargon-ii','khorsabad','assyrian-governance'],
    [('ISA',20,1,6)],
    'The chronology of the Ashdod operation uses scholarly Assyrian synthesis; the cited Isaiah verse is primary for the biblical description.'
)

add(
    'samaria-assyrian-chronology',
    'Samaria: Shalmaneser V, Sargon II and the biblical chronology',
    'Why a connected scriptural account and multiple Assyrian reigns must not be compressed into one unqualified conquest story.',
    [
        ('Two biblical vantage points',
         '2 Kings 17:3-6 names Shalmaneser king of Assyria, describes Hoshea\'s subjection, a conspiracy and the siege of Samaria, and reports deportation after its fall. 2 Kings 18:9-12 links the siege with Hezekiah\'s chronology and also names Shalmaneser at its opening. These passages should be read side by side, including their regnal dating, before assigning every stage of the siege to a single year or person.'),
        ('What later royal records add',
         'The Assyrian historical record includes material from the reign of Shalmaneser V and claims attributed to Sargon II. The RINAP 1 corpus and specialist king entries offer a route to the surviving evidence, which is not uniform in its detail. A royal claim to have taken a city might reflect conquest, reconquest, administrative settlement or a successor\'s royal presentation. It is methodologically unsafe to treat an authorial claim of credit as a complete operational chronology.'),
        ('Do not erase the disputed attribution',
         'Modern summaries often describe Samaria\'s fall around 722 BCE and debate how to distribute responsibility between Shalmaneser V and Sargon II. The biblical narrative and Assyrian royal self-presentation do not map onto each other automatically. Where the exact moment of capture, the ruler credited or the timing of deportations is disputed, record the uncertainty rather than asserting that one brief account settles the whole sequence.'),
        ('People, movement and provincial administration',
         '2 Kings 17:6 names deportation destinations; 2 Kings 17:24 describes later settlement in the cities of Samaria. 2 Kings 18:11-12 repeats the displacement theme. The Assyrian empire\'s administrative policies supply external context for organised population movement, but they are not a census of particular Israelite families. These narratives record the experience in theological and state language, and neither is an individual survivor\'s testimony.'),
        ('How to pursue exact comparison',
         'A high-resolution study should specify each royal inscription by ruler, edition and line, consider the biblical regnal synchronisms in full and distinguish conquest, regime change, provincial organisation and resettlement. This guide preserves that problem openly. The evidence demonstrates that multiple source traditions discuss the crisis of northern Israel; it does not make every chronological disagreement disappear.')
,
        ("Before the final siege: Menahem and tributary payment",
         "RINAP 1, Tiglath-pileser III 32 (Q003445), obverse line 1, names Menahem of Samaria in a list of rulers providing tribute to the Assyrian crown. Second Kings 15:19-20 names Pul in its account of the Assyrian approach to Menahem and the forced collection of silver. The royal list and Kings speak about tribute in the same historical context, but their surviving forms serve different audiences. The Assyrian edition does not verify how a levy was distributed among household groups, and it does not describe the later three-year siege. The conventional identification of Pul with Tiglath-pileser III should be stated openly rather than silently substituting royal names."),
        ("Pekah and Hoshea: the original damaged verb",
         "RINAP 1, Tiglath-pileser III 42 (Q003455), obverse lines 15'-18', places the fall of the older northern Israelite political order before the final Samaria crisis. It mentions Bīt-Ḫumrî, Pekah and Hoshea. Crucially, the verb near the death of Pekah is damaged: the edited commentary discusses readings equivalent to I killed and they killed. Second Kings 15:30 expressly names Hoshea in a conspiracy and killing of Pekah. The Assyrian king claims to install Hoshea, but the broken royal signs do not permit the present archive to prove who personally killed Pekah. A restoration in a printed edition is not the same as an intact inscription."),
        ("Shalmaneser V: biblical name and missing siege annals",
         "Second Kings 17:3-6 and 18:9-10 both identify Shalmaneser V at the start of Assyrian action against Hoshea and Samaria. The University College London and ORACC specialist account of Shalmaneser V explains how few royal inscriptions survive from the brief reign. No directly preserved Assyrian royal inscription of Shalmaneser V documenting the Samaria siege has been entered here. His activity and possible new province are presented as historical reconstruction. This limits attempts to assign an exact final capture year or exclude the possibility of another royal action under Sargon II. Biblical dating and modern absolute-year chronologies should remain distinguished."),
        ("Sargon II and the independently attributed conquest claim",
         "RINAP 2, Sargon II 007 (Q006488), lines 23-25, is a palace display composition in which Sargon II explicitly claims a siege and capture of Samaria, the removal of inhabitants and an imposed Assyrian administration. The inscription is direct evidence of what Sargon presented about his achievements, not a time-stamped neutral siege log. It overlaps the biblical story of capture and exile but does not erase the earlier attribution of the siege to Shalmaneser V in Second Kings. One campaign, successive phases, and later imperial appropriation are differently argued possibilities. The evidence does not by itself prove which interpretation is historically decisive."),
        ("Exile totals are different across Assyrian copies",
         "The RINAP 2 edited display text Q006488 line 24 lists 27,290 Samarians removed, but the editor notes a variant 27,280 and an apparently attested 24,280 in other exemplars. The related Nimrud Prism Q006555 column iv lines 25-38 has a damaged number for which a reading of 47,280 has been proposed. The copies and compositions also differ in their reported chariot contingents. Second Kings 17:6 records deportation without supplying this figure. These exact-looking royal numbers must never be presented as a single securely established modern population census, and their textual variants should not be hidden from readers."),
        ("The province and relocated residents",
         "Second Kings 17:24 reports the settlement of other populations in Samaria after the removal of Israelites. Sargon II royal texts also present imperial resettlement and the appointment of officials. RINAP 2 Sargon II 001 (Q006482), lines 12-17, contains heavily restored passages whose editorial reconstruction uses parallel royal records. It is an informative secondary textual witness to the same imperial policy but is not an independent complete list of the places named by Kings. Restored phrases, historical campaign dates and named population transfers each need their own evidence. Neither royal self-presentation nor a biblical theological explanation should be misrepresented as a modern census.")
    ],
    ['bible-webbe','aebp-shalmaneser-v','aebp-sargon','rinap-tiglath-corpus','rinap-sargon-corpus','rinap-tiglath-menahem32','rinap-tiglath-peqah42','rinap-sargon-samaria7','rinap-sargon-nimrud74','rinap-sargon-annals1','aebp-israel','aebp-deportation'],
    ['bible-samaria','sargon-ii','shalmaneser-v','assyrian-deportations-texts'],
    [('2KI',15,19,20),('2KI',15,29,30),('2KI',17,3,6),('2KI',17,24,24),('2KI',18,9,12)],
    'The Shalmaneser V / Sargon II attribution is a historical question. No individual Assyrian royal inscription has yet been independently collated line by line to every biblical verse.'
)

add(
    'assyrian-deportations-texts',
    'Deportation in Kings, Chronicles and imperial records',
    'What biblical exile notices say, what Assyrian state policy explains and which human experiences the sources cannot recover.',
    [
        ('Israel and the east of the Jordan',
         '2 Kings 15:29 reports Tiglath-pileser taking northern places and carrying people away. 1 Chronicles 5:26 describes Reubenites, Gadites and the half-tribe of Manasseh taken into exile, using names for Assyrian kings that must be read carefully. These are primary biblical reports of specific movements; the language of carrying away does not itself supply a complete register of names, ages, occupations or local destinations.'),
        ('Samaria and population change',
         '2 Kings 17:6 associates the capture of Samaria with relocation to Halah, Habor, the river of Gozan and cities of the Medes. Verse 24 then describes groups settled in Samaria from other places. This is a biblical account of removal and replacement. The historical record of Assyrian population management is relevant comparison, but later administrative categories should not silently overwrite the wording or implied theological reading of Kings.'),
        ('Royal representations of resettlement',
         'RINAP 1 contains edited inscriptions associated with Tiglath-pileser III and Shalmaneser V. The Assyrian governance and deportation resources describe resettlement within an imperial administrative system. Kings could boast about captives, labour and the ability to reorder conquered territories. Such texts tell us about state policy and propaganda, but not necessarily the wishes, faith or later identity of each person moved.'),
        ('Objects, landscapes and captives',
         'The relief of Lachish prisoners, British Museum 124908, gives visual evidence that captives and seizure of goods featured in Assyrian royal representation. It belongs to Sennacherib\'s Judah campaign, not the earlier fall of Samaria. Comparing the imagery with an eighth-century biblical exile notice can illuminate imperial practice, but claiming both were one event would be an error. Distinct reigns, locations and documentary genres need separate labels.'),
        ('Limits of numbers and identity',
         'Royal inscriptions sometimes give exact-looking totals of people moved. Without an inscription identifier, the actual preserved text and an explanation of what was counted, those numbers should not be repeated as verified population statistics. The archive also avoids presenting modern Assyrian identity or any present-day community as a simple direct statistic derived from ancient deportation records. A serious history combines Bible passages, specific records and cautious interpretation.')
    ],
    ['bible-webbe','rinap-tiglath-corpus','rinap-tiglath-peqah42','rinap-sargon-samaria7','rinap-sargon-nimrud74','rinap-sargon-annals1','aebp-deportation','aebp-governance','bm-lachish-deportees','aebp-israel'],
    ['bible-deportation','samaria-assyrian-chronology','lachish-reliefs-context','assyrian-governance'],
    [('2KI',15,29,29),('1CH',5,26,26),('2KI',17,6,6),('2KI',17,24,24),('2KI',18,11,12)],
    'The Judah captives pictured at Lachish are a later, distinct event. Source roles and chronology are deliberately kept apart.'
)

add(
    'babylonian-chronicle-nineveh',
    'BM 21901: the Babylonian Chronicle and Nineveh\'s fall',
    'A particular cuneiform tablet brings the 612 BCE destruction into historical focus without collapsing Nahum into a court chronicle.',
    [
        ('Identify the tablet, not just the date',
         'The British Museum catalogues tablet 21901, accession 1896,0409.6, as a Babylonian Chronicle describing the years 616-609 BCE and the fall of Nineveh. Its catalogue dates the surviving clay copy to approximately 550-400 BCE, later than the events it narrates. An ancient copy of an earlier chronicle tradition is primary physical evidence for that transmitted text, but the age of the surviving tablet must not be confused with the narrated event date.'),
        ('The political setting of 612 BCE',
         'The chronicle is a Babylonian narrative concerning campaigns involving Babylonia, Median forces and Assyria. It provides an independently preserved chronological route for the destruction of Nineveh in 612 BCE and the struggles that followed. This does not automatically fix the precise boundaries of every surviving Assyrian province or identify the position of every army. The archive\'s historical atlas deliberately leaves uncertain terminal borders unmapped.'),
        ('Nahum names Nineveh',
         'Nahum 1:1 introduces an oracle concerning Nineveh. The following chapters use poetic images of siege, violence, judgment and the city\'s downfall. The Bible is primary for these prophetic pronouncements and their theological meaning. A Babylonian chronicle and a prophetic book can be studied in relation to the same ancient city, but poetry should not be treated as a verbatim eyewitness military diary or an automatic translation of the cuneiform account.'),
        ('Zephaniah and later memory',
         'Zephaniah 2:13-15 also speaks against Assyria and Nineveh and portrays the city as desolate. The biblical prophetic texts together create a rich literary witness to judgment and political upheaval. The chronicle supports the historical setting of Assyria\'s imperial crisis, not the proposition that every detail of prophetic imagery appears literally in administrative records. Reading genre and historical subject together keeps both testimony and differences visible.'),
        ('What remains to check',
         'For precise chronology, retain the accession number, the copy date, the dated events and the specific preserved lines in a published edition. BM 21901 provides a stable object route; a future specialist comparison should collate the tablet\'s original-language line divisions with named translations and the passages in Nahum and Zephaniah. Source citation and plausible context are not yet an independent philological review.')
    ],
    ['bible-webbe','bm-chronicle','met-levant-chronology','met-nineveh-history'],
    ['fall-of-nineveh','bible-nahum','bible-zephaniah','historical-evidence-methods'],
    [('NAH',1,1,15),('NAH',2,1,13),('NAH',3,1,19),('ZEP',2,13,15)],
    'The British Museum object record dates the surviving tablet several generations later than the events recorded. This distinction is central to its evidential use.'
)

add(
    'historical-evidence-methods',
    'How to compare Scripture, inscriptions and royal art',
    'A worked research protocol for handling dates, translation, ancient source genres and agreement without inventing certainty.',
    [
        ('Begin by defining the exact claim',
         'A statement that 2 Kings 18:13 reports an attack on Judah is a claim about the wording of Scripture. A statement that a particular prism was inscribed in 691 BCE is an object catalogue claim. A statement that every event of 2 Kings 19 is independently corroborated requires a much stronger evidential demonstration. Distinguish what the Bible asserts, what an external object preserves and what a modern scholar infers before putting them into a single paragraph.'),
        ('Separate the four clocks',
         'A single dossier can contain a date for an ancient event, the year a royal text was composed, the archaeological or manuscript copy date, and a modern museum cataloguing date. The Judah campaign associated with 701 BCE appears on prisms made in later years. Likewise the British Museum\'s surviving Babylonian Chronicle tablet was made after 612 BCE, the year of Nineveh\'s fall. None of those distinct clocks should be silently swapped for another.'),
        ('Name the document and its genre',
         'A palace relief, royal annal, chronicle, administrative letter, oracle and narrative history are all real source types, but they answer different questions. The Black Obelisk constructs a scene of tribute; the Lachish panels depict siege and captives; Isaiah 20 gives a prophetic sign; 2 Kings provides narrative and theological history. Document type shapes the selection of events, point of view and silences. A comparative account must make that visible.'),
        ('Keep translation and preservation visible',
         'For an inscription, identify a museum accession, ORACC edition or exact tablet number where possible. Record signs and line breaks that are missing, restored or uncertain before making close verbal parallels to a Bible translation. For Scripture, give the book, chapter and verse and specify which translation is being read. A secondary article linking to the correct corpus is a research route, not proof that the author of the archive has personally checked each preserved cuneiform line.'),
        ('Record what agrees and what remains open',
         'The most valuable result is often narrow: independent ancient records describe Sennacherib and Judah, and the Bible also narrates the Assyrian attack. Other reported events, speeches, tribute amounts, miraculous acts and the king\'s motives are separate claims. The archive should show evidence roles and limitations for each, with claims kept in the independent-review queue until a qualified person reviews and documents them. Identifying an overlap makes research stronger without turning the whole narrative into an unexamined equivalence.')
    ],
    ['bible-webbe','oracc-rinap','bm-taylor-prism','imj-sennacherib-prism','bm-chronicle','bm-black-obelisk','bm-lachish-panel'],
    ['research-guide','sennacherib-prism-hezekiah','babylonian-chronicle-nineveh','black-obelisk-jehu'],
    [('2KI',18,13,16),('2KI',19,1,37),('ISA',20,1,6),('NAH',1,1,15)],
    'Method guide, not a claim of completed independent historical, biblical or philological review.'
)
