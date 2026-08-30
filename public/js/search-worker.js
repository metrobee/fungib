/**
 * FUNGIB MYCOLOGY ARCHIVE - SUB-MILLISECOND FUZZY SEARCH WEB WORKER
 * Inverted Index & Multilingual Trie Search Engine off the main UI thread.
 */

let indexedObservations = [];
let taxaRegistry = {};
let invertedIndex = new Map(); // token -> Set of observation indices

function normalizeText(text) {
  if (!text) return '';
  return text.toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // strip diacritics
    .replace(/[^a-z0-9\s]/g, ' ')
    .trim();
}

function tokenize(text) {
  const norm = normalizeText(text);
  if (!norm) return [];
  return norm.split(/\s+/).filter(t => t.length > 0);
}

function buildIndex(observations, taxa) {
  indexedObservations = observations || [];
  taxaRegistry = taxa || {};
  invertedIndex = new Map();

  for (let i = 0; i < indexedObservations.length; i++) {
    const obs = indexedObservations[i];
    const tokens = new Set();

    // 1. Taxon names (Latin + Estonian)
    if (obs.taxon) tokenize(obs.taxon).forEach(t => tokens.add(t));
    if (obs.est_name) tokenize(obs.est_name).forEach(t => tokens.add(t));

    // 2. Multilingual vernacular names from normalized taxa registry
    const tKey = obs.taxon_key || obs.taxon_id || obs.taxon;
    const taxonInfo = taxaRegistry[tKey];
    if (taxonInfo) {
      if (taxonInfo.all_names_search) {
        tokenize(taxonInfo.all_names_search).forEach(t => tokens.add(t));
      }
      if (Array.isArray(taxonInfo.vernacular_names)) {
        taxonInfo.vernacular_names.forEach(v => {
          if (v.name) tokenize(v.name).forEach(t => tokens.add(t));
          if (v.est_trans) tokenize(v.est_trans).forEach(t => tokens.add(t));
        });
      }
    }

    // 3. Location, Habitat, Substrate
    if (obs.locality) tokenize(obs.locality).forEach(t => tokens.add(t));
    if (obs.county) tokenize(obs.county).forEach(t => tokens.add(t));
    if (obs.commune) tokenize(obs.commune).forEach(t => tokens.add(t));
    if (obs.habitat) tokenize(obs.habitat).forEach(t => tokens.add(t));
    if (obs.substrate) tokenize(obs.substrate).forEach(t => tokens.add(t));

    // 4. People (Observers, Determiners, Verifiers)
    if (obs.primary_observer) tokenize(obs.primary_observer).forEach(t => tokens.add(t));
    if (obs.collectors) tokenize(obs.collectors).forEach(t => tokens.add(t));
    if (obs.determiner) tokenize(obs.determiner).forEach(t => tokens.add(t));
    if (obs.verified_by) tokenize(obs.verified_by).forEach(t => tokens.add(t));

    // 5. Specimen & Herbarium codes, microscopic notes
    if (obs.specimen_code) tokenize(obs.specimen_code).forEach(t => tokens.add(t));
    if (obs.microscopic_notes) tokenize(obs.microscopic_notes).forEach(t => tokens.add(t));
    if (obs.remarks) tokenize(obs.remarks).forEach(t => tokens.add(t));
    if (obs.id) tokens.add(obs.id.toString());

    // Populate Inverted Index
    tokens.forEach(token => {
      if (!invertedIndex.has(token)) {
        invertedIndex.set(token, new Set());
      }
      invertedIndex.get(token).add(i);
    });
  }
}

function search(query) {
  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) {
    return indexedObservations.map(o => o.id);
  }

  const scoreMap = new Map();

  queryTokens.forEach(qToken => {
    // 1. Exact match
    if (invertedIndex.has(qToken)) {
      invertedIndex.get(qToken).forEach(idx => {
        scoreMap.set(idx, (scoreMap.get(idx) || 0) + 10);
      });
    }

    // 2. Prefix & Substring match
    for (const [token, indexSet] of invertedIndex.entries()) {
      if (token !== qToken && token.startsWith(qToken)) {
        indexSet.forEach(idx => {
          scoreMap.set(idx, (scoreMap.get(idx) || 0) + 5);
        });
      } else if (qToken.length >= 3 && token.includes(qToken)) {
        indexSet.forEach(idx => {
          scoreMap.set(idx, (scoreMap.get(idx) || 0) + 2);
        });
      }
    }
  });

  const sortedIds = Array.from(scoreMap.entries())
    .sort((a, b) => b[1] - a[1])
    .map(entry => indexedObservations[entry[0]].id);

  return sortedIds;
}

self.onmessage = function(e) {
  const { type, observations, taxa, query, id } = e.data;

  if (type === 'INDEX') {
    buildIndex(observations, taxa);
    self.postMessage({ type: 'INDEX_READY', count: indexedObservations.length });
  } else if (type === 'SEARCH') {
    const results = search(query || '');
    self.postMessage({ type: 'SEARCH_RESULTS', query, results, id });
  }
};
