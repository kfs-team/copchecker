import time
from streamlit_image_coordinates import streamlit_image_coordinates
from streamlit_option_menu import option_menu
import streamlit as st
from multiapp import MultiApp
from pages import add_to_index_page
from pages import check_by_index_page
from pages import completed_checks_page
from pages import home

logo_url = 'logo.png'
st.sidebar.image(logo_url)

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

app = MultiApp()

app.add_app("Главная",home.main)
app.add_app("Добавить в индекс", add_to_index_page.add_to_index_page)
app.add_app("Проверить по индексу", check_by_index_page.check_by_index_page)
app.add_app("Выполненные проверки", completed_checks_page.completed_checks_page)

app.run()



