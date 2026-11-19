import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path


# -----------------------------------------
# PAGE SETUP
# -----------------------------------------

st.set_page_config(
    page_title="Carillon Library Viz",
    layout="wide"
)

st.markdown("""
    <style>
        /* Remove top whitespace */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0rem !important;
            padding-left: 4rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }

        /* Reduce spacing between elements */
        div[data-testid="stVerticalBlock"] {
            gap: 0.3rem;
        }

        /* Reduce title margins */
        h1 {
            margin-top: 0rem !important;
            padding-top: 0rem !important;
            margin-bottom: 1rem !important;
            font-size: 30px !important;
        }

        /* Remove header whitespace */
        header[data-testid="stHeader"] {
            height: 0.1rem;
            background: transparent;
        }

        /* Reduce dataframe spacing */
        div[data-testid="stDataFrame"] {
            margin-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Compact selection information */
    div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0.15rem !important;
        margin-top: 0.15rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="stAlert"] {
    background-color: #f0e7e6;
    color: #456590;
    border: 0px solid #1565C0;
}
</style>
""", unsafe_allow_html=True)

# Display github icon
st.markdown("""
<link rel="stylesheet"
 href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
""", unsafe_allow_html=True)
st.markdown("""
<a href="YOUR_GITHUB_REPOSITORY_URL" target="_blank"
   style="position: fixed; top: 20px; right: 130px;
          font-size: 24px; color: #444; text-decoration: none;">
    <i class="fab fa-github"></i>
</a>
""", unsafe_allow_html=True)



st.title("Carillon Library Viz: Region x Style")


# -----------------------------------------
# LOAD DATA
# -----------------------------------------
BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "Processed_Carillon_Library.csv"
df = pd.read_csv(csv_path)
# df = pd.read_csv("Processed_Carillon_Library.csv")

# Clean categorical columns
for col in ["style", "region_sub", "region"]:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()

# Remove rows without useful category labels
df = df[
    (df["style"] != "") &
    (df["region_sub"] != "")
].copy()


# -----------------------------------------
# GEOGRAPHIC GRANULARITY SELECTOR
# -----------------------------------------
geo_level = st.radio(
    "Geographic granularity:",
    options=["Region", "Sub-region"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

geo_column = {
    "Sub-region": "region_sub",
    "Region": "region",
}[geo_level]

if geo_column == "region_sub":
    heatmap_height = 1400
else:
    heatmap_height = 500

# -----------------------------------------
# CREATE HEATMAP DATA
# -----------------------------------------

heatmap_data = (
    df.groupby(["style", geo_column])
    # df.groupby(["style", "region_sub"])
      .size()
      .reset_index(name="count")
)

# -----------------------------------------
# INTERACTIVE SELECTION
# -----------------------------------------

selection = alt.selection_point(
    name="cell_select",
    fields=["style", geo_column],
    # fields=["style", "region_sub"],
    on="click",
    clear="dblclick"
)

# -----------------------------------------
# HEATMAP
# -----------------------------------------

heatmap = (
    alt.Chart(heatmap_data)
    .mark_rect(
        stroke="white",
        strokeWidth=1
    )
    .encode(
        y=alt.Y(
            # "region_sub:N",
            f"{geo_column}:N",
            title="Geographic Origin",
            sort=alt.SortField(
                field="region_sub",
                order="ascending"
            ),
            axis=alt.Axis(
                # labelAngle=-45,
                labelFontSize=11,
                labelLimit=200,
                labelOverlap=False,
                ticks=True,
                domain=True
                    )
        ),

        x=alt.X(
            "style:N",
            title="Musical Style",
            sort="-x",
            axis=alt.Axis(
                orient="top",
                labelAngle=-45,
                labelFontSize=11,
                labelLimit=200,
                labelOverlap=False,
                ticks=True,
                domain=True
                    )
        ), 

        color=alt.Color(
            "count:Q",
            title="# pieces",
            # scale=alt.Scale(scheme="blues"),
            scale=alt.Scale(range=["#F5E6E8", "#800000", "#4A001F"]),
            legend=alt.Legend(
                orient="bottom",
                direction='horizontal',
                titleOrient='top'
            )
        ),

        tooltip=[
            alt.Tooltip("style:N", title="Style"),
            # alt.Tooltip("region_sub:N", title="Region"),
            alt.Tooltip(f"{geo_column}:N", title=geo_level),
            alt.Tooltip("count:Q", title="Pieces")
        ]
    )
    .add_params(selection)
    .properties(
        width=350,
        height=heatmap_height
    )
)

chart = (heatmap).interactive()


# # -----------------------------------------
# # SIDE-BY-SIDE LAYOUT
# # -----------------------------------------

col1, col2 = st.columns([3, 5], gap='small')

with col1:

    event = st.altair_chart(
        chart,
        use_container_width=False,
        on_select="rerun",
        key="heatmap"
    )

# -----------------------------------------
# GET SELECTED CELL
# -----------------------------------------

selected = event.selection.get("cell_select", [])

# for the region/subregion
if selected:
    selected_style = selected[0]["style"]
    selected_geo = selected[0][geo_column]
    pieces = df[
        (df["style_sub"] == selected_style) &
        (df[geo_column] == selected_geo)
    ].copy()
# -----------------------------------------
# COMPOSITIONS TABLE
# -----------------------------------------

with col2:

    # st.subheader("Compositions")
    if selected:
        selected_style = selected[0]["style"]
        # selected_region = selected[0]["region_sub"]
        selected_region = selected[0][geo_column]
        
        pieces = df[
            (df["style"] == selected_style) &
            (df[geo_column] == selected_region)
        ].copy()


        st.markdown(
            f"""
            <div style="line-height:1.3; margin-bottom:8px;">
                <b>Style:</b> {selected_style}<br>
                <b>{geo_level}:</b> {selected_geo}<br>
                <b>Compositions:</b> {len(pieces)}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        columns_to_show = [
            "title",
            "composer",
            "arranger",
            "style_sub",
            "pages",
            "duet",
        ]

        st.dataframe(
            pieces[columns_to_show].reset_index(drop=True),
            use_container_width=False,
            hide_index=True,
            height=700,
            width=550
        )

    else:

        st.info("Click a heatmap cell to see its compositions.")

