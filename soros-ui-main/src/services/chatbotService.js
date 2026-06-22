import axios from 'axios';

const GEMINI_API_URL = 'http://127.0.0.1:8000/api/chatbot/';
const RAG_API_URL = 'http://127.0.0.1:8000/api/ragbot/';
const TRANSFORMER_API_URL = 'http://127.0.0.1:8000/api/transformerbot/';

/**
 * Sends a message to the appropriate chatbot backend API based on selected model.
 * @param {string} userMessage - The message text from the user.
 * @param {'gemini' | 'rag'} selectedModel - The model selected by the user.
 * @returns {Promise<string>} - A promise that resolves with the bot's reply text.
 * @throws {Error} - Throws an error if the API call fails.
 */
export const sendMessageToBot = async (userMessage, selectedModel, transformerToken) => {
    // Determine the correct API endpoint based on the selected model
    let apiUrl = GEMINI_API_URL;
    if (selectedModel === 'rag') apiUrl = RAG_API_URL;
    if (selectedModel === 'transformer') apiUrl = TRANSFORMER_API_URL;
    console.log(`Sending message to ${selectedModel} API: ${apiUrl}`);

    try {
        // Send message to the chosen endpoint using POST
        const payload = { message: userMessage };
        if (selectedModel === 'transformer' && transformerToken) {
            payload.token = transformerToken;
        }
        const response = await axios.post(apiUrl, payload);

        if (response.data && response.data.reply) {
            return response.data.reply;
        } else {
            throw new Error(`Invalid response format from ${selectedModel} API`);
        }
    } catch (error) {
        console.error(`Error sending message to ${selectedModel} bot:`, error);
        const errorMsg = error.response?.data?.reply || error.response?.data?.error || `Failed to get response from ${selectedModel} model.`;
        throw new Error(errorMsg);
    }
};
