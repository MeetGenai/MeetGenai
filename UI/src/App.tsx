import React, { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { NameEntryModal } from './components/NameEntryModal';
import { MeetingOptions } from './components/MeetingOptions';
import { NewMeetingForm, MeetingData } from './components/NewMeetingForm';
import { ExistingMeetingForm } from './components/ExistingMeetingForm';
import { MeetingProcessModal } from './components/MeetingProcessModal';
import { SummaryModal } from './components/SummaryModal';
import { ContactModal } from './components/ContactModal';
import { saveMeeting, saveUser, getUser, hasUser } from './utils/storage';

type AppState = 'landing' | 'options' | 'new-meeting' | 'existing-meeting';

function App() {
  const [currentState, setCurrentState] = useState<AppState>('landing');
  const [showNameModal, setShowNameModal] = useState(false);
  const [showProcessModal, setShowProcessModal] = useState(false);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [currentMeetingTitle, setCurrentMeetingTitle] = useState('');
  const [meetingSummary, setMeetingSummary] = useState('');
  const [userName, setUserName] = useState<string>('');

  React.useEffect(() => {
    const user = getUser();
    if (user) {
      setUserName(user.name);
    }
  }, []);

  const handleGetStarted = () => {
    if (!hasUser()) {
      setShowNameModal(true);
    } else {
    setCurrentState('options');
    }
  };

  const handleNameSubmit = (name: string) => {
    saveUser(name);
    setUserName(name);
    setShowNameModal(false);
    setCurrentState('options');
  };

  const handleBackToLanding = () => {
    setCurrentState('landing');
  };

  const handleBackToOptions = () => {
    setCurrentState('options');
  };

  const handleNewMeeting = () => {
    setCurrentState('new-meeting');
  };

  const handleExistingMeeting = () => {
    setCurrentState('existing-meeting');
  };

  const handleJoinMeeting = async (meetingData: MeetingData) => {
    // Save meeting to localStorage
    saveMeeting(meetingData.title, meetingData.email);
    
    // Set current meeting title for modal
    setCurrentMeetingTitle(meetingData.title);
    
    // Show process modal
    setShowProcessModal(true);

    try {
      const response = await fetch('/api/join_meeting', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(meetingData),
      });

      if (!response.ok) {
        throw new Error('Failed to join meeting');
      }

      // You can optionally handle the response here
      const result = await response.json();
      console.log(result);

    } catch (error) {
      console.error('Error joining meeting:', error);
      // Handle error appropriately in the UI
    }
  };

  const handleProcessComplete = (summary: string) => {
    setMeetingSummary(summary);
    setShowProcessModal(false);
    setShowSummaryModal(true);
  };

  const handleCloseSummaryModal = () => {
    setShowSummaryModal(false);
    setCurrentState('landing');
  };

  const handleContactUs = () => {
    setShowContactModal(true);
  };

  const handleCloseContactModal = () => {
    setShowContactModal(false);
  };

  const renderCurrentState = () => {
    switch (currentState) {
      case 'landing':
        return (
          <LandingPage 
            onGetStarted={handleGetStarted}
            onContactUs={handleContactUs}
            userName={userName}
          />
        );
      
      case 'options':
        return (
          <MeetingOptions
            onBack={handleBackToLanding}
            onNewMeeting={handleNewMeeting}
            onExistingMeeting={handleExistingMeeting}
          />
        );
      
      case 'new-meeting':
        return (
          <NewMeetingForm
            onBack={handleBackToOptions}
            onJoinMeeting={handleJoinMeeting}
          />
        );
      
      case 'existing-meeting':
        return (
          <ExistingMeetingForm
            onBack={handleBackToOptions}
            onJoinMeeting={handleJoinMeeting}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="App">
      {renderCurrentState()}
      
      {/* Modals */}
      <NameEntryModal
        isOpen={showNameModal}
        onClose={() => setShowNameModal(false)}
        onSubmit={handleNameSubmit}
      />
      
      <MeetingProcessModal
        isOpen={showProcessModal}
        onComplete={handleProcessComplete}
        meetingTitle={currentMeetingTitle}
      />
      
      <SummaryModal
        isOpen={showSummaryModal}
        onClose={handleCloseSummaryModal}
        summary={meetingSummary}
        meetingTitle={currentMeetingTitle}
      />
      
      <ContactModal
        isOpen={showContactModal}
        onClose={handleCloseContactModal}
      />
    </div>
  );
}

export default App;