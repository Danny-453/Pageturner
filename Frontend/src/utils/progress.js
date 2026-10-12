import { learningLevels } from '../data/learningLevels';
export function getLearningLevel(correctAnswers){let current=learningLevels[0]; for(const level of learningLevels){if(correctAnswers>=level.threshold)current=level;} return current;}
export function percentage(value,total){return total?Math.round((value/total)*100):0;}
