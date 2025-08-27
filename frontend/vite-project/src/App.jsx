import { useState } from "react";
import ProductCard from "./ProductCard";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!message) return;
    setLoading(true);
    setResponse("");
    setProducts([]);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });

      const data = await res.json();
      setResponse(data.response);
      setProducts(data.products);
    } catch (err) {
      setResponse("Error connecting to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>TikTok Shop AI Search</h1>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Type your query..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button onClick={handleSubmit}>Search</button>
      </div>

      {loading && <p className="loading-text">Loading...</p>}

      {response && (
        <div className="response-container">
          <h3>AI Response:</h3>
          <p>{response}</p>

          {products.length > 0 && (
            <>
              <h4>Products:</h4>
              <div className="products-grid">
                {products.map((p) => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
