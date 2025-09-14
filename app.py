import streamlit as st
from gtts import gTTS
import io
# Импортируем данные из нашего нового файла data.py
from data import flashcard_data, thai_translations

# --- Functions ---

@st.cache_data
def generate_audio(text, lang='ru'):
    """Генерирует аудио из текста на указанном языке."""
    audio_bytes = io.BytesIO()
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        st.error(f"Ошибка генерации аудио: {e}")
        return None

def initialize_session_state():
    """Инициализирует переменные состояния сессии."""
    if 'card_keys' not in st.session_state:
        st.session_state.card_keys = list(flashcard_data.keys())
    
    if 'total_cards' not in st.session_state:
        st.session_state.total_cards = len(st.session_state.card_keys)

    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    if 'is_flipped' not in st.session_state:
        st.session_state.is_flipped = False

    if 'card_status' not in st.session_state:
        st.session_state.card_status = {key: "Не просмотрено" for key in list(flashcard_data.keys())}

def apply_range(start_num, end_num):
    """Фильтрует карточки по заданному диапазону."""
    start_idx, end_idx = start_num - 1, end_num
    all_keys = list(flashcard_data.keys())
    if 0 <= start_idx < end_idx <= len(all_keys):
        st.session_state.card_keys = all_keys[start_idx:end_idx]
        st.session_state.total_cards = len(st.session_state.card_keys)
        st.session_state.current_index = 0
        st.session_state.is_flipped = False
    else:
        st.sidebar.error("Неверный диапазон.")

def next_card():
    if st.session_state.current_index < st.session_state.total_cards - 1:
        st.session_state.current_index += 1
        st.session_state.is_flipped = False

def prev_card():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.is_flipped = False

def mark_status(status):
    current_key = st.session_state.card_keys[st.session_state.current_index]
    st.session_state.card_status[current_key] = status

# --- UI Layout ---

st.set_page_config(page_title="Интерактивные Аудио-Карточки", layout="wide", page_icon="🗂️")
initialize_session_state()

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Настройки")
    total_cards_overall = len(flashcard_data)
    start_num = st.number_input("Начало", min_value=1, max_value=total_cards_overall, value=1, step=1)
    end_num = st.number_input("Конец", min_value=1, max_value=total_cards_overall, value=65, step=1)
    
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

if not st.session_state.card_keys:
    st.warning("Нет карточек для отображения. Пожалуйста, выберите и примените диапазон в боковой панели.")
else:
    current_key = st.session_state.card_keys[st.session_state.current_index]
    current_answer = flashcard_data[current_key]
    current_status = st.session_state.card_status[current_key]
    thai_translation = thai_translations.get(current_key, {}) # Получаем перевод

    progress_value = (st.session_state.current_index + 1) / st.session_state.total_cards
    st.progress(progress_value, text=f"Карточка {st.session_state.current_index + 1} из {st.session_state.total_cards}")

    card_placeholder = st.empty()

    if not st.session_state.is_flipped:
        # --- FRONT OF THE CARD ---
        with card_placeholder.container():
            st.markdown(f"**Статус:** {current_status}")
            with st.container(height=300, border=True):
                st.subheader("Вопрос:")
                st.write(current_key)
            
            # --- Кнопки для лицевой стороны ---
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("Перевернуть на ответ ↩️", use_container_width=True):
                    st.session_state.is_flipped = True
                    st.rerun()
            with col2:
                if st.button("▶️ Озвучить", use_container_width=True):
                    st.audio(generate_audio(current_key, 'ru'), format='audio/mp3', autoplay=True)
            with col3:
                # Кнопка помощи теперь в виде expander
                with st.expander("🇹🇭 Помощь (Thai)"):
                    st.info(thai_translation.get("question", "Перевод не найден."))

    else:
        # --- BACK OF THE CARD ---
        with card_placeholder.container():
            st.markdown(f"**Статус:** {current_status}")
            with st.container(height=300, border=True):
                st.subheader("Ответ:")
                st.write(current_answer)
                
            # --- Кнопки для обратной стороны ---
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("Перевернуть на вопрос ↪️", use_container_width=True):
                    st.session_state.is_flipped = False
                    st.rerun()
            with col2:
                if st.button("▶️ Озвучить", use_container_width=True):
                    st.audio(generate_audio(current_answer, 'ru'), format='audio/mp3', autoplay=True)
            with col3:
                with st.expander("🇹🇭 Помощь (Thai)"):
                    st.info(thai_translation.get("answer", "Перевод не найден."))
    
    st.divider()

    # --- Navigation and Status Buttons ---
    nav_col1, nav_col2 = st.columns(2)
    nav_col1.button("⬅️ Предыдущая", on_click=prev_card, use_container_width=True, disabled=(st.session_state.current_index == 0))
    nav_col2.button("Следующая ➡️", on_click=next_card, use_container_width=True, disabled=(st.session_state.current_index >= st.session_state.total_cards - 1))
        
    status_col1, status_col2 = st.columns(2)
    status_col1.button("✅ Я это знаю!", on_click=mark_status, args=("Запомнено",), use_container_width=True)
    status_col2.button("🔄 Нужно повторить", on_click=mark_status, args=("Нужно повторить",), use_container_width=True)

