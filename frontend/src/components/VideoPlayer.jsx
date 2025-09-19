import { useEffect, useRef } from 'react'

export default function VideoPlayer({ src, onFrame }) {
	const videoRef = useRef(null)
	const canvasRef = useRef(null)

	useEffect(() => {
		let raf
		const ctx = canvasRef.current.getContext('2d')
		const loop = () => {
			const v = videoRef.current
			if (v && !v.paused && !v.ended) {
				canvasRef.current.width = v.videoWidth
				canvasRef.current.height = v.videoHeight
				ctx.drawImage(v, 0, 0)
				onFrame && onFrame(canvasRef.current)
			}
			raf = requestAnimationFrame(loop)
		}
		raf = requestAnimationFrame(loop)
		return () => cancelAnimationFrame(raf)
	}, [onFrame])

	return (
		<div className="space-y-2">
			<video ref={videoRef} className="w-full bg-black" src={src} controls />
			<canvas ref={canvasRef} className="w-full" />
		</div>
	)
}
