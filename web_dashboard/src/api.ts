import axios from 'axios';

// Use relative path for static serving from same origin
const API_URL = '/dashboard';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Order {
    id: number;
    id_percakapan: string;
    nama_customer: string;
    jenis_barang: string;
    nama_barang: string;
    jumlah_barang: number;
    estimasi_nilai_barang: number;
    wilayah: string;
    email: string;
    status: string;
    created_at: string;
}

/**
 * Fetch all orders from the backend.
 * @returns {Promise<Order[]>} List of orders.
 */
export const getOrders = async (): Promise<Order[]> => {
    const response = await api.get('/orders');
    return response.data;
};

/**
 * Send verification email for a specific order.
 * @param {number} orderId - The ID of the order to verify.
 * @returns {Promise<any>} Response from the server.
 */
export const sendVerification = async (orderId: number) => {
    const response = await api.post(`/verification/${orderId}`);
    return response.data;
};

/**
 * Delete an order by ID.
 * @param {number} orderId - The ID of the order to delete.
 * @returns {Promise<any>} Response from the server.
 */
export const deleteOrder = async (orderId: number) => {
    const response = await api.delete(`/order/${orderId}`);
    return response.data;
};
