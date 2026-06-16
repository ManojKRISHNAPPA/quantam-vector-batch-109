import streamlit as st
from database import *

create_tables()

st.set_page_config(
    page_title="DevOps Community",
    page_icon="🚀",
    layout="wide"
)

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ----------------------------
# Registration Page
# ----------------------------
def registration_page():

    st.title("📝 Register")

    username = st.text_input("Username")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        if register_user(username, password):

            st.success(
                "Registration Successful!"
            )

            st.info(
                "Please login now."
            )

            st.session_state.page = "login"

            st.rerun()

        else:
            st.error(
                "Username already exists"
            )


# ----------------------------
# Login Page
# ----------------------------
def login_page():

    st.title("🔐 Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = login_user(
            username,
            password
        )

        if user:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.rerun()

        else:
            st.error(
                "Invalid Credentials"
            )


# ----------------------------
# Dashboard
# ----------------------------
def dashboard():

    st.title(
        f"🚀 Welcome {st.session_state.username}"
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Articles",
            "Create Post",
            "Community Posts"
        ]
    )

    # ------------------
    # Articles
    # ------------------
    with tab1:

        st.header("DevOps")

        st.markdown("""
### What is DevOps?

DevOps combines Development and Operations
to improve software delivery speed and reliability.

Topics:
- CI/CD
- Docker
- Kubernetes
- Terraform
- Monitoring
- SRE
        """)

        st.header("Machine Learning")

        st.markdown("""
### What is Machine Learning?

Machine Learning enables systems
to learn patterns from data.

Types:
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
        """)

        st.header("MCP")

        st.markdown("""
### What is MCP?

Model Context Protocol (MCP) allows
LLMs to interact with tools,
databases, APIs, and external systems.

Benefits:
- Tool Calling
- Context Sharing
- AI Agents
- Workflow Automation
        """)

    # ------------------
    # Create Post
    # ------------------
    with tab2:

        st.header("Create Post")

        title = st.text_input(
            "Post Title"
        )

        content = st.text_area(
            "Post Content"
        )

        if st.button("Publish Post"):

            create_post(
                st.session_state.username,
                title,
                content
            )

            st.success(
                "Post Published Successfully"
            )

    # ------------------
    # Community Posts
    # ------------------
    with tab3:

        st.header("Community Posts")

        posts = get_posts()

        if not posts:
            st.info(
                "No Posts Available"
            )

        for username, title, content in posts:

            with st.container():

                st.subheader(title)

                st.write(
                    f"✍️ By: {username}"
                )

                st.write(content)

                st.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        st.rerun()


# ----------------------------
# Main
# ----------------------------

if st.session_state.logged_in:
    dashboard()

else:

    page = st.sidebar.radio(
        "Navigation",
        ["Login", "Register"]
    )

    if page == "Login":
        login_page()
    else:
        registration_page()