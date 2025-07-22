import React, { useState } from 'react';
import styled from 'styled-components';
import VoucherSummary from './components/VoucherSummary';
import ChatInterface from './components/ChatInterface';
import VectorSearch from './components/VectorSearch';
import FeedbackWidget from './components/FeedbackWidget';
import { FiCpu, FiMessageSquare, FiGift, FiZap } from 'react-icons/fi';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
`;

const Subtitle = styled.p`
  font-size: 16px;
  color: #666;
  margin: 0;
`;

const MainContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`;

const Section = styled.div`
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  color: #333;
  font-weight: 600;
  font-size: 18px;
`;

const VoucherSelector = styled.div`
  margin-bottom: 24px;
  text-align: center;
`;

const VoucherSelect = styled.select`
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  min-width: 250px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }
`;

const StatusIndicator = styled.div<{ status: 'connected' | 'disconnected' | 'loading' }>`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  
  ${props => {
    switch (props.status) {
      case 'connected':
        return `
          background: #e8f5e8;
          color: #2e7d32;
        `;
      case 'disconnected':
        return `
          background: #ffebee;
          color: #c62828;
        `;
      case 'loading':
        return `
          background: #fff3e0;
          color: #f57c00;
        `;
      default:
        return '';
    }
  }}
`;

const StatusDot = styled.div<{ status: 'connected' | 'disconnected' | 'loading' }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  ${props => {
    switch (props.status) {
      case 'connected':
        return 'background: #4caf50;';
      case 'disconnected':
        return 'background: #f44336;';
      case 'loading':
        return 'background: #ff9800;';
      default:
        return '';
    }
  }}
`;

// Mock voucher data for demo
const DEMO_VOUCHERS = [
  { id: 'voucher_runam_200k', name: 'Giảm VND 200,000 - RuNam', merchant: 'Runam' },
  { id: 'voucher_runam_100k', name: 'Giảm VND 100,000 - RuNam', merchant: 'Runam' },
  { id: 'voucher_gocheap_12percent', name: 'Giảm 12% Thuê tài xế - GOCheap', merchant: 'GOCheap' },
  { id: 'voucher_citysight_200k', name: 'Tour xe buýt 2 tầng - City Sightseeing', merchant: 'City Sightseeing' },
  { id: 'voucher_spa_50k', name: 'Voucher 50,000đ - Spa 100% Thảo Mộc', merchant: 'Spa 100% Thảo Mộc' }
];

function App() {
  const [selectedVoucher, setSelectedVoucher] = useState(DEMO_VOUCHERS[0].id);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'loading'>('loading');

  React.useEffect(() => {
    // Check API status on component mount
    const checkApiStatus = async () => {
      try {
        const response = await fetch('/health');
        if (response.ok) {
          setApiStatus('connected');
        } else {
          setApiStatus('disconnected');
        }
      } catch (error) {
        setApiStatus('disconnected');
      }
    };

    checkApiStatus();
  }, []);

  const selectedVoucherData = DEMO_VOUCHERS.find(v => v.id === selectedVoucher);

  return (
    <AppContainer>
      <Header>
        <Title>
          <FiCpu />
            AI Voucher Assistant
        </Title>
        <Subtitle>
          Trợ lý AI thông minh giúp bạn hiểu rõ điều khoản voucher
        </Subtitle>
        <div style={{ marginTop: '12px' }}>
          <StatusIndicator status={apiStatus}>
            <StatusDot status={apiStatus} />
            {apiStatus === 'connected' && 'API Sẵn sàng'}
            {apiStatus === 'disconnected' && 'API Ngắt kết nối'}
            {apiStatus === 'loading' && 'Đang kết nối...'}
          </StatusIndicator>
        </div>
      </Header>

      <VoucherSelector>
        <VoucherSelect
          value={selectedVoucher}
          onChange={(e) => setSelectedVoucher(e.target.value)}
        >
          <option value="">Chọn voucher để thử nghiệm</option>
          {DEMO_VOUCHERS.map(voucher => (
            <option key={voucher.id} value={voucher.id}>
              {voucher.name} - {voucher.merchant}
            </option>
          ))}
        </VoucherSelect>
      </VoucherSelector>

      {selectedVoucher && (
        <>
          <MainContent>
            <Section>
              <SectionHeader>
                <FiGift />
                Tóm tắt thông minh
              </SectionHeader>
              <VoucherSummary voucherId={selectedVoucher} />
            </Section>

            <Section>
              <SectionHeader>
                <FiMessageSquare />
                Hỏi đáp trực tiếp
              </SectionHeader>
              <ChatInterface 
                voucherId={selectedVoucher} 
                voucherName={selectedVoucherData?.name}
              />
            </Section>
          </MainContent>
          
          {/* Vector Search Section */}
          <div style={{ maxWidth: '1200px', margin: '24px auto 0 auto' }}>
            <Section>
              <SectionHeader>
                <FiZap />
                Tìm kiếm Vector AI
              </SectionHeader>
              <VectorSearch />
            </Section>
          </div>
          
          {/* Feedback Widget */}
          <div style={{ maxWidth: '1200px', margin: '24px auto 0 auto' }}>
            <FeedbackWidget voucherId={selectedVoucher} />
          </div>
        </>
      )}
    </AppContainer>
  );
}

export default App;
