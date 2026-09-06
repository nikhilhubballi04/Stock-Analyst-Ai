import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api";
import { useTheme } from "../ThemeContext";
import "./Auth.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      navigate("/home");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <button
          onClick={toggleTheme}
          style={{
            position: "absolute", top: "1.2rem", right: "1.2rem",
            background: "var(--card-bg)", border: "1px solid var(--border)",
            borderRadius: "8px", padding: "0.4rem 0.7rem", fontSize: "0.8rem",
            color: "var(--text)"
          }}
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        <span className="auth-badge">MULTI-AGENT AI PIPELINE</span>
        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to run autonomous market analysis.</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="auth-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <button type="submit" className="auth-button" disabled={loading}>
            {loading ? "Signing in..." : "Log In"}
          </button>
        </form>

        <div className="auth-switch">
          Don't have an account? <Link to="/signup">Sign up →</Link>
        </div>
      </div>
    </div>
  );
}

export default Login;