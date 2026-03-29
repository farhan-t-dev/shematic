import React from "react";
import { Download, FileText } from "lucide-react";

interface SuccessScreenProps {
  downloadName: string;
  downloadUrl: string | null;
  onReset: () => void;
}

const SuccessScreen: React.FC<SuccessScreenProps> = ({ downloadName, downloadUrl, onReset }) => {
  const handleDownload = () => {
    if (!downloadUrl) return;
    const anchor = document.createElement("a");
    anchor.href = downloadUrl;
    anchor.download = downloadName;
    anchor.click();
  };

  return (
    <div className="flex flex-col flex-grow justify-center py-4 text-center">
      <div className="mb-8">
        <h2 className="text-5xl font-black tracking-tighter mb-2 leading-none">Your file is ready.</h2>
        <p className="text-gray-400 font-bold text-xs uppercase tracking-widest">PowerPoint Export Complete</p>
      </div>

      <div className="bg-gray-50 border border-gray-100 rounded-2xl p-8 mb-8 flex flex-col items-center gap-4">
        <div className="w-12 h-12 bg-black text-white rounded-lg flex items-center justify-center">
          <FileText className="w-6 h-6" />
        </div>
        <div className="max-w-xs">
          <p className="text-xs font-black uppercase tracking-[0.2em] text-gray-300 mb-1">Generated Output</p>
          <p className="font-bold text-sm tracking-tight truncate">{downloadName}</p>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <button
          onClick={handleDownload}
          className="w-full bg-black text-white font-black py-4 rounded-xl text-xs hover:opacity-90 active:scale-[0.98] transition-all flex items-center justify-center gap-2 uppercase tracking-[0.2em]"
        >
          <Download className="w-4 h-4" />
          <span>Download Document</span>
        </button>
        
        <button
          onClick={onReset}
          className="text-[9px] font-black text-gray-300 hover:text-black uppercase tracking-[0.3em] transition-all"
        >
          Upload New File
        </button>
      </div>
    </div>
  );
};

export default SuccessScreen;
