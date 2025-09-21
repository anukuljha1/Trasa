import { Link, useNavigate } from 'react-router-dom'
import TRASALogo from './TRASALogo'

export default function Navbar() {
	const navigate = useNavigate()
	const email = typeof localStorage !== 'undefined' ? localStorage.getItem('email') : null
	const role = typeof localStorage !== 'undefined' ? localStorage.getItem('role') : null

	const logout = () => {
		localStorage.removeItem('token')
		localStorage.removeItem('email')
		localStorage.removeItem('role')
		navigate('/')
	}

	return (
		<header className="bg-white border-b shadow-sm">
			<div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
				<Link to="/" className="flex items-center">
					<TRASALogo className="h-8" />
				</Link>
				<nav className="flex items-center gap-4">
					{email ? (
						<>
							{role === 'admin' ? (
								<>
									<Link to="/admin" className="text-gray-700 hover:text-blue-600 transition-colors">Admin Panel</Link>
									<Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">User View</Link>
								</>
							) : (
								<>
									<Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition-colors">Dashboard</Link>
									<Link to="/record" className="text-gray-700 hover:text-blue-600 transition-colors">Record Test</Link>
									<Link to="/profile" className="text-gray-700 hover:text-blue-600 transition-colors">Profile</Link>
								</>
							)}
							<div className="flex items-center gap-2 ml-4">
								<span className="text-sm text-gray-600">{email}</span>
								{role === 'admin' && (
									<span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">Admin</span>
								)}
								<button 
									onClick={logout} 
									className="px-3 py-1.5 rounded bg-gray-900 text-white hover:bg-gray-800 transition-colors"
								>
									Logout
								</button>
							</div>
						</>
					) : (
						<Link to="/" className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors">
							Login
						</Link>
					)}
				</nav>
			</div>
		</header>
	)
}
