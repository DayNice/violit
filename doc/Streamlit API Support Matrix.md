# 📊 Streamlit API Support Matrix

Violit supports most of Streamlit's major APIs, and has improved some structures for better performance.

## 1. Text & Media Elements
| Streamlit | Violit Support | Status | Note |
|---|---|---|---|
| `st.write` | `app.write` | ✅ | Compatible API (Signal/State auto-detection) |
| `st.markdown` | `app.markdown` | ✅ | Markdown syntax support |
| `st.title`, `st.header` | `app.title`, `app.header` | ✅ | Gradient effect automatically applied |
| `st.subheader`, `st.caption` | `app.subheader`, `app.caption` | ✅ | |
| `st.code` | `app.code` | ✅ |  |
| `st.text` | `app.text` | ✅ | |
| `st.latex` | `app.latex` | ❌ |  |
| `st.divider` | `app.divider` | ✅ | |
| `st.image` | `app.image` | ✅ | Supports URL, Local File, NumPy, PIL |
| `st.audio`, `st.video` | `app.audio`, `app.video` | ✅ | |

## 2. Data & Charts
| Streamlit | Violit Support | Status | Note |
|---|---|---|---|
| `st.dataframe` | `app.dataframe` | ✅ | **Ag-Grid Native** (High Performance) |
| `st.table` | `app.table` | ✅ | |
| `st.metric` | `app.metric` | ✅ | `delta` and automatic color support |
| `st.json` | `app.json` | ✅ | |
| `st.data_editor` | `app.data_editor` | ✅ | Simplified version provided |
| `st.plotly_chart` | `app.plotly_chart` | ✅ | Fully compatible with Plotly |
| `st.pyplot` | `app.pyplot` | ✅ | Matplotlib support |
| `st.line/bar/area_chart` | `app.line_chart` etc. | ✅ | |
| `st.scatter_chart` | `app.scatter_chart` | ✅ | |
| `st.map` | `app.map` | ❌ | Recommended to use Mapbox in `plotly_chart` |

## 3. Input Widgets
| Streamlit | Violit Support | Status | Note |
|---|---|---|---|
| `st.button` | `app.button` | ✅ | `key` unnecessary, `on_click` recommended |
| `st.download_button` | `app.download_button` | ✅ | |
| `st.link_button` | `app.link_button` | ✅ | |
| `st.text_input` | `app.text_input` | ✅ | |
| `st.number_input` | `app.number_input` | ✅ | |
| `st.text_area` | `app.text_area` | ✅ | |
| `st.checkbox`, `st.toggle` | `app.checkbox`, `app.toggle` | ✅ | |
| `st.radio` | `app.radio` | ✅ | |
| `st.selectbox` | `app.selectbox` | ✅ | |
| `st.multiselect` | `app.multiselect` | ✅ | |
| `st.slider` | `app.slider` | ✅ | |
| `st.date/time_input` | `app.date_input` etc. | ✅ | |
| `st.file_uploader` | `app.file_uploader` | ✅ | |
| `st.color_picker` | `app.color_picker` | ✅ | |
| `st.camera_input` | `app.camera_input` | ❌ | Not supported |

## 4. Layout & Containers
| Streamlit | Violit Support | Status | Note |
|---|---|---|---|
| `st.columns` | `app.columns` | ✅ | List ratio support (e.g. `[1, 2, 1]`) |
| `st.container` | `app.container` | ✅ | |
| `st.expander` | `app.expander` | ✅ | |
| `st.tabs` | `app.tabs` | ✅ | |
| `st.empty` | `app.empty` | ✅ | For dynamic updates |
| `st.sidebar` | `app.sidebar` | ✅ | Use `with app.sidebar:` syntax |
| `st.dialog` | `app.dialog` | ✅ | Modal Decorator supported |
| `st.popover` | `app.popover` | ❌ | Recommended to use `app.dialog` |

## 5. Chat & Status
| Streamlit | Violit Support | Status | Note |
|---|---|---|---|
| `st.chat_message` | `app.chat_message` | ✅ | Avatar supported |
| `st.chat_input` | `app.chat_input` | ✅ | |
| `st.status` | `app.status` | ✅ | |
| `st.spinner` | `app.spinner` | ✅ | |
| `st.progress` | `app.progress` | ✅ | |
| `st.toast` | `app.toast` | ✅ | |
| `st.balloons`, `st.snow` | `app.balloons` etc. | ✅ | |
| `st.success/error/warning` | `app.success` etc. | ✅ | |

## 6. Control Flow
| Streamlit | Violit Approach | Note |
|---|---|---|
| `st.rerun` | **Unnecessary** | Immediate partial update upon State change (Zero Rerun) |
| `st.stop` | **Unnecessary** | Handled by Python control flow (`return`, etc.) |
| `st.form` | `app.form` | ✅ Supported (For Batch Input) |

---

## 🔌 Third-Party Library Support

Violit is absorbing the features of Streamlit's popular third-party libraries as **Native** features.

| Library | Violit Status | Description |
|---|---|---|
| **streamlit-aggrid** | ✅ **Native** | `app.dataframe` basically uses high-performance Ag-Grid. No separate installation required. |
| **Plotly** | ✅ **Native** | Fully supported via `app.plotly_chart`. |
| **streamlit-lottie** | ❌ **Planned** | Currently not supported (Planned to add `app.lottie`). |
| **streamlit-option-menu** | ✅ **Native** | Violit's built-in Sidebar perfectly replaces Multi-page Navigation. |
| **streamlit-extras** | ⚠️ **Partial** | Some design elements like Metric Cards can be replaced by the Violit Theme System. |
| **streamlit-webrtc** | ⚠️ **Planned** | Future support planned via WebSocket-based real-time communication. |
