import React from 'react';

function StatementTable({ title, statement }) {
    if (!Array.isArray(statement) || statement.length === 0) {
        return <p className="dark:text-dark-text-secondary italic mt-4">No data available for {title}.</p>;
    }

    const headers = Object.keys(statement[0] || {})
        .filter(key => key !== 'Item')
        .sort((a, b) => new Date(b) - new Date(a));

    return (
        <div className="mt-6">
            <h4 className="text-lg font-semibold mb-3 text-brand-gold-light">{title}</h4>
            <div className="overflow-x-auto relative shadow-md sm:rounded-lg border border-dark-border">
                <table className="w-full text-sm text-left text-dark-text-secondary">
                    <thead className="text-xs uppercase bg-dark-card dark:bg-opacity-50 text-dark-text-secondary">
                        <tr>
                            <th scope="col" className="py-3 px-6 sticky left-0 bg-dark-card dark:bg-opacity-50 z-10"> {/* Adjusted sticky header bg */}
                                Item
                            </th>
                            {headers.map(header => (
                                <th key={header} scope="col" className="py-3 px-6 text-right whitespace-nowrap">
                                    {header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {statement.map((item, index) => (
                            <tr key={index} className={`border-b dark:border-dark-border ${index % 2 === 0 ? 'bg-dark-card bg-opacity-20' : 'bg-dark-card bg-opacity-40'} hover:bg-dark-card-hover group`}>
                                {/* Make sticky column background match row background */}
                                <th scope="row" className={`py-4 px-6 font-medium text-dark-text whitespace-nowrap sticky left-0 z-10 ${index % 2 === 0 ? 'bg-dark-card bg-opacity-20' : 'bg-dark-card bg-opacity-40'} group-hover:bg-dark-card-hover`}>
                                    {item.Item || 'N/A'}
                                </th>
                                {headers.map(header => (
                                    <td key={header} className="py-4 px-6 text-right whitespace-nowrap">
                                        {item[header] !== undefined ? item[header] : 'N/A'}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default StatementTable;