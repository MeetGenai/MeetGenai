import React, { useState } from 'react';
import { User, ArrowRight, X } from 'lucide-react';

interface NameEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (name: string) => void;
}

export const NameEntryModal: React.FC<NameEntryModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please enter your full name');
      return;
    }
    if (name.trim().length < 2) {
      setError('Name must be at least 2 characters long');
      return;
    }
    onSubmit(name.trim());
  };

  const handleInputChange = (value: string) => {
    setName(value);
    if (error) setError('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4 animate-fadeIn">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4 relative overflow-hidden animate-slideUp">
        {/* Background Animation */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-indigo-50/50 rounded-3xl"></div>
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200 hover:rotate-90 transform"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="relative z-10 space-y-8">
          {/* Icon */}
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce">
              <User className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-2">Welcome to MeetGenAI</h2>
            <p className="text-gray-600">Let's get started by knowing your name</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="relative">
              <label 
                htmlFor="fullName" 
                className={`absolute left-4 transition-all duration-300 pointer-events-none ${
                  isFocused || name 
                    ? 'top-2 text-xs text-blue-600 font-medium' 
                    : 'top-4 text-gray-500'
                }`}
              >
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={name}
                onChange={(e) => handleInputChange(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                className={`w-full px-4 pt-6 pb-2 bg-white/70 border-2 rounded-xl transition-all duration-300 ${
                  isFocused 
                    ? 'border-blue-500 shadow-lg scale-[1.02]' 
                    : error 
                      ? 'border-red-300' 
                      : 'border-gray-200 hover:border-gray-300'
                }`}
                placeholder=""
              />
              {isFocused && (
                <div className="absolute inset-0 bg-blue-500/5 rounded-xl pointer-events-none animate-pulse"></div>
              )}
            </div>
            
            {error && (
              <p className="text-red-500 text-sm animate-shake">{error}</p>
            )}

            <button
              type="submit"
              className="group w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 hover:scale-[1.02] hover:shadow-xl flex items-center justify-center space-x-2"
            >
              <span>Continue</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};