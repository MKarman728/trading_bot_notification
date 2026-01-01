export default function Home() {
  return (
    <div className="flex flex-col min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <h1 className="text-2xl mb-3">Login To Trading Bot</h1>
      <form className="flex flex-col" action="send">
        <p>Login Email</p>
        <input type="email" id="user_email" className="border border-white-300 outline-none rounded-md border-white" />
        <p>Password</p>
        <input type="password" id="user_password" className="border border-white-300 outline-none rounded-md border-white" />
      </form>

    </div>
  );
}
