import { useEffect, useState } from 'react'
import VideoPlayer from '../components/VideoPlayer'
import { API } from '../utils/api'

export default function Admin() {
	const [results, setResults] = useState([])
	const [selected, setSelected] = useState(null)
	const [error, setError] = useState('')
	const [stats, setStats] = useState(null)

	const refresh = () => {
		setError('')
		const token = (typeof window !== 'undefined' && localStorage.getItem('token')) || ''
		const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
		
		fetch(API + '/admin/results', { headers })
			.then(r => r.ok ? r.json() : Promise.reject(new Error(r.status)))
			.then(setResults)
			.catch((e)=> setError(e.message === '401' || e.message === '403' ? 'Unauthorized. Please log in as admin.' : 'Unable to load results. Is backend running?'))
		
		fetch(API + '/stats', { headers })
			.then(r => r.ok ? r.json() : Promise.reject(new Error(r.status)))
			.then(setStats)
			.catch(()=> {})
	}
	useEffect(refresh, [])

	const act = async (id, action) => {
		const token = (typeof window !== 'undefined' && localStorage.getItem('token')) || ''
		const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
		await fetch(API + `/admin/results/${id}/${action}` , { method: 'POST', headers })
		refresh()
	}

	const pendingCount = results.filter(r => r.status === 'pending').length
	const acceptedCount = results.filter(r => r.status === 'accepted').length
	const rejectedCount = results.filter(r => r.status === 'rejected').length

	return (
		<div className="space-y-6">
			{/* Admin Header */}
			<div className="bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg p-6">
				<h1 className="text-3xl font-bold mb-2">Admin Control Panel</h1>
				<p className="text-red-100">Manage user submissions and platform statistics</p>
			</div>

			{/* Stats Cards */}
			<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
				<div className="bg-white rounded-lg p-6 shadow-sm border">
					<div className="text-2xl font-bold text-blue-600">{stats?.sqlite?.athletes || 0}</div>
					<div className="text-gray-600">Total Athletes</div>
				</div>
				<div className="bg-white rounded-lg p-6 shadow-sm border">
					<div className="text-2xl font-bold text-yellow-600">{pendingCount}</div>
					<div className="text-gray-600">Pending Reviews</div>
				</div>
				<div className="bg-white rounded-lg p-6 shadow-sm border">
					<div className="text-2xl font-bold text-green-600">{acceptedCount}</div>
					<div className="text-gray-600">Accepted</div>
				</div>
				<div className="bg-white rounded-lg p-6 shadow-sm border">
					<div className="text-2xl font-bold text-red-600">{rejectedCount}</div>
					<div className="text-gray-600">Rejected</div>
				</div>
			</div>

			{/* Main Content */}
			<div className="grid gap-6 lg:grid-cols-2">
				{/* Submissions List */}
				<div className="bg-white rounded-lg shadow-sm border">
					<div className="p-6 border-b">
						<div className="flex items-center justify-between">
							<h2 className="text-xl font-semibold">Submissions Review</h2>
							<button 
								onClick={refresh} 
								className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
							>
								Refresh
							</button>
						</div>
					</div>
					<div className="p-6">
						{error && <div className="text-red-600 text-sm mb-4 p-3 bg-red-50 rounded">{error}</div>}
						<div className="space-y-3 max-h-96 overflow-y-auto">
							{results.map(r => (
								<div 
									key={r.id} 
									className={`border rounded-lg p-4 cursor-pointer transition-all ${
										selected?.id===r.id 
											? 'ring-2 ring-blue-500 bg-blue-50' 
											: 'hover:bg-gray-50'
									}`}
									onClick={()=>setSelected(r)}
								>
									<div className="flex items-center justify-between mb-2">
										<div>
											<div className="font-medium text-gray-900">{r.name}</div>
											<div className="text-sm text-gray-600">{r.email}</div>
										</div>
										<div className="flex items-center gap-2">
											<span className={`px-2 py-1 text-xs rounded-full ${
												r.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
												r.status === 'accepted' ? 'bg-green-100 text-green-800' :
												'bg-red-100 text-red-800'
											}`}>
												{r.status}
											</span>
											<span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
												{r.test_type}
											</span>
										</div>
									</div>
									<div className="text-xs text-gray-500 mb-2">
										Submitted: {new Date(r.created_at).toLocaleDateString()}
									</div>
									<div className="flex gap-2">
										<button 
											onClick={(e) => {e.stopPropagation(); act(r.id,'accept')}} 
											className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
										>
											Accept
										</button>
										<button 
											onClick={(e) => {e.stopPropagation(); act(r.id,'reject')}} 
											className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
										>
											Reject
										</button>
									</div>
								</div>
							))}
							{results.length===0 && !error && (
								<div className="text-center text-gray-500 py-8">
									<div className="text-4xl mb-2">📋</div>
									<div>No submissions to review</div>
								</div>
							)}
						</div>
					</div>
				</div>

				{/* Video Review */}
				<div className="bg-white rounded-lg shadow-sm border">
					<div className="p-6 border-b">
						<h2 className="text-xl font-semibold">Video Review</h2>
					</div>
					<div className="p-6">
						{selected ? (
							<div className="space-y-4">
								<div className="bg-gray-50 rounded-lg p-4">
									<h3 className="font-medium mb-2">Test Details</h3>
									<div className="text-sm space-y-1">
										<div><strong>Type:</strong> {selected.test_type}</div>
										<div><strong>Status:</strong> {selected.status}</div>
										<div><strong>Submitted:</strong> {new Date(selected.created_at).toLocaleString()}</div>
									</div>
								</div>
								
								{selected.video_path ? (
									<div className="bg-gray-50 rounded-lg p-4">
										<VideoPlayer src={`${API.replace(/\/$/, '')}/uploads/${selected.video_path}`} />
									</div>
								) : (
									<div className="text-center text-gray-500 py-8 bg-gray-50 rounded-lg">
										<div className="text-4xl mb-2">🎥</div>
										<div>No video uploaded</div>
									</div>
								)}
								
								<div className="bg-gray-50 rounded-lg p-4">
									<h3 className="font-medium mb-2">Metrics</h3>
									<pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-32">
										{selected.metrics_json}
									</pre>
								</div>
							</div>
						) : (
							<div className="text-center text-gray-500 py-12">
								<div className="text-4xl mb-2">👆</div>
								<div>Select a submission to review</div>
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	)
}
