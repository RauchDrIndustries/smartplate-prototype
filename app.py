import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="SmartPlate Diagnostic", page_icon="🛠️")
st.title("🛠️ Model Diagnostic Tool")

# 1. Get the Key
api_key = st.secrets.get("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ API Key is missing from Secrets.")
    st.stop()
else:
    # Check if it looks like a valid AI Studio key
    if api_key.startswith("AIza"):
        st.success(f"✅ API Key found (Starts with {api_key[:4]}...)")
    else:
        st.warning("⚠️ API Key format looks unusual. It should start with 'AIza'.")

# 2. Configure
genai.configure(api_key=api_key)

# 3. List Models
st.write("---")
st.write("### 📋 Checking Available Models...")
st.info("Querying Google's servers to see what is on the menu...")

try:
    # Get the list
    models = list(genai.list_models())
    
    found_any = False
    for m in models:
        # We only care about models that can generate text
        if 'generateContent' in m.supported_generation_methods:
            st.success(f"🟢 **AVAILABLE:** `{m.name}`")
            found_any = True
            
    if not found_any:
        st.error("❌ No text generation models found. This usually means your API Key is valid, but the Project doesn't have access to Gemini API.")
        
except Exception as e:
    st.error(f"❌ Error connecting to Google: {e}")
