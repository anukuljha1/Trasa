import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children, requireAdmin = false }) {
	const token = localStorage.getItem('token')
	const role = localStorage.getItem('role')
	
	if (!token) {
		return <Navigate to="/" replace />
	}
	
	if (requireAdmin && role !== 'admin') {
		return <Navigate to="/dashboard" replace />
	}
	
	return children
}
