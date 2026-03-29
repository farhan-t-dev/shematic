import React, { useState } from "react";
import { generatePptx, type ValidationResponse } from "../services/api";
import { cn } from "../lib/utils";

interface ValidationScreenProps {
  report: ValidationResponse;
  onCancel: () => void;
  onConfirm: (downloadName: string, blob: Blob) => void;
}

const ValidationScreen: React.FC<ValidationScreenProps> = ({ report, onCancel, onConfirm }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [accountNameOverride, setAccountNameOverride] = useState("");
  const [warningAnswers, setWarningAnswers] = useState<Record<string, string>>({});

  const blockingFlags = report.flags.filter((f) => f.level === "BLOCKING");
  const isBlocked = report.status === "blocked" || blockingFlags.length > 0;

  const handleGenerate = async () => {
    if (isBlocked || isGenerating) return;
    setIsGenerating(true);
    try {
      const downloadName = `${report.file_name.split(".")[0]}-schematic.pptx`;
      const blob = await generatePptx({
        uploadId: report.upload_id!,
        accountNameOverride,
        warningAnswers,
      });
      onConfirm(downloadName, blob);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col flex-grow py-4">
      <div className="mb-6 shrink-0">
        <h2 className="text-5xl font-black tracking-tighter mb-1 leading-none">Review.</h2>
        <p className="text-gray-400 font-bold text-[10px] uppercase tracking-widest truncate max-w-sm">Findings for {report.file_name}</p>
      </div>

      <div className="flex-grow overflow-y-auto max-h-[40vh] space-y-4 pr-2 mb-6 scrollbar-thin scrollbar-thumb-gray-200">
        {report.flags.map((flag) => (
          <div key={flag.key} className="border-l border-gray-100 pl-4 py-0.5 space-y-2">
            <div className="flex items-center gap-2">
              <span className={cn(
                "text-[8px] font-black px-1.5 py-0.5 rounded-sm uppercase tracking-widest shrink-0",
                flag.level === "BLOCKING" ? "bg-red-600 text-white" : "bg-gray-100 text-gray-400"
              )}>
                {flag.id}
              </span>
              <p className="font-bold text-xs tracking-tight text-gray-800 leading-tight">{flag.message}</p>
            </div>
            
            {flag.level === "WARNING" && flag.id === "W03" && (
              <div className="space-y-1">
                <input
                  type="text"
                  placeholder="Enter schematic title"
                  className="w-full bg-gray-50 border-gray-100 rounded-lg px-3 py-2 text-xs focus:bg-white focus:border-black focus:ring-0 transition-all font-bold"
                  value={accountNameOverride}
                  onChange={(e) => setAccountNameOverride(e.target.value)}
                />
              </div>
            )}

            {flag.level === "WARNING" && flag.metadata?.input_type === "boolean" && (
              <div className="flex gap-2">
                {["Yes", "No"].map(c => (
                  <button 
                    key={c}
                    onClick={() => setWarningAnswers(p => ({...p, [flag.key]: c.toLowerCase()}))}
                    className={cn(
                      "text-[9px] font-black px-4 py-1.5 rounded-lg border transition-all uppercase tracking-widest",
                      warningAnswers[flag.key] === c.toLowerCase() ? "bg-black border-black text-white" : "bg-white border-gray-100 text-gray-300 hover:text-black hover:border-black"
                    )}
                  >
                    {c}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="shrink-0 space-y-4">
        <button
          onClick={handleGenerate}
          disabled={isBlocked || isGenerating}
          className="w-full bg-black text-white font-black py-4 rounded-xl text-xs hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-10 uppercase tracking-[0.2em]"
        >
          {isGenerating ? "Processing..." : "Generate Document"}
        </button>
        
        <button 
          onClick={onCancel}
          className="w-full text-[9px] font-black text-gray-300 hover:text-black uppercase tracking-[0.3em] transition-all text-center"
        >
          Go Back
        </button>
      </div>
    </div>
  );
};

export default ValidationScreen;
