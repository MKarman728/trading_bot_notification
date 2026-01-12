'use client'
import SignInButton from "./components/SignInButton";
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react';

interface TableRow {
  symbol: string;
  security: string;
  signal: string;
  signal_date: string;
}

export default function Home() {
  const { data: session, status } = useSession()
  const [bollingerData, setBollingerData] = useState<TableRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!session) {
      return;
    }
    const fetchBollingerData = async () => {
      // fetching bollinger data to handle on frontend.
      setLoading(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/bollinger_bands`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })
        if (res.ok) {
          const data = await res.json();
          console.log(data);
          setBollingerData(data);
        } else {
          setError(`Error: ${res.status} ${res.statusText}`);
        }
      } catch (err) {
        console.error("Error fetching bollinger data: ", err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    }
    fetchBollingerData();
  }, [session])
  if (status == 'loading') {
    return <div>Loading...</div>
  }
  if (!session) {
    return (
      <main className="flex flex-col justify-center items-center min-h-screen gap-4">
        <h1 className="text-3xl">Trading Analysis on S&P 500</h1>
        <SignInButton />
      </main>
    )
  }

  return (
    < main className="p-8" >
      <div className="flex justify-between items-center mb-8">
        <h1>Welcome, {session.user?.name}!</h1>
        <SignInButton />
      </div>
      <div className="flex flex-col items-center">
        <h2 className="text-3xl mb-4">Your Trading Signals</h2>

        {loading && <p>Loading trading signals...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {bollingerData && bollingerData.length > 0 && (
          <div className="mt-4 w-full overflow-x-auto">
            <table className="min-w-full bg-white border dark:bg-gray-800 border-gray-300 dark:border-gray-700">
              <thead className="bg-gray-100 dark:bg-gray-700">
                <tr>
                  <th className="px-4 py-2 border dark:border-gray-600 dark:text-white">Symbol</th>
                  <th className="px-4 py-2 border dark:border-gray-600 dark:text-white">Security</th>
                  <th className="px-4 py-2 border dark:border-gray-600 dark:text-white">Signal</th>
                  <th className="px-4 py-2 border dark:border-gray-600 dark:text-white">Date</th>
                </tr>
              </thead>
              <tbody>
                {bollingerData.map((row, idx) => (
                  <tr
                    key={idx}
                    className={row.signal === 'Buy' ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-green-900/20'}
                  >
                    <td className="px-4 py-2 border dark:border-gray-600 dark:text-white font-mono">{row.symbol}</td>
                    <td className="px-4 py-2 border dark:border-gray-600 dark:text-white font-mono">{row.security}</td>
                    <td className={`px-4 py-2 border dark:border-gray-600 font-semibold ${row.signal === 'Buy' ?
                      'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                      }`}>
                      {row.signal}
                    </td>
                    <td className="px-4 py-2 border dark:border-gray-600 dark:text-white">{row.signal_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main >
  )
}
