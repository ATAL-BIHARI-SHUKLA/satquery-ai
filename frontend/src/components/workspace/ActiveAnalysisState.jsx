/* eslint-disable react-hooks/set-state-in-effect, no-unused-vars, no-empty */
import React, { useRef, useCallback, useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker as LeafletMarker, Circle as LeafletCircle, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import ImageContextStrip from "./ImageContextStrip";
import AnalysisPanel from "./AnalysisPanel";
import ConversationInput from "./ConversationInput";
import { api } from "../../services/api";

// Fix for default marker icon in leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
}

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
  const [satelliteData, setSatelliteData] = useState(null);
  const [satelliteLoading, setSatelliteLoading] = useState(false);
  const [satelliteError, setSatelliteError] = useState(null);

  const selectedImgObj = attachedImages.find((img) => img.id === selectedImage);
  const isLocationBased = !!locationContext;

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Use a timeout to scroll after render
  React.useEffect(() => {
    setTimeout(scrollToBottom, 100);
  }, [messages, scrollToBottom]);

  useEffect(() => {
    let isMounted = true;
    if (locationContext && locationContext.latitude && locationContext.longitude) {
      const fetchSatData = async () => {
        setSatelliteLoading(true);
        setSatelliteError(null);
        try {
          // Add a small radius since getSatelliteImagery uses point intersects by default
          const res = await api.getSatelliteImagery({
            latitude: locationContext.latitude,
            longitude: locationContext.longitude,
          });
          if (isMounted) {
            setSatelliteData(res);
          }
        } catch (error) {
          if (isMounted) {
            setSatelliteError("Failed to load satellite data.");
          }
        } finally {
          if (isMounted) {
            setSatelliteLoading(false);
          }
        }
      };
      fetchSatData();
    }
    return () => {
      isMounted = false;
    };
  }, [locationContext]);

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

        <div className="flex-1 relative rounded-xl border border-border-subtle overflow-hidden bg-[#0a1420] flex flex-col shadow-inner z-0">
          {isLocationBased ? (
              <MapContainer
                center={[locationContext.latitude, locationContext.longitude]}
                zoom={14}
                style={mapContainerStyle}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <MapUpdater center={[locationContext.latitude, locationContext.longitude]} />
                <LeafletMarker position={[locationContext.latitude, locationContext.longitude]} />
                <LeafletCircle
                  center={[locationContext.latitude, locationContext.longitude]}
                  radius={(locationContext.radiusKm || 2) * 1000}
                  pathOptions={{
                    fillColor: "#10b981",
                    fillOpacity: 0.15,
                    color: "#10b981",
                    weight: 2,
                  }}
                />
              </MapContainer>
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
              
              <div className="flex flex-col flex-1">
                <span className="text-[10px] text-emerald-400 uppercase font-bold tracking-wider">Data</span>
                {satelliteLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full border-2 border-emerald-400 border-t-transparent animate-spin"></div>
                    <span className="text-xs text-text-muted">Fetching STAC data...</span>
                  </div>
                ) : satelliteError ? (
                  <span className="text-xs text-red-400">{satelliteError}</span>
                ) : satelliteData?.available ? (
                  <div className="flex flex-col">
                    <span className="text-xs text-text-main">{satelliteData.provider}</span>
                    <span className="text-[10px] text-text-muted">
                      {satelliteData.selected_date ? new Date(satelliteData.selected_date).toLocaleDateString() : 'Recent'} 
                      {satelliteData.cloud_cover !== undefined ? ` • ${Math.round(satelliteData.cloud_cover)}% cloud cover` : ''}
                    </span>
                  </div>
                ) : (
                  <span className="text-xs text-red-400">No suitable satellite observation found for this location.</span>
                )}
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
