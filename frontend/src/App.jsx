import { useEffect, useState } from 'react'
import { EVENTS, NARRATIVES, PERSONA_TYPES, POSTS } from './data'
import './App.css'

const START = new Date(2025, 2, 1)
const DAYS = 30
const NAV = ['Feed', 'Source events', 'Personas', 'Scenario & export']

const initials = (name) => name.match(/\b[A-Z]/g).join('').slice(0, 2)

function Chips({ options, value, onChange, allLabel }) {
  return (
    <div className="chips">
      {[null, ...options].map((o) => (
        <button key={o ?? 'all'} className={`chip ${value === o ? 'on' : ''}`}
          aria-pressed={value === o} onClick={() => onChange(o)}>
          {o ?? allLabel}
        </button>
      ))}
    </div>
  )
}

function Post({ p }) {
  return (
    <article className="post">
      <div className="avatar" style={{ background: p.color }} aria-hidden>{initials(p.name)}</div>
      <div className="post-body">
        <header>
          <strong>{p.name}</strong>
          <span className="muted">@{p.handle} · {p.time}</span>
          <span className="tag">{p.type}</span>
          <span className="tag synthetic">SYNTHETIC</span>
        </header>
        <p>{p.text}</p>
        <div className="refs">
          <span className="ref event">{p.event} · {EVENTS[p.event]}</span>
          <span className="ref">{p.narrative}</span>
        </div>
        <footer>
          <span>💬 {p.replies} replies</span>
          <span>🔁 {p.reposts} reposts</span>
          <span>♡ {p.likes} likes</span>
          <a href={`#trace/${p.id}`} className="trace">Trace</a>
        </footer>
      </div>
    </article>
  )
}

export default function App() {
  const [day, setDay] = useState(12)
  const [playing, setPlaying] = useState(false)
  const [narrative, setNarrative] = useState(null)
  const [ptype, setPtype] = useState(null)
  const [query, setQuery] = useState('')
  const [event, setEvent] = useState('')
  const [from, setFrom] = useState('2025-03-01')
  const [to, setTo] = useState('2025-03-30')

  useEffect(() => {
    if (!playing) return
    if (day >= DAYS) return setPlaying(false)
    const t = setTimeout(() => setDay(day + 1), 800)
    return () => clearTimeout(t)
  }, [playing, day])

  const date = new Date(START)
  date.setDate(day)
  const q = query.trim().toLowerCase()
  // ponytail: client-side filter over sample data; time range is UI-only until posts carry real dates from the API
  const posts = POSTS.filter((p) =>
    (!narrative || p.narrative === narrative) &&
    (!ptype || p.type === ptype) &&
    (!event || p.event === event) &&
    (!q || p.name.toLowerCase().includes(q) || p.handle.includes(q) || p.id.toLowerCase().includes(q)))
  const traced = posts.length ? Math.round((posts.filter((p) => EVENTS[p.event]).length / posts.length) * 100) : 0

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">S</div>
          <div><strong>SynthFeed</strong><div className="muted">ARCONTRA sandbox</div></div>
        </div>
        <nav>
          {NAV.map((n, i) => (
            <a key={n} href="#" className={i === 0 ? 'active' : ''} aria-current={i === 0 ? 'page' : undefined}>{n}</a>
          ))}
        </nav>
        <div className="card scenario">
          <div className="eyebrow">ACTIVE SCENARIO</div>
          <strong>[Scenario name]</strong>
          <div className="muted">[Region] · 30 days · seed 4821</div>
        </div>
      </aside>

      <main className="feed">
        <div className="feed-head">
          <div className="title-row">
            <h1>Feed</h1>
            <span className="banner">All content is synthetic</span>
          </div>
          <div className="replay">
            <button className="play" onClick={() => setPlaying(!playing)} aria-label={playing ? 'Pause replay' : 'Play replay'}>
              {playing ? '❚❚' : '▶'}
            </button>
            <span className="muted">Replay day <strong>{day}</strong> / {DAYS}</span>
            <input type="range" min="1" max={DAYS} value={day} onChange={(e) => setDay(+e.target.value)} aria-label="Replay day" />
            <span className="muted">{date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
          </div>
        </div>
        <div className="narratives">
          <Chips options={NARRATIVES} value={narrative} onChange={setNarrative} allLabel="All narratives" />
        </div>
        {posts.map((p) => <Post key={p.id} p={p} />)}
        {!posts.length && <p className="empty muted">No posts match these filters.</p>}
      </main>

      <aside className="filters">
        <section className="card panel">
          <h2>Filter activity</h2>
          <h3>Time</h3>
          <div className="dates">
            <label>From<input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
            <label>To<input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
          </div>
          <h3>Persona type</h3>
          <Chips options={PERSONA_TYPES} value={ptype} onChange={setPtype} allLabel="All" />
          <h3><label htmlFor="persona">Persona</label></h3>
          <input id="persona" placeholder="Search name or ID" value={query} onChange={(e) => setQuery(e.target.value)} />
          <h3><label htmlFor="event">Source event</label></h3>
          <select id="event" value={event} onChange={(e) => setEvent(e.target.value)}>
            <option value="">All events (1,000)</option>
            {Object.entries(EVENTS).map(([id, name]) => <option key={id} value={id}>{id} · {name}</option>)}
          </select>
        </section>
        <section className="card stats">
          <h2>Showing</h2>
          <div className="stat-row">
            <div><div className="big">{posts.length}</div><div className="muted">posts in view</div></div>
            <div><div className="big">{traced}%</div><div className="muted">traced to an event</div></div>
          </div>
        </section>
      </aside>
    </div>
  )
}
