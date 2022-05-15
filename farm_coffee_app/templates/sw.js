const VERSION = '{{ version }}';
const staticCachePrefix = 'static';
const staticCacheName = `${staticCachePrefix}-${VERSION}`;
const dynamicCacheName = 'dynamic';

const networkWaitTime = 2000;


self.addEventListener('install', (event) => {
    console.log('[SW] Installing SW version:', VERSION);
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                console.log('[SW] Caching app shell');
                cache.addAll([
                    '/static/farm_coffee_app/manifest.json',
                    '/',
                    '/offline/',
                ]);
            }),
    );
});

self.addEventListener('fetch', (event) => {
    // Let the browser do its default thing
    // for non-GET requests.
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        networkThenCache(event),
    );
});

function networkThenCache(event) {
    return Promise.race([
        tryToFetchAndSaveInCache(event, dynamicCacheName),
        new Promise((_resolve, reject) => setTimeout (reject, networkWaitTime))
    ])
        .then(
            (response) => response,
            () => getFromCache(event).catch(() => provideOfflineFallback(event))
        );
}

function getFromCache(event) {
    return caches.match(event.request)
        .then((response) => {
            console.log(`[SW] Requesting ${event.request.url}.`);
            if (response) {
                console.log(`[SW] Served response to ${event.request.url} from the cache.`);
                return response;
            }
                return Promise.reject();
    });
}

function tryToFetchAndSaveInCache(event, cacheName) {
    return fetchAndSaveInCache(event, cacheName)
        .catch(err => {
            console.warn('[SW] Network request failed, app is probably offline', err);
            return provideOfflineFallback(event)
                .catch(error => console.warn('[SW] Network request failed.', error));
        });
}

function fetchAndSaveInCache(event, cacheName) {
    console.log(`[SW] Fetching ${event.request.url}`);
    return fetch(event.request)
        .then(res => {
            const requestSucceeded = res.status >= 200 && res.status <= 300;
            if (!requestSucceeded) {
                console.log(`[SW] Request failed.`);
                return res;
            }

            return caches.open(cacheName)
                .then(cache => {
                    console.log('[SW] Saving in the cache.');
                    cache.put(event.request.url, res.clone());
                    return res;
                });
        });
}

function provideOfflineFallback(event) {
    return caches.open(staticCacheName)
        .then((cache) => {
            if (event.request.headers.get('accept').includes('text/html')) {
                return cache.match('/offline/');
            }

            return Promise.reject();
        });
}