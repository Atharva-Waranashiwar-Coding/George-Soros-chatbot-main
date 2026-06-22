import axios from 'axios';

const RAG_API_URL = 'http://127.0.0.1:8000/api/ragbot/';

/**
 * Sends a message to the RAG chatbot backend API.
 * @param {string} userMessage - The message text from the user.
 * @returns {Promise<string>} - A promise that resolves with the bot's reply text.
 * @throws {Error} - Throws an error if the API call fails.
 */
export const sendMessageToBot = async (userMessage) => {
    console.log('Sending message to RAG API:', RAG_API_URL);

    try {
        // Send message to the RAG endpoint using POST
        const payload = { message: userMessage };
        const response = await axios.post(RAG_API_URL, payload);

        if (response.data && response.data.reply) {
            return response.data.reply;
        } else {
            throw new Error('Invalid response format from RAG API');
        }
    } catch (error) {
        console.error('Error sending message to RAG bot:', error);
        const errorMsg = error.response?.data?.reply || error.response?.data?.error || 'Failed to get response from the chatbot.';
        throw new Error(errorMsg);
    }
};
