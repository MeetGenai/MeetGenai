import React from 'react';
import { Plus, Clock, ArrowLeft } from 'lucide-react';

interface MeetingOptionsProps {
  onBack: () => void;
  onNewMeeting: () => void;
  onExistingMeeting: () => void;
}

export const MeetingOptions: React.FC<MeetingOptionsProps> = ({
  onBack,
  onNewMeeting,
  onExistingMeeting
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <button
            onClick={onBack}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800">Choose Your Option</h1>
            <p className="text-gray-600 mt-2">Join a new meeting or continue with an existing one</p>
          </div>
          
          <div className="w-16"></div> {/* Spacer for center alignment */}
        </div>

        {/* Options Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
          {/* New Meeting Option */}
          <div 
            onClick={onNewMeeting}
            className="group relative p-8 bg-white/70 backdrop-blur-sm rounded-3xl border border-gray-200 hover:bg-white hover:shadow-xl transition-all duration-300 cursor-pointer hover:-translate-y-2"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            
            <div className="relative z-10 text-center space-y-6">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-300">
                <Plus className="w-10 h-10 text-white" />
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-gray-800 mb-3">Join New Meeting</h3>
                <p className="text-gray-600 leading-relaxed">
                  Start fresh by joining a new meeting. Enter your meeting details and 
                  let our AI assistant take notes for you.
                </p>
              </div>
              
              <div className="pt-4">
                <div className="inline-flex items-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform duration-300">
                  <span>Get Started</span>
                  <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
                </div>
              </div>
            </div>
          </div>

          {/* Existing Meeting Option */}
          <div
            onClick={onExistingMeeting}
            className="group relative p-8 rounded-3xl border transition-all duration-300 cursor-pointer bg-white/70 backdrop-blur-sm border-gray-200 hover:bg-white hover:shadow-xl hover:-translate-y-2"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-all duration-300"></div>

            <div className="relative z-10 text-center space-y-6">
              <div className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto transition-transform duration-300 bg-gradient-to-br from-indigo-500 to-purple-500 group-hover:scale-110">
                <Clock className="w-10 h-10 text-white" />
              </div>

              <div>
                <h3 className="text-2xl font-bold text-gray-800 mb-3">Join Existing Meeting</h3>
                <p className="leading-relaxed text-gray-600">
                  Continue with a previous meeting setup. Select from your saved meetings and join with updated details.
                </p>
              </div>

              <div className="pt-4">
                <div className="inline-flex items-center text-indigo-600 font-semibold group-hover:translate-x-2 transition-transform duration-300">
                  <span>Continue</span>
                  <ArrowLeft className="w-4 h-4 ml-2 rotate-180" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Help Text */}
        <div className="text-center mt-12">
          <p className="text-gray-500 text-sm max-w-2xl mx-auto">
            MeetGenAI will automatically join your meeting, listen to the conversation, 
            and provide you with a comprehensive summary including key points, decisions made, 
            and action items assigned.
          </p>
        </div>
      </div>
    </div>
  );
};