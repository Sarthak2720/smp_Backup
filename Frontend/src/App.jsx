import Navbar from './components/Navbar'
import LoginContainer from './components/LoginContainer'
import { Route, Routes } from 'react-router-dom'
import Stage2 from './components/Stage2'
import Stage1 from './components/Stage1'
import Stage3 from './components/Stage3'
import Chatbot from './components/Chatbot.jsx'
import Chatbutton from './components/Chatbutton.jsx'
import ErrorBoundary from './ErrorBoundary.jsx'
import AccusedData from './components/AccusedData'

const App = () => {
  return (
    <div className='flex flex-col items-center gap-20 h-screen'>
      {location.pathname !== '/chatbot' && (
        <>
          <Navbar />
          <Chatbutton />
        </>
      )}
      <div className='background absolute top-0 left-0 w-full h-screen -z-10'></div>
      <ErrorBoundary>
      <Routes>
        <Route exact path='/' Component={LoginContainer} />
        <Route exact path='/accusedData/:platform' Component={AccusedData} />
        {/* Updated Stage1 route to accept dynamic 'platform' parameter */}
        <Route exact path='/stage1/:platform' Component={Stage1} />
        <Route exact path='/stage2' Component={Stage2} />
        <Route exact path='/stage3' Component={Stage3} />
        <Route exact path='/chatbot' Component={Chatbot} />
      </Routes>
      </ErrorBoundary>
    </div>
  )
}

export default App
