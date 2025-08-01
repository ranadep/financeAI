import React, { useState, useEffect } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { addExpense, deleteExpense } from "../api";

const categories = [
  "Rent", "Electricity", "Water", "Outside Food",
  "Cooking Material", "Misc", "Clothing", "Electronics"
];

const COLORS = [
  "#2563EB", "#22C55E", "#F59E0B", "#EF4444",
  "#8B5CF6", "#14B8A6", "#F43F5E", "#10B981",
];

export default function ExpenseTracker() {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Rent");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);
  const [expensesList, setExpensesList] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [projections, setProjections] = useState(null);
  const [comparison, setComparison] = useState(null);


  const handleAddExpense = async () => {
    if (!amount || !category || !description || !date) return;
    const expense = {
      amount: parseFloat(amount),
      category,
      description,
      date,
      month: date.slice(0, 7),
    };
    try {
      await addExpense(expense); // ✅ imported one is used here
      setAmount("");
      setCategory("Rent");
      setDescription("");
      setDate(new Date().toISOString().split("T")[0]);
      fetchData();
    } catch (err) {
      console.error("❌ Failed to post expense:", err.message);
    }
  };
  
  const handleDelete = async (id) => {
    try {
      await deleteExpense(id);
      fetchData(); // Refresh data after deletion
    } catch (err) {
      console.error("❌ Failed to delete expense:", err.message);
    }
  };
  

  const fetchData = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/expenses/${month}`);
      const categories = Object.entries(res.data.categories).map(([key, value]) => ({
        name: key,
        value,
      }));
      setData(categories);
      setTotal(res.data.total);
      setExpensesList(res.data.expenses);
  
      // Fetch Suggestions
      const suggestRes = await axios.get(`http://localhost:8000/insights/suggestions/${month}`);
      setSuggestions(suggestRes.data.suggestions || []);
  
      // Fetch Projection
      const projRes = await axios.get(`http://localhost:8000/insights/projection/${month}`);
      setProjections(projRes.data);
  
      // Fetch Comparison (previous month)
      const prev = new Date(new Date(month + "-01").setMonth(new Date(month + "-01").getMonth() - 1)).toISOString().slice(0, 7);
      const compareRes = await axios.get(`http://localhost:8000/insights/compare?month1=${month}&month2=${prev}`);
      setComparison(compareRes.data);
  
    } catch (err) {
      console.error("❌ Failed to fetch data:", err.message);
    }
  };
  

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, [month]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans text-gray-800">
      <div className="max-w-6xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-blue-700">💸 Expense Tracker</h1>

        {/* Expense Form */}
        <div className="bg-white shadow-md rounded-lg p-6 grid grid-cols-1 md:grid-cols-5 gap-4">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount ($)"
            className="border border-gray-300 p-2 rounded"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="border border-gray-300 p-2 rounded"
          >
            {categories.map((c) => <option key={c}>{c}</option>)}
          </select>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description"
            className="border border-gray-300 p-2 rounded"
          />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border border-gray-300 p-2 rounded"
          />
          <button
            onClick={handleAddExpense}
            className="bg-blue-600 text-white font-medium py-2 px-4 rounded hover:bg-blue-700 transition"
          >
            ➕ Add
          </button>

        </div>

        {/* Month Picker */}
        <div className="flex items-center space-x-4">
          <label className="font-medium text-lg">📆 Month:</label>
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border border-gray-300 p-2 rounded"
          />
        </div>

        {/* Summary Card */}
        <div className="bg-white p-6 rounded-lg shadow flex flex-col md:flex-row items-center justify-between">
          <div className="text-xl font-semibold">
            Total Spent in {month}: <span className="text-green-600">${total.toFixed(2)}</span>
          </div>
          {data.length > 0 && (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {data.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend layout="horizontal" verticalAlign="bottom" />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Summary Card */}
        {comparison && (
        <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-blue-700">📊 Month-over-Month Comparison</h2>
            <p className="mb-2">Change from last month: <strong>{comparison.changeFromLastMonth}</strong></p>
            {Object.entries(comparison.categories).map(([cat, val]) => (
            <p key={cat}>{cat}: {val.change}</p>
            ))}
        </div>
        )}

        {/* Savings Suggestions */}
        {suggestions.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-blue-700">💡 Savings Suggestions</h2>
            <ul className="list-disc pl-5 space-y-1">
            {suggestions.map((sug, i) => (
                <li key={i}>{sug}</li>
            ))}
            </ul>
        </div>
        )}

        {/* Budget Projection */}
        {projections && (
        <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4 text-blue-700">📈 Budget Projection</h2>
            <p>Current Spent: ${projections.currentSpent.toFixed(2)}</p>
            <p>Projected Month-End: ${projections.projectedMonthEnd.toFixed(2)}</p>
            <p>Budget: ${projections.budget.toFixed(2)}</p>
            {projections.warning && (
            <p className="text-red-600 font-semibold">⚠️ {projections.warning}</p>
            )}
        </div>
        )}


        {/* Expense Table */}
        {expensesList.length > 0 && (
        <div className="bg-white shadow-md rounded-lg overflow-x-auto">
            <table className="min-w-full text-sm text-left">
            <thead className="bg-gray-100 text-gray-700 uppercase tracking-wider">
                <tr>
                <th className="px-6 py-3">Amount ($)</th>
                <th className="px-6 py-3">Category</th>
                <th className="px-6 py-3">Description</th>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3">Delete</th>
                </tr>
            </thead>
            <tbody>
                {expensesList.map((exp, i) => (
                <tr key={exp._id} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="px-6 py-3 text-green-600">${exp.amount.toFixed(2)}</td>
                    <td className="px-6 py-3">{exp.category}</td>
                    <td className="px-6 py-3">{exp.description}</td>
                    <td className="px-6 py-3">{exp.date}</td>
                    <td className="px-6 py-3">
                    <button
                        onClick={() => {
                            const confirmed = window.confirm("Are you sure you want to delete this expense?");
                            if (confirmed) {
                            handleDelete(exp._id);
                            }
                        }}
                        className="text-red-600 hover:underline"
                        >
                        ❌ Delete
                        </button>
                    </td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
        )}
      </div>
    </div>
  );
}
