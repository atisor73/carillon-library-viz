import streamlit as st
import pandas as pd
import altair as alt

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
            gap: 1rem;
        }

        /* Reduce title margins */
        h1 {
            margin-top: 0rem !important;
            padding-top: 0rem !important;
            margin-bottom: 1.5rem !important;
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

st.title("Carillon Library Viz: region_sub x Style")


# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_csv("Processed_Carillon_Library.csv")

# Clean categorical columns
for col in ["style_full", "region_sub"]:
    df[col] = df[col].fillna("Unknown").astype(str).str.strip()

# Remove rows without useful category labels
df = df[
    (df["style_full"] != "") &
    (df["region_sub"] != "")
].copy()

# -----------------------------------------
# CREATE HEATMAP DATA
# -----------------------------------------

heatmap_data = (
    df.groupby(["style_full", "region_sub"])
      .size()
      .reset_index(name="count")
)

# -----------------------------------------
# INTERACTIVE SELECTION
# -----------------------------------------

selection = alt.selection_point(
    name="cell_select",
    fields=["style_full", "region_sub"],
    on="click",
    clear="dblclick"
)

# -----------------------------------------
# HEATMAP
# -----------------------------------------
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
        y=alt.X(
            "style_full:N",
            title="Musical Style (Subcategory)",
            sort=alt.SortField(
                field="style_full",
                order="ascending"
            ),
            axis=alt.Axis(
                labelFontSize=11,
                labelLimit=200,
                labelOverlap=False,
                ticks=True,
                domain=True
            )
        ),

        x=alt.X(
            "region_sub:N",
            title="Geographic region_sub",
            sort=alt.SortField(
                field="region_sub",
                order="ascending"
            ),
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
            scale=alt.Scale(
                range=["#F5E6E8", "#800000", "#4A001F"]
            ),
            legend=alt.Legend(
                orient="bottom",
                direction="horizontal",
                titleOrient="top"
            )
        ),

        tooltip=[
            alt.Tooltip("style_full:N", title="Style Subcategory"),
            alt.Tooltip("region_sub:N", title="region_sub"),
            alt.Tooltip("count:Q", title="Pieces")
        ]
    )
    .add_params(selection)
    .properties(
        width=1700,
        height=1900
    )
)

chart = heatmap.interactive()
# heatmap = (
#     alt.Chart(heatmap_data)
#     .mark_rect(
#         stroke="white",
#         strokeWidth=1
#     )
#     .encode(
#         y=alt.Y(
#             "style_full:N",
#             title="Style",
#             sort=alt.SortField(
#                 field="style",
#                 order="ascending"
#             ),
#             axis=alt.Axis(
#                 # labelAngle=-45,
#                 labelFontSize=11,
#                 labelLimit=200,
#                 labelOverlap=False,
#                 ticks=True,
#                 domain=True
#                     )
#         ),

#         x=alt.X(
#             "region_sub:N",
#             title="Musical Style",
#             sort="-y",
#             axis=alt.Axis(
#                 orient="top",
#                 labelAngle=-45,
#                 labelFontSize=11,
#                 labelLimit=200,
#                 labelOverlap=False,
#                 ticks=True,
#                 domain=True
#                     )
#         ), 

#         color=alt.Color(
#             "count:Q",
#             title="# pieces",
#             # scale=alt.Scale(scheme="blues"),
#             scale=alt.Scale(range=["#F5E6E8", "#800000", "#4A001F"]),
#             legend=alt.Legend(
#                 orient="bottom",
#                 direction='horizontal',
#                 titleOrient='top'
#             )
#         ),

#         tooltip=[
#             alt.Tooltip("style_full:N", title="Style"),
#             alt.Tooltip("region_sub:N", title="region_sub"),
#             alt.Tooltip("count:Q", title="Pieces")
#         ]
#     )
#     .add_params(selection)
#     .properties(
#         width=350,
#         height=1400
#     )
# )

# chart = (heatmap).interactive()


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

# -----------------------------------------
# COMPOSITIONS TABLE
# -----------------------------------------

with col2:

    # st.subheader("Compositions")

    if selected:

        selected_style = selected[0]["style_full"]
        selected_region_sub = selected[0]["region_sub"]

        pieces = df[
            (df["style_full"] == selected_style) &
            (df["region_sub"] == selected_region_sub)
        ].copy()

        st.markdown(
            f"""
            <div style="line-height:1.3; margin-bottom:8px;">
                <b>Style:</b> {selected_style}<br>
                <b>region_sub:</b> {selected_region_sub}<br>
                <b>Compositions:</b> {len(pieces)}
            </div>
            """,
            unsafe_allow_html=True
        
        )
        columns_to_show = [
            "title",
            "composer",
            "arranger",
            "pages",
            "duet"
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

