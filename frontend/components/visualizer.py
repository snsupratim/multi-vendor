import streamlit as st
import pandas as pd
import plotly.express as px
from typing import List, Dict, Any, Callable, Optional


def render_analytics_components(components: List[Dict[str, Any]]):
    """
    Dynamically renders components returned by the /analytics-chat Text-to-SQL Agent.
    Supports BAR_CHART, LINE_CHART, PIE_CHART, GRAPH, TABLE, METRIC, and TEXT.
    """
    if not components:
        st.info("No visualization components returned.")
        return

    for idx, comp in enumerate(components):
        comp_type = str(comp.get("componentType", "TEXT")).upper()
        title = comp.get("title", "")
        desc = comp.get("description", "")
        data = comp.get("data", [])
        config = comp.get("config", {})

        with st.container(border=True):
            if title:
                st.markdown(f"### {title}")
            if desc:
                st.caption(desc)

            # TEXT Component
            if comp_type == "TEXT":
                if desc and not title:
                    st.markdown(desc)
                elif not desc and data:
                    st.write(data)

            # METRIC Component
            elif comp_type == "METRIC":
                metric_value = config.get("value") or (data[0] if isinstance(data, list) and data else "N/A")
                label = config.get("label", title or "Metric")
                delta = config.get("delta", None)
                st.metric(label=label, value=metric_value, delta=delta)

            # TABLE Component
            elif comp_type == "TABLE":
                if data and isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Table is empty.")

            # CHART / GRAPH Component
            elif comp_type in ["GRAPH", "BAR_CHART", "LINE_CHART", "PIE_CHART"]:
                if not data or not isinstance(data, list):
                    st.info("No data available to plot chart.")
                    continue

                df = pd.DataFrame(data)
                chart_type = config.get("type", "bar").lower()
                if comp_type == "BAR_CHART":
                    chart_type = "bar"
                elif comp_type == "LINE_CHART":
                    chart_type = "line"
                elif comp_type == "PIE_CHART":
                    chart_type = "pie"

                # Find x and y axis
                x_axis = config.get("xAxis") or config.get("x")
                y_axis = config.get("yAxis") or config.get("y")

                # Auto-detect column names if not specified in config
                if not x_axis and len(df.columns) > 0:
                    x_axis = df.columns[0]
                if not y_axis and len(df.columns) > 1:
                    y_axis = df.columns[1]

                try:
                    if chart_type == "bar":
                        fig = px.bar(
                            df, 
                            x=x_axis, 
                            y=y_axis, 
                            title=title or None,
                            color_discrete_sequence=px.colors.qualitative.Prism,
                            template="plotly_dark"
                        )
                        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "line":
                        fig = px.line(
                            df, 
                            x=x_axis, 
                            y=y_axis, 
                            title=title or None,
                            markers=True,
                            template="plotly_dark"
                        )
                        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_type == "pie":
                        fig = px.pie(
                            df, 
                            names=x_axis, 
                            values=y_axis, 
                            title=title or None,
                            hole=0.3,
                            template="plotly_dark"
                        )
                        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.bar_chart(df.set_index(x_axis) if x_axis in df.columns else df)

                except Exception as chart_err:
                    st.warning(f"Could not render custom chart: {chart_err}")
                    st.dataframe(df, use_container_width=True)

            # Fallback
            else:
                if data:
                    st.json(data)
                elif desc:
                    st.markdown(desc)


def render_suggestions(suggestions: List[str], on_click_callback: Optional[Callable[[str], None]] = None):
    """
    Renders clickable suggestion pills / prompt chips for quick follow-ups.
    """
    if not suggestions:
        return

    st.markdown("💡 **Suggested Follow-ups:**")
    cols = st.columns(min(len(suggestions), 3))
    for idx, suggestion in enumerate(suggestions):
        col = cols[idx % len(cols)]
        if col.button(f"🔍 {suggestion}", key=f"sug_btn_{idx}_{hash(suggestion)}", use_container_width=True):
            if on_click_callback:
                on_click_callback(suggestion)
