"""Status Widgets Mixin for Violit"""

from typing import Union, Callable, Optional
from ..component import Component
from ..context import rendering_ctx
from ..state import get_session_store, State
from ..style_utils import build_cls


class StatusWidgetsMixin:
    """Status display widgets (success, info, warning, error, toast, progress, spinner, status, balloons, snow, exception)"""
    
    def success(self, content, cls: str = "", **props): 
        """Display success alert"""
        self.alert(content, "success", "check-circle", cls, **props)
    
    def warning(self, content, cls: str = "", **props): 
        """Display warning alert"""
        self.alert(content, "warning", "exclamation-triangle", cls, **props)
    
    def error(self, content, cls: str = "", **props): 
        """Display error alert"""
        self.alert(content, "danger", "x-circle", cls, **props)
    
    def info(self, content, cls: str = "", **props): 
        """Display info alert"""
        self.alert(content, "primary", "info-circle", cls, **props)
    
    def alert(self, content: Union[str, Callable, State], variant="primary", icon=None, cls: str = "", **props):
        """Display alert message
        
        Supports: State, ReactiveExpr, callable, or direct value
        """
        from ..state import ReactiveExpr
        import html as html_lib
        
        cid = self._get_next_cid("alert")
        def builder():
            # Signal handling
            val = content
            if isinstance(content, State):
                token = rendering_ctx.set(cid)
                val = content.value
                rendering_ctx.reset(token)
            elif isinstance(content, ReactiveExpr):
                token = rendering_ctx.set(cid)
                val = content()
                rendering_ctx.reset(token)
            elif callable(content):
                token = rendering_ctx.set(cid)
                val = content()
                rendering_ctx.reset(token)
            
            # XSS protection: escape content
            escaped_val = html_lib.escape(str(val))
            
            icon_html = f'<sl-icon slot="icon" name="{icon}"></sl-icon>' if icon else ""
            
            final_cls = build_cls(cls, **props)
            
            html_output = f'<sl-alert variant="{variant}" open class="{final_cls}">{icon_html}{escaped_val}</sl-alert>'
            return Component("div", id=cid, content=html_output)
        self._register_component(cid, builder)

    def toast(self, message: Union[str, Callable, State], icon="info-circle", variant="primary"):
        """Display toast notification
        
        Supports: State, ReactiveExpr, callable, or direct value
        """
        from ..state import ReactiveExpr
        import json
        
        if isinstance(message, (State, ReactiveExpr, Callable)) and callable(message) or isinstance(message, (State, ReactiveExpr)):
            # Special case: dynamic toast label isn't common but for consistency:
            cid = self._get_next_cid("toast_trigger")
            def builder():
                token = rendering_ctx.set(cid)
                if isinstance(message, State):
                    val = message.value
                elif isinstance(message, ReactiveExpr):
                    val = message()
                else:
                    val = message()
                rendering_ctx.reset(token)
                
                # XSS protection: safely escape with JSON.stringify
                safe_val = json.dumps(str(val))
                safe_variant = json.dumps(str(variant))
                safe_icon = json.dumps(str(icon))
                code = f"createToast({safe_val}, {safe_variant}, {safe_icon})"
                return Component("script", id=cid, content=code)
            self._register_component(cid, builder)
        else:
            # XSS protection: safely escape with JSON.stringify
            safe_message = json.dumps(str(message))
            safe_variant = json.dumps(str(variant))
            safe_icon = json.dumps(str(icon))
            code = f"createToast({safe_message}, {safe_variant}, {safe_icon})"
            self._enqueue_eval(code, toast_data={"message": str(message), "icon": str(icon), "variant": str(variant)})

    def balloons(self):
        """Display balloons animation"""
        code = "createBalloons()"
        self._enqueue_eval(code, effect="balloons")

    def snow(self):
        """Display snow animation"""
        code = "createSnow()"
        self._enqueue_eval(code, effect="snow")

    def exception(self, exception: Exception, cls: str = "", **props):
        """Display exception with traceback"""
        import traceback
        import html as html_lib
        
        cid = self._get_next_cid("exception")
        tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        def builder():
            # XSS protection: escape exception message and traceback
            escaped_name = html_lib.escape(type(exception).__name__)
            escaped_msg = html_lib.escape(str(exception))
            escaped_tb = html_lib.escape(tb)
            
            final_cls = build_cls(f"mb:1rem {cls}", **props)
            
            html_output = f'''
            <sl-alert variant="danger" open class="{final_cls}">
                <sl-icon slot="icon" name="exclamation-octagon"></sl-icon>
                <strong>{escaped_name}:</strong> {escaped_msg}
                <pre class="mt:0.5rem p:0.5rem bg:rgba(0,0,0,0.1) r:0.25rem overflow-x:auto font-size:0.85rem">{escaped_tb}</pre>
            </sl-alert>
            '''
            return Component("div", id=cid, content=html_output)
        self._register_component(cid, builder)

    def _enqueue_eval(self, code, **lite_data):
        """Internal helper to enqueue JS evaluation or store for lite mode"""
        if self.mode == 'ws':
            store = get_session_store()
            if 'eval_queue' not in store: store['eval_queue'] = []
            store['eval_queue'].append(code)
        else:
            store = get_session_store()
            if 'toasts' not in store: store['toasts'] = []
            if 'effects' not in store: store['effects'] = []
            
            if 'toast_data' in lite_data:
                store['toasts'].append(lite_data['toast_data'])
            if 'effect' in lite_data:
                store['effects'].append(lite_data['effect'])

    def progress(self, value=0, text=None, cls: str = "", **props):
        """Display progress bar
        
        Supports: State, ReactiveExpr, callable, or direct value
        """
        from ..state import ReactiveExpr
        import html as html_lib
        
        cid = self._get_next_cid("progress")
        
        def builder():
            # Handle Signal
            val_num = value
            if isinstance(value, State):
                token = rendering_ctx.set(cid)
                val_num = value.value
                rendering_ctx.reset(token)
            elif isinstance(value, ReactiveExpr):
                token = rendering_ctx.set(cid)
                val_num = value()
                rendering_ctx.reset(token)
            elif callable(value):
                token = rendering_ctx.set(cid)
                val_num = value()
                rendering_ctx.reset(token)
            
            progress_text = text or f"{val_num}%"
            # XSS protection: escape text
            escaped_text = html_lib.escape(str(progress_text))
            
            final_cls = build_cls(f"mb:0.5rem {cls}", **props)
            
            html_output = f'''
            <div class="{final_cls}">
                <div class="flex jc:space-between mb:0.25rem">
                    <span class="font-size:0.875rem color:text">{escaped_text}</span>
                    <span class="font-size:0.875rem color:text-muted">{val_num}%</span>
                </div>
                <sl-progress-bar value="{val_num}"></sl-progress-bar>
            </div>
            '''
            return Component("div", id=cid, content=html_output)
        self._register_component(cid, builder)

    def spinner(self, text="Loading...", cls: str = "", **props):
        """Display loading spinner"""
        import html as html_lib
        
        cid = self._get_next_cid("spinner")
        
        # XSS protection: escape text
        escaped_text = html_lib.escape(str(text))
        
        final_cls = build_cls(f"flex ai:center gap:0.5rem mb:1rem {cls}", **props)
        
        html_output = f'''
        <div class="{final_cls}">
            <sl-spinner class="font-size:1.5rem"></sl-spinner>
            <span class="color:text-muted font-size:0.875rem">{escaped_text}</span>
        </div>
        '''
        return Component("div", id=cid, content=html_output)
    
    def status(self, label: str, state: str = "running", expanded: bool = True, cls: str = "", **props):
        from ..context import fragment_ctx
        
        cid = self._get_next_cid("status")
        
        class StatusContext:
            def __init__(self, app, status_id, label, state, expanded, cls, props):
                self.app = app
                self.status_id = status_id
                self.label = label
                self.state = state
                self.expanded = expanded
                self.cls = cls
                self.props = props
                self.token = None
                
            def __enter__(self):
                # Register builder
                def builder():
                    store = get_session_store()
                    
                    # Collect nested content
                    htmls = []
                    # Check static
                    for cid_child, b in self.app.static_fragment_components.get(self.status_id, []):
                        htmls.append(b().render())
                    # Check session
                    for cid_child, b in store['fragment_components'].get(self.status_id, []):
                        htmls.append(b().render())
                    
                    inner_html = "".join(htmls)
                    
                    # Status icon and color based on state
                    if self.state == "running":
                        icon = '<sl-spinner style="font-size:1rem;"></sl-spinner>'
                        border_color = "var(--sl-primary)"
                    elif self.state == "complete":
                        icon = '<sl-icon name="check-circle-fill" style="color:#10b981;font-size:1rem;"></sl-icon>'
                        border_color = "#10b981"
                    elif self.state == "error":
                        icon = '<sl-icon name="x-circle-fill" style="color:#ef4444;font-size:1rem;"></sl-icon>'
                        border_color = "#ef4444"
                    else:
                        icon = '<sl-icon name="info-circle-fill" style="color:var(--sl-primary);font-size:1rem;"></sl-icon>'
                        border_color = "var(--sl-primary)"
                    
                    # XSS protection: escape label
                    import html as html_lib
                    escaped_label = html_lib.escape(str(self.label))
                    
                    final_cls = build_cls(f"mb:1rem {self.cls}", **self.props)
                    
                    # Build status container
                    html_output = f'''
                    <sl-details {"open" if self.expanded else ""} class="{final_cls}">
                        <div slot="summary" class="flex ai:center gap:0.5rem fw:600">
                            {icon}
                            <span>{escaped_label}</span>
                        </div>
                        <div style="padding:0.5rem 0 0 1.5rem;border-left:2px solid {border_color};margin-left:0.5rem;">
                            {inner_html}
                        </div>
                    </sl-details>
                    '''
                    return Component("div", id=self.status_id, content=html_output)
                
                self.app._register_component(self.status_id, builder)
                
                self.token = fragment_ctx.set(self.status_id)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.token:
                    fragment_ctx.reset(self.token)
            
            def __getattr__(self, name):
                return getattr(self.app, name)
                
        return StatusContext(self, cid, label, state, expanded, cls, props)
