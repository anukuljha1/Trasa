import { useEffect, useState } from 'react'
import { API } from '../utils/api'

export default function Landing() {
	const [stats, setStats] = useState(null)
	const [r, setR] = useState({ name: '', email: '', password: '' })
	const [l, setL] = useState({ email: '', password: '' })
	const [msg, setMsg] = useState('')

	useEffect(() => {
		fetch(API + '/stats').then(r=>r.json()).then(setStats)
	}, [])

	const doRegister = async (e) => {
		e.preventDefault(); setMsg('')
		const res = await fetch(API + '/mongo/register', {
			method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(r)
		})
		setMsg(res.ok ? 'Registered (MongoDB). Now login below.' : 'Register failed')
	}
	const doLogin = async (e) => {
		e.preventDefault(); setMsg('')
		const res = await fetch(API + '/mongo/login', {
			method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(l)
		})
		if (res.ok) {
			const j = await res.json()
			localStorage.setItem('token', j.access_token)
			localStorage.setItem('email', l.email)
			setMsg('Logged in. Go to Dashboard.')
		} else {
			setMsg('Login failed')
		}
	}

	return (
		<div className="space-y-8">
			<section className="text-center py-10 bg-white border rounded">
				<h1 className="text-3xl font-bold">TRASA: Train Smarter with On-Device Assessments</h1>
				<p className="text-gray-600 mt-2">AI-powered sit-ups and jump analysis. Record, analyze, and improve.</p>
				<div className="mt-4 flex justify-center gap-3">
					<a href="/register" className="px-4 py-2 rounded bg-blue-600 text-white">Get Started</a>
					<a href="/record" className="px-4 py-2 rounded bg-gray-900 text-white">Try a Demo</a>
				</div>
			</section>
			<section className="grid md:grid-cols-3 gap-4">
				<div className="bg-white border rounded p-4 text-center">
					<div className="text-2xl font-semibold">{stats?.sqlite?.athletes ?? '—'}</div>
					<div className="text-gray-600">Athletes (SQLite)</div>
				</div>
				<div className="bg-white border rounded p-4 text-center">
					<div className="text-2xl font-semibold">{stats?.sqlite?.results ?? '—'}</div>
					<div className="text-gray-600">Results (SQLite)</div>
				</div>
				<div className="bg-white border rounded p-4 text-center">
					<div className="text-2xl font-semibold">{stats?.mongo?.users ?? '—'}</div>
					<div className="text-gray-600">Users (MongoDB)</div>
				</div>
			</section>
			<section className="grid md:grid-cols-2 gap-4">
				<div className="bg-white border rounded p-4">
					<h2 className="text-xl font-semibold mb-2">Quick Sign Up (MongoDB)</h2>
					<form onSubmit={doRegister} className="space-y-3">
						<input className="w-full border rounded p-2" placeholder="Name" value={r.name} onChange={e=>setR({...r, name: e.target.value})} />
						<input className="w-full border rounded p-2" placeholder="Email" value={r.email} onChange={e=>setR({...r, email: e.target.value})} />
						<input type="password" className="w-full border rounded p-2" placeholder="Password" value={r.password} onChange={e=>setR({...r, password: e.target.value})} />
						<button className="px-3 py-2 bg-green-600 text-white rounded">Sign Up</button>
					</form>
				</div>
				<div className="bg-white border rounded p-4">
					<h2 className="text-xl font-semibold mb-2">Quick Login (MongoDB)</h2>
					<form onSubmit={doLogin} className="space-y-3">
						<input className="w-full border rounded p-2" placeholder="Email" value={l.email} onChange={e=>setL({...l, email: e.target.value})} />
						<input type="password" className="w-full border rounded p-2" placeholder="Password" value={l.password} onChange={e=>setL({...l, password: e.target.value})} />
						<button className="px-3 py-2 bg-blue-600 text-white rounded">Login</button>
					</form>
				</div>
			</section>
			{msg && <div className="text-center text-sm">{msg}</div>}
		</div>
	)
}
