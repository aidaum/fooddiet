import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import base64

st.set_page_config(page_title="잔반 다이어트 AI 프로젝트", page_icon="🍱", layout="centered")

st.title("🍱 AI와 함께하는 '잔반 다이어트'")
st.write("식판을 촬영해 AI 분석을 받고, 오늘 나의 성찰일지를 친구들과 공유해 보세요.")

# ⚠️ 여기에 1단계에서 복사한 구글 앱스스크립트(GAS) 웹 앱 URL을 넣으세요!
GAS_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnS9oC7GUyZ5Rzax5dJfk6gHbdtZJ_w9xZYcqZY3_98_abnLDvbNGMYmovpLjFQ8Eg0RDG74MhgZ85maJa4NNiAG_PY6Gv2Xt2fQcsPs3whz-d39Uu836MTUL8huy5O6yMS2f-bHxAKlPh_A97WFZOI-5SM3DOYWdpXvV1fshbhV5V6Jzk1ffwrWEVj7n6W_Wl2iBu0pZxkZ1lSlswms5481C4_DIcnWVIbzDUvVc9e1hu-tS2igvET4dnnjzdULPxoVAYvP39IwpOD1yNgObTJEgpiN7g&lib=MiJjpqqwqNtvVW1LOo685fAMetOoHZ3H2"

api_key = st.text_input("🔑 교사용 Gemini API 키를 입력하세요", type="password")

# 새로고침 시 AI 결과가 날아가지 않도록 세션 상태 보존 설정
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = ""

if api_key and GAS_URL != "여기에_구글_앱스스크립트_웹앱_주소_URL을_넣으세요":
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    
    st.subheader("👤 학생 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        student_num = st.text_input("학번을 입력하세요 (예: 60101)", max_chars=5)
    with col2:
        student_name = st.text_input("이름을 입력하세요")

    st.subheader("📸 식판 촬영")
    img_file = st.camera_input("식판을 똑바로 촬영해 주세요!")

    # 사진이 찍히면 AI 분석 작동
    if img_file and student_num and student_name:
        if st.session_state.ai_result == "":
            with st.spinner("AI가 식판을 분석하고 있습니다..."):
                image = Image.open(img_file)
                prompt = """
                너는 친절한 초등학교 환경 과학자야. 식판 사진을 보고 다음 양식으로만 짧고 명확하게 답해줘.
                ### 📊 AI 분석 결과
                - **잔반율**: 약 OO% 남음 (다 먹었다면 0%)
                - **가장 많이 남은 음식**: 음식 종류
                - **환경 영향도**: 탄소 배출 수준(상/중/하) 및 지구에 미치는 영향 한 줄 설명
                """
                response = model.generate_content([prompt, image])
                st.session_state.ai_result = response.text

        # AI 결과 화면에 고정 표시
        st.info("🤖 AI의 분석 결과를 확인하고 아래 성찰일지를 작성하세요.")
        st.markdown(st.session_state.ai_result)
        
        # ✍️ 성찰일지 입력란 추가
        st.subheader("✍️ 오늘 나의 급식 성찰일지")
        reflection_text = st.text_area("오늘 음식을 남긴 이유와 다음 식사 때 실천할 나의 다짐을 적어주세요.")
        
        if st.button("🚀 성찰일지 게시판에 올리기"):
            if reflection_text:
                with st.spinner("게시판에 등록 중입니다..."):
                    # 이미지를 구글에 보내기 위해 Base64 텍스트로 변환
                    bytes_data = img_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    data_uri = f"data:image/jpeg;base64,{base64_image}"
                    
                    # 구글 앱스스크립트로 보낼 패키지 묶기
                    payload = {
                        "num": student_num,
                        "name": student_name,
                        "feedback": st.session_state.ai_result,
                        "reflection": reflection_text,
                        "image_base64": data_uri
                    }
                    
                    # 구글 서버로 데이터 전송 (POST 요청)
                    res = requests.post(GAS_URL, json=payload)
                    if res.status_code == 200:
                        st.success("🎉 성찰일지가 게시판에 성공적으로 등록되었습니다!")
                        st.session_state.ai_result = "" # 다음 사람을 위해 AI결과 초기화
                        st.rerun() # 화면 새로고침하여 게시판 갱신
                    else:
                        st.error("등록에 실패했습니다. 다시 시도해 주세요.")
            else:
                st.warning("성찰일지 내용을 입력해야 등록할 수 있습니다.")
else:
    st.warning("교사용 세팅(Gemini API 키 및 구글 웹앱 URL 입력)이 필요합니다.")

# --- 👥 실시간 우리 반 성찰 게시판 표시 영역 ---
st.divider()
st.header("👥 우리 반 실시간 성찰 게시판")

try:
    # 구글 서버에서 실시간 데이터 읽어오기 (GET 요청)
    response = requests.get(GAS_URL)
    if response.status_code == 200:
        posts = response.json()
        if posts:
            # 최신글이 맨 위로 오도록 배열을 뒤집어서(reversed) 보여줌
            for post in reversed(posts):
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        # 구글 드라이브 주소를 웹에 표시 가능한 이미지 주소로 가공
                        file_id = post['image_url'].split('/d/')[1].split('/')[0]
                        direct_img_url = f"https://docs.google.com/uc?export=view&id={file_id}"
                        st.image(direct_img_url, use_container_width=True)
                    with col_txt:
                        st.subheader(f"{post['num']} {post['name']}")
                        st.write(f"**✍️ 나의 성찰:** {post['reflection']}")
                        with st.expander("🤖 AI 피드백 다시보기"):
                            st.markdown(post['feedback'])
        else:
            st.info("아직 등록된 성찰일지가 없습니다. 첫 번째 주인공이 되어보세요!")
except Exception as e:
    st.write("게시판 데이터를 불러오는 중입니다...")
