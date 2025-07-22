import json
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from feedback_models import UserFeedback, FeedbackSummary, FeedbackType, Rating

class FeedbackCollector:
    """Collect and analyze user feedback"""
    
    def __init__(self, storage_path: str = "data/feedback.json"):
        self.storage_path = storage_path
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> List[Dict]:
        """Load feedback from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading feedback: {e}")
                return []
        return []
    
    def _save_feedback(self):
        """Save feedback to storage"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"Error saving feedback: {e}")
    
    def submit_feedback(self, feedback: UserFeedback) -> str:
        """Submit new feedback"""
        feedback_dict = feedback.dict()
        feedback_dict['id'] = f"fb_{len(self.feedback_data) + 1}_{int(datetime.now().timestamp())}"
        
        self.feedback_data.append(feedback_dict)
        self._save_feedback()
        
        return feedback_dict['id']
    
    def get_feedback_summary(self, days: int = 30) -> FeedbackSummary:
        """Get feedback summary for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent feedback
        recent_feedback = [
            fb for fb in self.feedback_data
            if datetime.fromisoformat(str(fb['timestamp'])) > cutoff_date
        ]
        
        if not recent_feedback:
            return FeedbackSummary(
                total_feedback=0,
                average_rating=0.0,
                rating_distribution={},
                feedback_by_type={},
                recent_comments=[],
                improvement_suggestions=[]
            )
        
        # Calculate metrics
        ratings = [fb['rating'] for fb in recent_feedback]
        rating_counts = Counter(ratings)
        
        feedback_by_type = defaultdict(list)
        for fb in recent_feedback:
            feedback_by_type[fb['feedback_type']].append(fb)
        
        # Get recent comments
        recent_comments = [
            fb['comment'] for fb in recent_feedback[-20:]  # Last 20 comments
            if fb.get('comment')
        ]
        
        # Generate improvement suggestions based on low ratings
        improvement_suggestions = self._generate_improvement_suggestions(recent_feedback)
        
        return FeedbackSummary(
            total_feedback=len(recent_feedback),
            average_rating=round(sum(ratings) / len(ratings), 2),
            rating_distribution={str(k): v for k, v in rating_counts.items()},
            feedback_by_type={k: len(v) for k, v in feedback_by_type.items()},
            recent_comments=recent_comments,
            improvement_suggestions=improvement_suggestions
        )
    
    def _generate_improvement_suggestions(self, feedback_data: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on feedback"""
        suggestions = []
        
        # Analyze low ratings by type
        low_rating_feedback = [fb for fb in feedback_data if fb['rating'] <= 2]
        
        if not low_rating_feedback:
            return suggestions
        
        # Group by feedback type
        issues_by_type = defaultdict(list)
        for fb in low_rating_feedback:
            issues_by_type[fb['feedback_type']].append(fb)
        
        # Generate specific suggestions
        if FeedbackType.SUMMARY_QUALITY in issues_by_type:
            suggestions.append("Cải thiện chất lượng tóm tắt voucher - nhiều người dùng không hài lòng với độ chính xác")
        
        if FeedbackType.ANSWER_ACCURACY in issues_by_type:
            suggestions.append("Nâng cao độ chính xác câu trả lời - cần training thêm dữ liệu hoặc fine-tune model")
        
        if FeedbackType.UI_EXPERIENCE in issues_by_type:
            suggestions.append("Tối ưu giao diện người dùng - có phản hồi tiêu cực về trải nghiệm UI")
        
        # Analyze comment patterns
        all_comments = [fb.get('comment', '') for fb in low_rating_feedback]
        common_issues = self._extract_common_issues(all_comments)
        suggestions.extend(common_issues)
        
        return suggestions
    
    def _extract_common_issues(self, comments: List[str]) -> List[str]:
        """Extract common issues from comments"""
        suggestions = []
        comment_text = ' '.join(comments).lower()
        
        # Common issue patterns
        if 'chậm' in comment_text or 'lâu' in comment_text:
            suggestions.append("Tối ưu tốc độ phản hồi - người dùng phàn nàn về hiệu suất chậm")
        
        if 'sai' in comment_text or 'không đúng' in comment_text:
            suggestions.append("Kiểm tra và cải thiện độ chính xác thông tin voucher")
        
        if 'khó hiểu' in comment_text or 'rối rắm' in comment_text:
            suggestions.append("Đơn giản hóa ngôn ngữ và cách trình bày thông tin")
        
        if 'thiếu' in comment_text:
            suggestions.append("Bổ sung thêm thông tin chi tiết cho voucher")
        
        return suggestions
    
    def get_voucher_feedback(self, voucher_id: str) -> List[Dict]:
        """Get feedback for specific voucher"""
        return [
            fb for fb in self.feedback_data
            if fb.get('voucher_id') == voucher_id
        ]
    
    def get_feedback_trends(self, days: int = 90) -> Dict[str, Any]:
        """Get feedback trends over time"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Group feedback by week
        weekly_data = defaultdict(lambda: {'count': 0, 'ratings': []})
        
        for fb in self.feedback_data:
            fb_date = datetime.fromisoformat(str(fb['timestamp']))
            if fb_date > cutoff_date:
                # Get week start date (Monday)
                week_start = fb_date - timedelta(days=fb_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                weekly_data[week_key]['count'] += 1
                weekly_data[week_key]['ratings'].append(fb['rating'])
        
        # Calculate weekly averages
        trends = {}
        for week, data in weekly_data.items():
            trends[week] = {
                'feedback_count': data['count'],
                'average_rating': round(sum(data['ratings']) / len(data['ratings']), 2) if data['ratings'] else 0
            }
        
        return trends
    
    def export_feedback_report(self, days: int = 30) -> str:
        """Export comprehensive feedback report"""
        summary = self.get_feedback_summary(days)
        trends = self.get_feedback_trends(days)
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'period_days': days,
            'summary': summary.dict(),
            'trends': trends,
            'top_issues': self._get_top_issues(days),
            'voucher_performance': self._get_voucher_performance(days)
        }
        
        filename = f"feedback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return filename
    
    def _get_top_issues(self, days: int) -> List[Dict]:
        """Get top issues from recent feedback"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_feedback = [
            fb for fb in self.feedback_data
            if datetime.fromisoformat(str(fb['timestamp'])) > cutoff_date
            and fb['rating'] <= 2
        ]
        
        # Group by voucher and issue
        issue_groups = defaultdict(list)
        for fb in recent_feedback:
            key = f"{fb.get('voucher_id', 'general')}_{fb['feedback_type']}"
            issue_groups[key].append(fb)
        
        # Sort by frequency
        top_issues = []
        for key, feedbacks in sorted(issue_groups.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            voucher_id, feedback_type = key.split('_', 1)
            top_issues.append({
                'voucher_id': voucher_id if voucher_id != 'general' else None,
                'issue_type': feedback_type,
                'frequency': len(feedbacks),
                'average_rating': round(sum(fb['rating'] for fb in feedbacks) / len(feedbacks), 2),
                'sample_comments': [fb.get('comment') for fb in feedbacks[:3] if fb.get('comment')]
            })
        
        return top_issues
    
    def _get_voucher_performance(self, days: int) -> Dict[str, Dict]:
        """Get performance metrics by voucher"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        voucher_feedback = defaultdict(list)
        for fb in self.feedback_data:
            if (datetime.fromisoformat(str(fb['timestamp'])) > cutoff_date 
                and fb.get('voucher_id')):
                voucher_feedback[fb['voucher_id']].append(fb)
        
        performance = {}
        for voucher_id, feedbacks in voucher_feedback.items():
            ratings = [fb['rating'] for fb in feedbacks]
            performance[voucher_id] = {
                'total_feedback': len(feedbacks),
                'average_rating': round(sum(ratings) / len(ratings), 2),
                'satisfaction_rate': round(len([r for r in ratings if r >= 4]) / len(ratings) * 100, 2)
            }
        
        return performance

# Global feedback collector instance
feedback_collector = FeedbackCollector()
