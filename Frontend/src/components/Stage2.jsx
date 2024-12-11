// Stage2.jsx
import React, { useState, useEffect } from 'react';
import { CheckCircle2 } from 'lucide-react';
import Modal from './Modal'; // Assuming you create a Modal component
import { useLocation } from 'react-router-dom';

const Stage2 = () => {
  const location = useLocation();
  
  // Retrieve from location.state or sessionStorage
  const { accusedName: stateAccusedName, caseNumber: stateCaseNumber } = location.state || {};
  const [accusedName] = useState(stateAccusedName || sessionStorage.getItem('accusedName') || '');
  const [caseNumber] = useState(stateCaseNumber || sessionStorage.getItem('caseNumber') || '');

  const [platform, setPlatform] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [contactName, setContactName] = useState('');
  const [modalMessage, setModalMessage] = useState('');

  useEffect(() => {
    const storedPlatform = sessionStorage.getItem('platform');
    const storedUsername = sessionStorage.getItem('username');
    const storedPassword = sessionStorage.getItem('password');

    if (storedPlatform) {
      setPlatform(storedPlatform.toLowerCase());

      if (storedPlatform.toLowerCase() === 'whatsapp') {
        setMessage('Logged in successfully via WhatsApp!');
      } else if (storedUsername && storedPassword) {
        setUsername(storedUsername);
        setPassword(storedPassword);
      } else {
        setMessage('Error: Missing credentials. Please return to Stage1.');
      }
    } else {
      setMessage('Error: Missing platform. Please return to Stage1.');
    }
  }, []);

  const handleButtonClick = async (option) => {
    setMessage('');
    setIsLoading(true);

    try {
      if (!platform) {
        setMessage('Error: Missing platform.');
        setIsLoading(false);
        return;
      }

      const requestBody =
        (platform === 'whatsapp' || platform === 'telegram') && option === 'Parse Chats'
          ? { platform, option, accusedName, caseNumber }
          : { platform, username, password, option, accusedName, caseNumber };

      const response = await fetch('http://localhost:5000/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${platform}_${option.replace(' ', '_')}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        setMessage('File downloaded successfully.');
      } else {
        const data = await response.json();
        setMessage(`Error: ${data.message}`);
      }
    } catch (error) {
      setMessage('Error occurred during parsing. Please try again.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleParseAll = async () => {
    await handleButtonClick('Parse All');
  };

  const openModal = () => {
    setIsModalOpen(true);
    setContactName('');
    setModalMessage('');
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setContactName('');
    setModalMessage('');
  };

  const handleIndividualParse = async () => {
    if (!contactName.trim()) {
      setModalMessage('Please enter a contact name.');
      return;
    }

    setIsLoading(true);
    setModalMessage('');

    try {
      const response = await fetch('http://localhost:5000/parse-individual-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, contactName, accusedName, caseNumber }),
        });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${platform}_chat_${contactName.replace(' ', '_')}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        closeModal();
      } else {
        const data = await response.json();
        setModalMessage(data.message || 'Person not found.');
      }
    } catch (error) {
      setModalMessage('An error occurred. Please try again.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="loginContainer h-[70vh] flex flex-col gap-6 rounded-md w-[30vw] border-2 border-black bg-white">
      <div className="flex justify-evenly p-6">
        <CheckCircle2 className="bg-green-500 rounded-full" />
        <CheckCircle2 className="bg-green-500 rounded-full" />
        <p className="rounded-full border border-black px-2 py-1">3</p>
      </div>

      <h1 className="text-3xl text-center font-medium">Parsing Options</h1>

      {platform ? (
        <p className="text-center text-lg">
          {(platform === 'whatsapp' || platform === 'telegram') ? (
            <>
              Logged into <strong>{platform}</strong>.
            </>
          ) : (
            <>
              Logged into <strong>{platform.toUpperCase()}</strong> as{' '}
              <strong>{username}</strong>.
            </>
          )}
        </p>
      ) : (
        <p className="text-red-500 text-center">{message}</p>
      )}

      <p>Accused Name: {accusedName}</p>
      <p>Case Number: {caseNumber}</p>

      <div className="flex flex-col gap-5 px-10">
        {(platform === 'whatsapp' || platform === 'telegram' )? (
          <>
            <button
              className="rounded-lg px-4 py-2 text-white bg-green-600 hover:bg-green-800"
              onClick={() => handleButtonClick('Parse Chats')}
              disabled={isLoading}
            >
              Parse Chats
            </button>
            <button
              className="rounded-lg px-4 py-2 text-white bg-blue-600 hover:bg-blue-800"
              onClick={openModal}
              disabled={isLoading}
            >
              Parse Individual Chats
            </button>
          </>
        ) : (
          <>
            {['Parse Followers', 'Parse Posts', 'Parse Chats'].map((option, index) => (
              <button
                key={index}
                className="rounded-lg px-4 py-2 text-white bg-green-600 hover:bg-green-800"
                onClick={() => handleButtonClick(option)}
                disabled={isLoading}
              >
                {option}
              </button>
            ))}

            <button
              className="rounded-lg px-4 py-2 text-white bg-green-600 hover:bg-green-800"
              onClick={handleParseAll}
              disabled={isLoading}
            >
              Parse All
            </button>
          </>
        )}
      </div>

      {isLoading && (
        <p className="text-blue-500 text-center">Wait... the file is getting ready for download.</p>
      )}

      {message && !isLoading && (
        <p className="text-green-500 text-center">{message}</p>
      )}

      {isModalOpen && (
        <Modal onClose={closeModal}>
          <h2 className="text-xl font-semibold mb-4">Parse Individual Chat</h2>
          <input
            type="text"
            className="w-full px-3 py-2 border rounded mb-4"
            placeholder="Enter contact name"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
          />
          {modalMessage && <p className="text-red-500 mb-4">{modalMessage}</p>}
          <div className="flex justify-end gap-2">
            <button
              className="px-4 py-2 bg-gray-300 rounded"
              onClick={closeModal}
            >
              Cancel
            </button>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded"
              onClick={handleIndividualParse}
              disabled={isLoading}
            >
              {isLoading ? 'Parsing...' : 'Parse'}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Stage2;