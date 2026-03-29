import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

const Card: React.FC<CardProps> = ({ children, title, description }) => (
  <div className="bg-white rounded-xl shadow-lg shadow-slate-200/50 border border-slate-100 p-8 max-w-2xl w-full mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
    {title && <h2 className="text-2xl font-bold text-slate-800 mb-2">{title}</h2>}
    {description && <p className="text-slate-500 mb-8">{description}</p>}
    {children}
  </div>
);

export default Card;
