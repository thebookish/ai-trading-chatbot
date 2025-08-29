import Chat from './components/Chat'
import TradesPanel from './components/TradesPanel'

export default function App() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">AI Trading Chatbot</h1>
          <p className="text-sm text-neutral-600">Ask for index levels (e.g., SX5E) and manage trades.</p>
        </header>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-[70vh]"><Chat /></div>
          <div><TradesPanel /></div>
        </div>
      </div>
    </div>
  )
}
