import React, { useEffect, useState, useRef } from "react";
import "./styles.css";

export default function App() {
  const [tabs, setTabs] = useState([]);
  const [selectedTab, setSelectedTab] = useState(null);
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  // LOAD CHROME TABS + LISTEN FOR TAB EVENTS
  useEffect(() => {
    const loadTabs = () => {
      chrome.tabs.query({ currentWindow: true }, (updatedTabs) => {
        setTabs(updatedTabs);

        // If selected tab was closed → reset to null
        if (selectedTab && !updatedTabs.some((t) => t.id === selectedTab.id)) {
          setSelectedTab(null);
        }
      });
    };

    loadTabs();

    // TAB CREATED → REFRESH LIST
    chrome.tabs.onCreated.addListener(loadTabs);

    // TAB CLOSED → REMOVE AND RESET SELECTION IF NEEDED
    chrome.tabs.onRemoved.addListener((closedTabId) => {
      setTabs((prev) => prev.filter((t) => t.id !== closedTabId));

      if (selectedTab?.id === closedTabId) {
        setSelectedTab(null);
      }
    });

    // TAB UPDATED (title/url change)
    chrome.tabs.onUpdated.addListener(() => loadTabs());

    // USER SWITCHED ACTIVE TAB
    chrome.tabs.onActivated.addListener(() => loadTabs());

    return () => {
      chrome.tabs.onCreated.removeListener(loadTabs);
      chrome.tabs.onUpdated.removeListener(loadTabs);
      chrome.tabs.onActivated.removeListener(loadTabs);
      chrome.tabs.onRemoved.removeListener();
    };
  }, [selectedTab]);

  // SELECT / DESELECT TAB
  const handleSelect = (tab) => {
    if (selectedTab?.id === tab.id) {
      setSelectedTab(null); // clicking again = deselect
    } else {
      setSelectedTab(tab); // switch to new tab
    }
  };

  // SEND MESSAGE
  const handleSend = async () => {
    if (!message.trim()) {
      alert("Enter a message!");
      return;
    }

    const userMessage = message.trim();
    const tabTitle = selectedTab?.title || "No Tab Selected";

    // Add user message
    setChatHistory((prev) => [
      ...prev,
      { sender: "user", text: userMessage, tab: tabTitle },
    ]);

    setMessage("");
    setIsTyping(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tab_url: selectedTab?.url || "",
          user_message: userMessage,
        }),
      });

      const data = await response.json();

      setChatHistory((prev) => [
        ...prev,
        {
          sender: "bot",
          text: data.error ? `Error: ${data.error}` : data.response,
        },
      ]);
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        { sender: "bot", text: `Connection error: ${err.message}` },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // AUTO-SCROLL
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isTyping]);

  return (
    <div className="container">
      {/* CHAT AREA */}
      <div className="chat-section">
        {chatHistory.length === 0 && (
          <div className="header">
            <p className="title">Build with Agent</p>
            <p className="subtitle">AI responses may be inaccurate.</p>
          </div>
        )}

        <div className="chat-messages">
          {chatHistory.map((msg, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${
                msg.sender === "user" ? "user" : "bot"
              }`}
            >
              {msg.sender === "user" && msg.tab && (
                <div className="tab-label">{msg.tab}</div>
              )}
              <pre>{msg.text}</pre>
            </div>
          ))}

          {isTyping && (
            <div className="chat-bubble bot typing">
              <div className="dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={chatEndRef}></div>
        </div>
      </div>

      {/* TABS + INPUT */}
      <div className="bottom-section">
        {/* TAB BAR */}
        <div className="tabs">
          {tabs.map((tab) => {
            const isSelected = selectedTab?.id === tab.id;

            return (
              <div
                key={tab.id}
                className={`tab ${isSelected ? "active" : ""}`}
                onClick={() => handleSelect(tab)}
              >
                <span>{tab.title?.slice(0, 15)}...</span>
                <span className="plus-btn">{isSelected ? "×" : "+"}</span>
              </div>
            );
          })}
        </div>

        {/* INPUT AREA */}
        <div className="input-section">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe what to build next..."
          />
          <button onClick={handleSend}>▶</button>
        </div>
      </div>
    </div>
  );
}
