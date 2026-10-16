import { students } from './students';
export const leaderboard = [...students].sort((a,b)=>b.points-a.points).map((student,index)=>({...student,name:student.nickname||'Student',rank:index+1}));
