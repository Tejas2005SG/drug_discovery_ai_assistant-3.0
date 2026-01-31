import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/useAuthStore';
import { Toaster } from 'sonner';
import LoginPage from './components/login';
import SignUpPage from './components/sign-up';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import SettingsPage from './pages/SettingsPage';

import DrugDiscoveryPage from './pages/DrugDiscoveryPage';
import MoleculeViewerPage from './pages/MoleculeViewerPage';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { ResearchHistory } from './components/dashboard/ResearchHistory';
import { useThemeStore } from './store/useThemeStore';

function App() {
  const { authUser, checkAuth, isCheckingAuth } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  if (isCheckingAuth && !authUser) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={!authUser ? <LoginPage /> : <Navigate to="/dashboard" />} />
        <Route path="/signup" element={!authUser ? <SignUpPage /> : <Navigate to="/dashboard" />} />

        {/* Protected Dashboard Routes */}
        <Route path="/dashboard" element={authUser ? <DashboardLayout /> : <Navigate to="/login" />}>
          <Route index element={<DashboardPage />} />
          <Route path="research" element={<DrugDiscoveryPage />} />
          <Route path="research/:id" element={<DrugDiscoveryPage />} />
          <Route path="molecule-viewer" element={<MoleculeViewerPage />} />
          <Route path="history" element={<ResearchHistory />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <Toaster />
    </>
  );
}

export default App;
