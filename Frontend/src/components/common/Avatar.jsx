import { initials } from '../../utils/format';
export default function Avatar({name,size=40}){return <div style={{width:size,height:size,borderRadius:'50%',display:'grid',placeItems:'center',background:'var(--color-primary-light)',color:'var(--color-primary)',fontWeight:800,fontSize:size<40?12:14,flex:'0 0 auto'}}>{initials(name)}</div>}
