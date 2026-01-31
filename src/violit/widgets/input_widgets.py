"""Input widgets"""

from typing import Union, Callable, Optional, List, Any
import base64
import io
import json
from ..component import Component
from ..context import rendering_ctx, layout_ctx
from ..state import State
from ..style_utils import build_cls


class UploadedFile(io.BytesIO):
    def __init__(self, name, type, size, content_b64):
        self.name = name
        self.type = type
        self.size = size
        # content_b64 is like "data:text/csv;base64,AAAA..."
        if "," in content_b64:
             self.header, data = content_b64.split(",", 1)
        else:
             self.header = ""
             data = content_b64
        try:
            decoded = base64.b64decode(data)
        except:
            decoded = b""
        super().__init__(decoded)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<UploadedFile name='{self.name}' type='{self.type}' size={self.size}>"


class InputWidgetsMixin:
    
    def text_input(self, label, value="", key=None, on_change=None, cls: str = "", **props):
        """Single-line text input"""
        return self._input_component("input", "sl-input", label, value, on_change, key, cls=cls, **props)

    def slider(self, label, min_value=0, max_value=100, value=None, step=1, key=None, on_change=None, cls: str = "", **props):
        """Slider widget"""
        if value is None: value = min_value
        return self._input_component("slider", "sl-range", label, value, on_change, key, min=min_value, max=max_value, step=step, cls=cls, **props)

    def checkbox(self, label, value=False, key=None, on_change=None, cls: str = "", **props):
        """Checkbox widget"""
        cid = self._get_next_cid("checkbox")
        
        state_key = key or f"checkbox:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            real_val = str(v).lower() == 'true'
            s.set(real_val)
            if on_change: on_change(real_val)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            checked_attr = 'checked' if cv else ''
            
            # Separate semantic props from HTML attributes
            semantic_props = {}
            html_attrs = {}
            for k, v in props.items():
                if k in ['p', 'm', 'bg', 'color'] or k.startswith(('p:', 'm:', 'bg:', 'color:')): # Simple heuristic
                    semantic_props[k] = v
                else:
                    html_attrs[k] = v

            final_cls = build_cls(cls, **semantic_props)
            props_str = ' '.join(f'{k}="{v}"' for k, v in html_attrs.items() if v is not None and v is not False)
            
            if self.mode == 'lite':
                attrs_str = f'hx-post="/action/{cid}" hx-trigger="sl-change" hx-swap="none" hx-vals="js:{{value: event.target.checked}}"'
                listener_script = ""
            else:
                attrs_str = ""
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-change', function(e) {{
                            window.sendAction('{cid}', el.checked);
                        }});
                    }}
                }})();
                </script>
                '''
            
            html = f'<sl-checkbox id="{cid}" {checked_attr} {attrs_str} class="{final_cls}" {props_str}>{label}</sl-checkbox>{listener_script}'
            return Component(None, id=cid, content=html)
        self._register_component(cid, builder, action=action)
        return s

    def radio(self, label, options, index=0, key=None, on_change=None, cls: str = "", **props):
        """Radio button group"""
        cid = self._get_next_cid("radio_group")
        
        state_key = key or f"radio:{label}"
        default_val = options[index] if options else None
        s = self.state(default_val, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
            
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            opts_html = ""
            for opt in options:
                sel = 'checked' if opt == cv else ''
                opts_html += f'<sl-radio value="{opt}" {sel}>{opt}</sl-radio>'
            
            if self.mode == 'lite':
                attrs_str = f'hx-post="/action/{cid}" hx-trigger="sl-change" hx-swap="none" name="value"'
                listener_script = ""
            else:
                attrs_str = ""
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-change', function(e) {{
                            window.sendAction('{cid}', el.value);
                        }});
                    }}
                }})();
                </script>
                '''
            
            final_cls = build_cls(cls, **props)
            # Filter props for HTML attributes? For simplicity, assume props are mostly semantic/style in hybrid mode.
            # But radio-group might accept other props.
            # Let's just pass cls to class attribute.
            
            html = f'<sl-radio-group id="{cid}" label="{label}" value="{cv}" {attrs_str} class="{final_cls}">{opts_html}</sl-radio-group>{listener_script}'
            
            return Component(None, id=cid, content=html)
            
        self._register_component(cid, builder, action=action)
        return s

    def selectbox(self, label, options, index=0, key=None, on_change=None, cls: str = "", **props):
        """Single select dropdown"""
        cid = self._get_next_cid("select")
        
        state_key = key or f"select:{label}"
        default_val = options[index] if options else None
        s = self.state(default_val, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
            
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            opts_html = ""
            for opt in options:
                sel = 'selected' if opt == cv else ''
                opts_html += f'<sl-option value="{opt}" {sel}>{opt}</sl-option>'
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "sl-change", "hx-swap": "none", "name": "value"}
                listener_script = ""
            else:
                attrs = {}
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-change', function(e) {{
                            window.sendAction('{cid}', el.value);
                        }});
                    }}
                }})();
                </script>
                '''
            
            final_cls = build_cls(cls, **props)
            
            select_html = f'<sl-select id="{cid}" label="{label}" value="{cv}" class="{final_cls}"'
            for k, v in attrs.items():
                if v is True: select_html += f' {k}'
                elif v is not False and v is not None: select_html += f' {k}="{v}"'
            select_html += f'>{opts_html}</sl-select>{listener_script}'
            
            return Component(None, id=cid, content=select_html)
            
        self._register_component(cid, builder, action=action)
        return s

    def multiselect(self, label, options, default=None, key=None, on_change=None, cls: str = "", **props):
        """Multi-select dropdown"""
        cid = self._get_next_cid("multiselect")
        
        state_key = key or f"multiselect:{label}"
        default_val = default or []
        s = self.state(default_val, key=state_key)
        
        def action(v):
            if isinstance(v, str):
                selected = [x.strip() for x in v.split(',') if x.strip()]
            elif isinstance(v, list):
                selected = v
            else:
                selected = []
            s.set(selected)
            if on_change: on_change(selected)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            opts_html = ""
            for opt in options:
                sel = 'selected' if opt in cv else ''
                opts_html += f'<sl-option value="{opt}" {sel}>{opt}</sl-option>'
            
            attrs = {}
            if self.mode == 'ws':
                attrs = {"on_sl_change": f"window.sendAction('{cid}', this.value)"}

            final_cls = build_cls(cls, **props)
            return Component("sl-select", id=cid, label=label, content=opts_html, multiple=True, clearable=True, class_=final_cls, **attrs)
        
        self._register_component(cid, builder, action=action)
        
        if self.mode == 'lite':
            init_script_cid = f"{cid}_init"
            def script_builder():
                script = f'''
                <script>
                (function() {{
                    function initSelect() {{
                        const el = document.getElementById('{cid}');
                        if (!el) {{
                            setTimeout(initSelect, 50);
                            return;
                        }}
                        if (!el.hasAttribute('data-listener-added')) {{
                            el.setAttribute('data-listener-added', 'true');
                            el.addEventListener('sl-change', function(e) {{
                                const values = Array.isArray(el.value) ? el.value : [];
                                const valueStr = values.join(',');
                                htmx.ajax('POST', '/action/{cid}', {{
                                    values: {{ value: valueStr }},
                                    swap: 'none'
                                }});
                            }});
                        }}
                    }}
                    initSelect();
                }})();
                </script>
                '''
                return Component("div", id=init_script_cid, style="display:none", content=script)
            
            self.static_builders[init_script_cid] = script_builder
            if layout_ctx.get() == "sidebar":
                if init_script_cid not in self.static_sidebar_order:
                    self.static_sidebar_order.append(init_script_cid)
            else:
                if init_script_cid not in self.static_order:
                    self.static_order.append(init_script_cid)
        
        return s

    def text_area(self, label, value="", height=None, key=None, on_change=None, cls: str = "", **props):
        """Multi-line text input"""
        cid = self._get_next_cid("textarea")
        
        state_key = key or f"textarea:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "sl-input delay:50ms", "hx-swap": "none", "name": "value"}
                listener_script = ""
            else:
                attrs = {}
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-input', function(e) {{
                            window.sendAction('{cid}', el.value);
                        }});
                    }}
                }})();
                </script>
                '''
            
            textarea_props = {"rows": height or 3, "resize": "auto"}
            
            final_cls = build_cls(cls, **props)
            
            html = f'<sl-textarea id="{cid}" label="{label}" value="{cv}" class="{final_cls}"'
            for k, v in {**attrs, **textarea_props}.items():
                if v is True: html += f' {k}'
                elif v is not False and v is not None: html += f' {k}="{v}"'
            html += f'></sl-textarea>{listener_script}'
            
            return Component(None, id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def number_input(self, label, value=0, min_value=None, max_value=None, step=1, key=None, on_change=None, cls: str = "", **props):
        """Numeric input"""
        cid = self._get_next_cid("number")
        
        state_key = key or f"number:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            try:
                num_val = float(v) if '.' in str(v) else int(v)
                s.set(num_val)
                if on_change: on_change(num_val)
            except (ValueError, TypeError):
                pass
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "sl-input delay:50ms", "hx-swap": "none", "name": "value"}
                listener_script = ""
            else:
                attrs = {}
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-input', function(e) {{
                            window.sendAction('{cid}', el.value);
                        }});
                    }}
                }})();
                </script>
                '''
            
            num_props = {"type": "number"}
            if min_value is not None: num_props["min"] = min_value
            if max_value is not None: num_props["max"] = max_value
            if step is not None: num_props["step"] = step
            
            final_cls = build_cls(cls, **props)
            
            html = f'<sl-input id="{cid}" label="{label}" value="{cv}" class="{final_cls}"'
            for k, v in {**attrs, **num_props}.items():
                if v is True: html += f' {k}'
                elif v is not False and v is not None: html += f' {k}="{v}"'
            html += f'></sl-input>{listener_script}'
            
            return Component(None, id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def file_uploader(self, label, accept=None, multiple=False, key=None, on_change=None, help=None, cls: str = "", **props):
        """File upload widget"""
        cid = self._get_next_cid("file")
        
        state_key = key or f"file:{label}"
        s = self.state(None, key=state_key)
        
        def action(v):
            if v:
                try:
                    if isinstance(v, str) and v.startswith('{'):
                         try:
                             data = json.loads(v)
                         except:
                             data = v
                    else:
                        data = v
                    
                    if isinstance(data, dict):
                        if "content" in data:
                            uf = UploadedFile(data.get("name"), data.get("type"), data.get("size"), data.get("content"))
                            s.set(uf)
                            if on_change: on_change(uf)
                            return
                        elif "files" in data:
                             files = []
                             for f_data in data["files"]:
                                 files.append(UploadedFile(f_data.get("name"), f_data.get("type"), f_data.get("size"), f_data.get("content")))
                             s.set(files)
                             if on_change: on_change(files)
                             return
                except Exception as e:
                    print(f"File upload error: {e}")
            
            s.set(None)
            if on_change: on_change(None)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if cv:
                if isinstance(cv, list):
                    file_info = f"✅ {len(cv)} file(s) uploaded"
                else:
                    size_kb = cv.size / 1024
                    size_str = f"{size_kb:.1f}KB" if size_kb < 1024 else f"{size_kb/1024:.1f}MB"
                    file_info = f"✅ {cv.name} ({size_str})"
            else:
                file_info = ""
            
            accept_str = accept if accept else "*"
            help_html = f'<div class="font-size:0.75rem color:text-muted mt:0.25rem">{help}</div>' if help else ""
            
            final_cls = build_cls(f"mb:1rem {cls}", **props)
            
            html = f'''
            <div class="file-uploader {final_cls}">
                <label class="d:block mb:0.5rem fw:500 color:text">{label}</label>
                <input type="file" id="{cid}_input" accept="{accept_str}" {'multiple' if multiple else ''} 
                       class="d:block p:0.5rem b:1|solid|border r:0.25rem bg:bg-card color:text w:full font:inherit cursor:pointer" />
                {help_html}
                <div id="{cid}_info" class="mt:0.5rem font-size:0.875rem color:text-muted">{file_info}</div>
            </div>
            <script>
            (function() {{
                const input = document.getElementById('{cid}_input');
                const infoDiv = document.getElementById('{cid}_info');
                
                if (input && !input.hasAttribute('data-listener-added')) {{
                    input.setAttribute('data-listener-added', 'true');
                    
                    input.addEventListener('change', function(e) {{
                        const files = e.target.files;
                        if (files && files.length > 0) {{
                            infoDiv.textContent = '⏳ Uploading...';
                            
                            const fileArray = Array.from(files);
                            const promises = fileArray.map(file => {{
                                return new Promise((resolve, reject) => {{
                                    const reader = new FileReader();
                                    reader.onload = function(ev) {{
                                        resolve({{
                                            name: file.name,
                                            type: file.type,
                                            size: file.size,
                                            content: ev.target.result
                                        }});
                                    }};
                                    reader.onerror = function(err) {{
                                        reject(err);
                                    }};
                                    reader.readAsDataURL(file);
                                }});
                            }});
                            
                            Promise.all(promises).then(function(results) {{
                                let payload;
                                if ({'true' if multiple else 'false'}) {{
                                    payload = {{files: results}};
                                }} else {{
                                    payload = results[0];
                                }}
                                
                                if ({'true' if multiple else 'false'}) {{
                                    infoDiv.textContent = '✅ ' + results.length + ' file(s) uploaded';
                                }} else {{
                                    const file = results[0];
                                    const sizeKB = (file.size / 1024).toFixed(1);
                                    infoDiv.textContent = '✅ ' + file.name + ' (' + sizeKB + ' KB)';
                                }}
                                
                                if (window.sendAction) {{
                                    window.sendAction('{cid}', payload);
                                }} else if (window.htmx) {{
                                    htmx.ajax('POST', '/action/{cid}', {{
                                        values: {{ value: JSON.stringify(payload) }},
                                        swap: 'none'
                                    }});
                                }}
                            }}).catch(function(err) {{
                                infoDiv.textContent = '❌ Upload failed';
                                console.error('File upload error:', err);
                            }});
                        }}
                    }});
                }}
            }})();
            </script>
            '''
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def toggle(self, label, value=False, key=None, on_change=None, cls: str = "", **props):
        """Toggle switch widget"""
        cid = self._get_next_cid("toggle")
        
        state_key = key or f"toggle:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            real_val = str(v).lower() == 'true'
            s.set(real_val)
            if on_change: on_change(real_val)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            checked_attr = 'checked' if cv else ''
            
            if self.mode == 'lite':
                attrs_str = f'hx-post="/action/{cid}" hx-trigger="sl-change" hx-swap="none" hx-vals="js:{{value: event.target.checked}}"'
                listener_script = ""
            else:
                attrs_str = ""
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-change', function(e) {{
                            window.sendAction('{cid}', el.checked);
                        }});
                    }}
                }})();
                </script>
                '''
            
            final_cls = build_cls(cls, **props)
            html = f'<sl-switch id="{cid}" {checked_attr} {attrs_str} class="{final_cls}">{label}</sl-switch>{listener_script}'
            return Component(None, id=cid, content=html)
        self._register_component(cid, builder, action=action)
        return s

    def color_picker(self, label="Pick a color", value="#000000", key=None, on_change=None, cls: str = "", **props):
        """Color picker widget"""
        cid = self._get_next_cid("color")
        
        state_key = key or f"color:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "sl-change", "hx-swap": "none", "name": "value"}
            else:
                attrs = {"on_sl_change": f"window.sendAction('{cid}', this.value)"}
            
            final_cls = build_cls(cls, **props)
            return Component("sl-color-picker", id=cid, label=label, value=cv, class_=final_cls, **attrs)
        
        self._register_component(cid, builder, action=action)
        return s

    def date_input(self, label="Select date", value=None, key=None, on_change=None, cls: str = "", **props):
        """Date picker widget"""
        import datetime
        cid = self._get_next_cid("date")
        
        state_key = key or f"date:{label}"
        default_val = value if value else datetime.date.today().isoformat()
        s = self.state(default_val, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "change", "hx-swap": "none", "name": "value"}
            else:
                attrs = {"onchange": f"window.sendAction('{cid}', this.value)"}
            
            final_cls = build_cls(f"mb:0.5rem {cls}", **props)
            
            html = f'''
            <div class="{final_cls}">
                <label class="d:block mb:0.5rem fw:500 color:text">{label}</label>
                <input type="date" id="{cid}_input" value="{cv}" 
                       class="w:full p:0.5rem b:1|solid|border r:0.5rem bg:bg-card color:text font:inherit"
                       {' '.join(f'{k}="{v}"' for k,v in attrs.items())} />
            </div>
            '''
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def time_input(self, label="Select time", value=None, key=None, on_change=None, cls: str = "", **props):
        """Time picker widget"""
        import datetime
        cid = self._get_next_cid("time")
        
        state_key = key or f"time:{label}"
        default_val = value if value else datetime.datetime.now().strftime("%H:%M")
        s = self.state(default_val, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "change", "hx-swap": "none", "name": "value"}
            else:
                attrs = {"onchange": f"window.sendAction('{cid}', this.value)"}
            
            final_cls = build_cls(f"mb:0.5rem {cls}", **props)
            
            html = f'''
            <div class="{final_cls}">
                <label class="d:block mb:0.5rem fw:500 color:text">{label}</label>
                <input type="time" id="{cid}_input" value="{cv}" 
                       class="w:full p:0.5rem b:1|solid|border r:0.5rem bg:bg-card color:text font:inherit"
                       {' '.join(f'{k}="{v}"' for k,v in attrs.items())} />
            </div>
            '''
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def datetime_input(self, label="Select date and time", value=None, key=None, on_change=None, cls: str = "", **props):
        """DateTime picker widget"""
        import datetime
        cid = self._get_next_cid("datetime")
        
        state_key = key or f"datetime:{label}"
        default_val = value if value else datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        s = self.state(default_val, key=state_key)
        
        def action(v):
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs = {"hx-post": f"/action/{cid}", "hx-trigger": "change", "hx-swap": "none", "name": "value"}
            else:
                attrs = {"onchange": f"window.sendAction('{cid}', this.value)"}
            
            final_cls = build_cls(f"mb:0.5rem {cls}", **props)
            
            html = f'''
            <div class="{final_cls}">
                <label class="d:block mb:0.5rem fw:500 color:text">{label}</label>
                <input type="datetime-local" id="{cid}_input" value="{cv}" 
                       class="w:full p:0.5rem b:1|solid|border r:0.5rem bg:bg-card color:text font:inherit"
                       {' '.join(f'{k}="{v}"' for k,v in attrs.items())} />
            </div>
            '''
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder, action=action)
        return s

    def _input_component(self, type_name, tag_name, label, value, on_change, key=None, cls: str = "", **props):
        """Generic input component builder"""
        cid = self._get_next_cid(type_name)
        
        state_key = key or f"{type_name}:{label}"
        s = self.state(value, key=state_key)
        
        def action(v):
            if type_name == 'slider': 
                v = float(v) if '.' in str(v) else int(v)
            s.set(v)
            if on_change: on_change(v)
        
        def builder():
            token = rendering_ctx.set(cid)
            cv = s.value
            rendering_ctx.reset(token)
            
            if self.mode == 'lite':
                attrs_str = f'hx-post="/action/{cid}" hx-trigger="sl-change" hx-swap="none" name="value"'
                listener_script = ""
            else:
                attrs_str = ""
                listener_script = f'''
                <script>
                (function() {{
                    const el = document.getElementById('{cid}');
                    if (el && !el.hasAttribute('data-ws-listener')) {{
                        el.setAttribute('data-ws-listener', 'true');
                        el.addEventListener('sl-change', function(e) {{
                            window.sendAction('{cid}', el.value);
                        }});
                    }}
                }})();
                </script>
                '''
            
            # Separate semantic props from HTML attributes
            semantic_props = {}
            html_attrs = {}
            for k, v in props.items():
                if k in ['p', 'm', 'bg', 'color'] or k.startswith(('p:', 'm:', 'bg:', 'color:')):
                    semantic_props[k] = v
                else:
                    html_attrs[k] = v

            final_cls = build_cls(cls, **semantic_props)
            props_str = ' '.join(f'{k}="{v}"' for k, v in html_attrs.items() if v is not None and v is not False)
            
            html = f'<{tag_name} id="{cid}" label="{label}" value="{cv}" {attrs_str} class="{final_cls}" {props_str}></{tag_name}>{listener_script}'
            
            return Component(None, id=cid, content=html)
        self._register_component(cid, builder, action=action)
        return s
