const CACHE_NAME = 'gestion-scolaire-v10';

const urlsToCache = [
  '/',
  '/static/offline.html', // version générée par Flask via /generate-offline
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
  console.log('[ServiceWorker] 📥 Installation');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[ServiceWorker] 📦 Mise en cache initiale');
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting();
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] ⚙️ Activation');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log(`[ServiceWorker] 🧹 Suppression ancien cache : ${key}`);
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

      return fetch(event.request)
        .then(fetchResponse => {
          // Vérifie si la réponse est valide
          if (!fetchResponse || fetchResponse.status !== 200 || fetchResponse.type !== 'basic') {
            return fetchResponse;
          }

          // Clone la réponse pour la mettre en cache
          const responseClone = fetchResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            if (event.request.url.startsWith(self.location.origin)) {
              cache.put(event.request, responseClone);
            }
          });

          return fetchResponse;
        })
        .catch(() => {
          // En cas de panne réseau ou navigation
          if (event.request.mode === 'navigate') {
            return caches.match('/static/offline.html');
          }

          // Autres ressources (image, css, etc.)
          return new Response('Ressource indisponible hors ligne.', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          });
        });
    })
  );
});

// Permet l'activation immédiate d'un nouveau SW
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
