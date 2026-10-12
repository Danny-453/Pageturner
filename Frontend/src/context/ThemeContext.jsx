import { createContext, useContext, useEffect, useMemo, useState } from 'react';
const ThemeContext = createContext(null);
const STORAGE_KEY='pageturners-theme';
export function ThemeProvider({children}) {
 const [preference,setPreference]=useState(()=>localStorage.getItem(STORAGE_KEY)||'system');
 const [resolved,setResolved]=useState('light');
 useEffect(()=>{ localStorage.setItem(STORAGE_KEY,preference); const media=window.matchMedia('(prefers-color-scheme: dark)'); const apply=()=>setResolved(preference==='system'?(media.matches?'dark':'light'):preference); apply(); media.addEventListener('change',apply); return()=>media.removeEventListener('change',apply); },[preference]);
 useEffect(()=>{document.documentElement.dataset.theme=resolved;},[resolved]);
 const value=useMemo(()=>({preference,setPreference,resolved}),[preference,resolved]);
 return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
export const useTheme=()=>useContext(ThemeContext);
