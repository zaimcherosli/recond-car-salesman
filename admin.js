let currentCars = [];
let globalSettings = {};
let currentTab = 'top-ads';

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdmin);
} else {
    initAdmin();
}

async function initAdmin() {
    const candidateUrls = [
        'admin_inventory.json',
        './admin_inventory.json',
        '/admin_inventory.json',
        'cars_data.json',
        './cars_data.json',
        '/cars_data.json'
    ];

    for (const url of candidateUrls) {
        try {
            const res = await fetch(url);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    currentCars = data;
                    break;
                }
            }
        } catch (e) {}
    }

    if (currentCars.length === 0 && window.INVENTORY_DATA && Array.isArray(window.INVENTORY_DATA)) {
        currentCars = window.INVENTORY_DATA;
    }

    const settingUrls = ['pricing_settings.json', './pricing_settings.json', '/pricing_settings.json'];
    for (const sUrl of settingUrls) {
        try {
            const setRes = await fetch(sUrl);
            if (setRes.ok) {
                globalSettings = await setRes.json();
                break;
            }
        } catch(e){}
    }

    const savedSettings = localStorage.getItem('prestige_pricing_settings');
    if (savedSettings) {
        try { globalSettings = JSON.parse(savedSettings); } catch(e){}
    }

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

function switchTab(tabId) {
    currentTab = tabId;
    ['top-ads', 'inventory', 'settings', 'import-export'].forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        if (el) el.classList.toggle('hidden', t !== tabId);
    });
    document.querySelectorAll('.admin-tab-btn').forEach(b => {
        const onclickAttr = b.getAttribute('onclick') || '';
        if (onclickAttr.includes(`'${tabId}'`)) {
            b.className = "admin-tab-btn px-4 py-2 rounded-xl bg-slate-900 text-white font-extrabold shadow-sm transition-all whitespace-nowrap";
        } else {
            b.className = "admin-tab-btn px-4 py-2 rounded-xl text-slate-600 hover:text-slate-900 transition-all whitespace-nowrap";
        }
    });
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

    const unresearched = currentCars.filter(c => !c.market_median || c.market_freshness === 'UNRESEARCHED').length;
    const unresEl = document.getElementById('stat-unresearched');
    if (unresEl) unresEl.innerText = unresearched;

    const totalSpread = currentCars.reduce((acc, c) => acc + Math.max(0, c.available_market_spread || 0), 0);
    const spreadEl = document.getElementById('stat-total-spread');
    if (spreadEl) spreadEl.innerText = `RM ${(totalSpread/1000).toFixed(0)}k`;
}

function renderTopAds() {
    const grid = document.getElementById('top-ads-grid');
    if (!grid) return;

    const brand = document.getElementById('top-ads-brand-filter')?.value || 'all';
    let list = currentCars.filter(c => (c.ad_score || 0) >= 7.0 && (c.market_median || 0) > 0 && (c.image_count >= 2 || (c.images && c.images.length >= 2)));
    if (brand !== 'all') {
        list = list.filter(c => c.brand && c.brand.toLowerCase() === brand.toLowerCase());
    }

    list.sort((a, b) => (b.ad_score || 0) - (a.ad_score || 0));

    if (list.length === 0) {
        grid.innerHTML = '<div class="col-span-full py-16 text-center text-slate-500 bg-white rounded-3xl border border-slate-200 shadow-sm">Tiada cadangan iklan ditemui untuk penapis ini.</div>';
        return;
    }

    grid.innerHTML = list.map(car => {
        const cover = car.thumbnail || (car.images && car.images[0]) || 'public/cars/placeholder.jpg';
        const saving = Math.max(0, (car.market_median || 0) - (car.advertised_price_ncd55 || 0));
        
        return `
        <div class="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
            
            <!-- Media Container with Clean Non-Overlapping Header Overlays -->
            <div class="relative aspect-[16/10] bg-slate-900 overflow-hidden">
                <img src="${cover}" alt="${car.model}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" onerror="this.src='public/cars/placeholder.jpg'">
                
                <!-- Structured Top Bar -->
                <div class="absolute top-2.5 inset-x-2.5 flex items-center justify-between gap-2 z-10">
                    <span class="px-2.5 py-1 rounded-lg bg-slate-950/85 backdrop-blur-md text-amber-300 font-mono text-[10px] font-bold border border-slate-700/60 shadow-sm">
                        STOCK: ${car.stock_no}
                    </span>
                    <span class="px-2.5 py-1 rounded-lg bg-amber-400 text-slate-950 font-display font-extrabold text-[11px] shadow-md flex items-center gap-1">
                        <span>AD SCORE:</span>
                        <span class="text-xs">${car.ad_score || 8.5}</span>
                    </span>
                </div>

                <!-- Structured Bottom Bar -->
                <div class="absolute bottom-2.5 inset-x-2.5 flex items-center justify-between gap-2 z-10">
                    <span class="px-2.5 py-1 rounded-lg bg-slate-950/85 backdrop-blur-md text-slate-200 font-mono text-[10px]">
                        GRED ${car.grade || '4.5A'} • ${car.year}
                    </span>
                    <span class="px-2.5 py-1 rounded-lg bg-emerald-800/95 backdrop-blur-md text-white font-mono text-[10px] font-bold shadow-sm">
                        ${car.status || 'Ready Stock'}
                    </span>
                </div>
            </div>

            <!-- Content Details -->
            <div class="p-5 flex-1 flex flex-col justify-between space-y-4">
                <div>
                    <span class="text-[11px] font-bold text-amber-700 uppercase tracking-wider">${car.brand} • ${car.category}</span>
                    <h3 class="font-display text-base sm:text-lg font-bold text-slate-950 mt-0.5 leading-snug">${car.model}</h3>
                    <div class="text-xs text-slate-500 mt-1">${car.color} • ${car.mileage}</div>

                    <div class="mt-4 p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-2 text-xs font-mono">
                        <div class="flex justify-between text-slate-600"><span>Body Price (Dealer):</span><span class="text-slate-950 font-bold">RM ${(car.body_price || 0).toLocaleString()}</span></div>
                        <div class="flex justify-between text-slate-600"><span>Est. OTR (55% NCD):</span><span class="text-amber-700 font-bold">RM ${(car.advertised_price_ncd55 || 0).toLocaleString()}</span></div>
                        <div class="flex justify-between text-slate-600"><span>Median Pasaran:</span><span class="text-slate-800 font-semibold">RM ${(car.market_median || 0).toLocaleString()}</span></div>
                        <div class="pt-1.5 border-t border-slate-200 flex justify-between font-bold">
                            <span class="text-emerald-700">Potensi Kelebihan OTR:</span>
                            <span class="text-emerald-700">+RM ${saving.toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                <div class="space-y-2 pt-2 border-t border-slate-100">
                    <div class="flex justify-between items-center text-xs font-mono">
                        <span class="text-slate-500">Cadangan Komisen:</span>
                        <span class="text-slate-950 font-bold">RM ${(car.suggested_commission || 5000).toLocaleString()}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <button onclick="openEditCarModal('${car.unique_key || car.stock_no}')" class="py-2.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs border border-slate-300 transition-all text-center">
                            Edit Risikan
                        </button>
                        <a href="https://wa.me/60108118559?text=${encodeURIComponent(`Salam, saya nak semak unit ${car.model} (${car.stock_no}) harga OTR RM ${(car.advertised_price_ncd55||0).toLocaleString()}`)}" target="_blank" class="py-2.5 px-3 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white font-bold text-xs uppercase tracking-wider text-center transition-all shadow-sm">
                            Salin WhatsApp
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
        tbody.innerHTML = '<tr><td colspan="10" class="p-8 text-center text-slate-500 font-sans bg-white">Tiada padanan inventori ditemui.</td></tr>';
        renderTablePagination(0, 0, 0);
        return;
    }

    tbody.innerHTML = pageList.map(car => {
        let freshBadge = '<span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200 text-[10px]">Unresearched</span>';
        if (car.market_freshness === 'FRESH') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-semibold">Segar (&le;7h)</span>';
        } else if (car.market_freshness === 'MODERATE') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-[10px] font-semibold">8-14 Hari</span>';
        } else if (car.market_freshness === 'STALE') {
            freshBadge = '<span class="px-2 py-0.5 rounded-full bg-rose-50 text-rose-800 border border-rose-200 text-[10px] font-semibold">Lapuk (>14h)</span>';
        }

        const spread = car.available_market_spread || 0;
        const spreadClass = spread >= 5000 ? 'text-emerald-700 font-bold' : (spread > 0 ? 'text-amber-700 font-semibold' : 'text-slate-400');

        return `
        <tr class="hover:bg-slate-50 transition-colors">
            <td class="p-3.5">
                <div class="font-bold text-slate-900 text-xs">${car.model}</div>
                <div class="text-[10px] text-slate-500 font-mono">STOCK: ${car.stock_no} • ${car.year}</div>
            </td>
            <td class="p-3.5 text-slate-700 font-semibold">RM ${(car.body_price || 0).toLocaleString()}</td>
            <td class="p-3.5 text-slate-900 font-medium">RM ${(car.estimated_otr_base_ncd55 || 0).toLocaleString()}</td>
            <td class="p-3.5 text-slate-800 font-semibold">${car.market_median ? 'RM ' + car.market_median.toLocaleString() : '<span class="text-slate-400">-</span>'}</td>
            <td class="p-3.5 ${spreadClass}">${spread > 0 ? '+RM ' + spread.toLocaleString() : '<span class="text-slate-400">-</span>'}</td>
            <td class="p-3.5 text-slate-950 font-bold">RM ${(car.suggested_commission || 0).toLocaleString()}</td>
            <td class="p-3.5 text-amber-700 font-bold font-sans">${car.advertised_price_ncd55 ? 'RM ' + car.advertised_price_ncd55.toLocaleString() : 'Bincang'}</td>
            <td class="p-3.5"><span class="px-2 py-0.5 rounded-md bg-slate-100 font-bold text-slate-800 border border-slate-200">${car.ad_score || '-'}</span></td>
            <td class="p-3.5">${freshBadge}</td>
            <td class="p-3.5 text-right">
                <button onclick="openEditCarModal('${car.unique_key || car.stock_no}')" class="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-bold text-[11px] uppercase transition-all shadow-sm">
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

    if (totalPages > 1) {
        html += `<button onclick="goToInvPage(${invPage - 1})" ${invPage === 1 ? 'disabled' : ''} class="px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 disabled:opacity-30 text-xs font-bold">Prev</button>`;
        
        for (let i = 1; i <= Math.min(5, totalPages); i++) {
            const active = i === invPage;
            html += `<button onclick="goToInvPage(${i})" class="px-3 py-1.5 rounded-lg text-xs font-bold ${active ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50'}">${i}</button>`;
        }

        if (totalPages > 5) {
            html += `<span class="px-1 text-slate-400">...</span>`;
            html += `<button onclick="goToInvPage(${totalPages})" class="px-3 py-1.5 rounded-lg text-xs font-bold ${totalPages === invPage ? 'bg-slate-900 text-white' : 'bg-white border border-slate-200 text-slate-700'}">${totalPages}</button>`;
        }

        html += `<button onclick="goToInvPage(${invPage + 1})" ${invPage === totalPages ? 'disabled' : ''} class="px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 disabled:opacity-30 text-xs font-bold">Next</button>`;
    }

    if (btns) btns.innerHTML = html;
}

function goToInvPage(p) {
    const totalPages = Math.ceil(filteredInvList.length / INV_PER_PAGE) || 1;
    if (p < 1 || p > totalPages) return;
    invPage = p;
    renderInventoryTable();
}

let activeEditCar = null;

function openEditCarModal(uniqueKey) {
    const car = currentCars.find(c => (c.unique_key === uniqueKey || c.stock_no === uniqueKey));
    if (!car) return;
    activeEditCar = car;

    document.getElementById('modal-stock-no').innerText = `STOCK: ${car.stock_no}`;
    document.getElementById('modal-car-title').innerText = `${car.brand} ${car.model} (${car.year})`;
    document.getElementById('modal-body-price-text').innerText = `Dealer Body Price: RM ${(car.body_price || 0).toLocaleString()}`;

    document.getElementById('modal-market-low').value = car.market_low || '';
    document.getElementById('modal-market-median').value = car.market_median || '';
    document.getElementById('modal-market-high').value = car.market_high || '';
    document.getElementById('modal-market-date').value = car.market_checked_at || new Date().toISOString().split('T')[0];
    document.getElementById('modal-market-sources').value = car.market_sources || 'Mudah.my, Carlist';
    document.getElementById('modal-notes').value = car.market_notes || '';

    const isOverride = !!car.is_manual_override;
    document.getElementById('modal-override-checkbox').checked = isOverride;
    toggleModalOverride(isOverride);

    document.getElementById('modal-comm-input').value = car.suggested_commission || 5000;
    document.getElementById('modal-buffer-input').value = car.negotiation_buffer || 1800;
    document.getElementById('modal-adv-ncd55-input').value = car.advertised_price_ncd55 || '';
    document.getElementById('modal-min-sell-input').value = car.minimum_sell_price || '';

    recalcModalLive();

    const modal = document.getElementById('edit-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeEditModal() {
    const modal = document.getElementById('edit-modal');
    if (modal) modal.classList.add('hidden');
    activeEditCar = null;
}

function toggleModalOverride(isOverride) {
    const label = document.getElementById('modal-override-label');
    if (label) {
        label.innerText = isOverride ? 'Manual Override (Nilai Dikunci)' : 'Auto Compute (Formula Automatik)';
        label.className = isOverride ? 'text-[11px] text-amber-700 font-bold' : 'text-[11px] text-emerald-700 font-medium';
    }
}

function recalcModalLive() {
    if (!activeEditCar) return;
    const isOverride = document.getElementById('modal-override-checkbox')?.checked || false;
    const bodyPrice = activeEditCar.body_price || 0;
    const otrAddition55 = (globalSettings.default_otr_additions && globalSettings.default_otr_additions.ncd_55) || 7000;
    const baseOtr55 = bodyPrice + otrAddition55;

    const median = parseFloat(document.getElementById('modal-market-median')?.value || 0);
    const spread = median > 0 ? median - baseOtr55 : 0;
    const spreadEl = document.getElementById('modal-spread-val');
    if (spreadEl) {
        spreadEl.innerText = spread > 0 ? `+RM ${spread.toLocaleString()}` : `RM ${spread.toLocaleString()}`;
        spreadEl.className = spread >= 5000 ? 'text-emerald-700 font-bold' : (spread > 0 ? 'text-amber-700 font-semibold' : 'text-slate-400');
    }

    if (!isOverride) {
        const defaultBuffer = globalSettings.default_negotiation_buffer || 1800;
        let targetComm = 5000;
        if (bodyPrice < 100000) targetComm = 3000;
        else if (bodyPrice < 150000) targetComm = 4500;
        else if (bodyPrice < 200000) targetComm = 5500;
        else if (bodyPrice < 300000) targetComm = 7000;
        else targetComm = 10000;

        let comm = targetComm;
        if (median > 0) {
            const headroom = spread - defaultBuffer;
            if (headroom >= targetComm) comm = targetComm;
            else if (headroom >= 2000) comm = headroom;
            else comm = Math.max(1000, headroom);
        }

        const advOtr = baseOtr55 + comm + defaultBuffer;
        const minSell = baseOtr55 + Math.round(targetComm * 0.5);

        document.getElementById('modal-comm-input').value = comm;
        document.getElementById('modal-buffer-input').value = defaultBuffer;
        document.getElementById('modal-adv-ncd55-input').value = advOtr;
        document.getElementById('modal-min-sell-input').value = minSell;
    }
}

function resetModalToAuto() {
    document.getElementById('modal-override-checkbox').checked = false;
    toggleModalOverride(false);
    recalcModalLive();
}

function saveModalChanges() {
    if (!activeEditCar) return;

    const key = activeEditCar.unique_key || (activeEditCar.stock_no + '_' + (activeEditCar.chassis || ''));
    const isOverride = document.getElementById('modal-override-checkbox').checked;
    const low = parseFloat(document.getElementById('modal-market-low').value) || null;
    const median = parseFloat(document.getElementById('modal-market-median').value) || null;
    const high = parseFloat(document.getElementById('modal-market-high').value) || null;
    const checkedAt = document.getElementById('modal-market-date').value || new Date().toISOString().split('T')[0];
    const sources = document.getElementById('modal-market-sources').value;
    const notes = document.getElementById('modal-notes').value;

    const comm = parseFloat(document.getElementById('modal-comm-input').value) || 0;
    const buffer = parseFloat(document.getElementById('modal-buffer-input').value) || 1800;
    const advNcd55 = parseFloat(document.getElementById('modal-adv-ncd55-input').value) || 0;
    const minSell = parseFloat(document.getElementById('modal-min-sell-input').value) || 0;

    const updatedData = {
        market_low: low,
        market_median: median,
        market_high: high,
        market_checked_at: checkedAt,
        market_sources: sources,
        market_notes: notes,
        is_manual_override: isOverride,
        suggested_commission: comm,
        negotiation_buffer: buffer,
        advertised_price_ncd55: advNcd55,
        minimum_sell_price: minSell,
        market_freshness: 'FRESH'
    };

    activeEditCar = { ...activeEditCar, ...updatedData };
    const idx = currentCars.findIndex(c => (c.unique_key === key || c.stock_no === key));
    if (idx !== -1) currentCars[idx] = activeEditCar;

    let overrides = {};
    try {
        overrides = JSON.parse(localStorage.getItem('prestige_market_overrides') || '{}');
    } catch(e){}
    overrides[key] = updatedData;
    localStorage.setItem('prestige_market_overrides', JSON.stringify(overrides));

    closeEditModal();
    updateStatCounters();
    renderTopAds();
    renderInventoryTable();
    alert('Risikan kenderaan berjaya disimpan!');
}

function populateSettingsUI() {
    if (!globalSettings) return;
    if (globalSettings.default_otr_additions) {
        document.getElementById('setting-otr-55').value = globalSettings.default_otr_additions.ncd_55 || 7000;
        document.getElementById('setting-otr-0').value = globalSettings.default_otr_additions.ncd_0 || 10000;
    }
    if (globalSettings.default_negotiation_buffer) {
        document.getElementById('setting-buffer').value = globalSettings.default_negotiation_buffer || 1800;
    }
    if (globalSettings.freshness_threshold_days) {
        document.getElementById('setting-fresh-days').value = globalSettings.freshness_threshold_days.fresh || 7;
        document.getElementById('setting-mod-days').value = globalSettings.freshness_threshold_days.moderate || 14;
    }
}

function saveGlobalSettings() {
    const otr55 = parseInt(document.getElementById('setting-otr-55').value) || 7000;
    const otr0 = parseInt(document.getElementById('setting-otr-0').value) || 10000;
    const buffer = parseInt(document.getElementById('setting-buffer').value) || 1800;
    const freshDays = parseInt(document.getElementById('setting-fresh-days').value) || 7;
    const modDays = parseInt(document.getElementById('setting-mod-days').value) || 14;

    globalSettings = {
        ...globalSettings,
        default_otr_additions: { ncd_55: otr55, ncd_0: otr0 },
        default_negotiation_buffer: buffer,
        freshness_threshold_days: { fresh: freshDays, moderate: modDays }
    };

    localStorage.setItem('prestige_pricing_settings', JSON.stringify(globalSettings));
    alert('Tetapan Global berjaya disimpan ke LocalStorage!');
}

function resetDefaultSettings() {
    localStorage.removeItem('prestige_pricing_settings');
    location.reload();
}

function exportCSV() {
    const headers = [
        "UniqueKey", "StockNo", "Model", "Brand", "Year", "Chassis", "BodyPrice", 
        "EstOTR_Base_NCD55", "MarketLow", "MarketMedian", "MarketHigh", 
        "AvailableMarketSpread", "SuggestedCommission", "AdvertisedPrice_NCD55", 
        "MinTargetClosing", "MarketCheckedAt", "MarketFreshness", "IsManualOverride", "Notes"
    ];

    let csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n";

    currentCars.forEach(car => {
        const row = [
            `"${car.unique_key || car.stock_no}"`,
            `"${car.stock_no}"`,
            `"${(car.model || '').replace(/"/g, '""')}"`,
            `"${car.brand || ''}"`,
            `"${car.year || ''}"`,
            `"${car.chassis || ''}"`,
            car.body_price || 0,
            car.estimated_otr_base_ncd55 || 0,
            car.market_low || '',
            car.market_median || '',
            car.market_high || '',
            car.available_market_spread || 0,
            car.suggested_commission || 0,
            car.advertised_price_ncd55 || 0,
            car.minimum_sell_price || 0,
            `"${car.market_checked_at || ''}"`,
            `"${car.market_freshness || 'UNRESEARCHED'}"`,
            car.is_manual_override ? 'TRUE' : 'FALSE',
            `"${(car.market_notes || '').replace(/"/g, '""')}"`
        ];
        csvContent += row.join(",") + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `prestige_auto_market_pricing_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
