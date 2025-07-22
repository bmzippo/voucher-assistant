import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { VoucherSummary } from '../types';
import { voucherApi } from '../services/api';
import { FiInfo, FiTag, FiClock, FiAlertCircle } from 'react-icons/fi';

const SummaryContainer = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const VoucherTitle = styled.h2`
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MerchantName = styled.p`
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 20px 0;
`;

const KeyPointsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const KeyPoint = styled.li`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const PointIcon = styled.div`
  color: #ffd700;
  margin-top: 2px;
  flex-shrink: 0;
`;

const PointText = styled.span`
  font-size: 14px;
  line-height: 1.5;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  color: #666;
`;

const ErrorContainer = styled.div`
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 16px;
  color: #c33;
  text-align: center;
`;

interface VoucherSummaryComponentProps {
  voucherId: string;
}

const VoucherSummaryComponent: React.FC<VoucherSummaryComponentProps> = ({ voucherId }) => {
  const [summary, setSummary] = useState<VoucherSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        const summaryData = await voucherApi.getVoucherSummary(voucherId);
        setSummary(summaryData);
      } catch (err) {
        setError('Không thể tải thông tin tóm tắt voucher. Vui lòng thử lại sau.');
        console.error('Error fetching voucher summary:', err);
      } finally {
        setLoading(false);
      }
    };

    if (voucherId) {
      fetchSummary();
    }
  }, [voucherId]);

  if (loading) {
    return (
      <LoadingContainer>
        <div>Đang tải thông tin voucher...</div>
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ErrorContainer>
        <FiAlertCircle style={{ marginRight: 8 }} />
        {error}
      </ErrorContainer>
    );
  }

  if (!summary) {
    return null;
  }

  const getIconForPoint = (point: string, index: number) => {
    if (point.includes('giảm') || point.includes('ưu đãi')) return <FiTag />;
    if (point.includes('thời hạn') || point.includes('hạn sử dụng')) return <FiClock />;
    return <FiInfo />;
  };

  return (
    <SummaryContainer>
      <VoucherTitle>
        <FiTag />
        {summary.name}
      </VoucherTitle>
      <MerchantName>Merchant: {summary.merchant}</MerchantName>
      
      <KeyPointsList>
        {summary.key_points.map((point, index) => (
          <KeyPoint key={index}>
            <PointIcon>
              {getIconForPoint(point, index)}
            </PointIcon>
            <PointText>{point}</PointText>
          </KeyPoint>
        ))}
      </KeyPointsList>
    </SummaryContainer>
  );
};

export default VoucherSummaryComponent;
