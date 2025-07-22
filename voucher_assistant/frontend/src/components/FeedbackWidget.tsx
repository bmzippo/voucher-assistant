import React, { useState } from 'react';
import styled from 'styled-components';
import { FiStar, FiThumbsUp, FiThumbsDown, FiMessageSquare, FiSend } from 'react-icons/fi';

const FeedbackContainer = styled.div`
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  margin-top: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const FeedbackHeader = styled.h3`
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RatingSection = styled.div`
  margin-bottom: 16px;
`;

const RatingLabel = styled.label`
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  display: block;
`;

const StarRating = styled.div`
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
`;

const Star = styled.button<{ filled: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
  color: ${props => props.filled ? '#ffd700' : '#ddd'};
  transition: color 0.2s ease;
  
  &:hover {
    color: #ffd700;
  }
`;

const FeedbackTypeSelector = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
`;

const TypeButton = styled.button<{ selected: boolean }>`
  padding: 8px 12px;
  border: 1px solid ${props => props.selected ? '#667eea' : '#ddd'};
  border-radius: 16px;
  background: ${props => props.selected ? '#667eea' : 'white'};
  color: ${props => props.selected ? 'white' : '#666'};
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: #667eea;
    color: ${props => props.selected ? 'white' : '#667eea'};
  }
`;

const CommentTextarea = styled.textarea`
  width: 100%;
  min-height: 80px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }
`;

const SubmitButton = styled.button<{ disabled: boolean }>`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.5 : 1};
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
`;

const SuccessMessage = styled.div`
  background: #e8f5e8;
  color: #2e7d32;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #4caf50;
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const QuickActions = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const QuickActionButton = styled.button<{ type: 'positive' | 'negative' }>`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid ${props => props.type === 'positive' ? '#4caf50' : '#f44336'};
  border-radius: 20px;
  background: white;
  color: ${props => props.type === 'positive' ? '#4caf50' : '#f44336'};
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.type === 'positive' ? '#4caf50' : '#f44336'};
    color: white;
  }
`;

interface FeedbackWidgetProps {
  voucherId?: string;
  onFeedbackSubmitted?: () => void;
}

const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ voucherId, onFeedbackSubmitted }) => {
  const [rating, setRating] = useState<number>(0);
  const [hoverRating, setHoverRating] = useState<number>(0);
  const [feedbackType, setFeedbackType] = useState<string>('general');
  const [comment, setComment] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [showDetailedForm, setShowDetailedForm] = useState<boolean>(false);

  const feedbackTypes = [
    { value: 'summary_quality', label: 'Chất lượng tóm tắt' },
    { value: 'answer_accuracy', label: 'Độ chính xác câu trả lời' },
    { value: 'ui_experience', label: 'Trải nghiệm giao diện' },
    { value: 'general', label: 'Tổng quan' }
  ];

  const handleQuickFeedback = async (type: 'positive' | 'negative') => {
    const quickRating = type === 'positive' ? 5 : 2;
    await submitFeedback(quickRating, 'general', '');
  };

  const submitFeedback = async (feedbackRating: number, type: string, commentText: string) => {
    setIsSubmitting(true);
    
    try {
      const feedbackData = {
        feedback_type: type,
        rating: feedbackRating,
        comment: commentText || null,
        voucher_id: voucherId || null,
        user_session_id: localStorage.getItem('session_id') || null,
        timestamp: new Date().toISOString()
      };

      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData)
      });

      if (response.ok) {
        setIsSubmitted(true);
        setTimeout(() => {
          setIsSubmitted(false);
          setShowDetailedForm(false);
          setRating(0);
          setComment('');
          setFeedbackType('general');
        }, 3000);
        
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted();
        }
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDetailedSubmit = async () => {
    if (rating === 0) return;
    await submitFeedback(rating, feedbackType, comment);
  };

  if (isSubmitted) {
    return (
      <FeedbackContainer>
        <SuccessMessage>
          <FiThumbsUp />
          Cảm ơn bạn đã góp ý! Phản hồi của bạn giúp chúng tôi cải thiện dịch vụ.
        </SuccessMessage>
      </FeedbackContainer>
    );
  }

  return (
    <FeedbackContainer>
      <FeedbackHeader>
        <FiMessageSquare />
        Đánh giá trải nghiệm
      </FeedbackHeader>

      {!showDetailedForm ? (
        <>
          <QuickActions>
            <QuickActionButton 
              type="positive" 
              onClick={() => handleQuickFeedback('positive')}
              disabled={isSubmitting}
            >
              <FiThumbsUp />
              Hài lòng
            </QuickActionButton>
            <QuickActionButton 
              type="negative" 
              onClick={() => handleQuickFeedback('negative')}
              disabled={isSubmitting}
            >
              <FiThumbsDown />
              Chưa hài lòng
            </QuickActionButton>
          </QuickActions>
          
          <button
            onClick={() => setShowDetailedForm(true)}
            style={{
              background: 'none',
              border: '1px solid #ddd',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              color: '#666'
            }}
          >
            Đánh giá chi tiết
          </button>
        </>
      ) : (
        <>
          <RatingSection>
            <RatingLabel>Đánh giá tổng quan:</RatingLabel>
            <StarRating>
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  filled={star <= (hoverRating || rating)}
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setHoverRating(star)}
                  onMouseLeave={() => setHoverRating(0)}
                >
                  <FiStar />
                </Star>
              ))}
            </StarRating>
          </RatingSection>

          <RatingSection>
            <RatingLabel>Loại phản hồi:</RatingLabel>
            <FeedbackTypeSelector>
              {feedbackTypes.map((type) => (
                <TypeButton
                  key={type.value}
                  selected={feedbackType === type.value}
                  onClick={() => setFeedbackType(type.value)}
                >
                  {type.label}
                </TypeButton>
              ))}
            </FeedbackTypeSelector>
          </RatingSection>

          <RatingSection>
            <RatingLabel>Nhận xét (tùy chọn):</RatingLabel>
            <CommentTextarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Chia sẻ trải nghiệm của bạn để chúng tôi có thể cải thiện..."
            />
          </RatingSection>

          <SubmitButton
            onClick={handleDetailedSubmit}
            disabled={rating === 0 || isSubmitting}
          >
            <FiSend />
            {isSubmitting ? 'Đang gửi...' : 'Gửi đánh giá'}
          </SubmitButton>
        </>
      )}
    </FeedbackContainer>
  );
};

export default FeedbackWidget;
