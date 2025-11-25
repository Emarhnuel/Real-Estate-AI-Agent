import { FormEvent, useState } from 'react';

interface PropertySearchFormProps {
  onSubmit: (formData: PropertySearchData) => void;
  loading: boolean;
}

export interface PropertySearchData {
  purpose: string;
  location: string;
  bedrooms: number;
  maxBudget: number;
  bathrooms?: number;
  moveInDate?: string;
  leaseLength?: number;
  propertyType?: string;
  locationPriorities?: string;
}

export default function PropertySearchForm({ onSubmit, loading }: PropertySearchFormProps) {
  const [formData, setFormData] = useState<PropertySearchData>({
    purpose: 'rent',
    location: '',
    bedrooms: 2,
    maxBudget: 0,
    bathrooms: undefined,
    moveInDate: '',
    leaseLength: undefined,
    propertyType: '',
    locationPriorities: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    const newErrors: Record<string, string> = {};
    
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }
    
    if (formData.bedrooms < 1) {
      newErrors.bedrooms = 'At least 1 bedroom is required';
    }
    
    if (formData.maxBudget <= 0) {
      newErrors.maxBudget = 'Budget must be greater than 0';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    setErrors({});
    onSubmit(formData);
  };

  const handleChange = (field: keyof PropertySearchData, value: string | number | undefined) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="bg-[#1a1a1a] rounded-2xl shadow-[0_0_30px_rgba(255,107,0,0.3)] p-8 border-2 border-[#FF6B00]">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-[#FF6B00] mb-2 glitch" style={{ fontFamily: "'Creepster', cursive" }}>
          🎃 Summon Your Haunted Home
        </h2>
        <p className="text-[#E0E0E0]">
          Cast your spell below to conjure properties from the spirit realm
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Purpose - Required */}
        <div>
          <label className="block text-sm font-bold text-[#8B00FF] mb-2">
            🔮 Purpose <span className="text-[#8B0000]">*</span>
          </label>
          <select
            value={formData.purpose}
            onChange={(e) => handleChange('purpose', e.target.value)}
            disabled={loading}
            className="w-full px-4 py-3 border-2 border-[#8B00FF] rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="rent">🏚️ For Rent</option>
            <option value="buy">💀 For Sale/Buy</option>
            <option value="shortlet">👻 Shortlet</option>
          </select>
        </div>

        {/* Location - Required */}
        <div>
          <label className="block text-sm font-bold text-[#8B00FF] mb-2">
            📍 Haunted Location <span className="text-[#8B0000]">*</span>
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            placeholder="e.g., Lekki, Lagos"
            disabled={loading}
            className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed placeholder-[#E0E0E0]/40 ${
              errors.location ? 'border-[#8B0000]' : 'border-[#8B00FF]'
            }`}
          />
          {errors.location && (
            <p className="mt-1 text-sm text-[#8B0000]">💀 {errors.location}</p>
          )}
        </div>

        {/* Bedrooms and Bathrooms - Row */}
        <div className="grid md:grid-cols-2 gap-4">
          {/* Bedrooms - Required */}
          <div>
            <label className="block text-sm font-bold text-[#8B00FF] mb-2">
              🛏️ Bedrooms <span className="text-[#8B0000]">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.bedrooms}
              onChange={(e) => handleChange('bedrooms', parseInt(e.target.value) || 1)}
              disabled={loading}
              className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed ${
                errors.bedrooms ? 'border-[#8B0000]' : 'border-[#8B00FF]'
              }`}
            />
            {errors.bedrooms && (
              <p className="mt-1 text-sm text-[#8B0000]">💀 {errors.bedrooms}</p>
            )}
          </div>

          {/* Bathrooms - Optional */}
          <div>
            <label className="block text-sm font-bold text-[#8B00FF] mb-2">
              🚿 Min Bathrooms <span className="text-[#E0E0E0]/50">(Optional)</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.bathrooms || ''}
              onChange={(e) => handleChange('bathrooms', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Any"
              disabled={loading}
              className="w-full px-4 py-3 border-2 border-[#8B00FF] rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed placeholder-[#E0E0E0]/40"
            />
          </div>
        </div>

        {/* Maximum Budget - Required */}
        <div>
          <label className="block text-sm font-bold text-[#8B00FF] mb-2">
            💰 Maximum Budget (₦) <span className="text-[#8B0000]">*</span>
          </label>
          <input
            type="number"
            min="0"
            step="100000"
            value={formData.maxBudget || ''}
            onChange={(e) => handleChange('maxBudget', parseInt(e.target.value) || 0)}
            placeholder="e.g., 3000000"
            disabled={loading}
            className={`w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed placeholder-[#E0E0E0]/40 ${
              errors.maxBudget ? 'border-[#8B0000]' : 'border-[#8B00FF]'
            }`}
          />
          {errors.maxBudget && (
            <p className="mt-1 text-sm text-[#8B0000]">💀 {errors.maxBudget}</p>
          )}
          <p className="mt-1 text-sm text-[#00FF41] font-semibold">
            {formData.maxBudget > 0 && `₦${formData.maxBudget.toLocaleString()} ${
              formData.purpose === 'rent' ? 'per year' : 
              formData.purpose === 'shortlet' ? 'per night' : 
              'total'
            }`}
          </p>
        </div>

        {/* Move-in Date and Lease Length - Row */}
        <div className="grid md:grid-cols-2 gap-4">
          {/* Move-in Date - Optional */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Move-in Date <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="date"
              value={formData.moveInDate || ''}
              onChange={(e) => handleChange('moveInDate', e.target.value)}
              disabled={loading}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          {/* Lease Length - Optional */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Lease Length (years) <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.leaseLength || ''}
              onChange={(e) => handleChange('leaseLength', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="e.g., 1"
              disabled={loading}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        {/* Property Type - Optional */}
        <div>
          <label className="block text-sm font-bold text-[#8B00FF] mb-2">
            🏚️ Property Type <span className="text-[#E0E0E0]/50">(Optional)</span>
          </label>
          <select
            value={formData.propertyType || ''}
            onChange={(e) => handleChange('propertyType', e.target.value)}
            disabled={loading}
            className="w-full px-4 py-3 border-2 border-[#8B00FF] rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">Any haunted dwelling</option>
            <option value="apartment">🏢 Apartment</option>
            <option value="house">🏠 House</option>
            <option value="duplex">🏘️ Duplex</option>
            <option value="flat">🏬 Flat</option>
            <option value="studio">🏭 Studio</option>
          </select>
        </div>

        {/* Location Priorities - Optional */}
        <div>
          <label className="block text-sm font-bold text-[#8B00FF] mb-2">
            🗺️ Location Curses <span className="text-[#E0E0E0]/50">(Optional)</span>
          </label>
          <textarea
            value={formData.locationPriorities || ''}
            onChange={(e) => handleChange('locationPriorities', e.target.value)}
            placeholder="e.g., Near haunted malls, quiet graveyard, cursed schools nearby"
            rows={3}
            disabled={loading}
            className="w-full px-4 py-3 border-2 border-[#8B00FF] rounded-lg focus:ring-2 focus:ring-[#FF6B00] focus:border-[#FF6B00] bg-[#0A0A0A] text-[#E0E0E0] disabled:opacity-50 disabled:cursor-not-allowed resize-none placeholder-[#E0E0E0]/40"
          />
          <p className="mt-1 text-sm text-[#E0E0E0]/70">
            Describe what supernatural features matter to you
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-4 bg-gradient-to-r from-[#FF6B00] to-[#8B00FF] hover:from-[#ff8533] hover:to-[#a333ff] disabled:from-[#FF6B00]/40 disabled:to-[#8B00FF]/40 text-white font-bold rounded-lg transition-all transform hover:scale-[1.02] disabled:cursor-not-allowed disabled:transform-none shadow-[6px_6px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_30px_rgba(255,107,0,0.8)] uppercase tracking-wider"
          style={{ fontFamily: "'Creepster', cursive", fontSize: '1.2rem' }}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Summoning Spirits...
            </span>
          ) : (
            '🔮 Cast Search Spell'
          )}
        </button>
      </form>
    </div>
  );
}
