import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const AccusedData = () => {
  const { platform } = useParams();
  const navigate = useNavigate();
  const [accusedName, setAccusedName] = useState('');
  const [caseNumber, setCaseNumber] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Save to sessionStorage
    sessionStorage.setItem('accusedName', accusedName);
    sessionStorage.setItem('caseNumber', caseNumber);
    // Navigate to Stage1 with platform, accusedName, and caseNumber as state
    navigate(`/stage1/${platform}`, { state: { accusedName, caseNumber } });
  };

  return (
      <div className='loginContainer p-6 h-[50vh] flex flex-col gap-3 rounded-xl w-[30vw] border-2 border-black bg-white'>

    
    <h2 className="text-3xl text-center font-medium">Enter Accused Details</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Accused Name"
          value={accusedName}
          onChange={(e) => setAccusedName(e.target.value)}
        className="w-full px-3 py-2 border rounded mb-4"
          required
        />
        <input
          type="text"
          placeholder="Case Number"
          value={caseNumber}
          className="w-full px-3 py-2 border rounded mb-4"
          onChange={(e) => setCaseNumber(e.target.value)}
          required
        />
        <button 
        type="submit"
        className="px-4 py-2  bg-blue-600 text-white rounded"

        >Proceed</button>
      </form>
    
    </div>
  );
};




export default AccusedData;
