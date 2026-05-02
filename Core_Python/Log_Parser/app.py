import streamlit as st
import re
from collections import Counter
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ---------- Optional AI ----------
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    AI = True
except:
    AI = False

# ---------- Config ----------
LOG_FILE = "log.txt"

LOG_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}) "
    r"(\d{2}:\d{2}:\d{2}) "
    r"(\w+) "
    r"(.+)"
)

st.set_page_config(page_title="Log Monitor Pro", layout="wide")

st.title("🚨 Log Monitor PRO (Real-time + AI)")

refresh_rate = st.slider("Refresh rate (seconds)", 1, 5, 2)

# ---------- Session State ----------
if "level_counter" not in st.session_state:
    st.session_state.level_counter = Counter()

if "error_messages" not in st.session_state:
    st.session_state.error_messages = Counter()

if "timeline" not in st.session_state:
    st.session_state.timeline = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Parser ----------
def parse_line(line):
    match = LOG_PATTERN.match(line)
    if match:
        date, time_, level, msg = match.groups()
        timestamp = datetime.strptime(f"{date} {time_}", "%Y-%m-%d %H:%M:%S")
        return {
            "timestamp": timestamp,
            "level": level,
            "message": msg
        }
    return None

# ---------- Read Logs ----------
def read_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return f.readlines()[-50:]
    except:
        return []

# ---------- Process ----------
lines = read_logs()

st.session_state.level_counter.clear()
st.session_state.error_messages.clear()

parsed_logs = []

for line in lines:
    parsed = parse_line(line.strip())
    if parsed:
        parsed_logs.append(parsed)

        st.session_state.level_counter[parsed["level"]] += 1

        if parsed["level"] == "ERROR":
            st.session_state.error_messages[parsed["message"]] += 1

        # timeline data
        st.session_state.timeline.append(
            (parsed["timestamp"], parsed["level"])
        )

# ---------- Layout ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Log Levels")
    st.json(dict(st.session_state.level_counter))

with col2:
    st.subheader("🚨 Top Errors")
    st.write(st.session_state.error_messages.most_common(5))

# ---------- 📈 GRAPH 1: Error Trend ----------
st.subheader("📈 Error Trend Over Time")

error_times = [
    t for t, lvl in st.session_state.timeline if lvl == "ERROR"
]

if error_times:
    times = [t.strftime("%H:%M:%S") for t in error_times]
    counts = list(range(1, len(times) + 1))

    fig, ax = plt.subplots()
    ax.plot(times, counts)
    ax.set_title("Error Growth Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Error Count")

    st.pyplot(fig)
else:
    st.info("No errors yet")

# ---------- 📊 GRAPH 2: Level Distribution ----------
st.subheader("📊 Log Distribution")

levels = list(st.session_state.level_counter.keys())
counts = list(st.session_state.level_counter.values())

if levels:
    fig2, ax2 = plt.subplots()
    ax2.bar(levels, counts)
    ax2.set_title("Log Levels Distribution")

    st.pyplot(fig2)

# ---------- 🚨 Anomaly ----------
if st.session_state.level_counter.get("ERROR", 0) > 5:
    st.error("🚨 ALERT: Too many ERROR logs!")

# ---------- 📜 Logs ----------
st.subheader("📜 Recent Logs")

for log in parsed_logs[-10:]:
    st.text(f"{log['timestamp']} | {log['level']} | {log['message']}")

# ---------- 🤖 AI Chat ----------
st.subheader("💬 Chat with Logs")

user_query = st.text_input("Ask something about logs:")

if user_query:
    if AI:
        try:
            log_text = "\n".join(lines)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a log analysis expert."},
                    {
                        "role": "user",
                        "content": f"""
Logs:
{log_text}

Question:
{user_query}
"""
                    }
                ]
            )

            answer = response.choices[0].message.content

            st.session_state.chat_history.append(("You", user_query))
            st.session_state.chat_history.append(("AI", answer))

        except Exception as e:
            st.error(str(e))
    else:
        st.warning("Add OPENAI_API_KEY for chat feature")

# ---------- Chat History ----------
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.write(f"🧑 {msg}")
    else:
        st.write(f"🤖 {msg}")

# ---------- Auto Refresh ----------
time.sleep(refresh_rate)
st.rerun()