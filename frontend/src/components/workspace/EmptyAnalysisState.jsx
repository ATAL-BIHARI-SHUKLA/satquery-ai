/* eslint-disable react-hooks/set-state-in-effect, no-unused-vars, no-empty */
import { useState, useRef, useEffect } from "react";
import ConversationInput from "./ConversationInput";
import { useDebounce } from "use-debounce";


export default function EmptyAnalysisState({ 
  currentQuery, 
  setCurrentQuery, 
  onSubmit, 
  loading, 
  onFileUpload, 
  uploading,
  onSubmitLocation 
}) {
  const [mode, setMode] = useState("location"); // 'location' | 'image'
  const [locationSearch, setLocationSearch] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef(null);
  


  const [debouncedLocationSearch] = useDebounce(locationSearch, 800);

  const searchNominatim = async (query) => {
    setIsSearching(true);
    try {
      const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      setSuggestions(data);
      setShowSuggestions(true);
    } catch (error) {
      console.error("Nominatim search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  useEffect(() => {
    if (debouncedLocationSearch && debouncedLocationSearch.trim().length > 2) {
      searchNominatim(debouncedLocationSearch);
    } else {
      setSuggestions([]);
    }
  }, [debouncedLocationSearch]);

  const handleSelectSuggestion = (suggestion) => {
    setLocationSearch(suggestion.display_name);
    setShowSuggestions(false);
    if (onSubmitLocation) {
      onSubmitLocation({
        latitude: parseFloat(suggestion.lat),
        longitude: parseFloat(suggestion.lon),
        locationName: suggestion.display_name,
        radiusKm: 2
      });
    }
  };

  const handleExampleLocation = (name) => {
    setLocationSearch(name);
    searchNominatim(name);
  };

  const handleLiveLocation = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
            const data = await response.json();
            const name = data.display_name || "Current Location";
            
            setLocationSearch(name);
            if (onSubmitLocation) {
              onSubmitLocation({
                latitude: lat,
                longitude: lng,
                locationName: name,
                radiusKm: 2
              });
            }
          } catch (error) {
            console.error("Reverse geocoding error:", error);
            if (onSubmitLocation) {
              onSubmitLocation({
                latitude: lat,
                longitude: lng,
                locationName: "Current Location",
                radiusKm: 2
              });
            }
          }
        },
        (error) => {
          console.error("Error obtaining location", error);
          alert("Could not access your location. Please check your permissions or search manually.");
        }
      );
    } else {
      alert("Geolocation is not supported by your browser");
    }
  };

  const exampleQueries = [
    "Is there any visible change between these images?",
    "What type of land cover is visible here?",
    "Identify buildings in this area.",
    "Compare the optical and SAR observations."
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] h-full max-w-3xl mx-auto px-6 py-10">
      
      {/* Mode Toggle */}
      <div className="flex p-1 bg-surface border border-border-subtle rounded-xl mb-12">
        <button 
          onClick={() => setMode("location")}
          className={`px-6 py-2 rounded-lg text-sm font-medium transition-colors ${mode === "location" ? "bg-bg-base text-primary shadow-sm" : "text-text-muted hover:text-text-main"}`}
        >
          Analyze a Location
        </button>
        <button 
          onClick={() => setMode("image")}
          className={`px-6 py-2 rounded-lg text-sm font-medium transition-colors ${mode === "image" ? "bg-bg-base text-primary shadow-sm" : "text-text-muted hover:text-text-main"}`}
        >
          Analyze Your Own Image
        </button>
      </div>

      {mode === "location" ? (
        <div className="w-full flex flex-col items-center animate-in fade-in zoom-in duration-300">
          <div className="text-center mb-10">
            <h2 className="text-4xl md:text-5xl font-bold text-text-main mb-4 tracking-tight">Start with a location</h2>
            <p className="text-text-muted text-lg max-w-xl mx-auto leading-relaxed">
              Choose an area on Earth to explore satellite imagery and ask natural-language questions about it.
            </p>
          </div>

          <div className="w-full max-w-2xl relative mb-8">
              <input
                ref={inputRef}
                type="text"
                placeholder="Search a city, area, landmark or coordinates..."
                className="w-full px-6 py-4 rounded-2xl bg-surface border border-border-subtle text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary placeholder-text-muted/50 shadow-lg text-lg pr-32"
                value={locationSearch}
                onChange={(e) => {
                  setLocationSearch(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => {
                  if (suggestions.length > 0) setShowSuggestions(true);
                }}
                onBlur={() => {
                  // Delay hiding so clicks on suggestions register
                  setTimeout(() => setShowSuggestions(false), 200);
                }}
              />
              
              <button
                onClick={handleLiveLocation}
                className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2 px-3 py-2 text-sm text-sky-400 hover:text-sky-300 hover:bg-sky-400/10 rounded-lg transition-colors font-medium"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                My Location
              </button>

              {/* Suggestions Dropdown */}
              {showSuggestions && (suggestions.length > 0 || isSearching) && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-surface border border-border-subtle rounded-xl shadow-xl overflow-hidden z-50">
                  {isSearching ? (
                    <div className="px-4 py-3 text-sm text-text-muted">Searching...</div>
                  ) : (
                    <ul>
                      {suggestions.map((item, index) => (
                        <li 
                          key={item.place_id || index}
                          className="px-4 py-3 hover:bg-white/5 cursor-pointer text-sm text-text-main border-b border-border-subtle/50 last:border-0 truncate"
                          onClick={() => handleSelectSuggestion(item)}
                        >
                          {item.display_name}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
          </div>

          <div className="flex flex-wrap gap-2 justify-center">
            {["Delhi", "Punjab, India", "Ludhiana", "San Francisco, CA"].map((loc) => (
              <button
                key={loc}
                onClick={() => handleExampleLocation(loc)}
                className="px-4 py-2 rounded-full border border-border-subtle bg-surface hover:bg-white/5 hover:border-primary/30 transition-all text-xs text-text-muted hover:text-primary font-medium"
              >
                {loc}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="w-full flex flex-col items-center animate-in fade-in zoom-in duration-300">
          <div className="text-center mb-10">
            <h2 className="text-4xl md:text-5xl font-bold text-text-main mb-4 tracking-tight">Ask your satellite imagery.</h2>
            <p className="text-text-muted text-lg max-w-xl mx-auto leading-relaxed">
              Upload imagery, describe what you want to know, and SatQuery will select the appropriate remote-sensing workflow.
            </p>
          </div>

          <div className="w-full mb-12">
            <ConversationInput 
              currentQuery={currentQuery}
              setCurrentQuery={setCurrentQuery}
              onSubmit={onSubmit}
              loading={loading}
              onFileUpload={onFileUpload}
              uploading={uploading}
              isLarge={true}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full">
            {exampleQueries.map((q, i) => (
              <button
                key={i}
                onClick={() => setCurrentQuery(q)}
                className="text-left px-5 py-4 rounded-xl border border-border-subtle bg-surface hover:bg-white/5 hover:border-white/10 transition-all text-sm text-text-muted hover:text-main"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
