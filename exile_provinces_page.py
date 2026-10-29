"""Accessible research reading room for biblical exile and Assyrian provinces."""
from html import escape as H


def render(heading, categories, cases, stats, scope_note):
    controls=''.join(
        '<li><button type="button" data-exile-filter="'+H(item["id"])+'" aria-pressed="false">'+
        '<strong>'+H(item["title"])+'</strong><small>'+H(item["description"])+'</small></button></li>'
        for item in categories
    )
    cards=[]
    for item in cases:
        biblical=''.join('<li><a href="'+H(p["url"],quote=True)+'">'+H(p["label"])+'</a></li>'
                         for p in item["bible_links"])
        supporting=''.join('<li><a href="'+H(s["url"],quote=True)+
                           '" rel="noopener noreferrer" target="_blank">'+H(s["title"])+'</a></li>'
                           for s in item["secondary_links"])
        kind={"edited-text":"Original edited Assyrian text",
              "museum-object":"Museum-catalogued visual object",
              "scholarly-context":"Historical geography and source synthesis",
              "specialist-identified-text":"Named ancient letter through specialist source",
              "academic-synthesis":"Modern archaeological study"}[item["kind"]]
        cards.append(
            '<article id="exile-'+H(item["id"])+'" class="exile-case" data-exile-category="'+H(item["category"])+'">'+
            '<header><span class="eyebrow">'+H(item["date"])+' / '+H(item["scope"])+'</span>'+
            '<h2>'+H(item["title"])+'</h2><p class="exile-kind">'+H(kind)+'</p></header>'+
            '<div class="exile-witnesses">'+
            '<section aria-label="Material or historical evidence"><h3>Assyrian evidence and research context</h3>'+
            '<p class="exile-source-name">'+H(item["source_title"])+'</p>'+
            '<p><strong>Source location:</strong> '+H(item["source_location"])+'</p>'+
            '<p>'+H(item["witness"])+'</p>'+
            '<p><a href="'+H(item["source_url"],quote=True)+'" rel="noopener noreferrer" target="_blank">'+
            'Inspect '+('original edition or museum record' if item["kind"] in ("edited-text","museum-object")
                          else 'source and scholarly assessment')+'</a></p></section>'+
            '<section aria-label="Biblical evidence"><h3>Primary biblical reading</h3><ul>'+biblical+'</ul>'+
            '<p>'+H(item["scripture"])+'</p></section></div>'+
            '<div class="exile-assessment"><div><h3>What can be compared</h3><p>'+H(item["comparison"])+'</p></div>'+
            '<div><h3>What remains unproven</h3><p>'+H(item["limits"])+'</p></div></div>'+
            '<footer><details><summary>Further source routes ('+str(len(item["secondary_links"]))+
            ')</summary><ul>'+supporting+'</ul></details>'+
            '<a href="/articles/'+H(item["article"])+'/">Read the associated full dossier</a></footer></article>'
        )
    return ('<main id="main" class="wrap section exile-room">'+
            heading("RESEARCH / DIASPERSAL AND PROVINCES","Exile, resettlement and life across Assyria.",
                    "Trace biblical deportation notices through named places, original administrative texts, edited inscriptions, visual objects and carefully qualified scholarship.")+
            '<div class="exile-intro"><p><strong>The Bible remains the primary witness for what its passages report.</strong> '
            'A royal claim, a provincial letter, an image and a modern archaeological interpretation each answer '
            'different questions. They cannot be treated as interchangeable confirmations.</p>'+
            '<p>'+H(scope_note)+'</p>'+
            '<p><strong>'+str(stats["cases"])+' research comparisons / '+str(stats["bible_routes"])+
            ' Bible routes / '+str(stats["distinct_supporting_sources"])+' distinct institutional source records</strong> '
            'in this reading room. Independent specialist review is still pending.</p></div>'+
            '<nav class="exile-filters" aria-label="Filter exile and settlement research">'+
            '<h2>Explore by question</h2><div class="exile-reset"><button type="button" data-exile-filter="all" aria-pressed="true">All evidence</button></div>'+
            '<ul>'+controls+'</ul><p class="exile-filter-count" role="status" aria-live="polite">'+
            str(stats["cases"])+' studies displayed</p></nav>'+
            '<div class="exile-cases">'+''.join(cards)+'</div>'+
            '<section class="exile-bottom"><h2>Source roles and rights</h2>'+
            '<p>The direct administrative text SAA 01 220 is cited at a particular edition and line range. '
            'Letters SAA 19 17 and 19 18 are identified through an institutional specialist synthesis; their original '
            'tablet lines were not independently collated here. Museum reliefs represent other places or reigns, '
            'not visual portraits of the Samaria deportees. The Oxford archaeological chapter was assessed from '
            'its accessible abstract and cannot serve as an exhaustively consulted text.</p>'+
            '<p>All source links open institutional records. No copyrighted museum images or scholarly book chapters '
            'are reproduced. The <a href="/sources/">source library</a>, '
            '<a href="/about/evidence/">claim review register</a> and '
            '<a href="/about/#next-chapters">Next Chapters</a> record research and review limits.</p>'+
            '</section></main>')
