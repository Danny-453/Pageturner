import { students } from './students';
export const leaderboard = [...students].sort((a,b)=>b.points-a.points).map((student,index)=>({...student,rank:index+1}));
