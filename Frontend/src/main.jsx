import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter} from 'react-router-dom';
import {ThemeProvider} from './context/ThemeContext';
import {AuthProvider} from './context/AuthContext';
import AppRoutes from './routes/AppRoutes';
import './styles/global.css';

createRoot(document.getElementById('root')).render(<StrictMode><BrowserRouter><ThemeProvider><AuthProvider><AppRoutes/></AuthProvider></ThemeProvider></BrowserRouter></StrictMode>);
