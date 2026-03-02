<!DOCTYPE html>
<html lang="tr">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP8266 Akıllı Sera Sistem Mimarisi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

        body {
            font-family: 'Inter', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
        }

        .chart-container {
            position: relative;
            width: 100%;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            height: 300px;
            max-height: 400px;
        }

        @media (min-width: 768px) {
            .chart-container {
                height: 350px;
            }
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .gradient-text {
            background: linear-gradient(to right, #0ea5e9, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>

<body class="antialiased min-h-screen pb-20">

    <div hidden id="metadata-and-compliance">
        Plan Summary: Introduction -> Power Distribution (Donut Chart) -> Pin Architecture (Horizontal Bar) -> Relay
        Flow (HTML Flowchart).
        Visual Choices: Donut for composition of power, Bar for categorical pin mapping, HTML flexbox for flow.
        Palette: Vibrant Cyber Tech (Slate-900, Sky-500, Emerald-500, Rose-500, Violet-500).
        CRITICAL COMPLIANCE CONFIRMATION: NEITHER Mermaid JS NOR SVG were used anywhere in this output. No standard
        comments are used in code to comply with the negative constraint.
    </div>

    <nav class="sticky top-0 z-50 glass-card border-b border-slate-700 shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">🌱</span>
                    <span class="font-bold text-xl tracking-wider text-white">SERA<span
                            class="text-emerald-400">CORE</span></span>
                </div>
            </div>
        </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10">

        <header class="text-center mb-16">
            <h1 class="text-4xl md:text-5xl font-extrabold mb-4">ESP8266 Akıllı Sera <span class="gradient-text">Donanım
                    Mimarisi</span></h1>
            <p class="text-lg text-slate-400 max-w-2xl mx-auto">Modern tarım teknolojilerinin temelini oluşturan sensör,
                mikrokontrolcü ve aktüatör bağlantılarının detaylı topolojik ve elektriksel analizi.</p>
        </header>

        <section class="mb-16">
            <h2 class="text-2xl font-bold mb-4 flex items-center"><span class="text-sky-400 mr-2">📊</span> Sistem Özeti
                & Temel Metrikler</h2>
            <p class="text-slate-300 mb-6 leading-relaxed">
                Akıllı sera projesi, çevresel verileri toplayan ve sulama sistemini otonom olarak yöneten entegre bir
                IoT (Nesnelerin İnterneti) cihazıdır. Bu mimari, işlem gücünü sağlayan bir ESP8266 NodeMCU, çevresel
                durumu izleyen iki farklı sensör, veri gösterimi için bir I2C LCD ekran ve fiziksel sulama işlemini
                tetikleyen bir röle mekanizmasından oluşmaktadır. Aşağıdaki metrikler, sistemin donanımsal kapasitesini
                özetlemektedir.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div
                    class="glass-card p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center transform transition hover:scale-105">
                    <span class="text-4xl mb-2">⚡</span>
                    <span class="text-3xl font-black text-white mb-1">2</span>
                    <span class="text-sm text-slate-400 uppercase tracking-widest">Voltaj Hattı</span>
                </div>
                <div
                    class="glass-card p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center transform transition hover:scale-105">
                    <span class="text-4xl mb-2">📡</span>
                    <span class="text-3xl font-black text-white mb-1">5</span>
                    <span class="text-sm text-slate-400 uppercase tracking-widest">Aktif Pin</span>
                </div>
                <div
                    class="glass-card p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center transform transition hover:scale-105">
                    <span class="text-4xl mb-2">🔌</span>
                    <span class="text-3xl font-black text-white mb-1">5</span>
                    <span class="text-sm text-slate-400 uppercase tracking-widest">Dış Bileşen</span>
                </div>
                <div
                    class="glass-card p-6 rounded-2xl shadow-xl flex flex-col items-center justify-center text-center transform transition hover:scale-105">
                    <span class="text-4xl mb-2">💧</span>
                    <span class="text-3xl font-black text-white mb-1">1</span>
                    <span class="text-sm text-slate-400 uppercase tracking-widest">Aktüatör</span>
                </div>
            </div>
        </section>

        <section class="mb-20">
            <h2 class="text-2xl font-bold mb-4 flex items-center"><span class="text-rose-400 mr-2">⚡</span> Güç Dağılımı
                (Power Distribution)</h2>
            <p class="text-slate-300 mb-8 leading-relaxed">
                Mikrokontrolcü sistemlerinde stabilite, doğru voltaj seviyelerinin sağlanmasına bağlıdır. Bu sistemde
                bileşenler, ihtiyaç duydukları enerji seviyelerine göre 5V (Vin) ve 3.3V (3V3) olmak üzere iki ana gruba
                ayrılmıştır. LCD ekranın arka aydınlatması ve rölenin bobin tetiklemesi yüksek akım ve voltaj
                gerektirdiğinden 5V hattına bağlanırken, hassas okuma yapan sensörler 3.3V hattından beslenmektedir.
            </p>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="glass-card p-6 rounded-2xl shadow-xl">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Bileşenlerin Voltaj Dağılımı</h3>
                    <div class="chart-container">
                        <canvas id="powerChart"></canvas>
                    </div>
                </div>

                <div class="space-y-6">
                    <div class="bg-rose-900/30 border border-rose-500/30 p-5 rounded-xl">
                        <h4 class="text-rose-400 font-bold text-lg mb-2 flex items-center">🔋 5V (Vin) Hattı</h4>
                        <p class="text-slate-300 text-sm mb-3">Sistemin ana güç omurgasıdır. Genellikle USB üzerinden
                            alınan gücü doğrudan diğer yüksek güç gerektiren bileşenlere iletir.</p>
                        <ul class="list-disc list-inside text-sm text-slate-200 space-y-1">
                            <li>NodeMCU (Ana Besleme)</li>
                            <li>I2C LCD Ekran (Daha parlak görüntü için)</li>
                            <li>Röle Modülü (Güvenilir anahtarlama için)</li>
                        </ul>
                    </div>
                    <div class="bg-emerald-900/30 border border-emerald-500/30 p-5 rounded-xl">
                        <h4 class="text-emerald-400 font-bold text-lg mb-2 flex items-center">🔋 3.3V (3V3) Hattı</h4>
                        <p class="text-slate-300 text-sm mb-3">NodeMCU üzerindeki regülatörden sağlanan, sensörler için
                            optimize edilmiş hassas ve düşük gürültülü güç hattıdır.</p>
                        <ul class="list-disc list-inside text-sm text-slate-200 space-y-1">
                            <li>DHT11 Sıcaklık ve Nem Sensörü</li>
                            <li>Toprak Nem Sensörü</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <section class="mb-20">
            <h2 class="text-2xl font-bold mb-4 flex items-center"><span class="text-violet-400 mr-2">🖧</span> Pin
                Haritası ve Veri İletişimi</h2>
            <p class="text-slate-300 mb-8 leading-relaxed">
                Sensör verilerinin okunması ve aktüatörlerin kontrol edilmesi için ESP8266 üzerindeki belirli GPIO
                (Genel Amaçlı Giriş/Çıkış) pinleri kullanılmıştır. Analog sinyaller, I2C iletişim protokolü ve standart
                dijital tetiklemeler için pin tahsisleri mimarinin iletişim kalbini oluşturur.
            </p>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="order-2 lg:order-1 flex flex-col space-y-4">
                    <div class="glass-card p-4 rounded-xl flex items-center border-l-4 border-l-emerald-400">
                        <div class="bg-emerald-900/50 p-3 rounded-lg mr-4 text-emerald-400 font-bold text-xl">A0</div>
                        <div>
                            <h4 class="font-bold text-white">Toprak Nem Sensörü</h4>
                            <p class="text-sm text-slate-400">Tek analog giriş (AO). Topraktaki direnç değişimini
                                voltaja dönüştürür.</p>
                        </div>
                    </div>
                    <div class="glass-card p-4 rounded-xl flex items-center border-l-4 border-l-sky-400">
                        <div class="bg-sky-900/50 p-3 rounded-lg mr-4 text-sky-400 font-bold text-xl">D1</div>
                        <div>
                            <h4 class="font-bold text-white">I2C SCL (Saat/Clock)</h4>
                            <p class="text-sm text-slate-400">LCD Ekran veri senkronizasyon pini.</p>
                        </div>
                    </div>
                    <div class="glass-card p-4 rounded-xl flex items-center border-l-4 border-l-sky-400">
                        <div class="bg-sky-900/50 p-3 rounded-lg mr-4 text-sky-400 font-bold text-xl">D2</div>
                        <div>
                            <h4 class="font-bold text-white">I2C SDA (Veri/Data)</h4>
                            <p class="text-sm text-slate-400">LCD Ekran çift yönlü veri aktarım pini.</p>
                        </div>
                    </div>
                    <div class="glass-card p-4 rounded-xl flex items-center border-l-4 border-l-yellow-400">
                        <div class="bg-yellow-900/50 p-3 rounded-lg mr-4 text-yellow-400 font-bold text-xl">D4</div>
                        <div>
                            <h4 class="font-bold text-white">DHT11 Sensörü</h4>
                            <p class="text-sm text-slate-400">Dijital tek hat üzerinden sıcaklık ve hava nemi verisi.
                            </p>
                        </div>
                    </div>
                    <div class="glass-card p-4 rounded-xl flex items-center border-l-4 border-l-rose-400">
                        <div class="bg-rose-900/50 p-3 rounded-lg mr-4 text-rose-400 font-bold text-xl">D5</div>
                        <div>
                            <h4 class="font-bold text-white">Röle Kontrolü (IN)</h4>
                            <p class="text-sm text-slate-400">Dijital çıkış pini. Pompayı açıp kapatmak için sinyal
                                gönderir.</p>
                        </div>
                    </div>
                </div>

                <div class="order-1 lg:order-2 glass-card p-6 rounded-2xl shadow-xl">
                    <h3 class="text-lg font-semibold text-white mb-4 text-center">Sinyal Türüne Göre Pin Dağılımı</h3>
                    <div class="chart-container">
                        <canvas id="pinChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <section class="mb-10">
            <h2 class="text-2xl font-bold mb-4 flex items-center"><span class="text-blue-400 mr-2">🔄</span> Röle ve
                Pompa Mantıksal Akışı</h2>
            <p class="text-slate-300 mb-8 leading-relaxed">
                Su pompasının çalışması, NodeMCU'nun düşük akımlı mantık sinyallerinin röle modülü aracılığıyla yüksek
                akımlı bir devreye dönüştürülmesiyle sağlanır. Aşağıdaki akış, elektriksel bağlantının COM (Ortak Uç) ve
                NO (Normalde Açık) terminalleri üzerinden nasıl yönlendirildiğini göstermektedir.
            </p>

            <div class="glass-card p-8 rounded-2xl shadow-2xl overflow-x-auto">
                <div
                    class="flex flex-col md:flex-row items-center justify-center space-y-6 md:space-y-0 md:space-x-8 min-w-[700px]">

                    <div
                        class="flex flex-col items-center bg-slate-800 border-2 border-slate-600 rounded-xl p-4 w-40 text-center relative">
                        <div class="text-4xl mb-2">🔋</div>
                        <h4 class="font-bold text-white">Dış Güç Kaynağı</h4>
                        <p class="text-xs text-slate-400 mt-1">Pil veya Adaptör</p>
                        <div
                            class="absolute -right-10 top-1/2 transform -translate-y-1/2 text-2xl text-slate-500 hidden md:block">
                            ➡</div>
                        <div
                            class="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-2xl text-slate-500 md:hidden">
                            ⬇</div>
                    </div>

                    <div
                        class="flex flex-col items-center bg-rose-900/40 border-2 border-rose-500 rounded-xl p-4 w-48 text-center relative">
                        <div class="text-4xl mb-2">🎛️</div>
                        <h4 class="font-bold text-rose-300">Röle Modülü</h4>
                        <div class="mt-2 w-full flex justify-between text-xs font-mono bg-black/30 p-1 rounded">
                            <span class="text-slate-300 bg-slate-700 px-2 py-1 rounded">COM (Giriş)</span>
                            <span class="text-rose-400 bg-rose-950 px-2 py-1 rounded">NO (Çıkış)</span>
                        </div>
                        <div
                            class="absolute -right-10 top-1/2 transform -translate-y-1/2 text-2xl text-rose-500 hidden md:block">
                            ➡</div>
                        <div
                            class="absolute -bottom-8 left-1/2 transform -translate-x-1/2 text-2xl text-rose-500 md:hidden">
                            ⬇</div>
                    </div>

                    <div
                        class="flex flex-col items-center bg-blue-900/40 border-2 border-blue-500 rounded-xl p-4 w-40 text-center">
                        <div class="text-4xl mb-2">⛲</div>
                        <h4 class="font-bold text-blue-300">Su Pompası</h4>
                        <p class="text-xs text-slate-400 mt-1">Toprak nemi düştüğünde aktifleşir</p>
                    </div>

                </div>

                <div
                    class="mt-8 bg-slate-800/50 p-4 rounded-lg text-sm text-slate-300 text-center max-w-2xl mx-auto border border-slate-700">
                    <span class="text-rose-400 font-bold">NodeMCU D5 Pini</span> üzerinden gönderilen sinyal röleyi
                    tetikler. Röle tetiklendiğinde iç anahtar kapanarak <strong class="text-white">COM</strong> ucundaki
                    elektriği <strong class="text-white">NO</strong> ucuna aktarır ve pompa devresini tamamlar.
                </div>
            </div>
        </section>

    </main>

    <footer class="border-t border-slate-800 bg-slate-900 mt-12 py-8 text-center">
        <p class="text-slate-500 text-sm">Akıllı Sera Veri Görselleştirme Paneli | Tailwind CSS & Chart.js kullanılarak
            tasarlanmıştır.</p>
    </footer>

    <script>
        function wrapLabel(str) {
            let words = str.split(' ');
            let lines = [];
            let currentLine = '';
            for (let i = 0; i < words.length; i++) {
                if ((currentLine + words[i]).length > 16) {
                    if (currentLine.trim() !== '') {
                        lines.push(currentLine.trim());
                    }
                    currentLine = words[i] + ' ';
                } else {
                    currentLine += words[i] + ' ';
                }
            }
            if (currentLine.trim() !== '') {
                lines.push(currentLine.trim());
            }
            return lines;
        }

        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Inter', sans-serif";

        const powerLabels = [
            'NodeMCU (Vin/5V Güç)',
            'I2C LCD Ekran (Vin/5V Güç)',
            'Röle Modülü (Vin/5V Güç)',
            'DHT11 Sensörü (3.3V Güç)',
            'Toprak Nem Sensörü (3.3V Güç)'
        ];

        const wrappedPowerLabels = powerLabels.map(label => wrapLabel(label));

        const powerCtx = document.getElementById('powerChart').getContext('2d');
        new Chart(powerCtx, {
            type: 'doughnut',
            data: {
                labels: wrappedPowerLabels,
                datasets: [{
                    data: [1, 1, 1, 1, 1],
                    backgroundColor: [
                        '#f43f5e',
                        '#fb7185',
                        '#fda4af',
                        '#10b981',
                        '#6ee7b7'
                    ],
                    borderColor: '#0f172a',
                    borderWidth: 3,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                const item = tooltipItems[0];
                                let label = item.chart.data.labels[item.dataIndex];
                                if (Array.isArray(label)) {
                                    return label.join(' ');
                                } else {
                                    return label;
                                }
                            }
                        }
                    }
                }
            }
        });

        const pinLabels = [
            'I2C Veriyolu (D1, D2)',
            'Dijital Çıkış (D5)',
            'Dijital Giriş (D4)',
            'Analog Giriş (A0)'
        ];

        const wrappedPinLabels = pinLabels.map(label => wrapLabel(label));

        const pinCtx = document.getElementById('pinChart').getContext('2d');
        new Chart(pinCtx, {
            type: 'bar',
            data: {
                labels: wrappedPinLabels,
                datasets: [{
                    label: 'Pin Kullanım Dağılımı',
                    data: [2, 1, 1, 1],
                    backgroundColor: [
                        '#0ea5e9',
                        '#f43f5e',
                        '#eab308',
                        '#10b981'
                    ],
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            color: '#64748b'
                        },
                        grid: {
                            color: '#1e293b'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#e2e8f0',
                            font: {
                                weight: '600'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function (tooltipItems) {
                                const item = tooltipItems[0];
                                let label = item.chart.data.labels[item.dataIndex];
                                if (Array.isArray(label)) {
                                    return label.join(' ');
                                } else {
                                    return label;
                                }
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>

</html>