
import React, { useState, useEffect } from "react"; 
import ChatBox from "./components/ChatBox";
import AuthForm from "./components/AuthForm";
import Sidebar from "./components/Sidebar";
import axios from "axios";
import './styles/app.css';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [error, setError] = useState("");
  const [mode, setMode] = useState("medical");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("google_login") === "success") {
      setLoggedIn(true);
      window.history.replaceState({}, document.title, "/");
    } else if (params.get("error")) {
      setError(params.get("error"));
      window.history.replaceState({}, document.title, "/");
    }
  }, 
  []);

  const handleLogout = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:5000/logout");
      if (res.data.success) {
        setLoggedIn(false);
      }
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleToggleChange = () => {
    setMode((prevMode) =>
      prevMode === "medical" ? "mental_health" : "medical"
    );
  };

 
  return (
    <div className={`App ${mode === "mental_health" ? "mental-health-mode" : ""}`}>
       <div className="page-wrapper">
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {loggedIn ? (
    <main className="chat-main">
          <Sidebar />
          

    <div className="medibot-header">
    <img
    src={mode === "mental_health" ? "/Mental_Health.png" : "/Medical.png"}
    alt="Medibot Icon"
    className="medibot-icon"
  />
     <h1
  className={`text-2xl font-bold text-center mb-4 ${
    mode === "mental_health" ? "text-[#5E3219]" : "text-black"
  }`}
>
  {mode === "mental_health" ? "Medibot" : "Medibot"}
</h1>


</div>

          <div style={{ display: "flex", alignItems: "center", padding: "10px 20px",width: "100%" }}>
            <label className="switch">
              <input
                type="checkbox"
                onChange={handleToggleChange}
                checked={mode === "mental_health"}
              />
              <span className="slider round"></span>
            </label>
            <span className={`mode-label ${mode === "mental_health" ? "mental-health" : "medical"}`}>
              {mode === "mental_health" ? "Mental Health Mode 🌿" : "Default (Medical)"}
            </span>
          </div>
          <ChatBox mode={mode} />

          

          <button onClick={handleLogout} className="blue-btn logout-btn">
            Sign Out
          </button>
        </main>
      ) : (
        <AuthForm onLoginSuccess={() => setLoggedIn(true)} />
      )}
    </div>
    </div>

  );
}

export default App;


