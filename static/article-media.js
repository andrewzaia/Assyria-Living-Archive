(() => {
  "use strict";

  // Only display an image when a matching Wikipedia page and the separate
  // Commons file record provide a usable, permitted licence and credit.
  const panels = document.querySelectorAll("[data-article-media]");
  const httpsUrl = (value, suffix) => {
    try {
      const parsed = new URL(value);
      return parsed.protocol === "https:" && (parsed.hostname === suffix || parsed.hostname.endsWith("." + suffix));
    } catch {
      return false;
    }
  };
  const metadataText = value => String(value || "").replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
  const allowedLicence = value => /^(?:CC0(?:\s*1\.0)?|CC BY(?:-SA)?(?:\s*[1-4]\.0)?|Public domain|PD)\b/i.test(value);
  const request = async (host, fields) => {
    const url = new URL("https://" + host + "/w/api.php");
    const params = { action: "query", format: "json", origin: "*", ...fields };
    Object.entries(params).forEach(([key, val]) => url.searchParams.set(key, val));
    const response = await fetch(url, { mode: "cors", credentials: "omit", referrerPolicy: "no-referrer" });
    if (!response.ok) throw new Error("Media lookup failed");
    return response.json();
  };
  const firstPage = data => Object.values(data?.query?.pages || {})[0];
  const inspect = info => {
    const meta = info?.extmetadata || {};
    const licence = metadataText(meta.LicenseShortName?.value);
    const author = metadataText(meta.Artist?.value || meta.Credit?.value);
    const licenceLink = meta.LicenseUrl?.value;
    const source = info?.descriptionurl;
    const thumb = info?.thumburl;
    const validLicenceLink = httpsUrl(licenceLink, "creativecommons.org") ||
      (licence.toLowerCase().startsWith("public domain") && httpsUrl(licenceLink, "wikimedia.org"));
    if (!["image/jpeg", "image/png", "image/webp"].includes(info?.mime) ||
        !httpsUrl(source, "wikimedia.org") || !httpsUrl(thumb, "wikimedia.org") ||
        !allowedLicence(licence) || !validLicenceLink ||
        (!author && !/^(public domain|pd|cc0)/i.test(licence))) return null;
    return { source, thumb, licence, licenceLink, author };
  };

  function credit(caption, image, sourceDescription, rights) {
    const context = document.createElement("span");
    context.textContent = sourceDescription + " ";
    const attribution = document.createElement("span");
    attribution.textContent = "Photograph/artwork: " + (rights.author || "Creator not stated") + ". ";
    const original = document.createElement("a");
    original.href = rights.source;
    original.target = "_blank";
    original.rel = "noopener noreferrer";
    original.textContent = "Original file";
    const license = document.createElement("a");
    license.href = rights.licenceLink;
    license.target = "_blank";
    license.rel = "noopener noreferrer";
    license.textContent = rights.licence;
    caption.replaceChildren(context, attribution, original,
      document.createTextNode(". Licence: "), license,
      document.createTextNode(". Thumbnail displayed without editorial manipulation."));
  }

  async function renderSnapshotGallery(panel, status, candidates) {
    const fileTitles = [...new Set(candidates.map(c => "File:" + c.file))].slice(0, 8);
    const lookup = await request("commons.wikimedia.org", {
      prop: "imageinfo", iiprop: "url|mime|extmetadata", iiurlwidth: "850",
      iiextmetadatafilter: "LicenseShortName|LicenseUrl|Artist|Credit|AttributionRequired",
      titles: fileTitles.join("|")
    });
    const byTitle = new Map(Object.values(lookup?.query?.pages || {}).map(page =>
      [String(page.title || "").replace(/_/g, " ").toLowerCase(), page]));
    const gallery = panel.querySelector(".media-research-gallery");
    let accepted = 0;
    for (const item of candidates) {
      if (accepted >= 3) break;
      const page = byTitle.get(("File:" + item.file).replace(/_/g, " ").toLowerCase());
      const rights = inspect(page?.imageinfo?.[0]);
      if (!rights) continue;
      const figure = document.createElement("figure");
      figure.className = "media-research-item";
      const link = document.createElement("a");
      link.href = rights.source;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      const image = document.createElement("img");
      image.alt = item.alt || ("Media from the source article: " + item.file);
      image.loading = "lazy";
      image.decoding = "async";
      image.onerror = () => figure.remove();
      image.src = rights.thumb;
      const label = document.createElement("figcaption");
      const description = (item.caption || item.alt || item.file);
      credit(label, image, "Original reference caption (not independently verified): " + description + ".", rights);
      link.appendChild(image);
      figure.append(link, label);
      gallery.appendChild(figure);
      accepted++;
    }
    if (accepted) {
      status.textContent = "Selected images from the retained source. Image-specific attribution and licence links appear beneath each image.";
      status.classList.add("media-research-found");
    }
    return accepted;
  }

  async function enhance(panel) {
    const status = panel.querySelector(".media-research-status");
    const figure = panel.querySelector(".media-research-figure");
    const img = figure.querySelector("img");
    const caption = figure.querySelector("figcaption");
    const title = panel.dataset.mediaPage;
    try {
      let candidates = [];
      try { candidates = JSON.parse(panel.dataset.mediaCandidates || "[]"); } catch {}
      if (candidates.length) {
        const accepted = await renderSnapshotGallery(panel, status, candidates);
        if (accepted) return;
      }
      const result = await request("en.wikipedia.org", {
        prop: "pageimages", piprop: "name", redirects: "1", titles: title
      });
      const page = firstPage(result);
      if (!page || page.missing !== undefined || !page.pageimage) {
        status.textContent = "No source-specific lead illustration was found. Use the Commons link below to investigate available media.";
        return;
      }
      const fileTitle = "File:" + page.pageimage;
      const fileResult = await request("commons.wikimedia.org", {
        prop: "imageinfo", iiprop: "url|mime|extmetadata", iiurlwidth: "1100",
        iiextmetadatafilter: "LicenseShortName|LicenseUrl|Artist|Credit|AttributionRequired",
        titles: fileTitle
      });
      const filePage = firstPage(fileResult);
      const info = filePage?.imageinfo?.[0];
      const rights = inspect(info);
      if (!rights) {
        status.textContent = "An image was located, but its reuse rights or attribution could not be confirmed. No image has been republished.";
        return;
      }
      const { source, thumb } = rights;

      const subject = page.title || title;
      img.alt = "Lead illustration accompanying the Wikipedia article " + subject +
        ". Consult the linked original file page for the depicted subject and context.";
      const originalLink = figure.querySelector(".media-research-original");
      originalLink.href = source;
      const context = panel.dataset.mediaRelation === "subject"
        ? "Lead illustration from the source article " + subject + "."
        : "Contextual illustration from the related article " + subject + ". Not a verified portrait or depiction of this article's subject.";
      credit(caption, img, context, rights);
      img.onload = () => {
        figure.hidden = false;
        status.hidden = true;
      };
      img.onerror = () => {
        figure.hidden = true;
        status.hidden = false;
        status.textContent = "The verified media thumbnail could not be loaded. Use the original source link to view it.";
      };
      img.src = thumb;
    } catch {
      status.textContent = "External media lookup is unavailable. The article and its textual citations remain accessible.";
    }
  }

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        enhance(entry.target);
      });
    }, { rootMargin: "400px 0px" });
    panels.forEach(panel => observer.observe(panel));
  } else {
    panels.forEach(enhance);
  }
})();
