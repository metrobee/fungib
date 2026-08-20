// PLUTOFF Mycology Dashboard - Executive Minimalist Client
let observations = [];
let filteredObs = [];
let map = null;
let tileLayer = null;
let markersLayer = null;
let currentTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

const TILES = {
  light: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  dark: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
};

document.addEventListener("DOMContentLoaded", async () => {
  initTheme();
  initMap();
  initEventListeners();
  await loadData();
});

function initTheme() {
  document.documentElement.setAttribute("data-theme", currentTheme);
  updateThemeButton();
}

function toggleTheme() {
  currentTheme = currentTheme === "light" ? "dark" : "light";
  localStorage.setItem("theme", currentTheme);
  document.documentElement.setAttribute("data-theme", currentTheme);
  updateThemeButton();
  updateMapTiles();
  renderMarkers();
}

function updateThemeButton() {
  const btn = document.getElementById("themeToggleBtn");
  if (btn) {
    btn.textContent = currentTheme === "light" ? "DARK MODE" : "LIGHT MODE";
  }
}

function initMap() {
  const estoniaCenter = [58.5953, 25.0136];
  map = L.map("map", {
    center: estoniaCenter,
    zoom: 7,
    zoomControl: false,
    attributionControl: false
  });

  L.control.zoom({ position: "bottomright" }).addTo(map);

  tileLayer = L.tileLayer(TILES[currentTheme], {
    maxZoom: 19,
    subdomains: "abcd"
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

function updateMapTiles() {
  if (map && tileLayer) {
    map.removeLayer(tileLayer);
    tileLayer = L.tileLayer(TILES[currentTheme], {
      maxZoom: 19,
      subdomains: "abcd"
    }).addTo(map);
  }
}

async function loadData() {
  try {
    const res = await fetch("data/observations.json?v=" + Date.now());
    const data = await res.json();
    observations = data.observations || [];
    filteredObs = [...observations];

    populateFilters(data.metadata);
    updateStats(data.metadata);
    applyFilters();
  } catch (err) {
    console.error("Viga andmete laadimisel:", err);
    document.getElementById("obsGrid").innerHTML = `<div class="obs-no-thumb">Andmete laadimine ebaõnnestus.</div>`;
    document.getElementById("resultsMeta").textContent = "Viga andmete laadimisel";
  }
}

function populateFilters(meta) {
  const countySelect = document.getElementById("countyFilter");
  if (countySelect && meta.counties) {
    countySelect.innerHTML = '<option value="">Kõik maakonnad</option>';
    meta.counties.forEach(c => {
      if (c) {
        const opt = document.createElement("option");
        opt.value = c;
        opt.textContent = c;
        countySelect.appendChild(opt);
      }
    });
  }

  const subSelect = document.getElementById("substrateFilter");
  if (subSelect) {
    const substrates = new Set();
    observations.forEach(o => {
      if (o.substrate) substrates.add(o.substrate);
    });
    subSelect.innerHTML = '<option value="">Kõik substraadid</option>';
    Array.from(substrates).sort().forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      subSelect.appendChild(opt);
    });
  }
}

function updateStats(meta) {
  document.getElementById("statTotalObs").textContent = meta.total_observations || observations.length;
  document.getElementById("statUniqueTaxa").textContent = meta.unique_taxa || "-";
  document.getElementById("statCounties").textContent = (meta.counties ? meta.counties.length : 0);
}

function applyFilters() {
  const q = document.getElementById("searchInput").value.trim().toLowerCase();
  const county = document.getElementById("countyFilter").value;
  const sub = document.getElementById("substrateFilter").value;

  filteredObs = observations.filter(o => {
    const matchQuery = !q || 
      (o.taxon && o.taxon.toLowerCase().includes(q)) ||
      (o.locality && o.locality.toLowerCase().includes(q)) ||
      (o.county && o.county.toLowerCase().includes(q)) ||
      (o.substrate && o.substrate.toLowerCase().includes(q)) ||
      (o.substrate_type && o.substrate_type.toLowerCase().includes(q)) ||
      (o.id && o.id.includes(q));

    const matchCounty = !county || o.county === county;
    const matchSub = !sub || o.substrate === sub;

    return matchQuery && matchCounty && matchSub;
  });

  document.getElementById("resultsMeta").textContent = `${filteredObs.length} vaatlust leitud`;

  renderList();
  renderMarkers();
}

function renderList() {
  const grid = document.getElementById("obsGrid");
  grid.innerHTML = "";

  if (filteredObs.length === 0) {
    grid.innerHTML = `<div class="obs-no-thumb" style="grid-column: 1/-1; padding: 40px;">Ühtegi vaatlust ei leitud valitud filtritega.</div>`;
    return;
  }

  filteredObs.forEach(o => {
    const card = document.createElement("div");
    card.className = "obs-card";
    card.dataset.id = o.id;
    card.onclick = () => openModal(o);

    let imgHtml = "";
    if (o.photos && o.photos.length > 0 && o.photos[0].url && o.photos[0].url.startsWith("http")) {
      const src = o.photos[0].url;
      imgHtml = `<img src="${src}" alt="${escapeHtml(o.taxon)}" class="obs-thumb" loading="lazy" onerror="this.style.display='none';">`;
    } else {
      imgHtml = `<div class="obs-no-thumb">Foto puudub</div>`;
    }

    let badgesHtml = "";
    if (o.substrate) badgesHtml += `<span class="badge">${escapeHtml(o.substrate)}</span>`;
    if (o.substrate_type) badgesHtml += `<span class="badge">${escapeHtml(o.substrate_type)}</span>`;
    if (o.abundance) badgesHtml += `<span class="badge">${escapeHtml(o.abundance)}</span>`;

    card.innerHTML = `
      <div class="obs-thumb-container">
        ${imgHtml}
      </div>
      <div class="obs-body">
        <div class="obs-taxon">${escapeHtml(o.taxon)}</div>
        <div class="obs-meta-row">
          <span>${o.date || "-"}</span>
          <span>${escapeHtml(o.locality || o.county || "")}</span>
        </div>
        <div class="obs-badges">
          ${badgesHtml}
        </div>
      </div>
    `;

    grid.appendChild(card);
  });
}

function renderMarkers() {
  markersLayer.clearLayers();
  const bounds = [];

  filteredObs.forEach(o => {
    if (o.latitude && o.longitude) {
      const lat = parseFloat(o.latitude);
      const lon = parseFloat(o.longitude);

      if (!isNaN(lat) && !isNaN(lon)) {
        bounds.push([lat, lon]);

        const icon = L.divIcon({
          className: "custom-map-pin",
          iconSize: [10, 10],
          iconAnchor: [5, 5]
        });

        const marker = L.marker([lat, lon], { icon }).addTo(markersLayer);
        marker.on("click", () => {
          openModal(o);
          highlightCard(o.id);
        });

        marker.bindTooltip(`<strong>${escapeHtml(o.taxon)}</strong><br>${o.date || ""}`, {
          direction: "top",
          offset: [0, -6]
        });
      }
    }
  });

  if (bounds.length > 0 && map) {
    map.fitBounds(bounds, { padding: [30, 30], maxZoom: 13 });
  }
}

function highlightCard(id) {
  document.querySelectorAll(".obs-card").forEach(c => c.classList.remove("active"));
  const card = document.querySelector(`.obs-card[data-id="${id}"]`);
  if (card) {
    card.classList.add("active");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

function openModal(o) {
  const modal = document.getElementById("obsModal");
  document.getElementById("modalTitle").textContent = o.taxon;
  document.getElementById("modalDate").textContent = o.date || "-";
  document.getElementById("modalLocality").textContent = `${o.locality || "-"}, ${o.county || ""}`;
  document.getElementById("modalCoords").textContent = (o.latitude && o.longitude) ? `${parseFloat(o.latitude).toFixed(5)}, ${parseFloat(o.longitude).toFixed(5)}` : "-";
  document.getElementById("modalSubstrate").textContent = o.substrate || "-";
  document.getElementById("modalSubstrateType").textContent = o.substrate_type || "-";
  document.getElementById("modalAbundance").textContent = o.abundance || "-";
  document.getElementById("modalDeterminer").textContent = o.determiner || "-";
  document.getElementById("modalObserver").textContent = o.observer || "Boris Meldre";
  document.getElementById("modalRemarks").textContent = o.remarks || "-";
  
  const plutofLink = document.getElementById("modalPlutofLink");
  plutofLink.href = o.url || `https://app.plutof.ut.ee/observation/view/${o.id}`;

  const gallery = document.getElementById("modalGallery");
  if (o.photos && o.photos.length > 0 && o.photos[0].url && o.photos[0].url.startsWith("http")) {
    gallery.style.display = "flex";
    gallery.innerHTML = `<img src="${o.photos[0].url}" alt="${escapeHtml(o.taxon)}" class="modal-main-image">`;
  } else {
    gallery.style.display = "none";
    gallery.innerHTML = "";
  }

  modal.classList.add("open");
}

function closeModal() {
  document.getElementById("obsModal").classList.remove("open");
}

function initEventListeners() {
  document.getElementById("themeToggleBtn").addEventListener("click", toggleTheme);
  document.getElementById("searchInput").addEventListener("input", applyFilters);
  document.getElementById("countyFilter").addEventListener("change", applyFilters);
  document.getElementById("substrateFilter").addEventListener("change", applyFilters);
  document.getElementById("modalCloseBtn").addEventListener("click", closeModal);

  document.getElementById("obsModal").addEventListener("click", (e) => {
    if (e.target.id === "obsModal") {
      closeModal();
    }
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModal();
    } else if (e.key === "/" && document.activeElement !== document.getElementById("searchInput")) {
      e.preventDefault();
      document.getElementById("searchInput").focus();
    }
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
