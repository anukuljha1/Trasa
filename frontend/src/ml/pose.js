let detector

async function loadPoseDetectionFromCDN() {
	// Use ESM CDN for the model to avoid bundler resolution
	return await import('https://esm.sh/@tensorflow-models/pose-detection@3')
}

export async function initPoseModel() {
	if (detector) return detector
	try {
		// Ensure TFJS is loaded (CDN)
		await import('https://esm.sh/@tensorflow/tfjs@4')
		const poseDetection = await loadPoseDetectionFromCDN()
		detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, { modelType: 'Lightning' })
		return detector
	} catch (e) {
		console.warn('pose model load failed, using null detector', e)
		return null
	}
}

export async function analyzeFrame(canvas) {
	if (!detector) await initPoseModel()
	if (!detector) return null
	try {
		const poses = await detector.estimatePoses(canvas)
		return poses[0] || null
	} catch (_) {
		return null
	}
}

export function computeSitups(poses) {
	let count = 0
	let prevUp = false
	for (const p of poses) {
		if (!p || !p.keypoints) continue
		const nose = p.keypoints[0]
		const hip = p.keypoints[p.keypoints.length - 1]
		if (!nose || !hip) continue
		const up = (nose.y + 20) < hip.y
		if (up && !prevUp) count++
		prevUp = up
	}
	return { reps: Math.max(0, count - 1) }
}

export function computeJump(poses) {
	let minY = Infinity, maxY = -Infinity
	for (const p of poses) {
		if (!p || !p.keypoints) continue
		const hip = p.keypoints[p.keypoints.length - 1]
		if (!hip) continue
		minY = Math.min(minY, hip.y)
		maxY = Math.max(maxY, hip.y)
	}
	const px = (maxY - minY)
	return { peakDisplacementPx: isFinite(px) ? px : 0 }
}

export function detectCheat(poses) {
	let duplicates = 0
	let prev
	for (const p of poses) {
		const sig = JSON.stringify((p?.keypoints||[]).map(k=>[Math.round(k.x||0), Math.round(k.y||0)]))
		if (sig === prev) duplicates++
		prev = sig
	}
	return { duplicateFrames: duplicates > 10 }
}
