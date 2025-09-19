import { useEffect, useState } from 'react'
import { API } from '../utils/api'

export default function Profile() {
	const email = typeof localStorage !== 'undefined' ? localStorage.getItem('email') : ''
	const [name, setName] = useState('')
	const [best, setBest] = useState({})
	const [msg, setMsg] = useState('')

	useEffect(() => {
		if (!email) return
		fetch(`${API}/profile?email=${encodeURIComponent(email)}`)
			.then(r => r.json()).then(p => setName(p.name || ''))
		fetch(`${API}/profile/best?email=${encodeURIComponent(email)}`)
			.then(r => r.json()).then(setBest)
	}, [email])

	const save = async () => {
		setMsg('Saving...')
		const r = await fetch(`${API}/profile`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, name })
		})
		setMsg(r.ok ? 'Saved' : 'Save failed')
	}

	return (
		<div className="grid gap-4 md:grid-cols-2">
			<div className="bg-white border rounded p-4">
				<h1 className="text-2xl font-semibold mb-3">Profile</h1>
				<div className="space-y-3">
					<div>
						<label className="block text-sm text-gray-600">Email</label>
						<input className="w-full border rounded p-2 bg-gray-100" value={email} readOnly />
					</div>
					<div>
						<label className="block text-sm text-gray-600">Name</label>
						<input className="w-full border rounded p-2" value={name} onChange={e=>setName(e.target.value)} />
					</div>
					<button onClick={save} className="px-3 py-2 bg-blue-600 text-white rounded">Save</button>
					{msg && <div className="text-sm">{msg}</div>}
				</div>
			</div>
			<div className="bg-white border rounded p-4">
				<h2 className="text-xl font-semibold mb-2">Best Results</h2>
				<div className="space-y-2 text-sm">
					<div className="flex justify-between"><span>Sit-ups</span><span>{best?.situps?.reps ?? 0}</span></div>
					<div className="flex justify-between"><span>Vertical Jump (px)</span><span>{best?.jump?.peakDisplacementPx ?? 0}</span></div>
				</div>
			</div>
		</div>
	)
}
