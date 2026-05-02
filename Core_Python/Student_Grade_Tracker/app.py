import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------- Optional AI ----------
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    AI = True
except:
    AI = False

st.set_page_config(page_title="Student Dashboard", layout="wide")

st.title("🎓 Student Grade Tracker PRO")

# ---------- Upload ----------
file = st.file_uploader("Upload Student CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    st.subheader("📄 Data Preview")
    st.dataframe(df)

    # ---------- Compute ----------
    subjects = list(df.columns)
    subjects.remove("name")

    df["average"] = df[subjects].mean(axis=1)

    def get_grade(avg):
        return "A" if avg >= 90 else "B" if avg >= 75 else "C"

    df["grade"] = df["average"].apply(get_grade)

    # ---------- Rankings ----------
    st.subheader("🏆 Rankings")
    ranked = df.sort_values(by="average", ascending=False)
    st.dataframe(ranked)

    # ---------- Subject Toppers ----------
    st.subheader("🎯 Subject Toppers")

    toppers = {}
    for sub in subjects:
        top_row = df.loc[df[sub].idxmax()]
        toppers[sub] = (top_row["name"], top_row[sub])

    for sub, (name, marks) in toppers.items():
        st.write(f"{sub}: {name} ({marks})")

    # ---------- 📊 Grade Distribution ----------
    st.subheader("📊 Grade Distribution")

    grade_counts = df["grade"].value_counts()

    fig1, ax1 = plt.subplots()
    ax1.bar(grade_counts.index, grade_counts.values)
    ax1.set_title("Grade Distribution")

    st.pyplot(fig1)

    # ---------- 📈 Average per Subject ----------
    st.subheader("📈 Subject Averages")

    subject_avg = df[subjects].mean()

    fig2, ax2 = plt.subplots()
    ax2.bar(subject_avg.index, subject_avg.values)
    ax2.set_title("Average Marks per Subject")

    st.pyplot(fig2)

    # ---------- 🚨 Pass/Fail ----------
    st.subheader("🚨 Pass/Fail Analysis")

    df["status"] = df["average"].apply(lambda x: "Pass" if x >= 40 else "Fail")
    st.write(df["status"].value_counts())

    # ---------- 📜 Student Report ----------
    st.subheader("📜 Individual Report")

    student_name = st.selectbox("Select student", df["name"])

    student = df[df["name"] == student_name].iloc[0]

    st.write(student)

    # ---------- 🤖 AI Feedback ----------
    st.subheader("🤖 AI Feedback")

    if AI:
        if st.button("Generate AI Feedback"):
            try:
                prompt = f"""
Student Performance:
Name: {student['name']}
Marks: {student[subjects].to_dict()}
Average: {student['average']}
Grade: {student['grade']}

Give:
1. Strengths
2. Weak areas
3. Improvement suggestions
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an academic performance analyst."},
                        {"role": "user", "content": prompt}
                    ]
                )

                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(str(e))
    else:
        st.info("Add OPENAI_API_KEY for AI feedback")

    # ---------- 💬 Ask Anything ----------
    st.subheader("💬 Ask About Class")

    question = st.text_input("Ask something (e.g., who is weakest?)")

    if question:
        if AI:
            try:
                data_summary = df.to_string()

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a data analyst."},
                        {
                            "role": "user",
                            "content": f"Dataset:\n{data_summary}\n\nQuestion:\n{question}"
                        }
                    ]
                )

                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Add API key for chat feature")