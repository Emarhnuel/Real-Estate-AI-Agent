interface PointOfInterest {
  name: string;
  category: string;
  distance_meters: number;
  address: string;
}

interface LocationAnalysis {
  property_id: string;
  nearby_pois: PointOfInterest[];
  pros: string[];
  cons: string[];
  walkability_score?: number;
  transit_score?: number;
}

interface Property {
  id: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  property_type: string;
  listing_url: string;
  image_urls: string[];
  description: string;
}

interface PropertyReport {
  properties: Property[];
  location_analyses: Record<string, LocationAnalysis>;
  summary: string;
  generated_at: string;
}

interface PropertyReportViewProps {
  report: PropertyReport;
}

export default function PropertyReportView({ report }: PropertyReportViewProps) {
  const formatDistance = (meters: number) => {
    if (meters < 1000) {
      return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
  };

  const groupPOIsByCategory = (pois: PointOfInterest[]) => {
    const grouped: Record<string, PointOfInterest[]> = {};
    pois.forEach((poi) => {
      if (!grouped[poi.category]) {
        grouped[poi.category] = [];
      }
      grouped[poi.category].push(poi);
    });
    return grouped;
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-3xl font-bold mb-2">Property Analysis Report</h2>
            <p className="text-blue-100">
              Generated on {new Date(report.generated_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
          <button
            onClick={handlePrint}
            className="px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium print:hidden"
          >
            Print Report
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">
          Executive Summary
        </h3>
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {report.summary}
        </p>
      </div>

      {/* Properties */}
      <div className="p-6 space-y-8">
        {report.properties.map((property, index) => {
          const locationAnalysis = report.location_analyses[property.id];
          const groupedPOIs = locationAnalysis
            ? groupPOIsByCategory(locationAnalysis.nearby_pois)
            : {};

          return (
            <div
              key={property.id}
              className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden"
            >
              {/* Property Header */}
              <div className="bg-gray-50 dark:bg-gray-900 p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      Property {index + 1}: {property.address}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {property.city}, {property.state} {property.zip_code}
                    </p>
                  </div>
                  <a
                    href={property.listing_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors print:hidden"
                  >
                    View Listing →
                  </a>
                </div>
              </div>

              <div className="p-6">
                {/* Property Images */}
                {property.image_urls && property.image_urls.length > 0 && (
                  <div className="mb-6">
                    <div className="grid grid-cols-3 gap-4">
                      {property.image_urls.slice(0, 3).map((url, idx) => (
                        <img
                          key={idx}
                          src={url}
                          alt={`${property.address} - Image ${idx + 1}`}
                          className="w-full h-48 object-cover rounded-lg"
                          onError={(e) => {
                            e.currentTarget.src =
                              'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300"%3E%3Crect fill="%23e5e7eb" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="18"%3ENo Image%3C/text%3E%3C/svg%3E';
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Property Details */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Price</p>
                    <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      ₦{property.price.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">per year</p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Bedrooms</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                      {property.bedrooms}
                    </p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Bathrooms</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                      {property.bathrooms}
                    </p>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Size</p>
                    <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                      {property.square_feet.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">sq ft</p>
                  </div>
                </div>

                {/* Description */}
                <div className="mb-6">
                  <h5 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    Description
                  </h5>
                  <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                    {property.description}
                  </p>
                </div>

                {/* Location Analysis */}
                {locationAnalysis && (
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                    <h5 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      Location Analysis
                    </h5>

                    {/* Scores */}
                    {(locationAnalysis.walkability_score || locationAnalysis.transit_score) && (
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        {locationAnalysis.walkability_score && (
                          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                              Walkability Score
                            </p>
                            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                              {locationAnalysis.walkability_score}/100
                            </p>
                          </div>
                        )}
                        {locationAnalysis.transit_score && (
                          <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                              Transit Score
                            </p>
                            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                              {locationAnalysis.transit_score}/100
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Pros and Cons */}
                    <div className="grid md:grid-cols-2 gap-6 mb-6">
                      {/* Pros */}
                      {locationAnalysis.pros && locationAnalysis.pros.length > 0 && (
                        <div>
                          <h6 className="font-semibold text-green-600 dark:text-green-400 mb-3 flex items-center gap-2">
                            <span className="text-xl">✓</span> Advantages
                          </h6>
                          <ul className="space-y-2">
                            {locationAnalysis.pros.map((pro, idx) => (
                              <li
                                key={idx}
                                className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2"
                              >
                                <span className="text-green-500 mt-1">•</span>
                                <span>{pro}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Cons */}
                      {locationAnalysis.cons && locationAnalysis.cons.length > 0 && (
                        <div>
                          <h6 className="font-semibold text-orange-600 dark:text-orange-400 mb-3 flex items-center gap-2">
                            <span className="text-xl">⚠</span> Considerations
                          </h6>
                          <ul className="space-y-2">
                            {locationAnalysis.cons.map((con, idx) => (
                              <li
                                key={idx}
                                className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2"
                              >
                                <span className="text-orange-500 mt-1">•</span>
                                <span>{con}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Nearby Points of Interest */}
                    {Object.keys(groupedPOIs).length > 0 && (
                      <div>
                        <h6 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
                          Nearby Amenities
                        </h6>
                        <div className="grid md:grid-cols-2 gap-4">
                          {Object.entries(groupedPOIs).map(([category, pois]) => (
                            <div
                              key={category}
                              className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg"
                            >
                              <h6 className="font-medium text-gray-900 dark:text-gray-100 mb-2 capitalize">
                                {category} ({pois.length})
                              </h6>
                              <ul className="space-y-1">
                                {pois.slice(0, 3).map((poi, idx) => (
                                  <li
                                    key={idx}
                                    className="text-sm text-gray-600 dark:text-gray-400 flex justify-between"
                                  >
                                    <span className="truncate mr-2">{poi.name}</span>
                                    <span className="text-blue-600 dark:text-blue-400 font-medium flex-shrink-0">
                                      {formatDistance(poi.distance_meters)}
                                    </span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
