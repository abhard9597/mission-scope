"""MissionScope: a nebula-themed explorer for space mission history."""

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="MissionScope",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).with_name("space_missions.csv")
NEBULA_PATH = Path(__file__).parent / "assets" / "nebula-background.png"

# A calm, accessible nebula palette: no alert-red chart colours.
COLORS = {
    "background": "#0B1026",
    "surface": "#141B3D",
    "surface_light": "#1C2551",
    "text": "#F1F3FF",
    "muted": "#BEC7EA",
    "blue": "#93C5FD",
    "periwinkle": "#A5B4FC",
    "violet": "#C4B5FD",
    "lavender": "#DDD6FE",
    "aqua": "#99F6E4",
}
OUTCOME_COLORS = {
    "Success": COLORS["aqua"],
    "Failure": COLORS["violet"],
    "Partial Failure": COLORS["periwinkle"],
    "Prelaunch Failure": COLORS["lavender"],
}


@st.cache_data
def background_data_uri(path: Path) -> str:
    """Embed the local reference image so the dashboard has a reliable background."""
    if not path.exists():
        return ""
    return f"data:image/png;base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def apply_theme(background_image: str) -> None:
    """Add a gentle, high-contrast space treatment without heavy visual noise."""
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {COLORS['background']};
                background-image:
                    linear-gradient(180deg, rgba(5, 8, 24, 0.68) 0%, rgba(7, 11, 31, 0.82) 52%, rgba(8, 11, 31, 0.9) 100%),
                    radial-gradient(ellipse 52rem 33rem at 96% -9%, rgba(127, 92, 255, 0.17), transparent 66%),
                    url("{background_image}");
                background-size: cover, auto, cover;
                background-position: center, center, center;
                background-attachment: fixed, fixed, fixed;
                color: {COLORS['text']};
            }}
            .block-container {{ max-width: 1220px; padding-top: 3.4rem; padding-bottom: 4rem; }}
            h1, h2, h3 {{ color: {COLORS['text']} !important; letter-spacing: -0.03em; }}
            h1 {{ font-size: clamp(2.5rem, 6vw, 4.8rem) !important; line-height: 1 !important; margin: 0 !important; }}
            h2 {{ margin-top: 0.25rem !important; }}
            [data-testid="stMetric"] {{
                background: linear-gradient(145deg, rgba(23, 37, 82, 0.92), rgba(18, 24, 59, 0.92));
                border: 1px solid rgba(159, 182, 255, 0.24);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: 0 16px 32px rgba(3, 6, 24, 0.18);
            }}
            [data-testid="stMetricLabel"] {{ color: {COLORS['muted']} !important; }}
            [data-testid="stMetricValue"] {{ color: {COLORS['blue']} !important; }}
            [data-testid="stExpander"] {{
                background: rgba(16, 25, 58, 0.84);
                border: 1px solid rgba(154, 175, 255, 0.24);
                border-radius: 14px;
            }}
            [data-testid="stDataFrame"] {{
                background: rgba(9, 14, 37, 0.78);
                border: 1px solid rgba(154, 175, 255, 0.2);
                border-radius: 14px;
                overflow: hidden;
            }}
            [data-testid="stSidebar"] {{ background: {COLORS['surface']}; }}
            .eyebrow {{
                color: {COLORS['blue']}; font-size: 0.76rem; font-weight: 750;
                letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 0.7rem;
            }}
            .hero-copy {{ color: {COLORS['muted']}; font-size: 1.08rem; line-height: 1.7; max-width: 39rem; }}
            .section-kicker {{ color: {COLORS['blue']}; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }}
            .soft-card {{
                background: rgba(16, 25, 58, 0.78); border: 1px solid rgba(166, 151, 245, 0.24);
                border-radius: 18px; padding: 1.25rem 1.35rem; min-height: 100%;
            }}
            .soft-card strong {{ color: {COLORS['lavender']}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Load and lightly enrich the source CSV without changing source values."""
    df = pd.read_csv(path, encoding="latin-1", dtype={"Price": "string"})
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"].str.replace(",", "", regex=False), errors="coerce")
    df["Year"] = df["Date"].dt.year
    df["Country"] = df["Location"].str.rsplit(",", n=1).str[-1].str.strip()
    return df


def chart_layout(chart: object, title: str, x_title: str | None = None, y_title: str | None = None) -> object:
    """Apply the same quiet, readable presentation to every visualization."""
    return chart.update_layout(
        title={"text": title, "font": {"size": 19, "color": COLORS["text"]}, "x": 0.015},
        paper_bgcolor="rgba(11,16,38,0.64)",
        plot_bgcolor=COLORS["surface"],
        font={"color": COLORS["text"], "family": "Inter, ui-sans-serif, system-ui, sans-serif"},
        legend={"title": {"text": "Mission outcome"}, "orientation": "h", "y": -0.18, "x": 0},
        margin={"l": 18, "r": 18, "t": 58, "b": 52},
        xaxis={"title": x_title, "gridcolor": "rgba(190,199,234,0.11)", "zerolinecolor": "rgba(190,199,234,0.18)"},
        yaxis={"title": y_title, "gridcolor": "rgba(190,199,234,0.11)", "zerolinecolor": "rgba(190,199,234,0.18)"},
    )


def source_statistics(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": ["Mission records", "Source columns", "Launch date range", "Missing launch times", "Missing prices"],
            "Value": [
                f"{len(df):,}",
                str(len(df.columns) - 2),
                f"{df['Date'].min():%d %b %Y} – {df['Date'].max():%d %b %Y}",
                f"{df['Time'].isna().sum():,}",
                f"{df['Price'].isna().sum():,}",
            ],
        }
    )


def ensure_filter_state(df: pd.DataFrame, min_year: int, max_year: int) -> None:
    """Set explorer defaults before the story renders, so upper views stay reactive."""
    st.session_state.setdefault("year_range", (min_year, max_year))
    st.session_state.setdefault("company", sorted(df["Company"].dropna().unique().tolist()))
    st.session_state.setdefault("country", sorted(df["Country"].dropna().unique().tolist()))
    st.session_state.setdefault("outcome", sorted(df["MissionStatus"].dropna().unique().tolist()))
    st.session_state.setdefault("rocket_status", sorted(df["RocketStatus"].dropna().unique().tolist()))


def exploration_filters(df: pd.DataFrame, min_year: int, max_year: int) -> None:
    """Render detailed controls late in the story while keeping all views reactive."""
    with st.expander("Fine-tune this mission view", expanded=False):
        st.caption("All charts and headline figures above update as soon as you change a selection.")
        st.slider("Launch year", min_year, max_year, key="year_range", help="Inclusive launch-year range.")
        left, right = st.columns(2, gap="large")
        with left:
            st.multiselect("Launch provider", sorted(df["Company"].dropna().unique().tolist()), key="company")
            st.multiselect("Launch country", sorted(df["Country"].dropna().unique().tolist()), key="country")
        with right:
            st.multiselect("Mission outcome", sorted(df["MissionStatus"].dropna().unique().tolist()), key="outcome")
            st.multiselect("Rocket status", sorted(df["RocketStatus"].dropna().unique().tolist()), key="rocket_status")


def main() -> None:
    background_image = background_data_uri(NEBULA_PATH) if NEBULA_PATH.exists() else ""
    apply_theme(background_image)
    if not DATA_PATH.exists():
        st.error(f"Dataset not found: {DATA_PATH.name}")
        st.stop()

    df = load_data(DATA_PATH)
    min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
    ensure_filter_state(df, min_year, max_year)
    year_range = st.session_state["year_range"]
    companies = st.session_state["company"]
    countries = st.session_state["country"]
    outcomes = st.session_state["outcome"]
    rocket_statuses = st.session_state["rocket_status"]

    hero, mission_note = st.columns([1.65, 1], gap="large")
    with hero:
        st.markdown('<div class="eyebrow">A gentle archive of human launch history</div>', unsafe_allow_html=True)
        st.title("MissionScope")
        st.markdown(
            '<div class="hero-copy">Follow the arc of spaceflight—from the first satellite launches to modern missions. '
            'MissionScope turns a historical launch archive into a calm place to explore who launched, when they flew, and how missions turned out.</div>',
            unsafe_allow_html=True,
        )
    with mission_note:
        st.markdown("<div style='height: 2.5rem'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='soft-card'><div class='section-kicker'>Archive window</div><br><strong>{min_year} — {max_year}</strong><br><span style='color: {COLORS['muted']}'>A shared history of {len(df):,} recorded launches.</span></div>",
            unsafe_allow_html=True,
        )

    filtered = df.loc[
        df["Year"].between(*year_range)
        & df["Company"].isin(companies)
        & df["Country"].isin(countries)
        & df["MissionStatus"].isin(outcomes)
        & df["RocketStatus"].isin(rocket_statuses)
    ].copy()

    mission_count = len(filtered)
    success_rate = (filtered["MissionStatus"] == "Success").mean() * 100 if mission_count else 0
    st.markdown("<br><div class='section-kicker'>Mission briefing</div>", unsafe_allow_html=True)
    st.markdown("## The story at a glance")
    st.caption("These signals reflect the current mission view.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Visible missions", f"{mission_count:,}")
    c2.metric("Mission success", f"{success_rate:.1f}%")
    c3.metric("Launch providers", filtered["Company"].nunique())
    c4.metric("Years in view", f"{year_range[1] - year_range[0] + 1}")

    if filtered.empty:
        st.markdown("<br><div class='section-kicker'>Mission timeline</div>", unsafe_allow_html=True)
        st.markdown("## No missions in this orbit")
        st.info("This combination has no recorded missions. Expand **Explore the Data** below and widen a selection to bring the launch history back into view.")
    else:
        st.markdown("<br><div class='section-kicker'>Mission timeline</div>", unsafe_allow_html=True)
        st.markdown("## A history of launches")
        st.caption("Mission activity over time, layered by outcome. This is the main view of the archive.")
        by_year = filtered.groupby(["Year", "MissionStatus"], as_index=False).size().rename(columns={"size": "Missions"})
        timeline = px.bar(
            by_year, x="Year", y="Missions", color="MissionStatus", barmode="stack",
            color_discrete_map=OUTCOME_COLORS, hover_data={"Year": ":.0f", "Missions": ":.0f"},
        )
        st.plotly_chart(chart_layout(timeline, "Launch timeline", "Launch year", "Mission count"), width="stretch")

        st.markdown("<br><div class='section-kicker'>Launch landscape</div>", unsafe_allow_html=True)
        st.markdown("## Who launches the most?")
        st.caption("The providers and countries with the greatest number of recorded missions in this view.")
        by_provider = filtered["Company"].value_counts().head(10).rename_axis("Company").reset_index(name="Missions")
        country_counts = filtered["Country"].value_counts().head(10).rename_axis("Country").reset_index(name="Missions")
        left, right = st.columns(2, gap="large")
        with left:
            provider_chart = px.bar(by_provider.sort_values("Missions"), x="Missions", y="Company", orientation="h", color_discrete_sequence=[COLORS["violet"]], text_auto=True)
            provider_chart.update_layout(showlegend=False)
            st.plotly_chart(chart_layout(provider_chart, "Leading launch providers", "Mission count", "Provider"), width="stretch")
        with right:
            country_chart = px.bar(country_counts, x="Country", y="Missions", color_discrete_sequence=[COLORS["blue"]], text_auto=True)
            country_chart.update_layout(showlegend=False)
            st.plotly_chart(chart_layout(country_chart, "Leading launch countries", "Launch country", "Mission count"), width="stretch")

        st.markdown("<br><div class='section-kicker'>Mission outcomes</div>", unsafe_allow_html=True)
        st.markdown("## How did missions turn out?")
        outcome_counts = filtered["MissionStatus"].value_counts().rename_axis("MissionStatus").reset_index(name="Missions")
        outcome_left, outcome_right = st.columns([1.1, 0.9], gap="large")
        with outcome_left:
            outcome_chart = px.pie(outcome_counts, names="MissionStatus", values="Missions", hole=0.64, color="MissionStatus", color_discrete_map=OUTCOME_COLORS)
            outcome_chart.update_traces(textinfo="percent+label", textfont={"color": COLORS["text"]})
            st.plotly_chart(chart_layout(outcome_chart, "Outcome share", None, None), width="stretch")
        with outcome_right:
            st.markdown("<div style='height: 3.2rem'></div>", unsafe_allow_html=True)
            st.markdown("<div class='soft-card'><div class='section-kicker'>Read the signal</div><br>"
                        f"<strong>{success_rate:.1f}%</strong> of the visible missions are recorded as successful. "
                        "Use the explorer below to compare a provider, era, country, or rocket status.</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div class='section-kicker'>Explore the data</div>", unsafe_allow_html=True)
    st.markdown("## Choose your own mission view")
    st.caption("Detailed controls and the mission-level archive live here, so the story above stays easy to scan.")

    exploration_filters(df, min_year, max_year)
    st.markdown("### Source dataset profile")
    st.dataframe(source_statistics(df), hide_index=True, width="stretch")
    st.markdown("### Mission records")
    if filtered.empty:
        st.caption("No records to display for the active selection.")
    else:
        st.caption(f"{mission_count:,} filtered records, newest launches first.")
        display_columns = ["Company", "Location", "Date", "Time", "Rocket", "Mission", "RocketStatus", "Price", "MissionStatus"]
        st.dataframe(
            filtered[display_columns].sort_values("Date", ascending=False),
            hide_index=True,
            width="stretch",
            column_config={
                "Date": st.column_config.DateColumn("Launch date", format="DD MMM YYYY"),
                "Time": st.column_config.TextColumn("Launch time"),
                "RocketStatus": st.column_config.TextColumn("Rocket status"),
                "MissionStatus": st.column_config.TextColumn("Mission outcome"),
                "Price": st.column_config.NumberColumn("Price", format="%.2f"),
            },
        )


if __name__ == "__main__":
    main()
