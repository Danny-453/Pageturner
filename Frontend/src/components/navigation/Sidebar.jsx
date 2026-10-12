import {NavLink} from 'react-router-dom';
import {NAV_ITEMS} from '../../config/app';
import Icon from '../common/Icon';
import Logo from '../common/Logo';
import {useAuth} from '../../context/AuthContext';
export default function Sidebar({open,onClose}){const {user}=useAuth();return <aside id="app-sidebar" className={`sidebar ${open?'sidebar-open':''}`}><div className="sidebar-brand"><Logo className="sidebar-logo"/></div><nav className="sidebar-nav" aria-label="Student navigation">{NAV_ITEMS.map(item=><NavLink key={item.path} to={item.path} onClick={onClose} className={({isActive})=>isActive?'nav-link active':'nav-link'}><Icon name={item.icon}/><span>{item.label}</span></NavLink>)}{user?.role==='admin'&&<NavLink to="/admin" onClick={onClose} className={({isActive})=>isActive?'nav-link active':'nav-link'}><Icon name="settings"/><span>Manage content</span></NavLink>}</nav><div className="sidebar-bottom"><NavLink to="/settings" className="nav-link" onClick={onClose}><Icon name="settings"/><span>Settings</span></NavLink><div className="sidebar-note"><strong>Keep learning.</strong><span>Small sessions add up.</span></div></div></aside>}
