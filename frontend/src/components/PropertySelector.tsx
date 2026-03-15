import { useState } from 'react';
import { ExternalLink, Check, ChevronLeft, ChevronRight, Palette } from 'lucide-react';

interface ScrapedProperty {
    id: string; // or address acting as ID
    url?: string;
    price: number | string;
    address: string;
    bedrooms: number;
    bathrooms: number;
    description?: string;
    image_urls?: string[];
    property_type?: string;
    listing_url?: string;
}

interface PropertySelectorProps {
    properties: ScrapedProperty[];
    onApprove: (selected: { id: string, style: string }[]) => void;
    onRetry: () => void;
}

export function PropertySelector({ properties, onApprove, onRetry }: PropertySelectorProps) {
    const [selectedIds, setSelectedIds] = useState<string[]>(() => properties.map(p => p.id));
    const [styles, setStyles] = useState<Record<string, string>>({});
    const [imageIndices, setImageIndices] = useState<Record<string, number>>({});

    const toggleSelection = (id: string) => {
        setSelectedIds((prev: string[]) =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
        if (!styles[id]) {
            setStyles((prev: Record<string, string>) => ({ ...prev, [id]: "Modern Minimalist" }));
        }
    };

    const nextImage = (id: string, len: number, e: React.MouseEvent) => {
        e.stopPropagation();
        setImageIndices((prev: Record<string, number>) => ({ ...prev, [id]: ((prev[id] || 0) + 1) % len }));
    };

    const prevImage = (id: string, len: number, e: React.MouseEvent) => {
        e.stopPropagation();
        setImageIndices((prev: Record<string, number>) => ({ ...prev, [id]: ((prev[id] || 0) - 1 + len) % len }));
    };

    const handleStyleChange = (id: string, style: string) => {
        setStyles((prev: Record<string, string>) => ({ ...prev, [id]: style }));
    };

    const handleApprove = () => {
        const selectedData = selectedIds.map(id => ({
            id,
            style: styles[id] || "Modern Minimalist"
        }));
        onApprove(selectedData);
    };

    return (
        <div className="max-w-6xl mx-auto px-4">
            <div className="text-center mb-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-100 text-brand-800 text-sm font-semibold mb-4">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-brand-500"></span>
                    </span>
                    Action Required
                </div>
                <h2 className="text-3xl font-bold text-slate-900 font-serif mb-2">Agent Report: {properties.length} Properties Found</h2>
                <p className="text-slate-500">Select properties specifically to analyze and define your design vision for each.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                {properties.map((prop) => {
                    const currentImageIndex = imageIndices[prop.id] || 0;
                    const images = prop.image_urls || [];
                    const hasImages = images.length > 0;
                    const isSelected = selectedIds.includes(prop.id);

                    return (
                        <div
                            key={prop.id}
                            className={`
                                relative rounded-2xl border transition-all duration-300 overflow-hidden flex flex-col
                                ${isSelected
                                    ? 'border-brand-500 shadow-xl ring-4 ring-brand-500/10 translate-y-[-4px]'
                                    : 'border-slate-200 bg-white hover:border-brand-300 hover:shadow-lg'}
                            `}
                        >
                            {/* Selection Checkbox */}
                            <div
                                onClick={() => toggleSelection(prop.id)}
                                className={`absolute top-4 right-4 z-20 w-8 h-8 rounded-full flex items-center justify-center cursor-pointer transition-all shadow-sm border border-black/5 hover:scale-110 ${isSelected ? 'bg-brand-600 text-white' : 'bg-white/90 text-slate-300 hover:text-brand-400'
                                    }`}
                            >
                                <Check className="w-5 h-5" />
                            </div>

                            {/* Image Carousel */}
                            <div className="h-56 bg-slate-100 relative group">
                                {hasImages ? (
                                    <>
                                        <img
                                            src={images[currentImageIndex]}
                                            alt={`${prop.address} - view ${currentImageIndex + 1}`}
                                            className="w-full h-full object-cover transition-opacity duration-300"
                                        />

                                        {images.length > 1 && (
                                            <>
                                                <button
                                                    onClick={(e) => prevImage(prop.id, images.length, e)}
                                                    className="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-black/30 text-white hover:bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    <ChevronLeft className="w-5 h-5" />
                                                </button>
                                                <button
                                                    onClick={(e) => nextImage(prop.id, images.length, e)}
                                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-black/30 text-white hover:bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    <ChevronRight className="w-5 h-5" />
                                                </button>
                                                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
                                                    {images.slice(0, 5).map((_, idx) => (
                                                        <div
                                                            key={idx}
                                                            className={`w-1.5 h-1.5 rounded-full transition-colors ${idx === currentImageIndex ? 'bg-white' : 'bg-white/40'}`}
                                                        />
                                                    ))}
                                                </div>
                                            </>
                                        )}
                                    </>
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-slate-400 bg-slate-50">
                                        <span className="text-sm">No Images Available</span>
                                    </div>
                                )}
                                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-4 pt-12">
                                    <p className="text-white font-bold text-lg drop-shadow-md">
                                        {typeof prop.price === 'number' ? `£${prop.price.toLocaleString()}` : prop.price}
                                        {prop.property_type && (
                                            <span className="ml-2 text-sm font-normal text-white/80 bg-black/30 px-2 py-0.5 rounded capitalize">
                                                {prop.property_type}
                                            </span>
                                        )}
                                    </p>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="p-5 flex-1 flex flex-col">
                                <div onClick={() => toggleSelection(prop.id)} className="cursor-pointer mb-3">
                                    <h3 className="font-bold text-slate-900 text-lg leading-tight mb-1 line-clamp-2 hover:text-brand-700 transition-colors">
                                        {prop.address}
                                    </h3>
                                    <div className="flex gap-3 text-sm text-slate-500 mt-2">
                                        <span className="font-medium">{prop.bedrooms} Bed</span>
                                        <span className="text-slate-300">•</span>
                                        <span className="font-medium">{prop.bathrooms} Bath</span>
                                    </div>
                                </div>
                                
                                {prop.description && (
                                    <p className="text-sm text-slate-500 line-clamp-2 mb-4">
                                        {prop.description}
                                    </p>
                                )}

                                {/* Design Input for Selected Items */}
                                <div className={`mt-auto transition-all duration-300 ${isSelected ? 'opacity-100 max-h-32' : 'opacity-60 max-h-32 grayscale hover:grayscale-0'}`}>
                                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                                        <Palette className="w-3.5 h-3.5" />
                                        Interior Style Vision
                                    </label>
                                    <input
                                        type="text"
                                        placeholder="E.g. Scandinavian, Industrial Loft..."
                                        value={styles[prop.id] || ''}
                                        onChange={(e) => handleStyleChange(prop.id, e.target.value)}
                                        onClick={(e) => e.stopPropagation()}
                                        className={`w-full px-3 py-2.5 rounded-lg border text-sm transition-all focus:ring-2 focus:ring-brand-500/20 outline-none ${isSelected
                                            ? 'border-brand-200 bg-brand-50/30 text-brand-900 placeholder:text-brand-300 focus:border-brand-500'
                                            : 'border-slate-200 bg-slate-50 text-slate-600 focus:bg-white focus:border-brand-300'
                                            }`}
                                    />
                                </div>

                                <div className="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center">
                                    <a
                                        href={prop.listing_url || prop.url || "#"}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-xs font-semibold text-slate-400 hover:text-brand-600 flex items-center gap-1 transition-colors"
                                    >
                                        View Original <ExternalLink className="w-3 h-3" />
                                    </a>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Actions Footer */}
            <div className="sticky bottom-6 bg-white/95 backdrop-blur-md border border-slate-200/60 p-4 rounded-2xl shadow-2xl shadow-brand-900/10 flex flex-col md:flex-row items-center justify-between gap-6 ring-1 ring-slate-900/5">

                {/* Retry Option */}
                <div className="flex-1 w-full md:w-auto">
                    <button
                        onClick={() => onRetry()}
                        className="text-slate-500 hover:text-slate-800 text-sm font-medium underline decoration-dotted decoration-slate-300 underline-offset-4"
                    >
                        None of these fit? Start over.
                    </button>
                </div>

                {/* Approve Button */}
                <div className="flex items-center gap-6">
                    <div className="text-right hidden sm:block">
                        <span className="block text-2xl font-bold text-slate-900 leading-none">
                            {selectedIds.length}
                        </span>
                        <span className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                            Selected
                        </span>
                    </div>
                    <button
                        disabled={selectedIds.length === 0}
                        onClick={handleApprove}
                        className="btn-primary pl-8 pr-10 py-4 text-base shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 rounded-xl"
                    >
                        Analyze & Redesign
                    </button>
                </div>
            </div>
        </div>
    );
}
