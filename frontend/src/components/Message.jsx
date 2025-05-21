// import React from "react";

// const Message = ({ sender, text, source }) => (
//   <div className={`message ${sender}`}>
//     <div className="message-bubble">
//       <p>{text}</p>
//       {source && (
//         <details>
//           <summary>🔍 Source Documents</summary>
//           <ul>
//             {source.map((doc, i) => (
//               <li key={i}>{doc}</li>
//             ))}
//           </ul>
//         </details>
//       )}
//     </div>
//   </div>
// );

// export default Message;



import React from "react";

const Message = ({ sender, text, source, mode }) => {
  const isMentalHealth = mode === "mental_health";

  return (
    <div className={`message ${sender} ${isMentalHealth ? "mental-health-message" : ""}`}>
      <div className="message-bubble">
        <p>{text}</p>
        {source && (
          <details>
            <summary>🔍 Source Documents</summary>
            <ul>
              {source.map((doc, i) => (
                <li key={i}>{doc}</li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
};

export default Message;
