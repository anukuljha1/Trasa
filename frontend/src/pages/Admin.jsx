import { useEffect, useState } from 'react'
import VideoPlayer from '../components/VideoPlayer'
import { API } from '../utils/api'

export default function Admin() {
	const [results, setResults] = useState([])
	const [selected, setSelected] = useState(null)
	const [error, setError] = useState('')

	const refresh = () => {
		setError('')
		fetch(API + '/admin/results')
			.then(r => r.ok ? r.json() : Promise.reject(new Error('fetch failed')))
			.then(setResults)
			.catch(()=> setError('Unable to load results. Is backend running?'))
	}
	useEffect(refresh, [])

	const act = async (id, action) => {
		await fetch(API + `/admin/results/${id}/${action}` , { method: 'POST' })
		refresh()
	}

	return (
		<div className="grid gap-4 md:grid-cols-2">
			<div>
				<div className="flex items-center justify-between mb-3">
					<h1 className="text-2xl font-semibold">Admin Dashboard</h1>
					<button onClick={refresh} className="px-2 py-1 text-sm bg-gray-200 rounded">Refresh</button>
				</div>
				{error && <div className="text-red-600 text-sm mb-2">{error}</div>}
				<div className="space-y-2">
					{results.map(r => (
						<div key={r.id} className={`border rounded p-3 bg-white ${selected?.id===r.id?'ring-2 ring-indigo-500':''}`}>
							<div className="flex items-center justify-between">
								<div>
									<div className="font-medium">{r.name} ({r.email})</div>
									<div className="text-sm text-gray-600">{r.test_type} • {r.status}</div>
								</div>
								<div className="flex gap-2">
									<button onClick={()=>setSelected(r)} className="px-2 py-1 text-sm bg-gray-800 text-white rounded">View</button>
									<button onClick={()=>act(r.id,'accept')} className="px-2 py-1 text-sm bg-green-600 text-white rounded">Accept</button>
									<button onClick={()=>act(r.id,'reject')} className="px-2 py-1 text-sm bg-red-600 text-white rounded">Reject</button>
								</div>
							</div>
							<pre className="text-xs mt-2 whitespace-pre-wrap">{r.metrics_json}</pre>
						</div>
					))}
					{results.length===0 && !error && <div className="text-gray-500 bg-white border rounded p-10 text-center">No submissions.</div>}
				</div>
			</div>
			<div>
				{selected ? (
					<div className="space-y-2">
						<h2 className="text-xl font-semibold">Review</h2>
						{selected.video_path ? (
							<div className="bg-white border rounded p-3">
								<VideoPlayer src={`${API.replace(/\/$/, '')}/uploads/${selected.video_path}`} />
							</div>
						) : (
							<div className="text-gray-500 bg-white border rounded p-10 text-center">No video uploaded.</div>
						)}
					</div>
				) : (
					<div className="text-gray-500 bg-white border rounded p-10 text-center">Select a submission to view.</div>
				)}
			</div>
		</div>
	)
}
