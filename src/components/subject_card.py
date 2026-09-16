import streamlit as st


def subject_card(
    name,
    code,
    section,
    stats=None,
    footer_callback=None
):

    # Subject Card
    with st.container(border=True):

        # Subject name
        st.subheader(name)

        # Subject details
        st.write(f"**Code:** {code}")
        st.write(f"**Section:** {section}")

        # Stats
        if stats:

            cols = st.columns(len(stats))

            for col, stat in zip(cols, stats):

                with col:

                    if isinstance(stat, (list, tuple)) and len(stat) >= 2:

                        st.metric(
                            label=stat[0],
                            value=stat[1]
                        )

        # Footer callback
        if footer_callback:

            st.divider()

            footer_callback()