"""Data Widgets Mixin for Violit"""

from typing import Union, Callable, Optional, Any
import json
import pandas as pd
from ..component import Component
from ..context import rendering_ctx
from ..state import State
from ..style_utils import build_cls


class DataWidgetsMixin:
    """Data display widgets (dataframe, table, data_editor, metric, json)"""
    
    def dataframe(self, df: Union[pd.DataFrame, Callable, State], height=400, 
                  column_defs=None, grid_options=None, on_cell_clicked=None, cls: str = "", **props):
        """Display interactive dataframe with AG Grid"""
        cid = self._get_next_cid("df")
        
        def action(v):
            if on_cell_clicked and callable(on_cell_clicked):
                on_cell_clicked(v)
        
        def builder():
            current_df = df
            if isinstance(df, State):
                token = rendering_ctx.set(cid)
                current_df = df.value
                rendering_ctx.reset(token)
            elif callable(df):
                token = rendering_ctx.set(cid)
                current_df = df()
                rendering_ctx.reset(token)
                
            if not isinstance(current_df, pd.DataFrame):
                try: current_df = pd.DataFrame(current_df)
                except: return Component("div", id=cid, content="Invalid data format")

            data = current_df.to_dict('records')
            
            if column_defs:
                cols = column_defs
            else:
                cols = [{"field": c, "sortable": True, "filter": True} for c in current_df.columns]
            
            extra_options = grid_options or {}
            
            cell_click_handler = ""
            if on_cell_clicked:
                cell_click_handler = f'''
                onCellClicked: (params) => {{
                    const cellData = {{
                        value: params.value,
                        field: params.colDef.field,
                        rowData: params.data,
                        rowIndex: params.rowIndex
                    }};
                    {f"window.sendAction('{cid}', cellData);" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: JSON.stringify(cellData)}}, swap: 'none'}});"}
                }},
                '''
            
            final_cls = build_cls(f"ag-theme-alpine-dark w:full {cls}", **props)
            
            html = f'''
            <div id="{cid}" style="height: {height}px;" class="{final_cls}"></div>
            <script>(function(){{
                const opt = {{ 
                    columnDefs: {json.dumps(cols, default=str)}, 
                    rowData: {json.dumps(data, default=str)},
                    defaultColDef: {{flex: 1, minWidth: 100, resizable: true}},
                    {cell_click_handler}
                    ...{json.dumps(extra_options)}
                }};
                const el = document.querySelector('#{cid}');
                if (el && window.agGrid) {{ 
                    const grid = new agGrid.Grid(el, opt);
                    window['grid_{cid}'] = grid;
                }}
                else {{ console.error("agGrid not found"); }}
            }})();</script>
            '''
            return Component("div", id=f"{cid}_wrapper", content=html)
        
        self._register_component(cid, builder, action=action if on_cell_clicked else None)

    def table(self, df: Union[pd.DataFrame, Callable, State], 
              styled: bool = False, highlight_row: int = None, title: str = None, cls: str = "", **props):
        """Display static HTML table (Signal support)"""
        cid = self._get_next_cid("table")
        def builder():
            current_df = df
            if isinstance(df, State):
                token = rendering_ctx.set(cid)
                current_df = df.value
                rendering_ctx.reset(token)
            elif callable(df):
                token = rendering_ctx.set(cid)
                current_df = df()
                rendering_ctx.reset(token)
            
            if not isinstance(current_df, pd.DataFrame):
                try: current_df = pd.DataFrame(current_df)
                except: return Component("div", id=cid, content="Invalid data format")

            if styled:
                # Premium styled table
                headers_html = ''.join(
                    f'<th class="p:1rem text:center bb:2|solid|rgba(139,92,246,0.3)">{col}</th>' 
                    for col in current_df.columns
                )
                
                rows_html = []
                for i, (_, row) in enumerate(current_df.iterrows()):
                    is_highlight = highlight_row is not None and i == highlight_row
                    row_style = 'background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(217, 70, 239, 0.08));' if is_highlight else ''
                    
                    cells_html = []
                    for j, cell in enumerate(row):
                        cell_cls = 'p:1rem bb:1|solid|neutral-200'
                        if j == 0:
                            cell_cls += ' text:left'
                            if is_highlight:
                                cell_cls += ' fw:700 color:#A855F7'
                        else:
                            cell_cls += ' text:center'
                            if is_highlight:
                                cell_cls += ' fw:600'
                            if '✅' in str(cell):
                                cell_cls += ' color:#22c55e fw:600'
                        
                        cells_html.append(f'<td class="{cell_cls}">{cell}</td>')
                    
                    rows_html.append(f'<tr style="{row_style}">{"".join(cells_html)}</tr>')
                
                title_html = f'<div class="font:1.8rem fw:700 text:center mb:2rem color:neutral-900">{title}</div>' if title else ''
                
                final_cls = build_cls(f"bg:neutral-50 r:20 p:2.5rem my:1.5rem {cls}", **props)
                
                styled_html = f'''
                <div class="{final_cls}">
                    {title_html}
                    <table class="w:full border-collapse font-size:0.95rem">
                        <thead>
                            <tr style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(217, 70, 239, 0.1));">
                                {headers_html}
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(rows_html)}
                        </tbody>
                    </table>
                </div>
                '''
                return Component("div", id=cid, content=styled_html)
            else:
                # Default table
                html_table = current_df.to_html(index=False, border=0, classes=['data-table'])
                
                final_cls = build_cls(f"overflow-x:auto b:1|solid|border r:0.5rem {cls}", **props)
                
                styled_html = f'''
                <div class="{final_cls}">
                    <style>
                        .data-table {{ width: 100%; border-collapse: collapse; background: var(--sl-bg-card); color: var(--sl-text); }}
                        .data-table thead {{ background: var(--sl-primary); color: white; }}
                        .data-table th, .data-table td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--sl-border); }}
                        .data-table tbody tr:hover {{ background: color-mix(in srgb, var(--sl-bg-card), var(--sl-primary) 5%); }}
                    </style>
                    {html_table}
                </div>
                '''
                return Component("div", id=cid, content=styled_html)
        self._register_component(cid, builder)

    def data_editor(self, df: pd.DataFrame, num_rows="fixed", height=400, key=None, on_change=None, cls: str = "", **props):
        """Interactive data editor"""
        cid = self._get_next_cid("data_editor")
        
        state_key = key or f"data_editor:{cid}"
        s = self.state(df.to_dict('records'), key=state_key)
        
        def action(v):
            try:
                new_data = json.loads(v) if isinstance(v, str) else v
                s.set(new_data)
                if on_change: on_change(pd.DataFrame(new_data))
            except: pass
        
        def builder():
            token = rendering_ctx.set(cid)
            data = s.value
            rendering_ctx.reset(token)
            
            cols = [{"field": c, "sortable": True, "filter": True, "editable": True} for c in df.columns]
            add_row_btn = '' if num_rows == "fixed" else f'''
            <sl-button size="small" class="mt:0.5rem" onclick="addDataRow_{cid}()">
                <sl-icon slot="prefix" name="plus-circle"></sl-icon>
                Add Row
            </sl-button>
            '''
            
            final_cls = build_cls(f"ag-theme-alpine-dark w:full {cls}", **props)
            
            html = f'''
            <div>
                <div id="{cid}" style="height: {height}px;" class="{final_cls}"></div>
                {add_row_btn}
            </div>
            <script>(function(){{
                const gridOptions = {{
                    columnDefs: {json.dumps(cols, default=str)},
                    rowData: {json.dumps(data, default=str)},
                    defaultColDef: {{ flex: 1, minWidth: 100, resizable: true, editable: true }},
                    onCellValueChanged: (params) => {{
                        const allData = [];
                        params.api.forEachNode(node => allData.push(node.data));
                        {f"sendAction('{cid}', allData);" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: JSON.stringify(allData)}} , swap: 'none'}});"}
                    }},
                    onGridReady: (params) => {{
                        window['gridApi_{cid}'] = params.api;
                    }}
                }};
                const el = document.querySelector('#{cid}');
                if (el && window.agGrid) {{
                    new agGrid.Grid(el, gridOptions);
                }}
                
                window.addDataRow_{cid} = function() {{
                    const api = window['gridApi_{cid}'];
                    if (api && api.applyTransaction) {{
                        const newRow = {{}};
                        {json.dumps([c for c in df.columns])}.forEach(col => newRow[col] = '');
                        api.applyTransaction({{add: [newRow]}});
                        const allData = [];
                        api.forEachNode(node => allData.push(node.data));
                        {f"sendAction('{cid}', allData);" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: JSON.stringify(allData)}} , swap: 'none'}});"}
                    }}
                }};
            }})();</script>
            '''
            return Component("div", id=f"{cid}_wrapper", content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def metric(self, label: str, value: Union[str, int, float, State, Callable], 
               delta: Optional[Union[str, State, Callable]] = None, delta_color: str = "normal",
               icon: str = None, border_color: str = None, help_text: str = None, cls: str = "", **props):
        """Display metric value with Signal support"""
        import html as html_lib
        
        cid = self._get_next_cid("metric")
        
        def builder():
            curr_val = value
            if isinstance(value, State):
                token = rendering_ctx.set(cid)
                curr_val = value.value
                rendering_ctx.reset(token)
            elif callable(value):
                token = rendering_ctx.set(cid)
                curr_val = value()
                rendering_ctx.reset(token)
                
            curr_delta = delta
            if isinstance(delta, State):
                token = rendering_ctx.set(cid)
                curr_delta = delta.value
                rendering_ctx.reset(token)
            elif callable(delta):
                token = rendering_ctx.set(cid)
                curr_delta = delta()
                rendering_ctx.reset(token)

            escaped_label = html_lib.escape(str(label))
            escaped_val = html_lib.escape(str(curr_val))

            delta_html = ""
            if curr_delta:
                escaped_delta = html_lib.escape(str(curr_delta))
                color_map = {"positive": "#10b981", "negative": "#ef4444", "normal": "var(--sl-text-muted)"}
                color = color_map.get(delta_color, "var(--sl-text-muted)")
                delta_icon = "arrow-up" if delta_color == "positive" else "arrow-down" if delta_color == "negative" else ""
                icon_html = f'<sl-icon name="{delta_icon}" class="font-size:0.8em mr:2px"></sl-icon>' if delta_icon else ""
                delta_html = f'<div style="color: {color};" class="font-size:0.9rem mt:0.25rem fw:500">{icon_html}{escaped_delta}</div>'
            
            metric_icon = ""
            if icon:
                metric_icon = f'<sl-icon name="{icon}" class="font-size:1.5rem color:primary mr:0.75rem"></sl-icon>'
            
            border_style = ""
            if border_color:
                border_style = f"border-left: 4px solid {border_color}; padding-left: 1.25rem;"
            
            help_html = ""
            if help_text:
                help_html = f'<div class="font-size:0.75rem color:neutral-500 mt:0.5rem">{html_lib.escape(help_text)}</div>'
            
            final_cls = build_cls(f"card p:1.25rem {cls}", **props)
            
            html_output = f'''
            <div class="{final_cls}" style="{border_style}">
                <div class="flex ai:start">
                    {metric_icon}
                    <div class="flex:1">
                        <div class="font-size:0.875rem color:text-muted mb:0.5rem fw:500">{escaped_label}</div>
                        <div class="font-size:1.75rem fw:700 color:text">{escaped_val}</div>
                        {delta_html}
                        {help_html}
                    </div>
                </div>
            </div>
            '''
            return Component("div", id=cid, content=html_output)
            
        self._register_component(cid, builder)

    def json(self, body: Any, expanded=True, cls: str = "", **props):
        """Display JSON data"""
        cid = self._get_next_cid("json")
        json_str = json.dumps(body, indent=2, default=str)
        
        final_cls = build_cls(f"bg:bg-card b:1|solid|border r:0.5rem p:0.5rem {cls}", **props)
        
        html = f'''
        <details {"open" if expanded else ""} class="{final_cls}">
            <summary class="cursor:pointer font-size:0.875rem color:text-muted">JSON Data</summary>
            <pre class="m:0.5rem|0|0|0 font-size:0.875rem color:primary">{json_str}</pre>
        </details>
        '''
        return Component("div", id=cid, content=html)

    def heatmap(self, data: Union[dict, State, Callable], 
                start_date=None, end_date=None,
                color_map=None, show_legend=True, 
                show_weekdays=True, show_months=True,
                cell_size=12, gap=3, on_cell_clicked=None, cls: str = "", **props):
        """Display GitHub-style activity heatmap"""
        from datetime import date as date_obj, timedelta
        
        cid = self._get_next_cid("heatmap")
        
        def action(v):
            if on_cell_clicked and callable(on_cell_clicked):
                on_cell_clicked(v)
        
        def builder():
            current_data = data
            if isinstance(data, State):
                token = rendering_ctx.set(cid)
                current_data = data.value
                rendering_ctx.reset(token)
            elif callable(data):
                token = rendering_ctx.set(cid)
                current_data = data()
                rendering_ctx.reset(token)
            
            if start_date:
                if isinstance(start_date, str):
                    start = date_obj.fromisoformat(start_date)
                else:
                    start = start_date
            else:
                start = date_obj.today().replace(month=1, day=1)
            
            if end_date:
                if isinstance(end_date, str):
                    end = date_obj.fromisoformat(end_date)
                else:
                    end = end_date
            else:
                end = date_obj.today().replace(month=12, day=31)
            
            current_color_map = color_map if color_map is not None else {
                0: '#ebedf0',
                1: '#10b981',
                2: '#fbbf24'
            }
            
            start_day = start - timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)
            
            weeks = []
            current = start_day
            
            while current <= end:
                week = []
                for _ in range(7):
                    if start <= current <= end:
                        date_str = current.isoformat()
                        value = current_data.get(date_str, 0)
                        week.append({'date': current, 'value': value, 'valid': True})
                    else:
                        week.append({'date': current, 'value': 0, 'valid': False})
                    current += timedelta(days=1)
                weeks.append(week)
            
            # Use Master CSS for layout where possible, but grid calculations are specific
            final_cls = build_cls(f"bg:white p:1.5rem r:8 overflow-x:auto {cls}", **props)
            
            css = f'''
            <style>
            .heatmap-{cid} .grid {{ display: flex; gap: {gap}px; }}
            .heatmap-{cid} .weekdays {{ display: flex; flex-direction: column; gap: {gap}px; padding-top: 20px; margin-right: 4px; }}
            .heatmap-{cid} .day-label {{ height: {cell_size}px; font-size: 9px; color: #666; display: flex; align-items: center; }}
            .heatmap-{cid} .week {{ display: flex; flex-direction: column; gap: {gap}px; }}
            .heatmap-{cid} .month {{ height: 14px; font-size: 9px; color: #666; text-align: center; margin-bottom: 2px; }}
            .heatmap-{cid} .cell {{ width: {cell_size}px; height: {cell_size}px; border-radius: 2px; border: 1px solid #fff; cursor: pointer; }}
            .heatmap-{cid} .cell:hover {{ opacity: 0.8; border: 1px solid #000; }}
            .heatmap-{cid} .cell.today {{ border: 2px solid #000; }}
            .heatmap-{cid} .legend {{ margin-top: 1rem; display: flex; gap: 1rem; font-size: 11px; color: #666; align-items: center; }}
            .heatmap-{cid} .legend-item {{ display: flex; align-items: center; gap: 4px; }}
            </style>
            '''
            
            weekday_html = ''
            if show_weekdays:
                weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                weekday_html = f'''
                <div class="weekdays">
                    {"".join(f'<div class="day-label">{d}</div>' for d in weekdays)}
                </div>
                '''
            
            today = date_obj.today()
            current_month = None
            weeks_html = []
            
            for week in weeks:
                first_valid = next((d for d in week if d['valid']), None)
                if first_valid and show_months:
                    month = first_valid['date'].month
                    month_label = f"{month}" if month != current_month else ""
                    current_month = month
                else:
                    month_label = ""
                
                cells_html = []
                for day in week:
                    if not day['valid']:
                        cells_html.append(f'<div style="width: {cell_size}px; height: {cell_size}px;"></div>')
                    else:
                        value = day['value']
                        bg_color = current_color_map.get(value, '#ebedf0')
                        is_today = day['date'] == today
                        today_class = ' today' if is_today else ''
                        date_str = day['date'].isoformat()
                        
                        click_attr = ''
                        if on_cell_clicked:
                            click_js = f"window.sendAction('{cid}', {{date: '{date_str}', value: {value}}});" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: JSON.stringify({{date: '{date_str}', value: {value}}})}}), swap: 'none'}});"
                            click_attr = f'onclick="{click_js}"'
                        
                        cells_html.append(
                            f'<div class="cell{today_class}" style="background: {bg_color};" title="{date_str}" {click_attr}></div>'
                        )
                
                weeks_html.append(f'''
                <div class="week">
                    <div class="month">{month_label}</div>
                    {"".join(cells_html)}
                </div>
                ''')
            
            legend_html = ''
            if show_legend:
                legend_items = [
                    f'''<div class="legend-item">
                        <div class="cell" style="background: {color}; border: 1px solid #ddd;"></div>
                        <span>{label}</span>
                    </div>'''
                    for label, color in [('None', current_color_map.get(0, '#ebedf0')), 
                                         ('Done', current_color_map.get(1, '#10b981')), 
                                         ('Skip', current_color_map.get(2, '#fbbf24'))]
                    if color in current_color_map.values()
                ]
                legend_html = f'''
                <div class="legend">
                    <span>Legend:</span>
                    {"".join(legend_items)}
                </div>
                '''
            
            html = f'''
            {css}
            <div class="heatmap-{cid} {final_cls}">
                <div class="grid">
                    {weekday_html}
                    <div class="flex gap:{gap}px">
                        {"".join(weeks_html)}
                    </div>
                </div>
                {legend_html}
            </div>
            '''
            
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder, action=action if on_cell_clicked else None)
