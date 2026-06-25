import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import base64

st.set_page_config(page_title="잔반 다이어트 AI 프로젝트", page_icon="🍱", layout="centered")

st.title("🍱 AI와 함께하는 '잔반 다이어트'")
st.write("식판을 촬영해 AI 분석을 받고, 오늘 나의 성찰일지를 친구들과 공유해 보세요.")

# ⚠️ 여기에 1단계에서 복사한 구글 앱스스크립트(GAS) 웹 앱 URL을 넣으세요!
GAS_URL = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnS8vxx5mbCoA_3291r5HV8xk0HzToDwCR4EVwgmWDfP_DboWmwjKTZtgJEf8DSP0nnM9Gth0_k1u-ARC5HXv87wYzf2taI7Cfw9TOy_iFPoRebnsIBcUeOGv7xy9fvQVUnX_XUxobTYsNKIitMALRLpi-umQg8zFJojiBNXEgCNS3f9JAlFq5ZxANLLmlWvSs7WhDaeu71EdyohJ4bgSmZQSSY3Za9HZC3oi4dVfWzyujKypbfi8mQunyakqoyJ9zValnJsVo-bahNLA6F_U9C0_vmTcQ&lib=MiJjpqqwqNtvVW1LOo685fAMetOoHZ3H2"

api_key = st.text_input("🔑 교사용 Gemini API 키를 입력하세요", type="password")

# 새로고침 시 AI 결과가 날아가지 않도록 세션 상태 보존 설정
if 'ai_result' not in st.session_state:
    st.session_state.ai_result = ""

if api_key and GAS_URL != "":
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    
    st.subheader("👤 학생 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        student_num = st.text_input("학번을 입력하세요 (예: 6101)", max_chars=4)
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
                너는 초등학교 급식 잔반 분석 전문가이자 친절한 환경 과학자야. 
                제공된 식판 사진을 보고 다음 4가지 항목에 대해 초등학생이 이해하기 쉽게 다정하고 명확한 말투로 답변해 줘.
                
                1. [잔반율]: 식판 전체 면적 대비 남은 음식의 양(남은 음식의 종류 개수도 참고)을 대략적인 백분율(%)로 알려줘. (예: 약 30% 남음, 다 먹었다면 0%)
                2. [주요 잔반]: 가장 많이 남은 음식 종류가 무엇인지 알려줘. (밥/국물/고기반찬/채소반찬/과일/디저트 등 1~2가지 선택)
                3. [환경 영향도]: 이 잔반이 유발하는 탄소 배출량의 수준을 상/중/하로 나누고, 이로 인해 지구가 받는 영향을 초등학생 눈높이에서 설명해 줘.
                4. [지구의 한마디]: 음식을 다 먹었다면 아낌없는 칭찬을, 남겼다면 다음 식사 때 실천할 수 있는 구체적인 행동 1가지를 다정하게 제안해 줘.
               
                답변 양식은 아래 서식을 무조건 지켜서 작성해 줘:
                ### 📊 AI 분석 결과
                - **잔반율**: 내용
                - **주요 잔반**: 내용
                - **환경 영향도**: 내용
                
                ### 🌍 지구의 한마디
                내용
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
        
        # 데이터가 정상적인 리스트(배열) 형태인지, 그리고 비어있지 않은지 확인
        if isinstance(posts, list) and len(posts) > 0:
            # 최신글이 맨 위로 오도록 배열을 뒤집어서(reversed) 보여줌
            for post in reversed(posts):
                with st.container(border=True):
                    col_img, col_txt = st.columns([1, 2])
                    with col_img:
                        # ⚠️ [수정됨] GAS에서 이미 가공된 URL을 주므로 파이썬에서 자를 필요 없음!
                        # .get()을 사용하여 키가 없더라도 에러가 나지 않고 빈 문자열을 반환하도록 처리
                        img_url = post.get('image_url', '')
                        if img_url:
                            st.image(img_url, use_container_width=True)
                        else:
                            st.info("📷 이미지 없음")
                    
                    with col_txt:
                        st.subheader(f"{post.get('num', '')} {post.get('name', '')}")
                        st.write(f"**✍️ 나의 성찰:** {post.get('reflection', '')}")
                        with st.expander("🤖 AI 피드백 다시보기"):
                            st.markdown(post.get('feedback', ''))
        else:
            st.info("아직 등록된 성찰일지가 없습니다. 첫 번째 주인공이 되어보세요!")
            
except Exception as e:
    st.error(f"게시판 데이터를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요. (에러: {e})")
