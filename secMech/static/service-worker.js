self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("alarm-cache").then((cache) => {
      return cache.addAll([
        "/",
        "/static/stylesheet2.css",
        "/static/fontawesome-free-5.15.2-web/css/all.css",
      ]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
