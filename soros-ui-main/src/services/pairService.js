import axios from 'axios';

const PAIRS_API_URL = 'http://127.0.0.1:8000/api/pairs/';

export const runPairBacktest = async ({ symbolA, symbolB, startDate, endDate, entryZ, exitZ, rollingWindow }) => {
    const payload = {
        symbolA,
        symbolB,
        startDate,
        endDate,
        entryZ,
        exitZ,
        rollingWindow,
    };

    const response = await axios.post(PAIRS_API_URL, payload);
    return response.data;
};
