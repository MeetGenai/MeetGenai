import React, { useState } from 'react';
import { ArrowLeft, VideoIcon, Mail, Lock, Type, ExternalLink } from 'lucide-react';


interface NewMeetingFormProps {
  onBack: () => void;
  onJoinMeeting: (meetingData: MeetingData) => void;
}

export interface MeetingData {
  title: string;
  link: string;
  email: string;
  password: string;
}

export const NewMeetingForm: React.FC<NewMeetingFormProps> = ({ onBack, onJoinMeeting }) => {
  const [formData, setFormData] = useState<MeetingData>({
    title: '',
    link: '',
    email: '',
    password: ''
  });

  const [errors, setErrors] = useState<Partial<MeetingData>>({});
  const [focusedField, setFocusedField] = useState<string>('');

  const validateForm = () => {
    const newErrors: Partial<MeetingData> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Meeting title is required';
    }
    
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      // Show loading state (optional)
      // setLoading(true);

      const response = await fetch('http://localhost:5000/api/join_meeting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        // Handle errors as needed
        const err = await response.json();
        alert(`Failed to join: ${err.message}`);
        // setLoading(false);
        return;
      }

      // Success: get returned data if needed
      const result = await response.json();
      onJoinMeeting(formData); // or pass result if needed

      // setLoading(false);

    } catch (error) {
      alert('Network error, please try again.');
      // setLoading(false);
    }
  };


  const handleInputChange = (field: keyof MeetingData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-2xl mx-auto">
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
            <h1 className="text-3xl font-bold text-gray-800">New Meeting</h1>
            <p className="text-gray-600 mt-2">Enter your meeting details to get started</p>
          </div>
          
          <div className="w-16"></div>
        </div>

        {/* Form */}
        <div className="bg-white/70 backdrop-blur-sm rounded-3xl border border-gray-200 p-8 shadow-lg">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Meeting Title */}
            <div className="space-y-2">
              <label htmlFor="title" className="flex items-center space-x-2 text-sm font-semibold text-gray-700 mb-3">
                <Type className="w-4 h-4" />
                <span>Meeting Title</span>
              </label>
              <div className="relative">
                <input
                  id="title"
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  onFocus={() => setFocusedField('title')}
                  onBlur={() => setFocusedField('')}
                  className={`w-full px-4 py-4 bg-white/50 border-2 rounded-xl transition-all duration-300 ${
                    focusedField === 'title' 
                      ? 'border-blue-500 bg-white shadow-md' 
                      : errors.title 
                        ? 'border-red-300' 
                        : 'border-gray-200 hover:border-gray-300'
                  }`}
                  placeholder="Enter your meeting title"
                />
                {focusedField === 'title' && (
                  <div className="absolute inset-0 bg-blue-500/5 rounded-xl pointer-events-none"></div>
                )}
              </div>
              {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
            </div>

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

        {/* Security Note */}
        <div className="mt-8 p-4 bg-blue-50/50 rounded-2xl border border-blue-200">
          <p className="text-sm text-blue-700 text-center">
            🔒 Your credentials are securely processed and used only to join the meeting on your behalf.
          </p>
        </div>
      </div>
    </div>
  );
};