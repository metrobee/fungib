// PLUTOFF Mycology Dashboard - Executive Minimalist Client
let observations = [];
let filteredObs = [];
let activeRole = "all"; // "all" | "primary" | "co"
let map = null;
let tileLayer = null;
let markersLayer = null;
let currentTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

const TILES = {
  light: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
  dark: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
};

// Firebase Auth Configuration
const ALLOWED_EMAILS = ["borismeldre@gmail.com"];

const firebaseConfig = {
  apiKey: "AIzaSyBEtiCBt2hYWiiL2dDeTRSqE8pY15eGbcE",
  authDomain: "fungib.firebaseapp.com",
  projectId: "fungib",
  storageBucket: "fungib.firebasestorage.app",
  messagingSenderId: "589912931967",
  appId: "1:589912931967:web:8e4d9a3c33160617ab094a"
};

let auth = null;
if (typeof firebase !== "undefined") {
  try {
    firebase.initializeApp(firebaseConfig);
    auth = firebase.auth();
  } catch (e) {
    console.error("Firebase init error:", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initAuth();
  initEventListeners();
});

function initAuth() {
  const googleBtn = document.getElementById("googleSignInBtn");
  if (googleBtn) {
    googleBtn.addEventListener("click", () => {
      if (!auth) return;
      const provider = new firebase.auth.GoogleAuthProvider();
      auth.signInWithPopup(provider).catch(err => {
        console.error("Auth viga:", err);
        const errEl = document.getElementById("authErrorMsg");
        if (errEl) {
          errEl.style.display = "block";
          errEl.textContent = "Sisselogimine ebaõnnestus: " + (err.message || err);
        }
      });
    });
  }

  const signOutBtn = document.getElementById("signOutBtn");
  if (signOutBtn) {
    signOutBtn.addEventListener("click", () => {
      if (auth) auth.signOut();
    });
  }

  if (auth) {
    auth.onAuthStateChanged(async (user) => {
      const authScreen = document.getElementById("authScreen");
      const appContent = document.getElementById("appContent");
      const authError = document.getElementById("authErrorMsg");

      if (user && user.email && ALLOWED_EMAILS.includes(user.email.toLowerCase())) {
        if (authScreen) authScreen.style.display = "none";
        if (appContent) appContent.style.display = "block";
        if (authError) authError.style.display = "none";

        const emailEl = document.getElementById("userProfileEmail");
        if (emailEl) emailEl.textContent = user.email;

        if (!map) {
          initMap();
          await loadData();
        }
      } else if (user) {
        if (authScreen) authScreen.style.display = "flex";
        if (appContent) appContent.style.display = "none";
        if (authError) {
          authError.style.display = "block";
          authError.innerHTML = `Ligipääs puudub kontoga <strong>${escapeHtml(user.email)}</strong>.<br>See arhiiv on privaatne. <a href="#" id="authSignOutLink">Logi välja / vaheta kontot</a>`;
          const link = document.getElementById("authSignOutLink");
          if (link) link.onclick = (e) => { e.preventDefault(); auth.signOut(); };
        }
      } else {
        if (authScreen) authScreen.style.display = "flex";
        if (appContent) appContent.style.display = "none";
      }
    });
  } else {
    // If offline fallback
    initMap();
    loadData();
  }
}

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
  // Role counts
  if (meta.role_stats) {
    document.getElementById("roleCntAll").textContent = meta.role_stats.total;
    document.getElementById("roleCntPrimary").textContent = meta.role_stats.primary;
    document.getElementById("roleCntCo").textContent = meta.role_stats.co_observer;
  }

  // Observers filter
  const obsSelect = document.getElementById("observerFilter");
  if (obsSelect && meta.observers) {
    obsSelect.innerHTML = '<option value="">Kõik autorid / kaaslased</option>';
    meta.observers.forEach(o => {
      if (o) {
        const opt = document.createElement("option");
        opt.value = o;
        opt.textContent = o;
        obsSelect.appendChild(opt);
      }
    });
  }

  // Counties filter
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

  // Substrates filter
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

function formatTimeAgo(isoString) {
  if (!isoString) return "-";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 5) return "Värske (äsja uuendatud)";
    if (diffMins < 60) return `${diffMins} min tagasi`;
    if (diffHours < 24) return `${diffHours} h tagasi`;
    if (diffDays === 1) return "Eile";
    if (diffDays < 30) return `${diffDays} p tagasi`;
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths} k tagasi (${date.toISOString().split("T")[0]})`;
  } catch (e) {
    return "-";
  }
}

function updateStats(meta) {
  document.getElementById("statTotalObs").textContent = meta.total_observations || observations.length;
  document.getElementById("statUniqueTaxa").textContent = meta.unique_taxa || "-";

  if (meta.time_stats) {
    document.getElementById("statToday").textContent = meta.time_stats.today;
    document.getElementById("statWeek").textContent = meta.time_stats.this_week;
    document.getElementById("statMonth").textContent = meta.time_stats.this_month;
    document.getElementById("statYear").textContent = meta.time_stats.this_year;
  }

  const coFreshness = document.getElementById("coFreshnessText");
  if (coFreshness && meta.co_data_updated_at) {
    coFreshness.textContent = formatTimeAgo(meta.co_data_updated_at);
    coFreshness.title = `Viimane PlutoF eksport: ${meta.co_data_updated_at.split("T")[0]}`;
  }

  if (meta.user_profile) {
    const p = meta.user_profile;
    const nameEl = document.getElementById("userProfileName");
    const handleEl = document.getElementById("userProfileUsername");
    const emailEl = document.getElementById("userProfileEmail");
    const avatarEl = document.getElementById("userAvatar");

    if (nameEl && p.name) nameEl.textContent = p.name;
    if (handleEl && p.username) handleEl.textContent = `@${p.username}`;
    if (emailEl && p.email) emailEl.textContent = p.email;
    if (avatarEl && p.name) {
      const initials = p.name.split(" ").map(n => n[0]).join("").toUpperCase();
      avatarEl.textContent = initials || "BM";
    }
  }

  if (meta.latest_observation) {
    const lo = meta.latest_observation;
    const link = document.getElementById("latestObsLink");
    if (link) {
      const name = lo.est_name ? `${lo.est_name} (${lo.taxon})` : lo.taxon;
      link.textContent = `${name} • ${lo.date || ""} • ${lo.locality || lo.county || ""} (PlutoF ID: #${lo.id}) →`;
      link.href = lo.url || `https://app.plutof.ut.ee/observation/view/${lo.id}`;
    }
  }
}

function setRole(role) {
  activeRole = role;
  document.querySelectorAll(".role-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.role === role);
  });
  applyFilters();
}

function applyFilters() {
  const q = document.getElementById("searchInput").value.trim().toLowerCase();
  const sort = document.getElementById("sortOrder").value;
  const status = document.getElementById("statusFilter").value;
  const observer = document.getElementById("observerFilter").value;
  const county = document.getElementById("countyFilter").value;
  const sub = document.getElementById("substrateFilter").value;

  filteredObs = observations.filter(o => {
    // Role filter
    if (activeRole === "primary" && o.is_co_observer) return false;
    if (activeRole === "co" && !o.is_co_observer) return false;

    // Status filter
    if (status === "verified" && !o.is_verified) return false;
    if (status === "pending" && o.is_verified) return false;

    // Observer filter
    if (observer && o.primary_observer !== observer && !o.collectors.includes(observer)) return false;

    // Search query
    const matchQuery = !q || 
      (o.est_name && o.est_name.toLowerCase().includes(q)) ||
      (o.taxon && o.taxon.toLowerCase().includes(q)) ||
      (o.collectors && o.collectors.toLowerCase().includes(q)) ||
      (o.primary_observer && o.primary_observer.toLowerCase().includes(q)) ||
      (o.locality && o.locality.toLowerCase().includes(q)) ||
      (o.county && o.county.toLowerCase().includes(q)) ||
      (o.substrate && o.substrate.toLowerCase().includes(q)) ||
      (o.substrate_type && o.substrate_type.toLowerCase().includes(q)) ||
      (o.id && o.id.includes(q));

    const matchCounty = !county || o.county === county;
    const matchSub = !sub || o.substrate === sub;

    return matchQuery && matchCounty && matchSub;
  });

  // Sorteerimine
  filteredObs.sort((a, b) => {
    if (sort === "created_desc") {
      const aCreated = a.created_at || a.date || "";
      const bCreated = b.created_at || b.date || "";
      return bCreated.localeCompare(aCreated) || (parseInt(b.id) - parseInt(a.id));
    } else if (sort === "date_desc") {
      const aDate = a.date || "";
      const bDate = b.date || "";
      return bDate.localeCompare(aDate) || (parseInt(b.id) - parseInt(a.id));
    } else if (sort === "name_asc") {
      const aName = a.est_name || a.taxon;
      const bName = b.est_name || b.taxon;
      return aName.localeCompare(bName, "et");
    }
    return 0;
  });

  const primCount = filteredObs.filter(o => !o.is_co_observer).length;
  const coCount = filteredObs.filter(o => o.is_co_observer).length;

  document.getElementById("resultsMeta").textContent = `${filteredObs.length} vaatlust leitud (${primCount} minu, ${coCount} kaasvaatlust)`;

  currentPage = 1;
  renderList();
  renderMarkers();
}

let currentPage = 1;
const PAGE_SIZE = 50;

function renderList() {
  const grid = document.getElementById("obsGrid");
  grid.innerHTML = "";

  if (filteredObs.length === 0) {
    grid.innerHTML = `<div class="obs-no-thumb" style="grid-column: 1/-1; padding: 40px; text-align: center;">Ühtegi vaatlust ei leitud valitud filtritega.</div>`;
    renderPagination();
    return;
  }

  const totalPages = Math.ceil(filteredObs.length / PAGE_SIZE) || 1;
  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const startIdx = (currentPage - 1) * PAGE_SIZE;
  const pageObs = filteredObs.slice(startIdx, startIdx + PAGE_SIZE);

  pageObs.forEach(o => {
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

    let topBadges = "";
    if (o.is_co_observer) {
      topBadges += `<span class="badge badge-co-highlight">KAASVAATLEJA</span>`;
    }
    if (!o.is_verified) {
      topBadges += `<span class="badge badge-pending-top">OOTEL</span>`;
    }

    let badgesHtml = "";
    if (o.is_co_observer && o.primary_observer) {
      badgesHtml += `<span class="badge badge-co-author">Autor: ${escapeHtml(o.primary_observer)}</span>`;
    }
    if (o.is_verified) {
      const vText = o.verified_by ? `Kinnitatud (${escapeHtml(o.verified_by)})` : "Kinnitatud";
      badgesHtml += `<span class="badge badge-verified">${vText}</span>`;
    }
    if (o.substrate) badgesHtml += `<span class="badge">${escapeHtml(o.substrate)}</span>`;
    if (o.substrate_type) badgesHtml += `<span class="badge">${escapeHtml(o.substrate_type)}</span>`;
    if (o.abundance) badgesHtml += `<span class="badge">${escapeHtml(o.abundance)}</span>`;

    const estTitle = o.est_name ? `<div class="obs-est-name">${escapeHtml(o.est_name)}</div>` : "";
    const sciTitle = `<div class="obs-taxon">${escapeHtml(o.taxon)}</div>`;

    card.innerHTML = `
      <div class="obs-thumb-container">
        ${imgHtml}
        <div class="obs-top-badges">
          ${topBadges}
        </div>
      </div>
      <div class="obs-body">
        ${estTitle}
        ${sciTitle}
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

  renderPagination();
}

function renderPagination() {
  const totalPages = Math.ceil(filteredObs.length / PAGE_SIZE) || 1;
  const startIdx = filteredObs.length > 0 ? (currentPage - 1) * PAGE_SIZE + 1 : 0;
  const endIdx = Math.min(currentPage * PAGE_SIZE, filteredObs.length);
  const infoText = filteredObs.length > 0 
    ? `Kuvatakse ${startIdx}–${endIdx} (kokku ${filteredObs.length}) • Leht ${currentPage}/${totalPages}`
    : `0 vaatlust`;

  const topInfo = document.getElementById("paginationTopInfo");
  const bottomInfo = document.getElementById("paginationBottomInfo");
  if (topInfo) topInfo.textContent = infoText;
  if (bottomInfo) bottomInfo.textContent = infoText;

  const controlsHtml = buildPaginationButtons(currentPage, totalPages);
  const topControls = document.getElementById("paginationTopControls");
  const bottomControls = document.getElementById("paginationBottomControls");
  if (topControls) topControls.innerHTML = controlsHtml;
  if (bottomControls) bottomControls.innerHTML = controlsHtml;
}

function buildPaginationButtons(page, totalPages) {
  if (totalPages <= 1) return "";

  let html = `<div class="pagination-btn-group">`;
  
  // Previous button
  const prevDisabled = page <= 1 ? "disabled" : "";
  html += `<button class="page-btn page-nav-btn" ${prevDisabled} onclick="goToPage(${page - 1})">‹ Eelmine</button>`;

  // Number buttons
  let pages = [];
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i);
  } else {
    pages.push(1);
    if (page > 3) pages.push("...");
    
    let start = Math.max(2, page - 1);
    let end = Math.min(totalPages - 1, page + 1);
    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) pages.push(i);
    }
    
    if (page < totalPages - 2) pages.push("...");
    if (!pages.includes(totalPages)) pages.push(totalPages);
  }

  pages.forEach(p => {
    if (p === "...") {
      html += `<span class="page-ellipsis">…</span>`;
    } else {
      const activeClass = p === page ? "active" : "";
      html += `<button class="page-btn page-num-btn ${activeClass}" onclick="goToPage(${p})">${p}</button>`;
    }
  });

  // Next button
  const nextDisabled = page >= totalPages ? "disabled" : "";
  html += `<button class="page-btn page-nav-btn" ${nextDisabled} onclick="goToPage(${page + 1})">Järgmine ›</button>`;
  html += `</div>`;

  return html;
}

function goToPage(page) {
  currentPage = page;
  renderList();
  const contentPane = document.getElementById("contentPane");
  if (contentPane) {
    contentPane.scrollTo({ top: 0, behavior: "smooth" });
  } else {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
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

        const title = o.est_name ? `<strong>${escapeHtml(o.est_name)}</strong><br><em>${escapeHtml(o.taxon)}</em>` : `<strong>${escapeHtml(o.taxon)}</strong>`;
        const roleInfo = o.is_co_observer ? `<br><span style="color:#e0e0e0;font-size:0.7rem;">[KAASVAATLEJA: ${escapeHtml(o.primary_observer)}]</span>` : "";
        const statusText = o.is_verified ? `[Kinnitatud]` : `[OOTEL]`;
        marker.bindTooltip(`${title}${roleInfo}<br>${o.date || ""} • ${statusText}`, {
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
  document.getElementById("modalTitle").textContent = o.est_name ? `${o.est_name} (${o.taxon})` : o.taxon;
  
  const roleText = o.is_co_observer 
    ? `Kaasvaatleja (Peavaatleja: ${o.primary_observer} | Vaatlejad: ${o.collectors})` 
    : `Peavaatleja (Boris Meldre)`;
  document.getElementById("modalRole").textContent = roleText;

  const statusText = o.is_verified 
    ? (o.verified_by ? `Kinnitatud (${o.verified_by})` : "Kinnitatud")
    : "Ootel (Kinnitamata)";
  document.getElementById("modalVerified").textContent = statusText;

  document.getElementById("modalDate").textContent = o.date || "-";
  document.getElementById("modalLocality").textContent = `${o.locality || "-"}, ${o.county || ""}`;
  document.getElementById("modalCoords").textContent = (o.latitude && o.longitude) ? `${parseFloat(o.latitude).toFixed(5)}, ${parseFloat(o.longitude).toFixed(5)}` : "-";
  document.getElementById("modalSubstrate").textContent = o.substrate || "-";
  document.getElementById("modalSubstrateType").textContent = o.substrate_type || "-";
  document.getElementById("modalDeterminer").textContent = o.determiner || "-";
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
  document.getElementById("sortOrder").addEventListener("change", applyFilters);
  document.getElementById("statusFilter").addEventListener("change", applyFilters);
  document.getElementById("observerFilter").addEventListener("change", applyFilters);
  document.getElementById("countyFilter").addEventListener("change", applyFilters);
  document.getElementById("substrateFilter").addEventListener("change", applyFilters);
  document.getElementById("modalCloseBtn").addEventListener("click", closeModal);

  // Role button events
  document.querySelectorAll(".role-btn").forEach(btn => {
    btn.addEventListener("click", () => setRole(btn.dataset.role));
  });

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
