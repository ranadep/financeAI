const express = require("express");
const router = express.Router();
const Expense = require("../models/Expense");

// Helper to get month totals
async function getMonthSummary(month) {
  const expenses = await Expense.find({ month });
  const total = expenses.reduce((sum, e) => sum + e.amount, 0);
  const categories = {};
  expenses.forEach((e) => {
    categories[e.category] = (categories[e.category] || 0) + e.amount;
  });
  return { total, categories, expenses };
}

// 🔁 Compare two months
router.get("/compare", async (req, res) => {
  const { month1, month2 } = req.query;
  try {
    const [curr, prev] = await Promise.all([
      getMonthSummary(month1),
      getMonthSummary(month2),
    ]);

    const changeFromLastMonth =
      prev.total === 0 ? "N/A" : `${(((curr.total - prev.total) / prev.total) * 100).toFixed(1)}%`;

    const categories = {};
    const allCats = new Set([...Object.keys(curr.categories), ...Object.keys(prev.categories)]);
    allCats.forEach((cat) => {
      const current = curr.categories[cat] || 0;
      const previous = prev.categories[cat] || 0;
      const change = previous === 0
        ? (current === 0 ? "0%" : "+∞%")
        : `${(((current - previous) / previous) * 100).toFixed(1)}%`;
      categories[cat] = { change };
    });

    res.json({ changeFromLastMonth, categories });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 💡 Suggestions
router.get("/suggestions/:month", async (req, res) => {
  const { month } = req.params;
  try {
    const curr = await getMonthSummary(month);
    const prevMonth = new Date(`${month}-01`);
    prevMonth.setMonth(prevMonth.getMonth() - 1);
    const prev = await getMonthSummary(prevMonth.toISOString().slice(0, 7));

    const suggestions = [];
    for (let cat of Object.keys(curr.categories)) {
      const current = curr.categories[cat] || 0;
      const previous = prev.categories[cat] || 0;
      const changePercent =
        previous === 0 ? 100 : ((current - previous) / previous) * 100;
      if (changePercent > 15) {
        suggestions.push(`⚠️ Spending on ${cat} increased by ${changePercent.toFixed(1)}%. Consider budgeting.`);
      } else if (changePercent < -10) {
        suggestions.push(`✅ Spending on ${cat} decreased by ${Math.abs(changePercent).toFixed(1)}%. Good job!`);
      }
    }

    res.json({ suggestions });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 📈 Projection
router.get("/projection/:month", async (req, res) => {
  const { month } = req.params;
  try {
    const now = new Date();
    const currentDate = now.getDate();
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();

    const { total: currentSpent } = await getMonthSummary(month);
    const projectedMonthEnd = (currentSpent / currentDate) * daysInMonth;
    const budget = 25000; // you can make this dynamic later

    const warning = projectedMonthEnd > budget
      ? `At this rate, you'll exceed your budget of $${budget} by $${(projectedMonthEnd - budget).toFixed(2)}.`
      : null;

    res.json({
      currentSpent,
      projectedMonthEnd,
      budget,
      warning
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
