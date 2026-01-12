import React, { useState } from "react";
import axios from "axios";
import "../styles/app.css";

const AuthForm = ({ onLoginSuccess }) => {
  const [mode, setMode] = useState("login"); 
  const [name, setName] = useState("");
  const [identifier, setIdentifier] = useState(""); 
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = `http://127.0.0.1:5000/${mode}`;

    try {
      const res = await axios.post(
        url,
        mode === "register"
          ? { name, email: identifier, password }
          : { identifier, password }
      );

      if (res.data.success) {
        setMessage(" " + res.data.message);
        onLoginSuccess();
      } else {
        setMessage(" " + res.data.message);
      }
    } catch (error) {
      console.error(error);
      if (error.response && error.response.data.error) {
        setMessage(" " + error.response.data.error);
      } else {
        setMessage(" Something went wrong.");
      }
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = "http://127.0.0.1:5000/google/login";
  };

  return (
    <div className="login-container">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h3>{mode === "login" ? "LOGIN/SIGN UP": "Register"}</h3>

        {mode === "register" && (
          <input
            type="text"
            placeholder="Full Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        )}
        <input
          type="email"
          placeholder="Email"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" className="blue-btn">
          {mode === "login" ? "Login" : "Register"}
        </button>

        {message && <p style={{ color: "crimson" }}>{message}</p>}

        {}
          <button
            type="button"
            onClick={() => setMode(mode === "login" ? "Register" : "login")}
            className="toggle-btn"
          >
            {mode === "login" ? "Register/Sign up" : "Login"}
          </button>
        {}

        <button type="button" onClick={handleGoogleLogin} className="blue-btn google-btn">
          Continue with Google
        </button>
      </form>
    </div>
  );
};

export default AuthForm;
