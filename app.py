import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 웹페이지 기본 설정 (타이틀 및 아이콘)
st.set_page_config(page_title="잔반 다이어트 AI 프로젝트", page_icon="🍱", layout="centered")

# 화면 제목과 설명
st.title("🍱 AI와 함께하는 '잔반 다이어트'")
st.write("식사 후 남은 식판을 촬영하면 AI가 잔반량과 환경 영향을 분석해 줍니다.")

# 2. 교사용 AI API 키 입력창 (보안을 위해 화면에 입력받도록 처리)
api_key = st.text_input("🔑 교사용 Gemini API 키를 입력하세요", type="password")

if api_key:
    # AI 모델 설정 (이미지 분석에 뛰어난 gemini-1.5-flash 모델 사용)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.1-flash-lite')
    
    # 3. 학생 정보 입력받기
    st.subheader("👤 학생 정보 입력")
    col1, col2 = st.columns(2)
    with col1:
        student_num = st.text_input("학번을 입력하세요 (예: 60101)", max_chars=5)
    with col2:
        student_name = st.text_input("이름을 입력하세요")

    # 4. 카메라 촬영 기능 (스마트폰/태블릿으로 접속 시 바로 카메라가 켜집니다)
    st.subheader("📸 식판 촬영")
    img_file = st.camera_input("식판 모양이 잘 보이도록 위에서 곧바로 촬영해 주세요!")

    # 모두 입력되었을 때 AI 분석 시작
    if img_file and student_num and student_name:
        st.success("사진 업로드 완료! AI가 분석을 시작합니다...")
        
        # 이미지 열기
        image = Image.open(img_file)
        
        # AI에게 줄 조건(프롬프트) 설정
        prompt = """
        너는 초등학교 급식 잔반 분석 전문가이자 친절한 환경 과학자야. 
        제공된 식판 사진을 보고 다음 4가지 항목에 대해 초등학생이 이해하기 쉽게 다정하고 명확한 말투로 답변해 줘.
        
        1. [잔반율]: 식판 전체 면적 대비 남은 음식의 양을 대략적인 백분율(%)로 알려줘. (예: 약 30% 남음, 다 먹었다면 0%)
        2. [주요 잔반]: 가장 많이 남은 음식 종류가 무엇인지 알려줘. (밥/국물/고기반찬/채소반찬 중 선택)
        3. [환경 영향도]: 이 잔반이 유발하는 탄소 배출량의 수준을 상/중/하로 나누고, 이로 인해 지구가 받는 영향을 초등학생 눈높이에서 설명해 줘.
        4. [지구의 한마디]: 음식을 다 먹었다면 아낌없는 칭찬을, 남겼다면 다음 식사 때 실천할 수 있는 구체적인 행동 1가지를 다정하게 제안해 줘.
        
        답변 양식은 아래 서식을 무조건 지켜서 작성해 줘:
        ### 📊 AI 분석 결과
        - **잔반율**: 내용
        - **가장 많이 남은 음식**: 내용
        - **환경 영향도**: 내용
        
        ### 🌍 지구의 한마디
        내용
        """
        
        # AI 분석 중 로딩 표시
        with st.spinner("AI가 식판을 열심히 분석하고 있습니다... 잠시만 기다려주세요."):
            try:
                # AI에게 이미지와 질문을 던져 답변 받기
                response = model.generate_content([prompt, image])
                
                # 결과 화면에 출력
                st.subheader(f"✨ {student_name} 학생의 분석 결과")
                st.markdown(response.text)
                
                # 2단계 성찰 활동을 위한 안내 멘트
                st.info("💡 위의 AI 분석 결과를 캡처하거나 메모하여 '패들릿 성찰 일지'에 작성해 주세요!")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다. API 키나 사진을 확인해 주세요. (오류 내용: {e})")
else:
    st.warning("수업 시작 전, 교사 화면에서 2단계에서 발급받은 Gemini API 키를 먼저 입력해 주세요.")