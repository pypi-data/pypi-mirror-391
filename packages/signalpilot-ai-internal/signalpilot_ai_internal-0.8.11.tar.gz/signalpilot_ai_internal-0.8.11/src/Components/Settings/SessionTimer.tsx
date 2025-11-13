import * as React from 'react';
import { getCurrentSessionInfo } from '../../sessionUtils';

interface ISessionData {
  slot: number;
  session_id: string;
  container: string;
  expires_at: string;
  time_remaining_minutes: number;
  duration_minutes: number;
  is_expired: boolean;
}

interface ISessionTimerProps {
  onSessionExpired?: () => void;
}

/**
 * Beautiful animated session timer component
 * Displays time remaining and handles session expiration
 */
export function SessionTimer({ onSessionExpired }: ISessionTimerProps): JSX.Element | null {
  const [sessionData, setSessionData] = React.useState<ISessionData | null>(null);
  const [timeRemaining, setTimeRemaining] = React.useState<number>(0);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [isExpired, setIsExpired] = React.useState<boolean>(false);
  const [error, setError] = React.useState<string | null>(null);

  // Format time remaining as MM:SS
  const formatTime = (minutes: number): { minutes: number; seconds: number } => {
    const totalSeconds = Math.max(0, Math.floor(minutes * 60));
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return { minutes: mins, seconds: secs };
  };

  // Fetch session data
  const fetchSessionData = React.useCallback(async () => {
    try {
      const data = await getCurrentSessionInfo();
      
      if (!data) {
        setError('Unable to fetch session data');
        setIsLoading(false);
        return;
      }

      setSessionData(data);
      setTimeRemaining(data.time_remaining_minutes);
      
      if (data.is_expired) {
        setIsExpired(true);
        if (onSessionExpired) {
          onSessionExpired();
        }
      }
      
      setIsLoading(false);
      setError(null);
    } catch (err) {
      console.error('[SessionTimer] Error fetching session data:', err);
      setError('Failed to load session data');
      setIsLoading(false);
    }
  }, [onSessionExpired]);

  // Initial fetch on mount
  React.useEffect(() => {
    void fetchSessionData();
  }, [fetchSessionData]);

  // Countdown timer - update every second
  React.useEffect(() => {
    if (isExpired || isLoading || !sessionData) {
      return;
    }

    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        const newTime = prev - (1 / 60); // Decrease by 1 second
        
        if (newTime <= 0) {
          setIsExpired(true);
          if (onSessionExpired) {
            onSessionExpired();
          }
          return 0;
        }
        
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isExpired, isLoading, sessionData, onSessionExpired]);

  // Periodic refresh from server (every 30 seconds)
  React.useEffect(() => {
    if (isExpired) {
      return;
    }

    const interval = setInterval(() => {
      void fetchSessionData();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [isExpired, fetchSessionData]);

  if (isLoading) {
    return (
      <div className="sage-session-timer-container sage-session-timer-loading">
        <div className="sage-session-timer-spinner">
          <div className="sage-session-spinner-ring" />
          <div className="sage-session-spinner-pulse" />
        </div>
        <span className="sage-session-timer-loading-text">Loading session...</span>
      </div>
    );
  }

  if (error) {
    return null; // Silently fail if not in a cloud session
  }

  if (!sessionData) {
    return null;
  }

  const { minutes, seconds } = formatTime(timeRemaining);
  const percentRemaining = (timeRemaining / sessionData.duration_minutes) * 100;
  
  // Color based on time remaining
  let colorClass = 'sage-session-timer-normal';
  if (percentRemaining < 20) {
    colorClass = 'sage-session-timer-critical';
  } else if (percentRemaining < 50) {
    colorClass = 'sage-session-timer-warning';
  }

  return (
    <div className={`sage-session-timer-container ${colorClass}`}>
      <div className="sage-session-timer-header">
        <span className="sage-session-timer-icon">⏱️</span>
        <span className="sage-session-timer-label">Session Time Remaining</span>
      </div>
      
      <div className="sage-session-timer-display">
        <div className="sage-session-timer-numbers">
          <div className="sage-session-timer-number-group">
            <span className="sage-session-timer-value">{String(minutes).padStart(2, '0')}</span>
            <span className="sage-session-timer-unit">min</span>
          </div>
          <span className="sage-session-timer-separator">:</span>
          <div className="sage-session-timer-number-group">
            <span className="sage-session-timer-value">{String(seconds).padStart(2, '0')}</span>
            <span className="sage-session-timer-unit">sec</span>
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="sage-session-timer-progress-container">
        <div 
          className="sage-session-timer-progress-bar"
          style={{ width: `${percentRemaining}%` }}
        />
      </div>

      {/* Session info */}
      <div className="sage-session-timer-info">
        <span className="sage-session-timer-info-text">
          Session expires at {new Date(sessionData.expires_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}

/**
 * Session expired modal overlay
 */
export function SessionExpiredBanner(): JSX.Element {
  const handleExit = () => {
    window.location.href = 'https://signalpilot.ai/';
  };

  return (
    <div className="sage-session-expired-overlay">
      <div className="sage-session-expired-modal">
        <div className="sage-session-expired-icon">⚠️</div>
        <h2 className="sage-session-expired-title">Session Expired</h2>
        <p className="sage-session-expired-message">
          Your session has expired. Please return to the main site to start a new session.
        </p>
        <button 
          className="sage-session-expired-button"
          onClick={handleExit}
        >
          Exit to SignalPilot.ai
        </button>
      </div>
    </div>
  );
}
