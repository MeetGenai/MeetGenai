import { MeetingData } from './storage';

const API_BASE_URL = 'http://localhost:8000';

export const joinMeeting = async (meetingData: MeetingData): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/api/join_meeting`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(meetingData),
  });

  if (!response.ok) {
    throw new Error('Failed to join meeting');
  }
};

export const getStatus = async (): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/api/get_status`);
  if (!response.ok) {
    throw new Error('Failed to get status');
  }
  const data = await response.json();
  return data.status;
};
