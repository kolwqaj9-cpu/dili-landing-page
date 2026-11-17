/* analytics.js — page-view counter, nothing else.
 *
 * What it does when UMAMI_SITE_ID is filled in: loads Umami Cloud's script, which records
 * a page view (path, referrer, country/region, device type). No cookie is set for
 * tracking purposes, no cross-site profile is built, no personal data is collected.
 *
 * Why it exists: the letters we mail carry no web address and ask for no reply. The only
 * way to know whether a recipient went looking for us is the visit itself. Without a
 * counter, that signal does not exist — GitHub Pages keeps no access log we can read.
 *
 * TO ACTIVATE (one edit, then push):
 *   1. Create a free account at cloud.umami.is and add website "dilisights.com".
 *   2. Copy the Website ID it gives you (a UUID).
 *   3. Paste it between the quotes below, save, push. Done.
 *
 * Left empty, this file loads nothing and makes no request — it is inert, not broken.
 */
var UMAMI_SITE_ID = "";

(function () {
  if (!UMAMI_SITE_ID) return;
  var s = document.createElement("script");
  s.defer = true;
  s.src = "https://cloud.umami.is/script.js";
  s.setAttribute("data-website-id", UMAMI_SITE_ID);
  s.setAttribute("data-auto-track", "true");
  document.head.appendChild(s);
})();
