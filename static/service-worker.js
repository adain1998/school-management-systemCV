const CACHE_NAME = 'gestion-scolaire-v2';

const urlsToCache = [
  '/',
  '/offline', // Nouvelle page hors ligne
  '/static/css/student_list.css',
  '/static/css/Student_details.css',
  '/static/dashoard_styles.css',
  '/static/js/main.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/maskable-icon-512.png',
  '/static/manifest.json'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[ServiceWorker] Mise en cache des ressources');
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Suppression du cache ancien:', key);
            return caches.delete(key);
          }
        })
      )
    )
  );
  return self.clients.claim();
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(response => {
      if (response) {
        return response;
      }

      return fetch(event.request).then(fetchResponse => {
        return caches.open(CACHE_NAME).then(cache => {
          if (event.request.url.startsWith(self.location.origin)) {
            cache.put(event.request, fetchResponse.clone());
          }
          return fetchResponse;
        });
      });
    }).catch(() => {
      // Si c’est une navigation vers une page HTML, on montre la page hors ligne
      if (event.request.mode === 'navigate') {
        return caches.match('/offline');
      }
    })
  );
});
