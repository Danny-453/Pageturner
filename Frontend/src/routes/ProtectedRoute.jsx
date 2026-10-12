import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
export default function ProtectedRoute(){const {isAuthenticated,loading}=useAuth();const location=useLocation();if(loading)return <div className="page-container"><div className="card empty">Checking your session…</div></div>;return isAuthenticated?<Outlet/>:<Navigate to="/login" replace state={{from:location.pathname}}/>;}
