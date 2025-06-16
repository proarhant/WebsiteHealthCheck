import streamlit as st
import re
from website_checker import check_website_errors  # logic is in website_checker.py

# === Helper ===
def is_valid_url(url):
    pattern = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$')
    return bool(pattern.match(url))

# === Page Config ===
st.set_page_config(
    page_title="🌐 Website Error Checker",
    layout="centered",
    initial_sidebar_state="auto"
)

# Optional: dark mode-friendly title and description
st.markdown("""
    <style>
        h1 {
            text-align: center;
            color: #FAFAFA;
        }
        .centered {
            text-align: center;
            color: #CCCCCC;
        }
        .block-label {
            font-weight: 600;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌐 Website Error Checker</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered'>Scan websites for JavaScript, network, and console <code>errors</code>.</p>", unsafe_allow_html=True)
st.markdown("---")

# === Refresh + Input ===
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("🔄 New Test"):
        st.session_state.clear()
        st.rerun()

with col2:
    with st.form("website_check_form"):
        url_input = st.text_input("🔗 Enter Website URL", placeholder="https://example.com")
        submitted = st.form_submit_button("🚀 Submit")

# === Scan Results ===
if submitted:
    if not is_valid_url(url_input):
        st.warning("⚠️ Please enter a valid URL.")
    else:
        if not url_input.startswith(('http://', 'https://')):
            url_input = 'https://' + url_input

        with st.spinner("🕵️‍♂️ Scanning website..."):
            result = check_website_errors(url_input)

        st.markdown("---")
        st.markdown(f"<h3 style='color:#00D1FF;'>🔍 Scan Results for <code>{url_input}</code></h3>", unsafe_allow_html=True)

        if result.get("error"):
            st.error(f"❌ Failed to load the website:\n\n`{result['error']}`")
        else:
            # === HTTP Status ===
            status_code = result.get("status_code")
            if status_code is None:
                st.warning("⚠️ Unable to retrieve HTTP status code.")
            elif status_code >= 400:
                st.error(f"❌ Page returned error status: **{status_code}**")
            else:
                st.success(f"✅ Page loaded successfully! **(HTTP {status_code})**")

            st.markdown(f"**📝 Page Title:** `{result.get('title', '(unknown)')}`")
            st.markdown(f"**🔗 Final URL:** `{result['url']}`")
            st.markdown("---")

            # === JavaScript Errors ===
            with st.expander("🧠 JavaScript Errors", expanded=True):
                if result['js_errors']:
                    st.warning(f"❌ {len(result['js_errors'])} error(s) found:")
                    for err in result['js_errors']:
                        st.code(err, language="js")
                else:
                    st.success("✅ No JavaScript errors detected.")

            # === Network Errors ===
            with st.expander("🌐 Network Errors", expanded=True):
                if result['network_errors']:
                    st.warning(f"❌ {len(result['network_errors'])} network issue(s) detected:")
                    for err in result['network_errors']:
                        st.error(f"**URL**: `{err['url']}`\n\n**Failure**: `{err['failure']}`")
                else:
                    st.success("✅ No network errors detected.")

            # === Console Errors ===
            with st.expander("🧾 Console Errors", expanded=True):
                if result['console_errors']:
                    st.warning(f"❌ {len(result['console_errors'])} console error(s) found:")
                    for err in result['console_errors']:
                        loc = err.get('location', {})
                        st.error(f"{err['text']}\n\n📍 `{loc.get('url', '')}:{loc.get('lineNumber', 0)}`")
                else:
                    st.success("✅ No console errors detected.")

        st.markdown("---")