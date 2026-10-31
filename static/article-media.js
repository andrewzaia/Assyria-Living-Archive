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
  async function enhance(panel) {
    const status = panel.querySelector(".media-research-status");
    const figure = panel.querySelector(".media-research-figure");
    const img = figure.querySelector("img");
    const caption = figure.querySelector("figcaption");
    const title = panel.dataset.mediaPage;
    try {
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
      const meta = info?.extmetadata || {};
      const licence = metadataText(meta.LicenseShortName?.value);
      const author = metadataText(meta.Artist?.value || meta.Credit?.value);
      const licenceLink = meta.LicenseUrl?.value;
      const source = info?.descriptionurl;
      const thumb = info?.thumburl;
      const allowedType = ["image/jpeg", "image/png", "image/webp"].includes(info?.mime);
      const validLicenceLink = httpsUrl(licenceLink, "creativecommons.org") ||
        (licence.toLowerCase().startsWith("public domain") && httpsUrl(licenceLink, "wikimedia.org"));
      if (!allowedType || !httpsUrl(source, "wikimedia.org") ||
          !httpsUrl(thumb, "wikimedia.org") || !allowedLicence(licence) ||
          !validLicenceLink || (!author && !/^(public domain|pd|cc0)/i.test(licence))) {
        status.textContent = "An image was located, but its reuse rights or attribution could not be confirmed. No image has been republished.";
        return;
      }

      const subject = page.title || title;
      img.alt = "Lead illustration accompanying the Wikipedia article " + subject +
        ". Consult the linked original file page for the depicted subject and context.";
      const originalLink = figure.querySelector(".media-research-original");
      originalLink.href = source;
      const description = document.createElement("span");
      description.textContent = panel.dataset.mediaRelation === "subject"
        ? "Lead illustration from the source article " + subject + ". "
        : "Contextual illustration from the related article " + subject + ". Not a verified portrait or depiction of this article's subject. ";
      const attribution = document.createElement("span");
      attribution.textContent = "Image: " + (author || "Creator not stated") + ". ";
      const fileLink = document.createElement("a");
      fileLink.href = source;
      fileLink.target = "_blank";
      fileLink.rel = "noopener noreferrer";
      fileLink.textContent = "Original file and description";
      const licenceAnchor = document.createElement("a");
      licenceAnchor.href = licenceLink;
      licenceAnchor.target = "_blank";
      licenceAnchor.rel = "noopener noreferrer";
      licenceAnchor.textContent = licence;
      caption.replaceChildren(description, attribution, fileLink, document.createTextNode(". Licence: "), licenceAnchor,
        document.createTextNode(". Displayed at reduced resolution, without editorial manipulation."));
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
