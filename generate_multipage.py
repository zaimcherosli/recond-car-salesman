import os, sys, json, re, urllib.parse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "https://recond-car-salesman.pages.dev"
STOK_DIR = "stok"
os.makedirs(STOK_DIR, exist_ok=True)

with open("cars_data.json", "r", encoding="utf-8") as f:
    cars = json.load(f)

cars_json_str = json.dumps(cars, indent=2, ensure_ascii=False)

def get_header(active="home", depth=0):
    p = "../" if depth == 1 else ""
    h = "text-amber-700 font-extrabold" if active == "home" else "hover:text-amber-700"
    s = "text-amber-700 font-extrabold" if active == "stok" else "hover:text-amber-700"
    c = "text-amber-700 font-extrabold" if active == "kalkulator" else "hover:text-amber-700"
    pr = "text-amber-700 font-extrabold" if active == "proses" else "hover:text-amber-700"
    d = "text-amber-700 font-extrabold" if active == "dokumen" else "hover:text-amber-700"
    fq = "text-amber-700 font-extrabold" if active == "faq" else "hover:text-amber-700"

    html = """
    <!-- Top Running Marquee Bar -->
    <div class="bg-slate-950 text-slate-100 text-xs py-2.5 overflow-hidden border-b border-slate-800 w-full max-w-full">
        <div class="marquee-wrapper">
            <div class="marquee-content gap-8 font-medium tracking-wide">
                <span class="whitespace-nowrap font-bold text-amber-300">CLEARANCE STOK: Bermula 31 Ogos 2026 Sehingga Stok Habis!</span>
                <span class="text-amber-400 font-bold">•</span>
                <span class="whitespace-nowrap">Stok Recond Jepun & UK Unregistered Terkini 2026</span>
                <span class="text-amber-400 font-bold">•</span>
                <span class="whitespace-nowrap">Laporan Lelongan Tulen Disediakan (Gred 4.5 & 5A)</span>
                <span class="text-amber-400 font-bold">•</span>
                <span class="whitespace-nowrap">Talian Terus Sales Advisor: 010-8118 559</span>
                <span class="text-amber-400 font-bold">•</span>
                <span class="whitespace-nowrap">Kelulusan Pinjaman Bank Pantas 24 - 48 Jam</span>
                <span class="text-amber-400 font-bold">•</span>
                <span class="whitespace-nowrap">Pakej Waranti Komprehensif Sehingga 7 Tahun</span>
            </div>
        </div>
    </div>

    <!-- Navigation Header -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm w-full">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between gap-3">
            
            <a href="__PREFIX__index.html" class="flex flex-col min-w-0">
                <span class="font-display text-sm sm:text-lg lg:text-xl font-bold tracking-wider text-slate-900 uppercase leading-none truncate">PRESTIGE AUTO RECOND</span>
                <span class="text-[9px] sm:text-[10px] tracking-widest text-slate-500 uppercase font-semibold mt-1 truncate">Penasihat Jualan Sah & Dipercayai</span>
            </a>

            <nav class="hidden lg:flex items-center gap-6 xl:gap-8 text-xs font-bold uppercase tracking-wider text-slate-600">
                <a href="__PREFIX__index.html" class="__H_CLS__ transition-colors whitespace-nowrap">Laman Utama</a>
                
                <div class="relative group py-2">
                    <a href="__PREFIX__katalog.html" class="__S_CLS__ flex items-center gap-1 transition-colors whitespace-nowrap">
                        <span>Stok</span>
                        <svg class="w-3.5 h-3.5 transition-transform group-hover:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                    </a>

                    <div class="absolute left-0 top-full hidden group-hover:block w-72 bg-white rounded-2xl border border-slate-200 shadow-xl p-3 z-50">
                        <div class="text-[10px] font-bold text-amber-700 uppercase tracking-widest px-3 py-1.5 border-b border-slate-100">Kategori & Model Pilihan</div>
                        <div class="py-1 space-y-1 text-xs">
                            <a href="__PREFIX__katalog.html?brand=Honda" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">Honda (Civic Type R, N-Box, Stepwagon)</a>
                            <a href="__PREFIX__katalog.html?brand=Bmw" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">BMW (M135i, M4 Competition, 118i)</a>
                            <a href="__PREFIX__katalog.html?brand=Ferrari" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">Ferrari (812 GTS)</a>
                            <a href="__PREFIX__katalog.html?brand=Daihatsu" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">Daihatsu (Tanto Turbo)</a>
                            <a href="__PREFIX__katalog.html?cat=mpv" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">Kategori MPV Keluarga</a>
                            <a href="__PREFIX__katalog.html?cat=performance" class="block px-3 py-2 rounded-xl text-slate-700 hover:bg-slate-50 hover:text-amber-700 font-semibold transition-colors">Kategori Prestasi & Sukan</a>
                        </div>
                        <div class="pt-2 border-t border-slate-100 mt-1">
                            <a href="__PREFIX__katalog.html" class="block px-3 py-2 rounded-xl bg-slate-900 text-white text-center font-bold text-[11px] hover:bg-amber-600 transition-colors">Lihat Semua 20 Stok Kenderaan</a>
                        </div>
                    </div>
                </div>

                <a href="__PREFIX__kalkulator.html" class="__C_CLS__ transition-colors whitespace-nowrap">Kalkulator</a>
                <a href="__PREFIX__proses.html" class="__PR_CLS__ transition-colors whitespace-nowrap">Proses</a>
                <a href="__PREFIX__dokumen.html" class="__D_CLS__ transition-colors whitespace-nowrap">Dokumen</a>
                <a href="__PREFIX__faq.html" class="__FQ_CLS__ transition-colors whitespace-nowrap">Soalan Lazim</a>
            </nav>

            <div class="flex items-center gap-2">
                <a href="__PREFIX__katalog.html" class="hidden sm:inline-flex lg:hidden px-3 py-2 rounded-xl bg-slate-100 text-slate-800 text-xs font-bold uppercase tracking-wider">
                    Stok
                </a>
                <a href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20berminat%20nak%20tanya%20tentang%20stok%20kereta%20recond." target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-center px-4 py-2.5 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white text-xs font-bold uppercase tracking-wider transition-all shadow-sm whitespace-nowrap">
                    WhatsApp: 010-8118 559
                </a>
            </div>

        </div>
    </header>
    """
    return html.replace("__PREFIX__", p).replace("__H_CLS__", h).replace("__S_CLS__", s).replace("__C_CLS__", c).replace("__PR_CLS__", pr).replace("__D_CLS__", d).replace("__FQ_CLS__", fq)

def get_footer(depth=0):
    p = "../" if depth == 1 else ""
    html = """
    <footer class="bg-slate-950 text-slate-400 text-xs py-14 border-t border-slate-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
                <div class="space-y-3 md:col-span-1">
                    <div class="font-display text-base font-bold text-white uppercase tracking-wider">PRESTIGE AUTO RECOND</div>
                    <p class="text-slate-400 text-xs leading-relaxed">
                        Penasihat jualan kereta recond tulen import Jepun & UK Unregistered gred 4.0 hingga 5.0. Urusan telus bersama semakan auction sheet rasmi.
                    </p>
                    <div class="text-slate-300 font-semibold pt-1">Talian Terus: 010-8118 559</div>
                </div>

                <div class="space-y-2.5">
                    <div class="text-xs font-bold text-white uppercase tracking-wider">Pautan Utama</div>
                    <ul class="space-y-2 text-slate-400">
                        <li><a href="__PREFIX__index.html" class="hover:text-amber-400 transition-colors">Laman Utama</a></li>
                        <li><a href="__PREFIX__katalog.html" class="hover:text-amber-400 transition-colors">Katalog Stok Penuh (20 Unit)</a></li>
                        <li><a href="__PREFIX__kalkulator.html" class="hover:text-amber-400 transition-colors">Kalkulator Pinjaman Bank</a></li>
                        <li><a href="__PREFIX__proses.html" class="hover:text-amber-400 transition-colors">5 Langkah Proses Pembelian</a></li>
                        <li><a href="__PREFIX__dokumen.html" class="hover:text-amber-400 transition-colors">Senarai Semak Dokumen Loan</a></li>
                        <li><a href="__PREFIX__faq.html" class="hover:text-amber-400 transition-colors">Soalan Lazim (FAQ)</a></li>
                    </ul>
                </div>

                <div class="space-y-2.5">
                    <div class="text-xs font-bold text-white uppercase tracking-wider">Kategori Popular</div>
                    <ul class="space-y-2 text-slate-400">
                        <li><a href="__PREFIX__katalog.html?cat=mpv" class="hover:text-amber-400 transition-colors">MPV Keluarga (Stepwagon, Odyssey, Tanto)</a></li>
                        <li><a href="__PREFIX__katalog.html?cat=performance" class="hover:text-amber-400 transition-colors">Prestasi / Sukan (Type R FL5, M4, 812 GTS)</a></li>
                        <li><a href="__PREFIX__katalog.html?brand=Honda" class="hover:text-amber-400 transition-colors">Stok Honda Recond</a></li>
                        <li><a href="__PREFIX__katalog.html?brand=Bmw" class="hover:text-amber-400 transition-colors">Stok BMW Recond</a></li>
                        <li><a href="__PREFIX__katalog.html?brand=Ferrari" class="hover:text-amber-400 transition-colors">Supercar Koleksi (Ferrari)</a></li>
                    </ul>
                </div>

                <div class="space-y-3">
                    <div class="text-xs font-bold text-white uppercase tracking-wider">Jaminan Kualiti</div>
                    <div class="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 space-y-2 text-[11px] text-slate-300">
                        <div>✓ Laporan Lelongan Jepun Tulen</div>
                        <div>✓ Waranti Komprehensif Sehingga 7 Tahun</div>
                        <div>✓ Servis Lengkap PDI & Detailing Percuma</div>
                        <div>✓ Tiada Manipulasi Perbatuan (Original Mileage)</div>
                    </div>
                </div>
            </div>

            <div class="pt-8 border-t border-slate-900 text-center text-slate-600 text-[11px]">
                © 2026 Prestige Auto Recond Malaysia. Hak Cipta Terpelihara. Maklumat stok dan harga tertakluk kepada ketersediaan semasa.
            </div>
        </div>
    </footer>
    """
    return html.replace("__PREFIX__", p)

def get_head(title, desc, canonical, og_image="https://recond-car-salesman.pages.dev/public/cars/EW_517/Malay%207-7/WhatsApp%20Image%202026-07-07%20at%204.40.14%20PM.jpeg", schema_extra=""):
    return f"""<!DOCTYPE html>
<html lang="ms" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <link rel="canonical" href="{canonical}">

    <meta property="og:type" content="website">
    <meta property="og:url" content="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{og_image}">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{og_image}">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">

    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        display: ['Space Grotesk', 'sans-serif'],
                    }},
                    colors: {{
                        brand: {{
                            gold: '#D4AF37',
                            goldLight: '#F3E5AB',
                            emerald: '#0F5132',
                            emeraldHover: '#0b3d26',
                            charcoal: '#1A1A1A'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0%); }} 100% {{ transform: translateX(-50%); }} }}
        .marquee-wrapper {{ overflow: hidden; white-space: nowrap; display: flex; width: 100%; }}
        .marquee-content {{ display: inline-flex; white-space: nowrap; animation: marquee 28s linear infinite; }}
        .marquee-wrapper:hover .marquee-content {{ animation-play-state: paused; }}
        .gold-gradient-text {{ background: linear-gradient(135deg, #0f172a 0%, #b48c14 60%, #856404 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    </style>
    {schema_extra}
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased selection:bg-amber-500 selection:text-slate-950">
"""

print("Writing subpages now...")

# BUILD kalkulator.html
kalk_body = """
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div class="max-w-3xl mx-auto text-center space-y-3 mb-10">
            <span class="text-xs font-bold tracking-widest text-amber-700 uppercase">Alat Pengiraan Rasmi</span>
            <h1 class="font-display text-2xl sm:text-4xl font-bold text-slate-900">Kalkulator Pinjaman Bank Kereta Recond</h1>
            <p class="text-slate-600 text-xs sm:text-sm">Kira anggaran bayaran bulanan berdasarkan harga kenderaan, wang pendahuluan, tempoh pinjaman dan kadar faedah bank komersial semasa.</p>
        </div>

        <div class="max-w-4xl mx-auto bg-white rounded-3xl border border-slate-200 shadow-xl p-6 sm:p-10 space-y-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between items-center mb-2 font-bold text-sm text-slate-900">
                            <span>Harga Kereta (RM):</span>
                            <span id="calc-price-display" class="text-base text-amber-700 font-mono">RM 230,000</span>
                        </div>
                        <input type="range" id="car-price-slider" min="50000" max="600000" step="5000" value="230000" oninput="runCalculator()" class="w-full accent-amber-500">
                        <div class="flex justify-between text-[10px] text-slate-400 mt-1"><span>RM 50k</span><span>RM 300k</span><span>RM 600k</span></div>
                    </div>

                    <div>
                        <div class="flex justify-between items-center mb-2 font-bold text-sm text-slate-900">
                            <span>Bayaran Muka / Downpayment (RM):</span>
                            <span id="calc-dp-display" class="text-base text-amber-700 font-mono">RM 23,000 (10%)</span>
                        </div>
                        <input type="range" id="car-dp-slider" min="0" max="150000" step="5000" value="23000" oninput="runCalculator()" class="w-full accent-amber-500">
                        <div class="flex justify-between text-[10px] text-slate-400 mt-1"><span>RM 0 (Full Loan)</span><span>RM 50k</span><span>RM 150k</span></div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="block font-bold text-xs text-slate-700 mb-1.5">Tempoh Pinjaman:</label>
                            <select id="calc-period-select" onchange="runCalculator()" class="w-full p-3 rounded-xl bg-slate-50 border border-slate-300 font-bold text-xs text-slate-900 focus:outline-none focus:border-amber-500">
                                <option value="9" selected>9 Tahun (108 Bulan)</option>
                                <option value="7">7 Tahun (84 Bulan)</option>
                                <option value="5">5 Tahun (60 Bulan)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block font-bold text-xs text-slate-700 mb-1.5">Kadar Faedah Bank (%):</label>
                            <select id="calc-rate-select" onchange="runCalculator()" class="w-full p-3 rounded-xl bg-slate-50 border border-slate-300 font-bold text-xs text-slate-900 focus:outline-none focus:border-amber-500">
                                <option value="0.023">2.30% (Promo)</option>
                                <option value="0.025" selected>2.50% (Standard)</option>
                                <option value="0.028">2.80%</option>
                                <option value="0.032">3.20%</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="bg-slate-950 text-white rounded-3xl p-6 sm:p-8 space-y-6 flex flex-col justify-between">
                    <div>
                        <span class="text-[10px] font-bold tracking-widest text-amber-400 uppercase">Keputusan Anggaran Pinjaman</span>
                        <div class="mt-2">
                            <span class="text-xs text-slate-400 block font-medium">Anggaran Bayaran Bulanan:</span>
                            <div id="calc-monthly-big" class="font-display text-3xl sm:text-4xl font-bold text-amber-400 mt-1">RM 2,349 / bln</div>
                        </div>

                        <div class="mt-6 pt-6 border-t border-slate-800 space-y-2.5 text-xs">
                            <div class="flex justify-between text-slate-400"><span>Jumlah Pinjaman:</span><span id="calc-loan-amount" class="text-white font-semibold">RM 207,000</span></div>
                            <div class="flex justify-between text-slate-400"><span>Jumlah Faedah:</span><span id="calc-interest-amount" class="text-white font-semibold">RM 46,575</span></div>
                            <div class="flex justify-between text-slate-400"><span>Jumlah Bayaran Balik:</span><span id="calc-total-repay" class="text-white font-semibold">RM 253,575</span></div>
                        </div>
                    </div>

                    <a id="calc-whatsapp-btn" href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20nak%20semak%20kelayakan%20pinjaman%20untuk%20kereta%20anggaran%20RM230,000." target="_blank" rel="noopener noreferrer" class="w-full py-4 rounded-2xl bg-brand-emerald hover:bg-brand-emeraldHover text-white font-bold text-xs uppercase tracking-wider text-center transition-all shadow-md">
                        Semak Kelayakan Loan Saya via WhatsApp
                    </a>
                </div>
            </div>

            <div class="pt-6 border-t border-slate-100">
                <h3 class="font-display text-base font-bold text-slate-900 mb-3">Jadual Perbandingan Tempoh Pinjaman</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead>
                            <tr class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                                <th class="p-3">Tempoh Pinjaman</th>
                                <th class="p-3">Kadar Faedah</th>
                                <th class="p-3">Anggaran Bulanan</th>
                                <th class="p-3">Jumlah Faedah Bank</th>
                            </tr>
                        </thead>
                        <tbody id="comparison-tbody" class="divide-y divide-slate-100 text-slate-700"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        function runCalculator() {
            const price = parseFloat(document.getElementById('car-price-slider').value);
            const dp = parseFloat(document.getElementById('car-dp-slider').value);
            const period = parseFloat(document.getElementById('calc-period-select').value);
            const rate = parseFloat(document.getElementById('calc-rate-select').value);

            document.getElementById('calc-price-display').innerText = 'RM ' + price.toLocaleString();
            const dpPercent = Math.round((dp / price) * 100);
            document.getElementById('calc-dp-display').innerText = 'RM ' + dp.toLocaleString() + ' (' + dpPercent + '%)';

            const principal = Math.max(0, price - dp);
            const interest = principal * rate * period;
            const total = principal + interest;
            const monthly = period > 0 ? Math.round(total / (period * 12)) : 0;

            document.getElementById('calc-monthly-big').innerText = 'RM ' + monthly.toLocaleString() + ' / bln';
            document.getElementById('calc-loan-amount').innerText = 'RM ' + principal.toLocaleString();
            document.getElementById('calc-interest-amount').innerText = 'RM ' + Math.round(interest).toLocaleString();
            document.getElementById('calc-total-repay').innerText = 'RM ' + Math.round(total).toLocaleString();

            const waMsg = 'Salam Sales Advisor, saya berminat nak buat semakan loan kereta harga RM ' + price.toLocaleString() + ' dengan downpayment RM ' + dp.toLocaleString() + ' (' + period + ' tahun, anggaran RM ' + monthly.toLocaleString() + '/bulan).';
            document.getElementById('calc-whatsapp-btn').href = 'https://wa.me/60108118559?text=' + encodeURIComponent(waMsg);

            const tbody = document.getElementById('comparison-tbody');
            if (tbody) {
                let rowsHtml = '';
                [5, 7, 9].forEach(yrs => {
                    const i = principal * rate * yrs;
                    const tot = principal + i;
                    const m = Math.round(tot / (yrs * 12));
                    const isSelected = yrs === period ? 'bg-amber-50 font-bold text-amber-900' : '';
                    rowsHtml += '<tr class="' + isSelected + '">'
                        + '<td class="p-3">' + yrs + ' Tahun (' + (yrs * 12) + ' Bulan)</td>'
                        + '<td class="p-3">' + (rate * 100).toFixed(2) + '%</td>'
                        + '<td class="p-3 text-amber-700 font-bold">RM ' + m.toLocaleString() + ' / bln</td>'
                        + '<td class="p-3">RM ' + Math.round(i).toLocaleString() + '</td>'
                        + '</tr>';
                });
                tbody.innerHTML = rowsHtml;
            }
        }
        document.addEventListener('DOMContentLoaded', runCalculator);
    </script>
"""

with open("kalkulator.html", "w", encoding="utf-8") as out_f:
    out_f.write(get_head("Kalkulator Pinjaman Kereta Recond 2026 | Prestige Auto Recond", "Kira anggaran bayaran bulanan pinjaman kereta recond import Jepun & UK dengan kadar faedah bank terendah.", f"{BASE_URL}/kalkulator.html") + get_header("kalkulator") + kalk_body + get_footer() + "</body></html>")

print("kalkulator.html generated!")

# BUILD proses.html
proses_body = """
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div class="max-w-3xl mx-auto text-center space-y-3 mb-12">
            <span class="text-xs font-bold tracking-widest text-amber-700 uppercase">Panduan Pembeli Bijak</span>
            <h1 class="font-display text-2xl sm:text-4xl font-bold text-slate-900">5 Langkah Proses Pembelian Kereta Recond</h1>
            <p class="text-slate-600 text-xs sm:text-sm">Urusan telus dari semakan dokumen lelongan hingga penyerahan kunci di hadapan rumah anda.</p>
        </div>

        <div class="max-w-4xl mx-auto space-y-6">
            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row gap-6 items-start">
                <div class="w-12 h-12 rounded-2xl bg-slate-950 text-amber-400 flex items-center justify-center font-display font-bold text-xl flex-shrink-0">1</div>
                <div class="space-y-2 flex-1">
                    <h3 class="font-display text-lg font-bold text-slate-900">Pemilihan Model & Semakan Laporan Lelongan (Auction Sheet)</h3>
                    <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        Pilih kenderaan yang anda minati daripada katalog kami. Kami akan mendedahkan dokumen Auction Sheet rasmi Jepun (USS, TAA, CAA) untuk mengesahkan gred (4.0, 4.5, 5A) dan ketulenan perbatuan sebenar.
                    </p>
                </div>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row gap-6 items-start">
                <div class="w-12 h-12 rounded-2xl bg-slate-950 text-amber-400 flex items-center justify-center font-display font-bold text-xl flex-shrink-0">2</div>
                <div class="space-y-2 flex-1">
                    <h3 class="font-display text-lg font-bold text-slate-900">Penyerahan Dokumen & Permohonan Pinjaman Bank</h3>
                    <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        Hantarkan dokumen pendapatan secara selamat melalui WhatsApp atau emel. Kami akan menguruskan penghantaran ke bank-bank panel utama (Maybank, Public Bank, CIMB, Hong Leong, AmBank) untuk mendapatkan kadar faedah terendah.
                    </p>
                </div>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row gap-6 items-start">
                <div class="w-12 h-12 rounded-2xl bg-slate-950 text-amber-400 flex items-center justify-center font-display font-bold text-xl flex-shrink-0">3</div>
                <div class="space-y-2 flex-1">
                    <h3 class="font-display text-lg font-bold text-slate-900">Kelulusan Pinjaman & Menandatangani Perjanjian</h3>
                    <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        Selepas bank meluluskan pinjaman dalam masa 24 hingga 48 jam, anda akan menandatangani surat tawaran perjanjian sewa beli di cawangan bank berhampiran atau bersama pegawai bank kami.
                    </p>
                </div>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row gap-6 items-start">
                <div class="w-12 h-12 rounded-2xl bg-slate-950 text-amber-400 flex items-center justify-center font-display font-bold text-xl flex-shrink-0">4</div>
                <div class="space-y-2 flex-1">
                    <h3 class="font-display text-lg font-bold text-slate-900">Pemeriksaan PUSPAKOM, Servis PDI & Cucian Detailing</h3>
                    <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        Kereta akan menjalani pemeriksaan rasmi PUSPAKOM (B5 & B7), penukaran minyak servis baru, pemeriksaan 120-titik pra-penyerahan (PDI), serta cucian detailing penuh.
                    </p>
                </div>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col md:flex-row gap-6 items-start">
                <div class="w-12 h-12 rounded-2xl bg-amber-400 text-slate-950 flex items-center justify-center font-display font-bold text-xl flex-shrink-0">5</div>
                <div class="space-y-2 flex-1">
                    <h3 class="font-display text-lg font-bold text-slate-900">Pendaftaran Nombor Plat JPJ & Penyerahan Kunci (Delivery)</h3>
                    <p class="text-xs sm:text-sm text-slate-600 leading-relaxed">
                        Pendaftaran nombor plat baru dibuat di JPJ (anda boleh pilih nombor tender atau negeri pilihan). Kereta sedia diserahkan di bilik pameran kami atau dihantar terus dengan lori towing ke rumah anda!
                    </p>
                </div>
            </div>
        </div>

        <div class="max-w-xl mx-auto text-center mt-12">
            <a href="katalog.html" class="inline-flex items-center justify-center px-8 py-4 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs uppercase tracking-wider transition-all shadow-lg">
                Pilih Stok Kereta Anda Sekarang ➔
            </a>
        </div>
    </main>
"""

with open("proses.html", "w", encoding="utf-8") as out_f:
    out_f.write(get_head("5 Langkah Mudah Proses Pembelian Kereta Recond | Prestige Auto Recond", "Panduan lengkap langkah demi langkah membeli kereta recond import Jepun & UK tanpa risiko.", f"{BASE_URL}/proses.html") + get_header("proses") + proses_body + get_footer() + "</body></html>")

# BUILD dokumen.html
dokumen_body = """
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div class="max-w-3xl mx-auto text-center space-y-3 mb-12">
            <span class="text-xs font-bold tracking-widest text-amber-700 uppercase">Urusan Bank Pantas</span>
            <h1 class="font-display text-2xl sm:text-4xl font-bold text-slate-900">Senarai Semak Dokumen Permohonan Pinjaman</h1>
            <p class="text-slate-600 text-xs sm:text-sm">Sediakan dokumen berikut mengikut kategori pekerjaan anda untuk mempercepatkan proses kelulusan pinjaman bank dalam 24-48 jam.</p>
        </div>

        <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-6">
                <div class="space-y-4">
                    <div class="inline-block px-3 py-1 rounded-full bg-slate-100 text-slate-800 font-bold text-xs uppercase">Kategori 1</div>
                    <h3 class="font-display text-lg font-bold text-slate-900">Pekerja Swasta (Individual)</h3>
                    <ul class="space-y-2.5 text-xs text-slate-600">
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Salinan Kad Pengenalan (MyKad)</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Salinan Lesen Memandu Sah</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata Gaji 3 Bulan Terkini (6 Bulan jika komisen)</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata Bank Kemasukan Gaji 3 Bulan</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata KWSP / EPF Terkini</li>
                    </ul>
                </div>
                <a href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20pekerja%20swasta%20dan%20ingin%20hantar%20dokumen%20untuk%20semak%20kelayakan%20loan." target="_blank" rel="noopener noreferrer" class="w-full py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 font-bold text-xs text-center uppercase tracking-wider block transition-all">
                    Hantar Dokumen Swasta
                </a>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-6">
                <div class="space-y-4">
                    <div class="inline-block px-3 py-1 rounded-full bg-amber-100 text-amber-900 font-bold text-xs uppercase">Kategori 2</div>
                    <h3 class="font-display text-lg font-bold text-slate-900">Kakitangan Kerajaan</h3>
                    <ul class="space-y-2.5 text-xs text-slate-600">
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Salinan Kad Pengenalan (MyKad)</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Salinan Lesen Memandu Sah</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Slip Gaji 3 Bulan Terkini (e-Penyata Gaji)</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata Bank Kemasukan Gaji 3 Bulan</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Surat Pengesahan Jawatan Majikan</li>
                    </ul>
                </div>
                <a href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20kakitangan%20kerajaan%20dan%20ingin%20hantar%20dokumen%20untuk%20semak%20kelayakan%20loan." target="_blank" rel="noopener noreferrer" class="w-full py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 font-bold text-xs text-center uppercase tracking-wider block transition-all">
                    Hantar Dokumen Kerajaan
                </a>
            </div>

            <div class="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-6">
                <div class="space-y-4">
                    <div class="inline-block px-3 py-1 rounded-full bg-slate-900 text-white font-bold text-xs uppercase">Kategori 3</div>
                    <h3 class="font-display text-lg font-bold text-slate-900">Peniaga / Syarikat (Sdn Bhd)</h3>
                    <ul class="space-y-2.5 text-xs text-slate-600">
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Salinan MyKad Pengarah / Pemilik</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Pendaftaran Perniagaan SSM Lengkap</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata Bank Syarikat 6 Bulan Terkini</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Borang Nyata Cukai LHDN (Borang B / e-B)</li>
                        <li class="flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span> Penyata Audit Terkini (Sdn Bhd)</li>
                    </ul>
                </div>
                <a href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20pemilik%20syarikat%20dan%20ingin%20hantar%20dokumen%20untuk%20semak%20kelayakan%20loan%20syarikat." target="_blank" rel="noopener noreferrer" class="w-full py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs text-center uppercase tracking-wider block transition-all">
                    Hantar Dokumen Syarikat
                </a>
            </div>
        </div>
    </main>
"""

with open("dokumen.html", "w", encoding="utf-8") as out_f:
    out_f.write(get_head("Senarai Semak Dokumen Permohonan Pinjaman Kereta Recond | Prestige Auto Recond", "Senarai dokumen yang diperlukan untuk memohon pinjaman bank bagi pekerja swasta, kerajaan, dan peniaga.", f"{BASE_URL}/dokumen.html") + get_header("dokumen") + dokumen_body + get_footer() + "</body></html>")

# BUILD faq.html
faq_body = """
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-16">
        <div class="max-w-3xl mx-auto text-center space-y-3 mb-12">
            <span class="text-xs font-bold tracking-widest text-amber-700 uppercase">Pusat Informasi</span>
            <h1 class="font-display text-2xl sm:text-4xl font-bold text-slate-900">Soalan Lazim Pembelian Kereta Recond</h1>
            <p class="text-slate-600 text-xs sm:text-sm">Semua maklumat yang anda perlu tahu sebelum membuat keputusan membeli kereta recond idaman.</p>
        </div>

        <div class="max-w-3xl mx-auto space-y-4">
            <details class="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <summary class="flex justify-between items-center font-bold text-sm text-slate-900 cursor-pointer list-none">
                    <span>Apakah maksud kenderaan status "Unregistered"?</span>
                    <span class="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <p class="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed border-t border-slate-100 pt-3">
                    Unregistered bermaksud kenderaan tersebut belum pernah didaftarkan atas nama individu atau syarikat di Malaysia. Anda akan menjadi pemilik pertama di dalam geran pendaftaran JPJ dan berhak memilih nombor pendaftaran negeri baru pilihan anda.
                </p>
            </details>

            <details class="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <summary class="flex justify-between items-center font-bold text-sm text-slate-900 cursor-pointer list-none">
                    <span>Bagaimana cara membaca Gred Lelongan (Auction Grade)?</span>
                    <span class="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <p class="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed border-t border-slate-100 pt-3">
                    Rumah lelongan di Jepun (USS, TAA, CAA, JU) menilai keadaan fizikal dan mekanikal kenderaan:<br><br>
                    • <strong>Gred 5 & 6:</strong> Keadaan seperti baru (showroom condition), perbatuan sangat rendah, tiada kemalangan.<br>
                    • <strong>Gred 4.5:</strong> Keadaan sangat cemerlang, calar minima yang sukar dilihat mata kasar.<br>
                    • <strong>Gred 4.0:</strong> Keadaan baik dan terjaga rapi.<br>
                    • <strong>Gred R / RA:</strong> Kereta pernah mengalami pembaikan atau kemalangan (kami tidak menjual unit gred R).
                </p>
            </details>

            <details class="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <summary class="flex justify-between items-center font-bold text-sm text-slate-900 cursor-pointer list-none">
                    <span>Adakah perbatuan (mileage) kenderaan terjamin tulen?</span>
                    <span class="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <p class="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed border-t border-slate-100 pt-3">
                    Ya, 100%. Kami menyediakan salinan Auction Sheet rasmi yang merekodkan bacaan odometer semasa kereta dijual di Jepun. Kami mengamalkan dasar ketelusan mutlak tanpa manipulasi meter.
                </p>
            </details>

            <details class="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <summary class="flex justify-between items-center font-bold text-sm text-slate-900 cursor-pointer list-none">
                    <span>Berapa lamakah tempoh perlindungan waranti yang diberikan?</span>
                    <span class="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <p class="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed border-t border-slate-100 pt-3">
                    Setiap pembelian disertakan pakej waranti komprehensif sehingga 7 tahun daripada syarikat penyedia waranti berlesen utama. Perlindungan merangkumi Enjin, Transmisi Gearbox, Sistem ECU/ECM, Brek ABS, Stereng, dan Bateri Hybrid/EV.
                </p>
            </details>

            <details class="group bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
                <summary class="flex justify-between items-center font-bold text-sm text-slate-900 cursor-pointer list-none">
                    <span>Bolehkah memohon pinjaman penuh (Full Loan)?</span>
                    <span class="text-slate-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <p class="text-xs sm:text-sm text-slate-600 mt-3 leading-relaxed border-t border-slate-100 pt-3">
                    Kelayakan pinjaman penuh bergantung kepada profil kewangan pemohon. Kebanyakan pembeli mengambil 90% pinjaman dengan 10% bayaran pendahuluan untuk mendapatkan kadar faedah bank terendah.
                </p>
            </details>
        </div>
    </main>
"""

with open("faq.html", "w", encoding="utf-8") as out_f:
    out_f.write(get_head("Soalan Lazim (FAQ) Pembelian Kereta Recond | Prestige Auto Recond", "Jawapan lengkap kepada soalan popular mengenai status unregistered, waranti, auction sheet, dan pembiayaan bank.", f"{BASE_URL}/faq.html") + get_header("faq") + faq_body + get_footer() + "</body></html>")

print("proses.html, dokumen.html, faq.html generated!")

# BUILD katalog.html
katalog_body = """
    <section class="bg-slate-950 text-white py-10 sm:py-14 border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-3xl space-y-2">
                <span class="text-xs font-bold tracking-widest text-amber-400 uppercase">Bilik Pameran Digital</span>
                <h1 class="font-display text-2xl sm:text-4xl font-bold tracking-tight text-white">Katalog Stok Kereta Recond 2026</h1>
                <p class="text-slate-400 text-xs sm:text-sm">Semua unit lengkap dengan laporan lelongan Jepun tulen, nombor casis rasmi dan anggaran pinjaman bulanan.</p>
            </div>
        </div>
    </section>

    <section class="py-8 sm:py-12 w-full" id="katalog-section">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
            <div class="bg-white p-4 sm:p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div class="relative flex-1">
                        <input type="text" id="catalog-search" onkeyup="filterAndRenderCatalog()" placeholder="Cari Model, No. Stok (cth: EW 517, AM 495), No. Casis..." class="w-full pl-10 pr-4 py-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-900 focus:outline-none focus:border-amber-500 transition-all">
                        <span class="absolute left-3.5 top-3.5 text-slate-400 text-sm">🔍</span>
                    </div>

                    <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-500 font-semibold whitespace-nowrap">Susun:</span>
                        <select id="catalog-sort" onchange="filterAndRenderCatalog()" class="px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-bold text-slate-800 focus:outline-none focus:border-amber-500">
                            <option value="default">Susunan Asal</option>
                            <option value="price-low">Harga: Rendah ke Tinggi</option>
                            <option value="price-high">Harga: Tinggi ke Rendah</option>
                            <option value="year-new">Tahun: Terkini</option>
                        </select>
                    </div>
                </div>

                <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1 -mx-2 px-2 sm:mx-0 sm:px-0 sm:flex-wrap" id="catalog-filter-tabs">
                    <button onclick="filterCat('all', this)" class="cat-btn active px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-900 text-white shadow-sm flex-shrink-0">Semua Model (__TOTAL_CARS__)</button>
                    <button onclick="filterCat('Honda', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">Honda (14)</button>
                    <button onclick="filterCat('Bmw', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">BMW (4)</button>
                    <button onclick="filterCat('Ferrari', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">Ferrari (1)</button>
                    <button onclick="filterCat('Daihatsu', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">Daihatsu (1)</button>
                    <button onclick="filterCat('mpv', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">MPV (9)</button>
                    <button onclick="filterCat('performance', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-slate-100 text-slate-700 hover:bg-slate-200 flex-shrink-0">Prestasi / Sukan (6)</button>
                </div>
            </div>

            <div class="flex items-center justify-between text-xs font-semibold text-slate-600 px-1">
                <span id="catalog-count-text">Menunjukkan __TOTAL_CARS__ unit kenderaan</span>
                <span class="text-amber-700">6 unit per muka surat</span>
            </div>

            <div id="catalog-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"></div>

            <div id="catalog-pagination" class="pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="text-xs text-slate-500 font-medium" id="page-info-text">Muka surat 1</div>
                <div class="flex items-center gap-1.5" id="page-btns-container"></div>
            </div>
        </div>
    </section>

    <script>
        const allCars = __CARS_JSON__;
        const PER_PAGE = 6;
        let activePage = 1;
        let activeCat = 'all';
        let currentList = [...allCars];

        function onImgError(el) {
            el.src = 'public/cars/placeholder.jpg';
        }

        function checkUrlParams() {
            const urlParams = new URLSearchParams(window.location.search);
            const brand = urlParams.get('brand');
            const cat = urlParams.get('cat');
            if (brand) {
                activeCat = brand;
                updateTabUI(brand);
            } else if (cat) {
                activeCat = cat;
                updateTabUI(cat);
            } else {
                updateTabUI('all');
            }
        }

        function updateTabUI(category) {
            document.querySelectorAll('#catalog-filter-tabs .cat-btn').forEach(b => {
                b.classList.remove('bg-slate-900', 'text-white', 'shadow-sm', 'active');
                b.classList.add('bg-slate-100', 'text-slate-700');
                if (category === 'all' && b.innerText.toLowerCase().includes('semua')) {
                    b.classList.remove('bg-slate-100', 'text-slate-700');
                    b.classList.add('bg-slate-900', 'text-white', 'shadow-sm', 'active');
                } else if (category !== 'all' && b.innerText.toLowerCase().includes(category.toLowerCase())) {
                    b.classList.remove('bg-slate-100', 'text-slate-700');
                    b.classList.add('bg-slate-900', 'text-white', 'shadow-sm', 'active');
                }
            });
        }

        function renderCatalog() {
            const grid = document.getElementById('catalog-grid');
            if (!grid) return;

            const total = currentList.length;
            const totalPages = Math.ceil(total / PER_PAGE) || 1;

            if (activePage > totalPages) activePage = totalPages;
            if (activePage < 1) activePage = 1;

            const start = (activePage - 1) * PER_PAGE;
            const end = Math.min(start + PER_PAGE, total);
            const pageCars = currentList.slice(start, end);

            if (pageCars.length === 0) {
                grid.innerHTML = '<div class="col-span-full py-16 text-center text-slate-500 text-sm bg-white rounded-3xl border border-dashed border-slate-300">Tiada unit kenderaan ditemui untuk carian atau penapis ini.</div>';
                renderPaginationControls(0, 0, 0);
                return;
            }

            grid.innerHTML = pageCars.map(car => {
                const cover = car.thumbnail || (car.images && car.images[0]) || 'public/cars/placeholder.jpg';
                const imgCount = car.image_count || (car.images ? car.images.length : 0);
                const detailLink = car.detail_url || ('stok/' + car.slug + '.html');
                const waUrl = 'https://wa.me/60108118559?text=' + encodeURIComponent('Salam Sales Advisor, saya berminat dengan stok (' + car.stock_no + ') ' + car.model + ' tahun ' + car.year + ' harga ' + car.price_display + '. Boleh saya dapatkan maklumat lanjut?');

                return '<div class="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group">'
                    + '<div class="relative bg-slate-900 aspect-[16/10] overflow-hidden">'
                    + '<a href="' + detailLink + '"><img src="' + cover + '" alt="' + car.model + '" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" loading="lazy" onerror="onImgError(this)"></a>'
                    + '<div class="absolute top-3 left-3 flex gap-1.5 flex-wrap z-10">'
                    + '<span class="px-2.5 py-1 rounded-full bg-slate-950/85 backdrop-blur-md text-amber-300 font-mono text-[10px] font-bold tracking-wider border border-amber-500/30">STOCK: ' + car.stock_no + '</span>'
                    + '<span class="px-2.5 py-1 rounded-full bg-emerald-700/90 backdrop-blur-md text-white text-[10px] font-bold border border-emerald-500/30">' + car.status + '</span>'
                    + '</div>'
                    + '<div class="absolute top-3 right-3 z-10"><span class="px-2.5 py-1 rounded-full bg-amber-400 text-slate-950 font-mono text-[11px] font-extrabold shadow-md">GRED ' + car.grade + '</span></div>'
                    + '<div class="absolute bottom-3 right-3 z-10"><span class="px-2.5 py-1 rounded-lg bg-slate-950/85 backdrop-blur-md text-white text-[10px] font-semibold border border-slate-700 shadow-sm">' + imgCount + ' Foto</span></div>'
                    + '</div>'
                    + '<div class="p-5 flex-1 flex flex-col justify-between space-y-4">'
                    + '<div>'
                    + '<div><span class="text-[11px] font-bold text-amber-700 uppercase tracking-wider">' + car.brand + ' • ' + car.year + '</span>'
                    + '<h3 class="font-display text-base sm:text-lg font-bold text-slate-900 mt-0.5 leading-snug hover:text-amber-600 transition-colors"><a href="' + detailLink + '">' + car.model + '</a></h3></div>'
                    + '<div class="text-xs text-slate-500 mt-1.5 font-medium flex items-center gap-2"><span>Warna ' + (car.color || 'Solid') + '</span><span>•</span><span>' + (car.mileage || 'Perbatuan Rendah') + '</span></div>'
                    + '<div class="mt-3 p-3 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 line-clamp-2 leading-relaxed"><span class="font-bold text-slate-800">Spesifikasi:</span> ' + (car.specs || 'Spesifikasi import penuh tulen.') + '</div>'
                    + '<div class="mt-2 text-[11px] text-slate-400 font-mono">Casis: ' + (car.chassis || '-') + '</div>'
                    + '</div>'
                    + '<div class="pt-4 border-t border-slate-100 space-y-3">'
                    + '<div class="flex items-center justify-between">'
                    + '<div><span class="text-[10px] text-slate-500 block uppercase font-medium">Anggaran OTR (55% NCD):</span><span class="text-base sm:text-lg font-bold text-slate-950">' + car.price_display + '</span></div>'
                    + '<div class="text-right"><span class="text-[10px] text-slate-500 block uppercase font-medium">Anggaran Bulanan:</span><span class="text-xs font-bold text-amber-700">' + car.monthly_estimate + '</span></div>'
                    + '</div>'
                    + '<div class="grid grid-cols-2 gap-2">'
                    + '<a href="' + detailLink + '" class="py-2.5 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold uppercase tracking-wider transition-all text-center">Lihat Butiran ➔</a>'
                    + '<a href="' + waUrl + '" target="_blank" rel="noopener noreferrer" class="py-2.5 px-3 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white text-xs font-bold uppercase tracking-wider transition-all text-center truncate">WhatsApp</a>'
                    + '</div></div></div></div>';
            }).join('');

            renderPaginationControls(start + 1, end, total);
        }

        function renderPaginationControls(start, end, total) {
            const info = document.getElementById('page-info-text');
            const btns = document.getElementById('page-btns-container');
            const countText = document.getElementById('catalog-count-text');
            
            if (countText) countText.innerText = 'Menunjukkan ' + total + ' unit kenderaan ditemui';

            if (total === 0) {
                if (info) info.innerText = 'Tiada padanan';
                if (btns) btns.innerHTML = '';
                return;
            }

            const totalPages = Math.ceil(total / PER_PAGE);
            if (info) info.innerText = 'Menunjukkan ' + start + ' - ' + end + ' daripada ' + total + ' unit (Muka Surat ' + activePage + ' dari ' + totalPages + ')';

            let html = '';
            html += '<button type="button" onclick="setPage(' + (activePage - 1) + ')" ' + (activePage === 1 ? 'disabled class="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-300 bg-slate-100 cursor-not-allowed"' : 'class="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 shadow-sm transition-all"') + '>‹ Sebelumnya</button>';

            for (let p = 1; p <= totalPages; p++) {
                if (p === activePage) {
                    html += '<button type="button" class="w-9 h-9 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-sm">' + p + '</button>';
                } else {
                    html += '<button type="button" onclick="setPage(' + p + ')" class="w-9 h-9 rounded-xl text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 transition-all">' + p + '</button>';
                }
            }

            html += '<button type="button" onclick="setPage(' + (activePage + 1) + ')" ' + (activePage === totalPages ? 'disabled class="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-300 bg-slate-100 cursor-not-allowed"' : 'class="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-700 bg-white hover:bg-slate-100 border border-slate-300 shadow-sm transition-all"') + '>Seterusnya ›</button>';

            if (btns) btns.innerHTML = html;
        }

        function setPage(p) {
            const totalPages = Math.ceil(currentList.length / PER_PAGE);
            if (p < 1 || p > totalPages) return;
            activePage = p;
            renderCatalog();
            const sec = document.getElementById('katalog-section');
            if (sec) sec.scrollIntoView({ behavior: 'smooth' });
        }

        function filterCat(cat, btn) {
            activeCat = cat;
            activePage = 1;
            document.querySelectorAll('#catalog-filter-tabs .cat-btn').forEach(b => {
                b.classList.remove('bg-slate-900', 'text-white', 'shadow-sm', 'active');
                b.classList.add('bg-slate-100', 'text-slate-700');
            });
            if (btn) {
                btn.classList.remove('bg-slate-100', 'text-slate-700');
                btn.classList.add('bg-slate-900', 'text-white', 'shadow-sm', 'active');
            }
            filterAndRenderCatalog();
        }

        function filterAndRenderCatalog() {
            const query = (document.getElementById('catalog-search')?.value || '').toLowerCase().trim();
            const sortMode = document.getElementById('catalog-sort')?.value || 'default';
            activePage = 1;

            currentList = allCars.filter(car => {
                const matchCat = (activeCat === 'all')
                    || (car.category && car.category.toLowerCase() === activeCat.toLowerCase())
                    || (car.brand && car.brand.toLowerCase() === activeCat.toLowerCase());
                if (!matchCat) return false;

                if (!query) return true;
                const searchStr = (car.stock_no + ' ' + car.model + ' ' + car.brand + ' ' + car.color + ' ' + car.chassis + ' ' + car.specs).toLowerCase();
                return searchStr.includes(query);
            });

            if (sortMode === 'price-low') {
                currentList.sort((a, b) => (a.price_rm || 0) - (b.price_rm || 0));
            } else if (sortMode === 'price-high') {
                currentList.sort((a, b) => (b.price_rm || 0) - (a.price_rm || 0));
            } else if (sortMode === 'year-new') {
                currentList.sort((a, b) => (b.year || '').localeCompare(a.year || ''));
            }

            renderCatalog();
        }

        document.addEventListener('DOMContentLoaded', () => {
            checkUrlParams();
            filterAndRenderCatalog();
        });
    </script>
"""

katalog_final = katalog_body.replace("__TOTAL_CARS__", str(len(cars))).replace("__CARS_JSON__", cars_json_str)

with open("katalog.html", "w", encoding="utf-8") as out_f:
    out_f.write(get_head("Katalog Stok Kereta Recond Terkini 2026 | Prestige Auto Recond", "Semak inventori penuh 20 unit kereta recond import Jepun & UK Unregistered gred 4.0 hingga 5.0.", f"{BASE_URL}/katalog.html") + get_header("stok") + katalog_final + get_footer() + "</body></html>")

print("katalog.html generated!")

for idx, car in enumerate(cars):
    related = [c for c in cars if c['code'] != car['code'] and (c['brand'] == car['brand'] or c['category'] == car['category'])][:4]
    if len(related) < 4:
        related = [c for c in cars if c['code'] != car['code']][:4]

    imgs_list = car.get('images') or []
    cover_img = car.get('thumbnail') or (imgs_list[0] if len(imgs_list) > 0 else '') or 'public/cars/placeholder.jpg'
    images = imgs_list if len(imgs_list) > 0 else [cover_img]
    img_json = json.dumps(images)
    og_img_url = f"{BASE_URL}/{cover_img}" if not cover_img.startswith("http") else cover_img
    page_url = f"{BASE_URL}/stok/{car['slug']}.html"
    
    wa_msg = f"Salam Sales Advisor, saya berminat dengan stok ({car['stock_no']}) {car['model']} tahun {car['year']} (Casis: {car['chassis']}) harga {car['price_display']}. Boleh saya dapatkan maklumat lanjut dan semakan loan?"
    wa_link = f"https://wa.me/60108118559?text={urllib.parse.quote(wa_msg)}"
    
    p_55 = int(car.get('estimated_otr_ncd55') or car.get('price_rm') or 0)
    p_0 = int(car.get('estimated_otr_ncd0') or (p_55 + 3000 if p_55 > 0 else 0))
    
    schema_data = {
        "@context": "https://schema.org",
        "@type": "Car",
        "name": f"{car['brand']} {car['model']} ({car['year']})",
        "brand": { "@type": "Brand", "name": car['brand'] },
        "model": car['model'],
        "productionDate": car['year'],
        "color": car['color'],
        "vehicleIdentificationNumber": car['chassis'],
        "image": og_img_url,
        "offers": {
            "@type": "Offer",
            "price": str(car['price_rm']),
            "priceCurrency": "MYR",
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/UsedCondition",
            "url": page_url
        }
    }
    schema_json = '<script type="application/ld+json">\n' + json.dumps(schema_data, indent=2, ensure_ascii=False) + '\n</script>'
    
    related_html = ""
    for rel in related:
        rel_cover = rel.get('thumbnail') or ((rel.get('images') or [''])[0]) or '../public/cars/placeholder.jpg'
        if not rel_cover.startswith("../") and not rel_cover.startswith("http"):
            rel_cover = f"../{rel_cover}"
        related_html += f"""
        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
            <div class="relative aspect-[16/10] bg-slate-900 overflow-hidden">
                <img src="{rel_cover}" alt="{rel['model']}" class="w-full h-full object-cover hover:scale-105 transition-transform duration-300" loading="lazy">
                <div class="absolute top-2 left-2 flex gap-1">
                    <span class="px-2 py-0.5 rounded-full bg-slate-950/85 text-amber-300 font-mono text-[9px] font-bold">STOCK: {rel['stock_no']}</span>
                </div>
                <div class="absolute top-2 right-2">
                    <span class="px-2 py-0.5 rounded-full bg-amber-400 text-slate-950 font-mono text-[9px] font-extrabold">GRED {rel.get('grade','4.5A')}</span>
                </div>
            </div>
            <div class="p-3.5 flex-1 flex flex-col justify-between">
                <div>
                    <span class="text-[10px] font-bold text-amber-700 uppercase">{rel['brand']} • {rel['year']}</span>
                    <h4 class="text-xs font-bold text-slate-900 mt-0.5 leading-snug line-clamp-1">{rel['model']}</h4>
                    <div class="text-[11px] text-slate-500 mt-1">{rel['color']} • {rel['mileage']}</div>
                </div>
                <div class="pt-2.5 mt-2 border-t border-slate-100 flex items-center justify-between">
                    <div class="text-xs font-bold text-slate-900">{rel['price_display']}</div>
                    <a href="{rel['slug']}.html" class="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-amber-600 text-white text-[10px] font-bold uppercase transition-colors">
                        Lihat ➔
                    </a>
                </div>
            </div>
        </div>
        """

    thumbs_html = ""
    for tidx, img in enumerate(images):
        img_rel = f"../{img}" if not img.startswith("../") and not img.startswith("http") else img
        active_class = "border-amber-400 opacity-100 scale-105" if tidx == 0 else "border-transparent opacity-60 hover:opacity-100"
        thumbs_html += f"""
        <img src="{img_rel}" alt="Thumb {tidx+1}" onclick="switchDetailImage({tidx})" class="w-16 h-12 sm:w-20 sm:h-14 object-cover rounded-xl cursor-pointer border-2 transition-all flex-shrink-0 {active_class}" id="thumb-{tidx}" loading="lazy">
        """

    main_cover_rel = f"../{cover_img}" if not cover_img.startswith("../") and not cover_img.startswith("http") else cover_img

    detail_html = get_head(f"{car['model']} ({car['year']}) Recond Malaysia | Stok {car['stock_no']} | {car['price_display']}", f"{car['brand']} {car['model']} tahun {car['year']} Unregistered Gred {car['grade']}. Warna {car['color']}, mileage {car['mileage']}.", page_url, og_img_url, schema_json) + get_header("stok", depth=1) + f"""
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10">
        <nav class="flex items-center gap-2 text-xs text-slate-500 mb-6 flex-wrap font-medium">
            <a href="../index.html" class="hover:text-slate-900 transition-colors">Laman Utama</a>
            <span>/</span>
            <a href="../katalog.html" class="hover:text-slate-900 transition-colors">Katalog Stok</a>
            <span>/</span>
            <span class="text-slate-900 font-bold truncate max-w-xs">{car['model']}</span>
        </nav>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <div class="lg:col-span-7 space-y-4">
                <div class="relative bg-slate-950 rounded-3xl overflow-hidden shadow-lg aspect-[16/10] flex items-center justify-center group">
                    <img id="detail-main-img" src="{main_cover_rel}" alt="{car['model']}" class="w-full h-full object-contain select-none">
                    
                    <button type="button" onclick="stepDetailImage(-1)" class="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-950/70 hover:bg-amber-400 hover:text-slate-950 text-white flex items-center justify-center text-lg font-bold transition-all shadow-md">
                        ‹
                    </button>
                    <button type="button" onclick="stepDetailImage(1)" class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-slate-950/70 hover:bg-amber-400 hover:text-slate-950 text-white flex items-center justify-center text-lg font-bold transition-all shadow-md">
                        ›
                    </button>

                    <div class="absolute top-3.5 left-3.5 flex gap-2">
                        <span class="px-3 py-1 rounded-full bg-slate-950/85 backdrop-blur-md text-amber-300 font-mono text-xs font-bold tracking-wider border border-amber-500/30">STOCK: {car['stock_no']}</span>
                        <span class="px-3 py-1 rounded-full bg-emerald-700/90 backdrop-blur-md text-white text-xs font-bold border border-emerald-500/30">{car['status']}</span>
                    </div>
                    <div class="absolute top-3.5 right-3.5">
                        <span class="px-3 py-1 rounded-full bg-amber-400 text-slate-950 font-mono text-xs font-extrabold shadow-md">GRED {car['grade']}</span>
                    </div>
                    <div class="absolute bottom-3.5 left-3.5 bg-slate-950/85 backdrop-blur-md px-3 py-1 rounded-lg text-white text-xs font-mono border border-slate-800">
                        <span id="detail-counter">1 / {len(images)} Foto</span>
                    </div>
                </div>

                <div class="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm overflow-x-auto no-scrollbar flex items-center gap-2" id="detail-thumbs-container">
                    {thumbs_html}
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                    <div class="p-3 rounded-xl bg-white border border-slate-200 text-center">
                        <span class="text-[10px] text-slate-500 block uppercase font-medium">Tahun / Pendaftaran</span>
                        <span class="text-xs sm:text-sm font-bold text-slate-900 mt-0.5 block">{car['year']}</span>
                    </div>
                    <div class="p-3 rounded-xl bg-white border border-slate-200 text-center">
                        <span class="text-[10px] text-slate-500 block uppercase font-medium">Gred Lelongan</span>
                        <span class="text-xs sm:text-sm font-bold text-amber-700 mt-0.5 block">Gred {car['grade']} Asli</span>
                    </div>
                    <div class="p-3 rounded-xl bg-white border border-slate-200 text-center">
                        <span class="text-[10px] text-slate-500 block uppercase font-medium">Perbatuan / Mileage</span>
                        <span class="text-xs sm:text-sm font-bold text-slate-900 mt-0.5 block">{car['mileage']}</span>
                    </div>
                    <div class="p-3 rounded-xl bg-white border border-slate-200 text-center">
                        <span class="text-[10px] text-slate-500 block uppercase font-medium">Warna Asli</span>
                        <span class="text-xs sm:text-sm font-bold text-slate-900 mt-0.5 block">{car['color']}</span>
                    </div>
                </div>

                <div class="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                    <h3 class="font-display text-base font-bold text-slate-900">Spesifikasi Penuh Kenderaan</h3>
                    <p class="text-xs sm:text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-200/80 font-medium">
                        {car['specs']}
                    </p>
                    <div class="pt-2 text-xs text-slate-500 flex items-center gap-2">
                        <span class="font-bold text-slate-700">No. Casis / Chassis:</span>
                        <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-900 font-semibold">{car['chassis']}</span>
                    </div>
                </div>
            </div>

            <div class="lg:col-span-5 space-y-6">
                <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-5">
                    <div>
                        <span class="text-xs font-bold text-amber-700 uppercase tracking-wider">{car['brand']} • {car['year']}</span>
                        <h1 class="font-display text-xl sm:text-2xl font-bold text-slate-900 mt-1 leading-tight">{car['model']}</h1>
                    </div>

                    <!-- Customer NCD Selector -->
                    <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
                        <div class="flex items-center justify-between">
                            <span class="text-[11px] font-bold text-slate-700 uppercase tracking-wider">Pilihan Diskaun Insurans (NCD):</span>
                            <span class="text-[10px] text-amber-700 font-semibold">Tukar untuk semak OTR</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <button type="button" id="ncd-btn-55" onclick="setNcdMode(55)" class="py-2 px-3 rounded-xl bg-slate-900 text-white font-bold text-xs uppercase tracking-wider shadow-sm transition-all text-center">
                                55% NCD (Diskaun Penuh)
                            </button>
                            <button type="button" id="ncd-btn-0" onclick="setNcdMode(0)" class="py-2 px-3 rounded-xl bg-white text-slate-700 hover:bg-slate-100 font-bold text-xs uppercase tracking-wider border border-slate-300 transition-all text-center">
                                0% NCD (Kereta Pertama)
                            </button>
                        </div>
                    </div>

                    <div class="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-2">
                        <div class="flex items-center justify-between">
                            <div>
                                <span class="text-[11px] text-slate-600 block font-medium">Anggaran Harga Atas Jalan (OTR):</span>
                                <span id="car-price-display" class="text-xl sm:text-2xl font-bold text-slate-950">{car['price_display']}</span>
                            </div>
                            <div class="text-right">
                                <span class="text-[11px] text-slate-600 block font-medium">Anggaran Bulanan:</span>
                                <span id="car-monthly-display" class="text-sm sm:text-base font-bold text-amber-700">{car['monthly_estimate']}</span>
                            </div>
                        </div>
                        <p class="text-[10px] text-slate-500 italic leading-snug pt-1 border-t border-amber-500/20">
                            *Anggaran OTR berdasarkan NCD terpilih. Harga akhir tertakluk kepada sebut harga insurans rasmi & caj pendaftaran spesifik kenderaan.
                        </p>
                    </div>

                    <a href="{wa_link}" target="_blank" rel="noopener noreferrer" class="w-full py-4 px-6 rounded-2xl bg-brand-emerald hover:bg-brand-emeraldHover text-white font-bold text-xs sm:text-sm uppercase tracking-wider transition-all shadow-md flex items-center justify-center gap-2 text-center">
                        Tanya Stok & Tempah via WhatsApp
                    </a>

                    <div class="space-y-2 pt-2 border-t border-slate-100 text-xs text-slate-600">
                        <div class="flex items-center gap-2"><span class="text-emerald-600 font-bold">✓</span><span>Laporan Lelongan Jepun (Auction Sheet) Disediakan</span></div>
                        <div class="flex items-center gap-2"><span class="text-emerald-600 font-bold">✓</span><span>Waranti Terbuka Sehingga 7 Tahun</span></div>
                        <div class="flex items-center gap-2"><span class="text-emerald-600 font-bold">✓</span><span>Percuma Servis PDI, Penukaran Minyak & Cucian Detailing</span></div>
                        <div class="flex items-center gap-2"><span class="text-emerald-600 font-bold">✓</span><span>Urusan Pinjaman Bank Diuruskan Sepenuhnya</span></div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
                    <h3 class="font-display text-base font-bold text-slate-900">Kalkulator Loan Unit Ini</h3>
                    <div class="space-y-3 text-xs">
                        <div>
                            <div class="flex justify-between font-semibold text-slate-700 mb-1">
                                <span>Bayaran Muka (Downpayment 10%):</span>
                                <span id="calc-dp-text" class="text-amber-700 font-bold">RM {int((car.get('estimated_otr_ncd55') or car.get('price_rm', 0))*0.1):,}</span>
                            </div>
                            <input type="range" id="calc-dp-slider" min="0" max="{int((car.get('estimated_otr_ncd55') or car.get('price_rm', 0))*0.5)}" step="5000" value="{int((car.get('estimated_otr_ncd55') or car.get('price_rm', 0))*0.1)}" oninput="updateCarLoan()" class="w-full accent-amber-500">
                        </div>

                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block font-semibold text-slate-700 mb-1">Tempoh (Tahun):</label>
                                <select id="calc-period-select" onchange="updateCarLoan()" class="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900">
                                    <option value="9" selected>9 Tahun (108 bln)</option>
                                    <option value="7">7 Tahun (84 bln)</option>
                                    <option value="5">5 Tahun (60 bln)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block font-semibold text-slate-700 mb-1">Kadar Faedah (%):</label>
                                <select id="calc-rate-select" onchange="updateCarLoan()" class="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-200 font-bold text-slate-900">
                                    <option value="0.025" selected>2.50% (Bank Promo)</option>
                                    <option value="0.028">2.80% (Standard)</option>
                                    <option value="0.032">3.20%</option>
                                </select>
                            </div>
                        </div>

                        <div class="p-4 rounded-2xl bg-slate-950 text-white flex items-center justify-between mt-4">
                            <div>
                                <span class="text-[10px] text-slate-400 block uppercase font-medium">Anggaran Bulanan:</span>
                                <span id="calc-monthly-result" class="text-lg font-bold text-amber-400">{car['monthly_estimate']}</span>
                            </div>
                            <a href="{wa_link}" target="_blank" rel="noopener noreferrer" class="px-4 py-2 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white text-xs font-bold uppercase tracking-wider transition-all">
                                Semak Kelayakan
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-16 pt-10 border-t border-slate-200 space-y-6">
            <div>
                <span class="text-xs font-bold tracking-widest text-amber-700 uppercase">Pilihan Lain Berkaitan</span>
                <h3 class="font-display text-xl sm:text-2xl font-bold text-slate-900 mt-1">Model Yang Anda Mungkin Minat</h3>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-5">
                {related_html}
            </div>
        </div>
    </main>

    <script>
        const carImages = {img_json};
        const priceNcd55 = {p_55};
        const priceNcd0 = {p_0};
        let activeNcdMode = 55;
        let carPrice = priceNcd55;
        let currentImgIdx = 0;

        function setNcdMode(ncd) {{
            activeNcdMode = ncd;
            carPrice = (ncd === 55) ? priceNcd55 : priceNcd0;
            
            const btn55 = document.getElementById('ncd-btn-55');
            const btn0 = document.getElementById('ncd-btn-0');
            const priceDisp = document.getElementById('car-price-display');

            if (ncd === 55) {{
                btn55.className = "py-2 px-3 rounded-xl bg-slate-900 text-white font-bold text-xs uppercase tracking-wider shadow-sm transition-all text-center";
                btn0.className = "py-2 px-3 rounded-xl bg-white text-slate-700 hover:bg-slate-100 font-bold text-xs uppercase tracking-wider border border-slate-300 transition-all text-center";
                if (priceDisp) priceDisp.innerText = 'RM ' + priceNcd55.toLocaleString() + '*';
            }} else {{
                btn0.className = "py-2 px-3 rounded-xl bg-slate-900 text-white font-bold text-xs uppercase tracking-wider shadow-sm transition-all text-center";
                btn55.className = "py-2 px-3 rounded-xl bg-white text-slate-700 hover:bg-slate-100 font-bold text-xs uppercase tracking-wider border border-slate-300 transition-all text-center";
                if (priceDisp) priceDisp.innerText = 'RM ' + priceNcd0.toLocaleString() + '*';
            }}

            const slider = document.getElementById('calc-dp-slider');
            if (slider) {{
                slider.max = Math.round(carPrice * 0.5);
                slider.value = Math.round(carPrice * 0.1);
            }}
            updateCarLoan();
        }}

        function switchDetailImage(idx) {{
            if (idx < 0 || idx >= carImages.length) return;
            currentImgIdx = idx;
            const mainImg = document.getElementById('detail-main-img');
            const counter = document.getElementById('detail-counter');
            
            let targetSrc = carImages[idx];
            if (!targetSrc.startsWith('../') && !targetSrc.startsWith('http')) {{
                targetSrc = '../' + targetSrc;
            }}
            mainImg.src = targetSrc;
            counter.innerText = (idx + 1) + ' / ' + carImages.length + ' Foto';

            carImages.forEach((_, i) => {{
                const thumb = document.getElementById('thumb-' + i);
                if (thumb) {{
                    if (i === idx) {{
                        thumb.className = "w-16 h-12 sm:w-20 sm:h-14 object-cover rounded-xl cursor-pointer border-2 transition-all flex-shrink-0 border-amber-400 opacity-100 scale-105";
                        thumb.scrollIntoView({{ behavior: 'smooth', inline: 'center', block: 'nearest' }});
                    }} else {{
                        thumb.className = "w-16 h-12 sm:w-20 sm:h-14 object-cover rounded-xl cursor-pointer border-2 transition-all flex-shrink-0 border-transparent opacity-60 hover:opacity-100";
                    }}
                }}
            }});
        }}

        function stepDetailImage(step) {{
            let nextIdx = (currentImgIdx + step + carImages.length) % carImages.length;
            switchDetailImage(nextIdx);
        }}

        function updateCarLoan() {{
            const dpVal = parseFloat(document.getElementById('calc-dp-slider')?.value || 0);
            const periodYears = parseFloat(document.getElementById('calc-period-select')?.value || 9);
            const interestRate = parseFloat(document.getElementById('calc-rate-select')?.value || 0.025);
            
            const dpText = document.getElementById('calc-dp-text');
            if (dpText) dpText.innerText = 'RM ' + Math.round(dpVal).toLocaleString();

            const principal = carPrice - dpVal;
            if (principal <= 0) {{
                document.getElementById('calc-monthly-result').innerText = "RM 0 / bln";
                return;
            }}

            const totalInterest = principal * interestRate * periodYears;
            const totalLoan = principal + totalInterest;
            const totalMonths = periodYears * 12;
            const monthly = Math.round(totalLoan / totalMonths);

            const resultEl = document.getElementById('calc-monthly-result');
            if (resultEl) resultEl.innerText = '~RM ' + monthly.toLocaleString() + ' / bln';
            const carMonthlyDisp = document.getElementById('car-monthly-display');
            if (carMonthlyDisp) carMonthlyDisp.innerText = '~RM ' + monthly.toLocaleString() + ' / bln';
        }}

        window.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowRight') stepDetailImage(1);
            if (e.key === 'ArrowLeft') stepDetailImage(-1);
        }});
    </script>
""" + get_footer(depth=1) + "</body></html>"

    with open(os.path.join(STOK_DIR, f"{car['slug']}.html"), "w", encoding="utf-8") as out_f:
        out_f.write(detail_html)

# Update index.html header & hero
with open("index.html", "r", encoding="utf-8") as in_f:
    home_html = in_f.read()

h_start = home_html.find('<!-- Top Running Marquee Bar')
if h_start == -1:
    h_start = home_html.find('<!-- Top Running Text')
h_end = home_html.find('<!-- Hero Section')

if h_start != -1 and h_end != -1:
    home_html = home_html[:h_start] + get_header("home") + "\n" + home_html[h_end:]

old_hero_reg = re.compile(r'<!-- Hero Action Buttons -->[\s\S]*?</div>\s*</div>\s*<!-- Right Side Card', re.MULTILINE)
clean_hero_btns = """<!-- Hero Action Buttons -->
                    <div class="flex flex-col sm:flex-row gap-3 pt-2">
                        <a href="katalog.html" class="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 rounded-xl bg-amber-400 hover:bg-amber-500 text-slate-950 font-bold text-xs uppercase tracking-wider transition-all shadow-md text-center">
                            Buka Bilik Pameran (20 Stok) ➔
                        </a>
                        <a href="kalkulator.html" class="w-full sm:w-auto inline-flex items-center justify-center px-5 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs uppercase tracking-wider transition-all text-center">
                            Kira Anggaran Pinjaman
                        </a>
                        <a href="https://wa.me/60108118559?text=Salam%20Sales%20Advisor,%20saya%20ingin%20semak%20senarai%20stok%20terkini%20dan%20kelayakan%20loan." target="_blank" rel="noopener noreferrer" class="w-full sm:w-auto inline-flex items-center justify-center px-5 py-3.5 rounded-xl bg-brand-emerald hover:bg-brand-emeraldHover text-white font-bold text-xs uppercase tracking-wider transition-all shadow-md text-center">
                            Hubungi WhatsApp
                        </a>
                    </div>
                </div>
                <!-- Right Side Card"""

home_html = old_hero_reg.sub(clean_hero_btns, home_html)

with open("index.html", "w", encoding="utf-8") as out_f:
    out_f.write(home_html)

# Generate sitemap.xml & robots.txt
sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{BASE_URL}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>
  <url><loc>{BASE_URL}/katalog.html</loc><changefreq>daily</changefreq><priority>0.9</priority></url>
  <url><loc>{BASE_URL}/kalkulator.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>{BASE_URL}/proses.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>{BASE_URL}/dokumen.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
  <url><loc>{BASE_URL}/faq.html</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>
"""

for car in cars:
    sitemap_xml += f"  <url><loc>{BASE_URL}/stok/{car['slug']}.html</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n"

sitemap_xml += "</urlset>\n"

with open("sitemap.xml", "w", encoding="utf-8") as out_f:
    out_f.write(sitemap_xml)

robots_txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""

with open("robots.txt", "w", encoding="utf-8") as out_f:
    out_f.write(robots_txt)

print("SUCCESS: Full multi-page platform built successfully!")
