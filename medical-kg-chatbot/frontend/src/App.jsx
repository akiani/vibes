import { useState, useRef, useEffect } from 'react'

// The last two can only be answered by combining a patient's conditions with
// their medications; the lupus one isn't in the graph at all.
const EXAMPLES = [
  'Which conditions cause fatigue?',
  'Patient P-002 is on several medications — anything to watch for?',
  'Is anything Ada Whitfield takes risky given her conditions?',
  'What treats lupus?',
]

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages, loading])

  async function send(text) {
    const question = text.trim()
    if (!question || loading) return

    // The backend is stateless, so we send the whole conversation each time.
    const history = [...messages, { role: 'user', content: question }]
    setMessages(history)
    setInput('')
    setError(null)
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: history.map(({ role, content }) => ({ role, content })),
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`)
      setMessages([...history, { role: 'assistant', content: data.answer, trace: data.trace }])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container">
      <hgroup>
        <h1>Medical KG Chatbot</h1>
        <p>
          Every answer is grounded in a knowledge graph — expand the trace under any
          reply to see the GraphQL queries behind it. Browse the graph yourself at{' '}
          <a href="/graphql" target="_blank" rel="noreferrer">/graphql</a>.
        </p>
      </hgroup>

      {messages.length === 0 && (
        <article>
          <p><strong>Try asking:</strong></p>
          {EXAMPLES.map((q) => (
            <button key={q} className="outline example" onClick={() => send(q)}>{q}</button>
          ))}
        </article>
      )}

      {messages.map((msg, i) => (
        <article key={i} className={`msg ${msg.role}`}>
          <header>{msg.role === 'user' ? 'You' : 'Assistant'}</header>
          <div className="content">{msg.content}</div>
          {msg.trace?.length > 0 && <Trace trace={msg.trace} />}
        </article>
      ))}

      {loading && <article aria-busy="true">Querying the graph…</article>}
      {error && <article className="error"><strong>Error:</strong> {error}</article>}
      <div ref={bottomRef} />

      <form onSubmit={(e) => { e.preventDefault(); send(input) }}>
        <fieldset role="group">
          <input
            type="text"
            value={input}
            placeholder="Ask about a condition, drug, or patient…"
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>Send</button>
        </fieldset>
      </form>

      <footer><small>Fictional demonstration data. Not medical advice.</small></footer>
    </main>
  )
}

// The point of the demo: the queries that produced the answer above.
function Trace({ trace }) {
  return (
    <details className="trace">
      <summary>{trace.length} graph {trace.length === 1 ? 'query' : 'queries'}</summary>
      {trace.map((step, i) => (
        <div key={i} className="step">
          <small>{step.ok ? `Query ${i + 1}` : `Query ${i + 1} — rejected`}</small>
          <pre><code>{step.query.trim()}</code></pre>
          <small>Result</small>
          <pre className={step.ok ? '' : 'bad'}><code>{step.result}</code></pre>
        </div>
      ))}
    </details>
  )
}
