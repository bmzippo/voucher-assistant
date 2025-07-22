import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { ChatMessage, ChatResponse } from '../types';
import { voucherApi } from '../services/api';
import { FiSend, FiMessageCircle, FiUser, FiCpu } from 'react-icons/fi';

const ChatContainer = styled.div`
  background: white;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  height: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const MessageBubble = styled.div<{ isUser: boolean }>`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const MessageContent = styled.div<{ isUser: boolean }>`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  ${props => props.isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 4px;
  ` : `
    background: #f5f5f5;
    color: #333;
    border-bottom-left-radius: 4px;
  `}
`;

const MessageIcon = styled.div<{ isUser: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  ${props => props.isUser ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  ` : `
    background: #e0e0e0;
    color: #666;
  `}
  flex-shrink: 0;
`;

const ChatInput = styled.div`
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
`;

const InputContainer = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 24px;
  outline: none;
  font-size: 14px;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }
`;

const SendButton = styled.button<{ disabled: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.5 : 1};
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    transform: scale(1.05);
  }
`;

const ConfidenceIndicator = styled.div<{ confidence: number }>`
  margin-top: 4px;
  font-size: 11px;
  color: ${props => props.confidence > 0.7 ? '#4caf50' : props.confidence > 0.4 ? '#ff9800' : '#f44336'};
  opacity: 0.7;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  color: #666;
  font-size: 14px;
  padding: 20px;
  border-radius: 8px;
  background: #f9f9f9;
  margin-bottom: 16px;
`;

interface ChatInterfaceProps {
  voucherId: string;
  voucherName?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ voucherId, voucherName }) => {
  const [messages, setMessages] = useState<Array<{
    content: string;
    isUser: boolean;
    confidence?: number;
    timestamp: Date;
  }>>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');

    // Add user message
    setMessages(prev => [...prev, {
      content: userMessage,
      isUser: true,
      timestamp: new Date()
    }]);

    setIsLoading(true);

    try {
      const chatMessage: ChatMessage = {
        message: userMessage,
        timestamp: new Date().toISOString()
      };

      const response: ChatResponse = await voucherApi.chatWithVoucher(voucherId, chatMessage);

      // Add AI response
      setMessages(prev => [...prev, {
        content: response.response,
        isUser: false,
        confidence: response.confidence_score,
        timestamp: new Date(response.timestamp)
      }]);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      setMessages(prev => [...prev, {
        content: 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử lại sau hoặc liên hệ hotline 1900 558 865.',
        isUser: false,
        confidence: 0,
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        <FiMessageCircle />
        Hỏi đáp về voucher {voucherName ? `"${voucherName}"` : ''}
      </ChatHeader>

      <ChatMessages>
        {messages.length === 0 && (
          <WelcomeMessage>
            👋 Xin chào! Tôi có thể giúp bạn trả lời các câu hỏi về voucher này.
            <br />
            Hãy hỏi bất cứ điều gì bạn muốn biết!
          </WelcomeMessage>
        )}

        {messages.map((message, index) => (
          <MessageBubble key={index} isUser={message.isUser}>
            <MessageIcon isUser={message.isUser}>
              {message.isUser ? <FiUser /> : <FiCpu />}
            </MessageIcon>
            <div>
              <MessageContent isUser={message.isUser}>
                {message.content}
              </MessageContent>
              {!message.isUser && typeof message.confidence === 'number' && (
                <ConfidenceIndicator confidence={message.confidence}>
                  Độ tin cậy: {Math.round(message.confidence * 100)}%
                </ConfidenceIndicator>
              )}
            </div>
          </MessageBubble>
        ))}

        {isLoading && (
          <MessageBubble isUser={false}>
            <MessageIcon isUser={false}>
              <FiCpu />
            </MessageIcon>
            <MessageContent isUser={false}>
              Đang suy nghĩ...
            </MessageContent>
          </MessageBubble>
        )}

        <div ref={messagesEndRef} />
      </ChatMessages>

      <ChatInput>
        <InputContainer>
          <MessageInput
            type="text"
            placeholder="Hỏi về voucher này..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <SendButton 
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
          >
            <FiSend />
          </SendButton>
        </InputContainer>
      </ChatInput>
    </ChatContainer>
  );
};

export default ChatInterface;
