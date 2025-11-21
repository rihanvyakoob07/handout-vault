import { useState } from "react";
import { useRouter } from "next/router";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("rihan.y@hcltech.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Fake delay
      await new Promise((res) => setTimeout(res, 700));

      // Fake login success
      const fakeUser = {
        id: "user-123",
        email,
        is_admin: false,
      };

      localStorage.setItem("hv_token", "dummy_token_xyz");
      localStorage.setItem("hv_user", JSON.stringify(fakeUser));

      router.push("/dashboard");
    } catch (err) {
      setError("Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyles.wrapper}>
      <div style={pageStyles.card}>
        <h2 style={pageStyles.title}>Handout Vault</h2>
        <p style={pageStyles.subtitle}>Sign in to continue</p>

        <form onSubmit={handleSubmit} style={pageStyles.form}>
          <input
            type="email"
            value={email}
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
            style={pageStyles.input}
            required
          />

          <input
            type="password"
            value={password}
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
            style={pageStyles.input}
            required
          />

          <button type="submit" style={pageStyles.button} disabled={loading}>
            {loading ? "Signing in..." : "Login"}
          </button>

          {error && <p style={pageStyles.error}>{error}</p>}
        </form>
      </div>
    </div>
  );
}

const pageStyles = {
  wrapper: {
    height: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f4f4f4",
  },
  card: {
    width: 350,
    background: "white",
    padding: 30,
    borderRadius: 10,
    boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
  },
  title: {
    textAlign: "center",
    fontSize: 24,
    fontWeight: 700,
  },
  subtitle: {
    textAlign: "center",
    color: "#666",
    marginBottom: 20,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 14,
  },
  input: {
    padding: 12,
    border: "1px solid #ccc",
    borderRadius: 8,
  },
  button: {
    padding: 12,
    background: "#2563eb",
    color: "white",
    borderRadius: 8,
    border: "none",
    fontWeight: 600,
    cursor: "pointer",
  },
  error: {
    color: "red",
    textAlign: "center",
  },
};
