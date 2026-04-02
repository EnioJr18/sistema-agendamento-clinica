import { Navigate, Outlet, useLocation } from 'react-router-dom';

function hasToken(): boolean {
  const token = localStorage.getItem('token');
  return typeof token === 'string' && token.trim().length > 0;
}

export default function RequireAuth() {
  const location = useLocation();

  if (!hasToken()) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
