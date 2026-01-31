"""List widgets for reactive list management"""

from typing import Callable, Any, List as ListType
from ..component import Component
from ..context import rendering_ctx
from ..state import State
from ..style_utils import build_cls


class ListWidgetsMixin:
    
    def reactive_list(self, 
                     items: ListType[Any] = None,
                     render_item: Callable[[Any], str] = None,
                     key: str = None,
                     container_id: str = None,
                     empty_message: str = None,
                     reverse: bool = False,
                     item_gap: str = "1rem",
                     cls: str = "",
                     **props):
        """Create a reactive list that updates when items change"""
        cid = self._get_next_cid("reactive_list")
        container_id = container_id or f"{cid}-container"
        
        state_key = key or f"list:{cid}"
        if isinstance(items, State):
            list_state = items
        else:
            list_state = self.state(items or [], key=state_key)
        
        def builder():
            token = rendering_ctx.set(cid)
            current_items = list_state.value
            rendering_ctx.reset(token)
            
            if not current_items:
                if empty_message:
                    content = f'<div class="text:center p:2rem color:text-muted">{empty_message}</div>'
                else:
                    content = ''
            else:
                items_to_render = list(reversed(current_items)) if reverse else current_items
                
                if render_item:
                    rendered_items = []
                    for item in items_to_render:
                        item_html = render_item(item)
                        rendered_items.append(item_html)
                    content = ''.join(rendered_items)
                else:
                    content = ''.join([f'<div class="p:0.5rem">{item}</div>' for item in items_to_render])
            
            final_cls = build_cls(f"flex flex:col w:full {cls}", gap=item_gap, **props)
            
            html = f'''
            <div id="{container_id}" class="{final_cls}">
                {content}
            </div>
            '''
            
            return Component("div", id=cid, content=html)
        
        self._register_component(cid, builder)
        
        return list_state
    
    def card_list(self,
                 items: ListType[dict] = None,
                 key: str = None,
                 container_id: str = None,
                 empty_message: str = "No items yet",
                 card_type: str = "live",
                 reverse: bool = True,
                 cls: str = "",
                 **props):
        """Reactive list for card items"""
        def render_card(item):
            if card_type == 'live':
                # Use live_card from CardWidgetsMixin (assuming it's available on self via App inheritance)
                # But live_card registers a component, it doesn't return HTML string directly usually.
                # However, styled_card has return_html option. live_card is a wrapper around card().
                # We need a way to get HTML string for list items if we are concatenating them.
                # Or we can register components inside the list builder?
                # reactive_list expects render_item to return HTML string.
                
                # If we use styled_card with return_html=True, it works.
                return self.styled_card(
                    content=item.get('content', ''),
                    style='live',
                    header_badge='LIVE',
                    footer_text=item.get('created_at'),
                    data_id=item.get('id'),
                    return_html=True
                )
            elif card_type == 'admin':
                return self.styled_card(
                    content=item.get('content', ''),
                    style='admin',
                    header_badge=f"#{item.get('id')}",
                    footer_text=item.get('created_at'),
                    data_id=item.get('id'),
                    return_html=True
                )
            else:
                return self.styled_card(
                    content=item.get('content', ''),
                    style='default',
                    footer_text=item.get('created_at'),
                    data_id=item.get('id'),
                    return_html=True
                )
        
        return self.reactive_list(
            items=items,
            render_item=render_card,
            key=key,
            container_id=container_id,
            empty_message=empty_message,
            reverse=reverse,
            cls=cls,
            **props
        )
