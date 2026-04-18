import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

if not os.environ["GOOGLE_API_KEY"]:
    st.error("❌ Нет GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash-lite")

st.set_page_config(page_title="Multi-Agent Guide", layout="wide")

def load_css():
    if os.path.exists("style.css"):
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if "history" not in st.session_state:
    st.session_state.history = []

st.title("🌍 Adaptive Student Guide (Multi-Agent System)")

if os.path.exists("banner.jpg"):
    st.image("banner.jpg", use_container_width=True)

st.header("⚙️ Конфигурация агентов")

col1, col2 = st.columns(2)

with col1:
    analyst_role = st.text_input("Роль аналитика", "Культурный аналитик")
    analyst_goal = st.text_input("Цель аналитика", "Понять проблемы студента")

with col2:
    guide_role = st.text_input("Роль гида", "Навигатор кампуса")
    guide_goal = st.text_input("Цель гида", "Создать маршрут адаптации")

st.header("📝 Входные данные")

question = st.text_area("Запрос студента", "Как мне адаптироваться в университете?")
country = st.text_input("Страна", "Южная Корея")

req_type = st.selectbox(
    "Тип запроса",
    ["Общий", "Учёба", "Жильё", "Медицина", "Документы", "Досуг"]
)

knowledge = st.text_area(
    "Knowledge база",
    "Кампус включает общежитие, библиотеку, медцентр, деканат."
)

uploaded_file = st.file_uploader("Загрузите файл инфраструктуры (.txt)", type=["txt"])

infra_text = ""

if uploaded_file:
    infra_text = uploaded_file.read().decode("utf-8")
    st.success("Файл загружен")
elif os.path.exists("data/infrastructure.txt"):
    with open("data/infrastructure.txt", encoding="utf-8") as f:
        infra_text = f.read()

rules_text = ""
if os.path.exists("knowledge/rules.txt"):
    with open("knowledge/rules.txt", encoding="utf-8") as f:
        rules_text = f.read()

need_clarification = False

if req_type == "Общий" or len(question) < 25:
    need_clarification = True

st.header("🚀 Запуск системы")

if st.button("Сгенерировать ответ"):

    st.session_state.history.append({
        "question": question,
        "country": country,
        "type": req_type
    })

    def simple_tool_search(text):
        return f"🔎 Результаты поиска по: {text}"

    if need_clarification:
        st.warning("⚠️ Недостаточно данных — генерируется уточнение")

        clarification_prompt = f"""
Ты помощник университета.
Сгенерируй уточняющий вопрос студенту.

Запрос: {question}
Тип: {req_type}

Спроси про:
- проживание
- учебу
- медицину
- документы
- досуг
"""

        clarification = model.generate_content(clarification_prompt).text

        st.info("❓ Уточнение:")
        st.write(clarification)

    analyst_prompt = f"""
Ты {analyst_role}.

Цель: {analyst_goal}

Проанализируй студента:

Запрос: {question}
Страна: {country}
Тип: {req_type}

Knowledge:
{knowledge}

Rules:
{rules_text}

История:
{st.session_state.history}

Используй инструмент поиска:
{simple_tool_search(question)}

Определи:
- проблемы студента
- культурные сложности
- потребности
"""

    analyst_result = model.generate_content(analyst_prompt).text

    guide_prompt = f"""
Ты {guide_role}.

Цель: {guide_goal}

Используй инфраструктуру:
{infra_text}

Создай маршрут адаптации для студента:

Анализ:
{analyst_result}

Сделай:
- пошаговый маршрут
- рекомендации
- сервисы кампуса
"""

    guide_result = model.generate_content(guide_prompt).text

    final_prompt = f"""
Ты контролёр качества.

Проверь и улучши текст:

{guide_result}

Проверь:
- корректность
- культурную чувствительность
- понятность

Верни финальный гид.
"""

    final_result = model.generate_content(final_prompt).text

    st.subheader("🧑 HITL Проверка")

    decision = st.radio("Одобрить результат?", ["Да", "Нет"])

    if decision == "Да":
        st.success("✅ Финальный результат")
        st.markdown(f"<div class='card'>{final_result}</div>", unsafe_allow_html=True)
    else:
        st.error("❌ Отклонено пользователем")

    st.subheader("📊 Логика агентов")

    st.markdown("### 🧠 Аналитик")
    st.write(analyst_result)

    st.markdown("### 🧭 Гид")
    st.write(guide_result)

    st.markdown("### 🧪 Контроль")
    st.write(final_result)

st.header("📚 История запросов")

for h in st.session_state.history:
    st.markdown(
        f"<div class='card'>❓ {h['question']}<br>🌍 {h['country']}<br>📌 {h['type']}</div>",
        unsafe_allow_html=True
    )