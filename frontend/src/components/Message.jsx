export default function Message({ role, text }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm ${isUser ? 'bg-blue-600 text-white' : 'bg-white border'}`}>{text}</div>
    </div>
  )
}
