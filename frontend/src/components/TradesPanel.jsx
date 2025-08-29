import { useEffect, useState } from 'react'
import { getTrades, patchTrade, deleteTrade } from '../api'

export default function TradesPanel() {
  const [trades, setTrades] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = async () => {
    try {
      setLoading(true)
      const data = await getTrades()
      setTrades(data)
    } catch (e) { setError(String(e)) } finally { setLoading(false) }
  }

  useEffect(() => { refresh() }, [])

  const markExecuted = async (id) => { await patchTrade(id, { status: 'executed' }); refresh() }
  const remove = async (id) => { await deleteTrade(id); refresh() }

  return (
    <div className="bg-white rounded-2xl shadow p-4 border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Trades</h3>
        <button className="text-sm underline" onClick={refresh}>refresh</button>
      </div>
      {loading ? <div className="text-sm text-neutral-500">Loading…</div> : null}
      {error ? <div className="text-sm text-red-600">{error}</div> : null}
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-neutral-500">
              <th className="py-2 pr-4">#</th>
              <th className="py-2 pr-4">Symbol</th>
              <th className="py-2 pr-4">Side</th>
              <th className="py-2 pr-4">Qty</th>
              <th className="py-2 pr-4">Price</th>
              <th className="py-2 pr-4">Status</th>
              <th className="py-2 pr-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(t => (
              <tr key={t.id} className="border-t">
                <td className="py-2 pr-4">{t.id}</td>
                <td className="py-2 pr-4 font-mono">{t.symbol}</td>
                <td className="py-2 pr-4 capitalize">{t.side}</td>
                <td className="py-2 pr-4">{t.quantity}</td>
                <td className="py-2 pr-4">{t.price}</td>
                <td className="py-2 pr-4 capitalize">{t.status}</td>
                <td className="py-2 pr-4 space-x-2">
                  <button onClick={() => markExecuted(t.id)} className="px-2 py-1 rounded bg-green-600 text-white text-xs">Mark executed</button>
                  <button onClick={() => remove(t.id)} className="px-2 py-1 rounded bg-red-600 text-white text-xs">Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
