import { useState } from 'react'
import { apiRegister } from '../utils/api'
import { Link, useNavigate } from 'react-router-dom'

export default function Register() {
	const [name, setName] = useState('')
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [msg, setMsg] = useState('')
	const navigate = useNavigate()

	const onSubmit = async (e) => {
		e.preventDefault()
		setMsg('')
		try {
			await apiRegister({ name, email, password })
			setMsg('Registered. You can login now.')
			setTimeout(()=>navigate('/login'), 700)
		} catch (e) {
			setMsg('Registration failed')
		}
	}

	return (
		<div className="max-w-md mx-auto">
			<div className="bg-white border rounded-lg shadow p-6">
				<h1 className="text-2xl font-semibold mb-4">Register</h1>
				{msg && <div className="text-sm mb-3">{msg}</div>}
				<form onSubmit={onSubmit} className="space-y-3">
					<input className="w-full border rounded p-2" placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />
					<input className="w-full border rounded p-2" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
					<input type="password" className="w-full border rounded p-2" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
					<button className="w-full bg-green-600 hover:bg-green-700 text-white rounded p-2">Register</button>
				</form>
				<p className="text-sm mt-3">Have an account? <Link className="text-blue-600" to="/login">Login</Link></p>
			</div>
		</div>
	)
}
