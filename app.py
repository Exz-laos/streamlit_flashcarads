import streamlit as st
from gtts import gTTS
import io
import base64
import random
import time
from data import flashcard_data, thai_translations, thai_quotes  # NEW: import thai_quotes

# --- Functions ---

@st.cache_data
def generate_audio(text):
    """Generates audio and returns it as a Base64 encoded Data URI"""
    audio_bytes = io.BytesIO()
    try:
        tts = gTTS(text=text, lang='ru', slow=False)
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
        audio_uri = f"data:audio/mp3;base64,{b64}"
        return audio_uri
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None


def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'card_keys' not in st.session_state:
        st.session_state.card_keys = list(flashcard_data.keys())

    if 'total_cards' not in st.session_state:
        st.session_state.total_cards = len(st.session_state.card_keys)

    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    if 'is_flipped' not in st.session_state:
        st.session_state.is_flipped = False

    if 'card_status' not in st.session_state:
        st.session_state.card_status = {key: "Не просмотрено" for key in st.session_state.card_keys}

    if 'audio_to_play' not in st.session_state:
        st.session_state.audio_to_play = None

    if 'shuffle_on' not in st.session_state:
        st.session_state.shuffle_on = False

    # NEW: Timer for quotes & cats
    if 'last_popup_time' not in st.session_state:
        st.session_state.last_popup_time = time.time()


def apply_range(start_num, end_num):
    """Filters cards based on the selected range and shuffles if requested."""
    start_idx = start_num - 1
    end_idx = end_num

    all_keys = list(flashcard_data.keys())
    if 0 <= start_idx < end_idx <= len(all_keys):
        st.session_state.card_keys = all_keys[start_idx:end_idx]

        if st.session_state.shuffle_on:
            random.shuffle(st.session_state.card_keys)

        st.session_state.total_cards = len(st.session_state.card_keys)
        st.session_state.current_index = 0
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None
    else:
        st.sidebar.error("Неверный диапазон. Пожалуйста, выберите корректные номера.")


def next_card():
    if st.session_state.current_index < st.session_state.total_cards - 1:
        st.session_state.current_index += 1
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None


def prev_card():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None


def mark_status(status):
    current_key = st.session_state.card_keys[st.session_state.current_index]
    st.session_state.card_status[current_key] = status


# --- UI Layout ---

st.set_page_config(page_title="Интерактивные Аудио-Карточки", layout="wide", page_icon="🗂️")
initialize_session_state()

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Настройки")

    st.subheader("Диапазон карточек")
    total_cards_overall = len(flashcard_data)
    start_num = st.number_input("Начало", min_value=1, max_value=total_cards_overall, value=1, step=1)
    end_num = st.number_input("Конец", min_value=1, max_value=total_cards_overall, value=10, step=1)

    st.toggle("Перемешать карточки", key="shuffle_on", help="Активируйте, чтобы перемешать карточки в выбранном диапазоне.")

    if st.button("Применить диапазон", use_container_width=True):
        apply_range(start_num, end_num)
        st.rerun()

    st.header("📊 Прогресс")
    remembered_count = list(st.session_state.card_status.values()).count("Запомнено")
    repeat_count = list(st.session_state.card_status.values()).count("Нужно повторить")

    st.metric(label="✅ Запомнено", value=f"{remembered_count} / {st.session_state.total_cards}")
    st.metric(label="🔄 Повторить", value=f"{repeat_count} / {st.session_state.total_cards}")

    if st.button("Сбросить прогресс", use_container_width=True):
        st.session_state.card_status = {key: "Не просмотрено" for key in list(flashcard_data.keys())}
        st.rerun()

# --- Main Flashcard Area ---
st.title("🗂️ Интерактивные Аудио-Карточки по Истории")

# --- NEW FEATURE: Thai quote + cat every 2 minutes ---
current_time = time.time()
if current_time - st.session_state.last_popup_time >= 3:  # 120 sec = 2 minutes
    quote = random.choice(thai_quotes)

    # ✅ Popup stays 5 sec
    st.toast(f"🐱💡 : {quote}", icon="😺", duration=5)

    # ✅ Transparent cute cat gifs
    cat_gifs = [
        "https://media.tenor.com/nsGNQy4ZMjEAAAAi/gato-guitarra.gif", # guitar cat
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXN0d25hcW52dzdpZmN0eWFzMmxsNjhvaW5jcXU2Y3A2dG5nOXZmdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/fA7OjY4F5YwDBwFqkh/giphy.gif",
        "https://media.tenor.com/5aAZH40lwxgAAAAm/slowmo-cat-twerk.webp",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3pzeXB0ZnY5eDBoejBiMDBoNWQzdms3eGoyb2kxY3EwenlvZHI3ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/eLv7gJpxqiQtbNNQUe/giphy.gif",
        "https://media1.tenor.com/m/XBwe7zO46NQAAAAd/jive-cat-mega64-cat.gif",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXE2ZzBheDI5aTIyNDRqYmdvOThmZHV4aWJ1NDNldXN0eno4NzF1YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/W0VuY0dTxH9L6vLUJ2/giphy.gif",
        "https://media.tenor.com/9zmtHZ0tIjkAAAAi/nyancat-rainbow-cat.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2dxaG05emJoa3k1bmswbjBoZnpkdzZzYWU5ZjRhcnljbXhpdHlrMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/i4ldQWj8VNnbeGDqop/giphy.gif",
        "https://media.tenor.com/YEwxWExn80kAAAAi/cat-cute.gif",
        "https://media1.tenor.com/m/w4GOERle_1IAAAAC/cat.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTl6MWQ0aGJnczYxMXd5MnJiYnM1MWMwZTYzamZqMnYweTl3MzFsNyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/5ztVM85oObF12bA27A/200w.webp",
        "https://media.tenor.com/_nR-1FLTOAwAAAAi/pixel-cat.gif",
        "https://media.tenor.com/29Jgk2DXsm0AAAAi/mad-cat.gif",
        "https://media.tenor.com/IYdap55unFgAAAAi/nod-cat-nod.gif",
        
        
    ]
    cat_choice = random.choice(cat_gifs)

    # ✅ Show smaller cat with slower movement
    st.markdown(
        f"""
        <div style="position:relative; height:120px; overflow:hidden;">
            <img src="{cat_choice}"
                 style="position:absolute; left:0; bottom:0; height:60px; 
                        animation: run 20s linear infinite;">
        </div>
        <style>
        @keyframes run {{
            0% {{ left: -150px; }}
            100% {{ left: 100%; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.session_state.last_popup_time = current_time

# --- Flashcard Logic ---
if not st.session_state.card_keys:
    st.warning("Нет карточек для отображения. Пожалуйста, выберите и примените диапазон в боковой панели.")
else:
    current_key = st.session_state.card_keys[st.session_state.current_index]
    current_answer = flashcard_data[current_key]
    current_status = st.session_state.card_status[current_key]
    thai_translation = thai_translations.get(current_key, {})

    progress_value = (st.session_state.current_index + 1) / st.session_state.total_cards
    st.progress(progress_value, text=f"Карточка {st.session_state.current_index + 1} из {st.session_state.total_cards}")

    card_placeholder = st.empty()

    if not st.session_state.is_flipped:
        with card_placeholder.container():
            st.markdown(f"**Статус:** {current_status}")
            with st.container(height=300, border=True):
                st.subheader("Вопрос:")
                st.write(current_key)

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("Перевернуть на ответ ↩️", use_container_width=True):
                    st.session_state.is_flipped = True
                    st.session_state.audio_to_play = None
                    st.rerun()
            with col2:
                if st.button("▶️", use_container_width=True, help="Озвучить вопрос"):
                    with st.spinner("Генерация аудио..."):
                        audio_uri = generate_audio(current_key)
                    st.session_state.audio_to_play = audio_uri
                    if not audio_uri:
                        st.toast("Ошибка генерации аудио!", icon="🚨")
            with col3:
                if st.button("🇹🇭", use_container_width=True, help="Помощь (Thai)"):
                    if "question" in thai_translation:
                        with st.expander("Перевод на тайский", expanded=True):
                            st.info(thai_translation["question"])

            if st.session_state.audio_to_play:
                st.audio(st.session_state.audio_to_play)

    else:
        with card_placeholder.container():
            st.markdown(f"**Статус:** {current_status}")
            with st.container(height=300, border=True):
                st.subheader("Ответ:")
                st.write(current_answer)

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("Перевернуть на вопрос ↪️", use_container_width=True):
                    st.session_state.is_flipped = False
                    st.session_state.audio_to_play = None
                    st.rerun()
            with col2:
                if st.button("▶️", use_container_width=True, help="Озвучить ответ"):
                    with st.spinner("Генерация аудио..."):
                        audio_uri = generate_audio(current_answer)
                    st.session_state.audio_to_play = audio_uri
                    if not audio_uri:
                        st.toast("Ошибка генерации аудио!", icon="🚨")
            with col3:
                if st.button("🇹🇭", use_container_width=True, help="Помощь (Thai)"):
                    if "answer" in thai_translation:
                        with st.expander("Перевод на тайский", expanded=True):
                            st.info(thai_translation["answer"])

            if st.session_state.audio_to_play:
                st.audio(st.session_state.audio_to_play)

    st.divider()

    # --- Navigation and Status Buttons ---
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        st.button("⬅️ Предыдущая", on_click=prev_card, use_container_width=True,
                  disabled=(st.session_state.current_index == 0))
    with nav_col2:
        st.button("Следующая ➡️", on_click=next_card, use_container_width=True,
                  disabled=(st.session_state.current_index == st.session_state.total_cards - 1))

    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.button("✅ Я это знаю!", on_click=mark_status, args=("Запомнено",), use_container_width=True)
    with status_col2:
        st.button("🔄 Нужно повторить", on_click=mark_status, args=("Нужно повторить",), use_container_width=True)
