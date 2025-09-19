export const API = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) || 'http://127.0.0.1:8000'

export async function apiRegister(body) {
	const r = await fetch(API + '/register', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	})
	if (!r.ok) throw new Error('register failed')
	return r.json()
}

export async function apiLogin(body) {
	const r = await fetch(API + '/login', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	})
	if (!r.ok) throw new Error('login failed')
	return r.json()
}

export async function apiMongoRegister(body) {
	const r = await fetch(API + '/mongo/register', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	})
	if (!r.ok) throw new Error('mongo register failed')
	return r.json()
}

export async function apiMongoLogin(body) {
	const r = await fetch(API + '/mongo/login', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	})
	if (!r.ok) throw new Error('mongo login failed')
	return r.json()
}
