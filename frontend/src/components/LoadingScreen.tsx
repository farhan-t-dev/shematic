import React, { useEffect, useState } from "react";

interface LoadingScreenProps {
  onComplete: () => void;
  message?: string;
  duration?: number;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  onComplete, 
  message = "Processing...", 
  duration = 1500 
}) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - start;
      const nextProgress = Math.min((elapsed / duration) * 100, 100);
      setProgress(nextProgress);
      
      if (nextProgress >= 100) {
        clearInterval(interval);
        setTimeout(onComplete, 300);
      }
    }, 16);

    return () => clearInterval(interval);
  }, [onComplete, duration]);

  return (
    <div className="flex flex-col flex-grow justify-center py-10 md:py-20 animate-in fade-in duration-500">
      <div className="mb-10">
        <h2 className="text-5xl md:text-6xl font-black tracking-tighter mb-4 leading-none">{message}</h2>
        <p className="text-gray-400 font-black text-[10px] md:text-xs uppercase tracking-[0.2em]">Assembling Output</p>
      </div>
      
      <div className="w-full h-1 md:h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className="h-full bg-black transition-all duration-300 ease-out" 
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default LoadingScreen;
