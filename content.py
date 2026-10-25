"""Original editorial introductions for the Assyria foundation edition."""
ARTICLES = []
def add(slug, title, category, summary, sections, sources, related=(), image=None, note=None):
    ARTICLES.append(dict(slug=slug,title=title,category=category,summary=summary,sections=[dict(title=t,text=p) for t,p in sections],sources=sources,related=list(related),image=image,note=note))

add('assyrian-identity','Understanding Assyrian identity','People & diaspora',
'A starting point for understanding a people through language, memory, community and the names people use for themselves.',[
('A living identity','This archive centres Assyrian history and living culture. Its scope includes ancient Assyria, Aramaic-speaking communities, Syriac literary heritage and modern people who identify as Assyrian. These subjects overlap, but each needs its own historical context. A palace inscription, a medieval hymn and a modern migration interview answer different kinds of questions.'),
('Names deserve care','Assyrian, Chaldean, Syriac and Aramean appear in different ethnic, linguistic and ecclesiastical settings. Individuals and institutions do not all use these names in the same way. The archive follows the self-description of a person or organisation when discussing them. A church name alone cannot establish an individual\'s ethnic identification. Likewise, the fact that someone speaks an Aramaic variety does not automatically make them Assyrian.'),
('How to read the evidence','For ancient political history, begin with archaeological and textual scholarship. For language, use specialist linguistic descriptions and recordings. For modern life, add oral histories and community institutions. Sophia Kanna\'s Australian migration account, for example, records one Assyrian family experience; it is valuable testimony without being a census of the whole diaspora. This combination gives a richer account than making one type of evidence stand for every period.'),
('Questions still to develop','The foundation edition does not settle debates about the historical development of modern national consciousness or every competing interpretation of continuity. Those require dedicated articles, named scholarly positions and a wider bibliography. Future contributions should state the period, place, community and source behind each claim.')],
['modern-kanna','modern-aaa','modern-chaldean','gedsh-aramaic'],['australia','faith-and-churches','aramaic'],note='Editorial overview. Self-designations vary; this article does not impose one identity on all related communities.')

add('ancient-assyria','Ancient Assyria','History & archaeology',
'From a city on the Tigris to a major imperial power: an introduction to the places, periods and evidence.',[
('Begin with Ashur','Assyria developed in northern Mesopotamia, with the city of Ashur as a central religious and political reference point. Its history covers changing institutions and territories over many centuries. The Old, Middle and Neo-Assyrian labels are scholarly period divisions; they should not suggest that the same imperial boundaries existed throughout.'),
('Trade before the great palaces','Old Assyrian merchants operating in Anatolia in the early second millennium BCE left written accounts of trade, credit, travel and family affairs. Their tablets illuminate the practical work behind long-distance exchange. They offer a useful counterweight to the much later royal monuments that dominate popular images of Assyria.'),
('The imperial centuries','Assyria expanded in the Middle Assyrian period and again in the ninth to seventh centuries BCE. Rulers constructed major capitals at Kalhu, Dur-Sharrukin and Nineveh. Monumental art proclaimed royal authority, while inscriptions presented campaigns and building works in the king\'s preferred terms. These are important primary sources, but their political purpose matters when assessing what they tell us.'),
('After the empire','The late seventh-century BCE collapse of Assyrian imperial power marks a political transformation. It should not be treated as proof that every local population or cultural practice disappeared. Ashur itself experienced later occupation, including a Parthian revival. Studying subsequent centuries requires their own evidence rather than filling the interval with assumptions.'),
('A route through the archive','Read the city entries for geography, the trade article for everyday documents, and the art entries for visual interpretation. Keep a distinction between an artefact\'s ancient setting, its modern excavation and its later museum history. The full story includes all three.')],
['met-assyria','met-caravan','unesco-ashur','met-court'],['ashur','old-assyrian-trade','nimrud','nineveh'],image='relief',note='Introductory synthesis. Ancient chronology can vary between scholarly systems; dates are approximate where indicated.')

add('ashur','Ashur: city, sanctuary and crossroads','Places & heritage',
'The Tigris city at the heart of Assyrian political and religious life.',[
('On the Tigris','Ashur, also written Assur or Aššur, is the archaeological site known as Qal\'at Sherqat in present-day Iraq. UNESCO dates the city to the third millennium BCE and describes its setting near the transition between rain-fed and irrigated agriculture.'),
('More than a capital','Ashur was an important trading centre and the religious centre associated with the god Ashur. A city\'s religious significance could endure after a ruler moved the court elsewhere. The city therefore belongs in histories of commerce and ritual as well as accounts of kingship.'),
('A site with several lives','The site\'s history extends beyond the Assyrian imperial period. UNESCO records a revival under the Parthians. Archaeological layers must be dated and interpreted individually: a later building cannot automatically be read as evidence of an unchanged earlier institution. For conservation information, consult UNESCO\'s dated reports rather than assuming the site\'s condition is static.')],
['unesco-ashur'],['ancient-assyria','old-assyrian-trade','heritage-stewardship'])

add('old-assyrian-trade','Merchants, caravans and clay tablets','History & archaeology',
'Commercial records open a window onto travel, enterprise and family life in the Old Assyrian world.',[
('A trading network','In the early second millennium BCE, merchants from Ashur established settlements in Anatolia. Tin and textiles travelled through these networks in exchange for precious metals. Surviving tablets record investments, expenditure, loans and disputes as well as correspondence.'),
('Read a real document','The Met\'s caravan account, object 66.245.10, is a concrete starting point. Its record connects an individual clay object to the logistics of moving goods. A catalogue description is useful, but a full historical argument also requires a text edition, translation and the tablet\'s archaeological context.'),
('A different Assyrian world','These commercial archives predate the great Neo-Assyrian palace reliefs by many centuries. Reading them together is rewarding precisely because their social settings differ. The archive will expand this topic through individual documents, named merchants and the roles of women in family correspondence, using specialist editions.')],
['met-caravan'],['akkadian-and-cuneiform','ancient-assyria','research-guide'])

add('nimrud','Nimrud, ancient Kalhu','Places & heritage',
'A royal capital whose architecture and sculpture shaped the visual language of Assyrian kingship.',[
('A capital rebuilt','Ashurnasirpal II, who reigned approximately 883-859 BCE, made Kalhu a major royal capital. The site is widely known today as Nimrud. The palace sculptures now held in museums originally formed parts of architectural spaces, rather than independent pictures.'),
('Reconstructing a setting','The Met\'s Assyrian Sculpture Court evokes a palace setting while explicitly acknowledging that it is not a full reconstruction. Its reliefs originated in multiple rooms. That distinction helps visitors separate a modern display from a securely known ancient arrangement.'),
('Look closely','Observe changes in scale, repeated figures, patterned clothing and the relationship between carved imagery and inscriptions. Then ask where a panel stood and who could see it. Those contextual questions are as valuable as identifying the king or protective figure.')],
['met-court','met-lion'],['lamassu','royal-reliefs','ancient-assyria'],image='relief')

add('khorsabad','Dur-Sharrukin and Khorsabad','Places & heritage',
'Sargon II\'s planned royal city, known through its remains, excavations and monumental guardians.',[
('A royal foundation','Dur-Sharrukin, at modern Khorsabad, was built as a capital by Sargon II. It was a short-lived centre of royal power. The French Ministry of Culture\'s archaeological resource introduces the site, its palace and its excavation history.'),
('Ancient city, modern discoveries','Paul-Emile Botta began major excavations at Khorsabad in 1843. Excavation records are part of the evidence, but nineteenth-century discovery narratives should be read alongside the history of the place and its local communities.'),
('What needs further study','A complete entry should distinguish the original city plan, surviving archaeology, reconstructed architecture and objects dispersed among collections. Museum photographs alone cannot establish a palace\'s complete appearance. This introduction links to specialist material rather than presenting an imagined reconstruction as fact.')],
['khorsabad-ministry'],['nimrud','lamassu','heritage-stewardship'])

add('nineveh','Nineveh and the library of Ashurbanipal','History & archaeology',
'Royal collections of clay tablets reveal a wider world of scholarship, copying and commentary.',[
('A city of collected knowledge','Nineveh housed the royal scholarly collections associated with Ashurbanipal. Their tablets are central to the study of ancient Mesopotamian learning. The phrase "library of Ashurbanipal" is useful, but should not imply a modern public lending library.'),
('Part of a larger network','Yale\'s Cuneiform Commentaries Project distinguishes temple, palace and private collections across several Mesopotamian cities. Nineveh\'s collections belonged within this wider scholarly landscape. Calling them the world\'s first library would erase earlier and parallel traditions.'),
('Reading tablets today','Researchers compare manuscripts, identify joins between fragments and interpret texts with attention to copying and commentary. CDLI offers catalogue and text resources across cuneiform cultures. A digital record is a route into the evidence, rather than permission to reproduce every photograph or translation associated with it.')],
['yale-libraries','cdli'],['akkadian-and-cuneiform','research-guide','ancient-assyria'])

add('lamassu','Lamassu: guardians in stone','Arts & traditions',
'Human heads, powerful bodies and wings: the monumental figures at Assyrian palace thresholds.',[
('Protection and presence','Assyrian lamassu combined a human head with a winged bull or lion body. They stood at important palace entrances as protective figures. The Met\'s human-headed winged lion from Nimrud dates to approximately 883-859 BCE and is carved from gypsum alabaster.'),
('Why five legs?','Some monumental examples have five legs. Seen from the front they appear firmly planted; seen from the side they seem to stride. This solution responds to a visitor moving past a doorway. It is a useful reminder to read monumental sculpture through viewpoint and architecture.'),
('Ancient object, contemporary meaning','A lamassu may now function as a cultural emblem, an artistic reference or an image of heritage. Those contemporary uses deserve documentation in their own right. They should be distinguished from what an individual ancient sculpture\'s context supports. The photographs in this archive identify the actual museum object and its licence.')],
['met-lion','met-lamassu'],['nimrud','royal-reliefs','heritage-stewardship'],image='lamassu')

add('royal-reliefs','Reading Assyrian palace art','Arts & traditions',
'Reliefs preserve extraordinary craftsmanship and carefully constructed statements about power.',[
('Art within architecture','Assyrian stone panels formed parts of palace interiors. Their scale, arrangement and proximity to thresholds affected how they were experienced. Museum installations can help evoke this relationship, while remaining modern interpretations.'),
('Ask who is speaking','Royal imagery is not a neutral photographic record. A ruler commissioned images to represent authority, ritual or military success. Read scenes alongside inscriptions, archaeological context and independent evidence before drawing conclusions about a particular event.'),
('A practical looking guide','Begin with material and object provenance. Note the figure\'s posture, dress, gestures and repeated motifs. Check which elements a museum identifies confidently and which remain interpretations. Further articles should explore individual works, workshop practices, colour and the histories of excavation and collecting.')],
['met-court','met-assyria','met-relief'],['nimrud','lamassu','research-guide'],image='relief')

add('akkadian-and-cuneiform','Akkadian and cuneiform','Language & literature',
'A language and a writing system are different things. This distinction unlocks the ancient evidence.',[
('Language versus script','Akkadian is an ancient Semitic language; Assyrian and Babylonian are conventionally treated as its varieties. Cuneiform is a writing system used for more than one language. A tablet written with wedge-shaped signs is therefore not automatically an Assyrian text.'),
('Finding texts','CDLI provides records, images and textual resources for cuneiform inscriptions across periods and languages. Search by object, collection and linguistic attribution where available. A transliteration represents the signs in scholarly notation; a translation interprets their meaning in another language.'),
('The modern-language distinction','Modern Assyrian Neo-Aramaic belongs within Aramaic. It should not be described as present-day spoken Akkadian. Contact, historical memory and cultural inheritance are different questions from a language\'s linguistic classification. Follow the Aramaic and Sureth articles for the living-language side of the story.')],
['cambridge-mesopotamian-languages','cdli','gedsh-aramaic'],['aramaic','old-assyrian-trade','nineveh'])

add('aramaic','Aramaic: a family of histories','Language & literature',
'A broad linguistic tradition with many historical forms and modern speaker communities.',[
('One label, many varieties','Aramaic is a Northwest Semitic language tradition with a long and varied history. The name covers forms used in different regions, periods and communities. It does not designate one unchanged language shared identically by every speaker across time.'),
('Syriac and living speech','Classical Syriac is an important literary and liturgical Aramaic variety. Modern Neo-Aramaic includes several distinct groups and local varieties. Cambridge\'s NENA project documents North-Eastern varieties, including those historically spoken by Christian and Jewish communities. Surayt, associated with Tur Abdin, needs its own description.'),
('Choose a learning route','Before selecting a course, identify the goal: reading Classical Syriac, speaking a family\'s local variety or studying a particular regional standard. Record the teacher\'s terminology and pronunciation tradition. Materials aimed at one goal may be valuable without being interchangeable with materials for another.'),
('What the archive will preserve','Future language entries should pair writing with native-speaker recordings, named local varieties and a clear transliteration key. The foundation edition links to documented external resources. It does not generate unreviewed pronunciation audio or claim that a short word list represents every community.')],
['gedsh-aramaic','gedsh-syriac','cambridge-nena','gedsh-turoyo'],['classical-syriac','sureth','surayt','endangered-languages'])

add('classical-syriac','Classical Syriac','Language & literature',
'The literary and liturgical language of a wide intellectual and religious heritage.',[
('Origins and reach','Syriac is an Aramaic variety associated in its origins with Edessa, modern Urfa. It developed a large literary tradition, including prose, poetry and translations. Its texts preserve much more than ecclesiastical history: they also inform political, intellectual and cultural research.'),
('A literary tradition','The fourth to seventh centuries were especially productive in Syriac literature. Manuscripts and later copies transmit works across many periods. The date of a physical manuscript and the date of the text it contains may be centuries apart.'),
('Reading today','Classical Syriac continues in literary and liturgical use alongside living Neo-Aramaic varieties. Learning to read it requires attention to grammar, vocalisation and script tradition. The manuscript and script guides point to specialist teaching resources; the sources remain the place for fuller linguistic description.')],
['gedsh-syriac','syriaca-intro'],['syriac-scripts','manuscripts','ephrem'])

add('sureth','Sureth and North-Eastern Neo-Aramaic','Language & literature',
'Living speech, regional variation and literary practice across related communities.',[
('A name with local meanings','Sureth is used for several North-Eastern Neo-Aramaic varieties, especially in northern Iraq. Its exact scope varies between speakers and publications. A responsible word list should say whose variety it records rather than presenting one form as universal.'),
('Written and spoken heritage','The GEDSH entry describes literary use attested from the late sixteenth century and discusses religious poems and recorded wedding songs. The history of writing is one part of the picture; everyday speech and oral performance require their own records.'),
('Listen to documented voices','Cambridge\'s NENA project offers recorded material and descriptions organised by dialect. Such resources help readers encounter actual variation. When comparing vocabulary, preserve the locality, speaker context and transcription system supplied by the documentation project.')],
['gedsh-sureth','cambridge-nena'],['aramaic','endangered-languages','oral-history'])

add('surayt','Surayt, also known as Turoyo','Language & literature',
'A modern Aramaic tradition associated with Tur Abdin and its diaspora.',[
('Place and language','Surayt, often called Turoyo in scholarship, is associated with Tur Abdin. It has its own linguistic and literary history and should not be reduced to a generic version of Sureth.'),
('A growing written life','The GEDSH account describes wider written use in the second half of the twentieth century, including diaspora publications and writing for children. Literary development and spoken tradition belong together; a relatively recent print history does not make a spoken language new.'),
('A course to explore','Freie Universitat Berlin announced the advanced SLOMO SURAYT course in 2020. Its online learning materials include grammar, texts and a glossary. Follow the university\'s project link to the course and review its terms before reproducing any exercises. Free learning access is different from an unrestricted content licence.')],
['gedsh-turoyo','fu-surayt'],['aramaic','syriac-scripts','endangered-languages'])

add('syriac-scripts','Syriac scripts and the written word','Language & literature',
'Estrangela, Serto and East Syriac are writing traditions with histories of use and adaptation.',[
('Recognising the traditions','HMML School introduces Estrangela, Serto and East Syriac through manuscript examples. Letter forms, vowel marks and scribal practices vary. Script labels describe writing traditions; they do not provide a rigid test of ethnicity.'),
('A script can cross languages','Syriac script has also been used for non-Aramaic languages. Garshuni, in the teaching resource linked here, describes Arabic written using Syriac letters. This is another reason to keep script and language separate.'),
('Reading responsibly','A beautiful letterform is not enough to establish a correct transcription. Check orientation, joining, vowel marks and the manuscript\'s hand. Future alphabet lessons in this archive will need a stated tradition and specialist review. For now, HMML\'s palaeography lessons provide a stronger foundation than an unattributed alphabet graphic.')],
['hmml-palaeography'],['classical-syriac','manuscripts','surayt'])

add('manuscripts','Manuscripts and digital collections','Language & literature',
'A guide to finding texts, understanding catalogue records and respecting collection rights.',[
('More than religious books','Syriac manuscript collections include scripture and hymns alongside grammar, dictionaries, philosophy and natural history. The John Rylands collection at Manchester offers an institutional starting point, with holdings spanning many centuries.'),
('Distributed heritage','HMML\'s Voobus collection documents manuscripts from several countries. The syri.ac discovery guide points to digitised material held across institutions. No single portal contains every surviving manuscript, and a catalogue record does not mean that every page is digitised or openly downloadable.'),
('How to cite a manuscript','Record the holding institution, collection, shelfmark, folio or page, catalogue URL and access date. Distinguish the manuscript\'s copying date from the composition date of its contents. Check image rights independently from the copyright status of the ancient text.'),
('Books, archives and modern scholarship','eBethArke, developed by Beth Mardutho and Rutgers, brings together printed books, manuscripts, recordings and other resources. Its range is a reminder that digital preservation covers modern intellectual life as well as ancient and medieval material.')],
['manchester-syriac','hmml-voobus','syriac-digimss','rutgers-ebetharke'],['classical-syriac','syriac-scripts','research-guide'])

add('ephrem','Ephrem: poetry and theology','People & diaspora',
'A fourth-century writer whose hymns remain central to the study of Syriac literature.',[
('A documented literary figure','Ephrem, who died in 373 CE, was a deacon, poet and theologian associated with Nisibis and later Edessa. His works include hymns, metrical homilies, prose and biblical commentary. The scholarly GEDSH entry is the starting point used here.'),
('Read the works with care','Later authors attributed additional works to Ephrem, and later biographical traditions are not all reliable evidence for his life. An article about him should distinguish securely attributed writing from uncertain or pseudonymous material.'),
('Where to go next','A fuller treatment can examine an individual hymn through an identified edition and translation, then place its imagery within its theological and literary setting. Modern translations have their own copyright. This introduction links to scholarship rather than reproducing a complete translated hymn.')],
['gedsh-ephrem'],['classical-syriac','manuscripts','faith-and-churches'])

add('faith-and-churches','Faith and the Syriac Christian traditions','Faith & communities',
'A guide to related churches, shared literary inheritances and distinct institutional histories.',[
('A shared field, distinct churches','Assyrian cultural history overlaps with several Syriac Christian traditions. The Assyrian Church of the East, Chaldean Catholic Church and Syriac Orthodox Church have distinct institutional identities. This introductory selection is not a complete directory of every church or every community within the archive\'s scope.'),
('Tradition and historical evidence','Churches may describe their origins through apostolic tradition. That is important evidence of ecclesiastical self-understanding. It should be identified as tradition when it is different from the earliest surviving written documentation. The Assyrian Church\'s Australian account itself distinguishes its traditional foundation from written records traced to the late second century.'),
('Ethnicity is a separate question','Religious affiliation does not determine every member\'s ethnic identification. Use individuals\' preferred names and avoid turning a church history into a verdict on all related identities. Equally, people can participate in Assyrian cultural life without sharing one denomination or religious practice.'),
('How the archive will expand','Future church entries should separate doctrine, liturgy, architecture, institutional chronology and local parish life. Official sources are valuable for self-description; comparative scholarship is necessary for contested historical interpretation. Clergy directories, service times and leadership information need current verification before publication.')],
['modern-acoe','modern-chaldean','modern-syriac-constitution','gedsh-syriac'],['church-of-the-east','chaldean-church','syriac-orthodox','assyrian-identity'])

add('church-of-the-east','The Assyrian Church of the East','Faith & communities',
'An introduction through the church\'s own account of its historical and Syriac heritage.',[
('A first-party account','The Australian church\'s historical overview describes development under Parthian and Persian rule and identifies Syriac as its traditional ecclesiastical language. Its story belongs within a wider history of Christianity east of the Roman frontier.'),
('Foundations and evidence','The church traces its foundation to apostolic activity while noting written records from the late second century. The archive preserves that distinction rather than presenting a traditional first-century date as an independently demonstrated event.'),
('Further coverage','A full treatment needs scholarship on theology, liturgy, missions, institutions and modern history. The foundation edition avoids time-sensitive claims about leadership or parish schedules. Follow the official church source for its own descriptions and current institutional information.')],
['modern-acoe'],['faith-and-churches','chaldean-church','classical-syriac'])

add('chaldean-church','The Chaldean Catholic Church','Faith & communities',
'A distinct Catholic church within the wider heritage of the Church of the East.',[
('Institutional heritage','The Chaldean Diocese of St. Thomas the Apostle situates the Chaldean Catholic Church within the patrimony of the Church of the East. CNEWA supplies a further Catholic institutional overview of its history and Syriac liturgical context.'),
('Related histories','These accounts help readers understand relationships between churches without erasing distinct institutions. CNEWA also discusses the 1994 common Christological declaration and improved relations with the Assyrian Church of the East.'),
('Names and identity','"Chaldean" can appear in ecclesiastical and ethnic contexts. This article describes the church; it does not assume that every member uses the same ethnic self-description. Future coverage should include community voices alongside comparative historical scholarship.')],
['modern-chaldean','modern-chaldean-history'],['faith-and-churches','church-of-the-east','assyrian-identity'])

add('syriac-orthodox','The Syriac Orthodox Church','Faith & communities',
'A West Syriac Christian tradition with its own institutional and cultural heritage.',[
('An official self-description','The constitutional document provided by the Syriac Orthodox Patriarchate\'s Department of Syriac Studies uses the Syrian/Syriac Orthodox designation and describes the patriarch\'s institutional authority. It is a first-party source for the church\'s organisation.'),
('Language and writing','The wider West Syriac tradition includes distinctive script and pronunciation practices described in specialist Syriac language resources. These are linguistic and liturgical categories; they should not be turned into fixed ethnic boundaries.'),
('Scope of this entry','A full history of the church requires more than a constitutional document. Later stages should add comparative scholarship on theology, monasteries, architecture and regional communities. Apostolic foundation traditions should be attributed as traditions, and ethnic self-designations should be recorded with care.')],
['modern-syriac-constitution','gedsh-syriac'],['faith-and-churches','surayt','syriac-scripts'])

add('akitu','Akitu and Kha b-Nisan','Arts & traditions',
'New Year celebrations as a meeting place for heritage, music, food and community.',[
('A living celebration','Modern Assyrian New Year celebrations, often called Akitu or Kha b-Nisan, bring people together in homeland and diaspora settings. SBS Assyrian\'s reporting documents festivals that combine performance, books, food, art and community organisations.'),
('Ancient references, modern practice','Contemporary celebrations draw meaning from ancient Mesopotamian heritage. That connection should not be expanded into a claim that every ritual, date or calendar reckoning has continued unchanged since antiquity. Ancient festival practices and modern cultural renewal need their own evidence.'),
('Documenting an event','A useful festival record identifies the year, organiser, place, performers and community voices. The Sydney event linked below is historical reporting, not a current event listing. Future coverage can build a dated festival archive, with photographs and recordings used only with appropriate permissions.')],
['modern-akitu','modern-festival-sydney'],['dance','music','kileche'])

add('dance','Khigga and Assyrian dance','Arts & traditions',
'Shared steps, regional styles and the social life of dancing together.',[
('A practice carried by people','Dance is an active part of Assyrian cultural life at celebrations and community performances. The Assyrian Student Association of Arizona\'s Akitu Dance Crew describes workshops and names several dances, including Khigga Yaqoora, Gubare, Sheikhani and Bablaka.'),
('Variation matters','Dance names, spelling, tempo and steps can vary by region, teacher and performance context. A staged choreography is not necessarily identical to the way a family dances at a wedding. Each recorded example should identify the performers and setting.'),
('Learning and preservation','The best future dance entries will combine a practitioner\'s explanation with permission-cleared video, a named variation and musical context. Modern practice does not need an unprovable ancient date to be culturally meaningful. This introduction avoids claims that a particular sequence of steps has survived unchanged for millennia.')],
['modern-dance'],['akitu','music','oral-history'],image='khigga')

add('kileche','Kileche and the family table','Arts & traditions',
'Food offers a way into family memory, celebration and everyday cultural knowledge.',[
('A family account','Evan Yako\'s SBS Food feature presents kileche, Assyrian cookies, through his relationship with his mother Helen and the transmission of family food knowledge. It connects a recipe to a particular person\'s experience rather than treating food as an anonymous list of ingredients.'),
('Many versions can belong','Names, fillings, shapes and methods may differ between households and regions. A useful food archive records whose recipe it is, where they learnt it and when it is made. One family\'s version need not be declared the only authentic one.'),
('From link to cultural record','The original recipe remains on SBS. This archive does not reproduce its complete directions. Future contributions could pair a contributor-owned recipe with photographs, an interview and permission for publication, allowing cooking knowledge to be preserved alongside the story of the person who shares it.')],
['modern-kileche'],['oral-history','akitu','australia'])

add('music','Music, voice and cultural memory','Arts & traditions',
'Songs and performances connect language, public life and personal experience.',[
('Begin with listening','Assyrian music deserves coverage across artists, regions, genres and generations. SBS Assyrian offers interviews and audio programming that can help listeners encounter contemporary voices. Its Evin Agassi memorial reporting also documents how community members describe the significance of a musician.'),
('Build a careful discography','A reliable artist entry should identify recordings, credited writers and performers, release evidence and the source of biographical details. A fan upload can be a discovery lead, but its title and date are not automatically a verified discography.'),
('Preserve with permission','Lyrics, commercial recordings, cover art and videos usually have separate rights. The archive links to legitimate sources rather than copying complete songs or lyrics. Later stages can add authorised interviews, documented listening guides and artist-approved material.')],
['modern-radio','modern-agassi'],['evin-agassi','dance','endangered-languages'])

add('evin-agassi','Evin Agassi: a community remembers','People & diaspora',
'A starting point for documenting an influential musical voice through community testimony.',[
('A memorial record','SBS Assyrian reported on a memorial for Evin Agassi in Greenfield Park, Sydney, held on 22 September 2024. The report draws on attendance and community tributes. It offers evidence for how people remembered his music and its cultural meaning.'),
('Reception is part of history','Accounts of a musician should include listeners, migration settings and language as well as a list of recordings. Memorial testimony is valuable evidence of reception, while remaining different from an independently checked account of every event in an artist\'s life.'),
('A biography to develop','This is not a complete biography or discography. Future work should verify release details, credits and life dates against multiple reliable records, and seek permission for photographs and recordings. Where sources disagree, the archive should report the disagreement rather than silently select a convenient number.')],
['modern-agassi'],['music','australia','oral-history'])

add('oral-history','Oral histories: voices worth preserving','People & diaspora',
'Personal testimony brings migration, language and everyday life into the historical record.',[
('A voice in the archive','The NSW Migration Heritage Centre\'s interview with Sophia Kanna records her Assyrian background, her connection to Habbaniyah and her arrival in Sydney on 27 May 1964. It offers a specific account of home, work and language across migration.'),
('Memory and evidence','An oral history tells us what a person remembers and how they understand their experience. It can be checked against documents without losing the value of the speaker\'s perspective. Broad historical claims made during an interview still need independent evidence.'),
('A contribution method','For a future interview, record consent, the preferred display name, interview date, languages used and any access restrictions. Preserve the original recording and a transcript separately. Ask about places, objects, songs and ordinary routines as well as major events. Contributors should be able to discuss privacy before anything becomes public.')],
['modern-kanna'],['australia','assyrian-identity','endangered-languages'])

add('australia','Assyrian life in Australia','People & diaspora',
'Migration stories, language education and community institutions offer a grounded introduction.',[
('Start with a person','Sophia Kanna\'s archived migration history records her arrival in Sydney in 1964. Her account provides one route into the experience of building a life in Australia. It should not be treated as the single story of all Assyrian migration.'),
('Community institutions','The Assyrian Australian Association dates its establishment to 1969. Its account describes language education, scholarships, settlement work and cultural events. Its Resource Centre records establishment in 1984 in response to settlement needs around Fairfield and Liverpool.'),
('A wider picture to build','A fuller Australian section needs histories from multiple cities and generations, women\'s experiences, schools, arts, work, sport and public life. This edition does not publish an unsourced population total. Later demographic entries should specify census year, geography and the exact ancestry or language category being counted.')],
['modern-kanna','modern-aaa','modern-arc'],['assyrian-australian-association','oral-history','akitu'])

add('assyrian-australian-association','Assyrian Australian Association','People & diaspora',
'A community institution whose history illustrates the work of cultural and settlement support.',[
('An institutional history','The Assyrian Australian Association says it was founded in 1969. Its first-party history describes work spanning cultural events, language schools, scholarships and settlement support. These activities connect cultural transmission with the practical needs of a diaspora community.'),
('The Resource Centre','The association dates the Assyrian Resource Centre to 1984, established in response to needs in Fairfield and Liverpool. The linked source is the appropriate place to check its own account of services.'),
('Using this record','This entry is an introduction to the organisation, not an endorsement or a live service directory. Eligibility, programme availability and contact arrangements may change. Future institutional profiles should include dated records and preserve changes over time without turning old web copy into current advice.')],
['modern-aaa','modern-arc'],['australia','oral-history','assyrian-identity'])

add('simele','Simele, 1933','History & archaeology',
'An introduction to the massacre, its remembrance and the need for careful historical documentation.',[
('The historical subject','Assyrians were killed during the Iraqi military campaign of August 1933 in northern Iraq, including at Simele. The event occupies an important place in modern Assyrian historical memory. Assyrian Martyrs Day is observed on 7 August.'),
('Know the source type','The Assyrian Studies Association\'s 2020 letter calls for protection and impartial investigation of the site. The Assyrian Policy Institute\'s page presents a community advocacy perspective. These are useful sources for commemoration and preservation concerns, but an appeal is not a completed forensic investigation.'),
('What this edition does not settle','The archive does not publish a single casualty figure from these sources as a settled total. A full article needs comparative historical scholarship, contemporary records and explicit treatment of disputed estimates. Recognition and site-protection status also require dated verification; older campaign pages should not be presented as current policy.')],
['modern-simele-asa','modern-simele-api'],['sayfo','oral-history','heritage-stewardship'],note='Sensitive history. This foundation entry is limited in scope and requires a broader historical bibliography before expansion.')

add('sayfo','Sayfo and the First World War','History & archaeology',
'A research entry on mass violence against Assyrian, Syriac and Chaldean Christian communities.',[
('A field of historical research','The academic volume Let Them Not Return examines violence against Assyrian, Syriac and Chaldean Christians during and after the First World War, across borderland regions now in Turkey, Iran and Iraq. Sayfo is a central term in the study and remembrance of this history.'),
('Scholarship and testimony','The annotated source published as Sayfo - An Account of the Assyrian Genocide presents an eyewitness narrative associated with greater Tur Abdin. Eyewitness accounts preserve essential perspectives; they should be contextualised through location, date, authorship and comparison with other evidence.'),
('A careful expansion','This entry avoids an unsupported single casualty total and does not imply every region experienced identical events. A full treatment should distinguish local chronologies, survivor histories, displacement and later commemoration. The linked public catalogue descriptions are accessible, while access to complete books can vary. They are not marked here as freely licensed full texts.')],
['modern-sayfo','modern-sayfo-eyewitness'],['simele','oral-history','research-guide'],note='Sensitive history. Public book descriptions were consulted; this introduction does not claim a full review of the volumes.')

add('endangered-languages','Keeping living languages audible','Language & literature',
'Documentation, teaching and everyday use each play a role in language continuity.',[
('A documented need','Cambridge\'s NENA project describes the dialects it documents as highly endangered. It makes linguistic material available to researchers and speaker communities. The diversity within those records matters: saving a generic label is not the same as preserving a local variety.'),
('Record context as well as words','A useful recording includes the language variety, speaker\'s consent, date, place and the circumstances of the conversation. Stories, conversation and explanations of daily tasks can preserve forms that a vocabulary list misses. A transcription and translation make the recording easier to study.'),
('Teaching is another task','An archive can support learning but does not replace opportunities to speak. Match learners with materials for their intended variety, including the free Surayt course where appropriate. Future audio in this hub should come from consenting speakers and be reviewed for transcription and pronunciation.')],
['cambridge-nena','fu-surayt'],['sureth','surayt','oral-history'])

add('research-guide','How to research Assyrian history','Language & literature',
'A practical path from an interesting claim to evidence that another reader can check.',[
('Ask a precise question','Specify a person, place, language variety or period. "What does this tablet record?" is easier to investigate than a claim about an entire civilisation. Begin with a specialist overview, then follow its references to editions, catalogues and primary material.'),
('Choose the right collection','CDLI is useful for cuneiform records. Syriaca provides a reference portal for Syriac studies. syri.ac points to distributed manuscript resources, while eBethArke includes books, archives and recordings. These collections overlap without being interchangeable.'),
('Keep an evidence trail','Record author, title, publication date, stable URL and the page, folio or object identifier behind a claim. Distinguish a source\'s own words from your interpretation. If a translation or identification is disputed, name the alternatives and explain the basis.'),
('Access is not a licence','A page being readable does not make its text, images or recordings free to copy. Summarise in original language, link to the source and check reuse conditions for each asset. The source library records public discovery routes without promising unrestricted access to every underlying work.')],
['cdli','syriaca-intro','syriac-digimss','rutgers-ebetharke'],['manuscripts','heritage-stewardship','akkadian-and-cuneiform'])

add('heritage-stewardship','Caring for cultural heritage','Places & heritage',
'Documentation is a responsibility to objects, places and the people connected to them.',[
('Sites and collections','UNESCO\'s Ashur record is one starting point for understanding a major archaeological place. Museum records identify dispersed objects and their materials, dates and collection histories. Neither type of record replaces the voices of communities connected to the heritage.'),
('Digital survival','Manuscript photography and cataloguing can preserve access to evidence. HMML\'s collections illustrate the scale and complexity of that work. A digital surrogate still needs reliable metadata, storage and a clear relationship to the physical original.'),
('Practical principles','Preserve provenance, distinguish restoration from surviving fabric, record uncertainty and verify reproduction rights. Avoid publishing private family information or sensitive locations without consent. Future community contributions should document ownership, permissions and how the contributor wants to be credited.')],
['unesco-ashur','hmml-voobus','met-lion'],['ashur','manuscripts','oral-history'])

add('tur-abdin','Tur Abdin: language and a monastic landscape','Places & heritage',
'A limestone plateau in southeastern Turkey with a distinctive place in Syriac Christian history.',[
('A region with its own geography','Tur Abdin refers more precisely to the limestone plateau in the eastern part of Mardin province, between the Tigris and Nisibis. It is not simply another name for the whole province. Its villages, churches and monasteries form a connected historical landscape.'),
('Monasteries and institutions','The scholarly GEDSH account describes Hah as an early episcopal centre and the later importance of the monastery of Qartmin, known as Mor Gabriel. The region\'s ecclesiastical geography changed over time, including divisions and reunifications of jurisdictions. These institutional histories help explain why an individual building cannot stand for every period of the region\'s past.'),
('Language and memory','Surayt, also known as Turoyo, is associated with this region. Its spoken and written traditions extend into diaspora communities. The First World War violence remembered as Sayfo is also central to its modern history. Geography, language, monastic culture and displacement are connected subjects, each with its own evidence.')],
['gedsh-tur-abdin','gedsh-turoyo'],['surayt','sayfo','manuscripts'])

add('urmia','Urmia: language, printing and community','Places & heritage',
'A northwestern Iranian city whose schools, presses and speech belong in the modern cultural story.',[
('A city and its surrounding communities','Urmia lies west of Lake Urmia in northwestern Iran. The city and its region have an important place in the history of the Church of the East and modern Assyrian cultural life. City history and the histories of surrounding villages should be recorded separately.'),
('The nineteenth-century press','The GEDSH account describes the growth of missionary educational and publishing activity in the nineteenth century. The American mission press published Classical Syriac and Neo-Aramaic texts, including vernacular biblical translations and the periodical Zahrire d-Bahra, begun in 1849. Printing created new opportunities for circulation beyond the manuscript.'),
('A spoken record','Cambridge\'s Christian Urmi dialect page identifies fieldwork by Geoffrey Khan and links recordings such as village-life accounts, stories and material about the Assyrians of Urmi. These recordings preserve language use in context. They are a research and listening resource, with their own access and reuse conditions.'),
('Disruption and return','The First World War and the flight from Urmia in 1918 caused profound losses and displacement. Some Assyrian Christians later returned. This introduction avoids projecting an older source\'s community description into a present-day population estimate.')],
['gedsh-urmia','nena-urmi'],['syriac-printing','sureth','diaspora'])

add('nineveh-plain','The Nineveh Plain','Places & heritage',
'A region of living communities, language and religious heritage, distinct from the ancient city of Nineveh.',[
('Place and terminology','The Nineveh Plain is a modern regional setting for communities and settlements around the Mosul area. It should not be confused with the archaeological city of Nineveh, or treated as interchangeable with the full territory of the ancient Assyrian Empire.'),
('A linguistic landscape','The GEDSH entry on Sureth discusses North-Eastern Neo-Aramaic varieties associated especially with villages of the Mosul plain. A regional description still needs local detail: place names and language labels can have variant spellings and different histories of use.'),
('A dated community record','A UNAMI release from 3 October 2018 describes meetings in Bartella and Hamdaniya district with Christian and Shabak representatives. Reported concerns included public services, employment, political representation and the effects of conflict and demographic change. This is a dated record of those discussions, not a current assessment of every settlement or a travel advisory.'),
('The next level of detail','Future town entries should identify historic and current names, language varieties, institutions and sources for changes over time. Population and security information need explicit dates. Community histories should be represented through more than archaeological monuments alone.')],
['gedsh-sureth','unami-nineveh'],['nineveh','sureth','heritage-stewardship'])

add('diaspora','Across borders: the diaspora','People & diaspora',
'Migration creates new cultural centres while preserving, adapting and sometimes interrupting connections to earlier homes.',[
('Several migration histories','The Syriac Christian diaspora developed through different movements, rather than one departure at one date. The GEDSH overview identifies violence, political upheaval and limited educational or employment opportunities among the causes of migration. Displacement also occurred within the Middle East, not only towards Europe, the Americas or Australia.'),
('New centres of life','The same overview describes late nineteenth-century movement from the Urmia region towards the United States and later communities in places including Sweden, Germany and Australia. These are examples, not a complete census. Its older church and population listings should not be read as current totals.'),
('Culture in a new setting','Schools, churches, associations, media and family networks can create spaces for language and shared memory. The Assyrian Australian Association and Sophia Kanna\'s migration interview provide two Australian examples: one institutional, one personal.'),
('A global section to build','A fuller diaspora record needs local histories from multiple countries, accounts of return and continuing connections to homeland communities. It should include ordinary work, intergenerational experience and cultural creativity as well as displacement. The archive will need country-specific evidence before making demographic comparisons.')],
['gedsh-diaspora','modern-aaa','modern-kanna'],['australia','urmia','oral-history'])

add('syriac-printing','From manuscript to printing press','Language & literature',
'Type, publishing and later digital tools changed how Syriac and Neo-Aramaic texts could circulate.',[
('Early printed texts','The GEDSH history of printing distinguishes early Syriac woodcuts in European books from printing with type. It identifies Syriac type in an introductory language work printed at Pavia in 1539 and the Syriac New Testament printed at Vienna in 1555.'),
('Presses in several regions','A Syriac Psalter was printed at the Maronite monastery of Quzhayya in Lebanon in 1610. In nineteenth-century Urmia, mission printing supported vernacular texts as well as Classical Syriac. The newspaper Zahrire d-Bahra ran from 1849 to 1918. Other important presses operated in Mosul, Beirut and India.'),
('Print and a public readership','Printed religious and secular works connected publishers, readers and communities across distances. A publication\'s script, place of printing, language variety and intended audience each add context. Since the late twentieth century, digital composition has widened the practical possibilities for publishing in Syriac scripts.')],
['gedsh-printing'],['urmia','manuscripts','syriac-scripts'])

add('edessa','Edessa, Urhay and Urfa','Places & heritage',
'A city of trade, political change and literary importance in the development of Syriac.',[
('Several names, one changing city','Edessa, Syriac Urhay and modern Urfa refer to a city in southeastern Turkey. Its earlier settlement was known through forms such as Adme. Seleucus I rebuilt the settlement as a Hellenistic city in 304 BCE and named it Edessa.'),
('Aramaic and Syriac Christianity','The city\'s Aramaic variety is attested in inscriptions, documents and coins, and became the literary language of Syriac Christianity. Its Christian history includes diverse and sometimes competing traditions. A city associated with a major literary language was never simply a single, uniform intellectual community.'),
('A place in literary history','Ephrem\'s later career connects Edessa with one of the best-known figures in Syriac poetry and theology. The city\'s history can be studied through chronicles, inscriptions, texts and archaeology. Foundation legends and later associations should be distinguished from independently dated evidence.')],
['gedsh-edessa'],['classical-syriac','ephrem','tur-abdin'])

identity = next(a for a in ARTICLES if a['slug']=='assyrian-identity')
identity['sections'].insert(2,dict(title='The history of a name',text='James F. Coakley\'s GEDSH entry traces a change from geographically specific uses of Assyrian in pre-modern sources to broader ethnic and national uses in the nineteenth and twentieth centuries. It is one scholarly account of naming. Changes in the use of a name are a different question from the survival of regional populations or traditions. A fuller treatment must compare competing historical interpretations rather than turn terminology alone into a verdict on ancestry.'))
identity['sources'].append('gedsh-assyrians')
identity['related'].append('diaspora')

TIMELINE = [
('Third millennium BCE','Ancient','Ashur develops','The Tigris city has a long settlement history before the better-known imperial periods.','ashur','unesco-ashur'),
('Early second millennium BCE','Ancient','Merchant networks in Anatolia','Old Assyrian tablets document trade, investment and correspondence.','old-assyrian-trade','met-caravan'),
('Fourteenth to eleventh centuries BCE','Ancient','Middle Assyrian expansion','Assyria develops as a major territorial power. Period boundaries are approximate.','ancient-assyria','met-assyria'),
('883-859 BCE','Ancient','Ashurnasirpal II and Kalhu','A major programme of royal building and sculpture transforms Nimrud.','nimrud','met-court'),
('Eighth century BCE','Ancient','Dur-Sharrukin','Sargon II creates a new royal capital at modern Khorsabad.','khorsabad','khorsabad-ministry'),
('Seventh century BCE','Ancient','Scholarship at Nineveh','Royal tablet collections form part of a wider Mesopotamian scholarly landscape.','nineveh','yale-libraries'),
('Late seventh century BCE','Ancient','End of imperial power','The collapse of the Assyrian state is a political turning point, not evidence that every local population disappeared.','ancient-assyria','met-assyria'),
('Fourth century CE','Literary heritage','Ephrem and Syriac literature','The poet and theologian works in Nisibis and Edessa; he dies in 373.','ephrem','gedsh-ephrem'),
('Late sixteenth century','Literary heritage','Attested Sureth literary texts','The written record includes religious poetry in local Neo-Aramaic varieties.','sureth','gedsh-sureth'),
('First World War and aftermath','Modern','Sayfo','Mass violence, survival and displacement become central subjects of historical research and memory.','sayfo','modern-sayfo'),
('August 1933','Modern','Simele','Massacre and displacement leave a profound mark on modern Assyrian memory.','simele','modern-simele-asa'),
('1964','Modern','One migration story','Sophia Kanna arrives in Sydney, an experience preserved in an Australian oral-history archive.','oral-history','modern-kanna'),
('1969','Modern','Assyrian Australian Association','The association dates its founding to this year.','assyrian-australian-association','modern-aaa'),
('Today','Living culture','A culture carried forward','Language learning, music, family stories and community practice remain subjects for documentation.','endangered-languages','cambridge-nena')
]
