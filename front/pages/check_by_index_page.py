import streamlit as st
import os
import requests



# no_sidebar_style = """
#     <style>
#         div[data-testid="stSidebarNav"] {display: none;}
#     </style>
# """
# st.markdown(no_sidebar_style, unsafe_allow_html=True)
def check_by_index_page():
    st.title("Проверить видео по индексу")

    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

    uploaded_file = st.file_uploader(
        "Загрузите видеозапись",
        type=["mp4", "avi", "mov"],
        help='Подробная инфа / инструкция'
    )

    if uploaded_file is not None:
        if st.button("Добавить"):
            with st.spinner("Загрузка видео..."):
                # Реальная загрузка файла
                # Загружаем файл на сервер или выполняем другие действия
                video_bytes = uploaded_file.read()

                def send_request() -> requests.Response:
                    files = {
                        "video": video_bytes,
                    }
                    data = {
                        "name": uploaded_file.name,
                        "index": "false"
                    }
                    response = requests.post(f"{os.getenv('VIDEO_SERVICE_URL')}/video", files=files, data=data)
                    return response

                send_request()
                # Здесь вы можете сохранить видео на сервер или выполнить другие необходимые действия
                st.success("Видео добавлено в очередь на проверку")
            if st.button("OK"):
                st.rerun()

if __name__=="__main__":
    check_by_index_page()
