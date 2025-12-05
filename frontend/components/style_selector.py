"""
Style Selector Component.
Renders style selection and parameter controls.
"""

import streamlit as st
from typing import Dict, Any, Tuple, Optional


# Available styles with descriptions
STYLES = {
    "cartoon": {
        "name": "🎭 Cartoon",
        "description": "Classic cartoon effect with bold edges and smooth colors",
        "icon": "🎭"
    },
    "sketch": {
        "name": "✏️ Pencil Sketch",
        "description": "Black and white pencil drawing effect",
        "icon": "✏️"
    },
    "color_pencil": {
        "name": "🖍️ Color Pencil",
        "description": "Colored pencil drawing with soft strokes",
        "icon": "🖍️"
    },
    "oil_painting": {
        "name": "🎨 Oil Painting",
        "description": "Rich oil painting style with smooth textures",
        "icon": "🎨"
    },
    "watercolor": {
        "name": "💧 Watercolor",
        "description": "Soft watercolor paint effect",
        "icon": "💧"
    },
    "pop_art": {
        "name": "🌈 Pop Art",
        "description": "Andy Warhol-style pop art with vibrant colors",
        "icon": "🌈"
    }
}


def render_style_selector(key: str = "style_select") -> str:
    """
    Render the style selector component.
    
    Args:
        key: Unique key for the widget
    
    Returns:
        Selected style key
    """
    st.markdown("### 🎨 Choose Effect Style")
    
    # Style cards
    cols = st.columns(3)
    
    selected_style = st.session_state.get(f"{key}_selected", "cartoon")
    
    for i, (style_key, style_info) in enumerate(STYLES.items()):
        with cols[i % 3]:
            is_selected = style_key == selected_style
            border_style = "2px solid #ff4b4b" if is_selected else "1px solid #ddd"
            
            with st.container(border=True):
                st.markdown(f"### {style_info['icon']}")
                st.markdown(f"**{style_info['name'].split(' ', 1)[1]}**")
                st.caption(style_info['description'])
                
                if st.button(
                    "Select" if not is_selected else "✓ Selected",
                    key=f"{key}_{style_key}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state[f"{key}_selected"] = style_key
                    st.rerun()
    
    return st.session_state.get(f"{key}_selected", "cartoon")


def get_style_params(style: str, key: str = "params") -> Dict[str, Any]:
    """
    Render parameter controls for the selected style.
    
    Args:
        style: Selected style key
        key: Unique key prefix for widgets
    
    Returns:
        Dictionary of parameters
    """
    params = {}
    
    with st.expander("⚙️ Advanced Parameters", expanded=False):
        st.caption("Adjust parameters to fine-tune the effect")
        
        if style == "cartoon":
            params = _cartoon_params(key)
        elif style == "sketch":
            params = _sketch_params(key)
        elif style == "color_pencil":
            params = _color_pencil_params(key)
        elif style == "oil_painting":
            params = _oil_painting_params(key)
        elif style == "watercolor":
            params = _watercolor_params(key)
        elif style == "pop_art":
            params = _pop_art_params(key)
    
    return params


def _cartoon_params(key: str) -> Dict[str, Any]:
    """Cartoon effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        blur_kernel = st.slider(
            "Edge Blur",
            min_value=3, max_value=21, value=7, step=2,
            key=f"{key}_blur",
            help="Blur kernel size (must be odd)"
        )
        
        bilateral_d = st.slider(
            "Smoothing",
            min_value=5, max_value=15, value=9,
            key=f"{key}_bilateral",
            help="Bilateral filter diameter"
        )
    
    with col2:
        threshold_block = st.slider(
            "Edge Threshold Block",
            min_value=3, max_value=21, value=9, step=2,
            key=f"{key}_threshold",
            help="Adaptive threshold block size"
        )
        
        sigma_color = st.slider(
            "Color Sigma",
            min_value=50, max_value=300, value=200,
            key=f"{key}_sigma",
            help="Bilateral filter sigma color"
        )
    
    return {
        "blur_kernel_size": blur_kernel,
        "threshold_block_size": threshold_block,
        "bilateral_d": bilateral_d,
        "bilateral_sigma_color": sigma_color,
        "bilateral_sigma_space": sigma_color
    }


def _sketch_params(key: str) -> Dict[str, Any]:
    """Pencil sketch effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        blur_kernel = st.slider(
            "Blur Intensity",
            min_value=3, max_value=51, value=21, step=2,
            key=f"{key}_blur",
            help="Higher values create smoother strokes"
        )
    
    with col2:
        invert = st.checkbox(
            "Invert (White background)",
            value=True,
            key=f"{key}_invert",
            help="Invert colors for white background"
        )
    
    return {
        "blur_kernel_size": blur_kernel,
        "invert": invert
    }


def _color_pencil_params(key: str) -> Dict[str, Any]:
    """Color pencil effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        sketch_weight = st.slider(
            "Sketch Weight",
            min_value=0.0, max_value=1.0, value=0.7, step=0.1,
            key=f"{key}_sketch_weight",
            help="How much of the sketch effect to include"
        )
    
    with col2:
        color_weight = st.slider(
            "Color Weight",
            min_value=0.0, max_value=1.0, value=0.3, step=0.1,
            key=f"{key}_color_weight",
            help="How much of the original color to include"
        )
    
    blur_kernel = st.slider(
        "Stroke Softness",
        min_value=3, max_value=51, value=21, step=2,
        key=f"{key}_blur",
        help="Softness of pencil strokes"
    )
    
    return {
        "sketch_weight": sketch_weight,
        "color_weight": color_weight,
        "blur_kernel_size": blur_kernel
    }


def _oil_painting_params(key: str) -> Dict[str, Any]:
    """Oil painting effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        sigma_s = st.slider(
            "Brush Size",
            min_value=20, max_value=100, value=60,
            key=f"{key}_sigma_s",
            help="Size of brush strokes"
        )
    
    with col2:
        sigma_r = st.slider(
            "Color Range",
            min_value=0.1, max_value=1.0, value=0.6, step=0.1,
            key=f"{key}_sigma_r",
            help="Range of colors preserved"
        )
    
    return {
        "sigma_s": sigma_s,
        "sigma_r": sigma_r
    }


def _watercolor_params(key: str) -> Dict[str, Any]:
    """Watercolor effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        sigma_s = st.slider(
            "Smoothness",
            min_value=20, max_value=100, value=60,
            key=f"{key}_sigma_s",
            help="Smoothness of the effect"
        )
    
    with col2:
        sigma_r = st.slider(
            "Color Blending",
            min_value=0.1, max_value=1.0, value=0.4, step=0.1,
            key=f"{key}_sigma_r",
            help="How much colors blend together"
        )
    
    return {
        "sigma_s": sigma_s,
        "sigma_r": sigma_r
    }


def _pop_art_params(key: str) -> Dict[str, Any]:
    """Pop art effect parameters."""
    col1, col2 = st.columns(2)
    
    with col1:
        num_colors = st.slider(
            "Number of Colors",
            min_value=4, max_value=16, value=8,
            key=f"{key}_colors",
            help="Number of colors in the palette"
        )
    
    with col2:
        saturation = st.slider(
            "Color Boost",
            min_value=1.0, max_value=3.0, value=1.5, step=0.1,
            key=f"{key}_saturation",
            help="Saturation multiplier"
        )
    
    return {
        "num_colors": num_colors,
        "saturation_boost": saturation
    }
