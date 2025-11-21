import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import api from "../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [activeSection, setActiveSection] = useState("Home");
  const [selectedSubject, setSelectedSubject] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("hv_token");
    const userData = localStorage.getItem("hv_user");

    if (!token || !userData) {
      router.push("/login");
      return;
    }

    setUser(JSON.parse(userData));

    api
      .get("/protected", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setMessage(res.data.message))
      .catch(() => {
        localStorage.clear();
        router.push("/login");
      });
  }, []);

  const logout = () => {
    localStorage.clear();
    router.push("/login");
  };

  const subjects = [
    {
      name: "Digital Design",
      color: "#4f46e5",
      handouts: ["Boolean Algebra.pdf", "Combinational Circuits.pptx"],
      quizzes: ["Logic Gates Quiz", "Flip-Flop Quiz"],
    },
    {
      name: "Computer Organization",
      color: "#10b981",
      handouts: ["CPU Architecture.pdf", "Memory Hierarchy.docx"],
      quizzes: ["Processor Quiz", "Cache Systems Quiz"],
    },
    {
      name: "Linear Algebra",
      color: "#f59e0b",
      handouts: ["Matrix Operations.pdf", "Vector Spaces.pptx"],
      quizzes: ["Matrices Quiz", "Determinants Quiz"],
    },
    {
      name: "Object Oriented Programming",
      color: "#ef4444",
      handouts: ["OOP Basics.pdf", "Inheritance.docx"],
      quizzes: ["Classes Quiz", "Polymorphism Quiz"],
    },
  ];

  if (!user) return null;

  // ---------------- CONTENT RENDER ----------------
  const renderContent = () => {
    if (activeSection === "Subjects") {
      if (!selectedSubject) {
        return (
          <div style={styles.subjectGrid}>
            {subjects.map((sub) => (
              <div
                key={sub.name}
                style={{ ...styles.subjectCard, background: sub.color }}
                onClick={() => setSelectedSubject(sub)}
              >
                <h3 style={styles.subjectTitle}>{sub.name}</h3>
              </div>
            ))}
          </div>
        );
      }

      return (
        <div style={styles.subjectDetail}>
          <h2 style={{ marginBottom: 20 }}>{selectedSubject.name}</h2>
          <div style={styles.sectionGroup}>
            <h3>📘 Handouts</h3>
            <ul>
              {selectedSubject.handouts.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </div>
          <div style={styles.sectionGroup}>
            <h3>📝 Quizzes</h3>
            <ul>
              {selectedSubject.quizzes.map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ul>
          </div>
          <button style={styles.backBtn} onClick={() => setSelectedSubject(null)}>
            ← Back to Subjects
          </button>
        </div>
      );
    }

    if (activeSection === "Home") {
      return (
        <div style={{ display: "flex", flexDirection: "column", gap: 40 }}>
          {/* Search and Upload */}
          <div style={styles.searchBarContainer}>
            <input
              type="text"
              placeholder="Search handouts, assignments..."
              style={styles.searchInput}
            />
            <button style={styles.uploadBtn}>+ Upload</button>
          </div>

          {/* Recent Uploads */}
          <section>
            <h3>📂 Recent Uploads</h3>
            <div style={styles.cardGrid}>
              {["Chapter 1 - Basics", "Lecture Notes - Week 2", "Assignment 3", "Quiz 1 Solution"].map(
                (item) => (
                  <div key={item} style={styles.uploadCard}>
                    <p style={{ fontWeight: 600 }}>{item}</p>
                    <p style={{ color: "#666", fontSize: 14 }}>Uploaded 2 days ago</p>
                  </div>
                )
              )}
            </div>
          </section>

          {/* Subjects Preview */}
          <section>
            <h3>📘 Subjects</h3>
            <div style={styles.subjectGridPreview}>
              {subjects.map((sub) => (
                <div
                  key={sub.name}
                  style={{ ...styles.subjectCardSmall, background: sub.color }}
                  onClick={() => {
                    setActiveSection("Subjects");
                    setSelectedSubject(sub);
                  }}
                >
                  {sub.name}
                </div>
              ))}
            </div>
          </section>

          {/* Handouts */}
          <section>
            <h3>📄 Handouts </h3>
            <div style={styles.handoutList}>
              {[
                { title: "Data Structures - v1.2", color: "#4f46e5" },
                { title: "Machine Learning - v3.1", color: "#10b981" },
                { title: "Linear Algebra - v2.5", color: "#f59e0b" },
                { title: "Digital Design - v1.0", color: "#ef4444" },
              ].map((h) => (
                <div
                  key={h.title}
                  style={{
                    ...styles.handoutCard,
                    borderLeft: `6px solid ${h.color}`,
                  }}
                >
                  <p style={{ fontWeight: 600 }}>{h.title}</p>
                  <p style={{ color: "#666", fontSize: 13 }}>Last updated: Today</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      );
    }

    if (activeSection === "Recent")
      return (
        <div>
          <h3>Recent Files</h3>
          <p>No recent items yet.</p>
        </div>
      );

    if (activeSection === "Trash")
      return (
        <div>
          <h3>Trash Bin</h3>
          <p>No deleted items.</p>
        </div>
      );

    if (activeSection === "Settings")
      return (
        <div>
          <h3>Settings</h3>
          <p>Profile customization and preferences.</p>
        </div>
      );
  };

  // ---------------- UI ----------------
  return (
    <div style={styles.wrapper}>
      {/* Sidebar */}
      <aside style={styles.sidebar}>
        <div style={styles.logo}>
          <h2 style={{ margin: 0, color: "#0070f3" }}>Handout Vault</h2>
        </div>

        <nav style={styles.nav}>
          {["Home", "Recent", "Trash", "Subjects", "Settings"].map((item) => (
            <div
              key={item}
              onClick={() => {
                setActiveSection(item);
                setSelectedSubject(null);
              }}
              style={{
                ...styles.navItem,
                background: activeSection === item ? "#0070f3" : "transparent",
                color: activeSection === item ? "white" : "#333",
              }}
            >
              {item}
            </div>
          ))}
        </nav>

        <div style={styles.sidebarFooter}>
          <button style={styles.logoutBtn} onClick={logout}>
            Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={styles.main}>
        <div style={styles.header}>
          <h1>{activeSection}</h1>
          <p style={{ color: "#555" }}>Welcome, {user.email}</p>
        </div>
        <div style={styles.content}>{renderContent()}</div>
      </main>
    </div>
  );
}

// ---------------- STYLES ----------------
const styles = {
  wrapper: {
    display: "flex",
    height: "100vh",
    fontFamily: "system-ui, sans-serif",
    background: "#f8f9fa",
    color: "#222",
  },
  sidebar: {
    width: "240px",
    background: "#fff",
    borderRight: "1px solid #ddd",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "20px 0",
    boxShadow: "2px 0 6px rgba(0,0,0,0.05)",
  },
  logo: {
    textAlign: "center",
    marginBottom: 20,
  },
  nav: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
    padding: "0 20px",
  },
  navItem: {
    padding: "10px 14px",
    borderRadius: 6,
    cursor: "pointer",
    fontSize: 16,
    transition: "all 0.2s ease",
  },
  sidebarFooter: {
    padding: "0 20px",
  },
  logoutBtn: {
    width: "100%",
    padding: "10px 0",
    border: "none",
    borderRadius: 6,
    background: "#e63946",
    color: "white",
    cursor: "pointer",
    fontWeight: 500,
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "30px 40px",
    overflowY: "auto",
  },
  header: {
    marginBottom: 30,
    borderBottom: "1px solid #ddd",
    paddingBottom: 10,
  },
  content: {
    background: "white",
    padding: 20,
    borderRadius: 10,
    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
    minHeight: "60vh",
  },

  // HOME PAGE STYLES
  searchBarContainer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  searchInput: {
    width: "80%",
    padding: 10,
    borderRadius: 6,
    border: "1px solid #ccc",
    fontSize: 15,
  },
  uploadBtn: {
    background: "#0070f3",
    color: "white",
    border: "none",
    borderRadius: 6,
    padding: "10px 18px",
    fontWeight: 600,
    cursor: "pointer",
  },
  cardGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: 20,
    marginTop: 20,
  },
  uploadCard: {
    background: "#f1f5f9",
    borderRadius: 8,
    padding: 15,
    boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
  },
  subjectGridPreview: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 20,
    marginTop: 20,
  },
  subjectCardSmall: {
    height: 100,
    borderRadius: 10,
    color: "white",
    fontWeight: 600,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    boxShadow: "0 6px 12px rgba(0,0,0,0.1)",
    transition: "transform 0.2s ease",
  },
  handoutList: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    marginTop: 10,
  },
  handoutCard: {
    background: "#f8fafc",
    borderRadius: 6,
    padding: 10,
    boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
  },

  // SUBJECT SECTION STYLES
  subjectGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: 20,
    justifyItems: "center",
    marginTop: 40,
  },
  subjectCard: {
    width: 220,
    height: 150,
    borderRadius: 12,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
    boxShadow: "0 6px 12px rgba(0,0,0,0.15)",
    transition: "transform 0.2s ease, box-shadow 0.2s ease",
  },
  subjectTitle: {
    fontSize: 18,
    textAlign: "center",
  },
  subjectDetail: {
    textAlign: "left",
    padding: 20,
  },
  sectionGroup: {
    marginBottom: 30,
  },
  backBtn: {
    background: "#0070f3",
    color: "white",
    border: "none",
    borderRadius: 6,
    padding: "8px 14px",
    cursor: "pointer",
  },
};
