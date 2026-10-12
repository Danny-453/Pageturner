import { useTheme } from '../../context/ThemeContext';
import lightLogo from '../../assets/logo/pageturners-light-logo.png';
import darkLogo from '../../assets/logo/pageturners-dark-logo.png';
export default function Logo({className=''}){const {resolved}=useTheme();return <img className={className} src={resolved==='dark'?darkLogo:lightLogo} alt="PageTurners"/>}
