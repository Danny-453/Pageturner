import { Routes,Route } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import LandingPage from '../pages/public/LandingPage';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage';
import ResetPasswordPage from '../pages/auth/ResetPasswordPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import CoursesPage from '../pages/courses/CoursesPage';
import CourseDetailPage from '../pages/courses/CourseDetailPage';
import LessonPage from '../pages/lessons/LessonPage';
import PracticePage from '../pages/practice/PracticePage';
import LeaderboardPage from '../pages/leaderboard/LeaderboardPage';
import AchievementsPage from '../pages/achievements/AchievementsPage';
import ProfilePage from '../pages/profile/ProfilePage';
import SettingsPage from '../pages/profile/SettingsPage';
import AdminPage from '../pages/admin/AdminPage';
import AppLayout from '../layouts/AppLayout';
export default function AppRoutes(){return <Routes>
 <Route path="/" element={<LandingPage/>}/><Route path="/login" element={<LoginPage/>}/><Route path="/register" element={<RegisterPage/>}/><Route path="/forgot-password" element={<ForgotPasswordPage/>}/><Route path="/reset-password" element={<ResetPasswordPage/>}/>
 <Route element={<ProtectedRoute/>}><Route element={<AppLayout/>}>
  <Route path="/dashboard" element={<DashboardPage/>}/><Route path="/courses" element={<CoursesPage/>}/><Route path="/courses/:courseId" element={<CourseDetailPage/>}/><Route path="/courses/:courseId/lessons/:lessonId" element={<LessonPage/>}/><Route path="/practice" element={<PracticePage/>}/><Route path="/practice/:questionId" element={<PracticePage/>}/><Route path="/leaderboard" element={<LeaderboardPage/>}/><Route path="/leaderboard/course/:courseId" element={<LeaderboardPage/>}/><Route path="/leaderboard/level/:level" element={<LeaderboardPage/>}/><Route path="/achievements" element={<AchievementsPage/>}/><Route path="/profile" element={<ProfilePage/>}/><Route path="/settings" element={<SettingsPage/>}/><Route path="/admin" element={<AdminPage/>}/>
 </Route></Route>
 <Route path="*" element={<LandingPage/>}/>
 </Routes>}
