export default function Header() {
  return (
    <header className="border-b border-neutral-800/30 bg-black/20 backdrop-blur supports-[backdrop-filter]:bg-black/10">
      <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded bg-gradient-to-br from-indigo-500 to-violet-600" />
          <div>
            <h1 className="text-lg font-semibold leading-none">Secure Auth Demo</h1>
            <p className="text-xs text-neutral-400">Phishing‑resistant MFA & detection</p>
          </div>
        </div>
        <nav className="text-sm text-neutral-300">
          <a href="#login" className="hover:text-white">Login</a>
          <span className="mx-3 opacity-30">•</span>
          <a href="#passkeys" className="hover:text-white">Passkeys</a>
          <span className="mx-3 opacity-30">•</span>
          <a href="#report" className="hover:text-white">Report</a>
        </nav>
      </div>
    </header>
  );
}
