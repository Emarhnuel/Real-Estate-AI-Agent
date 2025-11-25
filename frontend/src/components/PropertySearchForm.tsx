import { FormEvent, useState } from 'react';

interface PropertySearchFormProps {
  onSubmit: (formData: PropertySearchData) => void;
  loading: boolean;
}

export interface PropertySearchData {
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

  const handleChange = (field: keyof PropertySearchData, value: any) => {
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
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Find Your Perfect Property
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Fill out the form below to search for properties that match your criteria
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Location - Required */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Location <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            placeholder="e.g., Lekki, Lagos"
            disabled={loading}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed ${
              errors.location ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
            }`}
          />
          {errors.location && (
            <p className="mt-1 text-sm text-red-500">{errors.location}</p>
          )}
        </div>

        {/* Bedrooms and Bathrooms - Row */}
        <div className="grid md:grid-cols-2 gap-4">
          {/* Bedrooms - Required */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Number of Bedrooms <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.bedrooms}
              onChange={(e) => handleChange('bedrooms', parseInt(e.target.value) || 1)}
              disabled={loading}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed ${
                errors.bedrooms ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errors.bedrooms && (
              <p className="mt-1 text-sm text-red-500">{errors.bedrooms}</p>
            )}
          </div>

          {/* Bathrooms - Optional */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Minimum Bathrooms <span className="text-gray-400">(Optional)</span>
            </label>
            <input
              type="number"
              min="1"
              value={formData.bathrooms || ''}
              onChange={(e) => handleChange('bathrooms', e.target.value ? parseInt(e.target.value) : undefined)}
              placeholder="Any"
              disabled={loading}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>
        </div>

        {/* Maximum Budget - Required */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Maximum Annual Budget (₦) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            min="0"
            step="100000"
            value={formData.maxBudget || ''}
            onChange={(e) => handleChange('maxBudget', parseInt(e.target.value) || 0)}
            placeholder="e.g., 3000000"
            disabled={loading}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed ${
              errors.maxBudget ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
            }`}
          />
          {errors.maxBudget && (
            <p className="mt-1 text-sm text-red-500">{errors.maxBudget}</p>
          )}
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {formData.maxBudget > 0 && `₦${formData.maxBudget.toLocaleString()} per year`}
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
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Property Type <span className="text-gray-400">(Optional)</span>
          </label>
          <select
            value={formData.propertyType || ''}
            onChange={(e) => handleChange('propertyType', e.target.value)}
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">Any type</option>
            <option value="apartment">Apartment</option>
            <option value="house">House</option>
            <option value="duplex">Duplex</option>
            <option value="flat">Flat</option>
            <option value="studio">Studio</option>
          </select>
        </div>

        {/* Location Priorities - Optional */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Location Priorities <span className="text-gray-400">(Optional)</span>
          </label>
          <textarea
            value={formData.locationPriorities || ''}
            onChange={(e) => handleChange('locationPriorities', e.target.value)}
            placeholder="e.g., Near shopping malls, quiet neighborhood, good schools nearby"
            rows={3}
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed resize-none"
          />
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Describe what's important to you about the location
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-blue-400 disabled:to-indigo-400 text-white font-semibold rounded-lg transition-all transform hover:scale-[1.02] disabled:cursor-not-allowed disabled:transform-none shadow-lg"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
              Searching Properties...
            </span>
          ) : (
            'Search Properties'
          )}
        </button>
      </form>
    </div>
  );
}
