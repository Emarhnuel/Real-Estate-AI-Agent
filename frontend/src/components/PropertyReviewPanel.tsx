import { useState } from 'react';

interface PropertyForReview {
  id: string;
  address: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  listing_url: string;
  image_urls: string[];
}

interface PropertyReviewPanelProps {
  properties: PropertyForReview[];
  onSubmit: (approvedIds: string[]) => void;
  loading?: boolean;
}

export default function PropertyReviewPanel({
  properties,
  onSubmit,
  loading = false,
}: PropertyReviewPanelProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const toggleProperty = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const handleSubmit = () => {
    onSubmit(Array.from(selectedIds));
  };

  const selectAll = () => {
    setSelectedIds(new Set(properties.map((p) => p.id)));
  };

  const deselectAll = () => {
    setSelectedIds(new Set());
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Review Properties
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Select the properties you'd like to analyze further. I'll provide detailed location
          analysis for your approved selections.
        </p>
      </div>

      {/* Bulk Actions */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={selectAll}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 disabled:opacity-50"
        >
          Select All
        </button>
        <button
          onClick={deselectAll}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 disabled:opacity-50"
        >
          Deselect All
        </button>
        <div className="ml-auto text-sm text-gray-600 dark:text-gray-400">
          {selectedIds.size} of {properties.length} selected
        </div>
      </div>

      {/* Property Cards */}
      <div className="space-y-4 mb-6 max-h-[500px] overflow-y-auto">
        {properties.map((property) => (
          <div
            key={property.id}
            className={`border-2 rounded-lg p-4 transition-all cursor-pointer ${
              selectedIds.has(property.id)
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            }`}
            onClick={() => toggleProperty(property.id)}
          >
            <div className="flex gap-4">
              {/* Checkbox */}
              <div className="flex-shrink-0 pt-1">
                <input
                  type="checkbox"
                  checked={selectedIds.has(property.id)}
                  onChange={() => toggleProperty(property.id)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  onClick={(e) => e.stopPropagation()}
                />
              </div>

              {/* Property Image */}
              {property.image_urls && property.image_urls.length > 0 && (
                <div className="flex-shrink-0">
                  <img
                    src={property.image_urls[0]}
                    alt={property.address}
                    className="w-32 h-24 object-cover rounded-lg"
                    onError={(e) => {
                      e.currentTarget.src =
                        'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="128" height="96" viewBox="0 0 128 96"%3E%3Crect fill="%23e5e7eb" width="128" height="96"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="14"%3ENo Image%3C/text%3E%3C/svg%3E';
                    }}
                  />
                </div>
              )}

              {/* Property Details */}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1 truncate">
                  {property.address}
                </h3>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                  <span className="font-semibold text-blue-600 dark:text-blue-400">
                    ₦{property.price.toLocaleString()}/year
                  </span>
                  <span>{property.bedrooms} bed</span>
                  <span>{property.bathrooms} bath</span>
                </div>
                <a
                  href={property.listing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:underline"
                  onClick={(e) => e.stopPropagation()}
                >
                  View Listing →
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <div className="flex justify-end gap-3">
        <button
          onClick={handleSubmit}
          disabled={loading || selectedIds.size === 0}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center gap-2">
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
              Processing...
            </span>
          ) : (
            `Analyze ${selectedIds.size} ${selectedIds.size === 1 ? 'Property' : 'Properties'}`
          )}
        </button>
      </div>
    </div>
  );
}
