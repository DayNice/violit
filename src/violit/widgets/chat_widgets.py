from typing import Optional, Union, Callable
from ..component import Component
from ..context import fragment_ctx
from ..state import get_session_store
from ..style_utils import build_cls

class ChatWidgetsMixin:
    """Chat-related widgets"""
    
    def chat_message(self, name: str, avatar: Optional[str] = None, cls: str = "", **props):
        """
        Insert a chat message container.
        """
        cid = self._get_next_cid("chat_message")
        
        class ChatMessageContext:
            def __init__(self, app, message_id, name, avatar, cls, props):
                self.app = app
                self.message_id = message_id
                self.name = name
                self.avatar = avatar
                self.cls = cls
                self.props = props
                self.token = None
                
            def __enter__(self):
                def builder():
                    store = get_session_store()
                    
                    htmls = []
                    for cid_child, b in self.app.static_fragment_components.get(self.message_id, []):
                        htmls.append(b().render())
                    for cid_child, b in store['fragment_components'].get(self.message_id, []):
                        htmls.append(b().render())
                    
                    inner_html = "".join(htmls)
                    
                    bg_color = "transparent"
                    avatar_content = ""
                    
                    if self.avatar:
                        if self.avatar.startswith("http") or self.avatar.startswith("data:"):
                            avatar_content = f'<img src="{self.avatar}" style="width:32px;height:32px;border-radius:4px;object-fit:cover;">'
                        else:
                            avatar_content = f'<div style="width:32px;height:32px;border-radius:4px;background:#eee;display:flex;align-items:center;justify-content:center;font-size:20px;">{self.avatar}</div>'
                    else:
                        if self.name == "user":
                            avatar_content = f'<div style="width:32px;height:32px;border-radius:4px;background:#7C4DFF;color:white;display:flex;align-items:center;justify-content:center;"><sl-icon name="person-fill"></sl-icon></div>'
                            bg_color = "rgba(124, 77, 255, 0.05)"
                        elif self.name == "assistant":
                            avatar_content = f'<div style="width:32px;height:32px;border-radius:4px;background:#FF5252;color:white;display:flex;align-items:center;justify-content:center;"><sl-icon name="robot"></sl-icon></div>'
                            bg_color = "rgba(255, 82, 82, 0.05)"
                        else:
                            initial = self.name[0].upper() if self.name else "?"
                            avatar_content = f'<div style="width:32px;height:32px;border-radius:4px;background:#9CA3AF;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;">{initial}</div>'
                            bg_color = "rgba(0,0,0,0.02)"

                    # Use Master CSS for layout, but keep specific avatar/bg logic inline or map it
                    # We can pass bg_color via style attribute if needed, or map to Master CSS if it's a standard color
                    # For dynamic bg colors based on role, inline style is safer/easier here.
                    
                    final_cls = build_cls(f"flex gap:16px mb:16px p:16px r:8 {self.cls}", **self.props)
                    
                    html = f'''
                    <div class="chat-message {final_cls}" style="background:{bg_color};">
                        <div class="chat-avatar flex-shrink:0">
                           {avatar_content}
                        </div>
                        <div class="chat-content flex:1 min-w:0 overflow-wrap:break-word">
                            {inner_html}
                        </div>
                    </div>
                    '''
                    return Component("div", id=self.message_id, content=html)
                
                self.app._register_component(self.message_id, builder)
                
                self.token = fragment_ctx.set(self.message_id)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.token:
                    fragment_ctx.reset(self.token)
            
            def __getattr__(self, name):
                return getattr(self.app, name)
                
        return ChatMessageContext(self, cid, name, avatar, cls, props)

    def chat_input(self, placeholder: str = "Your message", on_submit: Optional[Callable[[str], None]] = None, auto_scroll: bool = True, cls: str = "", **props):
        """
        Display a chat input widget at the bottom of the page.
        """
        cid = self._get_next_cid("chat_input")
        store = get_session_store()
        
        def handler(val):
            if on_submit:
                on_submit(val)
                
        self.static_actions[cid] = handler
            
        def builder():
            scroll_script = "window.scrollTo(0, document.body.scrollHeight);" if auto_scroll else ""
            
            final_cls = build_cls(cls, **props)
            
            # Using Master CSS for layout
            # Fixed positioning needs careful handling with Master CSS if we want to mix it
            # We keep the complex style logic but allow adding classes
            
            html = f'''
            <div class="chat-input-container {final_cls}" style="
                position: fixed; 
                bottom: 0; 
                left: 300px;
                right: 0;
                padding: 20px; 
                background: linear-gradient(to top, var(--sl-bg) 80%, transparent);
                z-index: 1000;
                display: flex;
                justify-content: center;
                pointer-events: none;
                transition: left 0.3s ease;
            ">
                <div style="
                    width: 100%; 
                    max-width: 800px; 
                    background: var(--sl-bg-card); 
                    border: 1px solid var(--sl-border); 
                    border-radius: 8px; 
                    padding: 8px; 
                    box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
                    display: flex;
                    gap: 8px;
                    pointer-events: auto;
                ">
                    <input type="text" id="input_{cid}" class="chat-input-box flex:1 b:none bg:transparent p:8px font-size:1rem color:text outline:none" placeholder="{placeholder}" 
                        onkeydown="if(event.key==='Enter'){{ 
                            window.chatInputWasActive = true;
                            {f"sendAction('{cid}', this.value);" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: this.value}}, swap: 'none'}});"}
                            this.value = ''; 
                        }}"
                    >
                    <sl-button size="small" variant="primary" circle onclick="
                        const el = document.getElementById('input_{cid}');
                        window.chatInputWasActive = true;
                        {f"sendAction('{cid}', el.value);" if self.mode == 'ws' else f"htmx.ajax('POST', '/action/{cid}', {{values: {{value: el.value}}, swap: 'none'}});"}
                        el.value = '';
                    ">
                        <sl-icon name="send" label="Send"></sl-icon>
                    </sl-button>
                </div>
            </div>
            <!-- Spacer -->
            <div style="height: 100px;"></div>
            <script>
                if ("{auto_scroll}" === "True") {{
                    setTimeout(() => {{ 
                        window.scrollTo({{
                            top: document.documentElement.scrollHeight,
                            behavior: 'smooth'
                        }});
                    }}, 100);
                }}

                if (window.chatInputWasActive) {{
                    setTimeout(() => {{
                        const el = document.querySelector('.chat-input-box');
                        if (el) {{
                            el.focus();
                        }}
                        window.chatInputWasActive = false;
                    }}, 150);
                }}
            </script>
            '''
            return Component("div", id=cid, content=html)
            
        self._register_component(cid, builder)
        
        val = store['actions'].get(cid)
        return val
