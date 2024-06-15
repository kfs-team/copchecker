import streamlit as st


class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        import streamlit as st
        from streamlit_option_menu import option_menu

        with st.sidebar:
            app_titles = [app['title'] for app in self.apps]
            selected = option_menu(
                "Меню",
                app_titles,
                icons=["house", "upload", "search", "check2-all"],
                menu_icon="cast",
                default_index=0,
            )

        for app in self.apps:
            if app['title'] == selected:
                app['function']()
