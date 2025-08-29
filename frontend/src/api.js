export async function ask(message) {
  const res = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getTrades() {
  const res = await fetch('/api/trades')
  return res.json()
}

export async function createTrade(payload) {
  const res = await fetch('/api/trades', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function patchTrade(id, payload) {
  const res = await fetch(`/api/trades/${id}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function deleteTrade(id) {
  const res = await fetch(`/api/trades/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function listSymbols() {
  const res = await fetch('/api/symbols')
  return res.json()
}
