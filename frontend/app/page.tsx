import SignInButton from "./components/SignInButton";

export default function Home() {
  return (
    <main className="flex flex-col justify-center items-center min-h-screen gap-4">
      <h1 className="text-3xl">Trading Analysis on S&P 500</h1>
      <SignInButton />
    </main>
  )
}
