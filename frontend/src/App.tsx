import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation, matchPath } from 'react-router-dom';
import Navbar from './components/navbar';
import Sidebar from './components/sidebar';
import Chat from './components/chat';
import Home from './components/home';

const AppContent: React.FC = () => {
  const location = useLocation();
  const showNavbarAndSidebar = ['/', '/chat/:chatId'].some((path) =>
    matchPath(path, location.pathname)
  );

  return (
    <div className='flex flex-col bg-gray-900 h-screen overflow-hidden'>
  {showNavbarAndSidebar && <Navbar />}
  <div className={`flex flex-row ${showNavbarAndSidebar ? 'mt-20' : ''} overflow-hidden`}>
    {showNavbarAndSidebar && (
      <>
        <div className='md:sticky absolute'>
          <Sidebar />
        </div>
      </>
    )}
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/chat/:chatId" element={<Chat />} />
    </Routes>
  </div>
</div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;
