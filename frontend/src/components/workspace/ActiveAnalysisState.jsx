import React, { useRef, useCallback } from "react";
import { GoogleMap, Marker, Circle, useJsApiLoader } from "@react-google-maps/api";
import ImageContextStrip from "./ImageContextStrip";
import AnalysisPanel from "./AnalysisPanel";
import ConversationInput from "./ConversationInput";

const mapContainerStyle = {
  width: "100%",
  height: "100%",
  borderRadius: "0.75rem",
};

export default function ActiveAnalysisState({
  messages,
  attachedImages,
  selectedImage,
  setSelectedImage,
  currentQuery,
  setCurrentQuery,
  onSubmit,
  loading,
  onFileUpload,
  uploading,
  locationContext,
}) {
  const messagesEndRef = useRef(null);
  
  const { isLoaded } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: ["places"],
  });

  const selectedImgObj = attachedImages.find((img) => img.id === selectedImage);
  const isLocationBased = !!locationContext;

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Use a timeout to scroll after render
  React.useEffect(() => {
    setTimeout(scrollToBottom, 100);
  }, [messages, scrollToBottom]);

  return (
    <div className="flex flex-col lg:flex-row h-full overflow-hidden bg-bg-base">
      {/* Left Panel: Imagery / Map (Sticky) */}
      <div className="w-full lg:w-1/2 xl:w-7/12 h-[50vh] lg:h-full border-b lg:border-b-0 lg:border-r border-border-subtle flex flex-col bg-surface p-4">
        
        {attachedImages.length > 0 && !isLocationBased && (
          <div className="mb-4 shrink-0">
            <ImageContextStrip
              images={attachedImages}
              selectedImage={selectedImage}
              onSelectImage={setSelectedImage}
            />
          </div>
        )}

        <div className="flex-1 relative rounded-xl border border-border-subtle overflow-hidden bg-[#0a1420] flex flex-col shadow-inner">
          {isLocationBased ? (
            isLoaded ? (
              <GoogleMap
                mapContainerStyle={mapContainerStyle}
                center={{ lat: locationContext.latitude, lng: locationContext.longitude }}
                zoom={14}
                options={{
                  disableDefaultUI: false,
                  zoomControl: true,
                  streetViewControl: false,
                  mapTypeControl: true,
                  mapTypeId: "hybrid",
                }}
              >
                <Marker position={{ lat: locationContext.latitude, lng: locationContext.longitude }} />
                <Circle
                  center={{ lat: locationContext.latitude, lng: locationContext.longitude }}
                  radius={(locationContext.radiusKm || 2) * 1000}
                  options={{
                    fillColor: "#10b981",
                    fillOpacity: 0.15,
                    strokeColor: "#10b981",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                  }}
                />
              </GoogleMap>
            ) : (
              <div className="flex items-center justify-center h-full text-text-muted">Loading map...</div>
            )
          ) : selectedImgObj ? (
            <div className="relative w-full h-full flex items-center justify-center bg-black/40">
              <img
                src={selectedImgObj.url}
                alt={selectedImgObj.filename}
                className="max-w-full max-h-full object-contain"
              />
              {/* Fake Metadata Overlay for Premium feel */}
              <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md border border-white/10 rounded-lg p-3 flex flex-col gap-1 shadow-xl">
                <div className="text-[10px] uppercase tracking-wider text-primary font-semibold">Image Metadata</div>
                <div className="text-xs text-text-main">File: <span className="text-sky-300">{selectedImgObj.filename}</span></div>
                <div className="text-xs text-text-main">Type: <span className="text-text-muted">Optical / Multispectral</span></div>
                <div className="text-xs text-text-main">Resolution: <span className="text-text-muted">~10m/px</span></div>
                <div className="text-xs text-text-main">Date: <span className="text-text-muted">{new Date().toISOString().split('T')[0]}</span></div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-text-muted text-sm flex-col gap-2">
              <svg className="w-8 h-8 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              No imagery selected
            </div>
          )}
        </div>
      </div>

      {/* Right Panel: Conversation Feed (Scrollable) */}
      <div className="flex flex-col w-full lg:w-1/2 xl:w-5/12 h-[50vh] lg:h-full relative">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 pb-40">
          <AnalysisPanel messages={messages} />
          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* Input anchored to bottom of right panel */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-bg-base via-bg-base/90 to-transparent pt-12">
          
          {isLocationBased && (
            <div className="mb-3 bg-surface/90 backdrop-blur-md border border-border-subtle rounded-xl p-3 flex flex-wrap items-center gap-4 shadow-lg shadow-black/20">
              <div className="flex flex-col">
                <span className="text-[10px] text-primary uppercase font-bold tracking-wider">Location</span>
                <span className="text-xs text-text-main font-medium truncate max-w-[150px]">{locationContext.locationName || "Selected Area"}</span>
              </div>
              <div className="w-px h-6 bg-border-subtle"></div>
              <div className="flex flex-col">
                <span className="text-[10px] text-sky-400 uppercase font-bold tracking-wider">Coordinates</span>
                <span className="text-xs text-text-muted font-mono">{locationContext.latitude?.toFixed(4)}, {locationContext.longitude?.toFixed(4)}</span>
              </div>
              <div className="w-px h-6 bg-border-subtle"></div>
              <div className="flex flex-col">
                <span className="text-[10px] text-emerald-400 uppercase font-bold tracking-wider">Data</span>
                <span className="text-xs text-text-muted">Sentinel-2 (Available)</span>
              </div>
            </div>
          )}

          {!isLocationBased && attachedImages.length > 0 && (
             <div className="mb-3">
               <span className="text-xs font-medium text-text-muted">Ask about this imagery</span>
             </div>
          )}

          <ConversationInput
            currentQuery={currentQuery}
            setCurrentQuery={setCurrentQuery}
            onSubmit={onSubmit}
            loading={loading}
            onFileUpload={onFileUpload}
            uploading={uploading}
            isLarge={false}
          />
        </div>
      </div>
    </div>
  );
}
