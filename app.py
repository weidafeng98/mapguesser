import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import random
import os

MAX_QUESTIONS = 10  # 设置最大题目数

def styled_write(message, color="black", font_size="16px"):
    st.markdown(f"<span style='color: {color}; font-size: {font_size};'>{message}</span>", unsafe_allow_html=True)

# Load the list of country names
@st.cache_data
def load_country_names():
    with open('Country_name_list.txt', 'r') as file:
        country_names = file.read().splitlines()
    return country_names

@st.cache_data
def load_country_name_mappings():
    with open('Country_name_list.txt', 'r') as file:
        english_names = file.read().splitlines()
    with open('Chinese_name.txt', 'r') as file:
        chinese_names = file.read().splitlines()

    # 假设两个文件中的国家名称是一一对应的
    return dict(zip(english_names, chinese_names))

def initialize_state():
    if 'score' not in st.session_state:
        st.session_state['score'] = 0
    if 'question_count' not in st.session_state:
        st.session_state['question_count'] = 0

    if st.session_state['question_count'] < MAX_QUESTIONS:
        # 加载国家名称映射
        name_mappings = load_country_name_mappings()
        
        country_names = load_country_names()
        correct_country_name = random.choice(country_names)
        correct_country_chinese_name = name_mappings[correct_country_name]  # 获取中文名称
        incorrect_countries = random.sample([name for name in country_names if name != correct_country_name], 3)
        incorrect_countries_chinese = [name_mappings[name] for name in incorrect_countries]  # 转换为中文名称
        answers = [correct_country_chinese_name] + incorrect_countries_chinese
        random.shuffle(answers)
        
        st.session_state['correct_country_name'] = correct_country_name
        st.session_state['correct_country_chinese_name'] = correct_country_chinese_name  # 存储中文正确答案
        st.session_state['answers'] = answers
        st.session_state['answered'] = False

def check_answer(answer):
    st.session_state['selected_answer'] = answer
    if answer == st.session_state['correct_country_chinese_name']:
        st.session_state['answer_feedback'] = f"正确！这确实是 {st.session_state['correct_country_chinese_name']}。"
        st.session_state['score'] += 1
    else:
        st.session_state['answer_feedback'] = f"错误。这是 {st.session_state['correct_country_chinese_name']} 的地图。"
    st.session_state['answered'] = True
    st.session_state['question_count'] += 1

    # 如果没有更多的问题，显示结束游戏信息和分数
    if st.session_state['question_count'] >= MAX_QUESTIONS:
        st.balloons()
        st.write(f"游戏结束！你的最终得分是：{st.session_state['score']} / {MAX_QUESTIONS}")
    st.experimental_rerun()


def next_question():
    if st.session_state['question_count'] < MAX_QUESTIONS:
        initialize_state()
        st.experimental_rerun()

# Initialize session state
if 'initialized' not in st.session_state:
    initialize_state()
    st.session_state['initialized'] = True

st.title('Map Guesser V0.2')

# 在标题下方显示当前题目数和总题目数
st.header(f"Finished Question {st.session_state['question_count']} of {MAX_QUESTIONS}")

# Plot the country map
def plot_country_map():
    # 路径应指向你保存图片的文件夹
    image_dir = 'svg'
    image_path = os.path.join(image_dir, st.session_state['correct_country_name'] + '.svg')

    # 如果图片已经存在，则显示图片
    if os.path.isfile(image_path):
        st.image(image_path)
    else:
        # 图片不存在，生成图片并保存
        shp_file_path = 'ne_10m_admin_0_map_units.shp'
        gdf = gpd.read_file(shp_file_path)
        country_gdf = gdf[gdf['NAME'].eq(st.session_state['correct_country_name'])]
        fig, ax = plt.subplots(figsize=(3, 1.5))
        country_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')
        ax.axis('off')

        # 保存生成的图片
        fig.savefig(image_path, format='svg', bbox_inches='tight')
        plt.close(fig)  # 关闭图形，避免内存泄露

        # 然后显示刚保存的图片
        st.image(image_path)

if st.session_state['question_count'] < MAX_QUESTIONS:
    plot_country_map()

# 用户选择答案的按钮
if st.session_state['question_count'] < MAX_QUESTIONS and not st.session_state['answered']:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(st.session_state['answers'][0], key='btn1'):
            check_answer(st.session_state['answers'][0])
    with col2:
        if st.button(st.session_state['answers'][1], key='btn2'):
            check_answer(st.session_state['answers'][1])
    with col3:
        if st.button(st.session_state['answers'][2], key='btn3'):
            check_answer(st.session_state['answers'][2])
    with col4:
        if st.button(st.session_state['answers'][3], key='btn4'):
            check_answer(st.session_state['answers'][3])

# 如果用户已经回答了当前问题，则不显示选项按钮
if st.session_state['answered']:
    # 这里可以添加显示答案的逻辑或其他内容
    # 例如：st.info("请等待下一题或查看解释。")
    pass

# 下一题按钮
if st.session_state['answered']:
    # 在下一题按钮前显示答案反馈信息
    st.write(st.session_state['answer_feedback'])
    
    if st.session_state['question_count'] < MAX_QUESTIONS:
        next_question_button = st.button('Next Question')
        if next_question_button:
            next_question()

# 游戏结束信息
if st.session_state['question_count'] >= MAX_QUESTIONS:
    st.balloons()
    st.header(f"Game over! Your final score is: {st.session_state['score']} / {MAX_QUESTIONS}")
