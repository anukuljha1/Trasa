import React from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom'
import './styles.css'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import RecordTest from './pages/RecordTest.jsx'
import Admin from './pages/Admin.jsx'
import Profile from './pages/Profile.jsx'

function Layout() {
	return (
		<div className="min-h-screen bg-gray-50">
			<Navbar />
			<main className="max-w-6xl mx-auto p-4">
				<Outlet />
			</main>
		</div>
	)
}

const router = createBrowserRouter([
	{
		path: '/',
		element: <Layout />,
		children: [
			{ index: true, element: <Landing /> },
			{ 
				path: 'dashboard', 
				element: (
					<ProtectedRoute>
						<Dashboard />
					</ProtectedRoute>
				)
			},
			{ 
				path: 'record', 
				element: (
					<ProtectedRoute>
						<RecordTest />
					</ProtectedRoute>
				)
			},
			{ 
				path: 'admin', 
				element: (
					<ProtectedRoute requireAdmin={true}>
						<Admin />
					</ProtectedRoute>
				)
			},
			{ 
				path: 'profile', 
				element: (
					<ProtectedRoute>
						<Profile />
					</ProtectedRoute>
				)
			},
			{ path: 'login', element: <Login /> },
			{ path: 'register', element: <Register /> },
		],
	},
])

createRoot(document.getElementById('root')).render(
	<React.StrictMode>
		<RouterProvider router={router} />
	</React.StrictMode>
)
