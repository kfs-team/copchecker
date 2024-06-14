import streamlit as st

# no_sidebar_style = """
#     <style>
#         div[data-testid="stSidebarNav"] {display: none;}
#     </style>
# """
# st.markdown(no_sidebar_style, unsafe_allow_html=True)

def add_to_index_page():
    st.title("Добавить в индекс")
    uploaded_file = st.file_uploader("Загрузите видеозапись", type=["mp4", "avi", "mov"])

    if uploaded_file is not None:
        if st.button("Добавить"):
            with st.spinner("Загрузка видео..."):
                # Реальная загрузка файла
                # Загружаем файл на сервер или выполняем другие действия
                video_bytes = uploaded_file.read()
                # Здесь вы можете сохранить видео на сервер или выполнить другие необходимые действия
                st.success("Видео добавлено в очередь на индексацию")



if __name__=="__main__":
    add_to_index_page()