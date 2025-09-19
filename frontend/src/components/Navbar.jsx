import { Link, useNavigate } from 'react-router-dom'

export default function Navbar() {
	const navigate = useNavigate()
	const email = typeof localStorage !== 'undefined' ? localStorage.getItem('email') : null

	const logout = () => {
		localStorage.removeItem('token')
		localStorage.removeItem('email')
		navigate('/login')
	}

	return (
		<header className="bg-white border-b">
			<div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
				<Link to="/" className="font-semibold text-lg">TRASA</Link>
				<nav className="flex items-center gap-4">
					<Link to="/dashboard" className="text-gray-700 hover:text-black">Dashboard</Link>
					<Link to="/record" className="text-gray-700 hover:text-black">Record</Link>
					<Link to="/admin" className="text-gray-700 hover:text-black">Admin</Link>
					<Link to="/profile" className="text-gray-700 hover:text-black">Profile</Link>
					{email ? (
						<button onClick={logout} className="ml-2 px-3 py-1.5 rounded bg-gray-900 text-white">Logout</button>
					) : (
						<Link to="/login" className="ml-2 px-3 py-1.5 rounded bg-blue-600 text-white">Login</Link>
					)}
				</nav>
			</div>
		</header>
	)
}
