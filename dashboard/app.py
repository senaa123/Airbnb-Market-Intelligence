"""
app.py
Streamlit dashboard for the Bangkok Airbnb analysis project.
Usage: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
import duckdb
import joblib
import plotly.express as px
import plotly.graph_objects as go
from src.utils.config import load_config

st.set_page_config(page_title="Bangkok Airbnb Market Analysis", layout="wide", page_icon="🏠")

# ---- Dark palette: Slate Blue & Charcoal ----
COLOR_BG = "#0F1419"
COLOR_CARD = "#1A1F26"
COLOR_PRIMARY = "#5B8AB8"
COLOR_SECONDARY = "#8FA8BD"
COLOR_MUTED = "#5C6773"
COLOR_TEXT = "#E8EAED"
COLOR_TEXT_MUTED = "#A8B2BD"
COLOR_BORDER = "#2A313C"
COLOR_HIGHLIGHT = "#D98C4A"
COLOR_TERTIARY = "#3D5A73"

st.markdown(f"""
    <style>
        div[data-testid="stMetric"] {{
            background-color: {COLOR_CARD};
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 16px 20px;
        }}
        div[data-testid="stMetricLabel"] {{ color: {COLOR_TEXT_MUTED}; font-size: 0.85rem; }}
        div[data-testid="stMetricValue"] {{ color: {COLOR_PRIMARY}; font-weight: 700; }}
        h1, h2, h3 {{ color: {COLOR_TEXT}; }}
        .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
    </style>
""", unsafe_allow_html=True)


def styled_chart(fig, height=420):
    fig.update_layout(
        plot_bgcolor=COLOR_CARD, paper_bgcolor=COLOR_CARD, font_color=COLOR_TEXT,
        margin=dict(l=10, r=10, t=30, b=10), height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=False, linecolor=COLOR_BORDER)
    fig.update_yaxes(showgrid=True, gridcolor=COLOR_BORDER, linecolor=COLOR_BORDER)
    return fig


@st.cache_resource
def get_connection():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    db_path = processed_dir / f"{city}_warehouse.duckdb"
    return duckdb.connect(str(db_path), read_only=True), city, processed_dir


con, city, processed_dir = get_connection()

st.markdown(f"""
    <div style="
        background-color: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        border-left: 4px solid {COLOR_PRIMARY};
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
    ">
        <h1 style="margin: 0; color: {COLOR_TEXT}; font-size: 1.8rem;">
            {city.title()} Airbnb Market Analysis
        </h1>
        <p style="margin: 6px 0 0 0; color: {COLOR_TEXT_MUTED}; font-size: 1.0rem;">
            Data source: Inside Airbnb &nbsp;·&nbsp; Scope: Data Engineering, EDA, Statistics, ML
            &nbsp;·&nbsp; 28,697 listings analyzed &nbsp; (290 excluded as fake placeholder prices)
        </p>
    </div>
""", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Price Explorer", "Map", "Segments", "Price Predictor"]
)

# ============================================================
# TAB 1: OVERVIEW — more density: 6 metrics + 3 charts instead of 4+2
# ============================================================
with tab1:
    metrics = con.execute("""
        SELECT
            COUNT(*) AS total_listings,
            ROUND(MEDIAN(price), 2) AS median_price,
            ROUND(AVG(price), 2) AS mean_price,
            ROUND(AVG(occupancy_rate_pct), 1) AS avg_occupancy,
            COUNT(DISTINCT host_id) AS total_hosts,
            ROUND(AVG(review_scores_rating), 2) AS avg_rating
        FROM fact_listings
        WHERE NOT price_likely_artifact AND price IS NOT NULL
    """).df().iloc[0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Listings", f"{int(metrics['total_listings']):,}")
    c2.metric("Median Price", f"฿{metrics['median_price']:,.0f}")
    c3.metric("Mean Price", f"฿{metrics['mean_price']:,.0f}")
    c4.metric("Avg Occupancy", f"{metrics['avg_occupancy']}%")
    c5.metric("Total Hosts", f"{int(metrics['total_hosts']):,}")
    c6.metric("Avg Rating", f"{metrics['avg_rating']}★")

    st.write("")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        with st.container(border=True):
            st.subheader("Room Type Distribution")
            room_dist = con.execute("""
                SELECT p.room_type, COUNT(*) AS n
                FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
                WHERE NOT f.price_likely_artifact
                GROUP BY p.room_type ORDER BY n DESC
            """).df()
            fig = px.bar(room_dist, x="room_type", y="n", color_discrete_sequence=[COLOR_PRIMARY])
            fig.update_layout(xaxis_title="", yaxis_title="Listings", showlegend=False)
            st.plotly_chart(styled_chart(fig, height=320), width="stretch")
            st.caption("Entire home/apt dominates supply; private/shared/hotel rooms are a small minority.")

    with col_b:
        with st.container(border=True):
            st.subheader("Host Concentration")
            host_counts = con.execute("""
                SELECT host_id, COUNT(*) AS n_listings
                FROM fact_listings GROUP BY host_id ORDER BY n_listings DESC
            """).df()
            fig2 = px.histogram(host_counts, x="n_listings", nbins=50, log_y=True,
                                 color_discrete_sequence=[COLOR_SECONDARY])
            fig2.update_layout(xaxis_title="Listings/Host", yaxis_title="Hosts (log)")
            st.plotly_chart(styled_chart(fig2, height=320), width="stretch")
            st.caption("Top 1% of hosts (79) control 21.8% of all listings")

    with col_c:
        with st.container(border=True):
            st.subheader("Top Neighbourhoods by Volume")
            top_neigh = con.execute("""
                SELECT neighbourhood, neighbourhood_listing_count
                FROM dim_neighbourhood ORDER BY neighbourhood_listing_count DESC LIMIT 8
            """).df()
            fig3 = px.bar(top_neigh, x="neighbourhood_listing_count", y="neighbourhood", orientation="h",
                           color_discrete_sequence=[COLOR_PRIMARY])
            fig3.update_layout(xaxis_title="Listings", yaxis_title="", yaxis=dict(autorange="reversed"))
            st.plotly_chart(styled_chart(fig3, height=320), width="stretch")
            st.caption("Vadhana alone outlists the next two neighbourhoods combined.")
            
    st.write("")
    col_d, col_e = st.columns(2)

    with col_d:
        with st.container(border=True):
            st.subheader("Review Score Distribution")
            ratings = con.execute("""
                SELECT review_scores_rating FROM fact_listings
                WHERE review_scores_rating IS NOT NULL
            """).df()
            fig4 = px.histogram(ratings, x="review_scores_rating", nbins=30,
                                 color_discrete_sequence=[COLOR_PRIMARY])
            fig4.update_layout(xaxis_title="Rating", yaxis_title="Listings")
            st.plotly_chart(styled_chart(fig4, height=300), width="stretch")
            st.caption("59.5% of listings rated ≥4.8 — a compressed, inflated scale")

    with col_e:
        with st.container(border=True):
            st.subheader("Occupancy by Room Type")
            monthly = con.execute("""
                SELECT p.room_type, ROUND(AVG(f.occupancy_rate_pct),1) as avg_occ
                FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
                WHERE NOT f.price_likely_artifact
                GROUP BY p.room_type ORDER BY avg_occ DESC
            """).df()
            fig5 = px.bar(monthly, x="room_type", y="avg_occ", color_discrete_sequence=[COLOR_TERTIARY])
            fig5.update_layout(xaxis_title="", yaxis_title="Avg Occupancy %")
            st.plotly_chart(styled_chart(fig5, height=300), width="stretch")
            st.caption("Entire home/apt has the highest occupancy (~26%); Shared room the lowest (~8%).")

# ============================================================
# TAB 2: PRICE EXPLORER
# ============================================================
with tab2:
    st.subheader("Explore Pricing by Room Type & Neighbourhood")

    room_types = con.execute("SELECT DISTINCT room_type FROM dim_property ORDER BY room_type").df()["room_type"].tolist()
    neighbourhoods = con.execute("""
        SELECT neighbourhood FROM dim_neighbourhood
        ORDER BY neighbourhood_listing_count DESC LIMIT 15
    """).df()["neighbourhood"].tolist()

    col1, col2 = st.columns(2)
    with col1:
        selected_rooms = st.multiselect("Room Type", room_types, default=room_types)
    with col2:
        selected_neigh = st.multiselect("Neighbourhood (top 15 by volume)", neighbourhoods, default=neighbourhoods[:5])

    if selected_rooms and selected_neigh:
        room_filter = "', '".join(selected_rooms)
        neigh_filter = "', '".join(selected_neigh)

        price_data = con.execute(f"""
            SELECT f.price, p.room_type, f.neighbourhood
            FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
            WHERE NOT f.price_likely_artifact
            AND p.room_type IN ('{room_filter}')
            AND f.neighbourhood IN ('{neigh_filter}')
        """).df()

        with st.container(border=True):
            fig_box = px.box(price_data, x="neighbourhood", y="price", color="room_type",
                              color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, COLOR_HIGHLIGHT, COLOR_MUTED])
            fig_box.update_layout(xaxis_title="", yaxis_title="Price (THB)")
            st.plotly_chart(styled_chart(fig_box, height=480), width="stretch")
            st.caption(f"Showing {len(price_data):,} listings matching current filters")

        col_x, col_y = st.columns(2)
        with col_x:
            with st.container(border=True):
                st.subheader("Price Summary Stats")
                summary = price_data.groupby("room_type")["price"].agg(["median", "mean", "count"]).round(2)
                st.dataframe(summary, width="stretch")
        with col_y:
            with st.container(border=True):
                st.subheader("Price Distribution")
                fig_hist = px.histogram(price_data, x="price", color="room_type", nbins=40,
                                         color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, COLOR_HIGHLIGHT, COLOR_MUTED])
                fig_hist.update_layout(xaxis_title="Price (THB)", yaxis_title="Count")
                st.plotly_chart(styled_chart(fig_hist, height=340), width="stretch")
    else:
        st.info("Select at least one room type and neighbourhood to see the chart.")

# ============================================================
# TAB 3: MAP
# ============================================================
with tab3:
    st.subheader("Listing Density & Price by Location")

    master = pd.read_parquet(processed_dir / f"listings_master_{city}.parquet")
    geo_df = master[master["price_likely_artifact"] == False][
        ["id", "latitude", "longitude", "price_clean", "review_scores_rating", "neighbourhood_cleansed"]
    ].dropna(subset=["latitude", "longitude"])

    sample_size = min(3000, len(geo_df))
    geo_sample = geo_df.sample(n=sample_size, random_state=42)

    with st.container(border=True):
        fig_map = px.scatter_mapbox(
            geo_sample, lat="latitude", lon="longitude", color="price_clean",
            size_max=8, zoom=10, height=550,
            color_continuous_scale=["#2A313C", COLOR_SECONDARY, COLOR_PRIMARY],
            hover_data={"neighbourhood_cleansed": True, "price_clean": ":.0f"},
            mapbox_style="carto-darkmatter"
        )
        fig_map.update_layout(
            paper_bgcolor=COLOR_CARD, font_color=COLOR_TEXT,
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(title="Price (THB)")
        )
        st.plotly_chart(fig_map, width="stretch")
        st.caption(f"Showing {sample_size:,} sampled listings (out of {len(geo_df):,} total) colored by price")

# ============================================================
# TAB 4: SEGMENTS
# ============================================================
with tab4:
    st.subheader("Host & Listing Segments (K-Means Clustering)")

    cluster_profiles = pd.read_csv("report/findings/section6_datascience/cluster_profiles.csv")

    cluster_names = {
        0: "Premium/Niche Listings",
        1: "Established, High-Track-Record",
        2: "Typical/Baseline Listings",
        3: "High-Demand Performers",
        4: "Professional Multi-Property Operators",
        5: "Underperforming/At-Risk"
    }
    cluster_profiles["cluster_name"] = cluster_profiles["cluster"].map(cluster_names)

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container(border=True):
            st.subheader("Cluster Sizes")
            fig_size = px.bar(cluster_profiles.sort_values("n_listings", ascending=True),
                               x="n_listings", y="cluster_name", orientation="h",
                               color_discrete_sequence=[COLOR_PRIMARY])
            fig_size.update_layout(xaxis_title="Number of Listings", yaxis_title="")
            st.plotly_chart(styled_chart(fig_size, height=400), width="stretch")

    with col2:
        with st.container(border=True):
            st.subheader("Quality Flag")
            at_risk = cluster_profiles[cluster_profiles["cluster"] == 5].iloc[0]
            st.metric("At-Risk Listings", f"{int(at_risk['n_listings']):,}",
                       help="Cluster 5: confirmed genuine low ratings, not an imputation artifact")
            st.metric("Avg Rating (At-Risk)", f"{at_risk['review_scores_rating']:.2f}★")

    st.write("")
    st.subheader("Full Cluster Profiles")
    display_cols = ["cluster_name", "n_listings", "calculated_host_listings_count",
                     "price", "occupancy_rate_pct", "review_scores_rating",
                     "number_of_reviews", "availability_365"]
    display_df = cluster_profiles[display_cols].rename(columns={
        "cluster_name": "Segment", "n_listings": "Listings",
        "calculated_host_listings_count": "Avg Host Portfolio",
        "price": "Avg Price (THB)", "occupancy_rate_pct": "Occupancy %",
        "review_scores_rating": "Avg Rating", "number_of_reviews": "Avg Reviews",
        "availability_365": "Avg Availability (days)"
    })
    with st.container(border=True):
        st.dataframe(display_df, width="stretch", hide_index=True)

# ============================================================
# TAB 5: PRICE PREDICTOR
# ============================================================
with tab5:
    st.subheader("Predict a Listing's Price")
    st.caption("Uses the trained XGBoost model (Section 6.1) — Test MAPE 41.9%")

    model = joblib.load(processed_dir / f"model_XGBoost_{city}.joblib")

    col1, col2, col3 = st.columns(3)
    with col1:
        accommodates = st.number_input("Accommodates", min_value=1, max_value=16, value=2)
        bedrooms = st.number_input("Bedrooms", min_value=0.0, max_value=10.0, value=1.0, step=1.0)
        bathrooms = st.number_input("Bathrooms", min_value=0.0, max_value=10.0, value=1.0, step=0.5)
    with col2:
        beds = st.number_input("Beds", min_value=0.0, max_value=16.0, value=1.0, step=1.0)
        room_type = st.selectbox("Room Type", ["Entire home/apt", "Private room", "Shared room", "Hotel room"])
        review_score = st.slider("Expected Review Score", 1.0, 5.0, 4.86, 0.01)
    with col3:
        occupancy = st.slider("Expected Occupancy %", 0, 100, 25)
        amenities_count = st.number_input("Amenities Count", min_value=0, max_value=100, value=20)
        availability = st.number_input("Availability (days/year)", min_value=0, max_value=365, value=300)

    if st.button("Predict Price", type="primary"):
        feature_row = pd.DataFrame([{
            "occupancy_rate_pct": occupancy, "review_scores_rating": review_score,
            "number_of_reviews": 10, "has_reviews": 1,
            "neighbourhood_median_price": 2222.22,
            "accommodates": accommodates, "bedrooms": bedrooms, "bathrooms": bathrooms, "beds": beds,
            "host_is_superhost": 0, "availability_365": availability,
            "calculated_host_listings_count": 1, "amenities_count": amenities_count,
            "room_Hotel room": 1 if room_type == "Hotel room" else 0,
            "room_Private room": 1 if room_type == "Private room" else 0,
            "room_Shared room": 1 if room_type == "Shared room" else 0,
            "prop_Entire home": 1 if room_type == "Entire home/apt" else 0,
            "prop_Entire rental unit": 0, "prop_Entire townhouse": 0, "prop_Other": 0,
            "prop_Private room in condo": 0, "prop_Private room in home": 0,
            "prop_Private room in rental unit": 0, "prop_Private room in townhouse": 0,
            "prop_Room in boutique hotel": 0, "prop_Room in hotel": 1 if room_type == "Hotel room" else 0,
            "accommodates_x_bedrooms": accommodates * bedrooms
        }])

        expected_cols = model.get_booster().feature_names
        feature_row = feature_row.reindex(columns=expected_cols, fill_value=0)

        log_pred = model.predict(feature_row)[0]
        price_pred = np.expm1(log_pred)

        st.success(f"### Predicted Price: ฿{price_pred:,.0f} per night")
        st.caption("Based on the trained XGBoost model. Actual prices vary ±42% (MAPE) due to factors not captured here (exact location, photos, host reputation).")