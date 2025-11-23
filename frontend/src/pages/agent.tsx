import { useState, FormEvent } from 'react';
import { useAuth } from '@clerk/nextjs';
import { GetServerSideProps } from 'next';
import { getAuth } from '@clerk/nextjs/server';
import Navigation from '@/components/Navigation';
import ChatInterface from '@/components/ChatInterface';
import PropertyReviewPanel from '@/components/PropertyReviewPanel';
import PropertyReportView from '@/components/PropertyReportView';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface PropertyForReview {
  id: string;
  address: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  listing_url: string;
  image_urls: string[];
}

interface PropertyReport {
  properties: any[];
  location_analyses: Record<string, any>;
  summary: string;
  generated_at: string;
}

export default function AgentPage() {
  const { getToken } = useAuth();

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Interrupt state
  const [interrupt, setInterrupt] = useState<{
    properties: PropertyForReview[];
    threadId: string;
  } | null>(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  
  // Report state
  const [report, setReport] = useState<PropertyReport | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    const jwt = await getToken();
    if (!jwt) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Authentication required. Please sign in again.' 
      }]);
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/invoke', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${jwt}`,
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: userMessage }],
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
            // Generate thread_id from user_id and timestamp
            const userId = jwt ? JSON.parse(atob(jwt.split('.')[1])).sub : '';
            const threadId = `${userId}-${Date.now()}`;
            
            setInterrupt({
              properties: interruptValue.properties,
              threadId: threadId
            });
            
            // Add system message about property review
            setMessages(prev => [...prev, {
              role: 'assistant',
              content: `I found ${interruptValue.properties.length} properties that match your criteria. Please review them below and select which ones you'd like me to analyze further.`
            }]);
          }
        }
      } else if (result.structured_response) {
        // Check if this is a final report with structured_response
        setReport(result.structured_response);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Analysis complete! Here is your comprehensive property report.'
        }]);
      } else {
        // Extract assistant message from result
        if (result.messages && result.messages.length > 0) {
          const lastMessage = result.messages[result.messages.length - 1];
          if (lastMessage.content) {
            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: lastMessage.content 
            }]);
          }
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Fetch error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error processing your request.' 
      }]);
      setLoading(false);
    }
  }

  async function handlePropertyReview(approvedIds: string[]) {
    if (!interrupt) return;
    
    setResumeLoading(true);
    
    const jwt = await getToken();
    if (!jwt) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Authentication required. Please sign in again.'
      }]);
      setResumeLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/resume', {
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
      
      // Add confirmation message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Great! I'm now analyzing the ${approvedIds.length} properties you selected. This will take a moment...`
      }]);
      
      // Check if this is a final report
      if (result.structured_response) {
        setReport(result.structured_response);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Analysis complete! Here is your comprehensive property report.'
        }]);
      } else if (result.messages && result.messages.length > 0) {
        // Extract assistant message from result
        const lastMessage = result.messages[result.messages.length - 1];
        if (lastMessage.content) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: lastMessage.content
          }]);
        }
      }
      
      setResumeLoading(false);
    } catch (error) {
      console.error('Resume error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your selections.'
      }]);
      setResumeLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navigation />

      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
            AI Real Estate Co-Pilot
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your intelligent property search assistant
          </p>
        </header>

        {/* Show PropertyReportView if report is available */}
        {report ? (
          <div className="space-y-6">
            <PropertyReportView report={report} />
            <button
              onClick={() => {
                setReport(null);
                setMessages([]);
              }}
              className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              Start New Search
            </button>
          </div>
        ) : interrupt ? (
          <PropertyReviewPanel
            properties={interrupt.properties}
            onSubmit={handlePropertyReview}
            loading={resumeLoading}
          />
        ) : (
          <ChatInterface
            messages={messages}
            input={input}
            loading={loading}
            onInputChange={setInput}
            onSubmit={handleSubmit}
          />
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
  
  return { props: {} };
};
