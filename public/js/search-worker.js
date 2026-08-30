/**
 * FUNGIB MYCOLOGY ARCHIVE - HIGH-PRECISION CONJUNCTIVE FUZZY SEARCH WEB WORKER
 * Strict multi-term AND matching with field-weighted relevance ranking.
 */

let indexedDocs = [];

function normalizeText(text) {
  if (!text) return '';
  return text.toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9äöüõšž\s-]/g, ' ')
    .trim();
}

function tokenize(text) {
  const norm = normalizeText(text);
  if (!norm) return [];
  return norm.split(/\s+/).filter(t => t.length > 0);
}

function buildIndex(observations, taxa) {
  const obsList = observations || [];
  const taxaRegistry = taxa || {};
  indexedDocs = [];

  for (let i = 0; i < obsList.length; i++) {
    const obs = obsList[i];
    const tKey = obs.taxon_key || obs.taxon_id || obs.taxon;
    const taxonInfo = taxaRegistry[tKey] || {};

    const est_name = normalizeText(obs.est_name || '');
    const taxon = normalizeText(obs.taxon || '');
    const all_names = normalizeText(taxonInfo.all_names_search || obs.all_names_search || '');
    const locality = normalizeText(obs.locality || '');
    const county = normalizeText(obs.county || '');
    const commune = normalizeText(obs.commune || '');
    const observer = normalizeText(obs.primary_observer || '');
    const collectors = normalizeText(obs.collectors || '');
    const notes = normalizeText((obs.microscopic_notes || '') + ' ' + (obs.remarks || '') + ' ' + (obs.specimen_code || '') + ' ' + (obs.id || ''));

    indexedDocs.push({
      id: obs.id,
      index: i,
      est_name,
      est_tokens: tokenize(est_name),
      taxon,
      taxon_tokens: tokenize(taxon),
      all_names,
      all_names_tokens: tokenize(all_names),
      meta: `${locality} ${county} ${commune} ${observer} ${collectors} ${notes}`,
      meta_tokens: tokenize(`${locality} ${county} ${commune} ${observer} ${collectors} ${notes}`)
    });
  }
}

function search(query) {
  const qNorm = normalizeText(query);
  const qTokens = tokenize(query);
  if (qTokens.length === 0) {
    return { results: indexedDocs.map(d => d.id), scores: {} };
  }

  const scoredResults = [];

  for (let i = 0; i < indexedDocs.length; i++) {
    const doc = indexedDocs[i];
    let allTokensMatched = true;
    let totalScore = 0;

    // 1. Exact full phrase matching boosts
    if (doc.est_name && doc.est_name.includes(qNorm)) {
      totalScore += 1000;
    } else if (doc.taxon && doc.taxon.includes(qNorm)) {
      totalScore += 800;
    } else if (doc.all_names && doc.all_names.includes(qNorm)) {
      totalScore += 600;
    } else if (doc.meta && doc.meta.includes(qNorm)) {
      totalScore += 400;
    }

    // 2. Strict conjunctive (AND) matching for all query tokens
    for (let t = 0; t < qTokens.length; t++) {
      const qToken = qTokens[t];
      let tokenMatched = false;

      // Check Estonian name
      for (let w = 0; w < doc.est_tokens.length; w++) {
        const word = doc.est_tokens[w];
        if (word === qToken) {
          tokenMatched = true;
          totalScore += 150;
          break;
        } else if (word.startsWith(qToken)) {
          tokenMatched = true;
          totalScore += 120;
          break;
        } else if (qToken.length >= 4 && (word.endsWith(qToken) || word.includes(qToken))) {
          // Compound words e.g. "põdranapsik" matches "napsik"
          tokenMatched = true;
          totalScore += 100;
          break;
        }
      }

      // Check Latin taxon
      if (!tokenMatched) {
        for (let w = 0; w < doc.taxon_tokens.length; w++) {
          const word = doc.taxon_tokens[w];
          if (word === qToken) {
            tokenMatched = true;
            totalScore += 130;
            break;
          } else if (word.startsWith(qToken)) {
            tokenMatched = true;
            totalScore += 100;
            break;
          }
        }
      }

      // Check Multilingual vernacular names
      if (!tokenMatched) {
        for (let w = 0; w < doc.all_names_tokens.length; w++) {
          const word = doc.all_names_tokens[w];
          if (word === qToken) {
            tokenMatched = true;
            totalScore += 80;
            break;
          } else if (word.startsWith(qToken) || (qToken.length >= 4 && word.endsWith(qToken))) {
            tokenMatched = true;
            totalScore += 60;
            break;
          }
        }
      }

      // Check Location, Observers, Specimen notes
      if (!tokenMatched) {
        for (let w = 0; w < doc.meta_tokens.length; w++) {
          const word = doc.meta_tokens[w];
          if (word === qToken) {
            tokenMatched = true;
            totalScore += 40;
            break;
          } else if (word.startsWith(qToken)) {
            tokenMatched = true;
            totalScore += 30;
            break;
          }
        }
      }

      if (!tokenMatched) {
        allTokensMatched = false;
        break;
      }
    }

    if (allTokensMatched && totalScore > 0) {
      scoredResults.push({ id: doc.id, score: totalScore });
    }
  }

  scoredResults.sort((a, b) => b.score - a.score);

  const scores = {};
  scoredResults.forEach(r => { scores[r.id] = r.score; });

  return {
    results: scoredResults.map(r => r.id),
    scores
  };
}

self.onmessage = function(e) {
  const { type, observations, taxa, query, id } = e.data;

  if (type === 'INDEX') {
    buildIndex(observations, taxa);
    self.postMessage({ type: 'INDEX_READY', count: indexedDocs.length });
  } else if (type === 'SEARCH') {
    const { results, scores } = search(query || '');
    self.postMessage({ type: 'SEARCH_RESULTS', query, results, scores, id });
  }
};
