import { useRef, useState, useCallback, useEffect } from "react";
import { useDebounce } from "use-debounce";
import { api } from "../../services/api";
import {
  GoogleMap,
  useJsApiLoader,
  Marker,
  Autocomplete,
  Circle,
} from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "100%",
  borderRadius: "1rem",
};

const defaultCenter = { lat: 37.7749, lng: -122.4194 };
const libraries = ["places"];

export default function LandingWorkspace({ navigateTo }) {
  const { isLoaded } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "",
    libraries,
  });
  const fileInputRef = useRef(null);
  const autocompleteRef = useRef(null);
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("idle"); // idle, loading, success, error
  const [resultMessage, setResultMessage] = useState("");
  const [mode, setMode] = useState("location");
  const [locationSearch, setLocationSearch] = useState("");
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [mapCenter, setMapCenter] = useState(defaultCenter);
  const [debouncedLocationSearch] = useDebounce(locationSearch, 800);

  useEffect(() => {
    if (debouncedLocationSearch && debouncedLocationSearch.trim().length > 2) {
      // Don't search if the search string is exactly the current location name 
      // (happens when a user clicks an autocomplete suggestion)
      if (selectedLocation && selectedLocation.locationName === debouncedLocationSearch) {
        return;
      }
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
          setSelectedLocation((prev) => ({
            lat,
            lng,
            locationName: results[0].formatted_address,
            radiusKm: prev?.radiusKm || 2,
          }));
          setMapCenter({ lat, lng });
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
        const name =
          place.formatted_address || place.name || "Selected Location";
        setSelectedLocation((prev) => ({
          lat,
          lng,
          locationName: name,
          radiusKm: prev?.radiusKm || 2,
        }));
        setMapCenter({ lat, lng });
        setLocationSearch(name);
      }
    }
  };

  const handleMapClick = useCallback((e) => {
    if (e.latLng) {
      const lat = e.latLng.lat();
      const lng = e.latLng.lng();
      if (window.google && window.google.maps && window.google.maps.Geocoder) {
        const geocoder = new window.google.maps.Geocoder();
        geocoder.geocode({ location: { lat, lng } }, (results, status) => {
          let name = "Selected Location";
          if (status === "OK" && results[0]) {
            name = results[0].formatted_address;
          }
          setSelectedLocation((prev) => ({
            lat,
            lng,
            locationName: name,
            radiusKm: prev?.radiusKm || 2,
          }));
          setLocationSearch(name);
        });
      } else {
        setSelectedLocation((prev) => ({
          lat,
          lng,
          locationName: "Selected Location",
          radiusKm: prev?.radiusKm || 2,
        }));
      }
    }
  }, []);

  const handleFetchLiveLocation = () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const lat = latitude;
          const lng = longitude;
          setMapCenter({ lat, lng });
          
          if (window.google && window.google.maps && window.google.maps.Geocoder) {
            const geocoder = new window.google.maps.Geocoder();
            geocoder.geocode({ location: { lat, lng } }, (results, status) => {
              let name = "Current Location";
              if (status === "OK" && results[0]) {
                name = results[0].formatted_address;
              }
              setSelectedLocation((prev) => ({
                lat,
                lng,
                locationName: name,
                radiusKm: prev?.radiusKm || 2,
              }));
              setLocationSearch(name);
            });
          } else {
            setSelectedLocation((prev) => ({
              lat,
              lng,
              locationName: "Current Location",
              radiusKm: prev?.radiusKm || 2,
            }));
            setLocationSearch("Current Location");
          }
        },
        (error) => {
          console.error("Error getting location: ", error);
          alert("Unable to fetch your current location. Please ensure location access is allowed.");
        }
      );
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  };

  const handleAnalyzeLocation = async () => {
    if (!selectedLocation || !query.trim()) return;
    setStatus("loading");
    setResultMessage("Preparing analysis workspace...");

    try {
      const context = {
        latitude: selectedLocation.lat,
        longitude: selectedLocation.lng,
        locationName: selectedLocation.locationName,
        radiusKm: selectedLocation.radiusKm || 2,
      };

      const convRes = await api.createConversation(context);
      const conversationId = convRes.conversation_id;

      await api.submitQuery({
        query: query.trim(),
        conversation_id: conversationId,
        context,
      });

      setStatus("success");
      setResultMessage("Analysis complete. Redirecting...");

      if (navigateTo) {
        navigateTo("workspace", {
          conversationId,
          locationContext: context,
        });
      }
    } catch (err) {
      setStatus("error");
      setResultMessage(err.message || "Failed to start workspace.");
    }
  };

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    if (selectedFile.type.startsWith("image/")) {
      setFile(selectedFile);
      setStatus("idle");
      setResultMessage("");
    }
  };

  const handleAnalyze = async () => {
    if (!file || !query.trim()) return;

    setStatus("loading");
    setResultMessage("Starting analysis...");

    try {
      // 1. Create conversation
      const convRes = await api.createConversation();
      const conversationId = convRes.conversation_id;

      // 2. Upload image
      const uploadRes = await api.uploadImage(file, conversationId);
      const uploadedFilename = uploadRes.filename;

      // 3. Submit query
      await api.submitQuery({
        filename: uploadedFilename,
        query: query,
        conversation_id: conversationId,
      });

      setStatus("success");
      setResultMessage("Analysis complete. Redirecting...");

      // 4. Navigate to workspace
      if (navigateTo) {
        navigateTo("workspace", { conversationId });
      }
    } catch (err) {
      setStatus("error");
      setResultMessage(err.message || "Failed to analyze image");
    }
  };

  return (
    <section className="bg-[#07111F] pt-12 pb-24 px-5 relative">
      {/* Decorative background elements for the heading */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-[200px] bg-primary/5 blur-[100px] rounded-full pointer-events-none" />
      
      <div className="relative mx-auto max-w-5xl mb-12 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold uppercase tracking-wider mb-6">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          Interactive Preview
        </div>
        <h2 className="text-3xl md:text-5xl font-bold text-text-main mb-4 tracking-tight">
          Experience <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">SatQuery AI</span>
        </h2>
        <p className="text-text-muted text-lg max-w-2xl mx-auto">
          Choose a location on the map or upload your own satellite imagery to instantly extract actionable insights using our specialized multimodal models.
        </p>
      </div>

      <div id="workspace" className="relative mx-auto max-w-5xl">
        <div className="glow-border glass rounded-3xl border border-border-subtle p-2">
          <div className="rounded-[22px] border border-border-subtle bg-surface p-5 sm:p-7">
            {/* Workspace header */}
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-text-main">
                  Analyze satellite imagery
                </p>
                <p className="mt-1 text-xs text-text-muted">
                  Upload imagery and ask a question
                </p>
              </div>

              <div className="hidden items-center gap-4 sm:flex">
                <div className="flex items-center gap-2 text-[11px] text-text-muted">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  Prototype mode
                </div>
                <button
                  onClick={() => navigateTo && navigateTo("workspace")}
                  className="text-xs bg-white/5 border border-border-subtle hover:bg-white/10 transition px-3 py-1.5 rounded-lg text-primary cursor-pointer"
                >
                  Open Workspace ↗
                </button>
              </div>
            </div>

            {/* Mode Selector */}
            <div className="mb-6 flex gap-2 rounded-xl bg-black/40 p-1 w-fit mx-auto border border-border-subtle">
              <button
                onClick={() => setMode("location")}
                className={`rounded-lg px-6 py-2 text-sm font-medium transition ${
                  mode === "location"
                    ? "bg-primary/20 text-primary border border-primary/30 shadow-[0_0_15px_rgba(14,165,233,0.15)]"
                    : "text-text-muted hover:text-text-main"
                }`}
              >
                Analyze a Location
              </button>
              <button
                onClick={() => setMode("upload")}
                className={`rounded-lg px-6 py-2 text-sm font-medium transition ${
                  mode === "upload"
                    ? "bg-primary/20 text-primary border border-primary/30 shadow-[0_0_15px_rgba(14,165,233,0.15)]"
                    : "text-text-muted hover:text-text-main"
                }`}
              >
                Analyze Your Own Image
              </button>
            </div>

            {mode === "location" ? (
              <div className="flex flex-col gap-4">
                {/* Location Search Input */}
                <div className="flex gap-3">
                  <div className="flex-1">
                    {isLoaded ? (
                      <Autocomplete
                        onLoad={(ref) => (autocompleteRef.current = ref)}
                        onPlaceChanged={handlePlaceChanged}
                      >
                        <input
                          type="text"
                          value={locationSearch}
                          onChange={(e) => setLocationSearch(e.target.value)}
                          placeholder="Enter a location, address, or coordinates..."
                          className="w-full rounded-xl border border-border-subtle bg-bg-base p-3.5 text-sm text-text-main placeholder:text-text-muted outline-none focus:border-primary/50 focus:bg-primary/[0.02]"
                        />
                      </Autocomplete>
                    ) : (
                      <input
                        type="text"
                        value={locationSearch}
                        onChange={(e) => setLocationSearch(e.target.value)}
                        placeholder="Enter a location, address, or coordinates..."
                        className="w-full rounded-xl border border-border-subtle bg-bg-base p-3.5 text-sm text-text-main placeholder:text-text-muted outline-none focus:border-primary/50 focus:bg-primary/[0.02]"
                      />
                    )}
                  </div>
                  <button
                    onClick={handleSearchLocation}
                    className="rounded-xl bg-white/5 border border-border-subtle px-6 py-3.5 text-sm font-medium text-text-main transition hover:bg-white/10"
                  >
                    Search location
                  </button>
                  <button
                    onClick={handleFetchLiveLocation}
                    className="flex shrink-0 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 px-4 py-3.5 text-primary transition hover:bg-primary/20"
                    title="Use Current Location"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.242-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </button>
                </div>

                {/* Map Area */}
                <div className="relative h-[400px] w-full rounded-2xl border border-dashed border-border-subtle bg-bg-base flex items-center justify-center overflow-hidden">
                  {isLoaded ? (
                    <GoogleMap
                      mapContainerStyle={containerStyle}
                      center={mapCenter}
                      zoom={selectedLocation ? 13 : 3}
                      onClick={handleMapClick}
                      options={{
                        disableDefaultUI: false,
                        zoomControl: true,
                        streetViewControl: false,
                        mapTypeControl: true,
                        fullscreenControl: true,
                        mapTypeId: "hybrid",
                      }}
                    >
                      {selectedLocation && (
                        <>
                          <Marker position={selectedLocation} />
                          <Circle
                            center={selectedLocation}
                            radius={(selectedLocation.radiusKm || 2) * 1000}
                            options={{
                              fillColor: "#10b981",
                              fillOpacity: 0.15,
                              strokeColor: "#10b981",
                              strokeOpacity: 0.8,
                              strokeWeight: 2,
                            }}
                          />
                        </>
                      )}
                    </GoogleMap>
                  ) : (
                    <div className="text-center z-10">
                      <p className="text-sm font-medium text-text-muted">
                        Loading map...
                      </p>
                    </div>
                  )}
                  {!selectedLocation && isLoaded && (
                    <div className="absolute inset-0 pointer-events-none flex items-center justify-center bg-black/20">
                      <div className="bg-black/60 px-4 py-2 rounded-lg backdrop-blur-sm border border-border-subtle text-text-main text-sm font-medium shadow-xl">
                        Click anywhere on the map or search to select a location
                      </div>
                    </div>
                  )}
                </div>

                {/* Selected Location Details */}
                {selectedLocation && (
                  <div className="flex flex-col gap-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-emerald-400">
                          {selectedLocation.locationName || "Selected Location"}
                        </p>
                        <p className="mt-1 text-xs text-text-muted">
                          Latitude: {selectedLocation.lat.toFixed(6)} | Longitude: {selectedLocation.lng.toFixed(6)}
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 border-t border-emerald-500/20 pt-3">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-medium text-text-main">
                          Analysis Area Radius
                        </p>
                        <p className="text-xs text-emerald-400">
                          Approx.{" "}
                          {Math.round(
                            Math.PI *
                              Math.pow(selectedLocation.radiusKm || 2, 2),
                          )}{" "}
                          km²
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {[0.5, 1, 2, 5, 10].map((r) => (
                          <button
                            key={r}
                            onClick={() =>
                              setSelectedLocation((prev) => ({
                                ...prev,
                                radiusKm: r,
                              }))
                            }
                            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition border ${
                              (selectedLocation.radiusKm || 2) === r
                                ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                                : "bg-black/20 text-text-muted border-border-subtle hover:bg-white/5"
                            }`}
                          >
                            {r === 0.5 ? "500 m" : `${r} km`}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  handleFile(e.dataTransfer.files[0]);
                }}
                className="group cursor-pointer rounded-2xl border border-dashed border-border-subtle bg-bg-base p-8 text-center transition hover:border-primary/50 hover:bg-primary/[0.03] sm:p-12"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleFile(e.target.files[0])}
                />

                {file ? (
                  <div className="flex flex-col items-center">
                    <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-400/10 text-emerald-300">
                      ✓
                    </div>

                    <p className="text-sm font-medium text-text-main">
                      {file.name}
                    </p>

                    <p className="mt-1 text-xs text-text-muted">
                      Image ready for analysis
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 transition group-hover:scale-105">
                      <svg
                        className="h-7 w-7 text-primary"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M14 8h.01M5 20h14a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v14a1 1 0 001 1z"
                        />
                      </svg>
                    </div>

                    <p className="text-sm font-medium text-text-main">
                      Drop satellite imagery here
                    </p>

                    <p className="mt-2 text-xs text-text-muted">
                      or click to browse from your device
                    </p>

                    <div className="mt-5 flex justify-center gap-2">
                      {["OPTICAL", "SAR", "MULTISPECTRAL"].map((type) => (
                        <span
                          key={type}
                          className="rounded-md border border-border-subtle bg-white/[0.03] px-2 py-1 text-[9px] tracking-wider text-text-muted"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Action / Query Area */}
            {mode === "upload" ? (
              <div className="mt-4 rounded-2xl border border-border-subtle bg-bg-base p-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary/10 text-blue-300">
                    ✦
                  </div>
                  <div className="flex-1">
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      rows={2}
                      placeholder="Ask anything about your satellite imagery..."
                      className="w-full resize-none bg-transparent text-sm leading-6 text-text-main outline-none placeholder:text-text-muted"
                    />
                    <div className="mt-3 flex flex-col gap-3 border-t border-border-subtle pt-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-[11px] text-text-muted">
                        Try: “What changed in this image?”
                      </p>
                      <button
                        onClick={handleAnalyze}
                        disabled={
                          !file || !query.trim() || status === "loading"
                        }
                        className="rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-slate-950 transition hover:bg-primary disabled:cursor-not-allowed disabled:opacity-30 flex items-center gap-2"
                      >
                        {status === "loading" ? "Analyzing..." : "Analyze →"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 rounded-2xl border border-border-subtle bg-bg-base p-4">
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary/10 text-blue-300">
                    ✦
                  </div>
                  <div className="flex-1">
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      rows={2}
                      placeholder="Ask about this location..."
                      className="w-full resize-none bg-transparent text-sm leading-6 text-text-main outline-none placeholder:text-text-muted"
                    />
                    <div className="mt-3 flex flex-col gap-3 border-t border-border-subtle pt-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-[11px] text-text-muted">
                        Try: “Is area mein pichle 10 saal mein kitna
                        development hua?”
                      </p>
                      <button
                        onClick={handleAnalyzeLocation}
                        disabled={
                          !selectedLocation ||
                          !query.trim() ||
                          status === "loading"
                        }
                        className="rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-slate-950 transition hover:bg-primary disabled:cursor-not-allowed disabled:opacity-30 flex items-center gap-2"
                      >
                        {status === "loading"
                          ? "Analyzing..."
                          : "Analyze This Location →"}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {/* Status messages */}
            {status === "success" && (
              <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm whitespace-pre-wrap">
                {resultMessage}
              </div>
            )}
            {status === "error" && (
              <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                {resultMessage}
              </div>
            )}
          </div>
        </div>

        {/* Trust line */}
        <div className="mt-6 flex flex-wrap justify-center gap-x-7 gap-y-2 text-[11px] text-text-muted">
          <span>Natural language queries</span>
          <span>•</span>
          <span>Visual evidence</span>
          <span>•</span>
          <span>Model-aware analysis</span>
        </div>
      </div>
    </section>
  );
}
