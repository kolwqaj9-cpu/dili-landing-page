/**
 * Facebook Pixel - Static HTML integration
 * Pixel ID: 2039176416657528
 */
(function() {
  var PIXEL_ID = '2039176416657528';
  if (typeof window.fbq === 'function') return;
  var n = window.fbq = function() {
    n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
  };
  if (!window._fbq) window._fbq = n;
  n.push = n;
  n.loaded = !0;
  n.version = '2.0';
  n.queue = [];
  var t = document.createElement('script');
  t.async = !0;
  t.src = 'https://connect.facebook.net/en_US/fbevents.js';
  var s = document.getElementsByTagName('script')[0];
  s.parentNode.insertBefore(t, s);
  window.fbq('init', PIXEL_ID);
  window.fbq('track', 'PageView');
})();
