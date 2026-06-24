import { useState } from "react"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const EXAMPLE_QUESTIONS = [
  "What is the habitat of the Indian Peafowl?",
  "What does the Great Hornbill eat?",
  "Describe the Sarus Crane",
  "How does the Baya Weaver build its nest?"
]

function Badge({ label, color }) {
  const colors = {
    green: { bg: "#eef3ee", text: "#3d6b3d", border: "#c3d9c3" },
    amber: { bg: "#fdf4e7", text: "#8a5010", border: "#f0d9b5" },
    blue: { bg: "#eef2ff", text: "#3730a3", border: "#c7d2fe" },
  }
  const c = colors[color] || colors.green
  return (
    <span style={{
      display: "inline-flex",
      alignItems: "center",
      padding: "2px 10px",
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 500,
      fontFamily: "var(--font-mono)",
      background: c.bg,
      color: c.text,
      border: `1px solid ${c.border}`,
    }}>
      {label}
    </span>
  )
}

function SourceCard({ source }) {
  return (
    <a
      href={source.url || "#"}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: "block",
        padding: "10px 14px",
        background: "var(--white)",
        border: "1px solid var(--border)",
        borderRadius: 8,
        textDecoration: "none",
        color: "var(--ink)",
        transition: "border-color 0.15s",
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "var(--sage)"}
      onMouseLeave={e => e.currentTarget.style.borderColor = "var(--border)"}
    >
      <div style={{ fontWeight: 600, fontSize: 14 }}>{source.species}</div>
      <div style={{ fontSize: 12, color: "var(--slate)", marginTop: 2 }}>
        {source.source} {source.url ? "↗" : ""}
      </div>
    </a>
  )
}

export default function App() {
  const [question, setQuestion] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleAsk(q) {
    const query = q || question
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query })
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleExample(q) {
    setQuestion(q)
    handleAsk(q)
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--mist)" }}>

      {/* Header */}
      <header style={{
        borderBottom: "1px solid var(--border)",
        background: "var(--white)",
        padding: "0 24px",
      }}>
        <div style={{ maxWidth: 800, margin: "0 auto", padding: "16px 0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 24 }}>🪶</span>
            <div>
                
              <div style={{ fontFamily: "var(--font-display)", fontSize: 20, color: "var(--ink)" }}>Pakshi Search</div>
              <div style={{ fontSize: 11, color: "var(--slate)", fontFamily: "var(--font-mono)" }}>Explore bird species, habitats, and behavior</div>
            </div>
          </div>
          {/* <Badge label="Atlas Search" color="green" /> */}
        </div>
      </header>

      <main style={{ maxWidth: 800, margin: "0 auto", padding: "40px 24px" }}>

        {/* Hero */}
        <div style={{ marginBottom: 32, textAlign: "center" }}>
          <h1 style={{
            fontFamily: "var(--font-display)",
            fontSize: 36,
            fontWeight: 400,
            color: "var(--ink)",
            lineHeight: 1.2,
            marginBottom: 12
          }}>
          Discover India's Birdlife
          </h1>
          <p style={{ color: "var(--slate)", fontSize: 15 }}>
             Explore bird habitats, diets, behavior, migration, and conservation.
          </p>
        </div>

        {/* Search */}
        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleAsk()}
            placeholder="e.g. What do flamingos eat?"
            style={{
              flex: 1,
              padding: "13px 16px",
              fontSize: 15,
              borderRadius: 10,
              border: "1.5px solid var(--border)",
              background: "var(--white)",
              color: "var(--ink)",
              outline: "none",
              fontFamily: "var(--font-body)",
              transition: "border-color 0.15s"
            }}
            onFocus={e => e.target.style.borderColor = "var(--sage)"}
            onBlur={e => e.target.style.borderColor = "var(--border)"}
          />
          <button
            onClick={() => handleAsk()}
            disabled={loading || !question.trim()}
            style={{
              padding: "13px 24px",
              borderRadius: 10,
              background: loading ? "var(--slate)" : "var(--sage)",
              color: "var(--white)",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "var(--font-body)",
              fontWeight: 600,
              fontSize: 15,
              transition: "background 0.15s",
              whiteSpace: "nowrap"
            }}
          >
            {loading ? "Searching…" : "Ask"}
          </button>
        </div>

        {/* Example questions */}
        {!result && !loading && (
          <div style={{ marginBottom: 32 }}>
            <div style={{ fontSize: 12, color: "var(--slate)", marginBottom: 8, fontWeight: 500 }}>Try an example</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {EXAMPLE_QUESTIONS.map(q => (
                <button
                  key={q}
                  onClick={() => handleExample(q)}
                  style={{
                    padding: "6px 14px",
                    borderRadius: 999,
                    border: "1px solid var(--border)",
                    background: "var(--white)",
                    color: "var(--slate)",
                    fontSize: 13,
                    cursor: "pointer",
                    fontFamily: "var(--font-body)",
                    transition: "all 0.15s"
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--sage)"; e.currentTarget.style.color = "var(--sage)" }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border)"; e.currentTarget.style.color = "var(--slate)" }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            padding: 16,
            background: "#fef2f2",
            border: "1px solid #fecaca",
            borderRadius: 10,
            color: "#991b1b",
            fontSize: 14,
            marginBottom: 24
          }}>
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{
            padding: 32,
            textAlign: "center",
            color: "var(--slate)",
            fontSize: 14,
            fontFamily: "var(--font-mono)"
          }}>
            Searching bird knowledge base…
          </div>
        )}

        {/* Result */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Bird Knowledge */}
            <div style={{
              padding: 24,
              background: "var(--white)",
              border: "1px solid var(--border)",
              borderRadius: 12,
            }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: "var(--sage)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", marginBottom: 12 }}>
                Bird Knowledge
              </div>
              <p style={{ fontSize: 15, lineHeight: 1.75, color: "var(--ink)" }}>
                {result.answer}
              </p>
            </div>

            {/* Retrieved Species */}
{result.sources?.length > 0 && (
  <div
    style={{
      padding: 20,
      background: "var(--white)",
      border: "1px solid var(--border)",
      borderRadius: 12,
    }}
  >
    <div
      style={{
        fontSize: 11,
        fontWeight: 600,
        color: "var(--slate)",
        fontFamily: "var(--font-mono)",
        letterSpacing: "0.08em",
        marginBottom: 12,
      }}
    >
      RETRIEVED SPECIES
    </div>

    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 8,
      }}
    >
      {result.sources.map((s, i) => (
        <Badge key={i} label={s.species} color="green" />
      ))}
    </div>
  </div>
)}

            {/* Sources */}
            {result.sources?.length > 0 && (
              <div>
                <div style={{ fontSize: 11, fontWeight: 600, color: "var(--slate)", fontFamily: "var(--font-mono)", letterSpacing: "0.08em", marginBottom: 10 }}>
                  SOURCES ({result.sources.length})
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 8 }}>
                  {result.sources.map((s, i) => (
                    <SourceCard key={i} source={s} />
                  ))}
                </div>
              </div>
            )}

            {/* Ask another */}
            <button
              onClick={() => { setResult(null); setQuestion("") }}
              style={{
                alignSelf: "flex-start",
                padding: "8px 16px",
                borderRadius: 8,
                border: "1px solid var(--border)",
                background: "transparent",
                color: "var(--slate)",
                fontSize: 13,
                cursor: "pointer",
                fontFamily: "var(--font-body)"
              }}
            >
              ← Ask another question
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border)",
        padding: "16px 24px",
        textAlign: "center",
        fontSize: 12,
        color: "var(--slate)",
        fontFamily: "var(--font-mono)"
      }}>
        Powered by MongoDB Atlas Search • Groq Llama 3.1 • Knowledge sourced from Wikipedia      </footer>
    </div>
  )
}