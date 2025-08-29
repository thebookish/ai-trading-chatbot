import { useEffect, useRef, useState } from 'react'
import { ask, createTrade, listSymbols } from '../api'
import Message from './Message'
import SymbolBadge from './SymbolBadge'

const EXAMPLES = [
  "what is the market value of SX5E?",
  "price of DAX",
  "buy 10 SX5E @ 4200",
  "sell 5 DAX @ 17650",
  "list trades",
  "mark trade 1 executed",
  "cancel trade 2"
]

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [symbols, setSymbols] = useState({ supported: [], mapping: {} })
  const endRef = useRef(null)

  useEffect(() => { (async () => setSymbols(await listSymbols()))() }, [])
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text) => {
    if (!text.trim()) return
    setMessages(m => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const res = await ask(text)
      setMessages(m => [...m, { role: 'assistant', text: res.answer }])
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', text: `Error: ${String(e)}` }])
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  const quick = (t) => send(t)

  return (
    <div className="bg-white rounded-2xl shadow p-4 border h-full flex flex-col">
      <div className="mb-3">
        <h3 className="text-lg font-semibold">Chat</h3>
        <p className="text-xs text-neutral-500">Supported symbols:&nbsp;
          {symbols.supported.slice(0, 12).map((s, i) => <SymbolBadge key={i} sym={s} />)}
          {symbols.supported.length > 12 ? <span className="text-xs text-neutral-400">…</span> : null}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto bg-neutral-50 rounded-xl p-3 border">
        {messages.length === 0 && (
          <div className="text-sm text-neutral-500">
            Try one of these:
            <div className="mt-2 flex flex-wrap gap-2">
              {EXAMPLES.map((e, i) => (
                <button key={i} onClick={() => quick(e)} className="text-xs px-2 py-1 rounded bg-neutral-200 hover:bg-neutral-300">{e}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => <Message key={i} role={m.role} text={m.text} />)}
        <div ref={endRef} />
      </div>

      <form className="mt-3 flex gap-2" onSubmit={e => { e.preventDefault(); send(input) }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask e.g. 'price of SX5E' or 'buy 3 SX5E @ 4200'" className="flex-1 border rounded-xl px-3 py-2 focus:outline-none focus:ring-2" />
        <button disabled={loading} className="px-4 py-2 rounded-xl bg-blue-600 text-white disabled:opacity-50">{loading ? '…' : 'Send'}</button>
      </form>
    </div>
  )
}
