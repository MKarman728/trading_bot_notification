'use client'

import { signIn, signOut, useSession } from 'next-auth/react'

export default function SignInButton() {
  const { data: session } = useSession()

  if (session) {
    return (
      <>
        <p>Signed in as {session.user?.email}</p>
        <button onClick={() => signOut()}>Sign Out</button>
      </>
    )
  }
  return <button className="px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
    onClick={() => signIn('google')}>Sign in with Google</button>
}
