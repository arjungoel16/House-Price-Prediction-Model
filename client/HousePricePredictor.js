import React, { useState, useEffect, useCallback } from "react";

function HousePricePredictor() {
  const [features, setFeatures] = useState({ size: "", bedrooms: "", bathrooms: "", location: "" });
  const [prediction, setPrediction] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch("http://localhost:5000/locations");
        if (!response.ok) throw new Error("Failed to fetch locations");
        const data = await response.json();
        setLocations(data.locations);
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    };

    fetchLocations();
  }, []);

  const handleChange = useCallback((e) => {
    setFeatures((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPrediction(null);

    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features }),
      });

      if (!response.ok) throw new Error("Prediction failed");

      const data = await response.json();
      setPrediction(data.predicted_price);
    } catch (error) {
      console.error("Error predicting price:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto bg-white shadow-lg rounded-lg p-6">
      <h1 className="text-2xl font-bold text-center mb-6 text-gray-700">House Price Predictor</h1>

      <form onSubmit={handleSubmit} className="space-y-5">
        {["size", "bedrooms", "bathrooms"].map((field) => (
          <div key={field} className="flex flex-col">
            <label htmlFor={field} className="text-sm font-medium text-gray-600">
              {field.charAt(0).toUpperCase() + field.slice(1)}:
            </label>
            <input
              type="number"
              id={field}
              name={field}
              value={features[field]}
              onChange={handleChange}
              placeholder={`Enter ${field}`}
              className="border rounded-lg p-3 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
        ))}

        <div className="flex flex-col">
          <label htmlFor="location" className="text-sm font-medium text-gray-600">Location:</label>
          <select
            id="location"
            name="location"
            value={features.location}
            onChange={handleChange}
            className="border rounded-lg p-3 focus:ring-2 focus:ring-blue-400"
            required
          >
            <option value="">Select location</option>
            {locations.map((loc, index) => (
              <option key={index} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-semibold p-3 rounded-lg transition hover:bg-blue-600 disabled:bg-gray-400"
          disabled={loading}
        >
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {prediction !== null && (
        <div className="mt-6 bg-gray-100 p-4 rounded-lg shadow-md text-center">
          <p className="text-lg font-semibold text-gray-700">Predicted Price:</p>
          <p className="text-2xl font-bold text-green-600">${prediction.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
}

export default HousePricePredictor;
