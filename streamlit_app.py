import streamlit as st
import requests
import json
import re

st.title("✍ 한국어 맞춤법 검사기")

text = st.text_area("검사할 문장을 입력하세요:")

if st.button("검사하기"):
    if text.strip() == "":
        st.warning("문장을 입력해주세요!")
    else:
        url = "https://speller.cs.pusan.ac.kr/results"
        data = {"text1": text}
        response = requests.post(url, data=data)

        try:
            # 부산대 API는 HTML 안에 JSON이 섞여있음 → 정규식으로 추출
            json_data = re.search(r"(?s)\"errInfo\":(.*?)}]", response.text)
            if not json_data:
                st.error("⚠ 맞춤법 검사 결과를 불러올 수 없습니다.")
            else:
                err_info = json.loads(json_data.group(0) + "}]")

                if not err_info:
                    st.success("✅ 맞춤법 오류가 없습니다!")
                    st.write("📝 교정된 문장:", text)
                else:
                    st.subheader("❌ 맞춤법 오류 발견")

                    corrected_text = text
                    for err in err_info:
                        org = err['orgStr']
                        cand = err['candWord'].split('|')[0]
                        help_msg = err['help']
                        st.write(f"- **{org}** → {cand} ({help_msg})")
                        corrected_text = corrected_text.replace(org, cand, 1)

                    st.subheader("📝 교정된 문장")
                    st.write(corrected_text)

        except Exception as e:
            st.error(f"⚠ 오류 발생: {e}")
