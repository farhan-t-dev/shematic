import React, { useState, useEffect } from "react";
import { type ValidationResponse, logout } from "./services/api";
import LoginScreen from "./components/LoginScreen";
import UploadScreen from "./components/UploadScreen";
import ValidationScreen from "./components/ValidationScreen";
import SuccessScreen from "./components/SuccessScreen";
import LoadingScreen from "./components/LoadingScreen";
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type AppStep = "login" | "upload" | "loading" | "validate" | "success";

const App: React.FC = () => {
  const [step, setStep] = useState<AppStep>(
    localStorage.getItem("auth-token") ? "upload" : "login"
  );
  const [nextStep, setNextStep] = useState<AppStep | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [generatedName, setGeneratedName] = useState("");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (downloadUrl) window.URL.revokeObjectURL(downloadUrl);
    };
  }, [downloadUrl]);

  const handleLogin = () => setStep("upload");

  const startLoading = (targetStep: AppStep, message: string) => {
    setNextStep(targetStep);
    setLoadingMessage(message);
    setStep("loading");
  };

  const handleUpload = (result: ValidationResponse) => {
    setValidation(result);
    startLoading("validate", "Analyzing...");
  };

  const handleGenerate = (downloadName: string, blob: Blob) => {
    const url = window.URL.createObjectURL(blob);
    setDownloadUrl(url);
    setGeneratedName(downloadName);
    startLoading("success", "Finalizing...");
  };

  const handleReset = () => {
    if (downloadUrl) window.URL.revokeObjectURL(downloadUrl);
    setDownloadUrl(null);
    setValidation(null);
    setGeneratedName("");
    setStep("upload");
  };

  const handleLogout = async () => {
    try { await logout(); } catch (e) {}
    localStorage.removeItem("auth-token");
    handleReset();
    setStep("login");
  };

  return (
    <div className="h-screen bg-white text-black font-sans antialiased selection:bg-black selection:text-white overflow-hidden">
      <div className="max-w-screen-sm mx-auto px-6 h-full flex flex-col py-8">
        
        <header className="flex items-center justify-between mb-8 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-black rounded-sm flex items-center justify-center shrink-0">
              <div className="w-3 h-0.5 bg-white rotate-45 absolute" />
              <div className="w-3 h-0.5 bg-white -rotate-45 absolute" />
            </div>
            <span className="font-black tracking-tighter text-lg uppercase">Schematic.</span>
          </div>
          
          {step !== "login" && (
            <button 
              onClick={handleLogout}
              className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-300 hover:text-black transition-colors"
            >
              Sign out
            </button>
          )}
        </header>

        <main className="flex-grow flex flex-col justify-center overflow-hidden">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            {step === "login" && <LoginScreen onLogin={handleLogin} />}
            {step === "upload" && <UploadScreen onUpload={handleUpload} />}
            {step === "loading" && (
              <LoadingScreen 
                message={loadingMessage} 
                onComplete={() => nextStep && setStep(nextStep)} 
              />
            )}
            {step === "validate" && validation && (
              <ValidationScreen
                report={validation}
                onCancel={handleReset}
                onConfirm={handleGenerate}
              />
            )}
            {step === "success" && (
              <SuccessScreen 
                downloadName={generatedName} 
                downloadUrl={downloadUrl}
                onReset={handleReset} 
              />
            )}
          </div>
        </main>

        <footer className="mt-8 pt-6 border-t border-gray-100 flex justify-between items-center text-[9px] uppercase tracking-[0.3em] text-gray-200 font-black shrink-0">
          <span>v2.0</span>
          <span>&copy; RPS Insurance</span>
        </footer>
      </div>
    </div>
  );
};

export default App;
