import { useEffect, useState } from 'react'
import { API } from '../utils/api'

export default function Dashboard() {
	const [results, setResults] = useState([])
	const [error, setError] = useState('')
	useEffect(() => {
		const token = localStorage.getItem('token') || ''
		const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
		fetch(API + '/results/mine', { headers })
			.then(r => r.ok ? r.json() : Promise.reject(new Error(r.status)))
			.then(data => setResults(data||[]))
			.catch((e)=> setError(e.message === '401' || e.message === '403' ? 'Please login to view your results.' : 'Unable to load results. Is backend running?'))
	}, [])

	return (
		<div>
			<div className="flex justify-between items-center mb-4">
				<h1 className="text-2xl font-semibold">Athlete Dashboard</h1>
				<a className="px-3 py-2 rounded bg-indigo-600 text-white" href="/record">Record Test</a>
			</div>
			{error && <div className="text-red-600 text-sm mb-2">{error}</div>}
			<div className="grid gap-3">
				{results.map(r => (
					<div key={r.id} className="border rounded p-3 bg-white">
						<div className="text-sm text-gray-600">{r.test_type} • {r.status}</div>
						<pre className="text-xs mt-1 whitespace-pre-wrap">{r.metrics_json}</pre>
					</div>
				))}
				{results.length === 0 && !error && (
					<div className="text-center text-gray-500 bg-white border rounded p-10">No results yet. Record a test to see your metrics.</div>
				)}
			</div>
		</div>
	)
}
