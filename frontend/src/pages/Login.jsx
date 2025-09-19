import { useState } from 'react'
import { apiLogin, apiMongoLogin } from '../utils/api'
import { Link, useNavigate } from 'react-router-dom'

export default function Login() {
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState('')
	const [useMongo, setUseMongo] = useState(true)
	const navigate = useNavigate()

	const onSubmit = async (e) => {
		e.preventDefault()
		setError('')
		try {
			const res = useMongo ? await apiMongoLogin({ email, password }) : await apiLogin({ email, password })
			localStorage.setItem('token', res.access_token)
			localStorage.setItem('email', email)
			navigate('/dashboard')
		} catch (e) {
			setError('Invalid credentials or server unavailable')
		}
	}

	return (
		<div className="max-w-md mx-auto">
			<div className="bg-white border rounded-lg shadow p-6">
				<h1 className="text-2xl font-semibold mb-4">Login</h1>
				<div className="flex items-center gap-2 text-sm mb-3">
					<label className="text-gray-700">Provider:</label>
					<select className="border rounded p-1" value={useMongo? 'mongo':'sqlite'} onChange={e=>setUseMongo(e.target.value==='mongo')}>
						<option value="mongo">MongoDB</option>
						<option value="sqlite">SQLite</option>
					</select>
				</div>
				{error && <div className="text-red-600 text-sm mb-3">{error}</div>}
				<form onSubmit={onSubmit} className="space-y-3">
					<input className="w-full border rounded p-2" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
					<input type="password" className="w-full border rounded p-2" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
					<button className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded p-2">Login</button>
				</form>
				<p className="text-sm mt-3">No account? <Link className="text-blue-600" to="/register">Register</Link></p>
			</div>
		</div>
	)
}
