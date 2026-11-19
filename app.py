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


st.title("Carillon Library Viz: Search by Region & Genre")


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
    options=["Region", "Subregion", "Subgenre"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

geo_column = {
    "Region": "region",
    "Subregion": "region_sub",
    "Subgenre": "region"
}[geo_level]

genre_column = {
    "Region":"style", 
    "Subregion": "style",
    "Subgenre": "style_intermediate"
    ""
}[geo_level]

# Reset selection when geographic granularity changes

if "previous_geo_level" not in st.session_state:
    st.session_state.previous_geo_level = geo_level
if st.session_state.previous_geo_level != geo_level:
    st.session_state.previous_geo_level = geo_level
    st.session_state.pop("heatmap", None)

if geo_level == "Region":
    heatmap_height = 500
    heatmap_width = 350
elif geo_level == 'Subregion':
    heatmap_height = 1400
    heatmap_width = 350
else:
    heatmap_height = 500
    heatmap_width = 700


# -----------------------------------------
# CREATE HEATMAP DATA
# -----------------------------------------

heatmap_data = (
    df.groupby([genre_column, geo_column])
    # df.groupby(["style", "region_sub"])
      .size()
      .reset_index(name="count")
)

# -----------------------------------------
# INTERACTIVE SELECTION
# -----------------------------------------

selection = alt.selection_point(
    name="cell_select",
    fields=[genre_column, geo_column],
    # fields=["style", "region_sub"],
    on="click",
    clear="dblclick"
)

# -----------------------------------------
# HEATMAP
# -----------------------------------------

sort_x = ["Unknown", "Hymn", "Traditional", "Classical", "Popular"]
if geo_column == 'Subgenre':
    sort_x = [
        'Hymn',
        'Traditional',
        'Classical - Early Music',
        'Classical - Baroque',
        'Classical - Classical',
        'Classical - Romantic',
        'Classical - Impressionist',
        'Classical - Modern Classical',
        'Classical - Contemporary Classical',
        'Classical - Unknown',
        'Popular - Jazz',
        'Popular - Musical',
        'Popular - Film',
        'Popular - Pop',
        'Unknown - Unknown',
    ]
    
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
            title="Composer Origin",
            sort=alt.SortField(
                # field="region_sub",
                field=f"{geo_column}",
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
            f"{genre_column}:N",
            title="Musical Genre",
            # sort="-x",
            sort=sort_x,
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
            scale=alt.Scale(
                # domain=[0, 1500],
                # clamp=True,
                range=["#F5E6E8", "#800000", "#4A001F"]),
                # range=["#F2DAE0", "#800000", "#4A001F"]),
            legend=alt.Legend(
                orient="bottom",
                direction='horizontal',
                titleOrient='top'
            )
        ),

        tooltip=[
            # alt.Tooltip("style:N", title="Style"),
            # alt.Tooltip("region_sub:N", title="Region"),
            alt.Tooltip(f"{genre_column}:N", title=geo_level),
            alt.Tooltip(f"{geo_column}:N", title=geo_level),
            alt.Tooltip("count:Q", title="Pieces")
        ]
    )
    .add_params(selection)
    .properties(
        width=heatmap_width,
        height=heatmap_height
    )
)

chart = (heatmap).interactive()





# -----------------------------------------
# CONDITIONAL LAYOUT
# -----------------------------------------
if geo_level == "Subgenre":
    # Heatmap on top
    event = st.altair_chart(
        chart,
        use_container_width=False,
        on_select="rerun",
        key="heatmap"
    )
else:
    # Heatmap and table side by side
    col1, col2 = st.columns([3, 5], gap="small")
    with col1:
        event = st.altair_chart(
            chart,
            use_container_width=False,
            on_select="rerun",
            key="heatmap"
        )

# # -----------------------------------------
# # SIDE-BY-SIDE LAYOUT
# # -----------------------------------------

# col1, col2 = st.columns([3, 5], gap='small')

# with col1:

#     event = st.altair_chart(
#         chart,
#         use_container_width=False,
#         on_select="rerun",
#         key="heatmap"
#     )

# -----------------------------------------
# GET SELECTED CELL
# -----------------------------------------

selected = event.selection.get("cell_select", [])
# Validate selection against current geographic granularity
if selected and geo_column not in selected[0]:
    selected = []
    
# for the region/subregion
if selected:
    selected_style = selected[0][genre_column]
    selected_geo = selected[0][geo_column]
    pieces = df[
        (df[genre_column] == selected_style) &
        (df[geo_column] == selected_geo)
    ].copy()
    
# -----------------------------------------
# COMPOSITIONS TABLE
# -----------------------------------------
if geo_level == "Subgenre":
    # Table underneath heatmap
    table_container = st.container()
else:
    # Table beside heatmap
    table_container = col2
with table_container:
    if selected:
        st.markdown(
            f"""
            <div style="line-height:1.3; margin-bottom:8px;">
                <b>Style:</b> {selected_style}<br>
                <b>{geo_level}:</b> {selected_geo}<br>
                <b>Compositions:</b> {len(pieces)}
                <div style='height: 15px;'></div>
            </div>
            """,
            unsafe_allow_html=True
        )
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
            # use_container_width=True,
            hide_index=True,
            height=700
        )
    else:
        # st.info("Click on a heatmap cell for composition table.")
        st.markdown(
            """
            <div style="
                color: #2F4EAE;
                background-color: #EFF5FE;
                padding: 12px 16px;
                border-radius: 5px;
                font-size: 14px;
            ">
                Click a heatmap block to see its compositions.
            </div>
            """,
            unsafe_allow_html=True
        )
