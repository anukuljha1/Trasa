import { useState } from 'react'
import CameraRecorder from '../components/CameraRecorder'
import VideoPlayer from '../components/VideoPlayer'
import { initPoseModel, analyzeFrame, computeSitups, computeJump, detectCheat } from '../ml/pose'
import { API } from '../utils/api'

export default function RecordTest() {
	const [blob, setBlob] = useState(null)
	const [url, setUrl] = useState('')
	const [testType, setTestType] = useState('situps')
	const [metrics, setMetrics] = useState(null)
	const [busy, setBusy] = useState(false)
	const [msg, setMsg] = useState('')

	const onStop = async (b, u) => {
		setBlob(b); setUrl(u); setMetrics(null); setMsg('Ready to analyze')
	}

	const analyze = async () => {
		if (!url) { setMsg('Record or upload a video first'); return }
		setBusy(true); setMsg('Loading model...')
		try {
			const model = await initPoseModel()
			if (!model) { setMsg('Pose model not available in this browser'); setBusy(false); return }
			setMsg('Analyzing frames...')
			const video = document.createElement('video')
			video.src = url
			await video.play(); video.pause()
			const canvas = document.createElement('canvas')
			const ctx = canvas.getContext('2d')
			let samples = 0
			let allPoses = []
			for (let t = 0; t < video.duration; t += 0.2) {
				video.currentTime = t
				await new Promise(r => video.onseeked = r)
				canvas.width = video.videoWidth; canvas.height = video.videoHeight
				ctx.drawImage(video, 0, 0)
				const p = await analyzeFrame(canvas)
				allPoses.push(p)
				samples++
				if (samples > 200) break
			}
			let m = testType === 'situps' ? computeSitups(allPoses) : computeJump(allPoses)
			m.cheat = detectCheat(allPoses)
			setMetrics(m)
			setMsg('Analysis complete')
		} catch (e) {
			console.error(e)
			setMsg('Failed to analyze')
		} finally {
			setBusy(false)
		}
	}

	const submit = async () => {
		if (!blob || !metrics) { setMsg('Analyze before submitting'); return }
		setMsg('Uploading...')
		const form = new FormData()
		form.append('athlete_email', localStorage.getItem('email') || '')
		form.append('test_type', testType)
		form.append('metrics_json', JSON.stringify(metrics))
		form.append('video', blob, (blob.type?.includes('mp4') ? 'recording.mp4' : 'recording.webm'))
		const r = await fetch(API + '/results', { method: 'POST', body: form })
		setMsg(r.ok ? 'Submitted' : 'Submit failed')
	}

	return (
		<div className="grid gap-4 md:grid-cols-2">
			<div className="space-y-3">
				<h1 className="text-2xl font-semibold">Record Test</h1>
				<p className="text-sm text-gray-600">Use Chrome/Edge for best recording support. If recording is unsupported, upload a video file instead.</p>
				<div className="flex items-center gap-2">
					<label className="text-sm text-gray-600">Test:</label>
					<select className="border rounded p-2" value={testType} onChange={e=>setTestType(e.target.value)}>
						<option value="situps">Sit-ups</option>
						<option value="jump">Vertical Jump</option>
					</select>
				</div>
				<div className="bg-white border rounded p-3">
					<CameraRecorder onStop={onStop} />
				</div>
				<div className="flex gap-2">
					<button onClick={analyze} disabled={!url || busy} className="px-3 py-2 bg-indigo-600 text-white rounded disabled:opacity-50">Analyze</button>
					<button onClick={submit} disabled={!metrics} className="px-3 py-2 bg-green-600 text-white rounded disabled:opacity-50">Submit</button>
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
				{metrics && (
					<div className="bg-white border rounded p-3">
						<h3 className="font-medium mb-2">Metrics</h3>
						<pre className="text-xs whitespace-pre-wrap">{JSON.stringify(metrics, null, 2)}</pre>
					</div>
				)}
			</div>
		</div>
	)
}
