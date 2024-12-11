import React from 'react';

const Chatbutton = () => {
  const handleChatbot = async () => {
    try {
      const response = await fetch('http://localhost:5000/start-chatbot');
      const data = await response.json();
      if (data.url) {
        window.open(data.url, '_blank'); // Open chatbot in a new tab
      }
    } catch (error) {
      console.error('Error starting chatbot:', error);
      alert('Failed to start chatbot. Please try again.');
    }
  };

  return (
    <button
      onClick={handleChatbot}
      className="absolute bottom-20 right-20 chatbot-btn px-3 py-2 rounded-lg bg-green-500 text-white font-semibold"
    >
      Chatbot 🤖
    </button>
  );
};

export default Chatbutton;
