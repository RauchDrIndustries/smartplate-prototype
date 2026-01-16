import streamlit as st
import datetime
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SmartPlate Beta", page_icon="🍽️", layout="wide")

# --- SIDEBAR: USER SETTINGS ---
st.sidebar.header("⚙️ User Profile")

# Household Settings
st.sidebar.subheader("🏠 Household")
family_size = st.sidebar.number_input("Family Size", min_value=1, max_value=10, value=4)
diet = st.sidebar.text_input("Dietary Restrictions", value="No Chicken")
dislikes = st.sidebar.text_input("Dislikes/Allergies", value="Dill, Cilantro")

# Schedule Settings
st.sidebar.subheader("📅 Schedule Defaults")
planning_duration = st.sidebar.slider("Days to Plan", 1, 7, 3)
arrival_time = st.sidebar.selectbox("Typical Arrival Time", ["4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM", "6:00 PM"], index=1)
dinner_time = st.sidebar.selectbox("Preferred Dinner Time", ["5:00 PM", "5:30 PM", "6:00 PM", "6:30 PM", "7:00 PM"], index=3)

# Cooking Strategy
st.sidebar.subheader("🍳 Strategy")
max_prep = st.sidebar.slider("Max Weeknight Prep (Mins)", 15, 60, 20, step=5)
prep_day = st.sidebar.selectbox("Meal Prep Day", ["None", "Sunday", "Monday", "Saturday"], index=1)
leftovers = st.sidebar.checkbox("Schedule Leftover Nights?", value=False)

# --- MAIN PAGE ---
st.title("🍽️ SmartPlate Prototype")
st.markdown("### The AI Meal Planner that respects your schedule.")

# --- API KEY SETUP ---
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ API Key not found. Please set it in Streamlit Secrets.")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_start_date():
    return datetime.date.today()

# --- MAIN APP LOGIC ---
if st.button("🚀 Generate Meal Plan"):
    
    with st.spinner("Analyzing your schedule..."):
        # 1. SIMULATE CALENDAR DATA (Placeholder for now)
        events_summary = """
        (Simulated Calendar Data for Testing)
        - Wednesday: Sax Lesson (4:30 PM - 5:00 PM)
        - Thursday: Basketball Game (Ends 6:30 PM)
        - Friday: No Events
        """
        
        # 2. PREPARE THE PROMPT
        start_date = get_start_date()
        date_list = ""
        for i in range(planning_duration):
             d = start_date + datetime.timedelta(days=i)
             date_list += f"- {d.strftime('%A, %B %d')}\n"

        if prep_day == "None": prep_instr = ""
        else: prep_instr = f"2. **Meal Prep Preference:** I usually have time to cook more on {prep_day}."

        prompt_plan = (
            f"You are a smart meal planning coach. I need a dinner plan for the dates listed below.\n\n"
            f"--- HOUSEHOLD PROFILE ---\n"
            f"1. **Family Size:** Cooking for {family_size} people.\n"
            f"2. **Dietary Restrictions:** {diet}.\n"
            f"3. **Dislikes/Allergies:** Please AVOID: {dislikes}.\n\n"
            f"--- USER PREFERENCES ---\n"
            f"1. **Typical Dinner Time:** {dinner_time}\n"
            f"{prep_instr}\n"
            f"3. **Schedule Leftover Nights?** {leftovers}.\n"
            f"4. **Max Prep Time (Weekdays):** {max_prep} minutes active cooking time.\n\n"
            f"--- THE SCHEDULE (SIMULATED FOR BETA) ---\n"
            f"{date_list}\n"
            f"{events_summary}\n\n"
            f"--- LOGIC RULES ---\n"
            f"1. **Analyze Gaps:** Look at Arrival Time ({arrival_time}) vs Event Start.\n"
            f"2. **Traffic Light Logic:** Green (>90m), Yellow (45-90m), Red (<45m).\n"
            f"3. **The Late Start:** If event ends 5:15-6:00 PM, give 2 options.\n"
            f"4. **Output Format:** Provide a Markdown table with exactly these columns:\n"
            f"   | Date | 📅 Schedule (The Constraint) | 🍽️ The Meal Plan | 📝 Prep Notes |\n"
            f"   - **Schedule Column:** List the event times briefly (e.g. 'Sax Lesson 4:30-5:00').\n"
            f"   - **Meal Column:** The Name of the dish.\n"
            f"   - **Prep Notes:** Active cooking time + The 'Why' (e.g. '20 mins - Quick cook due to late arrival')."
        )

        # 3. CALL GEMINI (USING GEMINI FLASH LATEST)
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('models/gemini-flash-latest')
            
            response = model.generate_content(prompt_plan)
            
            st.success("Plan Generated!")
            st.markdown("### 📅 Your Smart Schedule")
            # This renders the table beautifully in Streamlit
            st.markdown(response.text)
            
            # 4. SHOPPING LIST
            with st.spinner("Writing Shopping List..."):
                prompt_shopping = (
                    f"Extract ingredients for a family of {family_size} based on this plan:\n"
                    f"{response.text}\n"
                    f"Group by: 🛒 DEFINITELY NEED, 🔍 CHECK STOCK, 🧂 PANTRY."
                )
                res_shop = model.generate_content(prompt_shopping)
                
                st.markdown("---")
                st.markdown("### 🛒 Consolidated Shopping List")
                st.markdown(res_shop.text)

        except Exception as e:
            st.error(f"An error occurred: {e}")
