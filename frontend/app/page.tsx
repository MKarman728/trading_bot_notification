'use client'
import SignInButton from "./components/SignInButton";
import { useSession } from 'next-auth/react'
import { useEffect } from 'react';

export default function Home() {
  const { data: session, status } = useSession()
useEffect(()=>{
const bollinger = async () =>{
      try {
      const res = await fetch('http://localhost:8000/',{
        method: 'GET',
        headers: {'Content-Type': 'application/json'},
      })
      if(res.ok){
        const data = await res.json();
        console.log(data);
      }
      } catch(e){
        console.error("Error fetching bollinger data: ", e);
      }
    }
    bollinger();
  },[])
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
      <div className="flex justify-center items-center">
        {/* Your trading dashboard content here */}
        <h2 className="text-3xl">Your Trading Signals</h2>
        {/* Add components to display data from your FastAPI backend */}
      </div>
    </main >
  )
}
