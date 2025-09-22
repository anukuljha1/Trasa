import { useState, useEffect } from 'react'
import CameraRecorder from '../components/CameraRecorder'
import VideoPlayer from '../components/VideoPlayer'
import { API } from '../utils/api'

export default function RecordTest() {
	const [blob, setBlob] = useState(null)
	const [url, setUrl] = useState('')
	const [testType, setTestType] = useState('pushup')
	const [analysisResult, setAnalysisResult] = useState(null)
	const [busy, setBusy] = useState(false)
	const [msg, setMsg] = useState('')
	const [videoId, setVideoId] = useState(null)
	const [supportedExercises, setSupportedExercises] = useState([])

	useEffect(() => {
		// Load supported exercises
		fetch(API + '/ml/supported-exercises')
			.then(r => r.json())
			.then(data => setSupportedExercises(data.exercises))
			.catch(e => console.error('Failed to load exercises:', e))
	}, [])

const [durationMs, setDurationMs] = useState(0)
const onStop = async (b, u, dMs) => {
	setBlob(b); setUrl(u); setDurationMs(dMs||0); setAnalysisResult(null); setMsg('Ready to analyze')
}

	const analyze = async () => {
		if (!blob) { setMsg('Record or upload a video first'); return }
		setBusy(true); setMsg('Uploading video for analysis...')
		
		try {
			// Upload video for analysis
			const formData = new FormData()
			const filename = blob.type?.includes('mp4') ? 'recording.mp4' : (blob.name || 'recording.webm')
			formData.append('file', blob, filename)
			
			const response = await fetch(API + '/ml/analyze-video', {
				method: 'POST',
				body: formData
			})
			
			if (!response.ok) {
				throw new Error('Failed to upload video')
			}
			
			const result = await response.json()
			setVideoId(result.video_id)
			setMsg('Video uploaded, analyzing...')
			
			// Poll for results
			await pollAnalysisResults(result.video_id)
			
		} catch (e) {
			console.error('Analysis error:', e)
			setMsg('Failed to analyze video: ' + e.message)
		} finally {
			setBusy(false)
		}
	}

	const pollAnalysisResults = async (videoId) => {
		const maxAttempts = 30 // 30 seconds timeout
		let attempts = 0
		
		const poll = async () => {
			try {
				console.log(`Polling for results, attempt ${attempts + 1}`)
				const response = await fetch(API + `/ml/analysis/${videoId}`)
				const result = await response.json()
				
				console.log('Poll result:', result)
				
				if (result.status === 'completed') {
					console.log('Analysis completed:', result.results)
					setAnalysisResult(result.results)
					setMsg('Analysis complete! Check the results below.')
					return
				} else if (result.status === 'failed') {
					setMsg('Analysis failed: ' + result.error)
					return
				} else if (attempts < maxAttempts) {
					attempts++
					setMsg(`Analyzing... (${attempts}/${maxAttempts})`)
					setTimeout(poll, 1000)
				} else {
					setMsg('Analysis timeout - please try again')
				}
			} catch (e) {
				console.error('Polling error:', e)
				setMsg('Failed to get analysis results: ' + e.message)
			}
		}
		
		poll()
	}

	const submit = async () => {
		if (!blob || !analysisResult) { setMsg('Analyze before submitting'); return }
		setMsg('Submitting results...')
		
		try {
			const form = new FormData()
			form.append('athlete_email', localStorage.getItem('email') || '')
			form.append('test_type', testType)
			form.append('metrics_json', JSON.stringify(analysisResult))
			form.append('video', blob, (blob.type?.includes('mp4') ? 'recording.mp4' : 'recording.webm'))
			
			const response = await fetch(API + '/results', { 
				method: 'POST', 
				body: form 
			})
			
			setMsg(response.ok ? 'Results submitted successfully!' : 'Submit failed')
		} catch (e) {
			setMsg('Failed to submit: ' + e.message)
		}
	}

	return (
		<div className="grid gap-4 md:grid-cols-2">
			<div className="space-y-3">
				<h1 className="text-2xl font-semibold">Record Test</h1>
				<p className="text-sm text-gray-600">Use Chrome/Edge for best recording support. If recording is unsupported, upload a video file instead.</p>
				<div className="flex items-center gap-2">
					<label className="text-sm text-gray-600">Exercise:</label>
					<select className="border rounded p-2" value={testType} onChange={e=>setTestType(e.target.value)}>
						{supportedExercises.map(exercise => (
							<option key={exercise} value={exercise}>
								{exercise.charAt(0).toUpperCase() + exercise.slice(1)}
							</option>
						))}
					</select>
				</div>
				<div className="bg-white border rounded p-3">
				<CameraRecorder onStop={onStop} />
				</div>
			{durationMs > 0 && (
				<div className="text-xs text-gray-600">Recorded duration: {(durationMs/1000).toFixed(1)}s</div>
			)}
				<div className="flex gap-2">
					<button onClick={analyze} disabled={!url || busy} className="px-3 py-2 bg-indigo-600 text-white rounded disabled:opacity-50">
						{busy ? 'Analyzing...' : 'Analyze'}
					</button>
					<button onClick={submit} disabled={!analysisResult} className="px-3 py-2 bg-green-600 text-white rounded disabled:opacity-50">Submit</button>
					<button 
						onClick={() => {
							// Test with realistic results
							const testResult = {
								final_counts: { pushup: 0, situp: 0, jump: 0 },
								total_frames: 0,
								detected_exercise: null,
								form_score: 0,
								frame_results: [],
								analysis_quality: 'No Analysis',
								pose_detection_rate: 0
							}
							setAnalysisResult(testResult)
							setMsg('Analysis reset - record a video to see real results!')
						}}
						className="px-3 py-2 bg-yellow-600 text-white rounded text-sm"
					>
						Reset Analysis
					</button>
				</div>
				{msg && <div className="text-sm">{msg}</div>}
			</div>
			<div className="space-y-3">
				<h2 className="text-xl font-semibold">Preview</h2>
				{url ? (
					<div className="bg-white border rounded p-3">
						<VideoPlayer src={url} />
					</div>
				) : (
					<div className="text-gray-500 bg-white border rounded p-10 text-center">Record or upload to see a preview.</div>
				)}
				{analysisResult && (
					<div className="bg-white border rounded-lg p-4 shadow-sm">
						<div className="flex items-center justify-between mb-4">
							<h3 className="text-lg font-semibold text-gray-900">🎯 Analysis Results</h3>
							<div className="flex gap-2">
								<div className="text-sm text-green-600 bg-green-50 px-2 py-1 rounded">
									✅ Complete
								</div>
								<div className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded">
									{analysisResult.analysis_quality || 'Real Analysis'}
								</div>
							</div>
						</div>
						
						{/* Main Results */}
						<div className="grid grid-cols-2 gap-4 mb-4">
							<div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
								<div className="text-sm text-blue-600 font-medium">Push-ups</div>
								<div className="text-2xl font-bold text-blue-800">{analysisResult.final_counts?.pushup || 0}</div>
							</div>
							<div className="bg-green-50 p-3 rounded-lg border border-green-200">
								<div className="text-sm text-green-600 font-medium">Sit-ups</div>
								<div className="text-2xl font-bold text-green-800">{analysisResult.final_counts?.situp || 0}</div>
							</div>
							<div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
								<div className="text-sm text-purple-600 font-medium">Jumps</div>
								<div className="text-2xl font-bold text-purple-800">{analysisResult.final_counts?.jump || 0}</div>
							</div>
							<div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
								<div className="text-sm text-gray-600 font-medium">Total Frames</div>
								<div className="text-2xl font-bold text-gray-800">{analysisResult.total_frames || 0}</div>
							</div>
						</div>

						{/* Exercise Details */}
						{analysisResult.detected_exercise && (
							<div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
								<div className="flex items-center gap-2">
									<span className="text-yellow-600 font-medium">Detected Exercise:</span>
									<span className="text-yellow-800 font-semibold capitalize">
										{analysisResult.detected_exercise}
									</span>
								</div>
								<div className="flex items-center gap-4 mt-2">
									{analysisResult.form_score && (
										<div className="flex items-center gap-2">
											<span className="text-yellow-600 text-sm">Form Score:</span>
											<span className="text-yellow-800 font-semibold">{analysisResult.form_score}%</span>
										</div>
									)}
									{analysisResult.pose_detection_rate && (
										<div className="flex items-center gap-2">
											<span className="text-yellow-600 text-sm">Pose Detection:</span>
											<span className="text-yellow-800 font-semibold">{analysisResult.pose_detection_rate.toFixed(1)}%</span>
										</div>
									)}
								</div>
							</div>
						)}

						{/* Frame-by-Frame Results */}
						{analysisResult.frame_results && analysisResult.frame_results.length > 0 && (
							<div className="border-t pt-3">
								<h4 className="text-sm font-medium text-gray-700 mb-2">📊 Exercise Progression:</h4>
								<div className="space-y-1 max-h-32 overflow-y-auto">
									{analysisResult.frame_results.slice(-5).map((frame, i) => (
										<div key={i} className="flex justify-between items-center text-xs bg-gray-50 p-2 rounded">
											<span className="text-gray-600">Frame {frame.frame_number}</span>
											<span className="font-medium text-gray-800 capitalize">
												{frame.exercise || 'No exercise'}
											</span>
											<span className="text-blue-600 font-semibold">
												{frame.count} reps
											</span>
										</div>
									))}
								</div>
							</div>
						)}

						{/* Debug Info */}
						<div className="mt-3 p-2 bg-gray-100 rounded text-xs text-gray-600">
							<details>
								<summary className="cursor-pointer font-medium">Debug Info</summary>
								<pre className="mt-2 whitespace-pre-wrap text-xs">
									{JSON.stringify(analysisResult, null, 2)}
								</pre>
							</details>
						</div>
					</div>
				)}
			</div>
		</div>
	)
}
