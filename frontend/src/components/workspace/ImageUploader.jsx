import { useState, useRef } from 'react';
import { api } from '../../services/api';

export default function ImageUploader() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [errorMessage, setErrorMessage] = useState('');
  const [responseData, setResponseData] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Validate type (JPG, JPEG, PNG, WEBP)
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(selectedFile.type)) {
      setErrorMessage('Invalid file type. Only JPG, PNG, and WEBP are supported.');
      setStatus('error');
      setFile(null);
      setPreview(null);
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setStatus('idle');
    setErrorMessage('');
    setResponseData(null);
  };

  const handleUpload = async () => {
    if (!file) return;

    setStatus('uploading');
    setErrorMessage('');

    try {
      const data = await api.uploadImage(file);
      setResponseData(data);
      setStatus('success');
    } catch (err) {
      setStatus('error');
      setErrorMessage(err.message || 'Upload failed. Please try again.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto my-12 p-8 rounded-3xl border border-border-subtle bg-surface text-text-main sat-grid relative">
      <h2 className="text-2xl font-semibold mb-6">Test Image Uploader</h2>
      
      <div className="space-y-6 relative z-10">
        {/* Upload Area */}
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="cursor-pointer border border-dashed border-border-subtle bg-bg-base hover:border-primary/50 hover:bg-primary/[0.03] transition-colors rounded-2xl p-10 text-center"
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/jpeg, image/png, image/webp"
            className="hidden" 
          />
          {preview ? (
            <div className="flex flex-col items-center">
              <img src={preview} alt="Preview" className="h-48 object-contain mb-4 rounded-lg border border-border-subtle" />
              <p className="text-sm font-medium text-text-main">{file.name}</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10 text-primary">
                <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <p className="text-sm font-medium text-text-main mb-1">Click to select an image</p>
              <p className="text-xs text-text-muted">Supports JPG, PNG, WEBP</p>
            </div>
          )}
        </div>

        {/* Status Messages */}
        {status === 'error' && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {errorMessage}
          </div>
        )}

        {status === 'success' && responseData && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
            ✓ Upload successful! Image saved as: {responseData.filename}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end pt-2">
          <button 
            onClick={handleUpload}
            disabled={!file || status === 'uploading'}
            className="rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-slate-950 transition hover:bg-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {status === 'uploading' ? (
              <>
                <div className="h-4 w-4 rounded-full border-2 border-slate-950/20 border-t-slate-950 animate-spin" />
                Uploading...
              </>
            ) : (
              'Upload Image'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
