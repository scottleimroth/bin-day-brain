// Bin Day Brain - Web App
// © 2026 Scott Leimroth

// API via Cloudflare Worker proxy (bypasses CORS)
const API_BASE = 'https://bin-day-brain-proxy.scott-leimroth.workers.dev';
const WEATHER_API = 'https://api.open-meteo.com/v1/forecast';
const WOLLONGONG_LAT = -34.4278;
const WOLLONGONG_LON = 150.8931;

// State
let localities = [];
let streets = [];
let properties = [];
let materials = [];
let selectedPropertyId = null;
let config = null;
let cache = null;

// DOM Elements
const setupScreen = document.getElementById('setup-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const localityInput = document.getElementById('locality-input');
const localityDropdown = document.getElementById('locality-dropdown');
const streetInput = document.getElementById('street-input');
const streetDropdown = document.getElementById('street-dropdown');
const propertyInput = document.getElementById('property-input');
const propertyDropdown = document.getElementById('property-dropdown');
const setupStatus = document.getElementById('setup-status');
const completeSetupBtn = document.getElementById('complete-setup-btn');
const statusLabel = document.getElementById('status-label');
const alertsContainer = document.getElementById('alerts-container');
const whichBinModal = document.getElementById('which-bin-modal');
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const searchResultsCount = document.getElementById('search-results-count');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    loadConfig();

    if (config && config.setup_completed) {
        showDashboard();
        loadCachedData();
        refreshData();
    } else {
        showSetup();
        loadLocalities();
    }

    setupEventListeners();
}

function setupEventListeners() {
    // Setup screen
    localityInput.addEventListener('input', () => filterDropdown(localityInput, localityDropdown, localities, 'name'));
    localityInput.addEventListener('focus', () => showDropdown(localityDropdown, localities, 'name'));
    streetInput.addEventListener('input', () => filterDropdown(streetInput, streetDropdown, streets, 'name'));
    streetInput.addEventListener('focus', () => showDropdown(streetDropdown, streets, 'name'));
    propertyInput.addEventListener('input', () => filterDropdown(propertyInput, propertyDropdown, properties, 'name'));
    propertyInput.addEventListener('focus', () => showDropdown(propertyDropdown, properties, 'name'));

    completeSetupBtn.addEventListener('click', completeSetup);

    // Dashboard
    document.getElementById('change-address-btn').addEventListener('click', () => {
        showSetup();
        loadLocalities();
    });
    document.getElementById('which-bin-btn').addEventListener('click', openWhichBinModal);
    document.getElementById('refresh-btn').addEventListener('click', () => refreshData(false));

    // Modal
    document.getElementById('close-modal-btn').addEventListener('click', closeWhichBinModal);
    whichBinModal.addEventListener('click', (e) => {
        if (e.target === whichBinModal) closeWhichBinModal();
    });
    searchInput.addEventListener('input', filterMaterials);

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.form-group')) {
            hideAllDropdowns();
        }
    });
}

// Storage
function loadConfig() {
    const stored = localStorage.getItem('binDayBrain_config');
    config = stored ? JSON.parse(stored) : null;
}

function saveConfig(data) {
    config = data;
    localStorage.setItem('binDayBrain_config', JSON.stringify(data));
}

function loadCachedData() {
    const stored = localStorage.getItem('binDayBrain_cache');
    cache = stored ? JSON.parse(stored) : null;

    if (cache) {
        // Apply fallback calculation if needed
        if ((!cache.collections || cache.collections.length === 0) && cache.collection_day) {
            cache.collections = calculateCollections(cache.collection_day);
        }
        if (cache.collections && cache.collections.length > 0) {
            updateCards(cache.collections);
            statusLabel.textContent = `Using cached data`;
        }
    }
}

function saveCache(data) {
    data.cached_at = new Date().toISOString();
    cache = data;
    localStorage.setItem('binDayBrain_cache', JSON.stringify(data));
}

// Screens
function showSetup() {
    setupScreen.classList.remove('hidden');
    dashboardScreen.classList.add('hidden');
}

function showDashboard() {
    setupScreen.classList.add('hidden');
    dashboardScreen.classList.remove('hidden');
}

// API calls - Note: This API has CORS restrictions
// For production, you'll need to either:
// 1. Host on same domain as API allows
// 2. Use a backend proxy
// 3. Use a CORS proxy service
async function apiGet(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('API error');
        return await response.json();
    } catch (error) {
        console.error('API error:', error);
        return null;
    }
}

// Setup functions
async function loadLocalities() {
    setupStatus.textContent = 'Loading suburbs...';
    setupStatus.classList.remove('error');

    const data = await apiGet(`${API_BASE}/localities.json`);

    if (data && data.localities) {
        localities = data.localities.sort((a, b) => a.name.localeCompare(b.name));
        localityInput.disabled = false;
        localityInput.placeholder = 'Type to search suburbs...';
        setupStatus.textContent = '';
    } else {
        setupStatus.textContent = 'Error loading suburbs. The API may block browser requests (CORS). Try the desktop or Android app instead.';
        setupStatus.classList.add('error');
    }
}

async function onLocalitySelected(locality) {
    localityInput.value = locality.name;
    hideAllDropdowns();

    streetInput.value = '';
    streetInput.disabled = true;
    propertyInput.value = '';
    propertyInput.disabled = true;
    completeSetupBtn.disabled = true;
    selectedPropertyId = null;

    setupStatus.textContent = 'Loading streets...';
    setupStatus.classList.remove('error');

    const data = await apiGet(`${API_BASE}/streets.json?locality=${locality.id}`);

    if (data && data.streets) {
        streets = data.streets.sort((a, b) => a.name.localeCompare(b.name));
        streetInput.disabled = false;
        streetInput.placeholder = 'Type to search streets...';
        setupStatus.textContent = '';
    } else {
        setupStatus.textContent = 'Error loading streets.';
        setupStatus.classList.add('error');
    }
}

async function onStreetSelected(street) {
    streetInput.value = street.name;
    hideAllDropdowns();

    propertyInput.value = '';
    propertyInput.disabled = true;
    completeSetupBtn.disabled = true;
    selectedPropertyId = null;

    setupStatus.textContent = 'Loading properties...';
    setupStatus.classList.remove('error');

    const data = await apiGet(`${API_BASE}/properties.json?street=${street.id}`);

    if (data && data.properties) {
        properties = data.properties.sort((a, b) => a.name.localeCompare(b.name));
        propertyInput.disabled = false;
        propertyInput.placeholder = 'Type to search properties...';
        setupStatus.textContent = '';
    } else {
        setupStatus.textContent = 'Error loading properties.';
        setupStatus.classList.add('error');
    }
}

function onPropertySelected(property) {
    propertyInput.value = property.name;
    hideAllDropdowns();
    selectedPropertyId = property.id;
    completeSetupBtn.disabled = false;
    setupStatus.textContent = `Selected: ${property.name}`;
    setupStatus.classList.remove('error');
    setupStatus.classList.add('success');
}

async function completeSetup() {
    if (!selectedPropertyId) return;

    saveConfig({
        property_id: selectedPropertyId,
        setup_completed: true,
        setup_date: new Date().toISOString()
    });

    showDashboard();
    refreshData();
}

// Dropdown functions
function showDropdown(dropdown, items, key) {
    if (items.length === 0) return;
    renderDropdown(dropdown, items, key);
    dropdown.classList.add('show');
}

function hideAllDropdowns() {
    localityDropdown.classList.remove('show');
    streetDropdown.classList.remove('show');
    propertyDropdown.classList.remove('show');
}

function filterDropdown(input, dropdown, items, key) {
    const query = input.value.toLowerCase();
    const filtered = items.filter(item => item[key].toLowerCase().includes(query));
    renderDropdown(dropdown, filtered, key);
    dropdown.classList.add('show');
}

function renderDropdown(dropdown, items, key) {
    dropdown.innerHTML = items.slice(0, 100).map(item =>
        `<div class="dropdown-item" data-id="${item.id}">${item[key]}</div>`
    ).join('');

    dropdown.querySelectorAll('.dropdown-item').forEach(el => {
        el.addEventListener('click', () => {
            const id = parseInt(el.dataset.id);
            const item = items.find(i => i.id === id);

            if (dropdown === localityDropdown) onLocalitySelected(item);
            else if (dropdown === streetDropdown) onStreetSelected(item);
            else if (dropdown === propertyDropdown) onPropertySelected(item);
        });
    });
}

// Dashboard functions
async function refreshData(silent = true) {
    if (!config || !config.property_id) return;

    if (!silent) {
        statusLabel.textContent = 'Refreshing...';
        document.getElementById('refresh-btn').disabled = true;
    }

    const data = await apiGet(`${API_BASE}/properties/${config.property_id}.json`);

    if (data) {
        // If API returns empty collections, calculate from collection_day
        if ((!data.collections || data.collections.length === 0) && data.collection_day) {
            data.collections = calculateCollections(data.collection_day);
        }
        saveCache(data);
        updateCards(data.collections || []);
        statusLabel.textContent = `Last updated: ${new Date().toLocaleString()}`;
        loadWeather();
    } else if (!silent) {
        statusLabel.textContent = 'Error refreshing. Using cached data.';
    }

    document.getElementById('refresh-btn').disabled = false;
}

// Calculate collection dates from collection_day (1=Mon, 2=Tue, etc.)
function calculateCollections(collectionDay) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Find next occurrence of collection day
    // API uses 1=Mon, JS getDay() uses 0=Sun, so convert
    const jsDay = collectionDay === 7 ? 0 : collectionDay; // 7=Sun -> 0
    let daysAhead = jsDay - today.getDay();
    if (daysAhead < 0) daysAhead += 7;

    const nextCollection = new Date(today);
    nextCollection.setDate(today.getDate() + daysAhead);

    // Get ISO week number to determine recycling/landfill week
    const weekNum = getISOWeek(nextCollection);
    const isRecyclingWeek = (weekNum % 2 === 0);

    const nextCollectionStr = nextCollection.toISOString().split('T')[0] + 'T06:00:00+11:00';

    const weekLater = new Date(nextCollection);
    weekLater.setDate(nextCollection.getDate() + 7);
    const weekLaterStr = weekLater.toISOString().split('T')[0] + 'T06:00:00+11:00';

    return [
        { type: 'FOGO', next: { date: nextCollectionStr } },
        { type: 'Recycling', next: { date: isRecyclingWeek ? nextCollectionStr : weekLaterStr } },
        { type: 'Landfill', next: { date: isRecyclingWeek ? weekLaterStr : nextCollectionStr } }
    ];
}

// Get ISO week number
function getISOWeek(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 4 - (d.getDay() || 7));
    const yearStart = new Date(d.getFullYear(), 0, 1);
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

function updateCards(collections) {
    collections.forEach(collection => {
        const type = (collection.type || '').toLowerCase();
        const nextDate = collection.next?.date;

        let card;
        if (type.includes('fogo') || type.includes('organic')) {
            card = document.getElementById('fogo-card');
        } else if (type.includes('recycling')) {
            card = document.getElementById('recycling-card');
        } else if (type.includes('landfill') || type.includes('garbage') || type.includes('waste')) {
            card = document.getElementById('landfill-card');
        }

        if (card && nextDate) {
            const date = new Date(nextDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            date.setHours(0, 0, 0, 0);

            const diffDays = Math.ceil((date - today) / (1000 * 60 * 60 * 24));

            card.querySelector('.days-count').textContent = diffDays;
            card.querySelector('.days-label').textContent = diffDays === 1 ? 'day until collection' : 'days until collection';
            card.querySelector('.collection-date').textContent = date.toLocaleDateString('en-AU', {
                day: '2-digit',
                month: 'long',
                year: 'numeric'
            });
        }
    });
}

async function loadWeather() {
    // Find nearest collection date
    let nearestDate = null;
    document.querySelectorAll('.bin-card .collection-date').forEach(el => {
        if (el.textContent) {
            const date = new Date(el.textContent);
            if (!nearestDate || date < nearestDate) {
                nearestDate = date;
            }
        }
    });

    if (!nearestDate) return;

    const today = new Date();
    const daysAhead = Math.ceil((nearestDate - today) / (1000 * 60 * 60 * 24));

    if (daysAhead < 0 || daysAhead > 7) return;

    try {
        const response = await fetch(
            `${WEATHER_API}?latitude=${WOLLONGONG_LAT}&longitude=${WOLLONGONG_LON}&daily=precipitation_sum,wind_speed_10m_max&timezone=Australia/Sydney&forecast_days=${daysAhead + 1}`
        );
        const data = await response.json();

        if (data.daily) {
            const wind = data.daily.wind_speed_10m_max[daysAhead];
            const rain = data.daily.precipitation_sum[daysAhead];

            alertsContainer.innerHTML = '';

            if (wind >= 40) {
                const alertEl = document.createElement('div');
                alertEl.className = `alert ${wind >= 50 ? 'alert-warning' : 'alert-info'}`;
                alertEl.textContent = `Windy (${Math.round(wind)} km/h) on collection day - secure your bins!`;
                alertsContainer.appendChild(alertEl);
            }

            if (rain >= 5) {
                const alertEl = document.createElement('div');
                alertEl.className = 'alert alert-info';
                alertEl.textContent = `Rain expected (${Math.round(rain)}mm) - good for weighing down FOGO`;
                alertsContainer.appendChild(alertEl);
            }
        }
    } catch (error) {
        console.error('Weather error:', error);
    }
}

// Which Bin Modal
async function openWhichBinModal() {
    whichBinModal.classList.remove('hidden');
    searchInput.value = '';
    searchInput.focus();

    if (materials.length === 0) {
        searchResults.innerHTML = '<p class="loading">Loading materials...</p>';
        const data = await apiGet(`${API_BASE}/materials.json`);
        if (data && data.materials) {
            materials = data.materials.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
            filterMaterials();
        } else {
            searchResults.innerHTML = '<p class="loading">Error loading materials.</p>';
        }
    } else {
        filterMaterials();
    }
}

function closeWhichBinModal() {
    whichBinModal.classList.add('hidden');
}

function filterMaterials() {
    const query = searchInput.value.toLowerCase();
    const filtered = query
        ? materials.filter(m => (m.title || '').toLowerCase().includes(query))
        : materials;

    searchResultsCount.textContent = `${filtered.length} items`;

    searchResults.innerHTML = filtered.map(item => {
        // Check both disposal and bin_type fields
        const disposal = (item.disposal || item.bin_type || 'waste').toLowerCase();
        const colorClass = getBinColorClass(disposal);
        const binName = getBinName(disposal);
        const tip = item.tip || '';

        return `
            <div class="result-item ${colorClass}">
                <h3>${item.title || 'Unknown'}</h3>
                <span class="bin-name">${binName}</span>
                ${tip ? `<p class="tip">${tip}</p>` : ''}
            </div>
        `;
    }).join('');
}

function getBinColorClass(disposal) {
    switch (disposal) {
        case 'recycle':
        case 'recycling':
            return 'recycle';
        case 'organic':
        case 'fogo':
            return 'organic';
        case 'waste':
        case 'landfill':
        case 'garbage':
            return 'waste';
        case 'crc':
            return 'crc';
        case 'special':
            return 'special';
        case 'clean_up':
            return 'clean_up';
        default:
            return 'waste';
    }
}

function getBinName(disposal) {
    switch (disposal) {
        case 'recycle':
        case 'recycling':
            return 'Yellow Recycling Bin';
        case 'organic':
        case 'fogo':
            return 'Green FOGO Bin';
        case 'waste':
        case 'landfill':
        case 'garbage':
            return 'Red Landfill Bin';
        case 'crc':
            return 'Community Recycling Centre';
        case 'special':
            return 'Special Disposal';
        case 'clean_up':
            return 'Council Clean-up';
        default:
            return 'Red Landfill Bin';
    }
}

// Service Worker Registration (for PWA)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(err => console.log('SW registration failed:', err));
}
