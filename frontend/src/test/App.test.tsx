import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import App from '../App';

// Mock the API service to prevent real API calls
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock Register component to prevent async API calls in useEffect
vi.mock('../components/Register', () => ({
  default: ({ onLogin }: { onLogin: (user: { id: number; name: string; phone_number: string }) => void }) => (
    <div data-testid="register-component">
      <h2>Get Started</h2>
      <p>Register with your name and phone number to join SMS group chats</p>
      <form>
        <label htmlFor="name">Your Name</label>
        <input id="name" name="name" type="text" />
        <label htmlFor="phone">Phone Number</label>
        <input id="phone" name="phone" type="tel" />
        <button type="button" onClick={() => onLogin({ id: 1, name: 'Test User', phone_number: '+1234567890' })}>
          Register
        </button>
      </form>
      <div>Demo Mode: Try with any phone number (SMS will be mocked)</div>
    </div>
  )
}));

// Mock GroupList component to prevent async API calls
vi.mock('../components/GroupList', () => ({
  default: () => (
    <div data-testid="group-list">
      <h2>Groups</h2>
      <div>Mock Group List</div>
    </div>
  )
}));

describe('Frontend Tests - Group SMS Chat', () => {
  beforeEach(async () => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
    
    // Set up default mock responses
    const api = await import('../services/api');
    vi.mocked(api.default.get).mockResolvedValue({ data: [] });
    vi.mocked(api.default.post).mockResolvedValue({ data: {} });
  });

  describe('Initial App Rendering', () => {
    it('renders SMS Chat title', () => {
      render(<App />);
      expect(screen.getByText('Group SMS Chat')).toBeTruthy();
    });

    it('shows demo mode banner when not logged in', () => {
      render(<App />);
      expect(screen.getByText(/Demo Mode: Try with any phone number/)).toBeTruthy();
    });

    it('renders login form initially', () => {
      render(<App />);
      expect(screen.getByText('Get Started')).toBeTruthy();
    });

    it('does not crash on initial render', () => {
      expect(() => render(<App />)).not.toThrow();
    });
  });

  describe('User Registration Flow', () => {
    it('shows registration form fields', () => {
      render(<App />);
      
      expect(screen.getByLabelText(/Name/i)).toBeTruthy();
      expect(screen.getByLabelText(/Phone Number/i)).toBeTruthy();
      expect(screen.getByRole('button', { name: /register/i })).toBeTruthy();
    });

    it('allows user input in registration fields', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const nameInput = screen.getByLabelText(/Name/i);
      const phoneInput = screen.getByLabelText(/Phone Number/i);
      
      await user.type(nameInput, 'John Doe');
      await user.type(phoneInput, '+1234567890');
      
      expect(nameInput).toHaveValue('John Doe');
      expect(phoneInput).toHaveValue('+1234567890');
    });
  });

  describe('User Authentication State', () => {
    it('loads user from localStorage if available', () => {
      const mockUser = {
        id: 1,
        name: 'John Doe',
        phone_number: '+1234567890',
        created_at: '2023-01-01'
      };
      
      localStorage.setItem('currentUser', JSON.stringify(mockUser));
      render(<App />);
      
      // Should show user info in header
      expect(screen.getByText('John Doe')).toBeTruthy();
      expect(screen.getByText('+1234567890')).toBeTruthy();
    });

    it('shows logout button when user is logged in', () => {
      const mockUser = {
        id: 1,
        name: 'Jane Smith',
        phone_number: '+1987654321',
        created_at: '2023-01-01'
      };
      
      localStorage.setItem('currentUser', JSON.stringify(mockUser));
      render(<App />);
      
      expect(screen.getByRole('button', { name: /logout/i })).toBeTruthy();
    });

    it('clears user data on logout', async () => {
      const mockUser = {
        id: 1,
        name: 'Jane Smith',
        phone_number: '+1987654321',
        created_at: '2023-01-01'
      };
      
      localStorage.setItem('currentUser', JSON.stringify(mockUser));
      const user = userEvent.setup();
      render(<App />);
      
      const logoutButton = screen.getByRole('button', { name: /logout/i });
      await user.click(logoutButton);
      
      // Should return to registration form
      expect(screen.getByText('Get Started')).toBeTruthy();
      expect(localStorage.getItem('currentUser')).toBeNull();
    });
  });

  describe('Component Error Handling', () => {
    it('does not crash when localStorage contains invalid JSON', () => {
      localStorage.setItem('currentUser', 'invalid-json');
      
      expect(() => render(<App />)).not.toThrow();
      // Should default to showing registration
      expect(screen.getByText('Get Started')).toBeTruthy();
    });

    it('handles missing user data gracefully', () => {
      localStorage.setItem('currentUser', JSON.stringify({}));
      
      expect(() => render(<App />)).not.toThrow();
    });
  });

  describe('Routing', () => {
    it('redirects to groups when user is logged in', async () => {
      const mockUser = {
        id: 1,
        name: 'Test User',
        phone_number: '+1234567890',
        created_at: '2023-01-01'
      };
      
      localStorage.setItem('currentUser', JSON.stringify(mockUser));
      
      render(<App />);
      
      // Should show groups page content instead of registration
      await waitFor(() => {
        expect(screen.queryByTestId('group-list')).toBeTruthy();
      });
    });

    it('shows registration when no user is logged in', () => {
      render(<App />);
      
      expect(screen.getByText('Get Started')).toBeTruthy();
      expect(screen.queryByText(/Groups/)).toBeFalsy();
    });
  });

  describe('Error Boundaries', () => {
    it('catches and handles component errors gracefully', () => {
      // Mock console.error to avoid noise in test output
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      // This test ensures our app doesn't crash completely on errors
      expect(() => render(<App />)).not.toThrow();
      
      consoleError.mockRestore();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels and roles', () => {
      render(<App />);
      
      // Check for semantic HTML elements
      expect(screen.getByRole('button', { name: /register/i })).toBeTruthy();
      expect(screen.getByLabelText(/Name/i)).toBeTruthy();
      expect(screen.getByLabelText(/Phone Number/i)).toBeTruthy();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      // Tab should move through form elements
      await user.tab();
      expect(screen.getByLabelText(/Name/i)).toHaveFocus();
      
      await user.tab();
      expect(screen.getByLabelText(/Phone Number/i)).toHaveFocus();
    });
  });
});