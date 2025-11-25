import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { GetServerSideProps } from 'next';
import { getAuth, buildClerkProps } from '@clerk/nextjs/server';
import Navigation from '@/components/Navigation';
import PropertySearchForm, { PropertySearchData } from '@/components/PropertySearchForm';
import PropertyReviewPanel from '@/components/PropertyReviewPanel';
import PropertyReportView from '@/components/PropertyReportView';

interface PropertyForReview {
  id: string;
  address: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  listing_url: string;
  image_urls: string[];
}

interface LocationAnalysis {
  property_id: string;
  nearby_pois: Array<{
    name: string;
    category: string;
    distance_meters: number;
    address: string;
  }>;
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

type WorkflowStep = 'form' | 'review' | 'report';

export default function AgentPage() {
  const { getToken } = useAuth();

  // Workflow state
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('form');
  const [loading, setLoading] = useState(false);
  
  // Interrupt state
  const [interrupt, setInterrupt] = useState<{
    properties: PropertyForReview[];
    threadId: string;
  } | null>(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  
  // Report state
  const [report, setReport] = useState<PropertyReport | null>(null);
  
  // Error state
  const [error, setError] = useState<string | null>(null);

  async function handleFormSubmit(formData: PropertySearchData) {
    setLoading(true);
    setError(null);

    const jwt = await getToken();
    if (!jwt) {
      setError('Authentication required. Please sign in again.');
      setLoading(false);
      return;
    }

    // Generate thread_id
    const userId = jwt ? JSON.parse(atob(jwt.split('.')[1])).sub : '';
    const currentThreadId = `${userId}-${Date.now()}`;

    // Build search message from form data
    const searchMessage = buildSearchMessage(formData);

    try {
      const response = await fetch('http://localhost:8000/api/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${jwt}`,
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: searchMessage }],
          timestamp: Date.now()
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Check for interrupt (human-in-the-loop for property review)
      if (result.__interrupt__) {
        const interruptData = result.__interrupt__;
        
        // Extract properties from interrupt
        if (Array.isArray(interruptData) && interruptData.length > 0) {
          const interruptValue = interruptData[0]?.value;
          
          if (interruptValue?.type === 'property_review' && interruptValue.properties) {
            setInterrupt({
              properties: interruptValue.properties,
              threadId: currentThreadId
            });
            setCurrentStep('review');
          }
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Failed to connect to the agent: ${errorMessage}`);
      setLoading(false);
    }
  }

  function buildSearchMessage(formData: PropertySearchData): string {
    const purposeText = formData.purpose === 'rent' ? 'for rent' : 
                       formData.purpose === 'buy' ? 'for sale' : 
                       'for shortlet';
    
    const budgetText = formData.purpose === 'rent' ? 'per year' : 
                      formData.purpose === 'shortlet' ? 'per night' : 
                      'total';
    
    let message = `I am looking for a ${formData.bedrooms} bedroom ${formData.propertyType || 'apartment'} ${purposeText} in ${formData.location} with a maximum budget of ₦${formData.maxBudget.toLocaleString()} ${budgetText}.`;
    
    if (formData.bathrooms) {
      message += ` Minimum ${formData.bathrooms} bathrooms.`;
    }
    
    if (formData.moveInDate) {
      message += ` Move-in date: ${formData.moveInDate}.`;
    }
    
    if (formData.leaseLength && formData.purpose === 'rent') {
      message += ` Lease length: ${formData.leaseLength} year${formData.leaseLength > 1 ? 's' : ''}.`;
    }
    
    if (formData.locationPriorities) {
      message += ` Location priorities: ${formData.locationPriorities}.`;
    }
    
    return message;
  }

  function handleRetry() {
    setError(null);
    setReport(null);
    setInterrupt(null);
    setCurrentStep('form');
  }

  function handleNewSearch() {
    setReport(null);
    setInterrupt(null);
    setCurrentStep('form');
    setError(null);
  }

  async function handlePropertyReview(approvedIds: string[]) {
    if (!interrupt) return;
    
    setResumeLoading(true);
    
    const jwt = await getToken();
    if (!jwt) {
      setError('Authentication required. Please sign in again.');
      setResumeLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${jwt}`,
        },
        body: JSON.stringify({
          thread_id: interrupt.threadId,
          approved_properties: approvedIds
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Clear interrupt
      setInterrupt(null);
      
      // Check if this is a final report
      if (result.structured_response) {
        setReport(result.structured_response);
        setCurrentStep('report');
      }
      
      setResumeLoading(false);
    } catch (error) {
      console.error('Resume error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setError(`Failed to resume analysis: ${errorMessage}`);
      setResumeLoading(false);
      setInterrupt(null);
    }
  }

  return (
    <main className="min-h-screen bg-[#0A0A0A] relative">
      {/* Floating bats */}
      <div className="fixed top-20 left-10 animate-bounce" style={{ animationDuration: '3s' }}>
        <span className="text-4xl opacity-30">🦇</span>
      </div>
      <div className="fixed top-40 right-20 animate-bounce" style={{ animationDuration: '4s', animationDelay: '1s' }}>
        <span className="text-4xl opacity-30">🦇</span>
      </div>
      
      <Navigation />

      <div className="container mx-auto px-4 py-8 max-w-5xl relative z-10">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-2 glitch" style={{ fontFamily: "'Creepster', cursive", color: '#FF6B00', textShadow: '0 0 20px rgba(255,107,0,0.8)' }}>
            👻 Spirit Guide Portal
          </h1>
          <p className="text-[#E0E0E0] text-lg">
            Your <span className="text-[#8B00FF] font-bold">supernatural</span> property search assistant
          </p>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-[#1a1a1a] border-2 border-[#8B0000] rounded-lg p-4 shadow-[0_0_20px_rgba(139,0,0,0.5)]">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <span className="text-[#8B0000] text-2xl">💀</span>
                <div>
                  <h3 className="font-semibold text-[#8B0000] mb-1" style={{ fontFamily: "'Creepster', cursive" }}>
                    Curse Detected!
                  </h3>
                  <p className="text-sm text-[#E0E0E0]">{error}</p>
                </div>
              </div>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-[#8B0000] hover:bg-[#a00000] text-white text-sm font-bold rounded-lg transition-all shadow-[0_0_10px_rgba(139,0,0,0.6)]"
              >
                🔮 Retry Spell
              </button>
            </div>
          </div>
        )}

        {/* Step 1: Property Search Form */}
        {currentStep === 'form' && (
          <PropertySearchForm onSubmit={handleFormSubmit} loading={loading} />
        )}

        {/* Step 2: Property Review */}
        {currentStep === 'review' && interrupt && (
          <PropertyReviewPanel
            properties={interrupt.properties}
            onSubmit={handlePropertyReview}
            loading={resumeLoading}
          />
        )}

        {/* Step 3: Final Report */}
        {currentStep === 'report' && report && (
          <div className="space-y-6">
            <PropertyReportView report={report} />
            <button
              onClick={handleNewSearch}
              className="w-full px-6 py-3 bg-[#FF6B00] hover:bg-[#ff8533] text-white font-bold rounded-lg transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,0.8)] hover:shadow-[0_0_20px_rgba(255,107,0,0.8)] uppercase tracking-wider"
              style={{ fontFamily: "'Creepster', cursive" }}
            >
              🎃 Summon New Properties
            </button>
          </div>
        )}
      </div>
    </main>
  );
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const { userId } = getAuth(ctx.req);
  
  if (!userId) {
    return {
      redirect: {
        destination: '/sign-in',
        permanent: false,
      },
    };
  }
  
  return { 
    props: {
      ...buildClerkProps(ctx.req)
    } 
  };
};
