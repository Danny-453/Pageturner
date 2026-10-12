import { createContext,useContext,useEffect,useMemo,useState } from 'react';
import { login as loginService, register as registerService, logout as logoutService, getCurrentUser } from '../services/authService';
import { API_ENABLED, AUTH_TOKEN_KEY } from '../services/api';
const AuthContext=createContext(null);
export function AuthProvider({children}) {
 const [user,setUser]=useState(()=>{try{return JSON.parse(localStorage.getItem('pageturners-user'))||null}catch{return null}});
 const [loading,setLoading]=useState(()=>API_ENABLED&&Boolean(localStorage.getItem(AUTH_TOKEN_KEY)));
 useEffect(()=>{if(user)localStorage.setItem('pageturners-user',JSON.stringify(user));else localStorage.removeItem('pageturners-user')},[user]);
 useEffect(()=>{
  if(!API_ENABLED||!localStorage.getItem(AUTH_TOKEN_KEY))return;
  let active=true;
  getCurrentUser().then((currentUser)=>{if(active)setUser(currentUser)}).catch((error)=>{
   if(active&&error.message.includes('(401)')){localStorage.removeItem(AUTH_TOKEN_KEY);setUser(null)}
  }).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[]);
 const login=async(email,password)=>{setLoading(true);try{const result=await loginService(email,password);setUser(result.user);return result.user}finally{setLoading(false)}};
 const register=async(payload)=>{setLoading(true);try{const result=await registerService(payload);setUser(result.user);return result.user}finally{setLoading(false)}};
 const logout=async()=>{await logoutService();setUser(null)};
 return <AuthContext.Provider value={useMemo(()=>({user,loading,isAuthenticated:Boolean(user),login,register,logout}),[user,loading])}>{children}</AuthContext.Provider>;
}
export const useAuth=()=>useContext(AuthContext);
