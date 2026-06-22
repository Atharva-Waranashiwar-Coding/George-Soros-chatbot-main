import React, { useState } from 'react';
import { runPairBacktest } from '../services/pairService';

const LineChart = ({ title, series, height = 240 }) => {
    const padding = { top: 16, right: 12, bottom: 28, left: 12 };
    const cleanSeries = series.map(s => ({
        ...s,
        data: s.data.filter(p => p.y !== null && p.y !== undefined && !Number.isNaN(p.y)),
    }));
    const allPoints = cleanSeries.flatMap(s => s.data);
    if (!allPoints.length) {
        return (
            <div className="p-4 rounded-xl border border-cyan-500/20 bg-slate-900/60">
                <p className="text-sm text-slate-300">No data to plot.</p>
            </div>
        );
    }

    const minY = Math.min(...allPoints.map(p => p.y));
    const maxY = Math.max(...allPoints.map(p => p.y));
    const ySpan = maxY - minY || 1;

    const maxLen = Math.max(...cleanSeries.map(s => s.data.length));

    const width = 640;
    const h = height;

    const scaleX = (idx) => padding.left + (idx / Math.max(1, maxLen - 1)) * (width - padding.left - padding.right);
    const scaleY = (y) => h - padding.bottom - ((y - minY) / ySpan) * (h - padding.top - padding.bottom);

    const paths = cleanSeries.map(s => {
        if (!s.data.length) return '';
        return s.data.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(2)} ${scaleY(p.y).toFixed(2)}`).join(' ');
    });

    return (
        <div className="p-4 rounded-xl border border-cyan-500/20 bg-slate-900/60">
            <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-semibold text-cyan-200">{title}</p>
                <div className="flex gap-3 text-xs text-slate-300">
                    {cleanSeries
                        .filter(s => s.data.length)
                        .map((s) => (
                            <span key={s.label} className="flex items-center gap-1">
                                <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: s.color || '#67e8f9' }} />
                                {s.label}
                            </span>
                        ))}
                </div>
            </div>
            <svg viewBox={`0 0 ${width} ${h}`} className="w-full">
                {cleanSeries.map((s, idx) => (
                    <path
                        key={s.label}
                        d={paths[idx]}
                        fill="none"
                        stroke={s.color || '#67e8f9'}
                        strokeWidth={s.thick ? 2.4 : 1.6}
                        strokeDasharray={s.dash ? '6 4' : 'none'}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                ))}
            </svg>
            <div className="flex justify-between text-[11px] text-slate-400 mt-2">
                <span>{cleanSeries.find(s => s.data.length)?.data?.[0]?.label || 'start'}</span>
                <span>{cleanSeries.find(s => s.data.length)?.data?.slice(-1)?.[0]?.label || 'end'}</span>
            </div>
        </div>
    );
};

function PairTradingPage() {
    const [symbolA, setSymbolA] = useState('');
    const [symbolB, setSymbolB] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [entryZ, setEntryZ] = useState(1.0);
    const [exitZ, setExitZ] = useState(0.25);
    const [rollingWindow, setRollingWindow] = useState(60);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setResult(null);
        if (!symbolA.trim() || !symbolB.trim()) {
            setError('Please enter both symbols.');
            return;
        }
        setLoading(true);
        try {
            const data = await runPairBacktest({
                symbolA: symbolA.trim().toUpperCase(),
                symbolB: symbolB.trim().toUpperCase(),
                startDate,
                endDate,
                entryZ,
                exitZ,
                rollingWindow,
            });
            setResult(data);
        } catch (err) {
            const msg = err.response?.data?.error || err.message || 'Failed to run backtest.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const formatPct = (value) => {
        if (value === null || value === undefined) return 'N/A';
        return `${(value * 100).toFixed(2)}%`;
    };

    return (
        <div className="min-h-screen text-slate-100 p-4 md:p-8 w-full md:w-4/5 lg:w-3/4 mx-auto" style={{ background: "radial-gradient(circle at 20% 20%, rgba(0,255,200,0.08), transparent 35%), radial-gradient(circle at 80% 0%, rgba(120,50,255,0.12), transparent 30%), linear-gradient(135deg, #05080f 0%, #0a0f1e 50%, #05070d 100%)" }}>
            <h1 className="text-3xl md:text-4xl font-extrabold mb-8 text-center text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-emerald-300 tracking-tight drop-shadow-lg">
                Soros Pairs Trading Backtest
            </h1>

            <form onSubmit={handleSubmit} className="bg-slate-950/60 backdrop-blur rounded-2xl shadow-2xl p-6 md:p-8 border border-cyan-500/20 ring-1 ring-cyan-400/10 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Symbol A</label>
                        <input
                            value={symbolA}
                            onChange={(e) => setSymbolA(e.target.value)}
                            placeholder="e.g., XLF"
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Symbol B</label>
                        <input
                            value={symbolB}
                            onChange={(e) => setSymbolB(e.target.value)}
                            placeholder="e.g., JPM"
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Start Date (optional)</label>
                        <input
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            max={new Date().toISOString().split('T')[0]}
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">End Date (optional)</label>
                        <input
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            max={new Date().toISOString().split('T')[0]}
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Entry Z (|z| &gt;)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={entryZ}
                            onChange={(e) => setEntryZ(parseFloat(e.target.value) || 0)}
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Exit Z (|z| &lt;)</label>
                        <input
                            type="number"
                            step="0.05"
                            value={exitZ}
                            onChange={(e) => setExitZ(parseFloat(e.target.value) || 0)}
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                    <div>
                        <label className="block text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Rolling Window (days)</label>
                        <input
                            type="number"
                            min="5"
                            value={rollingWindow}
                            onChange={(e) => setRollingWindow(parseInt(e.target.value, 10) || 0)}
                            className="w-full p-3 bg-slate-900/80 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 shadow-inner"
                        />
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={loading}
                        className="px-6 py-3 bg-gradient-to-r from-cyan-400 via-emerald-400 to-teal-500 hover:from-cyan-300 hover:to-emerald-400 text-slate-950 font-semibold rounded-lg transition-all duration-300 disabled:opacity-60 shadow-lg shadow-cyan-500/30"
                    >
                        {loading ? 'Running...' : 'Run Backtest'}
                    </button>
                </div>

                {error && (
                    <div className="text-red-300 bg-red-900/40 border border-red-700 rounded-lg p-4">
                        {error}
                    </div>
                )}
            </form>

            {result && (
                <div className="mt-8 bg-slate-950/60 backdrop-blur rounded-2xl shadow-2xl p-6 md:p-8 border border-cyan-500/20 ring-1 ring-cyan-400/10 space-y-4">
                    <h2 className="text-2xl font-semibold text-cyan-200 mb-4 tracking-tight">Results</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Metric label="Hedge Ratio (A ~ beta * B)" value={result.hedgeRatio?.toFixed(4)} />
                        <Metric label="Cointegration test statistic" value={result.cointegrationTestStatistic !== null && result.cointegrationTestStatistic !== undefined ? result.cointegrationTestStatistic?.toFixed(3) : 'N/A'} />
                        <Metric label="Cointegration p-value" value={result.cointegrationPValue !== null && result.cointegrationPValue !== undefined ? result.cointegrationPValue?.toFixed(4) : 'N/A (library unavailable)'} />
                        <Metric label="Cointegration verdict" value={result.cointegrationInterpretation || 'N/A'} />
                        <Metric label="Latest Z-Score" value={result.latestZScore !== null ? result.latestZScore?.toFixed(2) : 'N/A'} />
                        <Metric label="Trades Triggered" value={result.trades} />
                        <Metric label="Cumulative Return" value={formatPct(result.cumulativeReturn)} highlight />
                    </div>
                    <CointegrationCallout
                        pValue={result.cointegrationPValue}
                        interpretation={result.cointegrationInterpretation}
                        symbols={result.symbols}
                    />
                    <div className="text-slate-300 text-sm">
                        <p>
                            Strategy: enter when |z| &gt; {result.entryZ ?? entryZ}, exit when |z| &lt; {result.exitZ ?? exitZ}, z computed on rolling {result.rollingWindow ?? rollingWindow}-day mean/std.
                            Long spread = long A / short beta*B; short spread = short A / long beta*B.
                        </p>
                    </div>
                    {(result.suggestedRange || result.georgeSorosInsight) && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {result.suggestedRange && (
                                <div className="p-4 rounded-lg border border-cyan-500/30 bg-slate-900/70">
                                    <p className="text-xs uppercase tracking-wide text-cyan-200/80 mb-1">Suggested Date Window</p>
                                    <p className="text-base text-slate-100 font-semibold">
                                        {result.suggestedRange.start} → {result.suggestedRange.end}
                                    </p>
                                    {result.suggestionReason && (
                                        <p className="text-sm text-slate-300 mt-2">{result.suggestionReason}</p>
                                    )}
                                </div>
                            )}
                            {result.georgeSorosInsight && (
                                <div className="p-4 rounded-lg border border-cyan-500/30 bg-slate-900/70">
                                    <p className="text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Insight from George Soros</p>
                                    <pre className="whitespace-pre-wrap text-slate-100 text-sm leading-relaxed">{result.georgeSorosInsight}</pre>
                                </div>
                            )}
                        </div>
                    )}
                    {result.strategyTweak && (
                        <div className="p-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10">
                            <p className="text-xs uppercase tracking-wide text-emerald-200/80 mb-2">Suggested Strategy Tweak</p>
                            <p className="text-sm text-slate-100 leading-relaxed whitespace-pre-wrap">{result.strategyTweak}</p>
                        </div>
                    )}
                    {(result.spreadSeries?.length || result.pnlSeries?.length || result.priceSeries?.length) && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {result.spreadSeries?.length > 0 && (
                                <LineChart
                                    title="Spread & Bands"
                                    series={[
                                        {
                                            label: 'Spread',
                                            color: '#67e8f9',
                                            thick: true,
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.spread,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: 'Mean',
                                            color: '#a5b4fc',
                                            dash: true,
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.mean,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: 'Entry Upper',
                                            color: '#f472b6',
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.entryUpper,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: 'Entry Lower',
                                            color: '#f472b6',
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.entryLower,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: 'Exit Upper',
                                            color: '#fde68a',
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.exitUpper,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: 'Exit Lower',
                                            color: '#fde68a',
                                            data: result.spreadSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.exitLower,
                                                label: d.date,
                                            })),
                                        },
                                    ]}
                                />
                            )}
                            {result.pnlSeries?.length > 0 && (
                                <LineChart
                                    title="Cumulative PnL"
                                    series={[
                                        {
                                            label: 'PnL',
                                            color: '#34d399',
                                            thick: true,
                                            data: result.pnlSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.cumulativeReturn,
                                                label: d.date,
                                            })),
                                        },
                                    ]}
                                />
                            )}
                            {result.priceSeries?.length > 0 && (
                                <LineChart
                                    title="Prices (A vs B)"
                                    series={[
                                        {
                                            label: `Price ${result.symbols?.A || 'A'}`,
                                            color: '#60a5fa',
                                            data: result.priceSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.priceA,
                                                label: d.date,
                                            })),
                                        },
                                        {
                                            label: `Price ${result.symbols?.B || 'B'}`,
                                            color: '#fbbf24',
                                            data: result.priceSeries.map((d, idx) => ({
                                                x: idx,
                                                y: d.priceB,
                                                label: d.date,
                                            })),
                                        },
                                    ]}
                                />
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

const Metric = ({ label, value, highlight }) => (
    <div className={`p-4 rounded-lg border ${highlight ? 'border-emerald-400/50 bg-emerald-400/10' : 'border-cyan-500/20 bg-slate-900/70'}`}>
        <p className="text-xs uppercase tracking-wide text-cyan-200/80 mb-1">{label}</p>
        <p className={`text-xl font-semibold ${highlight ? 'text-emerald-200' : 'text-slate-100'}`}>{value}</p>
    </div>
);

const CointegrationCallout = ({ pValue, interpretation, symbols }) => {
    const isCointegrated = pValue !== null && pValue !== undefined && pValue < 0.05;
    const verdictText = isCointegrated
        ? '✅ p-value < 0.05: reject H₀ (no cointegration) → series appear cointegrated.'
        : pValue !== null && pValue !== undefined
            ? '❌ p-value ≥ 0.05: fail to reject H₀ → not cointegrated on this window.'
            : 'Cointegration test unavailable (library or data issue).';

    return (
        <div className={`p-4 rounded-xl border ${isCointegrated ? 'border-emerald-400/40 bg-emerald-400/5' : 'border-amber-400/40 bg-amber-400/5'}`}>
            <div className="flex items-start justify-between gap-3">
                <div>
                    <p className="text-xs uppercase tracking-wide text-cyan-200/80 mb-2">Cointegration Decision</p>
                    <p className="text-sm text-slate-100 leading-relaxed">
                        Symbols: {symbols?.A} vs {symbols?.B} &nbsp;|&nbsp; {interpretation || 'N/A'}
                    </p>
                    <p className="text-sm text-slate-200 mt-2">{verdictText}</p>
                </div>
                <div className="text-[11px] text-slate-300 bg-slate-900/60 rounded-lg p-3 border border-cyan-500/20">
                    <p className="font-semibold text-cyan-100 mb-1">Test framing</p>
                    <p>H₀: No cointegration</p>
                    <p>H₁: Series are cointegrated</p>
                    <p>Use: p-value &lt; 0.05 → reject H₀</p>
                </div>
            </div>
        </div>
    );
};

export default PairTradingPage;
