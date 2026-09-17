import { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import ConversationSidebar from "../components/workspace/ConversationSidebar";
import EmptyAnalysisState from "../components/workspace/EmptyAnalysisState";
import ActiveAnalysisState from "../components/workspace/ActiveAnalysisState";


export default function AnalysisWorkspace({
  navigateTo,
  initialConversationId,
  initialLocationContext,
}) {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(
    initialConversationId || null,
  );
  const [attachedImages, setAttachedImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentQuery, setCurrentQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [activeLocationContext, setActiveLocationContext] = useState(initialLocationContext || null);
  
  const hasContent = messages.length > 0 || attachedImages.length > 0 || activeLocationContext;

  useEffect(() => {
    loadAllConversations();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      loadConversation(selectedConversation);
    }
  }, [selectedConversation]);

  const loadAllConversations = async () => {
    try {
      const data = await api.getConversations();
      setConversations(
        data.map((c) => ({
          id: c.id,
          title: c.title,
          date: new Date(c.updated_at).toLocaleDateString(),
        }))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const loadConversation = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getConversation(id);

      const formattedMessages = data.messages.map((m) => {
        let textContent = m.text;
        let parsedData = null;
        try {
          parsedData = JSON.parse(m.text);
          if (parsedData.answer) {
            textContent = parsedData.answer;
          } else if (parsedData.reason) {
            textContent = parsedData.reason;
          } else {
            textContent = JSON.stringify(parsedData, null, 2);
          }
        } catch {}

        return {
          id: m.message_id,
          role: m.role,
          text: textContent,
          raw: parsedData,
        };
      });
      setMessages(formattedMessages);

      const formattedImages = data.images.map((img) => ({
        id: img.image_id,
        url: `https://via.placeholder.com/150?text=${encodeURIComponent(img.original_filename)}`,
        filename: img.original_filename || img.filename,
      }));
      setAttachedImages(formattedImages);
      if (formattedImages.length > 0) {
        setSelectedImage(formattedImages[formattedImages.length - 1].id);
      }

      // No need to update conversations locally here if we call loadAllConversations, but we can to be safe
      setConversations((prev) => {
        if (!prev.find((c) => c.id === id)) {
          return [
            { id: id, title: `Conv ${id.substring(0, 6)}`, date: new Date().toLocaleDateString() },
            ...prev
          ];
        }
        return prev;
      });
    } catch {
      setError("Failed to load conversation");
    } finally {
      setLoading(false);
    }
  };

  const handleQuerySubmit = async () => {
    if (!currentQuery.trim()) return;

    setLoading(true);
    setError(null);
    try {
      let convId = selectedConversation;
      if (!convId) {
        const newConv = await api.createConversation();
        convId = newConv.conversation_id;
        setSelectedConversation(convId);
      }

      const selectedImgObj =
        attachedImages.find((img) => img.id === selectedImage) ||
        attachedImages[attachedImages.length - 1];
      const filename = selectedImgObj ? selectedImgObj.filename : "unknown";

      const context = activeLocationContext;
      await api.submitQuery({
        filename: filename,
        query: currentQuery,
        conversation_id: convId,
        context: context
      });

      setCurrentQuery("");
      await loadConversation(convId);
      await loadAllConversations();
    } catch (err) {
      setError(err.message || "Failed to submit query");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setUploading(true);
    setError(null);
    try {
      let convId = selectedConversation;
      if (!convId) {
        const newConv = await api.createConversation();
        convId = newConv.conversation_id;
        setSelectedConversation(convId);
      }

      await api.uploadImage(file, convId);
      await loadConversation(convId);
      await loadAllConversations();
    } catch (err) {
      setError(err.message || "Failed to upload image");
    } finally {
      setUploading(false);
    }
  };

  const handleSubmitLocation = async (context) => {
    setLoading(true);
    setError(null);
    try {
      // Only create a conversation if we don't have one
      let convId = selectedConversation;
      if (!convId) {
        const newConv = await api.createConversation(context);
        convId = newConv.conversation_id;
        setSelectedConversation(convId);
      }
      setActiveLocationContext(context);
      await loadAllConversations();
    } catch (err) {
      setError(err.message || "Failed to initialize location analysis");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-full bg-bg-base text-text-main overflow-hidden">
      {/* Sidebar Overlay for Mobile */}
      {isMobileSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
          onClick={() => setIsMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 ${isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"} border-r border-border-subtle bg-bg-base flex flex-col shadow-2xl md:shadow-none`}>
        <ConversationSidebar
          conversations={conversations}
          selectedConversation={selectedConversation}
          onSelectConversation={(id) => {
            setSelectedConversation(id);
            setIsMobileSidebarOpen(false);
          }}
          onNewConversation={() => {
            setSelectedConversation(null);
            setMessages([]);
            setAttachedImages([]);
            setIsMobileSidebarOpen(false);
          }}
          navigateTo={navigateTo}
        />
      </div>

      {/* Main Workspace */}
      <div className="flex flex-col flex-1 h-full relative overflow-hidden">


        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative">
          {error && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm shadow-xl backdrop-blur-md">
              {error}
            </div>
          )}

          {hasContent ? (
            <ActiveAnalysisState
              messages={messages}
              attachedImages={attachedImages}
              selectedImage={selectedImage}
              setSelectedImage={setSelectedImage}
              currentQuery={currentQuery}
              setCurrentQuery={setCurrentQuery}
              onSubmit={handleQuerySubmit}
              loading={loading}
              onFileUpload={handleFileUpload}
              uploading={uploading}
              locationContext={activeLocationContext}
            />
          ) : (
            <div className="h-full overflow-y-auto">
              <EmptyAnalysisState
                currentQuery={currentQuery}
                setCurrentQuery={setCurrentQuery}
                onSubmit={handleQuerySubmit}
                loading={loading}
                onFileUpload={handleFileUpload}
                uploading={uploading}
                onSubmitLocation={handleSubmitLocation}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
