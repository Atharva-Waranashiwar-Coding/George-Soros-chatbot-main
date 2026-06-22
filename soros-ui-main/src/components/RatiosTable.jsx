import React, { useState } from 'react'; // Import useState

// --- Ratio Explanations ---
// Storing explanations in a simple object, keyed by ratio name
const ratioExplanations = {
    "Gross Margin (resilience)": "Core profitability buffer; higher margins help absorb shocks. Soros lens: resilience to macro squeezes.",
    "SG&A / Gross Profit (cost discipline)": "Overhead burden relative to gross profit. Lower ratios signal operating flexibility when conditions tighten.",
    "R&D / Gross Profit (innovation spend)": "Innovation drag on profits; useful context for cyclicals/tech when liquidity tightens.",
    "Depreciation / Gross Profit (asset intensity)": "Capital intensity proxy; heavy upkeep makes businesses fragile under rate stress.",
    "Interest Exp / Operating Income (debt burden)": "Service cost of debt versus operating income; high burden limits room to maneuver in tightening cycles.",
    "Income Tax Rate": "Reference to statutory rates; sharp deviations can hint at one-offs or jurisdictional exposure.",
    "Net Margin (profit capture)": "End-state profitability; durable margins matter when volatility rises.",
    "EPS Growth (YoY)": "Momentum in per-share earnings; shrinking EPS is a warning to cut risk.",
    "Cash vs Current Debt (liquidity buffer)": "Cash coverage of near-term debt. Critical for staying liquid when funding tightens.",
    "Debt to Equity (balance-sheet leverage)": "Balance-sheet stress gauge. Soros lens: leverage amplifies reflexive moves.",
    "Preferred Stock": "Flags capital stack complexity; can bite common holders in stress.",
    "Retained Earnings Growth (capacity to self-fund)": "Internal funding capacity; lowers dependency on external capital during dislocations.",
    "Treasury Stock Exists?": "Repurchases signal confidence; but watch if done with leverage late-cycle.",
    "CapEx / Net Income (cash demands)": "Investment drain on cash; high needs reduce flexibility if credit conditions tighten.",
};
// --- End Ratio Explanations ---


// Inline SVG Icons
const InfoIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 text-blue-300 group-hover:text-blue-100 cursor-help"> {/* Changed cursor */}
        <path strokeLinecap="round" strokeLinejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
    </svg>
);


// Inline SVG Icons for Check/Cross/Minus
const CheckIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-green-400">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const CrossIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-red-400">
        <path strokeLinecap="round" strokeLinejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);

const MinusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 text-gray-500">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
);


const MeetsIcon = ({ meets }) => {
    if (meets === true) {
        return <span title="Meets Rule"><CheckIcon /></span>;
    } else if (meets === false) {
        return <span title="Does Not Meet Rule"><CrossIcon /></span>;
    } else {
        return <span title="Not Applicable"><MinusIcon /></span>;
    }
};

function RatiosTable({ ratios }) {

    // State to track which tooltip is hovered (using index)
    const [hoveredTooltip, setHoveredTooltip] = useState(null);

    if (!Array.isArray(ratios) || ratios.length === 0) {
        return <p className="dark:text-dark-text-secondary">No ratio data available.</p>;
    }

    return (
        <div className="overflow-x-auto relative shadow-md sm:rounded-lg border border-dark-border">
            <table className="w-full text-sm text-left text-dark-text-secondary">
                <thead className="text-xs uppercase bg-dark-card dark:bg-opacity-50 text-dark-text-secondary">
                    <tr>
                        <th scope="col" className="py-3 px-6">
                            Ratio Name
                        </th>
                        <th scope="col" className="py-3 px-6">
                            Value
                        </th>
                        <th scope="col" className="py-3 px-6">
                            Risk Check
                        </th>
                        <th scope="col" className="py-3 px-6 text-center">
                            Meets Rule?
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {ratios.map((ratio, index) => (
                        <tr key={index} className={`border-b dark:border-dark-border ${index % 2 === 0 ? 'bg-dark-card bg-opacity-20' : 'bg-dark-card bg-opacity-40'} hover:bg-dark-card-hover`}>
                            {/* Ratio Name Cell with Tooltip Trigger */}
                            <th scope="row" className="py-4 px-6 font-medium text-dark-text whitespace-nowrap relative">
                                {/* Wrap name and icon in a div for hover events and relative positioning context */}
                                <div
                                    className="flex items-center space-x-2 group cursor-help" // Use group for potential icon styling on hover
                                    onMouseEnter={() => setHoveredTooltip(index)}
                                    onMouseLeave={() => setHoveredTooltip(null)}
                                >
                                    <span>{ratio.name || 'N/A'}</span>
                                    <InfoIcon /> {/* Icon indicates information is available */}

                                    {/* Tooltip - Absolutely Positioned ABOVE, Conditionally Rendered */}
                                    {hoveredTooltip === index && (
                                        <div
                                            className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-max max-w-xs z-30 p-2 text-s font-normal text-dark-text bg-dark-bg rounded-md shadow-xl border border-dark-border pointer-events-none whitespace-normal"
                                        >
                                            {ratioExplanations[ratio.name] || 'No explanation available.'}
                                        </div>
                                    )}
                                </div>
                            </th>
                            {/* Other Cells */}
                            <td className="py-4 px-6">
                                {ratio.value !== undefined ? ratio.value : 'N/A'}
                            </td>
                            <td className="py-4 px-6">
                                {ratio.rule || 'N/A'}
                            </td>
                            <td className="py-4 px-6 flex justify-center items-center">
                                <MeetsIcon meets={ratio.meets} />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default RatiosTable;
