/**
 * Typing Sprint - Word Repositories
 * Curated dictionaries for Programming, Roman Urdu, English Core, and Cyber/Tech
 */

export const WORD_LISTS = {
  programming: [
    // Short (3-5 letters)
    'byte', 'code', 'data', 'loop', 'node', 'null', 'path', 'push', 'root', 'void',
    'ajax', 'async', 'await', 'const', 'false', 'fetch', 'float', 'heap', 'index', 'logic',
    'parse', 'query', 'react', 'scope', 'stack', 'state', 'token', 'true', 'yield', 'array',
    // Medium (6-8 letters)
    'binary', 'buffer', 'commit', 'deploy', 'export', 'filter', 'import', 'lambda', 'memory', 'module',
    'object', 'params', 'promise', 'reduce', 'render', 'router', 'schema', 'script', 'server', 'socket',
    'string', 'syntax', 'thread', 'vector', 'backend', 'boolean', 'closure', 'command', 'compile', 'console',
    'context', 'database', 'debugger', 'function', 'frontend', 'generic', 'handler', 'heritage', 'instance',
    'iterator', 'mutation', 'operator', 'overflow', 'package', 'pipeline', 'pointer', 'protocol', 'reactive',
    // Long (9+ letters)
    'algorithm', 'asynchronous', 'benchmark', 'component', 'concurrency', 'controller', 'declarative',
    'dependency', 'deprecated', 'destructure', 'encapsulate', 'encryption', 'environment', 'executable',
    'expression', 'framework', 'functional', 'immutable', 'inheritance', 'middleware', 'observable',
    'pagination', 'parameters', 'performance', 'polymorphism', 'recursion', 'refactoring', 'repository',
    'responsive', 'scalability', 'serialization', 'synchronous', 'typescript', 'validation', 'vulnerability'
  ],

  romanUrdu: [
    // Everyday & Conversational (3-5 letters)
    'aag', 'aam', 'aql', 'baat', 'chai', 'dard', 'dil', 'dost', 'dua', 'gham',
    'hawa', 'jaan', 'naam', 'pani', 'raat', 'sach', 'saal', 'subh', 'umeed', 'waqt',
    'yaad', 'zabt', 'apna', 'bhai', 'behan', 'khel', 'phool', 'rang', 'soch', 'taara',
    // Rich & Cultural (6-8 letters)
    'barish', 'chirag', 'dariya', 'dostee', 'ehsaas', 'fursat', 'gulaab', 'hansi', 'himmat', 'ishq',
    'jazba', 'junoon', 'kareem', 'khawab', 'khushi', 'koshish', 'manzil', 'mehfil', 'mehar', 'mohabbat',
    'musafir', 'nigaah', 'paighaam', 'parwaaz', 'raasta', 'roshni', 'saaya', 'salam', 'shabnam', 'shandar',
    'shukriya', 'sukoon', 'tabassum', 'tamanna', 'tareef', 'tasveer', 'yaari', 'zindagi', 'zaroorat',
    // Poetic & Expressive (9+ letters)
    'afreenish', 'ahmiyat', 'aitbaar', 'bahaaristaan', 'chaandni', 'darakhshaan', 'ehteraam',
    'farmaaish', 'humsafar', 'intezaar', 'iqbaal', 'izzatdaar', 'jaanisar', 'khamoshi', 'khushamdeed',
    'khoobsurat', 'mahekaan', 'masoomiyat', 'muqaddar', 'muntazir', 'nawaazish', 'pasandeeda',
    'rehnumaee', 'roshanraah', 'sarbuland', 'shaadmani', 'sharmindagi', 'shafaqat', 'shujaat',
    'tabdeeli', 'tashakkur', 'yakjehti', 'zindadili', 'zauq-e-nazar'
  ],

  english: [
    // Short
    'glow', 'wave', 'flux', 'echo', 'mist', 'star', 'fire', 'wind', 'bold', 'peak',
    'swift', 'spark', 'storm', 'ocean', 'prism', 'bloom', 'blaze', 'orbit', 'pulse', 'frost',
    // Medium
    'cascade', 'crystal', 'horizon', 'journey', 'dynamic', 'gravity', 'radiant', 'phantom',
    'kinetic', 'solitude', 'breeze', 'courage', 'freedom', 'harmony', 'infinite', 'luminous',
    'monarch', 'nebula', 'odyssey', 'pioneer', 'quantum', 'serenity', 'twilight', 'venture',
    // Long
    'celestial', 'brilliance', 'constellation', 'equilibrium', 'extraordinary', 'fascinating',
    'kaleidoscope', 'magnificent', 'metamorphosis', 'persistence', 'phenomenon', 'resilience',
    'spectacular', 'transcendence', 'unconditional', 'vulnerability', 'wonderstruck'
  ],

  cyberpunk: [
    // Tech & Cyber theme
    'grid', 'neon', 'warp', 'core', 'mech', 'cyber', 'drone', 'glitch', 'laser', 'matrix',
    'cyborg', 'daemon', 'hacker', 'neural', 'plasma', 'silicon', 'synapse', 'uplink', 'vector',
    'augmented', 'bandwidth', 'biometric', 'mainframe', 'nanotech', 'overclock', 'quantum',
    'satellite', 'synthetic', 'terminal', 'transistor', 'cybernetic', 'decentralized', 'holographic',
    'hyperdrive', 'infrastructure', 'interstellar', 'nanoseconds', 'neuroplastic', 'supercluster'
  ]
};

// Default custom word list to seed user experience
export const DEFAULT_CUSTOM_WORDS = [
  'fast', 'focus', 'speed', 'sprint', 'reflex', 'precision',
  'accuracy', 'velocity', 'challenge', 'champion', 'momentum', 'perfection'
];

/**
 * Normalizes input text into a clean array of unique alphanumeric words
 * @param {string} text 
 * @returns {string[]}
 */
export function parseCustomWords(text) {
  if (!text || typeof text !== 'string') return [];
  // Split on whitespace, commas, semicolons, newlines
  const rawWords = text.split(/[\s,;\n\r\t]+/);
  const cleanSet = new Set();

  for (const raw of rawWords) {
    // Keep letters, hyphens, and digits (allow Roman Urdu with apostrophe/hyphen or programming tokens)
    const cleaned = raw.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '');
    if (cleaned.length >= 2 && cleaned.length <= 25) {
      cleanSet.add(cleaned);
    }
  }

  return Array.from(cleanSet);
}

/**
 * Gets a random word from the specified pool with optional length biasing
 * @param {string} categoryKey 
 * @param {string[]} [customPool] 
 * @param {number} [targetMinLength=2]
 * @returns {string}
 */
export function getRandomWord(categoryKey, customPool = null, targetMinLength = 2) {
  let pool = WORD_LISTS[categoryKey];
  if (categoryKey === 'custom' && customPool && customPool.length > 0) {
    pool = customPool;
  }
  if (!pool || pool.length === 0) {
    pool = WORD_LISTS.english;
  }

  // Pick random
  const idx = Math.floor(Math.random() * pool.length);
  return pool[idx];
}
