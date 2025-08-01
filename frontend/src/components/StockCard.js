// frontend/src/components/StockCard.js
export default function StockCard({ stock }) {
  return (
    <div style={{
      padding: '1rem',
      border: '1px solid #ccc',
      borderRadius: '10px',
      marginBottom: '1rem',
      boxShadow: '0px 2px 5px rgba(0,0,0,0.1)'
    }}>
      <h3>{stock.ticker}</h3>
      {stock.score_pct_change_1d !== undefined && (
        <p><strong>1-day momentum:</strong> {stock.score_pct_change_1d.toFixed(2)}%</p>
      )}
      <p><strong>Action:</strong> {stock.action}</p>
      <p><strong>Reason:</strong> {stock.reason}</p>
    </div>
  );
}
