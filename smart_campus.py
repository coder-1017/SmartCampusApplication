import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv, io

# ── PAGE CONFIG ──
st.set_page_config(page_title="SMS", layout="wide", page_icon="🎓")

# Force light theme
st.markdown("""
<script>
var observer = new MutationObserver(function() {
    document.documentElement.setAttribute('data-theme', 'light');
});
observer.observe(document.documentElement, {attributes: true});
document.documentElement.setAttribute('data-theme', 'light');
</script>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for key, val in [("students", []), ("enrollments", {}), ("records", [])]:
    if key not in st.session_state:
        st.session_state[key] = val

# ── HELPERS ──
def evaluate_grade(score):
    if score >= 90: return "A", "Excellent"
    elif score >= 75: return "B", "Very Good"
    elif score >= 60: return "C", "Good"
    elif score >= 40: return "D", "Average"
    else: return "F", "Needs Improvement"

def bubble_sort(lst):
    arr = lst[:]
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def linear_search(arr, target):
    for i, v in enumerate(arr):
        if v == target: return i
    return -1

# ── GLOBAL STYLES ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #f8f9fa; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e9ecef !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #495057 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] h2 { color: #212529 !important; font-size: 1.1rem !important; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Metrics */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 600 !important; color: #212529 !important; }
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #6c757d !important; font-family: 'JetBrains Mono', monospace !important; text-transform: uppercase; letter-spacing: 0.05em; }

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border: 1px solid #dee2e6 !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
    background: #212529 !important;
    color: #fff !important;
    border-color: #212529 !important;
}
.stButton > button[kind="primary"]:hover { background: #343a40 !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox select {
    border-radius: 8px !important;
    border: 1px solid #dee2e6 !important;
    font-size: 14px !important;
    background: #ffffff !important;
    color: #212529 !important;
}
.stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
    color: #adb5bd !important;
    opacity: 1 !important;
}
.stTextInput input:focus, .stNumberInput input:focus { border-color: #495057 !important; box-shadow: none !important; }
/* Fix all text inside inputs/forms */
input, textarea, select { color: #212529 !important; background: #ffffff !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; border: 1px solid #e9ecef; }

/* Divider */
hr { border-color: #e9ecef !important; }

/* Code blocks */
.stCode { border-radius: 10px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }

/* Radio */
.stRadio > div { gap: 4px !important; }
.stRadio label { padding: 6px 10px !important; border-radius: 7px !important; transition: background 0.15s !important; }
.stRadio label:hover { background: #f1f3f5 !important; }

/* Page title chip */
.page-chip {
    display: inline-block;
    background: #212529;
    color: #fff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 6px;
    letter-spacing: 0.05em;
}
.page-head { font-size: 1.6rem; font-weight: 600; color: #212529; margin-bottom: 1.5rem; line-height: 1.2; }
.section-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #adb5bd; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🎓 SMS")
    st.caption("Student Management System")
    st.divider()
    module = st.radio("", [
        "01 · Registration",
        "02 · Enrollment",
        "03 · Records",
        "04 · Sort & Search",
        "05 · Fee Calculator",
        "06 · Export",
        "07 · Directory Scan",
        "08 · Analytics",
    ], label_visibility="collapsed")
    st.divider()
    n = len(st.session_state.students)
    st.markdown(f"<div style='font-family:JetBrains Mono,monospace;font-size:12px;color:#6c757d'>{n} student{'s' if n!=1 else ''} registered</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⊘ Clear all data", use_container_width=True):
        for k in ["students","enrollments","records"]: st.session_state[k] = [] if k!="enrollments" else {}
        st.success("Cleared.")
        st.rerun()

# ══════════════════════════════════════════
# MODULE 1 — REGISTRATION
# ══════════════════════════════════════════
if module.startswith("01"):
    st.markdown('<div class="page-chip">Module 01</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Registration & Grades</div>', unsafe_allow_html=True)

    students = st.session_state.students
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", len(students))
    if students:
        avg = sum(s["score"] for s in students) / len(students)
        top = max(students, key=lambda s: s["score"])
        c2.metric("Avg score", f"{avg:.1f}")
        c3.metric("Top scorer", top["name"].split()[0])
        c4.metric("Grade A", sum(1 for s in students if s["grade"]=="A"))
    else:
        c2.metric("Avg score", "—"); c3.metric("Top scorer", "—"); c4.metric("Grade A", 0)

    st.divider()
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-label">Register student</div>', unsafe_allow_html=True)
        with st.form("reg", clear_on_submit=True):
            name  = st.text_input("Full name", placeholder="e.g. Priya Sharma")
            score = st.number_input("Exam score (0–100)", 0.0, 100.0, step=0.5)
            if st.form_submit_button("Register →", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Name cannot be empty.")
                else:
                    g, r = evaluate_grade(score)
                    sid = 100 + len(st.session_state.students) + 1
                    st.session_state.students.append({"id":sid,"name":name.strip(),"score":score,"grade":g,"remark":r})
                    st.success(f"✓ {name} registered — ID {sid}, Grade {g} ({r})")

    with col2:
        st.markdown('<div class="section-label">Grade scale</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"Range":"90–100","Grade":"A","Remark":"Excellent"},
            {"Range":"75–89", "Grade":"B","Remark":"Very Good"},
            {"Range":"60–74", "Grade":"C","Remark":"Good"},
            {"Range":"40–59", "Grade":"D","Remark":"Average"},
            {"Range":"0–39",  "Grade":"F","Remark":"Needs Improvement"},
        ]), hide_index=True, use_container_width=True)

    if students:
        st.divider()
        st.markdown('<div class="section-label">All students</div>', unsafe_allow_html=True)
        df = pd.DataFrame(students)[["id","name","score","grade","remark"]]
        df.columns = ["ID","Name","Score","Grade","Remark"]
        st.dataframe(df, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════
# MODULE 2 — ENROLLMENT
# ══════════════════════════════════════════
elif module.startswith("02"):
    st.markdown('<div class="page-chip">Module 02</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Course Enrollment</div>', unsafe_allow_html=True)

    if not st.session_state.students:
        st.info("Register students in Module 01 first.")
    else:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="section-label">Enroll</div>', unsafe_allow_html=True)
            chosen = st.selectbox("Student", [f"{s['name']} (ID {s['id']})" for s in st.session_state.students])
            sname = chosen.split(" (ID")[0]
            with st.form("enroll", clear_on_submit=True):
                cname   = st.text_input("Course name", placeholder="e.g. Data Structures")
                credits = st.number_input("Credits", 1, 6, step=1)
                if st.form_submit_button("Add course →", type="primary", use_container_width=True):
                    enr = st.session_state.enrollments
                    if not cname.strip(): st.error("Course name required.")
                    elif len(enr.get(sname,[])) >= 5: st.warning("Max 5 courses reached.")
                    else:
                        enr.setdefault(sname,[]).append({"course":cname.strip(),"credits":int(credits)})
                        st.success(f'✓ Added "{cname}" ({credits} cr)')

        with col2:
            st.markdown('<div class="section-label">Summary</div>', unsafe_allow_html=True)
            enr = st.session_state.enrollments.get(sname, [])
            if not enr:
                st.info("No courses yet.")
            else:
                df = pd.DataFrame(enr); df.index += 1; df.columns=["Course","Credits"]
                st.dataframe(df, use_container_width=True)
                st.metric("Total credits", sum(e["credits"] for e in enr))

# ══════════════════════════════════════════
# MODULE 3 — RECORDS
# ══════════════════════════════════════════
elif module.startswith("03"):
    st.markdown('<div class="page-chip">Module 03</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Student Records</div>', unsafe_allow_html=True)

    with st.form("rec", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name  = c1.text_input("Name")
        age   = c2.number_input("Age", 1, 100, step=1)
        raw   = c3.text_input("Grades (space-separated)", placeholder="85 90 78")
        if st.form_submit_button("Add record →", type="primary", use_container_width=True):
            try:
                grades = [float(g) for g in raw.strip().split()]
                if not name.strip() or not grades: raise ValueError
                st.session_state.records.append({"name":name.strip(),"age":int(age),"grades":grades})
                st.success(f"✓ Record added for {name}")
            except: st.error("Fill in all fields with valid values.")

    if st.session_state.records:
        st.divider()
        rows = []
        for r in st.session_state.records:
            avg = sum(r["grades"])/len(r["grades"])
            g,_ = evaluate_grade(avg)
            rows.append({"Name":r["name"],"Age":r["age"],"Grades":", ".join(str(x) for x in r["grades"]),"Avg":round(avg,1),"Grade":g})
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

# ══════════════════════════════════════════
# MODULE 4 — SORT & SEARCH
# ══════════════════════════════════════════
elif module.startswith("04"):
    st.markdown('<div class="page-chip">Module 04</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Sort & Search</div>', unsafe_allow_html=True)

    if not st.session_state.students:
        st.info("Register students in Module 01 first.")
    else:
        ids = [s["id"] for s in st.session_state.students]
        sorted_ids = bubble_sort(ids)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="section-label">Unsorted</div>', unsafe_allow_html=True)
            st.code("  ".join(str(i) for i in ids))
        with col2:
            st.markdown('<div class="section-label">Bubble sorted</div>', unsafe_allow_html=True)
            st.code("  ".join(str(i) for i in sorted_ids))

        st.divider()
        st.markdown('<div class="section-label">Linear search</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2,1], gap="medium")
        target = c1.number_input("Student ID", min_value=100, step=1, label_visibility="collapsed")
        if c2.button("Search →", type="primary", use_container_width=True):
            idx = linear_search(sorted_ids, int(target))
            if idx != -1:
                m = next(s for s in st.session_state.students if s["id"]==int(target))
                st.success(f"✓ Found ID **{target}** at index **{idx}** — {m['name']}, Grade {m['grade']}")
            else:
                st.error(f"ID {target} not found.")

# ══════════════════════════════════════════
# MODULE 5 — FEE CALCULATOR
# ══════════════════════════════════════════
elif module.startswith("05"):
    st.markdown('<div class="page-chip">Module 05</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Fee Calculator</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="section-label">Enter fees</div>', unsafe_allow_html=True)
        tuition   = st.number_input("Tuition fee (₹)",       0.0, step=500.0, format="%.2f")
        hostel    = st.number_input("Hostel fee (₹)",         0.0, step=500.0, format="%.2f")
        transport = st.number_input("Transportation fee (₹)", 0.0, step=100.0, format="%.2f")

    with col2:
        st.markdown('<div class="section-label">Breakdown</div>', unsafe_allow_html=True)
        total = tuition + hostel + transport
        st.dataframe(pd.DataFrame([
            {"Component":"Tuition",        "Amount (₹)": f"{tuition:,.2f}"},
            {"Component":"Hostel",          "Amount (₹)": f"{hostel:,.2f}"},
            {"Component":"Transportation",  "Amount (₹)": f"{transport:,.2f}"},
        ]), hide_index=True, use_container_width=True)
        st.metric("Total payable", f"₹ {total:,.2f}")

# ══════════════════════════════════════════
# MODULE 6 — EXPORT
# ══════════════════════════════════════════
elif module.startswith("06"):
    st.markdown('<div class="page-chip">Module 06</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">File Export</div>', unsafe_allow_html=True)

    if not st.session_state.students:
        st.info("No students to export yet.")
    else:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["ID","Name","Score","Grade","Remark"])
        for s in st.session_state.students:
            w.writerow([s["id"],s["name"],int(s["score"]),s["grade"],s["remark"]])
        csv_str = buf.getvalue()
        st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)
        st.code(csv_str, language="text")
        st.download_button("⬇ Download student_records.csv", csv_str, "student_records.csv", "text/csv", use_container_width=True, type="primary")

# ══════════════════════════════════════════
# MODULE 7 — DIRECTORY SCAN
# ══════════════════════════════════════════
elif module.startswith("07"):
    st.markdown('<div class="page-chip">Module 07</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Directory Scan</div>', unsafe_allow_html=True)
    st.caption("Simulates `os.walk()` output.")

    c1, c2 = st.columns([3,1], gap="medium")
    path = c1.text_input("Path", value=".", label_visibility="collapsed", placeholder="/home/student/projects")
    scan = c2.button("Scan →", type="primary", use_container_width=True)

    if scan:
        base = path.rstrip("/") + "/"
        tree = [
            (base,"dir"),(base+"assignments/","dir"),
            (base+"assignments/hw1.pdf","file"),(base+"assignments/hw2.pdf","file"),
            (base+"assignments/project_report.docx","file"),
            (base+"notes/","dir"),(base+"notes/lecture_01.md","file"),
            (base+"notes/lecture_02.md","file"),
            (base+"data/","dir"),(base+"data/student_performance.csv","file"),
            (base+"data/student_records.txt","file"),
            (base+"student_management.py","file"),
        ]
        bd = base.count("/")
        lines = []
        for p,t in tree:
            d = p.count("/") - bd
            name = p.rstrip("/").split("/")[-1]
            lines.append("    "*d + name + ("/" if t=="dir" else ""))
        st.code("\n".join(lines), language="text")
        files = sum(1 for _,t in tree if t=="file")
        dirs  = sum(1 for _,t in tree if t=="dir")
        st.caption(f"{files} files · {dirs} directories found in `{path}`")

# ══════════════════════════════════════════
# MODULE 8 — ANALYTICS
# ══════════════════════════════════════════
elif module.startswith("08"):
    st.markdown('<div class="page-chip">Module 08</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-head">Performance Analytics</div>', unsafe_allow_html=True)

    default = "Name,Math,Science,English\nPriya,88,92,85\nRahul,75,80,70\nAnita,95,89,93\nKiran,60,72,68\nSneha,82,78,88"
    data = st.text_area("CSV input", value=default, height=160)

    if st.button("Generate analytics →", type="primary"):
        try:
            df = pd.read_csv(io.StringIO(data))
            df.columns = [c.strip() for c in df.columns]
            scores = df[["Math","Science","English"]].to_numpy()
            means  = np.mean(scores, axis=0)

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Avg Math",    f"{means[0]:.1f}")
            c2.metric("Avg Science", f"{means[1]:.1f}")
            c3.metric("Avg English", f"{means[2]:.1f}")
            c4.metric("Students",    len(df))

            st.divider()
            left, right = st.columns(2, gap="large")

            with left:
                st.markdown('<div class="section-label">Scores table</div>', unsafe_allow_html=True)
                df["Avg"]   = scores.mean(axis=1).round(1)
                df["Grade"] = df["Avg"].apply(lambda s: evaluate_grade(s)[0])
                st.dataframe(df, hide_index=True, use_container_width=True)

            with right:
                st.markdown('<div class="section-label">Subject averages — bar chart</div>', unsafe_allow_html=True)
                fig, ax = plt.subplots(figsize=(5, 3.2))
                bars = ax.bar(["Math","Science","English"], means,
                              color=["#212529","#495057","#adb5bd"], width=0.45)
                ax.set_ylim(0,100); ax.set_ylabel("Score", fontsize=10)
                ax.set_facecolor("#f8f9fa"); fig.patch.set_facecolor("#f8f9fa")
                for sp in ["top","right"]: ax.spines[sp].set_visible(False)
                for sp in ["left","bottom"]: ax.spines[sp].set_color("#dee2e6")
                ax.tick_params(colors="#495057", labelsize=10)
                for bar, v in zip(bars, means):
                    ax.text(bar.get_x()+bar.get_width()/2, v+1, f"{v:.1f}",
                            ha="center", va="bottom", fontsize=10, color="#212529", fontweight="500")
                plt.tight_layout()
                st.pyplot(fig); plt.close(fig)

            st.divider()
            col_pie, col_line = st.columns(2, gap="large")

            with col_pie:
                st.markdown('<div class="section-label">Score share — pie chart</div>', unsafe_allow_html=True)
                avgs = scores.mean(axis=1)
                colors_pie = ["#212529","#495057","#6c757d","#adb5bd","#ced4da","#dee2e6"]
                fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                wedges, texts, autotexts = ax2.pie(
                    avgs, labels=df["Name"].tolist(),
                    autopct="%1.1f%%", startangle=140,
                    colors=colors_pie[:len(avgs)],
                    pctdistance=0.8,
                    wedgeprops={"linewidth":1.5,"edgecolor":"#f8f9fa"}
                )
                for t in texts: t.set_fontsize(10); t.set_color("#212529")
                for at in autotexts: at.set_fontsize(9); at.set_color("#ffffff")
                fig2.patch.set_facecolor("#f8f9fa")
                plt.tight_layout()
                st.pyplot(fig2); plt.close(fig2)

            with col_line:
                st.markdown('<div class="section-label">Subject performance — line plot</div>', unsafe_allow_html=True)
                subjects = ["Math","Science","English"]
                colors_line = ["#212529","#495057","#6c757d","#adb5bd","#ced4da"]
                fig3, ax3 = plt.subplots(figsize=(5, 3.5))
                for i, row in df.iterrows():
                    vals = [row["Math"], row["Science"], row["English"]]
                    ax3.plot(subjects, vals,
                             marker="o", linewidth=2, markersize=5,
                             label=row["Name"],
                             color=colors_line[i % len(colors_line)])
                ax3.set_ylim(0, 100)
                ax3.set_ylabel("Score", fontsize=10)
                ax3.set_facecolor("#f8f9fa"); fig3.patch.set_facecolor("#f8f9fa")
                for sp in ["top","right"]: ax3.spines[sp].set_visible(False)
                for sp in ["left","bottom"]: ax3.spines[sp].set_color("#dee2e6")
                ax3.tick_params(colors="#495057", labelsize=10)
                ax3.legend(fontsize=9, framealpha=0, labelcolor="#212529")
                plt.tight_layout()
                st.pyplot(fig3); plt.close(fig3)

        except Exception as e:
            st.error(f"Could not parse CSV: {e}")