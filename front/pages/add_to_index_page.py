import streamlit as st
import requests
import os

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

                def send_request() -> requests.Response:
                    files = {
                        "video": video_bytes,
                    }
                    data = {
                        "name": uploaded_file.name,
                        "index": "true",
                    }
                    response = requests.post(f"{os.getenv('VIDEO_SERVICE_URL')}/video", files=files, data=data)
                    return response

                response = send_request()
                if response.status_code == 200:
                    st.success("Видео добавлено в очередь на индексацию")
                else:
                    st.error(f"Ошибка: {response.text}")



if __name__=="__main__":
    add_to_index_page()
