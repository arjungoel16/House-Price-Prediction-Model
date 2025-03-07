import React, { useState, useEffect, useCallback } from "react";

// HousePricePredictor component allows users to input house details and get a price prediction.
function HousePricePredictor() {
  // State for user input features, prediction result, available locations, and loading state.
  const [features, setFeatures] = useState({ size: "", bedrooms: "", bathrooms: "", location: "" });
  const [prediction, setPrediction] = useState(null);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [customLocation, setCustomLocation] = useState(""); // Store user-inputted location
  const [showCustomLocation, setShowCustomLocation] = useState(false); // Track if custom input should be shown

  // Fetch available locations from the backend when the component mounts.
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch("http://localhost:5000/locations");
        if (!response.ok) throw new Error("Failed to fetch locations");

        const data = await response.json();
        console.log("Fetched locations:", data.locations); // Debug log

        if (data.locations && data.locations.length > 0) {
          setLocations([...data.locations, "Other"]);
        } else {
          console.warn("No locations received from API.");
        }
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    };

    fetchLocations();
  }, []);


  // Handles changes to form fields, including handling the "Other" location selection.
  const handleChange = useCallback((e) => {
    const { name, value } = e.target;

    if (name === "location") {
      if (value === "Other") {
        setShowCustomLocation(true); // Show text input for custom location
        setFeatures((prev) => ({ ...prev, location: "" })); // Reset location value
      } else {
        setShowCustomLocation(false); // Hide custom location input
        setFeatures((prev) => ({ ...prev, location: value }));
      }
    } else {
      setFeatures((prev) => ({ ...prev, [name]: value }));
    }
  }, []);

  // Updates the custom location state when the user types a new custom location.
  const handleCustomLocationChange = (e) => {
    setCustomLocation(e.target.value);
  };

  // Handles form submission and sends user input to the backend for prediction.
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPrediction(null);

    try {
      const selectedLocation = showCustomLocation ? customLocation : features.location; // Use custom location if "Other"

      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features: { ...features, location: selectedLocation } }),
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
        {/* Input fields for size, bedrooms, and bathrooms */}
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

        {/* Location dropdown */}
        <div className="flex flex-col">
          <label htmlFor="location" className="text-sm font-medium text-gray-600">Enter your location:</label>
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

        {/* Custom Location Input (only shows when "Other" is selected) */}
        {showCustomLocation && (
          <div className="flex flex-col">
            <label htmlFor="custom-location" className="text-sm font-medium text-gray-600">Enter your city/town:</label>
            <input
              type="text"
              id="custom-location"
              name="customLocation"
              value={customLocation}
              onChange={handleCustomLocationChange}
              placeholder="Enter your city or town"
              className="border rounded-lg p-3 focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          className="w-full bg-blue-500 text-white font-semibold p-3 rounded-lg transition hover:bg-blue-600 disabled:bg-gray-400"
          disabled={loading}
        >
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>

      {/* Display predicted price */}
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
