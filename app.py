import streamlit as st
import pandas as pd
from storage import init_db, fetch_receipts, fetch_receipt_items
from upload_module import upload_receipt_ui
import google.generativeai as genai
st.set_page_config(page_title="Receipt and Invoice Digitizer", layout="wide")

init_db()

# ---------------- Small API key validation function
def validate_gemini_key(api_key: str) -> bool:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        model.generate_content("Hello")  # test call
        return True
    except Exception:
        return False

# ---------------- API KEY GATE (PERSISTENT UI) ----------------
st.sidebar.markdown("## 🔐 Gemini API Configuration")

# Init session state
if "GEMINI_API_KEY" not in st.session_state:
    st.session_state["GEMINI_API_KEY"] = ""

if "API_VERIFIED" not in st.session_state:
    st.session_state["API_VERIFIED"] = False

# Always show input box
api_key = st.sidebar.text_input(
    "Enter Gemini API Key",
    type="password",
    value=st.session_state["GEMINI_API_KEY"],
    placeholder="Enter your Gemini API key here",
)

# Update key if changed
if api_key != st.session_state["GEMINI_API_KEY"]:
    st.session_state["GEMINI_API_KEY"] = api_key
    st.session_state["API_VERIFIED"] = False

# Verify button (explicit action = better UX)
verify_btn = st.sidebar.button("✅ Verify API Key")

if verify_btn:
    if not api_key:
        st.sidebar.warning("⚠️ Please enter an API key.")
    else:
        with st.spinner("🔍 Verifying API key..."):
           if validate_gemini_key(api_key):
              st.session_state["API_VERIFIED"] = True
              st.sidebar.success("✅ API key verified")
           else:
                st.session_state["API_VERIFIED"] = False
                st.sidebar.error("❌ Invalid API key")


# Block app access if not verified
if not st.session_state["API_VERIFIED"]:
    st.warning("🔒 Please verify a valid Gemini API key to access the app.")
    st.stop()

# ---------------- MAIN APP ----------------
st.title("🧾 Receipt and Invoice Digitizer")

tab1, tab2, tab3 = st.tabs([
    "📤 Upload Receipt",
    "📊 Dashboard & Analysis",
    "🕒 History"
])

# ---------------- TAB 1 ----------------
with tab1:
    upload_receipt_ui()

    st.markdown("### 📁 Persistent Storage")

rows = fetch_receipts()
if not rows:
    st.info("No receipts stored yet.")
else:
    df = pd.DataFrame(
        rows,
        columns=["ID", "Merchant", "Date", "Total", "Tax"]
    )

    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )

    # Check if a row is selected
    if event.selection.rows:
        selected_row_index = event.selection.rows[0]
        selected_id = int(df.iloc[selected_row_index]["ID"])

        st.markdown("### 🧾 Detailed Bill Items")

        items = fetch_receipt_items(selected_id)

        if items:
            items_df = pd.DataFrame(
                items,
                columns=["Item Name", "Quantity", "Price"]
            )
            st.dataframe(items_df, use_container_width=True)
        else:
            st.info("No bill items found for this receipt.")


# ---------------- TAB 2 ----------------
with tab2:
    st.info("Analytics & Gemini insights can be added here next.")

# ---------------- TAB 3 ----------------
with tab3:
    st.info("History view can reuse stored data (already persistent).")
