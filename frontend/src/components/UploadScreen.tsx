import React, { useState } from "react";
import { Upload } from "lucide-react";
import { validateExcel, type ValidationResponse } from "../services/api";

interface UploadScreenProps {
  onUpload: (result: ValidationResponse) => void;
}

const UploadScreen: React.FC<UploadScreenProps> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const selected = e.target.files[0];
      if (selected.name.toLowerCase().endsWith(".xlsx")) {
        setFile(selected);
        setError(null);
      } else {
        setError("Please upload a .xlsx spreadsheet.");
      }
    }
  };

  const handleSubmit = async () => {
    if (!file) return;
    setIsLoading(true);
    try {
      const result = await validateExcel(file);
      onUpload(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-grow justify-center py-4">
      <div className="mb-8">
        <h2 className="text-5xl font-black tracking-tighter mb-2 leading-none">Upload File</h2>
        <p className="text-gray-400 font-bold text-xs uppercase tracking-widest">A Simple xlsx to ppt file generator</p>
      </div>

      <div className="space-y-6">
        <label className="block border border-gray-100 rounded-2xl p-12 cursor-pointer hover:border-black transition-all group relative bg-gray-50/30">
          <input 
            type="file" 
            accept=".xlsx" 
            className="hidden" 
            onChange={handleFileChange}
            disabled={isLoading}
          />
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:bg-black group-hover:text-white transition-all">
              <Upload className="w-5 h-5" />
            </div>
            <div className="max-w-[200px] md:max-w-none">
              <p className="font-black text-sm tracking-tight truncate">{file ? file.name : "Select Spreadsheet"}</p>
              <p className="text-[9px] font-black text-gray-300 mt-1 uppercase tracking-widest">PowerPoint Generator</p>
            </div>
          </div>
        </label>

        {error && <p className="text-xs font-black text-red-500 text-center">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={!file || isLoading}
          className="w-full bg-black text-white font-black py-4 rounded-xl text-xs hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-20 disabled:pointer-events-none uppercase tracking-[0.2em]"
        >
          {isLoading ? "Processing..." : "Analyze File"}
        </button>
      </div>
    </div>
  );
};

export default UploadScreen;
