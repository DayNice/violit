"""
Style Utilities for Violit (Hybrid Styling Engine)
Maps semantic Python props to Master CSS classes.
"""

from typing import Dict, Any, Optional

def build_cls(base_cls: str = "", **kwargs) -> str:
    """
    Build Master CSS class string from semantic props.
    
    Args:
        base_cls: User provided class string (e.g. "hover:scale-105")
        **kwargs: Semantic props (e.g. p=2, m="4rem", bg="red-50")
        
    Returns:
        Combined class string
    """
    classes = []
    
    # Semantic Props Mapping
    # Key: Prop name, Value: Master CSS prefix
    mappings = {
        # Spacing
        'p': 'p', 'padding': 'p',
        'px': 'px', 'py': 'py', 'pt': 'pt', 'pb': 'pb', 'pl': 'pl', 'pr': 'pr',
        'm': 'm', 'margin': 'm',
        'mx': 'mx', 'my': 'my', 'mt': 'mt', 'mb': 'mb', 'ml': 'ml', 'mr': 'mr',
        'gap': 'gap',
        
        # Sizing
        'w': 'w', 'width': 'w', 'min_w': 'min-w', 'max_w': 'max-w',
        'h': 'h', 'height': 'h', 'min_h': 'min-h', 'max_h': 'max-h',
        
        # Typography
        'font': 'font', 'f': 'font',
        'size': 'font-size', 'fs': 'font-size',
        'weight': 'font-weight', 'fw': 'font-weight',
        'align': 'text-align', 'text_align': 'text-align',
        'color': 'color', 'c': 'color', 'fg': 'color',
        'leading': 'line-height', 'lh': 'line-height',
        
        # Background & Border
        'bg': 'bg', 'background': 'bg',
        'b': 'border', 'border': 'border',
        'r': 'r', 'radius': 'r', 'rounded': 'r',
        'outline': 'outline',
        
        # Flex/Grid
        'd': 'd', 'display': 'd',
        'flex': 'flex',
        'grid': 'grid',
        'justify': 'jc', 'justify_content': 'jc',
        'items': 'ai', 'align_items': 'ai',
        
        # Effects
        'shadow': 'shadow', 'box_shadow': 'shadow',
        'opacity': 'opacity',
        'z': 'z', 'z_index': 'z',
        'cursor': 'cursor',
        'transition': 'transition',
        'transform': 'transform',
        'overflow': 'overflow',
    }
    
    for key, value in kwargs.items():
        if value is None:
            continue
            
        # Handle boolean flags
        if isinstance(value, bool):
            if value:
                if key == 'center':
                    classes.append("text:center")
                elif key == 'middle':
                    classes.append("flex ai:center jc:center")
                elif key == 'hidden':
                    classes.append("d:none")
                elif key == 'block':
                    classes.append("d:block")
                elif key == 'inline':
                    classes.append("d:inline")
                elif key == 'pointer':
                    classes.append("cursor:pointer")
                elif key == 'relative':
                    classes.append("rel")
                elif key == 'absolute':
                    classes.append("abs")
                elif key == 'fixed':
                    classes.append("fixed")
                elif key == 'full':
                    classes.append("w:full h:full")
            continue
            
        # Handle mapped props
        if key in mappings:
            prefix = mappings[key]
            # Convert spaces to pipes for Master CSS syntax (e.g. "10px 20px" -> "10px|20px")
            val_str = str(value).replace(" ", "|")
            classes.append(f"{prefix}:{val_str}")
            
    if base_cls:
        classes.append(base_cls)
        
    return " ".join(classes).strip()

def get_variant_styles(variant: str) -> str:
    """Get predefined styles for variants using Master CSS classes"""
    variants = {
        # Box Variants
        'hero': 'p:4rem|2rem m:0|0|3rem|0 r:24 text:center bg:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(168,85,247,0.12)) rel overflow:hidden',
        'cta': 'p:4rem|2rem m:3rem|0 r:24 text:center bg:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(217,70,239,0.1))',
        'stat': 'p:2rem r:16 text:center bg:linear-gradient(135deg,rgba(139,92,246,0.1),rgba(168,85,247,0.05)) b:1|solid|rgba(139,92,246,0.2)',
        'glass': 'p:2rem r:16 bg:rgba(255,255,255,0.7) backdrop-filter:blur(12px) b:1|solid|rgba(255,255,255,0.5) shadow:0|8|32|0|rgba(31,38,135,0.1)',
        'footer': 'p:3rem|0 m:4rem|0|0|0 text:center bt:1|solid|gray-20',
        
        # Card Variants
        'feature': 'p:2rem r:16 bg:white shadow:lg hover:translateY(-5) hover:shadow:xl transition:all|0.3s',
    }
    return variants.get(variant, "")
