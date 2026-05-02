import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Optional AI (only works if you add API key)
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False


# ---------- Title ----------
st.title("📊 CSV Analyzer + AI Insights")

# ---------- Upload ----------
file = st.file_uploader("Upload your CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)

    # ---------- Preview ----------
    st.subheader("📄 Data Preview")
    st.dataframe(df)

    # ---------- Basic Info ----------
    st.subheader("📌 Dataset Info")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")
    st.write("Column Names:", list(df.columns))

    # ---------- Stats ----------
    st.subheader("📊 Statistical Summary")
    st.write(df.describe())

    # ---------- Missing Values ----------
    st.subheader("⚠️ Missing Values")
    st.write(df.isnull().sum())

    # ---------- Column Selection ----------
    st.subheader("📈 Visualize Column")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    if numeric_cols:
        col = st.selectbox("Choose column", numeric_cols)

        fig, ax = plt.subplots()
        ax.hist(df[col].dropna())
        ax.set_title(f"{col} Distribution")
        st.pyplot(fig)
    else:
        st.write("No numeric columns available")

    # ---------- Dataset Type Detection ----------
    st.subheader("🤖 Dataset Type Detection")

    def detect_type(columns):
        cols = [c.lower() for c in columns]
        if "name" in cols:
            return "Student Dataset"
        elif "price" in cols:
            return "Sales Dataset"
        elif "age" in cols:
            return "Demographic Dataset"
        else:
            return "Generic Dataset"

    dataset_type = detect_type(df.columns)
    st.write("Detected Type:", dataset_type)

    # ---------- AI Insights ----------
    st.subheader("🧠 AI Insights")

    if AI_AVAILABLE:
        if st.button("Generate AI Insights"):
            try:
                summary = df.describe().to_string()

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a data analyst."},
                        {
                            "role": "user",
                            "content": f"Analyze this dataset summary and give key insights:\n{summary}"
                        }
                    ]
                )

                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error("AI Error: " + str(e))
    else:
        st.info("AI insights require OpenAI API key setup.")