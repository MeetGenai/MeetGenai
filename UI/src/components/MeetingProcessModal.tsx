import React, { useState, useEffect } from 'react';
import { Loader2, Check, FileText, Brain, Download } from 'lucide-react';
import { getStatus } from '../utils/api';

interface MeetingProcessModalProps {
  isOpen: boolean;
  onComplete: (summary: string) => void;
  meetingTitle: string;
}

type ProcessStep = 'joining' | 'joined' | 'ended' | 'generating' | 'completed';

const processSteps = [
  { key: 'joining', message: 'Trying to join the meeting...', icon: Loader2 },
  { key: 'joined', message: 'Joined the meeting successfully', icon: Check },
  { key: 'ended', message: 'Meeting ended, preparing notes...', icon: FileText },
  { key: 'generating', message: 'Generating summaries...', icon: Brain },
  { key: 'completed', message: 'Summary generation completed', icon: Download }
];

export const MeetingProcessModal: React.FC<MeetingProcessModalProps> = ({ 
  isOpen, 
  onComplete, 
  meetingTitle 
}) => {
  const [currentStep, setCurrentStep] = useState<ProcessStep>('joining');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!isOpen) return;

    const interval = setInterval(async () => {
      try {
        const status = await getStatus();
        let nextStep: ProcessStep = 'joining';
        let progressValue = 0;

        switch (status) {
          case 'not started':
            nextStep = 'joined';
            progressValue = 25;
            break;
          case 'Transcription':
          case 'Preprocessing':
            nextStep = 'ended';
            progressValue = 50;
            break;
          case 'summary generation':
            nextStep = 'generating';
            progressValue = 75;
            break;
          case 'completed':
            nextStep = 'completed';
            progressValue = 100;
            clearInterval(interval);
            // TODO: Get the actual summary
            onComplete('Summary completed!');
            break;
          default:
            nextStep = 'joining';
            progressValue = 10;
        }

        setCurrentStep(nextStep);
        setProgress(progressValue);

      } catch (error) {
        console.error('Error fetching status:', error);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [isOpen, onComplete]);

  if (!isOpen) return null;

  const currentStepData = processSteps.find(step => step.key === currentStep);
  const IconComponent = currentStepData?.icon || Loader2;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-lg w-full mx-4 relative overflow-hidden">
        {/* Background Animation */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 to-indigo-50/30 rounded-3xl"></div>
        
        <div className="relative z-10 text-center space-y-8">
          {/* Animated Icon */}
          <div className="relative mx-auto w-24 h-24">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center ${
              currentStep === 'joined' || currentStep === 'completed'
                ? 'bg-gradient-to-br from-green-500 to-emerald-500'
                : 'bg-gradient-to-br from-blue-500 to-indigo-500'
            }`}>
              <IconComponent className={`w-12 h-12 text-white ${
                currentStep === 'joining' || currentStep === 'generating' ? 'animate-spin' : ''
              } ${currentStep === 'joined' || currentStep === 'completed' ? 'animate-bounce' : ''}`} />
            </div>
            
            {/* Pulse Animation */}
            <div className={`absolute inset-0 rounded-full animate-ping ${
              currentStep === 'joined' || currentStep === 'completed'
                ? 'bg-green-500/30'
                : 'bg-blue-500/30'
            }`}></div>
          </div>

          {/* Status Message */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-gray-800 animate-fadeIn">
              {currentStepData?.message}
            </h3>
            
            <div className="bg-gray-50 rounded-2xl p-4">
              <p className="text-sm text-gray-600 font-medium">{meetingTitle}</p>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-3">
            <div className="flex justify-between text-sm text-gray-500">
              <span>Processing...</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-blue-500 to-indigo-500 h-3 rounded-full transition-all duration-1000 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* Step Indicators */}
          <div className="flex justify-center space-x-2">
            {processSteps.map((step, index) => (
              <div
                key={step.key}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  processSteps.findIndex(s => s.key === currentStep) >= index
                    ? 'bg-blue-500 scale-110'
                    : 'bg-gray-300'
                }`}
              ></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};