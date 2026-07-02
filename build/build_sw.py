#!/usr/bin/env python3
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.abspath(_oe.path.join(_oe.path.dirname(_oe.path.abspath(__file__)), '..')))
import pzenv
"""Emit sw.js, a cache-first service worker that caches image GETs."""
SW = r'''/* Project Zomboid reference - image cache (cache-first). Bump version to purge. */
const CACHE = 'pz-img-v1';
const IMG = /\.(png|jpe?g|webp|gif|svg|avif)$/i;

self.addEventListener('install', e => { self.skipWaiting(); });

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  if (url.origin !== self.location.origin) return;
  if (!IMG.test(url.pathname) && !url.pathname.includes('/images/')) return;  // images only
  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req);
    if (hit) return hit;                       // cache-first: no network if already stored
    try {
      const res = await fetch(req);
      if (res && res.status === 200) cache.put(req, res.clone());
      return res;
    } catch (err) {
      const any = await cache.match(req);
      if (any) return any;
      throw err;
    }
  })());
});
'''
out = pzenv.REPO + '/sw.js'
open(out, 'w', encoding='utf-8').write(SW)
print(f"Wrote {out} ({len(SW)} bytes)")
