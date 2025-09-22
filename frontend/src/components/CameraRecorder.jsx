import { useEffect, useRef, useState } from 'react'
import { initPoseModel, analyzeFrame, computeSitups, computeJump } from '../ml/pose'

const CANDIDATE_MIMES = [
	'video/webm;codecs=vp9',
	'video/webm;codecs=vp8',
	'video/webm',
]

function getSupportedMime() {
	for (const m of CANDIDATE_MIMES) {
		if (window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(m)) return m
	}
	return ''
}

export default function CameraRecorder({ onStop }) {
	const videoRef = useRef(null)
	const mediaRecorderRef = useRef(null)
	const [recording, setRecording] = useState(false)
	const [error, setError] = useState('')
	const chunksRef = useRef([])
	const [hasMediaRecorder, setHasMediaRecorder] = useState(!!window.MediaRecorder)
	const startAtRef = useRef(0)
	const [elapsed, setElapsed] = useState(0)
	const timerRef = useRef(null)
	const [liveReps, setLiveReps] = useState(0)
	const repTimerRef = useRef(null)
	const canvasRef = useRef(null)

	useEffect(() => {
		let stream
		;(async () => {
			try {
				if (!navigator.mediaDevices?.getUserMedia) {
					setError('Camera not supported in this browser.')
					return
				}
				stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
				if (videoRef.current) {
					videoRef.current.srcObject = stream
					await videoRef.current.play().catch(()=>{})
				}
			} catch (e) {
				setError('Unable to access camera. Please allow permissions.')
			}
		})()
		return () => {
			try {
				const s = videoRef.current?.srcObject
				s && s.getTracks().forEach(t => t.stop())
			} catch {}
		}
	}, [])

	const start = async () => {
		setError('')
		chunksRef.current = []
		try {
			const mimeType = getSupportedMime()
			mediaRecorderRef.current = new MediaRecorder(videoRef.current.srcObject, mimeType ? { mimeType } : undefined)
			mediaRecorderRef.current.ondataavailable = (e) => { if (e.data && e.data.size) chunksRef.current.push(e.data) }
			mediaRecorderRef.current.onstop = () => {
				const type = (mimeType || 'video/webm')
				const blob = new Blob(chunksRef.current, { type })
				const durationMs = Math.max(0, Date.now() - startAtRef.current)
				onStop && onStop(blob, URL.createObjectURL(blob), durationMs)
			}
			mediaRecorderRef.current.start(250)
			setRecording(true)
			startAtRef.current = Date.now()
			setElapsed(0)
			clearInterval(timerRef.current)
			timerRef.current = setInterval(() => {
				setElapsed(Math.floor((Date.now() - startAtRef.current) / 1000))
			}, 250)
			// start lightweight live rep counter loop (~5 FPS)
			try { await initPoseModel() } catch {}
			clearInterval(repTimerRef.current)
			repTimerRef.current = setInterval(async () => {
				try {
					const video = videoRef.current
					if (!video) return
					// draw current frame to an offscreen canvas for pose estimation
					let canvas = canvasRef.current
					if (!canvas) {
						canvas = document.createElement('canvas')
						canvasRef.current = canvas
					}
					canvas.width = video.videoWidth || 320
					canvas.height = video.videoHeight || 240
					const ctx = canvas.getContext('2d')
					ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
					const pose = await analyzeFrame(canvas)
					if (!pose) return
					// simple heuristic: use situp or jump counter preview
					// choose metric by vertical hip movement; if small -> situp, else jump
					const res = computeSitups([pose])
					const jump = computeJump([pose])
					const val = Math.max(res.reps || 0, (jump.peakDisplacementPx||0) > 20 ? 0 : 0)
					setLiveReps(prev => Math.max(prev, val))
				} catch {}
			}, 200)
		} catch (e) {
			setError('Recording not supported in this browser. Use the upload fallback below.')
			setHasMediaRecorder(false)
		}
	}

	const stop = () => {
		try { mediaRecorderRef.current?.stop() } catch {}
		setRecording(false)
		clearInterval(timerRef.current)
		clearInterval(repTimerRef.current)
	}

	const onFile = async (e) => {
		const file = e.target.files?.[0]
		if (!file) return
		onStop && onStop(file, URL.createObjectURL(file))
	}

	return (
		<div className="space-y-2">
			<video ref={videoRef} className="w-full bg-black" playsInline muted />
			{hasMediaRecorder ? (
				<div className="flex gap-2">
					<button onClick={start} disabled={recording} className="px-3 py-2 bg-red-600 text-white rounded disabled:opacity-50">Start</button>
					<button onClick={stop} disabled={!recording} className="px-3 py-2 bg-gray-800 text-white rounded disabled:opacity-50">Stop</button>
				</div>
			) : (
				<div className="space-y-2">
					<label className="block text-sm text-gray-600">Upload a video (fallback)</label>
					<input type="file" accept="video/*" onChange={onFile} />
				</div>
			)}
			{recording && (
				<div className="text-xs text-gray-200 bg-gray-900 inline-block px-2 py-1 rounded">
					Recording... {elapsed}s • Reps: {liveReps}
				</div>
			)}
			{error && <div className="text-sm text-red-600">{error}</div>}
		</div>
	)
}
