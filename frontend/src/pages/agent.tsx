import { GetServerSideProps } from 'next';
import { getAuth } from '@clerk/nextjs/server';
import { UserButton } from '@clerk/nextjs';


export default function AgentPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* User Menu in Top Right */}
      <div className="absolute top-4 right-4">
        <UserButton showName={true} />
      </div>

      <div className="container mx-auto px-4 py-12">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            AI Real Estate Co-Pilot
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Your intelligent property search assistant
          </p>
        </header>

        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
            <p className="text-gray-700 dark:text-gray-300">
              Agent interaction interface coming soon...
            </p>
          </div>
        </div>
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
