"""
core/analytics.py
-----------------
Simple analytics tracker for usage statistics and paper metrics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class UsageAnalytics:
    """Track system usage for research metrics and paper writing."""
    
    def __init__(self, log_file: str = "data/usage_analytics.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing analytics data."""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {
            "total_queries": 0,
            "agent_usage": {
                "scientist": 0,
                "analyst": 0,
                "reviewer": 0
            },
            "session_count": 0,
            "image_uploads": 0,
            "pdf_uploads": 0,
            "query_history": [],
            "response_times": [],
            "user_feedback": []
        }
    
    def _save_data(self):
        """Persist analytics data to disk."""
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_query(self, 
                  query: str, 
                  agent_used: str, 
                  session_id: str,
                  response_time: Optional[float] = None,
                  has_image: bool = False,
                  has_pdf: bool = False):
        """Log a query event."""
        self.data["total_queries"] += 1
        self.data["agent_usage"][agent_used] = self.data["agent_usage"].get(agent_used, 0) + 1
        
        if has_image:
            self.data["image_uploads"] += 1
        if has_pdf:
            self.data["pdf_uploads"] += 1
        
        if response_time:
            self.data["response_times"].append(response_time)
        
        # Store recent queries (limit to last 1000)
        self.data["query_history"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],  # Truncate for privacy
            "agent": agent_used,
            "session": session_id,
            "has_image": has_image,
            "has_pdf": has_pdf,
            "response_time": response_time
        })
        if len(self.data["query_history"]) > 1000:
            self.data["query_history"] = self.data["query_history"][-1000:]
        
        self._save_data()
    
    def log_feedback(self, session_id: str, rating: int, comment: str = ""):
        """Log user feedback (1-5 stars)."""
        self.data["user_feedback"].append({
            "timestamp": datetime.now().isoformat(),
            "session": session_id,
            "rating": rating,
            "comment": comment
        })
        self._save_data()
    
    def log_new_session(self):
        """Increment session counter."""
        self.data["session_count"] += 1
        self._save_data()
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for paper writing."""
        import statistics
        
        avg_response_time = statistics.mean(self.data["response_times"]) if self.data["response_times"] else 0
        
        avg_rating = 0
        if self.data["user_feedback"]:
            ratings = [f["rating"] for f in self.data["user_feedback"]]
            avg_rating = statistics.mean(ratings)
        
        return {
            "total_queries": self.data["total_queries"],
            "total_sessions": self.data["session_count"],
            "agent_distribution": self.data["agent_usage"],
            "image_uploads": self.data["image_uploads"],
            "pdf_uploads": self.data["pdf_uploads"],
            "avg_response_time_sec": round(avg_response_time, 2),
            "avg_user_rating": round(avg_rating, 2),
            "total_feedback_count": len(self.data["user_feedback"])
        }
    
    def export_for_paper(self, output_file: str = "paper_metrics.txt"):
        """Export formatted metrics for paper."""
        stats = self.get_summary_stats()
        
        report = f"""
=== AI Scientist System Usage Metrics ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Queries Processed: {stats['total_queries']}
Total User Sessions: {stats['total_sessions']}
Average Response Time: {stats['avg_response_time_sec']}s

Agent Usage Distribution:
  - AI Scientist Agent: {stats['agent_distribution'].get('scientist', 0)} ({stats['agent_distribution'].get('scientist', 0)/max(stats['total_queries'], 1)*100:.1f}%)
  - Image Analyst Agent: {stats['agent_distribution'].get('analyst', 0)} ({stats['agent_distribution'].get('analyst', 0)/max(stats['total_queries'], 1)*100:.1f}%)
  - Paper Reviewer Agent: {stats['agent_distribution'].get('reviewer', 0)} ({stats['agent_distribution'].get('reviewer', 0)/max(stats['total_queries'], 1)*100:.1f}%)

File Uploads:
  - Images Analyzed: {stats['image_uploads']}
  - Papers Reviewed: {stats['pdf_uploads']}

User Satisfaction:
  - Average Rating: {stats['avg_user_rating']}/5.0
  - Total Feedback: {stats['total_feedback_count']}
"""
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        return report


# Global analytics instance
ANALYTICS = UsageAnalytics()
