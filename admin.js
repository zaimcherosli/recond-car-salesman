let currentCars = [];
let globalSettings = {};
let currentTab = 'top-ads';
let currentEditingCar = null;

async function initAdminApp() {
    try {
        const carsRes = await fetch('admin_inventory.json');
        currentCars = await carsRes.json();
    } catch (e) {
        console.warn('Could not fetch admin_inventory.json directly, falling back to embedded/empty data');
    }

    try {
        const setRes = await fetch('pricing_settings.json');
        globalSettings = await setRes.json();
    } catch (e) {
        globalSettings = {
            default_otr_addition_ncd55: 7000,
            default_otr_addition_ncd0: 10000,
            default_negotiation_buffer: 1800,
            freshness_threshold_fresh_days: 7,
            freshness_threshold_moderate_days: 14
        };
    }

    // Load saved settings from LocalStorage
    const savedSettings = localStorage.getItem('prestige_pricing_settings');
    if (savedSettings) {
        try { globalSettings = JSON.parse(savedSettings); } catch(e){}
    }

    // Load saved overrides from LocalStorage
    const savedOverrides = localStorage.getItem('prestige_market_overrides');
    if (savedOverrides) {
        try {
            const overrides = JSON.parse(savedOverrides);
            currentCars = currentCars.map(car => {
                const key = car.unique_key || (car.stock_no + '_' + (car.chassis || ''));
                if (overrides[key]) {
                    return { ...car, ...overrides[key] };
                }
                return car;
            });
        } catch(e){}
    }

    updateStatCounters();
    renderTopAds();
    renderInventoryTable();
    populateSettingsUI();
}

function switchTab(tabId, btn) {
    currentTab = tabId;
    ['top-ads', 'inventory', 'settings', 'import-export'].forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        if (el) el.classList.toggle('hidden', t !== tabId);
    });
    document.querySelectorAll('.admin-tab-btn').forEach(b => {
        b.classList.remove('bg-amber-400', 'text-slate-950', 'font-extrabold');
        b.classList.add('text-slate-300');
    });
    if (btn) {
        btn.classList.remove('text-slate-300');
        btn.classList.add('bg-amber-400', 'text-slate-950', 'font-extrabold');
    }
}

function updateStatCounters() {
    const totalEl = document.getElementById('stat-total-cars');
    if (totalEl) totalEl.innerText = currentCars.length;

    const fresh = currentCars.filter(c => c.market_freshness === 'FRESH').length;
    const freshEl = document.getElementById('stat-fresh-cars');
    if (freshEl) freshEl.innerText = fresh;

    const topAds = currentCars.filter(c => (c.ad_score || 0) >= 8.5 && (c.available_market_spread || 0) >= 3000).length;
    const topAdsEl = document.getElementById('stat-top-ads-count');
    if (topAdsEl) topAdsEl.innerText = topAds;

    const unres = currentCars.filter(c => c.pricing_status === 'UNRESEARCHED' || !c.market_median).length;
    const unresEl = document.getElementById('stat-unresearched');
    if (unresEl) unresEl.innerText = unres;

    const totalSpread = currentCars.reduce((acc, c) => acc + Math.max(0, c.available_market_spread || 0), 0);
    const spreadEl = document.getElementById('stat-total-spread');
    if (spreadEl) spreadEl.innerText = `RM ${(totalSpread/1000).toFixed(0)}k`;
}

function renderTopAds() {
    const grid = document.getElementById('top-ads-grid');
    if (!grid) return;

    const brand = document.getElementById('top-ads-brand-filter')?.value || 'all';
    let list = currentCars.filter(c => (c.ad_score || 0) >= 7.0 && (c.market_median || 0) > 0);
    if (brand !== 'all') {
        list = list.filter(c => c.brand && c.brand.toLowerCase() === brand.toLowerCase());
    }

    list.sort((a, b) => (b.ad_score || 0) - (a.ad_score || 0));

    if (list.length === 0) {
        grid.innerHTML = '<div class="col-span-full py-16 text-center text-slate-500 bg-slate-900 rounded-3xl border border-slate-800">Tiada cadangan iklan ditemui untuk penapis ini.</div>';
        return;
    }

    grid.innerHTML = list.map(car => {
        const cover = car.thumbnail || (car.images && car.images[0]) || 'public/cars/placeholder.jpg';
        const saving = Math.max(0, (car.market_median || 0) - (car.advertised_price_ncd55 || 0));
        
        return `
        <div class="bg-slate-900 rounded-3xl border border-slate-800 overflow-hidden shadow-xl hover:border-amber-500/50 transition-all flex flex-col justify-between group">
            <div class="relative aspect-[16/10] bg-slate-950 overflow-hidden">
                <img src="${cover}" alt="${car.model}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" onerror="this.src='public/cars/placeholder.jpg'">
                <div class="absolute top-3 left-3 flex gap-1.5 flex-wrap">
                    <span class="px-2.5 py-1 rounded-full bg-slate-950/90 text-amber-300 font-mono text-[10px] font-bold border border-amber-500/30">STOCK: ${car.stock_no}</span>
                    <span class="px-2.5 py-1 rounded-full bg-emerald-950/90 text-emerald-400 font-mono text-[10px] font-bold border border-emerald-500/30">${car.status || 'Ready Stock'}</span>
                </div>
                <div class="absolute top-3 right-3">
                    <div class="px-3 py-1 rounded-full bg-amber-400 text-slate-950 font-display font-extrabold text-xs shadow-lg flex items-center gap-1">
                        <span>🔥 AD SCORE:</span>
                        <span class="text-sm">${car.ad_score || 8.5}</span>
                    </div>
                </div>
                <div class="absolute bottom-3 left-3 bg-slate-950/85 backdrop-blur-md px-3 py-1 rounded-lg text-white font-mono text-[11px]">
                    GRED ${car.grade || '4.5A'} • ${car.year}
                </div>
            </div>

            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
                <div>
                    <span class="text-[11px] font-bold text-amber-400 uppercase tracking-wider">${car.brand} • ${car.category}</span>
                    <h3 class="font-display text-lg font-bold text-white mt-0.5 leading-snug">${car.model}</h3>
                    <div class="text-xs text-slate-400 mt-1">${car.color} • ${car.mileage}</div>

                    <div class="mt-4 p-3.5 rounded-2xl bg-slate-950 border border-slate-800 space-y-2 text-xs font-mono">
                        <div class="flex justify-between text-slate-400"><span>Body Price (Dealer):</span><span class="text-white font-bold">RM ${(car.body_price || 0).toLocaleString()}</span></div>
                        <div class="flex justify-between text-slate-400"><span>Est. OTR (55% NCD):</span><span class="text-amber-400 font-bold">RM ${(car.advertised_price_ncd55 || 0).toLocaleString()}</span></div>
                        <div class="flex justify-between text-slate-400"><span>Median Pasaran:</span><span class="text-slate-300 font-semibold">RM ${(car.market_median || 0).toLocaleString()}</span></div>
                        <div class="pt-1.5 border-t border-slate-800/80 flex justify-between font-bold">
                            <span class="text-emerald-400">Potensi Kelebihan OTR:</span>
                            <span class="text-emerald-400">+RM ${saving.toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                <div class="space-y-2 pt-2 border-t border-slate-800">
                    <div class="flex justify-between items-center text-xs font-mono">
                        <span class="text-slate-400">Cadangan Komisen:</span>
                        <span class="text-white font-bold">RM ${(car.suggested_commission || 5000).toLocaleString()}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <button onclick="openEditCarModal('${car.unique_key || car.stock_no}')" class="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs transition-all text-center">
                            Edit Risikan ✏️
                        </button>
                        <a href="https://wa.me/60108118559?text=${encodeURIComponent(`Salam, saya nak semak unit ${car.model} (${car.stock_no}) harga OTR RM ${(car.advertised_price_ncd55||0).toLocaleString()}`)}" target="_blank" class="py-2.5 px-3 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white font-bold text-xs uppercase tracking-wider text-center">
                            Copy Iklan 📲
                        </a>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join('');
}

let invPage = 1;
const INV_PER_PAGE = 15;
let filteredInvList = [];

function filterInventoryTable() {
    const query = (document.getElementById('inv-search')?.value || '').toLowerCase().trim();
    const brand = document.getElementById('inv-filter-brand')?.value || 'all';
    const status = document.getElementById('inv-filter-status')?.value || 'all';
    const fresh = document.getElementById('inv-filter-freshness')?.value || 'all';

    filteredInvList = currentCars.filter(car => {
        if (brand !== 'all' && car.brand && car.brand.toLowerCase() !== brand.toLowerCase()) return false;
        if (status !== 'all' && car.pricing_status !== status) return false;
        if (fresh !== 'all' && car.market_freshness !== fresh) return false;

        if (!query) return true;
        const searchStr = `${car.stock_no} ${car.model} ${car.chassis} ${car.brand}`.toLowerCase();
        return searchStr.includes(query);
    });

    invPage = 1;
    renderInventoryTable();
}

function renderInventoryTable() {
    const tbody = document.getElementById('inventory-table-body');
    if (!tbody) return;

    if (filteredInvList.length === 0 && currentCars.length > 0) {
        filteredInvList = [...currentCars];
    }

    const total = filteredInvList.length;
    const totalPages = Math.ceil(total / INV_PER_PAGE) || 1;
    if (invPage > totalPages) invPage = totalPages;
    const start = (invPage - 1) * INV_PER_PAGE;
    const end = Math.min(start + INV_PER_PAGE, total);
    const pageList = filteredInvList.slice(start, end);

    if (pageList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="p-8 text-center text-slate-500 font-sans">Tiada padanan inventori ditemui.</td></tr>';
        renderTablePagination(0, 0, 0);
        return;
    }

    tbody.innerHTML = pageList.map(car => {
        let freshBadge = '<span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">Unresearched</span>';
        if (car.market_freshness === 'FRESH') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30 text-[10px]">Segar (≤7h)</span>';
        } else if (car.market_freshness === 'MODERATE') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-amber-950 text-amber-400 border border-amber-500/30 text-[10px]">8-14 Hari</span>';
        } else if (car.market_freshness === 'STALE') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-rose-950 text-rose-400 border border-rose-500/30 text-[10px]">Lapuk (>14h)</span>';
        }

        const spread = car.available_market_spread || 0;
        const spreadClass = spread >= 5000 ? 'text-emerald-400 font-bold' : (spread > 0 ? 'text-amber-300' : 'text-slate-500');

        return `
        <tr class="hover:bg-slate-800/50 transition-colors">
            <td class="p-3.5">
                <div class="font-bold text-white text-xs">${car.model}</div>
                <div class="text-[10px] text-slate-400 font-mono">STOCK: ${car.stock_no} • ${car.year}</div>
            </td>
            <td class="p-3.5 text-slate-300 font-semibold">RM ${(car.body_price || 0).toLocaleString()}</td>
            <td class="p-3.5 text-amber-300">RM ${(car.estimated_otr_base_ncd55 || 0).toLocaleString()}</td>
            <td class="p-3.5 text-slate-300 font-semibold">${car.market_median ? 'RM ' + car.market_median.toLocaleString() : '<span class="text-slate-600">-</span>'}</td>
            <td class="p-3.5 ${spreadClass}">${spread > 0 ? '+RM ' + spread.toLocaleString() : '<span class="text-slate-600">-</span>'}</td>
            <td class="p-3.5 text-white font-bold">RM ${(car.suggested_commission || 0).toLocaleString()}</td>
            <td class="p-3.5 text-amber-400 font-bold font-sans">${car.advertised_price_ncd55 ? 'RM ' + car.advertised_price_ncd55.toLocaleString() : 'Bincang'}</td>
            <td class="p-3.5"><span class="px-2 py-0.5 rounded-md bg-slate-950 font-bold text-amber-400 border border-slate-800">${car.ad_score || '-'}</span></td>
            <td class="p-3.5">${freshBadge}</td>
            <td class="p-3.5 text-right">
                <button onclick="openEditCarModal('${car.unique_key || car.stock_no}')" class="px-3 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-500 text-slate-950 font-bold text-[11px] uppercase transition-all">
                    Edit
                </button>
            </td>
        </tr>
        `;
    }).join('');

    renderTablePagination(start + 1, end, total);
}

function renderTablePagination(start, end, total) {
    const info = document.getElementById('inv-table-info');
    const btns = document.getElementById('inv-table-pagination');
    if (info) info.innerText = `Menunjukkan ${start} - ${end} daripada ${total} unit`;

    const totalPages = Math.ceil(total / INV_PER_PAGE) || 1;
    let html = '';
    if (invPage > 1) {
        html += `<button onclick="setInvPage(${invPage-1})" class="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-xs">‹ Prev</button>`;
    }
    html += `<span class="px-3 py-1 font-mono text-xs text-amber-400 font-bold">${invPage} / ${totalPages}</span>`;
    if (invPage < totalPages) {
        html += `<button onclick="setInvPage(${invPage+1})" class="px-2.5 py-1 rounded bg-slate-800 text-slate-300 text-xs">Next ›</button>`;
    }
    if (btns) btns.innerHTML = html;
}

function setInvPage(p) {
    invPage = p;
    renderInventoryTable();
}

function openEditCarModal(identifier) {
    const car = currentCars.find(c => (c.unique_key === identifier || c.stock_no === identifier));
    if (!car) return;
    currentEditingCar = car;

    document.getElementById('modal-stock-no').innerText = `STOCK: ${car.stock_no} • ${car.chassis || 'No Chassis'}`;
    document.getElementById('modal-car-title').innerText = `${car.brand} ${car.model} (${car.year})`;
    document.getElementById('modal-body-price-text').innerText = `Body Price (Dealer): RM ${(car.body_price || 0).toLocaleString()}`;

    const isOverride = (car.is_manual_override === true || car.is_manual_override === 'true');
    document.getElementById('modal-override-checkbox').checked = isOverride;
    toggleModalOverride(isOverride);

    document.getElementById('modal-market-low').value = car.market_low || '';
    document.getElementById('modal-market-median').value = car.market_median || '';
    document.getElementById('modal-market-high').value = car.market_high || '';
    document.getElementById('modal-market-date').value = (car.market_checked_at || '').split('T')[0] || new Date().toISOString().split('T')[0];
    document.getElementById('modal-market-sources').value = car.market_sources || '';
    document.getElementById('modal-comm-input').value = car.suggested_commission || 5000;
    document.getElementById('modal-buffer-input').value = car.negotiation_buffer || 1800;
    document.getElementById('modal-adv-ncd55-input').value = car.advertised_price_ncd55 || '';
    document.getElementById('modal-min-sell-input').value = car.minimum_sell_price || '';
    document.getElementById('modal-notes').value = car.market_notes || '';

    recalcModalLive();
    document.getElementById('edit-modal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
    currentEditingCar = null;
}

function toggleModalOverride(checked) {
    const label = document.getElementById('modal-override-label');
    if (label) {
        label.innerText = checked ? 'MANUAL OVERRIDE AKTIF (Nilai Dikunci)' : 'Auto Compute (Formula Automatik)';
        label.className = checked ? 'text-[11px] text-amber-400 font-bold' : 'text-[11px] text-emerald-400 font-medium';
    }
}

function recalcModalLive() {
    if (!currentEditingCar) return;
    const body = currentEditingCar.body_price || 0;
    const otr55 = currentEditingCar.otr_addition_ncd55 || 7000;
    const estBase = body + otr55;
    
    const median = parseFloat(document.getElementById('modal-market-median').value || 0);
    const spread = median > 0 ? (median - estBase) : 0;
    document.getElementById('modal-spread-val').innerText = spread > 0 ? `+RM ${spread.toLocaleString()}` : 'RM 0';

    const isOverride = document.getElementById('modal-override-checkbox').checked;
    if (!isOverride) {
        let comm = 5000;
        if (body < 100000) comm = 3000;
        else if (body < 150000) comm = 4500;
        else if (body < 200000) comm = 5500;
        else if (body < 300000) comm = 7000;
        else comm = 10000;

        const buffer = 1800;
        document.getElementById('modal-comm-input').value = comm;
        document.getElementById('modal-buffer-input').value = buffer;
        document.getElementById('modal-adv-ncd55-input').value = estBase + comm + buffer;
        document.getElementById('modal-min-sell-input').value = estBase + Math.floor(comm / 2);
    }
}

function resetModalToAuto() {
    document.getElementById('modal-override-checkbox').checked = false;
    toggleModalOverride(false);
    recalcModalLive();
}

function saveModalChanges() {
    if (!currentEditingCar) return;
    const key = currentEditingCar.unique_key || currentEditingCar.stock_no;

    const isOverride = document.getElementById('modal-override-checkbox').checked;
    const mLow = parseFloat(document.getElementById('modal-market-low').value || 0);
    const mMedian = parseFloat(document.getElementById('modal-market-median').value || 0);
    const mHigh = parseFloat(document.getElementById('modal-market-high').value || 0);
    const mDate = document.getElementById('modal-market-date').value;
    const mSources = document.getElementById('modal-market-sources').value;
    const comm = parseFloat(document.getElementById('modal-comm-input').value || 5000);
    const buffer = parseFloat(document.getElementById('modal-buffer-input').value || 1800);
    const adv55 = parseFloat(document.getElementById('modal-adv-ncd55-input').value || 0);
    const minSell = parseFloat(document.getElementById('modal-min-sell-input').value || 0);
    const notes = document.getElementById('modal-notes').value;

    const estBase = (currentEditingCar.body_price || 0) + (currentEditingCar.otr_addition_ncd55 || 7000);
    const spread = mMedian > 0 ? (mMedian - estBase) : 0;
    const demand = currentEditingCar.demand_score || 8.5;
    const spreadRatio = mMedian > 0 ? (spread / mMedian) : 0;
    const marketScore = Math.min(10.0, 5.0 + (spreadRatio * 40));
    const saving = Math.max(0, mMedian - adv55);
    const savingRatio = mMedian > 0 ? (saving / mMedian) : 0;
    const adScore = parseFloat(Math.min(10.0, (demand * 0.45) + (marketScore * 0.40) + (savingRatio * 15)).toFixed(1));

    const updatedFields = {
        market_low: mLow,
        market_median: mMedian,
        market_high: mHigh,
        market_checked_at: mDate,
        market_freshness: 'FRESH',
        market_sources: mSources,
        suggested_commission: comm,
        negotiation_buffer: buffer,
        advertised_price_ncd55: adv55,
        advertised_price_ncd0: adv55 + 3000,
        minimum_sell_price: minSell,
        available_market_spread: spread,
        market_notes: notes,
        ad_score: adScore,
        pricing_status: adScore >= 9.0 ? 'HIGH_PRIORITY' : (spread >= 3000 ? 'GOOD_DEAL' : 'RESEARCHED'),
        is_manual_override: isOverride
    };

    const idx = currentCars.findIndex(c => (c.unique_key === key || c.stock_no === key));
    if (idx !== -1) {
        currentCars[idx] = { ...currentCars[idx], ...updatedFields };
    }

    let stored = {};
    try { stored = JSON.parse(localStorage.getItem('prestige_market_overrides') || '{}'); } catch(e){}
    stored[key] = updatedFields;
    localStorage.setItem('prestige_market_overrides', JSON.stringify(stored));

    alert('Risikan pasaran bagi kenderaan ini berjaya disimpan!');
    closeEditModal();
    updateStatCounters();
    renderTopAds();
    renderInventoryTable();
}

function populateSettingsUI() {
    document.getElementById('setting-otr-55').value = globalSettings.default_otr_addition_ncd55 || 7000;
    document.getElementById('setting-otr-0').value = globalSettings.default_otr_addition_ncd0 || 10000;
    document.getElementById('setting-buffer').value = globalSettings.default_negotiation_buffer || 1800;
    document.getElementById('setting-fresh-days').value = globalSettings.freshness_threshold_fresh_days || 7;
    document.getElementById('setting-mod-days').value = globalSettings.freshness_threshold_moderate_days || 14;
}

function saveGlobalSettings() {
    globalSettings.default_otr_addition_ncd55 = parseFloat(document.getElementById('setting-otr-55').value || 7000);
    globalSettings.default_otr_addition_ncd0 = parseFloat(document.getElementById('setting-otr-0').value || 10000);
    globalSettings.default_negotiation_buffer = parseFloat(document.getElementById('setting-buffer').value || 1800);
    globalSettings.freshness_threshold_fresh_days = parseInt(document.getElementById('setting-fresh-days').value || 7);
    globalSettings.freshness_threshold_moderate_days = parseInt(document.getElementById('setting-mod-days').value || 14);

    localStorage.setItem('prestige_pricing_settings', JSON.stringify(globalSettings));
    alert('Tetapan engine OTR berjaya disimpan!');
}

function resetDefaultSettings() {
    localStorage.removeItem('prestige_pricing_settings');
    populateSettingsUI();
    alert('Tetapan dikembalikan ke nilai default.');
}

function exportCSV() {
    const headers = ['stock_no', 'chassis', 'model', 'body_price', 'estimated_otr_55', 'market_low', 'market_median', 'market_high', 'available_market_spread', 'suggested_commission', 'advertised_price_ncd55', 'ad_score', 'market_checked_at', 'market_sources', 'market_notes'];
    let csvRows = [headers.join(',')];

    currentCars.forEach(car => {
        const row = [
            `"${car.stock_no || ''}"`,
            `"${car.chassis || ''}"`,
            `"${(car.model || '').replace(/"/g, '""')}"`,
            car.body_price || 0,
            car.estimated_otr_base_ncd55 || 0,
            car.market_low || 0,
            car.market_median || 0,
            car.market_high || 0,
            car.available_market_spread || 0,
            car.suggested_commission || 0,
            car.advertised_price_ncd55 || 0,
            car.ad_score || 0,
            `"${car.market_checked_at || ''}"`,
            `"${(car.market_sources || '').replace(/"/g, '""')}"`,
            `"${(car.market_notes || '').replace(/"/g, '""')}"`
        ];
        csvRows.push(row.join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `market_pricing_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

document.addEventListener('DOMContentLoaded', initAdminApp);
