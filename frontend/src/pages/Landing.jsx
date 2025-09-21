import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { API } from '../utils/api'
import TRASALogo from '../components/TRASALogo'

export default function Landing() {
	const [stats, setStats] = useState(null)
	const [r, setR] = useState({ name: '', email: '', password: '' })
	const [l, setL] = useState({ email: '', password: '' })
	const [msg, setMsg] = useState('')
	const [showAuth, setShowAuth] = useState(false)
	const [authMode, setAuthMode] = useState('login') // 'login' or 'signup'
	const navigate = useNavigate()

	useEffect(() => {
		fetch(API + '/stats').then(r=>r.json()).then(setStats)
	}, [])

	const doRegister = async (e) => {
		e.preventDefault(); setMsg('')
		try {
			console.log('Attempting registration with:', r)
			const res = await fetch(API + '/mongo/register', {
				method: 'POST', 
				headers: { 'Content-Type': 'application/json' }, 
				body: JSON.stringify(r)
			})
			console.log('Registration response status:', res.status)
			
			if (res.ok) {
				setMsg('Registered successfully! You can now login.')
				// Clear form and switch to login
				setR({ name: '', email: '', password: '' })
				setTimeout(() => {
					setAuthMode('login')
					setMsg('')
				}, 2000)
			} else {
				const errorText = await res.text()
				console.log('Registration error response:', errorText)
				setMsg(`Registration failed - ${res.status}: ${errorText}`)
			}
		} catch (error) {
			console.error('Registration error:', error)
			setMsg(`Registration failed - ${error.message}`)
		}
	}
	
	const doLogin = async (e) => {
		e.preventDefault(); setMsg('')
		try {
			console.log('Attempting login with:', l)
			console.log('API URL:', API)
			const res = await fetch(API + '/mongo/login', {
				method: 'POST', 
				headers: { 'Content-Type': 'application/json' }, 
				body: JSON.stringify(l)
			})
			console.log('Response status:', res.status)
			console.log('Response ok:', res.ok)
			
			if (res.ok) {
				const j = await res.json()
				console.log('Login response:', j)
				localStorage.setItem('token', j.access_token)
				localStorage.setItem('email', l.email)
				localStorage.setItem('role', j.role || 'user')
				setMsg('Login successful! Redirecting...')
				setTimeout(() => {
					setShowAuth(false) // Close modal
					if (j.role === 'admin') {
						navigate('/admin')
					} else {
						navigate('/dashboard')
					}
				}, 1000)
			} else {
				const errorText = await res.text()
				console.log('Login error response:', errorText)
				setMsg(`Login failed - ${res.status}: ${errorText}`)
			}
		} catch (error) {
			console.error('Login error:', error)
			setMsg(`Login failed - ${error.message}`)
		}
	}

	return (
		<div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
			{/* Hero Section */}
			<section className="relative py-20 px-4">
				<div className="max-w-6xl mx-auto text-center">
					<div className="flex justify-center mb-8">
						<TRASALogo className="h-20" />
					</div>
					<h1 className="text-5xl font-bold text-gray-900 mb-6">
						TRASA Prototype
					</h1>
					<p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
						An AI-powered sports assessment platform that uses on-device machine learning 
						to analyze fitness tests like sit-ups and vertical jumps in real-time.
					</p>
					<div className="flex flex-col sm:flex-row gap-4 justify-center">
						<button 
							onClick={() => setShowAuth(true)}
							className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
						>
							Get Started
						</button>
						<button 
							onClick={() => document.getElementById('features-section').scrollIntoView({behavior: 'smooth'})}
							className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
						>
							Learn More
						</button>
					</div>
				</div>
			</section>

			{/* Features Section */}
			<section id="features-section" className="py-16 px-4 bg-white">
				<div className="max-w-6xl mx-auto">
					<h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
						Prototype Features
					</h2>
					<div className="grid md:grid-cols-3 gap-8">
						<div className="text-center p-6 rounded-lg bg-blue-50">
							<div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
								<svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
								</svg>
							</div>
							<h3 className="text-xl font-semibold mb-2">Real-time Analysis</h3>
							<p className="text-gray-600">Record fitness tests with your camera and get instant AI-powered analysis of your performance.</p>
						</div>
						<div className="text-center p-6 rounded-lg bg-green-50">
							<div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
								<svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
								</svg>
							</div>
							<h3 className="text-xl font-semibold mb-2">Performance Tracking</h3>
							<p className="text-gray-600">Track your progress over time with detailed metrics and performance analytics.</p>
						</div>
						<div className="text-center p-6 rounded-lg bg-purple-50">
							<div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
								<svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
								</svg>
							</div>
							<h3 className="text-xl font-semibold mb-2">Secure & Private</h3>
							<p className="text-gray-600">All analysis happens on your device. Your data stays private and secure.</p>
						</div>
					</div>
				</div>
			</section>

			{/* Stats Section */}
			<section className="py-16 px-4 bg-gray-50">
				<div className="max-w-6xl mx-auto">
					<h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
						Platform Statistics
					</h2>
					<div className="grid md:grid-cols-3 gap-8">
						<div className="bg-white rounded-lg p-8 text-center shadow-sm">
							<div className="text-4xl font-bold text-blue-600 mb-2">{stats?.sqlite?.athletes ?? '0'}</div>
							<div className="text-gray-600">Registered Athletes</div>
						</div>
						<div className="bg-white rounded-lg p-8 text-center shadow-sm">
							<div className="text-4xl font-bold text-green-600 mb-2">{stats?.sqlite?.results ?? '0'}</div>
							<div className="text-gray-600">Tests Completed</div>
						</div>
						<div className="bg-white rounded-lg p-8 text-center shadow-sm">
							<div className="text-4xl font-bold text-purple-600 mb-2">{stats?.mongo?.users ?? '0'}</div>
							<div className="text-gray-600">Active Users</div>
						</div>
					</div>
				</div>
			</section>

			{/* Authentication Modal */}
			{showAuth && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
					<div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
						<div className="p-6">
							<div className="flex justify-between items-center mb-6">
								<h2 className="text-2xl font-bold text-gray-900">Access TRASA</h2>
								<button 
									onClick={() => setShowAuth(false)}
									className="text-gray-400 hover:text-gray-600"
								>
									<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
									</svg>
								</button>
							</div>

							{/* Tab Navigation */}
							<div className="flex mb-6 border-b border-gray-200">
								<button
									onClick={() => setAuthMode('login')}
									className={`flex-1 py-2 px-4 text-center font-medium ${
										authMode === 'login' 
											? 'text-blue-600 border-b-2 border-blue-600' 
											: 'text-gray-500 hover:text-gray-700'
									}`}
								>
									Login
								</button>
								<button
									onClick={() => setAuthMode('signup')}
									className={`flex-1 py-2 px-4 text-center font-medium ${
										authMode === 'signup' 
											? 'text-blue-600 border-b-2 border-blue-600' 
											: 'text-gray-500 hover:text-gray-700'
									}`}
								>
									Sign Up
								</button>
							</div>

							{/* Demo Credentials */}
							<div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
								<p className="text-sm text-blue-800 font-medium mb-2">Demo Credentials:</p>
								<div className="grid grid-cols-2 gap-4 text-xs text-blue-700">
									<div>
										<p className="font-medium">User:</p>
										<p>Email: test@trasa.com</p>
										<p>Password: test123</p>
									</div>
									<div>
										<p className="font-medium">Admin:</p>
										<p>Email: admin@trasa.com</p>
										<p>Password: admin123</p>
									</div>
								</div>
							</div>

							{/* Login Form */}
							{authMode === 'login' && (
								<form onSubmit={doLogin} className="space-y-4">
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
										<input 
											className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
											placeholder="Enter your email" 
											value={l.email} 
											onChange={e=>setL({...l, email: e.target.value})} 
											required
										/>
									</div>
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
										<input 
											type="password" 
											className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
											placeholder="Enter your password" 
											value={l.password} 
											onChange={e=>setL({...l, password: e.target.value})} 
											required
										/>
									</div>
									<button 
										type="submit"
										className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
									>
										Login
									</button>
								</form>
							)}

							{/* Signup Form */}
							{authMode === 'signup' && (
								<form onSubmit={doRegister} className="space-y-4">
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
										<input 
											className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
											placeholder="Enter your full name" 
											value={r.name} 
											onChange={e=>setR({...r, name: e.target.value})} 
											required
										/>
									</div>
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
										<input 
											type="email"
											className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
											placeholder="Enter your email" 
											value={r.email} 
											onChange={e=>setR({...r, email: e.target.value})} 
											required
										/>
									</div>
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
										<input 
											type="password" 
											className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent" 
											placeholder="Create a password" 
											value={r.password} 
											onChange={e=>setR({...r, password: e.target.value})} 
											required
										/>
									</div>
									<button 
										type="submit"
										className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
									>
										Sign Up
									</button>
								</form>
							)}

							{msg && (
								<div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-center">
									<p className="text-green-800 text-sm">{msg}</p>
								</div>
							)}
						</div>
					</div>
				</div>
			)}
		</div>
	)
}
