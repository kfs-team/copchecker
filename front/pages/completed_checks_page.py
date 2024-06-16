import streamlit as st
import requests
import os
from pathlib import Path

# получить json файл с информацией





@st.cache_data(ttl=30)
def get_processing():
    # get запрос на json с основной инфой о проверках
    answer = requests.get(f"{os.getenv('VIDEO_SERVICE_URL')}/processing")
    if answer.status_code != 200:
        st.error("Не удалось получить информацию о проверках, ЖИЖА")
        return None, None, None, None, None
    answer = answer.json()
    if answer is None or len(answer) == 0:
        st.error("Не удалось получить информацию о проверках, ЖИЖА")
        return None, None, None, None, None
    video_names = [video['name'] for video in answer]
    processing_ids = [video['processing_id'] for video in answer]
    image_links = [video['thumbnail_url'] for video in answer]
    is_stolen = [video['has_copyright_violences'] for video in answer]
    intervals = [video['intervals'] for video in answer]
    return video_names, processing_ids, image_links, is_stolen, intervals


def get_video_json():
    # get запрос на джейсон с подробной инфой
    return 0

def shorten_filename(filename, max_length):
    path = Path(filename)
    stem = path.stem  # Имя файла без расширения
    suffix = path.suffix  # Расширение файла

    if len(stem) > max_length:
        half_length = (max_length - len(suffix)) // 2
        shortened_stem = stem[:half_length] + '...' + stem[-half_length:]
        shortened_name = shortened_stem + suffix
    else:
        shortened_name = filename

    return shortened_name


def completed_checks_page():
    # Заголовок страницы
    st.title("Выполненные проверки")
    video_names, processing_ids, image_links, is_stolen, intervals = get_processing()
    if video_names is None or processing_ids is None or image_links is None or is_stolen is None or intervals is None:
        return
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = [False] * len(video_names)

    elements = [
        (f"**Название:** {shorten_filename(name, 30)}\n\n**ID:** {id_}"
         f"\n\n {':red-background[**Обнаружены заимствования**]' if cond else ':green-background[**Заимствования не найдены**]'}")
        for name, id_, cond in zip(video_names, processing_ids, is_stolen)
    ]
    for i, element in enumerate(elements):
        col1, col2, col3 = st.columns([1, 7, 2.4])
        with col1:
            st.image(image_links[i], use_column_width=True)
        with col2:
            st.markdown(element)
        with col3:
            if st.button('Подробнее', key=f"button_{i}"):
                st.session_state.button_clicked[i] = not st.session_state.button_clicked[i]
        if st.session_state.button_clicked[i]:
            # здесь будет дополнительная инфа о проверке (видимо тоже из джейсонины)
            interval = intervals[i]
            st.write(interval)
            st.write(is_stolen[i])
            st.write('Подробная информация')
            get_video_json()
        st.write("---")


if __name__ == "__main__":
    completed_checks_page()
