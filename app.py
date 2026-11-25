import os
import io
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="나의 카공 스타일 & 인생 음료 테스트",
    page_icon="☕",
    layout="centered"
)

# 스타일 커스터마이징 (따뜻한 카페 배경 + 밝은 갈색 포인트 테마 + 상단 타이틀 박스 정중앙 정렬)
st.markdown("""
    <style>
    .main, .stApp {
        background-color: #FAF6F0;
    }
    .stRadio > label {
        font-weight: bold;
        font-size: 1.05rem;
        color: #3E2723;
    }
    /* 상단 제목 및 설명 모서리 둥근 박스 (강제 중앙 정렬 적용) */
    .title-box {
        background-color: #FFFDF9;
        border: 2px solid #D7CCC8;
        border-radius: 18px;
        padding: 28px 24px;
        margin-bottom: 22px;
        text-align: center !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(93, 64, 55, 0.06);
    }
    .title-box h1 {
        color: #3E2723;
        font-size: 1.85rem;
        margin: 0 0 12px 0;
        font-weight: 800;
        text-align: center !important;
        width: 100%;
    }
    .title-box p {
        color: #5D4037;
        font-size: 1.05rem;
        margin: 0;
        line-height: 1.5;
        text-align: center !important;
        width: 100%;
    }
    /* 진행률 바 밝은 갈색 변경 */
    div[data-testid="stProgress"] > div > div > div > div {
        background-color: #A1887F !important;
    }
    /* 라디오 버튼 선택 색상 밝은 갈색 변경 */
    div[data-testid="stRadio"] input[type="radio"]:checked + div {
        background-color: #A1887F !important;
        border-color: #A1887F !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        border-color: #A1887F !important;
    }
    /* Primary 버튼 (결과 확인하기) 밝은 갈색 변경 */
    button[kind="primary"] {
        background-color: #A1887F !important;
        border-color: #A1887F !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #8D6E63 !important;
        border-color: #8D6E63 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 16가지 결과 유형 데이터 정의
RESULTS = {
    "BHQM": {
        "name": "고독한 새벽의 사색가",
        "drink": "아이스 아메리카노",
        "env": "구석진 1인 바 테이블, 조용한 개인 로스터리 카페",
        "desc": "4시간 이상 미동도 없이 몰입하는 진성 카공족입니다. 깔끔하고 쌉싸름한 커피 한 잔과 정적 속에서 최고의 집중력을 발휘합니다."
    },
    "BHQF": {
        "name": "냉철한 효율 추구자",
        "drink": "에스프레소 더블샷",
        "env": "백색소음만 흐르는 스터디형 카페의 벽면 좌석",
        "desc": "짧은 시간 안에 할 일을 완벽히 끝내고 깔끔하게 일어나는 타입입니다. 불필요한 군더더기 없이 확실한 카페인 각성을 선호합니다."
    },
    "BHVM": {
        "name": "노트북 앞의 자유로운 노마드",
        "drink": "아이스 콜드브루",
        "env": "적당한 활기와 콘센트가 넉넉한 대형 프랜차이즈 매장",
        "desc": "적당한 백색소음 속에서 하루 종일 작업해도 지치지 않는 스타일입니다. 깔끔한 콜드브루와 함께 긴 호흡으로 작업을 이어갑니다."
    },
    "BHVF": {
        "name": "도심 속 스파크 워커",
        "drink": "플랫화이트",
        "env": "채광 좋은 창가 자리, 활기찬 도심 속 테라스형 카페",
        "desc": "빠른 카페인 수혈로 1~2시간 만에 아이디어를 폭발시키는 타입입니다. 활기찬 공간의 에너지를 받아 단기 집중력을 극대화합니다."
    },
    "BLQM": {
        "name": "고요한 서재의 탐구자",
        "drink": "따뜻한 루이보스 티",
        "env": "한적한 동네 북카페의 넓은 원목 테이블",
        "desc": "카페인 부담 없이 장시간 독서나 논문·자료 정리에 몰두하는 학구파입니다. 은은한 허브티와 함께 차분하게 생각의 깊이를 더합니다."
    },
    "BLQF": {
        "name": "미니멀리즘 산책자",
        "drink": "따뜻한 페퍼민트 티",
        "env": "조용한 골목 안쪽의 아담한 티 하우스",
        "desc": "가벼운 마음으로 들러 1~2시간 생각을 정리하고 리프레시하는 타입입니다. 상쾌한 민트 향과 함께 머릿속을 맑게 비워냅니다."
    },
    "BLVM": {
        "name": "여유로운 관찰자",
        "drink": "디카페인 카페라떼",
        "env": "통유리창 너머 거리가 보이는 감성 카페",
        "desc": "적당한 사람 구경과 함께 느긋하게 자기계발이나 글쓰기를 즐기는 스타일입니다. 카페인 걱정 없이 부드러운 라떼를 즐기며 오래 머무릅니다."
    },
    "BLVF": {
        "name": "산뜻한 리프레시 메이커",
        "drink": "아이스 얼그레이 티",
        "env": "밝고 캐주얼한 분위기의 브런치 겸용 카페",
        "desc": "무겁지 않은 분위기에서 가볍게 플래너를 정리하거나 할 일을 체크하는 타입입니다. 향긋한 홍차 한 잔으로 기분 좋은 에너지를 얻습니다."
    },
    "SHQM": {
        "name": "은밀한 당충전 전략가",
        "drink": "아이스 돌체 라떼",
        "env": "칸막이가 있거나 프라이빗한 좌석이 있는 조용한 카페",
        "desc": "조용한 공간에서 달콤한 카페인 수혈로 장기전을 버텨내는 전략가입니다. 연유의 진한 단맛이 지치는 뇌에 꾸준한 연료를 공급해 줍니다."
    },
    "SHQF": {
        "name": "조용한 벼락치기 승부사",
        "drink": "아이스 바닐라 라떼",
        "env": "소음이 차단된 1인 좌석 위주의 카공 친화 카페",
        "desc": "시험 직전이나 마감 임박 시 조용히 초인적인 집중력을 발휘하는 타입입니다. 달콤한 바닐라 라떼 한 잔으로 단기간에 폭발적인 효율을 냅니다."
    },
    "SHVM": {
        "name": "에너제틱 멀티플레이어",
        "drink": "아이스 카페 모카",
        "env": "넓은 테이블과 음악이 흐르는 복층형 대형 카페",
        "desc": "달달한 음료와 함께 팀플, 과제, 자료 조사를 지치지 않고 해내는 만능형입니다. 활기찬 분위기와 초콜릿의 달콤함이 시너지를 일으킵니다."
    },
    "SHVF": {
        "name": "벼락치기 도파민 불도저",
        "drink": "카라멜 마키아또",
        "env": "활기차고 트렌디한 역세권 대형 카페 바 테이블",
        "desc": "짧은 시간 동안 당과 카페인을 풀충전해 무서운 속도로 끝내는 타입입니다. 시끌벅적한 에너지 속에서 오히려 집중력이 최고조에 달합니다."
    },
    "SLQM": {
        "name": "포근한 아지트 수집가",
        "drink": "따뜻한 고구마 라떼",
        "env": "아늑한 조명과 푹신한 의자가 있는 동네 아지트 카페",
        "desc": "집처럼 편안하고 조용한 공간에서 나만의 속도로 진득하게 작업하는 타입입니다. 든든하고 포근한 음료와 함께 느긋하게 목표를 달성합니다."
    },
    "SLQF": {
        "name": "달콤한 휴식의 사색가",
        "drink": "마시멜로 핫초코",
        "env": "조용한 주택가 골목의 작은 디저트 카페",
        "desc": "공부도 중요하지만 달콤한 음료 한 잔으로 소확행을 챙기는 힐링파입니다. 조용한 공간에서 잠깐의 달콤한 몰입을 즐깁니다."
    },
    "SLVM": {
        "name": "감성 충만 크리에이터",
        "drink": "아이스 말차 라떼",
        "env": "인테리어가 감각적이고 채광이 좋은 복합문화공간 카페",
        "desc": "딱딱한 암기보다는 디자인, 기획, 아이디어 스케치에 최적화된 타입입니다. 감각적인 공간에서 영감을 얻으며 오랜 시간 작업을 즐깁니다."
    },
    "SLVF": {
        "name": "통통 튀는 아이디어 뱅크",
        "drink": "아이스 자몽 에이드",
        "env": "경쾌한 분위기와 밝은 톤의 캐주얼 카페",
        "desc": "상큼달달한 음료로 기분을 업시키고 짧은 시간 반짝이는 영감을 얻는 스타일입니다. 톡 쏘는 탄산처럼 빠르고 경쾌하게 할 일을 해치웁니다."
    }
}

# 3. 12개 질문 문항 데이터
QUESTIONS = [
    {
        "q": "Q1. 카페에 들어가 메뉴판을 볼 때, 가장 먼저 눈이 가는 쪽은?",
        "options": [
            "원두의 산미나 고소함, 깔끔한 끝맛이 느껴지는 메뉴",
            "크림, 시럽, 초콜릿, 과일청 등 기분 좋아지는 달콤한 메뉴"
        ],
        "types": ["B", "S"]
    },
    {
        "q": "Q2. 주로 카공을 할 때의 시간대와 컨디션은?",
        "options": [
            "잠을 깨워야 하거나 집중력을 최대로 끌어올려야 하는 상태",
            "늦은 오후·저녁이거나, 심장 두근거림 없이 편안하게 있고 싶은 상태"
        ],
        "types": ["H", "L"]
    },
    {
        "q": "Q3. 카페 문을 열고 들어갔을 때 가장 이상적인 소음 수준은?",
        "options": [
            "책장 넘기는 소리와 작은 백색소음만 들리는 독서실 같은 정적",
            "잔잔한 음악과 사람들의 적당한 대화 소리가 섞인 활기찬 분위기"
        ],
        "types": ["Q", "V"]
    },
    {
        "q": "Q4. 카페에 자리를 잡을 때 나의 가방 속 준비물은?",
        "options": [
            "노트북, 충전기, 태블릿, 파우치까지 풀세팅 (콘센트 자리 필수!)",
            "가벼운 노트나 태블릿 하나, 혹은 책 한 권 정도로 단출한 편"
        ],
        "types": ["M", "F"]
    },
    {
        "q": "Q5. 시험 기간이나 마감 직전, 극심한 스트레스를 받을 때 나의 선택은?",
        "options": [
            "정신이 번쩍 들 만큼 쌉싸름하고 묵직한 음료 한 잔",
            "뇌에 당을 즉각 공급해 줄 달달한 음료나 디저트 조합"
        ],
        "types": ["B", "S"]
    },
    {
        "q": "Q6. 평소 커피(카페인)를 마셨을 때 나의 몸 반응은?",
        "options": [
            "커피를 마셔야 비로소 머리가 돌아가고 시동이 걸린다",
            "카페인을 많이 마시면 밤에 잠이 안 오거나 속이 쓰린 편이다"
        ],
        "types": ["H", "L"]
    },
    {
        "q": "Q7. 옆 테이블에서 조용히 대화를 나누는 소리가 들린다면?",
        "options": [
            "신경이 쓰여서 이어폰을 꽂거나 자리를 옮기고 싶어진다",
            "오히려 적당한 생활 소음이 있어야 집중이 더 잘 된다"
        ],
        "types": ["Q", "V"]
    },
    {
        "q": "Q8. 보통 카페에서의 체류 시간은?",
        "options": [
            "최소 3~4시간 이상, 엉덩이 붙이고 진득하게 끝장을 본다",
            "1~2시간 내에 목표한 분량만 바짝 끝내고 깔끔하게 이동한다"
        ],
        "types": ["M", "F"]
    },
    {
        "q": "Q9. 음료를 다 마신 뒤 입안에 남는 느낌으로 더 선호하는 것은?",
        "options": [
            "물처럼 깔끔하고 개운하게 떨어지는 잔향",
            "기분 좋은 달콤함과 부드러운 여운"
        ],
        "types": ["B", "S"]
    },
    {
        "q": "Q10. 카페에서 음료 한 잔을 고를 때 나에게 더 중요한 가치는?",
        "options": [
            "확실한 각성 효과와 에너지 부스팅",
            "카페인 부담 없는 편안함과 은은한 향·맛의 힐링"
        ],
        "types": ["H", "L"]
    },
    {
        "q": "Q11. 선호하는 카페 인테리어와 좌석 배치는?",
        "options": [
            "시선이 차단된 구석 자리, 1인 바 테이블, 차분한 우드톤 공간",
            "통유리창 너머 거리가 보이는 개방적인 공간, 탁 트인 대형 테이블"
        ],
        "types": ["Q", "V"]
    },
    {
        "q": "Q12. 나에게 '성공적인 카공'이란?",
        "options": [
            "여유롭게 호흡을 길게 가져가며 방대한 분량을 차근차근 해내는 것",
            "정해진 시간 안에 고도의 집중력을 발휘해 효율을 극대화하는 것"
        ],
        "types": ["M", "F"]
    }
]

# 4. 알록달록한 컨페티 애니메이션 실행 함수
def trigger_confetti():
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            const duration = 1100;
            const end = Date.now() + duration;

            (function frame() {
                window.parent.confetti({
                    particleCount: 6,
                    angle: 60,
                    spread: 55,
                    origin: { x: 0 },
                    ticks: 90,
                    gravity: 1.35,
                    colors: ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#FF9F1C']
                });
                window.parent.confetti({
                    particleCount: 6,
                    angle: 120,
                    spread: 55,
                    origin: { x: 1 },
                    ticks: 90,
                    gravity: 1.35,
                    colors: ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#FF9F1C']
                });

                if (Date.now() < end) {
                    requestAnimationFrame(frame);
                }
            }());
        </script>
        """,
        height=0,
    )

# 5. 4대 성향 비율 막대 그래프 생성 함수
def create_mbti_chart(scores):
    axes = [
        ("쌉싸름 (B)", "달달함 (S)", scores["B"], scores["S"], "#6D4C41", "#E57373"),
        ("고카페인 (H)", "저카페인 (L)", scores["H"], scores["L"], "#4E342E", "#81C784"),
        ("고요함 (Q)", "적당한 활기 (V)", scores["Q"], scores["V"], "#546E7A", "#FFB74D"),
        ("장기 체류 (M)", "단기 몰입 (F)", scores["M"], scores["F"], "#5C6BC0", "#4DB6AC")
    ]

    fig = go.Figure()

    for left_label, right_label, left_val, right_val, left_color, right_color in reversed(axes):
        left_pct = round((left_val / 3) * 100)
        right_pct = 100 - left_pct
        axis_title = f"{left_label}  vs  {right_label}"

        fig.add_trace(go.Bar(
            y=[axis_title],
            x=[left_pct],
            name=left_label,
            orientation='h',
            marker=dict(color=left_color, line=dict(color='white', width=1)),
            text=f"{left_label} {left_pct}%" if left_pct > 0 else "",
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=13, family="sans-serif"),
            hoverinfo='none'
        ))

        fig.add_trace(go.Bar(
            y=[axis_title],
            x=[right_pct],
            name=right_label,
            orientation='h',
            marker=dict(color=right_color, line=dict(color='white', width=1)),
            text=f"{right_label} {right_pct}%" if right_pct > 0 else "",
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=13, family="sans-serif"),
            hoverinfo='none'
        ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(range=[0, 100], showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=13, color="#3E2723"), showgrid=False),
        showlegend=False,
        height=280,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# 6. 공유용 결과 카드 이미지 생성 함수
def generate_share_image(result_code, img_path):
    canvas = Image.new("RGB", (600, 680), "#FAF6F0")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([20, 20, 580, 660], outline="#8D6E63", width=4)

    if img_path and os.path.exists(img_path):
        drink_img = Image.open(img_path).convert("RGB")
        drink_img = drink_img.resize((420, 420))
        canvas.paste(drink_img, (90, 60))
    else:
        draw.rectangle([90, 60, 510, 480], fill="#EFEBE9", outline="#BCAAA4", width=2)

    font_large = ImageFont.load_default(size=42)
    font_small = ImageFont.load_default(size=22)

    draw.text((300, 535), f"TYPE : [ {result_code} ]", fill="#3E2723", font=font_large, anchor="mm")
    draw.text((300, 595), "My Cafe Study & Drink Test", fill="#6D4C41", font=font_small, anchor="mm")

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue()

# 7. 세션 상태 초기화 및 리셋 함수
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "show_share" not in st.session_state:
    st.session_state.show_share = False
if "play_confetti" not in st.session_state:
    st.session_state.play_confetti = False

def reset_test():
    for idx in range(len(QUESTIONS)):
        st.session_state[f"q_{idx}"] = None
    st.session_state.show_result = False
    st.session_state.show_share = False
    st.session_state.play_confetti = False

# 8. 메인 화면 UI (모서리 둥근 타이틀 박스)
st.markdown("""
    <div class="title-box">
        <h1>☕ 나의 카공 스타일 & 인생 음료 테스트</h1>
        <p>12가지 질문에 답하고, 나의 <b>카공 유형</b>과 <b>인생 카페 음료</b>를 추천받아 보세요!</p>
    </div>
""", unsafe_allow_html=True)

# 사용자 응답 수집 및 상단 실시간 응답 진행률 표시
user_answers = {idx: st.session_state.get(f"q_{idx}", None) for idx in range(len(QUESTIONS))}
answered_count = sum(1 for ans in user_answers.values() if ans is not None)
progress_ratio = answered_count / len(QUESTIONS)
st.progress(progress_ratio, text=f"📊 전체 응답 진행률: **{answered_count} / {len(QUESTIONS)}문항** ({int(progress_ratio * 100)}%)")
st.divider()

# 12개 질문 라디오 버튼 출력
for idx, item in enumerate(QUESTIONS):
    st.radio(
        label=item["q"],
        options=item["options"],
        index=None,
        key=f"q_{idx}"
    )
    st.write("")

# 실시간 응답 상태 재확인
current_answers = {idx: st.session_state.get(f"q_{idx}") for idx in range(len(QUESTIONS))}
unanswered = [idx + 1 for idx, ans in current_answers.items() if ans is None]

# 버튼 클릭 시 안내 문구 출력용 영역 (결과 확인하기 버튼 바로 위)
warning_placeholder = st.empty()

if st.button("✨ 결과 확인하기", use_container_width=True, type="primary"):
    if unanswered:
        st.session_state.show_result = False
        unanswered_str = ", ".join([f"{num}번" for num in unanswered])
        warning_placeholder.warning(f"⚠️ 아직 대답하지 않은 질문이 있습니다! **{unanswered_str} 문항에 응답하세요!**")
    else:
        warning_placeholder.empty()
        st.session_state.show_result = True
        st.session_state.show_share = False
        st.session_state.play_confetti = True

# 9. 결과 화면 출력
if st.session_state.show_result and not unanswered:
    if st.session_state.play_confetti:
        trigger_confetti()
        st.session_state.play_confetti = False

    scores = {"B": 0, "S": 0, "H": 0, "L": 0, "Q": 0, "V": 0, "M": 0, "F": 0}
    for idx, ans in current_answers.items():
        selected_idx = QUESTIONS[idx]["options"].index(ans)
        selected_type = QUESTIONS[idx]["types"][selected_idx]
        scores[selected_type] += 1

    code_1 = "B" if scores["B"] > scores["S"] else "S"
    code_2 = "H" if scores["H"] > scores["L"] else "L"
    code_3 = "Q" if scores["Q"] > scores["V"] else "V"
    code_4 = "M" if scores["M"] > scores["F"] else "F"
    result_code = f"{code_1}{code_2}{code_3}{code_4}"

    result_data = RESULTS[result_code]

    st.divider()
    st.subheader(f"🎉 당신의 카공 유형은 [{result_code}]")
    st.markdown(f"## **\"{result_data['name']}\"**")

    col1, col2 = st.columns([1, 1.3])

    # 저장해 두신 images/유형이름.png 파일을 자동으로 불러옵니다.
    img_png = f"images/{result_code}.png"
    img_jpg = f"images/{result_code}.jpg"
    valid_img_path = img_png if os.path.exists(img_png) else (img_jpg if os.path.exists(img_jpg) else None)

    with col1:
        if valid_img_path:
            st.image(valid_img_path, caption=f"추천 인생 음료: {result_data['drink']}", use_container_width=True)
        else:
            st.info(f"🥤 **추천 음료: {result_data['drink']}**\n\n*(GitHub의 images 폴더 안에 `{result_code}.png` 파일을 넣어주세요!)*")

    with col2:
        st.success(f"### ☕ 추천 인생 음료\n**{result_data['drink']}**")
        st.info(f"### 🪑 찰떡 작업 환경\n{result_data['env']}")
        st.write(f"**💡 유형 특징:** {result_data['desc']}")

    st.write("")
    st.markdown("### 📊 나의 4대 카공 성향 비율")
    fig = create_mbti_chart(scores)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 10. 검사 결과 공유하기 & 다시 검사하기 버튼
    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("📤 검사 결과 공유하기", use_container_width=True):
            st.session_state.show_share = not st.session_state.show_share
    with action_col2:
        st.button("🔄 다시 검사하기", use_container_width=True, on_click=reset_test)

    if st.session_state.show_share:
        share_col1, share_col2 = st.columns(2)

        with share_col1:
            st.markdown("#### 🖼️ 사진으로 저장하기")
            card_bytes = generate_share_image(result_code, valid_img_path)
            st.download_button(
                label="📥 결과 이미지 다운로드 (PNG)",
                data=card_bytes,
                file_name=f"cafe_test_{result_code}.png",
                mime="image/png",
                use_container_width=True
            )

        with share_col2:
            st.markdown("#### 🔗 결과 링크 & 텍스트 복사")
            share_text = (
                f"☕ 나의 카공 스타일 & 인생 음료 테스트 결과!\n"
                f"유형: [{result_code}] {result_data['name']}\n"
                f"추천 음료: {result_data['drink']}\n"
                f"나도 테스트하러 가기 👉 (배포 후 웹앱 주소를 여기에 붙여넣으세요!)"
            )
            st.code(share_text, language="text")
            st.caption("👆 위 박스 오른쪽 위의 **복사 아이콘**을 누르면 한 번에 복사됩니다!")