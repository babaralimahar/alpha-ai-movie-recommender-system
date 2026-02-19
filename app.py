import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Alpha Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# ADVANCED 3D & CINEMATIC STYLES
# =============================
st.markdown(
    """
    <style>
    /* App Background - Deep Cinematic Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f1f5f9;
    }

    /* Main App Title - Neon Glow */
    .app-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 20px rgba(0, 242, 254, 0.4);
        margin-bottom: 0px;
        padding-bottom: 0px;
    }

    /* Subtitle / Instructions */
    .small-muted { 
        color: #94a3b8; 
        font-size: 1rem; 
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Movie Title Text */
    .movie-title { 
        font-size: 1.05rem; 
        font-weight: 600;
        line-height: 1.3rem; 
        height: 2.6rem; 
        overflow: hidden; 
        text-align: center;
        margin-top: 12px;
        color: #e2e8f0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* 3D Hover Effect on Images (The Magic) */
    div[data-testid="stImage"] img {
        border-radius: 12px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
    }
    div[data-testid="column"]:hover img {
        transform: translateY(-10px) scale(1.05) perspective(1000px) rotateX(2deg) rotateY(-2deg);
        box-shadow: 15px 25px 30px rgba(0,0,0,0.7);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* 3D Glowing Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 5px;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.7);
        color: white;
    }

    /* Details Page Glassmorphism Card */
    .details-card { 
        border: 1px solid rgba(255,255,255,0.1); 
        border-radius: 20px; 
        padding: 25px; 
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }
    
    /* Search Bar Styling */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }

    /* Developer Credit */
    .developer-credit {
        text-align: center;
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    .developer-name {
        color: #4facfe;
        font-weight: bold;
        letter-spacing: 1px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass

def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()

def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()

# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"

def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols, gap="medium")
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.write("🖼️ No poster")
                
                st.markdown(f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True)
                
                if st.button("Details", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards

def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()
    raw_items = []

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )
    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [{"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]} for x in final_list[:limit]]
    return suggestions, cards

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown("## 🎬 Control Panel")
    if st.button("🏠 Return to Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### 🍿 Feed Settings")
    home_category = st.selectbox(
        "Explore Categories",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid Columns", 4, 8, 5)

    # DEVELOPER CREDIT
    st.markdown("<div class='developer-credit'>Developed by: <br><span class='developer-name'>Babar Ali</span></div>", unsafe_allow_html=True)

# =============================
# HEADER
# =============================
st.markdown("<h1 class='app-title'>Alpha Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Discover your next favorite movie. Search, explore, and let the algorithm do the rest.</div>", unsafe_allow_html=True)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    # Clarified the prompt so users know to press Enter
    typed = st.text_input("🔍 Search by movie title (Press Enter to search)", placeholder="e.g. Inception, The Dark Knight, Interstellar...")

    st.markdown("<br>", unsafe_allow_html=True)

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                # THE AUTOCOMPLETE / SUGGESTIONS DROPDOWN
                if suggestions:
                    labels = ["-- Select an exact match --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("✨ Suggestions (Pick one to view details)", labels, index=0)

                    if selected != "-- Select an exact match --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### 🔎 Search Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
        st.stop()

    # HOME FEED MODE
    st.markdown(f"### 🔥 {home_category.replace('_',' ').title()} Movies")

    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Back Button
    if st.button("← Back to Feed"):
        goto_home()
    st.markdown("<br>", unsafe_allow_html=True)

    # Layout: Poster LEFT, Details RIGHT inside a Glassmorphism Container
    st.markdown("<div class='details-card'>", unsafe_allow_html=True)
    left, right = st.columns([1, 2.5], gap="large")

    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
        else:
            st.write("🖼️ No poster")

    with right:
        st.markdown(f"<h2 style='margin-bottom:0;'>{data.get('title','')}</h2>", unsafe_allow_html=True)
        release = data.get("release_date") or "-"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        
        st.markdown(f"<div style='color: #4facfe; font-weight: bold; margin-bottom: 15px;'>{release} • {genres}</div>", unsafe_allow_html=True)
        st.markdown("### Overview")
        st.write(data.get("overview") or "No overview available.")
        
    st.markdown("</div><br>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.markdown("#### Cinematic Backdrop")
        st.image(data["backdrop_url"], use_container_width=True)

    st.markdown("---")
    st.markdown("<h3 style='text-align: center; color: #4facfe;'>🤖 Alpha's AI Recommendations</h3><br>", unsafe_allow_html=True)

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🎯 Because you liked this (Content-Based AI)")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("<br>#### 🎭 More in these Genres", unsafe_allow_html=True)
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(genre_only, cols=grid_cols, key_prefix="details_genre_fallback")
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")