import streamlit as st
import requests
import re # HTML 응답을 파싱하기 위해 사용합니다.

# 맞춤법 검사 결과를 처리하는 함수 (인크루트 API 사용)
def check_spelling_incruit(text):
    """
    인크루트 맞춤법 검사기 API에 직접 요청을 보내 결과를 반환하는 함수
    """
    url = "https://spell.incruit.com/api/spell"
    
    # API가 요구하는 형식에 맞춰 데이터를 전송합니다.
    payload = {'spell_text': text}
    
    # 서버가 스크립트 요청을 차단하지 않도록 헤더를 추가합니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 응답 대기 시간을 10초로 설정합니다.
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 응답은 JSON 형식이므로 .json()으로 파싱합니다.
        data = response.json()
        
        # 1. 전체 교정 문장 추출
        # API 결과에 포함된 HTML에서 태그를 제거하여 순수 텍스트만 남깁니다.
        corrected_html = data.get('Html', '')
        corrected_text = re.sub(r'<[^>]+>', '', corrected_html)
        
        # 2. 개별 수정 제안 추출
        errors = data.get('ErrInfo', [])
        suggestions = {}
        for err in errors:
            wrong_word = err.get('WrongWord', '')
            right_word = err.get('RightWord', '')
            if wrong_word and right_word:
                # 동일한 오류가 여러 번 나올 수 있으므로, 중복을 방지합니다.
                if wrong_word not in suggestions:
                    suggestions[wrong_word] = right_word
                    
        was_corrected = (len(errors) > 0)
        
        return corrected_text, was_corrected, suggestions

    except requests.exceptions.RequestException as e:
        st.error(f"맞춤법 검사기 서버에 연결하는 중 오류가 발생했습니다: {e}")
        return text, False, {}
    except Exception as e:
        st.error(f"결과를 처리하는 중 알 수 없는 오류가 발생했습니다: {e}")
        return text, False, {}


# --- Streamlit UI 부분 ---
st.title("✍️ 한국어 맞춤법 검사기 (인크루트 API, 최종 안정 버전)")
st.caption("문장을 입력하고 '검사하기' 버튼을 누르면, 인크루트 맞춤법 검사기를 통해 오류를 찾아 수정합니다.")

text = st.text_area("검사할 문장을 입력하세요:", height=150, placeholder="예: 아버지가방에들어가신다.")

if st.button("검사하기", type="primary"):
    if not text.strip():
        st.warning("문장을 입력해주세요!")
    else:
        with st.spinner("맞춤법을 검사하는 중입니다..."):
            corrected_text, was_corrected, suggestions = check_spelling_incruit(text)

            if not was_corrected:
                st.success("✅ 맞춤법 오류가 발견되지 않았습니다!")
                st.info(f"**원본 문장:** {text}")
            else:
                st.error(f"❌ 총 {len(suggestions)}개의 맞춤법 오류를 발견하여 수정했습니다.")
                
                # 개별 오류 항목을 다시 보여주는 기능을 복원했습니다.
                st.subheader("수정 제안")
                for original, corrected in suggestions.items():
                    st.markdown(f"- **'{original}'** → **'{corrected}'**")
                
                st.divider()
                
                st.subheader("📝 전체 교정 문장")
                st.success(corrected_text)
