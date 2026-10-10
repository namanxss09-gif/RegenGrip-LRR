import plotly.graph_objects as go
RED, GREY = "#C8102E", "#6B7280"
def bar(names, vals, title, ylabel, base, evid, fmt="%{y:.4g}"):
    colors = [GREY if n == base else RED for n in names]
    f = go.Figure(go.Bar(x=names, y=vals, marker_color=colors, customdata=evid,
                         hovertemplate="%{x}<br>" + fmt + " " + ylabel + "<br>Evidence: %{customdata}<extra></extra>"))
    f.update_layout(title=f"{title} (grey = baseline)", yaxis_title=ylabel, template="plotly_white", height=340, margin=dict(t=50, b=30))
    return f
def delta_bar(names, vals, title, ylabel):
    f = go.Figure(go.Bar(x=names, y=vals, marker_color=[RED if (v or 0) < 0 else GREY for v in vals],
                         hovertemplate="%{x}<br>%{y:.3f} " + ylabel + "<br>Evidence: CALCULATION<extra></extra>"))
    f.add_hline(y=0, line_color="black"); f.update_layout(title=title, yaxis_title=ylabel, template="plotly_white", height=340, margin=dict(t=50, b=30))
    return f
