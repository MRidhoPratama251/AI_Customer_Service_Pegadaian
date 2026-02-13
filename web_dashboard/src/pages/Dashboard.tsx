import { useState, useEffect } from 'react';
import { getOrders, sendVerification, deleteOrder, type Order } from '../api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Trash2, CheckCircle, Mail, Loader2, RefreshCw } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export default function Dashboard() {
    // State for storing orders list
    const [orders, setOrders] = useState<Order[]>([]);
    // Loading state for UI feedback
    const [loading, setLoading] = useState(true);
    // Track which order is currently sending an email to disable repeated clicks
    const [sendingEmailId, setSendingEmailId] = useState<number | null>(null);

    /**
     * Fetch orders from the API.
     * Updates local state and handles loading indicators.
     */
    const fetchData = async () => {
        setLoading(true);
        try {
            const data = await getOrders();
            setOrders(data);
        } catch (error) {
            console.error("Failed to fetch orders", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Auto-refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const handleVerify = async (id: number) => {
        setSendingEmailId(id);
        try {
            await sendVerification(id);
            alert("Verification email sent!");
            fetchData(); // Refresh to update status or logs
        } catch (error) {
            alert("Failed to send verification email.");
            console.error(error);
        } finally {
            setSendingEmailId(null);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm("Are you sure you want to delete this order?")) return;
        try {
            await deleteOrder(id);
            setOrders(orders.filter(o => o.id !== id));
        } catch (error) {
            alert("Failed to delete order.");
            console.error(error);
        }
    };

    // Prepare Chart Data
    const regionData = orders.reduce((acc, order) => {
        const region = order.wilayah || 'Unknown';
        acc[region] = (acc[region] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    const chartData = Object.entries(regionData).map(([name, value]) => ({ name, value }));

    return (
        <div className="min-h-screen bg-gray-50 p-4 md:p-8 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Admin Dashboard</h1>
                        <p className="text-gray-500 text-sm mt-1">Manage pawn shop orders and verifications</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-600"
                        title="Refresh Data"
                    >
                        <RefreshCw className={cn("w-5 h-5", loading && "animate-spin")} />
                    </button>
                </div>

                {/* Stats & Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Summary Cards */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="text-sm font-medium text-gray-500 uppercase">Total Active Orders</h3>
                            <p className="text-4xl font-bold text-gray-900 mt-2">{orders.length}</p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="text-sm font-medium text-gray-500 uppercase">Orders On Process</h3>
                            <p className="text-4xl font-bold text-blue-600 mt-2">
                                {orders.filter(o => o.status === 'On Process').length}
                            </p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="text-sm font-medium text-gray-500 uppercase">On Verification</h3>
                            <p className="text-4xl font-bold text-orange-600 mt-2">
                                {orders.filter(o => o.status === 'On Verification').length}
                            </p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                            <h3 className="text-sm font-medium text-gray-500 uppercase">Verified Orders</h3>
                            <p className="text-4xl font-bold text-green-600 mt-2">
                                {orders.filter(o => o.status === 'Verified').length}
                            </p>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-lg font-semibold text-gray-900 mb-6">Regional Distribution</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={chartData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {chartData.map((_entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Data Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100">
                        <h3 className="text-lg font-semibold text-gray-900">Order List</h3>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-gray-600">
                            <thead className="bg-gray-50 text-gray-900 font-medium uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-4">ID</th>
                                    <th className="px-6 py-4">Customer</th>
                                    <th className="px-6 py-4">Item (Type/Name)</th>
                                    <th className="px-6 py-4 text-center">Qty</th>
                                    <th className="px-6 py-4 text-right">Est. Value</th>
                                    <th className="px-6 py-4">Region</th>
                                    <th className="px-6 py-4">Status</th>
                                    <th className="px-6 py-4 text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {orders.length === 0 ? (
                                    <tr>
                                        <td colSpan={8} className="px-6 py-12 text-center text-gray-400">
                                            No orders found.
                                        </td>
                                    </tr>
                                ) : (
                                    orders.map((order) => (
                                        <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4 truncate max-w-[100px]" title={order.id_percakapan}>
                                                #{order.id}
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="font-medium text-gray-900">{order.nama_customer}</div>
                                                <div className="text-xs text-gray-400">{order.email}</div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="font-medium text-gray-900">{order.nama_barang}</div>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                                    {order.jenis_barang}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-center">{order.jumlah_barang}</td>
                                            <td className="px-6 py-4 text-right font-medium text-gray-900">
                                                {new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(order.estimasi_nilai_barang)}
                                            </td>
                                            <td className="px-6 py-4">{order.wilayah}</td>
                                            <td className="px-6 py-4">
                                                <span className={cn(
                                                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize",
                                                    order.status === 'Verified'
                                                        ? "bg-green-100 text-green-800"
                                                        : order.status === 'On Verification'
                                                            ? "bg-orange-100 text-orange-800"
                                                            : "bg-yellow-100 text-yellow-800"
                                                )}>
                                                    {order.status === 'Verified' ? <CheckCircle className="w-3 h-3 mr-1" /> : <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                                                    {order.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center justify-center space-x-2">
                                                    <button
                                                        onClick={() => handleVerify(order.id)}
                                                        disabled={order.status === 'Verified' || order.status === 'On Verification' || sendingEmailId === order.id}
                                                        className={cn(
                                                            "p-2 rounded-lg transition-colors focus:ring-2 focus:ring-offset-1 focus:ring-blue-500",
                                                            order.status === 'Verified' || order.status === 'On Verification'
                                                                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                                                : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
                                                        )}
                                                        title="Verify via Email"
                                                    >
                                                        {sendingEmailId === order.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mail className="w-4 h-4" />}
                                                    </button>

                                                    <button
                                                        onClick={() => handleDelete(order.id)}
                                                        className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors focus:ring-2 focus:ring-offset-1 focus:ring-red-500"
                                                        title="Delete Order"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
}
