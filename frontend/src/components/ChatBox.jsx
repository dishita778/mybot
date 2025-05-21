
// import React, { useState,useEffect, useRef } from "react";
// import axios from "axios";
// import Message from "./Message";
// import "../styles/app.css";

// const ChatBox = ({ mode,className }) => {
//   const [messages, setMessages] = useState([]);
//   const [query, setQuery] = useState("");
//   const [language, setLanguage] = useState("English");
//   const [loading, setLoading] = useState(false);

//   const endOfMessagesRef = useRef(null);

//   useEffect(() => {
//     endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const sendMessage = async () => {
//     if (!query.trim()) return;

//     const newMessage = { sender: "user", text: query };
//     setMessages((prev) => [...prev, newMessage]);
//     setQuery("");
//     setLoading(true);
//     console.log("🟢 ChatBox sending message in mode:", mode);

//     try {
//       const res = await axios.post("http://localhost:5000/ask", {
//         query,
//         language,
//         domain: mode, // send mode to backend
//       });

//       const botMessage = {
//         sender: "bot",
//         text: res.data.response,
//         source: res.data.source_documents,
//       };

//       setMessages((prev) => [...prev, botMessage]);
//     } catch (error) {
//       setMessages((prev) => [
//         ...prev,
//         { sender: "bot", text: "❌ Something went wrong." },
//       ]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleKey = (e) => {
//     if (e.key === "Enter") sendMessage();
//   };

//   return (
//     <div className={chatbox ${className}}>
//       /* <div className="chat-header">
//         <h2>{mode === "mental_health" ? "🌿 Mental Health Mode":" "}</h2>
//       </div> */

//       <div className="response">
//         {messages.map((msg, idx) => (
//           <Message key={idx} {...msg} />
//         ))}
//                 {/* Scroll marker */}
//                 <div ref={endOfMessagesRef} />
//       </div>

//       <div className={`input-bar ${mode === "mental_health" ? "mental-input-bar" : "medical-input-bar"}`}>
//         <select value={language} onChange={(e) => setLanguage(e.target.value)}>
//           <option>English</option>
//           <option>Hindi</option>
//           <option>Gujarati</option>
//           <option>Marathi</option>
//           <option>Spanish</option>
//           <option>French</option>
//           <option>German</option>
//           <option>Chinese</option>
//           <option>Japanese</option>
//           <option>Arabic</option>
//         </select>

//         <input
//           type="text"
//           value={query}
//           onChange={(e) => setQuery(e.target.value)}
//           onKeyDown={handleKey}
//           placeholder={
//             mode === "mental_health"
//               ? "Share your mental health concerns..."
//               : "Ask a medical question..."
//           }
//         />

//         <button onClick={sendMessage} className="blue-btn">
//           {loading ? "⏳" : "Send"}
//         </button>
//       </div>
//     </div>
//   );
// };

// export default ChatBox;



import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import Message from "./Message";
import "../styles/app.css";

const ChatBox = ({ mode, className }) => {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState("English");
  const [loading, setLoading] = useState(false);

  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!query.trim()) return;

    const newMessage = { sender: "user", text: query };
    setMessages((prev) => [...prev, newMessage]);
    setQuery("");
    setLoading(true);
    console.log("🟢 ChatBox sending message in mode:", mode);

    try {
      const res = await axios.post("http://localhost:5000/ask", {
        query,
        language,
        domain: mode, // send mode to backend
      });

      const botMessage = {
        sender: "bot",
        text: res.data.response,
        source: res.data.source_documents,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Something went wrong." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    // <div className={`chatbox ${className}`}>

    <div className={`chatbox ${className}`}>

      <div className="response">
        {messages.map((msg, idx) => (
          <Message key={idx} {...msg} />
        ))}
        {/* Scroll marker */}
        <div ref={endOfMessagesRef} />
      </div>

      <div
        className={`input-bar ${
          mode === "mental_health" ? "mental-input-bar" : "medical-input-bar"
        }`}
      >
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option>English</option>
          <option>Hindi</option>
          <option>Gujarati</option>
          <option>Marathi</option>
          <option>Spanish</option>
          <option>French</option>
          <option>German</option>
          <option>Chinese</option>
          <option>Japanese</option>
          <option>Arabic</option>
        </select>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKey}
          placeholder={
            mode === "mental_health"
              ? "Share your mental health concerns..."
              : "Ask a medical question..."
          }
        />

        <button onClick={sendMessage} className="blue-btn">
          {loading ? "⏳" : "Send"}
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
