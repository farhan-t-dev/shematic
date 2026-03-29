import React, { useState } from "react";
import { login } from "../services/api";

interface LoginScreenProps {
  onLogin: () => void;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await login(username, password);
      localStorage.setItem("auth-token", data.token);
      onLogin();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Access denied");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-grow justify-center">
      <div className="mb-10 md:mb-14">
        <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4 leading-none">Secure Access.</h2>
        <p className="text-gray-400 font-bold text-sm">Internal tools for schematic generation.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-300">Username</label>
          <input
            type="text"
            required
            className="w-full bg-gray-50 border-gray-100 rounded-xl px-4 py-3.5 md:py-4 text-sm focus:bg-white focus:border-black focus:ring-0 transition-all font-bold"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <label className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-300">Password</label>
          <input
            type="password"
            required
            className="w-full bg-gray-50 border-gray-100 rounded-xl px-4 py-3.5 md:py-4 text-sm focus:bg-white focus:border-black focus:ring-0 transition-all font-bold"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        
        {error && <p className="text-xs font-black text-red-500">{error}</p>}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-black text-white font-black py-4 md:py-5 rounded-xl text-sm hover:opacity-90 active:scale-[0.98] transition-all disabled:opacity-50 mt-4 uppercase tracking-[0.1em]"
        >
          {isLoading ? "Authenticating..." : "Sign in"}
        </button>
      </form>
    </div>
  );
};

export default LoginScreen;
