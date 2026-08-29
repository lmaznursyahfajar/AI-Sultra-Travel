"""
Peta interaktif ala Google Maps untuk SultraTravel — dibangun dengan Leaflet.js
(dirender sebagai komponen HTML kustom, bukan folium, agar bisa punya fitur setara
Google Maps: rute mengikuti jalan sungguhan, pencarian destinasi, tombol lokasi saya,
kontrol layar penuh, dan pilihan tampilan peta jalan/satelit/topografi.
"""
import json
import uuid
import pandas as pd
import streamlit.components.v1 as components
from .photo_utils import get_photo
from .database import KATEGORI_LABELS

CATEGORY_HEX = {
    "bahari": "#0E7C86",
    "alam": "#2E7D4F",
    "sejarah": "#8A5A2B",
    "religi": "#5B4B8A",
    "kuliner": "#C1521F",
}

SULTRA_CENTER = [-4.2, 122.3]

_TEMPLATE = r"""
<div id="wrap___ID___" style="position:relative;width:100%;height:___HEIGHT___px;
     border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(15,61,62,0.18);
     font-family:'Segoe UI',Inter,sans-serif;">
  <div id="map___ID___" style="width:100%;height:100%;"></div>

  <div style="position:absolute;top:12px;left:12px;right:64px;z-index:1000;">
    <div style="position:relative;">
      <input id="search___ID___" type="text" placeholder="&#128269; Cari destinasi wisata..."
             style="width:100%;max-width:340px;padding:10px 14px;border-radius:10px;border:none;
                    box-shadow:0 2px 10px rgba(0,0,0,0.22);font-size:14px;outline:none;box-sizing:border-box;"/>
      <div id="suggest___ID___" style="position:absolute;top:44px;left:0;width:100%;max-width:340px;
                  background:white;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.22);
                  overflow:hidden;display:none;max-height:260px;overflow-y:auto;z-index:1001;"></div>
    </div>
  </div>

  <div style="position:absolute;top:12px;right:12px;z-index:1000;display:flex;flex-direction:column;gap:8px;">
    <button id="locate___ID___" title="Lokasi saya"
       style="width:40px;height:40px;border-radius:10px;border:none;background:white;
              box-shadow:0 2px 10px rgba(0,0,0,0.22);cursor:pointer;font-size:18px;">&#128205;</button>
    <button id="fullscreen___ID___" title="Layar penuh"
       style="width:40px;height:40px;border-radius:10px;border:none;background:white;
              box-shadow:0 2px 10px rgba(0,0,0,0.22);cursor:pointer;font-size:16px;">&#9974;</button>
  </div>

  <div id="routeinfo___ID___" style="position:absolute;bottom:16px;left:12px;z-index:1000;
       background:white;border-radius:12px;box-shadow:0 2px 14px rgba(0,0,0,0.22);
       padding:10px 14px;font-size:13px;display:none;max-width:280px;">
  </div>

  <div style="position:absolute;bottom:16px;right:12px;z-index:1000;background:white;
       border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.18);padding:8px 10px;font-size:11px;
       line-height:1.6;">
    ___LEGEND___
  </div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.js"></script>

<style>
  .lrm___ID___ .leaflet-routing-container { display:none; }
  .dest-popup img { display:block; }
  .dest-popup button:hover { filter:brightness(1.08); }
  #suggest___ID___ div:hover { background:#f0f5f5; }
</style>

<script>
(function() {
  const DATA = ___DATA_JSON___;
  const USER_LOC = ___USER_LOC_JSON___;
  const CENTER = ___CENTER_JSON___;
  const ZOOM = ___ZOOM___;

  const map = L.map('map___ID___', { zoomControl: true }).setView(CENTER, ZOOM);

  const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
  }).addTo(map);
  const satelliteLayer = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      { attribution: 'Tiles &copy; Esri', maxZoom: 19 }
  );
  const terrainLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenTopoMap contributors', maxZoom: 17
  });
  L.control.layers(
      { "&#128506;&#65039; Jalan": streetLayer, "&#128752;&#65039; Satelit": satelliteLayer, "&#9968;&#65039; Topografi": terrainLayer },
      {}, { position: 'topright', collapsed: true }
  ).addTo(map);
  L.control.scale({ position: 'bottomleft', imperial: false }).addTo(map);

  const clusterGroup = L.markerClusterGroup({ maxClusterRadius: 50 });
  let userMarker = null;
  let userLatLng = USER_LOC ? L.latLng(USER_LOC[0], USER_LOC[1]) : null;
  let routingControl = null;
  let straightLine = null;

  function haversine(a, b) {
      const R = 6371, toRad = x => x * Math.PI / 180;
      const dLat = toRad(b[0]-a[0]), dLon = toRad(b[1]-a[1]);
      const s = Math.sin(dLat/2)**2 + Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*Math.sin(dLon/2)**2;
      return 2 * R * Math.asin(Math.sqrt(s));
  }

  function showRouteInfo(html) {
      const el = document.getElementById('routeinfo___ID___');
      el.innerHTML = html;
      el.style.display = 'block';
  }

  function clearRoute() {
      if (routingControl) { map.removeControl(routingControl); routingControl = null; }
      if (straightLine) { map.removeLayer(straightLine); straightLine = null; }
  }

  window.routeTo___ID___ = function(lat, lon, nama) {
      if (!userLatLng) {
          showRouteInfo('&#128205; Aktifkan <b>Lokasi Saya</b> terlebih dahulu (tombol pin di kanan atas) untuk melihat rute ke &quot;' + nama + '&quot;.');
          return;
      }
      clearRoute();
      showRouteInfo('&#8987; Menghitung rute jalan ke <b>' + nama + '</b>...');
      try {
          routingControl = L.Routing.control({
              waypoints: [userLatLng, L.latLng(lat, lon)],
              routeWhileDragging: false,
              addWaypoints: false,
              draggableWaypoints: false,
              fitSelectedRoutes: true,
              show: false,
              lineOptions: { styles: [{ color: '#14919B', weight: 5, opacity: 0.85 }] },
              createMarker: function() { return null; },
              router: L.Routing.osrmv1({ serviceUrl: 'https://router.project-osrm.org/route/v1' })
          }).addTo(map);
          routingControl.getContainer().className += ' lrm___ID___';

          routingControl.on('routesfound', function(e) {
              const r = e.routes[0];
              const km = (r.summary.totalDistance / 1000).toFixed(1);
              const menit = Math.round(r.summary.totalTime / 60);
              showRouteInfo('&#128663; <b>' + nama + '</b><br>' + km + ' km &bull; &plusmn;' + menit + ' menit (rute jalan)');
          });
          routingControl.on('routingerror', function() {
              clearRoute();
              const dist = haversine([userLatLng.lat, userLatLng.lng], [lat, lon]);
              straightLine = L.polyline([userLatLng, [lat, lon]], { color: '#F2A541', weight: 4, dashArray: '8,6' }).addTo(map);
              map.fitBounds(straightLine.getBounds(), { padding: [60,60] });
              showRouteInfo('&#128205; <b>' + nama + '</b><br>&plusmn;' + dist.toFixed(1) + ' km (garis lurus, rute jalan tidak tersedia saat ini)');
          });
      } catch (err) {
          const dist = haversine([userLatLng.lat, userLatLng.lng], [lat, lon]);
          showRouteInfo('&#128205; <b>' + nama + '</b><br>&plusmn;' + dist.toFixed(1) + ' km (estimasi garis lurus)');
      }
  };

  function popupHtml(d) {
      const badgeColor = d.color;
      let img = '<img src="' + d.foto + '" style="width:100%;height:110px;object-fit:cover;border-radius:10px 10px 0 0;" onerror="this.style.display=\'none\'"/>';
      let html = '<div class="dest-popup" style="width:230px;margin:-13px -20px;">' + img +
          '<div style="padding:10px 14px;">' +
          '<div style="font-weight:700;font-size:14px;color:#0F3D3E;margin-bottom:4px;">' + d.nama + '</div>' +
          '<span style="display:inline-block;background:' + badgeColor + '22;color:' + badgeColor + ';padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:600;margin-right:4px;">' + d.kategori_label + '</span>' +
          '<span style="display:inline-block;background:#F2A54122;color:#96650f;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:600;">&#11088; ' + d.rating + '</span>' +
          '<div style="font-size:12px;color:#456;margin-top:6px;">&#128205; ' + d.kab + '<br>&#128176; ' + d.harga + '</div>' +
          '<button onclick="window.routeTo___ID___(' + d.lat + ',' + d.lon + ',\'' + d.nama.replace(/'/g,"") + '\')" ' +
          'style="margin-top:8px;width:100%;background:#0F3D3E;color:white;border:none;padding:7px 0;border-radius:8px;font-size:12px;cursor:pointer;">' +
          '&#129517; Rute ke sini</button>' +
          '</div></div>';
      return html;
  }

  const markerMap = {};
  DATA.forEach(function(d) {
      const icon = L.divIcon({
          className: '',
          html: '<div style="background:' + d.color + ';width:26px;height:26px;border-radius:50% 50% 50% 0;' +
                'transform:rotate(-45deg);border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.35);' +
                'display:flex;align-items:center;justify-content:center;">' +
                '<span style="transform:rotate(45deg);font-size:12px;">' + d.emoji + '</span></div>',
          iconSize: [26, 26],
          iconAnchor: [13, 26],
          popupAnchor: [0, -26]
      });
      const marker = L.marker([d.lat, d.lon], { icon: icon }).bindPopup(popupHtml(d));
      clusterGroup.addLayer(marker);
      markerMap[d.nama] = marker;
  });
  map.addLayer(clusterGroup);

  // --- Pencarian destinasi (mirip kotak pencarian Google Maps) ---
  const searchInput = document.getElementById('search___ID___');
  const suggestBox = document.getElementById('suggest___ID___');
  searchInput.addEventListener('input', function() {
      const q = this.value.toLowerCase().trim();
      suggestBox.innerHTML = '';
      if (!q) { suggestBox.style.display = 'none'; return; }
      const matches = DATA.filter(d => d.nama.toLowerCase().includes(q) || d.kab.toLowerCase().includes(q)).slice(0, 6);
      if (matches.length === 0) { suggestBox.style.display = 'none'; return; }
      matches.forEach(function(d) {
          const item = document.createElement('div');
          item.style.cssText = 'padding:10px 14px;cursor:pointer;border-bottom:1px solid #eef2f2;font-size:13px;';
          item.innerHTML = '<b>' + d.emoji + ' ' + d.nama + '</b><br><span style="color:#889;font-size:11.5px;">' + d.kab + '</span>';
          item.onclick = function() {
              map.setView([d.lat, d.lon], 14, { animate: true });
              markerMap[d.nama].openPopup();
              clusterGroup.zoomToShowLayer(markerMap[d.nama], function() { markerMap[d.nama].openPopup(); });
              suggestBox.style.display = 'none';
              searchInput.value = d.nama;
          };
          suggestBox.appendChild(item);
      });
      suggestBox.style.display = 'block';
  });
  document.addEventListener('click', function(e) {
      if (!suggestBox.contains(e.target) && e.target !== searchInput) suggestBox.style.display = 'none';
  });

  // --- Lokasi saya ---
  function setUserLocation(lat, lon, doFly) {
      userLatLng = L.latLng(lat, lon);
      if (userMarker) map.removeLayer(userMarker);
      userMarker = L.marker([lat, lon], {
          icon: L.divIcon({
              className: '',
              html: '<div style="background:#1a73e8;width:18px;height:18px;border-radius:50%;border:3px solid white;box-shadow:0 0 0 4px rgba(26,115,232,0.25);"></div>',
              iconSize: [18, 18], iconAnchor: [9, 9]
          })
      }).addTo(map).bindPopup('&#128205; Lokasi Anda');
      if (doFly) map.flyTo([lat, lon], 13);
  }
  if (userLatLng) setUserLocation(userLatLng.lat, userLatLng.lng, false);

  document.getElementById('locate___ID___').addEventListener('click', function() {
      if (!navigator.geolocation) { alert('Geolocation tidak didukung browser ini.'); return; }
      this.innerHTML = '&#8987;';
      const btn = this;
      navigator.geolocation.getCurrentPosition(function(pos) {
          setUserLocation(pos.coords.latitude, pos.coords.longitude, true);
          btn.innerHTML = '&#128205;';
      }, function() {
          alert('Tidak dapat mengambil lokasi. Pastikan izin lokasi browser diaktifkan.');
          btn.innerHTML = '&#128205;';
      });
  });

  // --- Layar penuh ---
  document.getElementById('fullscreen___ID___').addEventListener('click', function() {
      const wrap = document.getElementById('wrap___ID___');
      if (!document.fullscreenElement) {
          wrap.requestFullscreen ? wrap.requestFullscreen() : null;
          wrap.style.height = '100vh';
      } else {
          document.exitFullscreen();
          wrap.style.height = '___HEIGHT___px';
      }
      setTimeout(function() { map.invalidateSize(); }, 300);
  });
  document.addEventListener('fullscreenchange', function() {
      setTimeout(function() { map.invalidateSize(); }, 200);
  });
})();
</script>
"""


def _build_legend_html():
    items = []
    for key, (emoji, label) in KATEGORI_LABELS.items():
        color = CATEGORY_HEX.get(key, "#888")
        items.append(
            f'<div><span style="display:inline-block;width:9px;height:9px;border-radius:50%;'
            f'background:{color};margin-right:5px;"></span>{emoji} {label}</div>'
        )
    return "".join(items)


def render_interactive_map(destinations_df: pd.DataFrame, user_location=None, height: int = 560, zoom: int = None):
    """Merender peta interaktif kustom (Leaflet) dengan fitur ala Google Maps ke dalam Streamlit."""
    map_id = uuid.uuid4().hex[:8]

    valid = destinations_df.dropna(subset=["latitude", "longitude"]) if destinations_df is not None else pd.DataFrame()

    data = []
    for _, row in valid.iterrows():
        kategori = str(row.get("kategori", "alam")).lower()
        emoji, label = KATEGORI_LABELS.get(kategori, ("📍", kategori.title()))
        photo = get_photo(row)
        data.append({
            "nama": str(row["nama"]),
            "kategori_label": label,
            "emoji": emoji,
            "color": CATEGORY_HEX.get(kategori, "#607d8b"),
            "kab": str(row.get("kabupaten_kota", "-")),
            "harga": str(row.get("harga_tiket", "-")),
            "rating": row.get("rating", "-"),
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"]),
            "foto": photo["url"],
        })

    if not data:
        center = SULTRA_CENTER
        zoom = zoom or 7
    elif len(data) == 1:
        center = [data[0]["lat"], data[0]["lon"]]
        zoom = zoom or 12
    else:
        center = [sum(d["lat"] for d in data) / len(data), sum(d["lon"] for d in data) / len(data)]
        zoom = zoom or (10 if len(data) <= 6 else 8)

    def _safe_json(obj):
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    html = (
        _TEMPLATE.replace("___ID___", map_id)
        .replace("___HEIGHT___", str(height))
        .replace("___DATA_JSON___", _safe_json(data))
        .replace("___USER_LOC_JSON___", _safe_json(user_location) if user_location else "null")
        .replace("___CENTER_JSON___", _safe_json(center))
        .replace("___ZOOM___", str(zoom))
        .replace("___LEGEND___", _build_legend_html())
    )
    components.html(html, height=height + 20, scrolling=False)
