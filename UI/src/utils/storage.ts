export interface StoredMeeting {
  id: string;
  title: string;
  email: string;
  savedAt: number;
  userName?: string;
}

export interface UserData {
  name: string;
  savedAt: number;
}

export const saveUser = (name: string): void => {
  const userData: UserData = {
    name: name.trim(),
    savedAt: Date.now()
  };
  localStorage.setItem('meetgenai_user', JSON.stringify(userData));
};

export const getUser = (): UserData | null => {
  try {
    const stored = localStorage.getItem('meetgenai_user');
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Error loading user from storage:', error);
    return null;
  }
};

export const clearUser = (): void => {
  localStorage.removeItem('meetgenai_user');
};

export const saveMeeting = (title: string, email: string): void => {
  const meetings = getMeetings();
  const user = getUser();
  const newMeeting: StoredMeeting = {
    id: generateId(),
    title: title.trim(),
    email: email.trim(),
    savedAt: Date.now(),
    userName: user?.name
  };
  
  // Remove duplicate meetings with same title and email
  const filteredMeetings = meetings.filter(
    meeting => !(meeting.title === newMeeting.title && meeting.email === newMeeting.email)
  );
  
  filteredMeetings.unshift(newMeeting);
  
  // Keep only the last 10 meetings
  const recentMeetings = filteredMeetings.slice(0, 10);
  
  localStorage.setItem('meetgenai_meetings', JSON.stringify(recentMeetings));
};

export const getMeetings = (): StoredMeeting[] => {
  try {
    const stored = localStorage.getItem('meetgenai_meetings');
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error loading meetings from storage:', error);
    return [];
  }
};



export const hasUser = (): boolean => {
  return getUser() !== null;
};

const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
};