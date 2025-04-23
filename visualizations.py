import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

def create_mood_trend(mood_history):
    if not mood_history:
        return None

    df = pd.DataFrame(mood_history)
    df['created_at'] = pd.to_datetime(df['created_at'])

    fig = go.Figure()

    # Add mood score line
    fig.add_trace(go.Scatter(
        x=df['created_at'],
        y=df['mood_score'],
        mode='lines+markers',
        name='Mood Score',
        line=dict(color='#4A90E2', width=2),
        marker=dict(size=8, symbol='circle')
    ))

    # Add moving average
    df['moving_avg'] = df['mood_score'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=df['created_at'],
        y=df['moving_avg'],
        mode='lines',
        name='7-Day Average',
        line=dict(color='#FF9999', width=2, dash='dash')
    ))

    # Customize layout
    fig.update_layout(
        title='Your Mood Trend',
        xaxis_title='Date',
        yaxis_title='Mood Score',
        yaxis=dict(
            tickmode='array',
            ticktext=['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'],
            tickvals=[1, 2, 3, 4, 5],
            range=[0.5, 5.5]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    return fig

def create_mood_distribution(mood_history):
    if not mood_history:
        return None

    df = pd.DataFrame(mood_history)

    # Calculate mood distribution
    mood_counts = df['mood_score'].value_counts().sort_index()

    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'],
        values=mood_counts,
        hole=.3,
        marker_colors=['#FF9999', '#FFB366', '#FFFF99', '#99FF99', '#99CCFF']
    )])

    fig.update_layout(
        title='Mood Distribution',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_weekly_summary(mood_history):
    if not mood_history:
        return None

    df = pd.DataFrame(mood_history)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['week'] = df['created_at'].dt.strftime('%Y-%U')

    weekly_stats = df.groupby('week').agg({
        'mood_score': ['mean', 'min', 'max', 'count']
    }).reset_index()
    weekly_stats.columns = ['week', 'avg_mood', 'min_mood', 'max_mood', 'entries']

    fig = go.Figure()

    # Add range of moods
    fig.add_trace(go.Bar(
        name='Mood Range',
        x=weekly_stats['week'],
        y=weekly_stats['max_mood'] - weekly_stats['min_mood'],
        base=weekly_stats['min_mood'],
        marker_color='rgba(74, 144, 226, 0.3)',
        hovertemplate='Week: %{x}<br>Range: %{base} - %{y}<extra></extra>'
    ))

    # Add average line
    fig.add_trace(go.Scatter(
        name='Average Mood',
        x=weekly_stats['week'],
        y=weekly_stats['avg_mood'],
        mode='lines+markers',
        line=dict(color='#4A90E2', width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='Weekly Mood Summary',
        xaxis_title='Week',
        yaxis_title='Mood Score',
        yaxis=dict(
            tickmode='array',
            ticktext=['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'],
            tickvals=[1, 2, 3, 4, 5],
            range=[0.5, 5.5]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    return fig

def analyze_mood_patterns(mood_history):
    if not mood_history:
        return None

    df = pd.DataFrame(mood_history)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['day_of_week'] = df['created_at'].dt.day_name()
    df['hour'] = df['created_at'].dt.hour

    # Create heatmap data
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = df.pivot_table(
        values='mood_score',
        index='day_of_week',
        columns='hour',
        aggfunc='mean'
    ).reindex(day_order)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlBu',
        hoverongaps=False
    ))

    fig.update_layout(
        title='Mood Patterns by Day and Time',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

