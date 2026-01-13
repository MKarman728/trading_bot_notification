'use client'

import { signIn, signOut, useSession } from 'next-auth/react'
import { useEffect } from 'react'

export default function SignInButton() {
  const { data: session } = useSession()

  useEffect(() => {
    const createUser = async () => {
      if (session?.user) {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: session.user.email,
              name: session.user.name,
              image: session.user.image,
              provider: 'google',
              provider_id: session.user.email,
            })
          })

          if (response.ok) {
            console.log("User added to database");
          }
        } catch (e) {
          console.error("Error adding user: ", e);
        }
      }
    }
    createUser();
  }, [session])

  if (session) {
    return (
      <>
        <p>Signed in as {session.user?.email}</p>
        <button className="px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700" onClick={() => signOut()}>Sign Out</button>
      </>
    )
  }
  return <button className="px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
    onClick={() => signIn('google')}>Sign in with Google</button>
}
