import { CheckCircle2, Eye, EyeOff, User, CheckCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

const Stage1 = () => {
  const { platform } = useParams(); // Get the platform from URL
  const location = useLocation();
  
  // Retrieve from location.state or sessionStorage
  const { accusedName: stateAccusedName, caseNumber: stateCaseNumber } = location.state || {};
  const [accusedName, setAccusedName] = useState(stateAccusedName || sessionStorage.getItem('accusedName') || '');
  const [caseNumber, setCaseNumber] = useState(stateCaseNumber || sessionStorage.getItem('caseNumber') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [passwordType, setPasswordType] = useState('password');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [qrCode, setQrCode] = useState(null); // State to hold the QR code
  const navigate = useNavigate();

  // Function to fetch the QR code from the backend
  const fetchQRCode = () => {
    if (platform === 'whatsapp') {
      fetch('http://localhost:5000/get-whatsapp-qr')
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch QR code');
          }
          return response.blob();
        })
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          setQrCode(url); // Update state to display QR code
        })
        .catch((error) => {
          console.error(error);
          setErrorMessage('Failed to load WhatsApp QR code. Please try again.');
        });
    } else if (platform === 'telegram') {
      fetch('http://localhost:5000/get-telegram-qr')
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to fetch QR code');
          }
          return response.blob();
        })
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          setQrCode(url); // Update state to display QR code
        })
        .catch((error) => {
          console.error(error);
          setErrorMessage('Failed to load Telegram QR code. Please try again.');
        });
    }
  };
  // Poll WhatsApp login status
  const checkWhatsAppLogin = async () => {
    
    try {
      const response = await fetch('http://localhost:5000/check-whatsapp-login');
      const data = await response.json();
      if (data.loggedIn) {
        setShowSuccess(true);
        sessionStorage.setItem('platform', 'whatsapp');
        setTimeout(() => {
          navigate('/stage2');
        }, 2000); // Navigate after a short delay
      }
    } catch (error) {
      console.error('Error checking WhatsApp login:', error);
    }
  

  };
  const checkTelegramLogin = async () => {
    try {
      const response = await fetch('http://localhost:5000/check-telegram-login');
      const data = await response.json();
      if (data.loggedIn) {
        setShowSuccess(true);
        sessionStorage.setItem('platform', 'telegram');
        setTimeout(() => {
          navigate('/stage2');
        }, 20000); // Navigate after a short delay
      }
    } catch (error) {
      console.error('Error checking Telegram login:', error);
    }
  };

  useEffect(() => {
    fetchQRCode(); // Initial QR code fetch
    const qrUpdateInterval = setInterval(fetchQRCode, 20 * 1000); // Refresh QR code every 15 seconds

    const loginCheckInterval = platform === 'whatsapp'
      ? setInterval(checkWhatsAppLogin, 5000)
      : setInterval(checkTelegramLogin, 5000); // Check login status every 5 seconds

    return () => {
      clearInterval(qrUpdateInterval); // Cleanup QR code interval
      clearInterval(loginCheckInterval); // Cleanup login check interval
    };
  }, [platform]);

  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setPasswordType(passwordType === 'password' ? 'text' : 'password');
  };

  const handleLogin = async () => {
    setIsLoading(true);
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setShowSuccess(true);

        sessionStorage.setItem('username', username);
        sessionStorage.setItem('password', password);
        sessionStorage.setItem('platform', platform);
        sessionStorage.setItem('accusedName', accusedName);
        sessionStorage.setItem('caseNumber', caseNumber);
        setTimeout(() => {
          navigate('/stage2');
        }, 2000);
      } else {
        setErrorMessage(data.message || 'Invalid username or password');
      }
    } catch (error) {
      setErrorMessage('An error occurred while logging in. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative">
      {/* Login Form */}
      {(platform === 'whatsapp' || platform === 'telegram') ? (
        // Display QR code for WhatsApp login
        <div className="flex flex-col items-center gap-4 p-6 bg-white rounded-md shadow-lg">
          <h1 className="text-3xl font-medium text-center">{platform} Login</h1>
          {qrCode ? (
            <img
              src={qrCode}
              alt="WhatsApp QR Code"
              className="border rounded-lg shadow-md"
            />
          ) : (
            <p className="text-gray-500">Loading QR code...</p>
          )}
          {errorMessage && <p className="text-red-500">{errorMessage}</p>}
          <p className="text-black-500">Scan this QR code to link a device!</p>
        </div>
      ) : (
        <div className="loginContainer h-[60vh] flex flex-col gap-10 rounded-md w-[25vw] border-2 border-black bg-white">
          <div className="flex justify-evenly p-6">
            <CheckCircle2 className="bg-green-500 rounded-full" />
            <p className="rounded-full border border-black px-2 py-1">2</p>
            <p className="rounded-full border border-black px-2 py-1">3</p>
          </div>

          <h1 className="text-3xl text-center font-medium">
            {`Login to ${platform.charAt(0).toUpperCase() + platform.slice(1)}`}
          </h1>

          <div className="flex justify-center items-center relative">
            <User className="absolute right-24" />
            <input
              type="text"
              className="rounded-lg border px-3 py-2 border-neutral-300"
              placeholder="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="flex justify-center items-center relative">
            <button
              type="button"
              className="absolute top-0 right-24 p-2"
              onClick={togglePasswordVisibility}
            >
              {passwordType === 'password' ? <Eye /> : <EyeOff />}
            </button>
            <input
              type={passwordType}
              className="rounded-lg border px-3 py-2 border-neutral-300"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {errorMessage && <p className="text-red-500 text-center">{errorMessage}</p>}

          <div className="flex justify-center">
            <button
              className="hover:no-underline bg-green-500 rounded-md px-3 py-2 w-20 flex justify-center items-center"
              onClick={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? 'Loading...' : 'Login'}
            </button>
          </div>
        </div>
      )}

      {/* Success Message Overlay */}
      {showSuccess && (
        <div className="absolute inset-0 flex justify-center items-center bg-black bg-opacity-50">
          <div className="flex flex-col items-center bg-white rounded-lg p-8 shadow-lg w-[30vw]">
            <CheckCircle className="text-green-500 w-16 h-16" />
            <h2 className="text-2xl font-semibold text-green-500 mt-4">
              Login Successful!
            </h2>
            <p className="text-gray-500 mt-2">
              Redirecting you to the next stage...
            </p>
          </div>
        </div>
      )}
      <p>Accused Name: {accusedName}</p>
      <p>Case Number: {caseNumber}</p>
    </div>
  );
};

export default Stage1;
