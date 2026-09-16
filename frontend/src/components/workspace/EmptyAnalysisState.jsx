import { useState, useRef, useEffect } from "react";
import ConversationInput from "./ConversationInput";
import { useJsApiLoader, Autocomplete } from "@react-google-maps/api";
import { useDebounce } from "use-debounce";

const libraries = ["places"];

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
  const autocompleteRef = useRef(null);
  const { isLoaded } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "",
    libraries,
  });

  const [debouncedLocationSearch] = useDebounce(locationSearch, 800);

  useEffect(() => {
    if (debouncedLocationSearch && debouncedLocationSearch.trim().length > 2) {
      handleSearchLocation(debouncedLocationSearch);
    }
  }, [debouncedLocationSearch]);

  const handleSearchLocation = (searchQuery = locationSearch) => {
    if (!searchQuery.trim()) return;

    if (window.google && window.google.maps && window.google.maps.Geocoder) {
      const geocoder = new window.google.maps.Geocoder();
      geocoder.geocode({ address: searchQuery }, (results, status) => {
        if (status === "OK" && results[0]) {
          const location = results[0].geometry.location;
          const lat = location.lat();
          const lng = location.lng();
          const name = results[0].formatted_address;
          
          if (onSubmitLocation) {
            onSubmitLocation({
              lat,
              lng,
              locationName: name,
              radiusKm: 2
            });
          }
        }
      });
    }
  };

  const handlePlaceChanged = () => {
    if (autocompleteRef.current) {
      const place = autocompleteRef.current.getPlace();
      if (place && place.geometry) {
        const lat = place.geometry.location.lat();
        const lng = place.geometry.location.lng();
        const name = place.formatted_address || place.name || "Selected Location";
        
        if (onSubmitLocation) {
          onSubmitLocation({
            lat,
            lng,
            locationName: name,
            radiusKm: 2
          });
        }
      }
    }
  };

  const handleExampleLocation = (name) => {
    setLocationSearch(name);
    handleSearchLocation(name);
  };

  const handleLiveLocation = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          
          // Reverse geocode to get name
          if (window.google && window.google.maps && window.google.maps.Geocoder) {
            const geocoder = new window.google.maps.Geocoder();
            geocoder.geocode({ location: { lat, lng } }, (results, status) => {
              let name = "Current Location";
              if (status === "OK" && results[0]) {
                name = results[0].formatted_address;
              }
              if (onSubmitLocation) {
                onSubmitLocation({
                  lat,
                  lng,
                  locationName: name,
                  radiusKm: 2
                });
              }
            });
          } else {
             // Fallback if google maps isn't loaded
             if (onSubmitLocation) {
                onSubmitLocation({
                  lat,
                  lng,
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
             {isLoaded ? (
                <Autocomplete
                  onLoad={(autocomplete) => {
                    autocompleteRef.current = autocomplete;
                  }}
                  onPlaceChanged={handlePlaceChanged}
                >
                  <input
                    type="text"
                    placeholder="Search a city, address, place or coordinates..."
                    className="w-full px-6 py-4 rounded-2xl bg-surface border border-border-subtle text-text-main focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary placeholder-text-muted/50 shadow-lg text-lg pr-32"
                    value={locationSearch}
                    onChange={(e) => setLocationSearch(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleSearchLocation();
                      }
                    }}
                  />
                </Autocomplete>
              ) : (
                <input
                  type="text"
                  placeholder="Loading maps..."
                  className="w-full px-6 py-4 rounded-2xl bg-surface border border-border-subtle text-text-main focus:outline-none placeholder-text-muted/50 shadow-lg text-lg"
                  disabled
                />
              )}
              
              <button
                onClick={handleLiveLocation}
                className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2 px-3 py-2 text-sm text-sky-400 hover:text-sky-300 hover:bg-sky-400/10 rounded-lg transition-colors font-medium"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Live Location
              </button>
          </div>

          <div className="flex flex-wrap gap-2 justify-center">
            {["Delhi", "Punjab, India", "30.3165, 78.0322", "San Francisco, CA"].map((loc) => (
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
                className="text-left px-5 py-4 rounded-xl border border-border-subtle bg-surface hover:bg-white/5 hover:border-white/10 transition-all text-sm text-text-muted hover:text-text-main"
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
