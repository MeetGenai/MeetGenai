import React, { useState, useEffect } from 'react';
import { ArrowLeft, VideoIcon, Mail, Lock, ExternalLink, Clock, User } from 'lucide-react';
import { MeetingData } from './NewMeetingForm';

interface SavedMeeting {
  id: string;
  title: string;
  email: string;
  savedAt: number;
}

interface ExistingMeetingFormProps {
  onBack: () => void;
  onJoinMeeting: (meetingData: MeetingData) => void;
}

export const ExistingMeetingForm: React.FC<ExistingMeetingFormProps> = ({ onBack, onJoinMeeting }) => {
  const [savedMeetings, setSavedMeetings] = useState<SavedMeeting[]>([]);
  const [selectedMeeting, setSelectedMeeting] = useState<SavedMeeting | null>(null);
  const [formData, setFormData] = useState<Omit<MeetingData, 'title'>>({
    link: '',
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState<Partial<Omit<MeetingData, 'title'>>>({});
  const [focusedField, setFocusedField] = useState<string>('');

  useEffect(() => {
    const meetings = JSON.parse(localStorage.getItem('meetgenai_meetings') || '[]');
    setSavedMeetings(meetings);
  }, []);

  const validateForm = () => {
    const newErrors: Partial<Omit<MeetingData, 'title'>> = {};
    
    if (!formData.link.trim()) {
      newErrors.link = 'Meeting link is required';
    } else if (!isValidUrl(formData.link)) {
      newErrors.link = 'Please enter a valid meeting URL';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return url.includes('meet.google.com') || url.includes('zoom.us') || url.includes('teams.microsoft.com');
    } catch {
      return false;
    }
  };

  const isValidEmail = (email: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMeeting && validateForm()) {
      onJoinMeeting({
        title: selectedMeeting.title,
        ...formData
      });
    }
  };

  const handleInputChange = (field: keyof Omit<MeetingData, 'title'>, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleMeetingSelect = (meeting: SavedMeeting) => {
    setSelectedMeeting(meeting);
    setFormData(prev => ({ ...prev, email: meeting.email }));
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

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
            <h1 className="text-3xl font-bold text-gray-800">Existing Meeting</h1>
            <p className="text-gray-600 mt-2">Select a previous meeting and update details</p>
          </div>
          
          <div className="w-16"></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Meeting List */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center space-x-2">
              <Clock className="w-5 h-5" />
              <span>Previous Meetings</span>
            </h2>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {savedMeetings.map((meeting) => (
                <div
                  key={meeting.id}
                  onClick={() => handleMeetingSelect(meeting)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all duration-300 ${
                    selectedMeeting?.id === meeting.id
                      ? 'bg-blue-50 border-blue-300 shadow-md'
                      : 'bg-white/70 backdrop-blur-sm border-gray-200 hover:bg-white hover:shadow-lg hover:-translate-y-1'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-800 mb-2">{meeting.title}</h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <User className="w-4 h-4" />
                        <span>{meeting.email}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Saved on {formatDate(meeting.savedAt)}
                      </p>
                    </div>
                    {selectedMeeting?.id === meeting.id && (
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Form */}
          <div className="space-y-6">
            {selectedMeeting && (
              <div className="bg-blue-50/50 backdrop-blur-sm rounded-2xl border border-blue-200 p-6">
                <h3 className="font-semibold text-gray-800 mb-2">Selected Meeting</h3>
                <p className="text-blue-700 font-medium">{selectedMeeting.title}</p>
              </div>
            )}

            {selectedMeeting ? (
              <div className="bg-white/70 backdrop-blur-sm rounded-3xl border border-gray-200 p-8 shadow-lg">
                <form onSubmit={handleSubmit} className="space-y-8">
                  {/* Meeting Link */}
                  <div className="space-y-2">
                    <label htmlFor="link" className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-3">
                      <ExternalLink className="w-4 h-4" />
                      <span>Meeting Link</span>
                    </label>
                    <div className="relative">
                      <input
                        id="link"
                        type="url"
                        value={formData.link}
                        onChange={(e) => handleInputChange('link', e.target.value)}
                        onFocus={() => setFocusedField('link')}
                        onBlur={() => setFocusedField('')}
                        className={`w-full px-4 py-4 bg-white/50 border-2 rounded-xl transition-all duration-300 ${
                          focusedField === 'link' 
                            ? 'border-blue-500 bg-white shadow-md' 
                            : errors.link 
                              ? 'border-red-300' 
                              : 'border-gray-200 hover:border-gray-300'
                        }`}
                        placeholder="https://meet.google.com/xxx-xxxx-xxx"
                      />
                      {focusedField === 'link' && (
                        <div className="absolute inset-0 bg-blue-500/5 rounded-xl pointer-events-none"></div>
                      )}
                    </div>
                    {errors.link && <p className="text-red-500 text-sm mt-1">{errors.link}</p>}
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <label htmlFor="email" className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-3">
                      <Mail className="w-4 h-4" />
                      <span>Login Email ID</span>
                    </label>
                    <div className="relative">
                      <input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        onFocus={() => setFocusedField('email')}
                        onBlur={() => setFocusedField('')}
                        className={`w-full px-4 py-4 bg-white/50 border-2 rounded-xl transition-all duration-300 ${
                          focusedField === 'email' 
                            ? 'border-blue-500 bg-white shadow-md' 
                            : errors.email 
                              ? 'border-red-300' 
                              : 'border-gray-200 hover:border-gray-300'
                        }`}
                        placeholder="your.email@company.com"
                      />
                      {focusedField === 'email' && (
                        <div className="absolute inset-0 bg-blue-500/5 rounded-xl pointer-events-none"></div>
                      )}
                    </div>
                    {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
                  </div>

                  {/* Password */}
                  <div className="space-y-2">
                    <label htmlFor="password" className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-3">
                      <Lock className="w-4 h-4" />
                      <span>Email Password</span>
                    </label>
                    <div className="relative">
                      <input
                        id="password"
                        type="password"
                        value={formData.password}
                        onChange={(e) => handleInputChange('password', e.target.value)}
                        onFocus={() => setFocusedField('password')}
                        onBlur={() => setFocusedField('')}
                        className={`w-full px-4 py-4 bg-white/50 border-2 rounded-xl transition-all duration-300 ${
                          focusedField === 'password' 
                            ? 'border-blue-500 bg-white shadow-md' 
                            : errors.password 
                              ? 'border-red-300' 
                              : 'border-gray-200 hover:border-gray-300'
                        }`}
                        placeholder="Enter your email password"
                      />
                      {focusedField === 'password' && (
                        <div className="absolute inset-0 bg-blue-500/5 rounded-xl pointer-events-none"></div>
                      )}
                    </div>
                    {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
                  </div>

                  {/* Submit Button */}
                  <div className="pt-6">
                    <button
                      type="submit"
                      className="group w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg flex items-center justify-center space-x-2"
                    >
                      <VideoIcon className="w-5 h-5" />
                      <span>Join Meeting</span>
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              <div className="bg-white/50 backdrop-blur-sm rounded-3xl border border-gray-200 p-12 text-center">
                <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Select a meeting from the list to continue</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};