import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { API_BASE_URL, getApiHeaders } from '../config/apiConfig';
import { useLanguage } from '../i18n/LanguageContext';
import './Chatbot.css';

function Chatbot() {
  const { language, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [isOpen, messages]);

  const toggleChatbot = () => {
    setIsOpen((prev) => !prev);
  };

  const clearChat = () => {
    setMessages([]);
  };

  const formatTimestamp = () => {
    const now = new Date();
    return now.toTimeString().split(' ')[0];
  };

  const sendMessage = async (textToSend) => {
    const questionText = (textToSend || userInput).trim();
    if (!questionText || isLoading) return;

    if (questionText.length > 1000) {
      const errorMsg = {
        sender: 'bot',
        text: t('chatbot.oversizedError'),
        timestamp: formatTimestamp(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    const userMessage = {
      sender: 'user',
      text: questionText,
      timestamp: formatTimestamp(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/chatbot`,
        { question: questionText, locale: language },
        { headers: getApiHeaders() }
      );

      const botMessage = {
        sender: 'bot',
        text: response.data.answer || (language === 'en' ? 'No response received from system.' : 'Không nhận được phản hồi từ hệ thống.'),
        timestamp: formatTimestamp(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorDetail =
        error.response?.data?.error || t('chatbot.networkError');
      const botErrorMessage = {
        sender: 'bot',
        text: `⚠️ **${t('common.error')}:** ${errorDetail}`,
        timestamp: formatTimestamp(),
      };
      setMessages((prev) => [...prev, botErrorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedChips = t('chatbot.chips') || [];

  return (
    <div className="sdn-chatbot-container">
      {/* Floating launcher button */}
      <button
        className={`sdn-chatbot-launcher ${isOpen ? 'active' : ''}`}
        onClick={toggleChatbot}
        title={t('chatbot.headerTitle')}
        aria-label="Open SDNFlowGuard Operations Assistant"
      >
        <svg
          className="sdn-launcher-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="M9 12l2 2 4-4" />
        </svg>
        <span className="sdn-launcher-label">{t('chatbot.launcherLabel')}</span>
        <span className="sdn-launcher-status-dot" />
      </button>

      {/* Chatbot modal window */}
      {isOpen && (
        <div className="sdn-chatbot-window" role="dialog" aria-label="SDNFlowGuard Assistant">
          {/* Header */}
          <div className="sdn-chatbot-header">
            <div className="sdn-header-branding">
              <div className="sdn-header-icon-box">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
                  <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
                  <line x1="6" y1="6" x2="6.01" y2="6" />
                  <line x1="6" y1="18" x2="6.01" y2="18" />
                </svg>
              </div>
              <div className="sdn-header-text">
                <h4 className="sdn-header-title">{t('chatbot.headerTitle')}</h4>
                <div className="sdn-header-sub">{t('chatbot.headerSub')}</div>
              </div>
            </div>

            <div className="sdn-header-actions">
              <span className="sdn-header-badge" title="Assistant operates in read-only audit mode">
                <span className="sdn-badge-dot" />
                {t('chatbot.readOnlyBadge')}
              </span>
              <button
                className="sdn-header-btn"
                onClick={clearChat}
                title={t('chatbot.clearChat')}
                aria-label="Clear chat"
              >
                ↺
              </button>
              <button
                className="sdn-header-btn sdn-header-btn-close"
                onClick={toggleChatbot}
                title={t('chatbot.closeChat')}
                aria-label="Close assistant"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Quick chips bar */}
          <div className="sdn-chips-bar">
            {Array.isArray(suggestedChips) &&
              suggestedChips.map((item, idx) => (
                <button
                  key={idx}
                  className="sdn-chip"
                  onClick={() => sendMessage(item.query)}
                  disabled={isLoading}
                >
                  {item.label}
                </button>
              ))}
          </div>

          {/* Messages list */}
          <div className="sdn-messages-container">
            {messages.length === 0 ? (
              <div className="sdn-empty-state">
                <div className="sdn-empty-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
                    <path d="M12 12L2.5 7.5" />
                    <path d="M12 12v10" />
                  </svg>
                </div>
                <h5 className="sdn-empty-title">{t('chatbot.emptyTitle')}</h5>
                <p className="sdn-empty-desc">{t('chatbot.emptyDesc')}</p>
                <div className="sdn-empty-notice">
                  <span className="sdn-notice-pill">{t('chatbot.emptyNoticePill')}</span>
                  <span>{t('chatbot.emptyNoticeText')}</span>
                </div>
                <div className="sdn-empty-grid">
                  <button
                    className="sdn-empty-card"
                    onClick={() =>
                      sendMessage(
                        language === 'en'
                          ? 'What is the current status of the ONOS controller?'
                          : 'Trạng thái ONOS controller hiện tại thế nào?'
                      )
                    }
                  >
                    <div className="sdn-card-title">{t('chatbot.quickStarters.controllerTitle')}</div>
                    <div className="sdn-card-sub">{t('chatbot.quickStarters.controllerSub')}</div>
                  </button>
                  <button
                    className="sdn-empty-card"
                    onClick={() =>
                      sendMessage(
                        language === 'en'
                          ? 'Show SDN network topology including switches and hosts'
                          : 'Xem thông tin topo mạng SDN và các switch/host'
                      )
                    }
                  >
                    <div className="sdn-card-title">{t('chatbot.quickStarters.topologyTitle')}</div>
                    <div className="sdn-card-sub">{t('chatbot.quickStarters.topologySub')}</div>
                  </button>
                  <button
                    className="sdn-empty-card"
                    onClick={() =>
                      sendMessage(
                        language === 'en'
                          ? 'How many flow rules are active on the switch and how are they classified?'
                          : 'Hiện có bao nhiêu flow rule trên switch và phân loại thế nào?'
                      )
                    }
                  >
                    <div className="sdn-card-title">{t('chatbot.quickStarters.flowsTitle')}</div>
                    <div className="sdn-card-sub">{t('chatbot.quickStarters.flowsSub')}</div>
                  </button>
                  <button
                    className="sdn-empty-card"
                    onClick={() =>
                      sendMessage(
                        language === 'en'
                          ? 'What is the current defense mode and how does the Safety Gate operate?'
                          : 'Chế độ phòng vệ hiện tại là gì và Safety Gate hoạt động ra sao?'
                      )
                    }
                  >
                    <div className="sdn-card-title">{t('chatbot.quickStarters.safetyTitle')}</div>
                    <div className="sdn-card-sub">{t('chatbot.quickStarters.safetySub')}</div>
                  </button>
                </div>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`sdn-message-row ${msg.sender}`}>
                  <div className="sdn-message-bubble">
                    <div className="sdn-message-meta">
                      <span className="sdn-meta-author">
                        {msg.sender === 'user'
                          ? t('chatbot.operatorLabel')
                          : t('chatbot.assistantLabel')}
                      </span>
                      <span className="sdn-meta-time">{msg.timestamp}</span>
                    </div>
                    <div className="sdn-message-body">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="sdn-message-row bot">
                <div className="sdn-message-bubble sdn-loading-bubble">
                  <div className="sdn-loading-indicator">
                    <span className="sdn-pulse-dot" />
                    <span className="sdn-pulse-dot" />
                    <span className="sdn-pulse-dot" />
                    <span className="sdn-loading-text">{t('chatbot.loadingText')}</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input bar */}
          <div className="sdn-chatbot-input-bar">
            <div className="sdn-input-wrapper">
              <textarea
                ref={textareaRef}
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t('chatbot.inputPlaceholder')}
                maxLength={1000}
                rows={2}
                disabled={isLoading}
              />
              <div className="sdn-input-footer">
                <span className={`sdn-char-count ${userInput.length > 900 ? 'warning' : ''}`}>
                  {userInput.length} / 1000
                </span>
                <button
                  className="sdn-send-btn"
                  onClick={() => sendMessage()}
                  disabled={!userInput.trim() || isLoading}
                  title={t('chatbot.btnSend')}
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  <span>{t('chatbot.btnSend')}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;
