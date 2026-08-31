/* ホーム画面から起動できるようにするための最小の Service Worker。
 *
 * 触るのは offline.html と icons/ だけ。ゲーム本体（dist/pyxel.html、
 * その中の wasm・.pyxres・音）には手を出さない。中途半端にキャッシュすると
 * 「Code Maker で書き換えたのに古いゲームが出る」という分かりにくい壊れ方をする。
 *
 * オフラインでできるのは「つながっていない」と伝えることだけ。
 */

const CACHE = "blockquest-shell-v1";

// install 時に貯めるのはこの3つだけ。ここに載らないものは素通しする。
const SHELL = ["offline.html", "icons/icon-192.png", "icons/icon-512.png"];

function offlineUrl() {
  return new URL("offline.html", self.registration.scope).toString();
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) =>
        cache.addAll(SHELL.map((path) => new URL(path, self.registration.scope).toString()))
      )
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(names.filter((name) => name !== CACHE).map((name) => caches.delete(name)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  // ページ遷移だけ見る。ゲーム本体・wasm・画像・API はすべて素通し。
  if (request.mode !== "navigate") return;

  event.respondWith(
    fetch(request).catch(() =>
      caches.match(offlineUrl()).then((hit) => hit || new Response("offline", { status: 503 }))
    )
  );
});
