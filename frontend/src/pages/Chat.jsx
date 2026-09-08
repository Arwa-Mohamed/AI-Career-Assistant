import { useEffect, useMemo, useRef, useState } from "react";

import { sendChatMessage } from "../services/api";

import "./Chat.css";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const [sessionId, setSessionId] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // =========================================================
  // SUGGESTIONS
  // =========================================================

  const suggestions = [
    {
      title: "Career Skills",
      text: "What skills should I learn next?",
    },
    {
      title: "Improve My CV",
      text: "How can I improve my CV?",
    },
    {
      title: "Career Readiness",
      text: "Am I ready for a backend developer job?",
    },
    {
      title: "Interview Prep",
      text: "How should I prepare for my next interview?",
    },
  ];

  // =========================================================
  // AUTO SCROLL
  // =========================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // =========================================================
  // FOCUS INPUT
  // =========================================================

  useEffect(() => {
    inputRef.current?.focus();
  }, [loading]);

  // =========================================================
  // MESSAGE COUNT
  // =========================================================

  const messageCount = useMemo(
    () => messages.length,
    [messages]
  );

  // =========================================================
  // SEND MESSAGE
  // =========================================================

  const handleSend = async (event) => {
    event.preventDefault();

    const text = input.trim();

    if (!text || loading) {
      return;
    }

    setError("");
    setCopiedIndex(null);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: text,
        createdAt: new Date().toISOString(),
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(
        text,
        sessionId
      );

      if (data?.session_id) {
        setSessionId(data.session_id);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data?.message ||
            "I couldn't generate a response.",
          createdAt:
            new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError(
        err?.message ||
          "Something went wrong while contacting the AI Assistant."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // SUGGESTION
  // =========================================================

  const handleSuggestion = (text) => {
    if (loading) {
      return;
    }

    setInput(text);

    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  // =========================================================
  // NEW CONVERSATION
  // =========================================================

  const handleNewConversation = () => {
    if (loading) {
      return;
    }

    setMessages([]);
    setInput("");
    setSessionId(null);
    setError("");
    setCopiedIndex(null);

    setTimeout(() => {
      inputRef.current?.focus();
    }, 0);
  };

  // =========================================================
  // COPY MESSAGE
  // =========================================================

  const handleCopy = async (
    content,
    index
  ) => {
    try {
      await navigator.clipboard.writeText(
        content
      );

      setCopiedIndex(index);

      setTimeout(() => {
        setCopiedIndex(null);
      }, 1800);
    } catch {
      setError(
        "Unable to copy this message."
      );
    }
  };

  // =========================================================
  // FORMAT TIME
  // =========================================================

  const formatTime = (dateValue) => {
    if (!dateValue) {
      return "";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
      return "";
    }

    return date.toLocaleTimeString(
      undefined,
      {
        hour: "numeric",
        minute: "2-digit",
      }
    );
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="chat-page">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="chat-page-header">

        <div className="chat-header-main">

          <div className="chat-ai-avatar">
            AI
          </div>

          <div>

            <div className="chat-eyebrow">
              AI CAREER INTELLIGENCE
            </div>

            <h1>
              AI Career Assistant
            </h1>

            <p>
              Your personal AI coach for skills,
              careers, jobs, CVs, and interviews.
            </p>

          </div>

        </div>


        <div className="chat-header-actions">

          <div className="chat-status">

            <span className="chat-status-dot" />

            <span>
              AI Assistant Online
            </span>

          </div>

          <button
            type="button"
            className="chat-new-button"
            onClick={handleNewConversation}
            disabled={loading}

          >
            + New Conversation
          </button>

        </div>

      </header>


      {/* =====================================================
          CHAT WORKSPACE
      ===================================================== */}

      <section className="chat-workspace">

        {/* ===================================================
            CHAT TOP BAR
        =================================================== */}

        <div className="chat-toolbar">

          <div className="chat-toolbar-info">

            <div className="chat-toolbar-title">
              Career Conversation
            </div>

            <div className="chat-toolbar-meta">

              <span>
                {messageCount}{" "}
                {messageCount === 1
                  ? "message"
                  : "messages"}
              </span>

              {sessionId && (
                <>
                  <span className="chat-meta-dot">
                    •
                  </span>

                  <span>
                    Active session
                  </span>
                </>
              )}

            </div>

          </div>


          {messages.length > 0 && (
            <button
              type="button"
              className="chat-clear-button"
              onClick={
                handleNewConversation
              }
              disabled={loading}
            >
              Clear chat
            </button>
          )}

        </div>


        {/* ===================================================
            MESSAGES AREA
        =================================================== */}

        <div className="chat-messages">

          {/* =================================================
              EMPTY STATE
          ================================================= */}

          {messages.length === 0 && (
            <div className="chat-empty-state">

              <div className="chat-empty-icon">
                AI
              </div>

              <div className="chat-welcome">

                <span className="chat-welcome-label">
                  YOUR AI CAREER COACH
                </span>

                <h2>
                  How can I help you today?
                </h2>

                <p>
                  Ask me about your career path,
                  CV, skills, jobs, projects,
                  or interview preparation.
                </p>

              </div>


              {/* Suggestions */}

              <div className="chat-suggestions">

                {suggestions.map(
                  (suggestion) => (
                    <button
                      type="button"
                      key={suggestion.title}
                      className="chat-suggestion-card"
                      onClick={() =>
                        handleSuggestion(
                          suggestion.text
                        )
                      }
                      disabled={loading}
                    >

                      <span className="chat-suggestion-icon">
                        +
                      </span>

                      <span>

                        <strong>
                          {suggestion.title}
                        </strong>

                        <small>
                          {suggestion.text}
                        </small>

                      </span>

                      <span className="chat-suggestion-arrow">
                        →
                      </span>

                    </button>
                  )
                )}

              </div>


              {/* Capability Hint */}

              <div className="chat-capabilities">

                <span>
                  I can help with
                </span>

                <div>

                  <span>CV</span>
                  <span>Skills</span>
                  <span>Jobs</span>
                  <span>Projects</span>
                  <span>Interviews</span>

                </div>

              </div>

            </div>
          )}


          {/* =================================================
              MESSAGES
          ================================================= */}

          {messages.map(
            (message, index) => {

              const isUser =
                message.role === "user";

              return (
                <div
                  key={`${index}-${message.createdAt || ""}`}
                  className={`chat-message-row ${
                    isUser
                      ? "chat-message-user"
                      : "chat-message-assistant"
                  }`}
                >

                  {/* Avatar */}

                  <div className="chat-message-avatar">

                    {isUser
                      ? "You"
                      : "AI"}

                  </div>


                  {/* Message Content */}

                  <div className="chat-message-content">

                    <div className="chat-message-meta">

                      <strong>
                        {isUser
                          ? "You"
                          : "AI Career Assistant"}
                      </strong>

                      {message.createdAt && (
                        <span>
                          {formatTime(
                            message.createdAt
                          )}
                        </span>
                      )}

                    </div>


                    <div
                      className={`chat-message-bubble ${
                        isUser
                          ? "chat-user-bubble"
                          : "chat-assistant-bubble"
                      }`}
                    >

                      <p>
                        {message.content}
                      </p>

                    </div>


                    {/* Assistant Actions */}

                    {!isUser && (
                      <div className="chat-message-actions">

                        <button
                          type="button"
                          onClick={() =>
                            handleCopy(
                              message.content,
                              index
                            )
                          }
                        >
                          {copiedIndex ===
                          index
                            ? "✓ Copied"
                            : "Copy"}
                        </button>

                      </div>
                    )}

                  </div>

                </div>
              );
            }
          )}


          {/* =================================================
              THINKING
          ================================================= */}

          {loading && (
            <div className="chat-message-row chat-message-assistant">

              <div className="chat-message-avatar">
                AI
              </div>

              <div className="chat-message-content">

                <div className="chat-message-meta">

                  <strong>
                    AI Career Assistant
                  </strong>

                  <span>
                    Thinking
                  </span>

                </div>


                <div className="chat-message-bubble chat-assistant-bubble">

                  <div className="chat-thinking">

                    <span />
                    <span />
                    <span />

                    <em>
                      Thinking...
                    </em>

                  </div>

                </div>

              </div>

            </div>
          )}


          <div
            ref={messagesEndRef}
            className="chat-scroll-anchor"
          />

        </div>


        {/* ===================================================
            ERROR
        =================================================== */}

        {error && (
          <div className="chat-error">

            <span className="chat-error-icon">
              !
            </span>

            <span>
              {error}
            </span>

            <button
              type="button"
              onClick={() =>
                setError("")
              }
            >
              ×
            </button>

          </div>
        )}


        {/* ===================================================
            INPUT AREA
        =================================================== */}

        <div className="chat-composer-wrapper">

          <form
            className="chat-composer"
            onSubmit={handleSend}
          >

            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(event) =>
                setInput(
                  event.target.value
                )
              }
              placeholder="Ask your AI career coach anything..."
              disabled={loading}
              maxLength={2000}
              aria-label="Career assistant message"
            />

            <div className="chat-composer-footer">

              <span>
                {input.length}/2000
              </span>

              <button
                type="submit"
                disabled={
                  loading ||
                  !input.trim()
                }
              >
                {loading ? (
                  <>
                    <span className="chat-send-spinner" />
                    Sending
                  </>
                ) : (
                  <>
                    Send
                    <span>→</span>
                  </>
                )}
              </button>

            </div>

          </form>


          <div className="chat-disclaimer">
            AI Career Assistant can make mistakes.
            Use its recommendations as guidance and
            verify important career information.
          </div>

        </div>

      </section>

    </div>
  );
}

export default Chat;