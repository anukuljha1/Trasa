import { useEffect, useRef, useState } from 'react'

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

	const start = () => {
		setError('')
		chunksRef.current = []
		try {
			const mimeType = getSupportedMime()
			mediaRecorderRef.current = new MediaRecorder(videoRef.current.srcObject, mimeType ? { mimeType } : undefined)
			mediaRecorderRef.current.ondataavailable = (e) => { if (e.data && e.data.size) chunksRef.current.push(e.data) }
			mediaRecorderRef.current.onstop = () => {
				const type = (mimeType || 'video/webm')
				const blob = new Blob(chunksRef.current, { type })
				onStop && onStop(blob, URL.createObjectURL(blob))
			}
			mediaRecorderRef.current.start(250)
			setRecording(true)
		} catch (e) {
			setError('Recording not supported in this browser. Use the upload fallback below.')
			setHasMediaRecorder(false)
		}
	}

	const stop = () => {
		try { mediaRecorderRef.current?.stop() } catch {}
		setRecording(false)
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
			{error && <div className="text-sm text-red-600">{error}</div>}
		</div>
	)
}
