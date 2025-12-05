"""
Dashboard Page - Usage Statistics
View analytics and usage charts.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import APIClient, APIError
from utils.session import is_authenticated

# Page configuration
st.set_page_config(
    page_title="Toonify - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.stop()


def main():
    """Main page content."""
    st.title("📊 Dashboard")
    st.markdown("Your usage statistics and analytics")
    
    try:
        client = APIClient()
        
        # Get stats from listing jobs
        response = client.list_jobs(page=1, page_size=100)
        jobs = response.get("items", [])
        total = response.get("total", 0)
        
        # Calculate stats
        stats = calculate_stats(jobs, total)
        
        # Display metrics
        display_metrics(stats)
        
        st.markdown("---")
        
        # Charts
        display_charts(stats, jobs)
        
        st.markdown("---")
        
        # Recent activity
        display_recent_activity(jobs[:10])
    
    except APIError as e:
        st.error(f"❌ Error loading dashboard: {e.message}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")


def calculate_stats(jobs: list, total: int) -> dict:
    """Calculate statistics from jobs."""
    stats = {
        "total": total,
        "by_status": {},
        "by_style": {},
        "recent_jobs": []
    }
    
    for job in jobs:
        # Count by status
        status = job['status']
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Count by style
        style = job['style']
        stats["by_style"][style] = stats["by_style"].get(style, 0) + 1
    
    return stats


def display_metrics(stats: dict):
    """Display key metrics."""
    st.subheader("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Images",
            stats["total"],
            help="Total number of processed images"
        )
    
    with col2:
        completed = stats["by_status"].get("done", 0)
        success_rate = (completed / stats["total"] * 100) if stats["total"] > 0 else 0
        st.metric(
            "Completed",
            completed,
            f"{success_rate:.0f}% success",
            help="Successfully processed images"
        )
    
    with col3:
        processing = stats["by_status"].get("processing", 0) + stats["by_status"].get("queued", 0)
        st.metric(
            "In Progress",
            processing,
            help="Images currently processing"
        )
    
    with col4:
        failed = stats["by_status"].get("failed", 0)
        st.metric(
            "Failed",
            failed,
            help="Failed processing jobs"
        )


def display_charts(stats: dict, jobs: list):
    """Display charts and visualizations."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Images by Style")
        
        if stats["by_style"]:
            import plotly.express as px
            import pandas as pd
            
            style_data = pd.DataFrame([
                {"Style": k.replace("_", " ").title(), "Count": v}
                for k, v in stats["by_style"].items()
            ])
            
            fig = px.pie(
                style_data,
                values="Count",
                names="Style",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False, height=300)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")
    
    with col2:
        st.subheader("📊 Status Distribution")
        
        if stats["by_status"]:
            import plotly.express as px
            import pandas as pd
            
            status_colors = {
                "done": "#4CAF50",
                "processing": "#FFC107",
                "queued": "#9E9E9E",
                "failed": "#F44336"
            }
            
            status_data = pd.DataFrame([
                {"Status": k.title(), "Count": v, "Color": status_colors.get(k, "#666")}
                for k, v in stats["by_status"].items()
            ])
            
            fig = px.bar(
                status_data,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={k.title(): v for k, v in status_colors.items()}
            )
            fig.update_layout(showlegend=False, height=300)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet")
    
    # Activity over time
    st.subheader("📅 Activity Over Time")
    
    if jobs:
        import plotly.express as px
        import pandas as pd
        from collections import Counter
        from datetime import datetime
        
        # Extract dates
        dates = []
        for job in jobs:
            created = job.get('created_at', '')[:10]
            if created:
                dates.append(created)
        
        if dates:
            date_counts = Counter(dates)
            activity_data = pd.DataFrame([
                {"Date": k, "Count": v}
                for k, v in sorted(date_counts.items())
            ])
            
            fig = px.line(
                activity_data,
                x="Date",
                y="Count",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Images Processed",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available")
    else:
        st.info("No activity data yet")


def display_recent_activity(jobs: list):
    """Display recent activity table."""
    st.subheader("🕐 Recent Activity")
    
    if not jobs:
        st.info("No recent activity")
        return
    
    # Create table data
    table_data = []
    for job in jobs:
        status_emoji = {
            "done": "✅",
            "processing": "⏳",
            "queued": "📋",
            "failed": "❌"
        }.get(job['status'], "❓")
        
        table_data.append({
            "File": job['original_filename'][:30] + "..." if len(job['original_filename']) > 30 else job['original_filename'],
            "Style": job['style'].replace('_', ' ').title(),
            "Status": f"{status_emoji} {job['status'].title()}",
            "Date": job.get('created_at', '')[:19].replace('T', ' ')
        })
    
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    main()
