import { useState, FormEvent } from 'react';
import { useAuth } from '@clerk/nextjs';
import { GetServerSideProps } from 'next';
import { getAuth } from '@clerk/nextjs/server';
import Navigation from '@/components/Navigation';
import ChatInterface from '@/components/ChatInterface';
import PropertyReviewPanel from '@/components/PropertyReviewPanel';

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

        <ChatInterface
          messages={messages}
          input={input}
          loading={loading}
          onInputChange={setInput}
          onSubmit={handleSubmit}
        />
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
