import { GetServerSideProps } from 'next';
import { getAuth } from '@clerk/nextjs/server';
import { UserProfile } from '@clerk/nextjs';
import Navigation from '@/components/Navigation';

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <Navigation />
      <div className="flex items-center justify-center p-4 py-12">
        <UserProfile 
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "shadow-xl"
            }
          }}
          routing="path"
          path="/profile"
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
