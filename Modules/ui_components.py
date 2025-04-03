import streamlit as st

def styled_metric(label, value, delta=None, help_text=None, color="default"):
    """
    Displays a stylized metric box with optional delta and help tooltip.
    """
    with st.container():
        st.metric(label=label, value=value, delta=delta)
        if help_text:
            st.caption(f"ℹ️ {help_text}")

def section_header(title, icon="📊"):
    """
    Displays a clean section header with an icon.
    """
    st.markdown(f"### {icon} {title}")
    st.markdown("---")


def centered_message(message, icon="💡"):
    """
    Centered info message for empty states or notes.
    """
    st.markdown(
        f"<div style='text-align: center; padding: 1rem; font-size: 18px;'>"
        f"{icon} {message}</div>",
        unsafe_allow_html=True
    )

def show_data_expander(title, df):
    """
    Display a dataframe inside an expandable section.
    """
    with st.expander(f"📂 {title}"):
        st.dataframe(df, use_container_width=True)
