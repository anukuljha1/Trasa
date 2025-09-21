export default function TRASALogo({ className = "h-8" }) {
  return (
    <div className={`flex items-center ${className}`}>
      <svg viewBox="0 0 200 60" className="h-full">
        {/* Background gradient */}
        <defs>
          <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1e3a8a" />
            <stop offset="100%" stopColor="#1e40af" />
          </linearGradient>
          <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#60a5fa" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
          <linearGradient id="pinkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#f472b6" />
            <stop offset="100%" stopColor="#ec4899" />
          </linearGradient>
        </defs>
        
        {/* Background */}
        <rect width="200" height="60" fill="url(#bgGradient)" rx="8" />
        
        {/* Speed lines */}
        <g opacity="0.3">
          <line x1="10" y1="15" x2="30" y2="15" stroke="#60a5fa" strokeWidth="2" />
          <line x1="10" y1="25" x2="40" y2="25" stroke="#10b981" strokeWidth="2" />
          <line x1="10" y1="35" x2="35" y2="35" stroke="#60a5fa" strokeWidth="2" />
          <line x1="10" y1="45" x2="25" y2="45" stroke="#10b981" strokeWidth="2" />
        </g>
        
        {/* TRASA Text */}
        <text x="20" y="40" fontSize="24" fontWeight="bold" fill="white" fontFamily="Arial, sans-serif">
          TRASA
        </text>
        
        {/* Stylized T with arcs */}
        <g transform="translate(20, 20)">
          {/* T vertical line with arcs */}
          <path d="M 0 0 L 0 20" stroke="white" strokeWidth="3" />
          <path d="M -8 0 L 8 0" stroke="white" strokeWidth="3" />
          
          {/* Blue arc */}
          <path d="M -6 -2 Q 2 8 6 12" stroke="url(#arcGradient)" strokeWidth="3" fill="none" />
          
          {/* Pink arc */}
          <path d="M -6 2 Q 2 12 6 16" stroke="url(#pinkGradient)" strokeWidth="3" fill="none" />
        </g>
        
        {/* Running figure */}
        <g transform="translate(120, 15)" opacity="0.8">
          {/* Head */}
          <circle cx="8" cy="8" r="6" fill="none" stroke="#60a5fa" strokeWidth="2" />
          {/* Earbuds */}
          <circle cx="4" cy="6" r="1" fill="#60a5fa" />
          <circle cx="12" cy="6" r="1" fill="#60a5fa" />
          
          {/* Body */}
          <path d="M 8 14 L 8 35" stroke="#60a5fa" strokeWidth="2" fill="none" />
          
          {/* Arms */}
          <path d="M 8 20 L 4 30" stroke="#60a5fa" strokeWidth="2" fill="none" />
          <path d="M 8 20 L 12 30" stroke="#60a5fa" strokeWidth="2" fill="none" />
          
          {/* Legs */}
          <path d="M 8 35 L 4 45" stroke="#60a5fa" strokeWidth="2" fill="none" />
          <path d="M 8 35 L 12 45" stroke="#60a5fa" strokeWidth="2" fill="none" />
          
          {/* Musculature lines */}
          <path d="M 6 18 L 10 18" stroke="#60a5fa" strokeWidth="1" opacity="0.6" />
          <path d="M 6 25 L 10 25" stroke="#60a5fa" strokeWidth="1" opacity="0.6" />
        </g>
      </svg>
    </div>
  )
}
