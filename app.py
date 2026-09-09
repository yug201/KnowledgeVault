import os
import html
import requests
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
BASE_URL="https://knowledgevault-3bqk.onrender.com"

st.set_page_config(
    page_title="Knowledge Vault",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6;
    }

    .login-brand {
        text-align: center;
        margin: 2rem 0 1.5rem 0;
    }

    .login-brand h1 {
        font-size: 2.5rem;
        margin-bottom: 0.3rem;
        color: #1f2937;
    }

    .login-brand p {
        color: #6b7280;
        font-size: 1.05rem;
    }

    .demo-box {
        border: 1px solid #bfdbfe;
        background: #eff6ff;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin: 1rem 0 1.3rem 0;
        color: #1e3a8a;
    }

    .demo-box strong {
        color: #1d4ed8;
    }

    .page-heading {
        margin-bottom: 1.5rem;
    }

    .page-heading h1 {
        margin-bottom: 0.2rem;
        color: #111827;
    }

    .page-heading p {
        color: #6b7280;
        font-size: 1rem;
    }

    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem 1.2rem;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.85rem;
    }

    .stat-value {
        color: #111827;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    .entry-type {
        color: #2563eb;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.06rem;
    }

    .tag {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        border-radius: 20px;
        padding: 3px 9px;
        margin: 2px 3px 2px 0;
        font-size: 0.76rem;
    }

    .empty-state {
        border: 1px dashed #cbd5e1;
        border-radius: 14px;
        padding: 2rem;
        text-align: center;
        color: #64748b;
        background: #f8fafc;
    }

    .todo-completed {
        text-decoration: line-through;
        color: #9ca3af;
    }

    .todo-active {
        color: #111827;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None

if "page" not in st.session_state:
    st.session_state.page = "Vault"


# =========================================================
# API FUNCTIONS
# =========================================================
def api_headers():
    if st.session_state.access_token:
        return {
            "Authorization": f"Bearer {st.session_state.access_token}"
        }
    return {}


def api_call(method, endpoint, **kwargs):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"

    try:
        return requests.request(
            method=method,
            url=url,
            headers=api_headers(),
            timeout=30,
            **kwargs,
        )

    except requests.RequestException as error:
        st.error(f"Could not connect to the server: {error}")
        return None


def api_error(response, default_message="Something went wrong."):
    if not response:
        return

    try:
        message = response.json().get("detail", default_message)
    except ValueError:
        message = default_message

    st.error(message)


def logout():
    st.session_state.access_token = None
    st.session_state.editing_id = None
    st.session_state.page = "Vault"
    st.rerun()


# =========================================================
# LOGIN PAGE
# =========================================================
def login_page():
    left, main, right = st.columns([1, 1.25, 1])

    with main:
        st.markdown("""
        <div class="login-brand">
            <h1>✦ Knowledge Vault</h1>
            <p>Your personal home for ideas, notes, files, and tasks.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="demo-box">
            <strong>Try the demo account</strong><br>
            Email: <strong>demo@example.com</strong><br>
            Password: <strong>demo123</strong>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Use Demo Account", use_container_width=True):
            st.session_state.login_email = "demo@example.com"
            st.session_state.login_password = "demo123"
            st.rerun()

        login_tab, register_tab = st.tabs(["Sign In", "Create Account"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    key="login_email",
                    placeholder="you@example.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                    placeholder="Enter your password",
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email or not password:
                    st.warning("Please enter your email and password.")
                    return

                response = api_call(
                    "POST",
                    "/auth/login",
                    json={
                        "email": email,
                        "password": password,
                    },
                )

                if response and response.status_code == 200:
                    st.session_state.access_token = response.json()["access_token"]
                    st.rerun()

                elif response:
                    api_error(response, "Incorrect email or password.")

        with register_tab:
            with st.form("register_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="signup_email",
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    key="signup_password",
                )

                submitted = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email or not password:
                    st.warning("Please enter an email and password.")
                    return

                response = api_call(
                    "POST",
                    "/auth/register",
                    json={
                        "email": email,
                        "password": password,
                    },
                )

                if response and response.status_code == 201:
                    st.success("Account created. Please sign in.")

                elif response:
                    api_error(response, "Could not create your account.")


# =========================================================
# SIDEBAR
# =========================================================
def sidebar():
    with st.sidebar:
        st.markdown("## ✦ Knowledge Vault")
        st.caption("Your private workspace")

        st.divider()

        if st.button(
            "📚  My Vault",
            use_container_width=True,
            type="primary" if st.session_state.page == "Vault" else "secondary",
        ):
            st.session_state.page = "Vault"
            st.rerun()

        if st.button(
            "✅  My Tasks",
            use_container_width=True,
            type="primary" if st.session_state.page == "Tasks" else "secondary",
        ):
            st.session_state.page = "Tasks"
            st.rerun()

        st.divider()

        with st.expander("＋ Add Knowledge"):
            add_knowledge_form()

        with st.expander("＋ Add Task"):
            add_task_form()

        st.divider()

        if st.button("Log Out", use_container_width=True):
            logout()


# =========================================================
# CREATE FORMS
# =========================================================
def add_knowledge_form():
    with st.form("add_knowledge", clear_on_submit=True):
        entry_type = st.selectbox(
            "Type",
            ["TEXT", "URL", "IMAGE", "PDF"],
        )

        title = st.text_input("Title")
        description = st.text_area("Description", height=80)
        tags = st.text_input("Tags", placeholder="python, ideas, project")

        content = None
        uploaded_file = None

        if entry_type == "TEXT":
            content = st.text_area(
                "Your note",
                height=180,
                placeholder="Write something useful...",
            )

        elif entry_type == "URL":
            content = st.text_input(
                "Website link",
                placeholder="https://example.com",
            )

        elif entry_type in ["IMAGE", "PDF"]:
            uploaded_file = st.file_uploader(
                "Choose file",
                type=["png", "jpg", "jpeg", "webp", "pdf"],
            )

        submitted = st.form_submit_button(
            "Save Entry",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not title.strip():
            st.warning("A title is required.")
            return

        response = api_call(
            "POST",
            "/knowledge",
            json={
                "type": entry_type,
                "title": title.strip(),
                "description": description.strip() or None,
                "content": content.strip() if content else None,
                "tags": [
                    tag.strip()
                    for tag in tags.split(",")
                    if tag.strip()
                ],
            },
        )

        if response and response.status_code == 201:
            entry = response.json()

            if uploaded_file:
                upload_response = api_call(
                    "POST",
                    f"/knowledge/{entry['id']}/file",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                )

                if not upload_response or upload_response.status_code != 200:
                    st.warning("Entry was saved, but the file upload failed.")

            st.success("Added to your vault.")
            st.rerun()

        elif response:
            api_error(response, "Could not save the entry.")


def add_task_form():
    with st.form("add_task", clear_on_submit=True):
        title = st.text_input(
            "Task title",
            placeholder="What do you need to do?",
        )

        description = st.text_area(
            "Description",
            height=80,
        )

        submitted = st.form_submit_button(
            "Add Task",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not title.strip():
            st.warning("A task title is required.")
            return

        response = api_call(
            "POST",
            "/todos",
            json={
                "title": title.strip(),
                "description": description.strip() or None,
            },
        )

        if response and response.status_code == 201:
            st.success("Task added.")
            st.rerun()

        elif response:
            api_error(response, "Could not add the task.")


# =========================================================
# KNOWLEDGE ENTRY CARD
# =========================================================
def knowledge_card(item):
    with st.container(border=True):
        file_url = item.get("file_url")
        mime_type = item.get("mime_type", "")
        item_type = item.get("type", "TEXT")

        if file_url and mime_type.startswith("image"):
            st.image(file_url, use_container_width=True)

        st.markdown(
            f'<div class="entry-type">{html.escape(item_type)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"#### {item['title']}")

        if item.get("description"):
            st.write(item["description"])

        if item_type == "TEXT" and item.get("content"):
            content = item["content"]
            st.caption(
                content[:180] + "..."
                if len(content) > 180
                else content
            )

        if item_type == "URL" and item.get("content"):
            st.link_button(
                "Open Website ↗",
                item["content"],
                use_container_width=True,
            )

        if file_url and not mime_type.startswith("image"):
            st.link_button(
                "Open File ↗",
                file_url,
                use_container_width=True,
            )

        if item.get("tags"):
            tags_html = "".join(
                f'<span class="tag">{html.escape(tag)}</span>'
                for tag in item["tags"]
            )
            st.markdown(tags_html, unsafe_allow_html=True)

        st.caption(f"Added on {item['created_at'][:10]}")

        edit_col, delete_col = st.columns(2)

        if edit_col.button(
            "Edit",
            key=f"edit_{item['id']}",
            use_container_width=True,
        ):
            st.session_state.editing_id = item["id"]
            st.rerun()

        if delete_col.button(
            "Delete",
            key=f"delete_{item['id']}",
            use_container_width=True,
        ):
            response = api_call("DELETE", f"/knowledge/{item['id']}")

            if response and response.status_code == 204:
                st.rerun()

            elif response:
                api_error(response, "Could not delete the entry.")

        if st.session_state.editing_id == item["id"]:
            st.divider()
            st.markdown("##### Edit Entry")

            with st.form(f"edit_entry_{item['id']}"):
                title = st.text_input("Title", value=item["title"])
                description = st.text_area(
                    "Description",
                    value=item.get("description") or "",
                    height=80,
                )
                content = st.text_area(
                    "Content / URL",
                    value=item.get("content") or "",
                    height=140,
                )
                tags = st.text_input(
                    "Tags",
                    value=", ".join(item.get("tags", [])),
                )

                save, cancel = st.columns(2)
                save_clicked = save.form_submit_button(
                    "Save",
                    type="primary",
                    use_container_width=True,
                )
                cancel_clicked = cancel.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )

            if cancel_clicked:
                st.session_state.editing_id = None
                st.rerun()

            if save_clicked:
                response = api_call(
                    "PUT",
                    f"/knowledge/{item['id']}",
                    json={
                        "title": title.strip(),
                        "description": description.strip() or None,
                        "content": content.strip() or None,
                        "tags": [
                            tag.strip()
                            for tag in tags.split(",")
                            if tag.strip()
                        ],
                    },
                )

                if response and response.status_code == 200:
                    st.session_state.editing_id = None
                    st.rerun()

                elif response:
                    api_error(response, "Could not update the entry.")


# =========================================================
# VAULT PAGE
# =========================================================
def vault_page(knowledge_items, todos):
    st.markdown("""
    <div class="page-heading">
        <h1>My Vault</h1>
        <p>Everything you want to remember, all in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    completed = sum(todo["completed"] for todo in todos)

    stat_one, stat_two, stat_three = st.columns(3)

    stat_one.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">Knowledge entries</div>'
        f'<div class="stat-value">{len(knowledge_items)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    stat_two.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">Total tasks</div>'
        f'<div class="stat-value">{len(todos)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    stat_three.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-label">Completed tasks</div>'
        f'<div class="stat-value">{completed}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    search_col, filter_col = st.columns([3, 1])

    search = search_col.text_input(
        "Search",
        placeholder="Search your knowledge...",
        label_visibility="collapsed",
    ).lower()

    entry_types = ["ALL"] + sorted(
        {item.get("type", "TEXT") for item in knowledge_items}
    )

    selected_type = filter_col.selectbox(
        "Type",
        entry_types,
        label_visibility="collapsed",
    )

    filtered_items = []

    for item in knowledge_items:
        searchable = " ".join([
            item.get("title", ""),
            item.get("description") or "",
            item.get("content") or "",
            " ".join(item.get("tags", [])),
        ]).lower()

        search_match = search in searchable
        type_match = (
            selected_type == "ALL"
            or item.get("type") == selected_type
        )

        if search_match and type_match:
            filtered_items.append(item)

    if not filtered_items:
        st.markdown("""
        <div class="empty-state">
            <h3>No knowledge entries found</h3>
            <p>Add your first note, link, image, or PDF from the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    first_column, second_column = st.columns(2)

    for index, item in enumerate(filtered_items):
        with first_column if index % 2 == 0 else second_column:
            knowledge_card(item)


# =========================================================
# TASK PAGE
# =========================================================
def tasks_page(todos):
    st.markdown("""
    <div class="page-heading">
        <h1>My Tasks</h1>
        <p>Keep track of what matters and complete it step by step.</p>
    </div>
    """, unsafe_allow_html=True)

    if not todos:
        st.markdown("""
        <div class="empty-state">
            <h3>No tasks yet</h3>
            <p>Add a task from the sidebar and it will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    show_completed = st.toggle("Show completed tasks", value=True)

    for todo in todos:
        if todo["completed"] and not show_completed:
            continue

        with st.container(border=True):
            check_col, text_col, delete_col = st.columns([0.08, 0.82, 0.10])

            completed = check_col.checkbox(
                "Complete",
                value=todo["completed"],
                key=f"task_{todo['id']}",
                label_visibility="collapsed",
            )

            if completed != todo["completed"]:
                response = api_call(
                    "PUT",
                    f"/todos/{todo['id']}",
                    json={"completed": completed},
                )

                if response and response.status_code == 200:
                    st.rerun()

            css_class = "todo-completed" if todo["completed"] else "todo-active"

            text_col.markdown(
                f'<div class="{css_class}">{html.escape(todo["title"])}</div>',
                unsafe_allow_html=True,
            )

            if todo.get("description"):
                text_col.caption(todo["description"])

            if delete_col.button(
                "✕",
                key=f"remove_task_{todo['id']}",
                use_container_width=True,
            ):
                response = api_call("DELETE", f"/todos/{todo['id']}")

                if response and response.status_code == 204:
                    st.rerun()


# =========================================================
# DASHBOARD
# =========================================================
def dashboard():
    sidebar()

    knowledge_response = api_call("GET", "/knowledge")
    todo_response = api_call("GET", "/todos")

    if not knowledge_response or not todo_response:
        st.warning("The vault could not be loaded.")
        return

    if knowledge_response.status_code == 401:
        st.warning("Your login session expired. Please sign in again.")
        logout()
        return

    if knowledge_response.status_code != 200:
        api_error(knowledge_response, "Could not load your knowledge.")
        return

    if todo_response.status_code != 200:
        api_error(todo_response, "Could not load your tasks.")
        return

    knowledge_items = knowledge_response.json()
    todos = todo_response.json()

    if st.session_state.page == "Tasks":
        tasks_page(todos)
    else:
        vault_page(knowledge_items, todos)


# =========================================================
# APP START
# =========================================================
if st.session_state.access_token:
    dashboard()
else:
    login_page()
