import streamlit as st
from gtts import gTTS
import io
from data import flashcard_data, thai_translations # Import data from the external file

# --- Functions ---

@st.cache_data
def generate_audio(text):
    """Generates audio from text and returns it as a byte object."""
    audio_bytes = io.BytesIO()
    try:
        tts = gTTS(text=text, lang='ru', slow=False)
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        # Log the exception for debugging if running locally
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
    
    # NEW: State to hold the audio player data
    if 'audio_to_play' not in st.session_state:
        st.session_state.audio_to_play = None

def apply_range(start_num, end_num):
    """Filters cards based on the selected range."""
    start_idx = start_num - 1
    end_idx = end_num
    
    all_keys = list(flashcard_data.keys())
    if 0 <= start_idx < end_idx <= len(all_keys):
        st.session_state.card_keys = all_keys[start_idx:end_idx]
        st.session_state.total_cards = len(st.session_state.card_keys)
        st.session_state.current_index = 0
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None # Reset audio on range change
    else:
        st.sidebar.error("Неверный диапазон. Пожалуйста, выберите корректные номера.")

def next_card():
    """Moves to the next card and resets state."""
    if st.session_state.current_index < st.session_state.total_cards - 1:
        st.session_state.current_index += 1
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None # Reset audio player

def prev_card():
    """Moves to the previous card and resets state."""
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.is_flipped = False
        st.session_state.audio_to_play = None # Reset audio player

def mark_status(status):
    """Marks the current card with a status."""
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
    thai_translation = thai_translations.get(current_key, {})

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
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("Перевернуть на ответ ↩️", use_container_width=True):
                    st.session_state.is_flipped = True
                    st.session_state.audio_to_play = None # Reset audio
                    st.rerun()
            with col2:
                if st.button("▶️", use_container_width=True, help="Озвучить вопрос"):
                    with st.spinner("Генерация аудио..."):
                        audio_file = generate_audio(current_key)
                        if audio_file:
                            st.session_state.audio_to_play = audio_file
                        else:
                            st.session_state.audio_to_play = None
                            st.toast("Ошибка генерации аудио!", icon="🚨")
            with col3:
                # Thai translation logic remains the same
                if st.button("🇹🇭", use_container_width=True, help="Помощь (Thai)"):
                    if "question" in thai_translation:
                        with st.expander("Перевод на тайский", expanded=True):
                           st.info(thai_translation["question"])
            
            # NEW: Display the audio player if it exists in the state
            if st.session_state.audio_to_play:
                st.audio(st.session_state.audio_to_play, format='audio/mp3')

    else:
        # --- BACK OF THE CARD ---
        with card_placeholder.container():
            st.markdown(f"**Статус:** {current_status}")
            with st.container(height=300, border=True):
                st.subheader("Ответ:")
                st.write(current_answer)
                
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("Перевернуть на вопрос ↪️", use_container_width=True):
                    st.session_state.is_flipped = False
                    st.session_state.audio_to_play = None # Reset audio
                    st.rerun()
            with col2:
                if st.button("▶️", use_container_width=True, help="Озвучить ответ"):
                    with st.spinner("Генерация аудио..."):
                        audio_file = generate_audio(current_answer)
                        if audio_file:
                            st.session_state.audio_to_play = audio_file
                        else:
                            st.session_state.audio_to_play = None
                            st.toast("Ошибка генерации аудио!", icon="🚨")
            with col3:
                # Thai translation logic remains the same
                if st.button("🇹🇭", use_container_width=True, help="Помощь (Thai)"):
                     if "answer" in thai_translation:
                        with st.expander("Перевод на тайский", expanded=True):
                           st.info(thai_translation["answer"])

            # NEW: Display the audio player if it exists in the state
            if st.session_state.audio_to_play:
                st.audio(st.session_state.audio_to_play, format='audio/mp3')

    st.divider()

    # --- Navigation and Status Buttons ---
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        st.button("⬅️ Предыдущая", on_click=prev_card, use_container_width=True, disabled=(st.session_state.current_index == 0))
    with nav_col2:
        st.button("Следующая ➡️", on_click=next_card, use_container_width=True, disabled=(st.session_state.current_index == st.session_state.total_cards - 1))
        
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.button("✅ Я это знаю!", on_click=mark_status, args=("Запомнено",), use_container_width=True)
    with status_col2:
        st.button("🔄 Нужно повторить", on_click=mark_status, args=("Нужно повторить",), use_container_width=True)

