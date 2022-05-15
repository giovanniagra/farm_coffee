importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.0.0/workbox-sw.js');

if (workbox) {
  console.log(`Yay! Workbox is loaded 🎉`);
} else {
  console.log(`Boo! Workbox didn't load 😬`);
}

const OFFLINE_URL = '{{ offline_url }}';

const appShell = [
    '{{ icon_url }}',
    '{{ manifest_url }}',
    '{{ style_url }}',
    '{{ home_url }}',
    '{{ offline_url }}',
].map((partialUrl) => `${location.protocol}//${location.host}${partialUrl}`);

workbox.precaching.precacheAndRoute(appShell.map(url => ({
    url,
    revision: null,
})));

// Serve the app shell from the cache.
workbox.routing.registerRoute(({url}) => appShell.includes(url), new workbox.strategies.CacheOnly());

// Serve the other pages from the cache and make a request to update the value in the cache.
// Limit the cache to 5 entries.
workbox.routing.registerRoute(
    ({url}) => !appShell.includes(url),
    new workbox.strategies.StaleWhileRevalidate({
        cacheName: 'dynamic-cache',
        plugins: [new workbox.expiration.ExpirationPlugin({
            maxEntries: 5,
        })],
    })
);

// Handle offline.
// From https://developers.google.com/web/tools/workbox/guides/advanced-recipes#provide_a_fallback_response_to_a_route
workbox.routing.setCatchHandler(({ event }) => {
    console.log(event)
    switch (event.request.method) {
        case 'GET':
            return caches.match(OFFLINE_URL);
        default:
            return Response.error();
    }
});