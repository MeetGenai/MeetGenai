import React, { useEffect, useState } from 'react';
import { Check, Loader2, Video, X } from 'lucide-react';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  meetingTitle: string;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ 
  isOpen, 
  onClose, 
  meetingTitle 
}) => {
  const [status, setStatus] = useState<'joining' | 'success'>('joining');

  useEffect(() => {
    if (isOpen) {
      setStatus('joining');
      const timer = setTimeout(() => {
        setStatus('success');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4 relative overflow-hidden">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Background Animation */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-indigo-50/50 rounded-3xl"></div>
        
        <div className="relative z-10 text-center space-y-6">
          {/* Icon */}
          <div className="relative mx-auto w-20 h-20">
            {status === 'joining' ? (
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <Loader2 className="w-10 h-10 text-white animate-spin" />
              </div>
            ) : (
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center animate-bounce">
                <Check className="w-10 h-10 text-white" />
              </div>
            )}
            
            {/* Pulse Animation */}
            <div className={`absolute inset-0 rounded-full ${
              status === 'joining' 
                ? 'bg-blue-500/30 animate-ping' 
                : 'bg-green-500/30 animate-ping'
            }`}></div>
          </div>

          {/* Status Message */}
          <div className="space-y-3">
            <h3 className="text-2xl font-bold text-gray-800">
              {status === 'joining' ? 'Joining Meeting...' : 'Successfully Joined!'}
            </h3>
            
            <p className="text-gray-600 leading-relaxed">
              {status === 'joining' 
                ? `Connecting to "${meetingTitle}". Please wait while we set up the AI assistant.`
                : `Your AI assistant has successfully joined "${meetingTitle}" and is now taking notes.`
              }
            </p>
          </div>

          {/* Meeting Details */}
          <div className="bg-gray-50 rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
              <Video className="w-4 h-4" />
              <span className="font-medium">{meetingTitle}</span>
            </div>
            
            {status === 'success' && (
              <div className="flex items-center justify-center space-x-2 text-xs text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>AI Assistant Active</span>
              </div>
            )}
          </div>

          {/* Progress Indicators */}
          {status === 'joining' && (
            <div className="space-y-3">
              <div className="flex justify-between text-sm text-gray-500">
                <span>Connecting to meeting...</span>
                <span>Step 1/3</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full animate-pulse" style={{ width: '33%' }}></div>
              </div>
            </div>
          )}

          {/* Success Actions */}
          {status === 'success' && (
            <div className="space-y-4 pt-4">
              <div className="text-sm text-gray-600 space-y-2">
                <p>✅ Connected to meeting platform</p>
                <p>✅ AI assistant activated</p>
                <p>✅ Recording and transcription started</p>
              </div>
              
              <button
                onClick={onClose}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300"
              >
                Continue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};