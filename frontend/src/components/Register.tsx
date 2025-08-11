import React, { useState, useEffect } from 'react';
import { User, UserPlus, LogIn, MessageSquare, Smartphone, Check, Lock } from 'lucide-react';
import api from '../services/api';
import { User as UserType } from '../types';

interface RegisterProps {
  onLogin: (user: UserType) => void;
}

function Register({ onLogin }: RegisterProps) {
  const [name, setName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMockMode, setIsMockMode] = useState(false);

  useEffect(() => {
    let mounted = true;
    
    // Check if we're in mock mode
    const checkMockMode = async () => {
      try {
        const response = await api.get('/health');
        if (mounted) {
          setIsMockMode(response.data.mock_mode);
        }
      } catch (error) {
        console.error('Health check failed:', error);
        if (mounted) {
          setIsMockMode(false);
        }
      }
    };
    
    checkMockMode();
    
    return () => {
      mounted = false;
    };
  }, []);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await api.post('/users/send-otp', {
        phone_number: phoneNumber
      });
      setShowOtpInput(true);
      setError('');
    } catch (err) {
      setError('Failed to send OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setError('');
    setIsLoading(true);

    try {
      if (isRegistering) {
        // Register with OTP
        const response = await api.post('/users/register', {
          phone_number: phoneNumber,
          name: name,
          otp_code: otpCode
        });
        onLogin(response.data);
      } else {
        // Login with OTP
        const response = await api.post('/users/login', {
          phone_number: phoneNumber,
          otp_code: otpCode
        });
        onLogin(response.data);
      }
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const errorResponse = err as { response?: { data?: { detail?: string }, status?: number } };
        if (errorResponse.response?.data?.detail) {
          setError(errorResponse.response.data.detail);
        } else {
          setError(isRegistering ? 'Failed to register. Please try again.' : 'Failed to login. Please try again.');
        }
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = () => {
    setIsRegistering(true);
    const submitEvent = new Event('submit') as unknown as React.FormEvent;
    handleSendOtp(submitEvent);
  };

  const handleLogin = () => {
    setIsRegistering(false);
    const submitEvent = new Event('submit') as unknown as React.FormEvent;
    handleSendOtp(submitEvent);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-8 text-white">
          <h2 className="text-3xl font-bold mb-2 flex items-center">
            <UserPlus className="mr-3 h-8 w-8" />
            Get Started
          </h2>
          <p className="text-indigo-100">
            Register with your name and phone number to join SMS group chats
          </p>
        </div>
        
        <div className="p-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          {!showOtpInput ? (
            <form onSubmit={handleSendOtp} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <User className="inline h-4 w-4 mr-1" />
                Your Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Smartphone className="inline h-4 w-4 mr-1" />
                Phone Number
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+1234567890 (with country code)"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              />
              <p className="mt-2 text-sm text-gray-500">
                Include country code (e.g., +1 for US, +44 for UK)
              </p>
            </div>
            
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleRegister}
                  disabled={isLoading || !phoneNumber || !name}
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? 'Sending OTP...' : (
                    <>
                      <UserPlus className="inline h-5 w-5 mr-2" />
                      Register
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleLogin}
                  disabled={isLoading || !phoneNumber}
                  className="flex-1 bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  <LogIn className="inline h-5 w-5 mr-2" />
                  Login
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Lock className="inline h-4 w-4 mr-1" />
                  Enter OTP Code
                </label>
                <input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors text-center text-2xl tracking-widest"
                  autoFocus
                />
                <p className="mt-2 text-sm text-gray-500">
                  We sent a verification code to {phoneNumber}
                </p>
                {isMockMode && (
                  <div className="mt-3 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <p className="text-sm text-yellow-800">
                      <strong>Mock Mode:</strong> Use code <span className="font-mono font-bold">111111</span>
                    </p>
                  </div>
                )}
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleVerifyOtp}
                  disabled={isLoading || otpCode.length !== 6}
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? 'Verifying...' : 'Verify & Continue'}
                </button>
                <button
                  onClick={() => {
                    setShowOtpInput(false);
                    setOtpCode('');
                    setError('');
                  }}
                  disabled={isLoading}
                  className="px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all"
                >
                  Back
                </button>
              </div>
            </div>
          )}
          
          <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <MessageSquare className="h-5 w-5 mr-2 text-indigo-600" />
              How it works
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <Check className="h-4 w-4 mr-2 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Register with your phone number</span>
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 mr-2 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Browse and join group chats</span>
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 mr-2 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Receive SMS when you join a group</span>
              </li>
              <li className="flex items-start">
                <Check className="h-4 w-4 mr-2 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Reply to SMS to send messages to the group</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;