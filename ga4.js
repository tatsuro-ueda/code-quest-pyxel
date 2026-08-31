// GA4 測定ID。Google Analytics 管理画面で発行したものをここに1行だけ書く。
// 空文字のあいだは何も読み込まない（計測しない）。
var GA4_MEASUREMENT_ID = "";

(function () {
  if (!GA4_MEASUREMENT_ID) return;
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA4_MEASUREMENT_ID;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  function gtag() { dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("consent", "default", {
    ad_storage: "denied",
    ad_personalization: "denied",
    ad_user_data: "denied",
    analytics_storage: "granted"
  });
  gtag("js", new Date());
  gtag("config", GA4_MEASUREMENT_ID);
})();
