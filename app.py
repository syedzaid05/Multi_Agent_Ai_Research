import html
import re
import time

import streamlit as st

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain

st.set_page_config(page_title="HYDRA  · Multi-Agent Research Lab", page_icon="🐉", layout="wide")

# ---------------------------------------------------------------- styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;800&family=Source+Serif+4:wght@400;600&family=Manrope:wght@400;500;600;700&display=swap');

:root{
  --bg:#0B1020; --bg2:#0F1630; --card:#141B38; --card2:#1A2347; --line:#27315C;
  --ink:#E8ECFF; --muted:#93A0C8;
  --cyan:#38E1FF; --violet:#8B5CFF; --pink:#FF4FA3; --amber:#FFB84D; --green:#3DDC97; --red:#FF6B6B;
}
.stApp{
  background:
    radial-gradient(900px 500px at 8% -10%, rgba(139,92,255,.22), transparent 60%),
    radial-gradient(800px 480px at 100% 0%, rgba(56,225,255,.13), transparent 60%),
    var(--bg);
  color:var(--ink); font-family:'Manrope',sans-serif;
}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1120px; padding-top:2rem;}
[data-testid="stSidebar"]{background:var(--bg2); border-right:1px solid var(--line);}
[data-testid="stSidebar"] *{color:var(--ink);}
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, label, [data-testid="stCaptionContainer"]{color:var(--ink);}
[data-testid="stCaptionContainer"]{color:var(--muted) !important;}

h1,h2,h3{font-family:'Unbounded',sans-serif !important; color:var(--ink) !important; letter-spacing:-0.02em;}

/* hero */
.hero h1{font-size:4.2rem; font-weight:800; margin:0; line-height:1; letter-spacing:-0.04em;
  background:linear-gradient(95deg,var(--cyan),var(--violet) 55%,var(--pink)); -webkit-background-clip:text; background-clip:text; color:transparent !important;}
.hero .tag{font-family:'Unbounded',sans-serif; font-size:1.1rem; font-weight:500; margin:.8rem 0 .5rem; color:var(--ink);}
.hero p{color:var(--muted); font-size:1.02rem; max-width:62ch; margin:0 0 1rem;}
.chips{display:flex; flex-wrap:wrap; gap:.5rem; margin-bottom:1.2rem;}
.chip{border:1px solid var(--line); background:var(--card); color:var(--ink); border-radius:999px; padding:.3rem .8rem; font-size:.82rem; font-weight:600;}
.chip i{font-style:normal; color:var(--cyan); margin-right:.35rem;}

/* input */
[data-testid="stForm"]{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.1rem 1.2rem;}
.stTextInput input{background:var(--bg) !important; color:var(--ink) !important; border:1.5px solid var(--line) !important; border-radius:12px; font-size:1.05rem; padding:.75rem .95rem;}
.stTextInput input::placeholder{color:#5F6C99 !important;}
.stTextInput input:focus{border-color:var(--cyan) !important; box-shadow:0 0 0 3px rgba(56,225,255,.2) !important;}
.stTextInput label p{color:var(--ink) !important; font-weight:700;}
[data-testid="stFormSubmitButton"] button, .stDownloadButton button{
  background:linear-gradient(95deg,var(--violet),var(--pink)); color:#fff; border:none; border-radius:12px; font-weight:700; padding:.65rem 1.5rem;}
[data-testid="stFormSubmitButton"] button:hover, .stDownloadButton button:hover{filter:brightness(1.12); color:#fff;}
[data-testid="stFormSubmitButton"] button:focus-visible, .stDownloadButton button:focus-visible{outline:3px solid rgba(56,225,255,.5); outline-offset:2px;}
[data-testid="stSidebar"] .stButton button{background:var(--card); border:1px solid var(--line); color:var(--ink); border-radius:10px; text-align:left;}
[data-testid="stSidebar"] .stButton button:hover{border-color:var(--cyan); color:var(--cyan);}

/* pipeline tracker */
.steps{display:grid; grid-template-columns:repeat(4,1fr); gap:.9rem; margin:1.8rem 0 1.4rem;}
.step{--c:var(--cyan); position:relative; padding:1.2rem 1rem 1rem; display:flex; flex-direction:column; gap:.25rem;
  background:var(--card2); border:1px solid var(--c); border-top:5px solid var(--c); border-radius:14px;
  box-shadow:0 0 14px color-mix(in srgb, var(--c) 30%, transparent); transition:all .25s;}
.step:nth-child(1){--c:var(--cyan);}
.step:nth-child(2){--c:var(--violet);}
.step:nth-child(3){--c:var(--pink);}
.step:nth-child(4){--c:var(--amber);}
.step b{font-family:'Unbounded',sans-serif; font-size:1rem; color:var(--c);}
.step small{color:var(--ink); font-size:.86rem; opacity:.9;}
.step .dot{position:absolute; top:-12px; left:14px; width:17px; height:17px; border-radius:50%;
  background:var(--c); border:3px solid var(--bg);}

/* not started yet: still colourful, just slightly calmer */
.step:not(.done):not(.active){opacity:.75; box-shadow:none;}

/* finished */
.step.done{background:linear-gradient(160deg, color-mix(in srgb, var(--c) 28%, var(--card2)), var(--card2));
  box-shadow:0 0 22px color-mix(in srgb, var(--c) 55%, transparent);}
.step.done b::after{content:" ✓"; color:var(--green);}

/* running right now */
.step.active{background:linear-gradient(160deg, color-mix(in srgb, var(--c) 40%, var(--card2)), var(--card2));
  transform:translateY(-4px); animation:glow 1.3s ease-in-out infinite;}
.step.active .dot{animation:pulse 1.3s ease-in-out infinite;}
@keyframes glow{0%,100%{box-shadow:0 0 14px color-mix(in srgb, var(--c) 50%, transparent);}
  50%{box-shadow:0 0 30px color-mix(in srgb, var(--c) 90%, transparent);}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 color-mix(in srgb, var(--c) 70%, transparent);}
  50%{box-shadow:0 0 0 9px transparent;}}
@media (prefers-reduced-motion:reduce){.step.active, .step.active .dot{animation:none;}}
@media (max-width:640px){.steps{grid-template-columns:repeat(2,1fr); row-gap:1.6rem;} .hero h1{font-size:3rem;}}

/* bordered containers (report, panels) */
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--card); border:1px solid var(--line) !important; border-radius:16px;}
[data-testid="stVerticalBlockBorderWrapper"] .stMarkdown p, [data-testid="stVerticalBlockBorderWrapper"] .stMarkdown li{font-family:'Source Serif 4',serif; font-size:1.06rem; line-height:1.75;}
[data-testid="stVerticalBlockBorderWrapper"] h1,[data-testid="stVerticalBlockBorderWrapper"] h2,[data-testid="stVerticalBlockBorderWrapper"] h3{font-size:1.3rem; margin-top:1.2rem;}
.stMarkdown a{color:var(--cyan);}

/* metrics strip */
.metrics{display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; margin:.6rem 0 1.2rem;}
.metric{background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.8rem 1rem;}
.metric .v{font-family:'Unbounded',sans-serif; font-size:1.6rem; font-weight:700; color:var(--ink);}
.metric .l{color:var(--muted); font-size:.82rem;}
@media (max-width:640px){.metrics{grid-template-columns:repeat(2,1fr);}}

/* critic */
.score{display:flex; align-items:baseline; gap:.4rem; margin-bottom:.6rem;}
.score .n{font-family:'Unbounded',sans-serif; font-size:4.2rem; font-weight:800; line-height:1;}
.score .d{font-size:1.4rem; color:var(--muted);}
.bar{height:9px; background:var(--line); border-radius:8px; overflow:hidden; margin-bottom:1.2rem;}
.bar > div{height:100%; border-radius:8px;}
.verdict{border-left:4px solid var(--amber); background:rgba(255,184,77,.1); padding:.8rem 1rem; border-radius:0 12px 12px 0; color:var(--ink);}

/* sources */
.src{display:block; padding:.7rem .9rem; background:var(--card); border:1px solid var(--line); border-radius:12px; margin-bottom:.5rem;
  color:var(--cyan); text-decoration:none; word-break:break-all; font-size:.92rem;}
.src:hover{border-color:var(--cyan);}

/* advantages */
.sec{font-family:'Unbounded',sans-serif; font-size:1.25rem; font-weight:700; margin:2rem 0 .9rem;}
.grid{display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem;}
.adv{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.1rem 1.2rem;}
.adv:hover{border-color:var(--violet);}
.adv .ic{font-size:1.5rem;}
.adv h4{font-family:'Unbounded',sans-serif; font-size:.98rem; margin:.5rem 0 .3rem; color:var(--ink);}
.adv p{color:var(--muted); font-size:.92rem; line-height:1.55; margin:0;}
@media (max-width:900px){.grid{grid-template-columns:repeat(2,1fr);} }
@media (max-width:640px){.grid{grid-template-columns:1fr;} }

/* widgets */
/* result tabs: Report / Critic review / Sources / Raw research (solid, fully opaque) */
[data-baseweb="tab-list"]{gap:.8rem !important; padding:.8rem .4rem 1.2rem !important; border-bottom:none !important; overflow:visible !important; background:transparent !important;}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"]{display:none !important;}
[data-baseweb="tab-list"] button[role="tab"]{
  --c:#00E676; position:relative; height:auto !important; padding:.9rem 1.6rem !important; border-radius:14px !important;
  background:var(--c) !important; background-image:none !important; opacity:1 !important; filter:none !important;
  border:3px solid #0B1020 !important; box-shadow:0 5px 0 #0B1020 !important; transition:transform .15s;}
[data-baseweb="tab-list"] button[role="tab"]:nth-of-type(1){--c:#00E676;}  /* solid green */
[data-baseweb="tab-list"] button[role="tab"]:nth-of-type(2){--c:#FFD600;}  /* solid yellow */
[data-baseweb="tab-list"] button[role="tab"]:nth-of-type(3){--c:#FF6D00;}  /* solid orange */
[data-baseweb="tab-list"] button[role="tab"]:nth-of-type(4){--c:#00B0FF;}  /* solid blue */
[data-baseweb="tab-list"] button[role="tab"] p,
[data-baseweb="tab-list"] button[role="tab"] div{
  font-family:'Unbounded',sans-serif !important; font-size:1.05rem !important; font-weight:800 !important;
  color:#000000 !important; opacity:1 !important; margin:0 !important;}
[data-baseweb="tab-list"] button[role="tab"]:hover{transform:translateY(-3px);}
/* selected tab: white ring + glow + arrow, same solid colour */
[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"]{
  transform:translateY(-5px) scale(1.07); border:3px solid #fff !important;
  box-shadow:0 0 0 4px var(--c), 0 0 34px var(--c), 0 10px 26px rgba(0,0,0,.5) !important;}
[data-baseweb="tab-list"] button[role="tab"][aria-selected="true"]::after{
  content:""; position:absolute; left:50%; bottom:-16px; transform:translateX(-50%);
  border:9px solid transparent; border-top-color:#fff;}
[data-baseweb="tab-list"] button[role="tab"]:focus-visible{outline:3px solid #fff; outline-offset:3px;}
@media (max-width:640px){[data-baseweb="tab-list"]{flex-wrap:wrap;}}
[data-testid="stExpander"]{border:1px solid var(--line); border-radius:12px; background:var(--card);}
[data-testid="stAlert"]{background:#1F2A5C !important; border:2px solid var(--cyan) !important; border-radius:12px; color:#fff !important;}
[data-testid="stAlert"] *{color:#fff !important;}
hr{border-color:var(--line);}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- content
STEPS = [
    ("Deep Search", "Sniffs out live sources"),
    ("Deep Diver", "Scrapes the best page"),
    ("Ghostwriter", "Drafts the report"),
    ("Iron Critic", "Scores it, no mercy"),
]

EXAMPLES = [
    "Solid-state batteries in electric vehicles",
    "How CRISPR is used in agriculture",
    "State of open-source LLMs",
    "Microplastics and human health",
]

STACK = ["LangChain agents", "Google Gemini", "Tavily web search", "Web scraping tool", "Streamlit"]

ADVANTAGES = [
    ("🧠", "Multi-agent, not one prompt",
     "Four specialised agents each own one job, so every stage is testable, swappable and easy to debug."),
    ("🌐", "Grounded in the live web",
     "Real-time search plus page scraping means answers come from today's sources, not stale training data."),
    ("⚖️", "Built-in self-review",
     "A separate critic agent scores every report out of 10 with strengths, gaps and a one-line verdict."),
    ("🔗", "Every claim is traceable",
     "All URLs are pulled into a Sources tab, so a reader can verify where each fact came from."),
    ("🔍", "Fully transparent",
     "The Raw research tab exposes each agent's output. Nothing is a black box."),
    ("⚡", "Ship-ready UX",
     "Live progress tracker, run-time and word-count metrics, graceful errors and one-click Markdown export."),
]


def stepper(active: int, all_done: bool = False) -> str:
    out = '<div class="steps">'
    for i, (name, desc) in enumerate(STEPS):
        cls = "done" if all_done or i < active else ("active" if i == active else "")
        out += f'<div class="step {cls}"><span class="dot"></span><b>{name}</b><small>{desc}</small></div>'
    return out + "</div>"


def text_of(content) -> str:
    """Gemini can return a plain string or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            parts.append(c.get("text", "") if isinstance(c, dict) else str(c))
        return "\n".join(p for p in parts if p)
    return str(content)


def run_pipeline(topic: str, slot) -> dict:
    """Same four steps as pipeline.py, with live progress for the UI."""
    state, t0 = {}, time.time()

    slot.markdown(stepper(0), unsafe_allow_html=True)
    res = build_search_agent().invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    state["search_result"] = text_of(res["messages"][-1].content)

    slot.markdown(stepper(1), unsafe_allow_html=True)
    res = build_reader_agent().invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_result'][:800]}",
                )
            ]
        }
    )
    state["scraped_content"] = text_of(res["messages"][-1].content)

    slot.markdown(stepper(2), unsafe_allow_html=True)
    research = (
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research})

    slot.markdown(stepper(3), unsafe_allow_html=True)
    state["feedback"] = critic_chain.invoke({"report": state["report"]})

    slot.markdown(stepper(4, all_done=True), unsafe_allow_html=True)
    state["topic"] = topic
    state["seconds"] = round(time.time() - t0)
    return state


def parse_feedback(text: str) -> dict:
    score = re.search(r"Score\s*:?\s*(\d+(?:\.\d+)?)\s*/\s*10", text, re.I)
    out = {"score": float(score.group(1)) if score else None, "Strengths": "", "Areas to Improve": "", "Verdict": ""}
    keys = {"strengths": "Strengths", "areas to improve": "Areas to Improve", "one line verdict": "Verdict"}
    current = None
    for line in text.splitlines():
        head = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if head in keys:
            current = keys[head]
            continue
        if current and line.strip():
            out[current] += line.strip() + "\n"
    return out


def extract_urls(*texts: str) -> list:
    seen, urls = set(), []
    for t in texts:
        for u in re.findall(r"https?://[^\s\)\]\"'>]+", t):
            u = u.rstrip(".,;")
            if u not in seen:
                seen.add(u)
                urls.append(u)
    return urls


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### 🐉 HYDRA")
    st.write("Cut one topic, grow four AI heads. Each head does one job, and together they ship a sourced, reviewed report.")
    st.markdown("**Meet the heads**")
    for name, desc in STEPS:
        st.markdown(f"**{name}** · {desc}")
    st.divider()
    st.markdown("**Try a topic**")
    for ex in EXAMPLES:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state["topic_input"] = ex
    st.divider()
    if "result" in st.session_state and st.button("Clear results", use_container_width=True):
        del st.session_state["result"]
        st.rerun()
    st.caption("Needs GOOGLE_API_KEY and TAVILY_API in your .env file.")

# ---------------------------------------------------------------- hero
chips = "".join(f'<span class="chip"><i>●</i>{s}</span>' for s in STACK)
st.markdown(
    '<div class="hero"><h1>HYDRA</h1>'
    '<div class="tag">Four AI heads. One sourced report. Zero blind trust.</div>'
    "<p>Type a topic. Hydra searches the live web, dives into the best page, writes a structured report, "
    "then a merciless critic grades it so you know how far to trust it.</p>"
    f'<div class="chips">{chips}</div></div>',
    unsafe_allow_html=True,
)

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        key="topic_input",
        placeholder="e.g. Solid-state batteries in electric vehicles",
    )
    go = st.form_submit_button("Unleash Hydra")

tracker = st.empty()

if go:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        try:
            st.session_state["result"] = run_pipeline(topic.strip(), tracker)
        except Exception as e:
            tracker.empty()
            st.error(
                f"The pipeline stopped: {e}\n\n"
                "Check that GOOGLE_API_KEY and TAVILY_API are set in .env and that the model name in agents.py is valid."
            )

res = st.session_state.get("result")
EMPTY = "Nothing here yet. Type a topic above and press **Unleash Hydra**."

if res:
    tracker.markdown(stepper(4, all_done=True), unsafe_allow_html=True)
    fb = parse_feedback(res["feedback"])
    urls = extract_urls(res["search_result"], res["scraped_content"], res["report"])
    words = len(res["report"].split())
    score_txt = f"{fb['score']:g}/10" if fb["score"] is not None else "n/a"

    st.markdown(f"## {res['topic']}")
    st.markdown(
        '<div class="metrics">'
        f'<div class="metric"><div class="v">{res["seconds"]}s</div><div class="l">End-to-end run time</div></div>'
        f'<div class="metric"><div class="v">{words}</div><div class="l">Words written</div></div>'
        f'<div class="metric"><div class="v">{len(urls)}</div><div class="l">Sources found</div></div>'
        f'<div class="metric"><div class="v">{score_txt}</div><div class="l">Critic score</div></div>'
        "</div>",
        unsafe_allow_html=True,
    )
elif not go:
    tracker.markdown(stepper(-1), unsafe_allow_html=True)

# tabs are ALWAYS visible, with or without a result
tab_report, tab_review, tab_sources, tab_raw = st.tabs(["📄 Report", "⚖️ Critic review", "🔗 Sources", "🔍 Raw research"])

with tab_report:
    if res:
        with st.container(border=True):
            st.markdown(res["report"])
        st.write("")
        st.download_button(
            "Download report (.md)",
            res["report"],
            file_name=re.sub(r"\W+", "_", res["topic"]).strip("_").lower() + ".md",
            mime="text/markdown",
        )
    else:
        st.info(EMPTY)

with tab_review:
    if res:
        if fb["score"] is not None:
            s = fb["score"]
            color = "#3DDC97" if s >= 8 else "#FFB84D" if s >= 6 else "#FF6B6B"
            st.markdown(
                f'<div class="score"><span class="n" style="color:{color}">{s:g}</span><span class="d">/ 10</span></div>'
                f'<div class="bar"><div style="width:{s * 10}%; background:{color}"></div></div>',
                unsafe_allow_html=True,
            )
        if fb["Strengths"] or fb["Areas to Improve"]:
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.markdown("### Strengths")
                    st.markdown(fb["Strengths"])
            with c2:
                with st.container(border=True):
                    st.markdown("### Areas to improve")
                    st.markdown(fb["Areas to Improve"])
            if fb["Verdict"]:
                st.write("")
                st.markdown(f'<div class="verdict">{html.escape(fb["Verdict"].strip())}</div>', unsafe_allow_html=True)
        else:
            st.markdown(res["feedback"])
    else:
        st.info(EMPTY)

with tab_sources:
    if res:
        if urls:
            for u in urls:
                safe = html.escape(u, quote=True)
                st.markdown(f'<a class="src" href="{safe}" target="_blank" rel="noopener">{safe}</a>', unsafe_allow_html=True)
        else:
            st.info("No URLs were found in the research.")
    else:
        st.info(EMPTY)

with tab_raw:
    if res:
        with st.expander("Bloodhound output (search)", expanded=False):
            st.markdown(res["search_result"])
        with st.expander("Deep Diver output (scrape)", expanded=False):
            st.markdown(res["scraped_content"])
    else:
        st.info(EMPTY)

if not res:
    cards = "".join(
        f'<div class="adv"><div class="ic">{ic}</div><h4>{t}</h4><p>{d}</p></div>' for ic, t, d in ADVANTAGES
    )
    st.markdown(
        f'<div class="sec">Why Hydra beats a single chatbot prompt</div><div class="grid">{cards}</div>',
        unsafe_allow_html=True,
    )


# to run:  python -m streamlit run app.py