import React, { useState, useEffect } from "react";

function HousePricePredictor() {
  const [features, setFeatures] = useState({
    size: "",
    bedrooms: "",
    bathrooms: "",
    location: "",
  });
  const [prediction, setPrediction] = useState(null);
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    // Fetch possible locations from the backend
    const fetchLocations = async () => {
      const response = await fetch("http://localhost:5000/locations");
      const data = await response.json();
      setLocations(data.locations);
    };

    fetchLocations();
  }, []);

  const handleChange = (e) => {
    setFeatures({ ...features, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ features }),
    });
    const data = await response.json();
    setPrediction(data.predicted_price);
  };

  return (
    <div className="container mx-auto p-6 max-w-xl">
      <h1 className="text-2xl font-semibold mb-4">House Price Predictor</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col">
          <label htmlFor="size" className="text-sm font-medium">Size (sq ft):</label>
          <input
            type="number"
            id="size"
            name="size"
            value={features.size}
            onChange={handleChange}
            placeholder="Enter size in square feet"
            className="border p-2"
            required
          />
        </div>

        <div className="flex flex-col">
          <label htmlFor="bedrooms" className="text-sm font-medium">Bedrooms:</label>
          <input
            type="number"
            id="bedrooms"
            name="bedrooms"
            value={features.bedrooms}
            onChange={handleChange}
            placeholder="Enter number of bedrooms"
            className="border p-2"
            required
          />
        </div>

        <div className="flex flex-col">
          <label htmlFor="bathrooms" className="text-sm font-medium">Bathrooms:</label>
          <input
            type="number"
            id="bathrooms"
            name="bathrooms"
            value={features.bathrooms}
            onChange={handleChange}
            placeholder="Enter number of bathrooms"
            className="border p-2"
            required
          />
        </div>

        <div className="flex flex-col">
          <label htmlFor="location" className="text-sm font-medium">Location:</label>
          <select
            id="location"
            name="location"
            value={features.location}
            onChange={handleChange}
            className="border p-2"
            required
          >
            <option value="">Select location</option>
            {locations.map((location, index) => (
              <option key={index} value={location}>{location}</option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded-md"
        >
          Predict
        </button>
      </form>

      {prediction !== null && (
        <p className="mt-4 text-lg">Predicted Price: ${prediction.toFixed(2)}</p>
      )}
    </div>
  );
}

export default HousePricePredictor;
