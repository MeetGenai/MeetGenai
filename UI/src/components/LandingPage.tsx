import React from 'react';
import { Bot, Users, Brain, ArrowRight, Sparkles } from 'lucide-react';

interface LandingPageProps {
  onGetStarted: () => void;
  onContactUs: () => void;
  userName?: string;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted, onContactUs, userName }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 relative overflow-hidden">
      {/* Background Animation Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-4 -right-4 w-72 h-72 bg-blue-200/30 rounded-full mix-blend-multiply filter blur-xl animate-float"></div>
        <div className="absolute top-1/3 -left-4 w-72 h-72 bg-indigo-200/30 rounded-full mix-blend-multiply filter blur-xl animate-float-delayed"></div>
        <div className="absolute bottom-1/4 right-1/3 w-72 h-72 bg-cyan-200/30 rounded-full mix-blend-multiply filter blur-xl animate-float-slow"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-purple-200/20 rounded-full mix-blend-multiply filter blur-2xl animate-pulse"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center animate-pulse">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-ping"></div>
            <Sparkles className="absolute -top-2 -left-2 w-4 h-4 text-yellow-400 animate-bounce" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              MeetGenAI
            </h1>
            <p className="text-xs text-gray-500 font-medium">AI Meeting Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {userName && (
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-white/70 backdrop-blur-sm rounded-full border border-gray-200">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">{userName.charAt(0).toUpperCase()}</span>
              </div>
              <span className="text-sm font-medium text-gray-700">Welcome, {userName.split(' ')[0]}</span>
            </div>
          )}
        <button
          onClick={onContactUs}
          className="px-6 py-3 bg-white/70 backdrop-blur-sm border border-gray-200 text-gray-700 rounded-full hover:bg-white hover:shadow-lg transition-all duration-300 hover:scale-105 font-medium"
        >
          Contact Us
        </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-6 text-center">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="space-y-6">
            <div className="space-y-4">
              {userName && (
                <p className="text-xl text-blue-600 font-semibold animate-fadeIn">
                  Welcome back, {userName.split(' ')[0]}! 👋
                </p>
              )}
            <h2 className="text-5xl md:text-7xl font-bold text-gray-800 leading-tight animate-slideUp">
              Never Miss a
              <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Meeting Detail
              </span>
            </h2>
            </div>
            
            <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed animate-fadeIn">
              Automated meeting assistant that joins your Google Meet and Zoom calls, 
              then generates comprehensive summaries with action items, keynotes, and maintains context from previous meetings.
            </p>
          </div>

          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-12 animate-staggerIn">
            <div className="group p-6 bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 hover:bg-white hover:shadow-xl transition-all duration-500 hover:-translate-y-2 hover:rotate-1">
              <Users className="w-12 h-12 text-blue-600 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Auto-Join Meetings</h3>
              <p className="text-gray-600">Seamlessly joins Google Meet and Zoom calls on your behalf</p>
            </div>
            
            <div className="group p-6 bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 hover:bg-white hover:shadow-xl transition-all duration-500 hover:-translate-y-2 hover:-rotate-1">
              <Brain className="w-12 h-12 text-indigo-600 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">AI-Powered Summaries</h3>
              <p className="text-gray-600">Generates intelligent summaries with key insights, decisions, and context</p>
            </div>
            
            <div className="group p-6 bg-white/60 backdrop-blur-sm rounded-2xl border border-gray-200 hover:bg-white hover:shadow-xl transition-all duration-500 hover:-translate-y-2 hover:rotate-1">
              <ArrowRight className="w-12 h-12 text-cyan-600 mx-auto mb-4 group-hover:scale-110 transition-transform duration-300" />
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Action Items</h3>
              <p className="text-gray-600">Automatically extracts and organizes action items for follow-up</p>
            </div>
          </div>

          {/* CTA Button */}
          <div className="pt-8">
            <button
              onClick={onGetStarted}
              className="group relative px-16 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xl font-semibold rounded-full hover:from-blue-700 hover:to-indigo-700 transition-all duration-500 hover:scale-110 hover:shadow-2xl shadow-xl animate-pulse-slow"
            >
              <span className="flex items-center space-x-2">
                <span>{userName ? "Let's Continue" : "Let's Start"}</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform duration-300" />
              </span>
              
              {/* Button Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full blur-lg opacity-40 group-hover:opacity-70 transition-opacity duration-500 -z-10 animate-pulse"></div>
            </button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-6 px-6 text-center">
        <div className="max-w-4xl mx-auto">
          <p className="text-sm text-gray-500">
            © 2025 MeetGenAI. Revolutionizing meeting productivity with AI.
          </p>
        </div>
      </footer>
    </div>
  );
};