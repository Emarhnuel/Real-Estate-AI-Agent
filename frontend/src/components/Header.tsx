import { Link, useNavigate, useLocation } from 'react-router-dom';

export function Header() {
    const navigate = useNavigate();
    const location = useLocation();

    const handleNavigation = (id: string) => {
        // If we represent the home page with '/', check if we are there
        if (location.pathname === '/') {
            document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        } else {
            // Navigate to home and pass the ID to scroll to
            navigate('/', { state: { scrollTo: id } });
        }
    };

    return (
        <nav className="fixed w-full top-0 z-50 bg-white transition-all duration-300 pt-4 pb-2">
            <div className="container mx-auto px-6 flex items-center justify-between">
                {/* Logo - Always links to Home */}
                <Link to="/" className="flex items-center gap-3 group cursor-pointer">
                    <div className="w-20 h-20 rounded-xl flex items-center justify-center overflow-hidden shadow-soft group-hover:scale-105 transition-transform bg-white border border-slate-100 p-1">
                        <img src="/logo.png" alt="Property Nova Logo" className="w-full h-full object-cover" />
                    </div>
                </Link>

                <div className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
                    <button
                        onClick={() => handleNavigation('features')}
                        className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors bg-transparent border-none cursor-pointer"
                    >
                        Features
                    </button>
                    <button
                        onClick={() => handleNavigation('how-it-works')}
                        className="text-sm font-medium text-brand-700 hover:text-brand-900 transition-colors bg-transparent border-none cursor-pointer"
                    >
                        How it Works
                    </button>
                    {/* Get Started - Always links to Analysis */}
                    <Link to="/analysis" className="text-sm font-bold text-brand-800 hover:text-gold-500 transition-colors border-b-2 border-gold-400">
                        Get Started
                    </Link>
                </div>

                <div className="w-24"></div>
            </div>
        </nav>
    );
}
