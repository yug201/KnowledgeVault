import streamlit as st
import requests
from datetime import datetime
import os
import os
# BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
BASE_URL="https://knowledgevault-3bqk.onrender.com/"
st.set_page_config(page_title="Vault Dashboard", layout="wide", page_icon="🛡️")

# --- IMPROVED CSS (Fixes the white bars and improves spacing) ---
st.markdown("""
    <style>
    /* Card Container */
    .vault-card {
        border-radius: 12px;
        padding: 20px;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
        transition: transform 0.2s;
    }
    .vault-card:hover {
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    /* Thumbnail Fix */
    .thumb-img {
        object-fit: cover;
        border-radius: 8px;
        height: 160px;
        width: 100%;
        margin-bottom: 12px;
        display: block;
    }
    /* Tags */
    .tag-pill {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ddd;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.75rem;
        margin-right: 6px;
        display: inline-block;
        margin-bottom: 5px;
    }
    /* Todo Styling */
    .todo-container {
        background: rgba(255, 255, 255, 0.03);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

# --- API HELPER ---
def api_call(method, endpoint, **kwargs):
    with st.spinner("⏳ Syncing with Vault..."):
        try:
            url = f"{BASE_URL}{endpoint}"
            headers = get_headers()
            if method == "GET": res = requests.get(url, headers=headers)
            elif method == "POST": res = requests.post(url, headers=headers, **kwargs)
            elif method == "PUT": res = requests.put(url, headers=headers, **kwargs)
            elif method == "DELETE": res = requests.delete(url, headers=headers)
            return res
        except Exception as e:
            st.error(f"Vault Connection Error: {e}")
            return None

# --- AUTHENTICATION ---
def auth_screen():
    st.title("🛡️ Knowledge Vault Login")
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        # --- GENERAL DEMO INFO BANNER ---
        st.info("""
        👋 **Welcome to the Knowledge Vault!**  
        To explore the dashboard and test its features, feel free to use the pre-filled demo credentials below. 
        *(Email: **demo@example.com** | Password: **demo123**)*
        """)

        # Pre-filled using the `value` parameter
        e = st.text_input("Email", value="demo@example.com", key="l_email")
        p = st.text_input("Password", value="demo123", type="password", key="l_pass")
        
        if st.button("Access Vault", use_container_width=True):
            res = api_call("POST", "/auth/login", json={"email": e, "password": p})
            if res and res.status_code == 200:
                st.session_state.access_token = res.json()["access_token"]
                st.rerun()
            else: 
                st.error("Access Denied! (Have you registered this  account in the backend?)")

    with tab2:
        re = st.text_input("Email", key="r_email")
        rp = st.text_input("Password", type="password", key="r_pass")
        if st.button("Register", use_container_width=True):
            res = api_call("POST", "/auth/register", json={"email": re, "password": rp})
            if res and res.status_code == 201: 
                st.success("Account Created! You can login now.")

# --- MAIN DASHBOARD ---
def dashboard():
    st.sidebar.title("🔐 Vault Controls")
    
    # --- ADD KNOWLEDGE ---
    with st.sidebar.expander("➕ NEW KNOWLEDGE", expanded=False):
        k_type = st.selectbox("Format", ["TEXT", "URL", "IMAGE", "PDF"])
        title = st.text_input("Title", key="new_title")
        desc = st.text_input("Description", key="new_desc")
        tags = st.text_input("Tags (comma separated)", key="new_tags")
        
        content = None
        if k_type == "TEXT": content = st.text_area("Note Content")
        elif k_type == "URL": content = st.text_input("Link URL")
        
        file_up = None
        if k_type in ["IMAGE", "PDF"]:
            file_up = st.file_uploader(f"Choose {k_type} File")

        if st.button("Save Entry", use_container_width=True):
            payload = {
                "title": title, "type": k_type, "description": desc,
                "content": content, "tags": [t.strip() for t in tags.split(",") if t.strip()]
            }
            res = api_call("POST", "/knowledge", json=payload)
            if res and res.status_code == 201:
                if file_up:
                    api_call("POST", f"/knowledge/{res.json()['id']}/file", files={"file": (file_up.name, file_up.getvalue(), file_up.type)})
                st.rerun()

    # --- ADD TODO ---
    with st.sidebar.expander("✅ NEW TASK", expanded=False):
        t_title = st.text_input("What needs to be done?")
        if st.button("Add Task"):
            api_call("POST", "/todos", json={"title": t_title})
            st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.access_token = None
        st.rerun()

    # --- LAYOUT ---
    left_col, right_col = st.columns([2.2, 1])

    with left_col:
        st.header("📁 My Vault")
        k_res = api_call("GET", "/knowledge")
        if k_res and k_res.status_code == 200:
            items = k_res.json()
            # Grid of 2
            grid = st.columns(2)
            for i, item in enumerate(items):
                with grid[i % 2]:
                    # The Card
                    st.markdown(f'<div class="vault-card">', unsafe_allow_html=True)
                    
                    # Image Thumbnail
                    if item.get("file_url") and item.get("mime_type", "").startswith("image"):
                        st.markdown(f'<img src="{item["file_url"]}" class="thumb-img">', unsafe_allow_html=True)
                    
                    st.subheader(item['title'])
                    st.caption(f"{item['type']} • {item['created_at'][:10]}")
                    
                    if item.get('description'):
                        st.info(item['description'])
                    
                    if item.get('content') and item['type'] == "TEXT":
                        st.write(item['content'][:150] + "..." if len(item['content']) > 150 else item['content'])

                    # Tags Pills
                    tag_html = "".join([f'<span class="tag-pill">{t}</span>' for t in item.get('tags', [])])
                    st.markdown(tag_html, unsafe_allow_html=True)
                    
                    # Buttons Row
                    btn_cols = st.columns([1, 1, 1])
                    if item.get("file_url"):
                        btn_cols[0].link_button("📎 View", item["file_url"], use_container_width=True)
                    
                    # UPDATE BUTTON
                    if btn_cols[1].button("✏️ Edit", key=f"edit_{item['id']}", use_container_width=True):
                        st.session_state.editing_id = item['id']
                    
                    # DELETE BUTTON
                    if btn_cols[2].button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                        api_call("DELETE", f"/knowledge/{item['id']}")
                        st.rerun()
                    
                    # EDIT FORM (Appears only if this item is selected)
                    if st.session_state.editing_id == item['id']:
                        st.divider()
                        st.write("Updating Entry...")
                        new_t = st.text_input("New Title", value=item['title'], key=f"ut_{item['id']}")
                        new_c = st.text_area("New Content/URL", value=item.get('content', '') or "", key=f"uc_{item['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("Save Changes", key=f"save_{item['id']}"):
                            api_call("PUT", f"/knowledge/{item['id']}", json={"title": new_t, "content": new_c})
                            st.session_state.editing_id = None
                            st.rerun()
                        if c2.button("Cancel", key=f"can_{item['id']}"):
                            st.session_state.editing_id = None
                            st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.header("📝 Tasks")
        t_res = api_call("GET", "/todos")
        if t_res and t_res.status_code == 200:
            for t in t_res.json():
                st.markdown(f'<div class="todo-container">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([0.2, 0.8, 0.2])
                
                done = col1.checkbox("", value=t['completed'], key=f"check_{t['id']}")
                if done != t['completed']:
                    api_call("PUT", f"/todos/{t['id']}", json={"completed": done})
                    st.rerun()
                
                label = f"~~{t['title']}~~" if t['completed'] else t['title']
                col2.markdown(f"{label}")
                
                if col3.button("❌", key=f"tdel_{t['id']}"):
                    api_call("DELETE", f"/todos/{t['id']}")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# --- RUN APP ---
if st.session_state.access_token is None:
    auth_screen()
else:
    dashboard()
