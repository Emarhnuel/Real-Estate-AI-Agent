import { useState } from 'react';

interface PropertyForReview {
  id: string;
  address: string;
  price: string | number;
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
    <div className="bg-[#1a1a1a] rounded-2xl shadow-[0_0_30px_rgba(255,107,0,0.3)] p-6 border-2 border-[#FF6B00]">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-[#FF6B00] mb-2 glitch" style={{ fontFamily: "'Creepster', cursive" }}>
          🏚️ Choose Your Haunted Homes
        </h2>
        <p className="text-[#E0E0E0]">
          Select the cursed properties you would like to investigate further. Our spirits will provide detailed paranormal analysis for your approved selections.
        </p>
      </div>

      {/* Bulk Actions */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={selectAll}
          disabled={loading}
          className="px-4 py-2 text-sm font-bold text-[#00FF41] hover:text-[#33ff66] disabled:opacity-50 transition-colors"
        >
          ✓ Curse All
        </button>
        <button
          onClick={deselectAll}
          disabled={loading}
          className="px-4 py-2 text-sm font-bold text-[#8B00FF] hover:text-[#a333ff] disabled:opacity-50 transition-colors"
        >
          ✗ Banish All
        </button>
        <div className="ml-auto text-sm text-[#E0E0E0] font-semibold">
          👻 {selectedIds.size} of {properties.length} haunted
        </div>
      </div>

      {/* Property Cards */}
      <div className="space-y-4 mb-6 max-h-[500px] overflow-y-auto">
        {properties.map((property) => (
          <div
            key={property.id}
            className={`border-2 rounded-lg p-4 transition-all cursor-pointer ${
              selectedIds.has(property.id)
                ? 'border-[#FF6B00] bg-[#FF6B00]/10 shadow-[0_0_15px_rgba(255,107,0,0.5)]'
                : 'border-[#8B00FF]/30 hover:border-[#8B00FF] hover:shadow-[0_0_10px_rgba(139,0,255,0.3)]'
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
                  className="w-5 h-5 text-[#FF6B00] rounded focus:ring-2 focus:ring-[#FF6B00] bg-[#0A0A0A] border-2 border-[#8B00FF]"
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
                <h3 className="font-semibold text-[#E0E0E0] mb-1 truncate">
                  🏚️ {property.address}
                </h3>
                <div className="flex flex-wrap gap-4 text-sm text-[#E0E0E0] mb-2">
                  <span className="font-bold text-[#FF6B00]">
                    {typeof property.price === 'number' ? `₦${property.price.toLocaleString()}` : property.price}
                  </span>
                  <span>🛏️ {property.bedrooms} bed</span>
                  <span>🚿 {property.bathrooms} bath</span>
                </div>
                <a
                  href={property.listing_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[#00FF41] hover:text-[#33ff66] hover:underline font-semibold"
                  onClick={(e) => e.stopPropagation()}
                >
                  👁️ View Cursed Listing →
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
          className="px-6 py-3 bg-[#8B00FF] hover:bg-[#a333ff] disabled:bg-[#8B00FF]/40 text-white font-bold rounded-lg transition-all duration-200 disabled:cursor-not-allowed shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_20px_rgba(139,0,255,0.8)] uppercase tracking-wider"
          style={{ fontFamily: "'Creepster', cursive" }}
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
              Summoning Spirits...
            </span>
          ) : (
            `🔮 Investigate ${selectedIds.size} ${selectedIds.size === 1 ? 'Haunt' : 'Haunts'}`
          )}
        </button>
      </div>
    </div>
  );
}
