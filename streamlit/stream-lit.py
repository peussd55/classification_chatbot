import streamlit as st
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# CSV 파일 경로 설정
file_path = 'C:\\Users\\user\\jupyter2\\contest\\TB_LM_OUT_RATE_S_dt_with_diss_nm_2.csv'

# 데이터 로드
data = pd.read_csv(file_path)
data = data[['diss_nm', 'diag_nm', 'stty_infcd_tpcd']].dropna()  # 필요한 열만 로드 및 NaN 제거

# 정규 표현식을 사용한 명사 추출 함수 정의
tokenizer = RegexpTokenizer(r'\b\w+\b')

def extract_nouns(text):
    nouns = tokenizer.tokenize(text)  # 단어만 추출
    return ' '.join(nouns)

# `diss_nm`과 `diag_nm` 결합하여 명사만 추출한 `combined_nouns` 열 생성
data['combined_text'] = data['diss_nm'] + ' ' + data['diag_nm']
data['combined_nouns'] = data['combined_text'].apply(extract_nouns)

# TF-IDF 벡터화
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(data['combined_nouns'])

# Streamlit 사이드바 메뉴
st.sidebar.title("메뉴")
menu = st.sidebar.radio("메뉴를 선택하세요", ["법정감염병코드검색", "감염병검색", "미정"])

# "법정감염병코드검색" 메뉴 화면 구성
if menu == "법정감염병코드검색":
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>법정감염병코드검색</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>진단명을 입력하시면 법정감염병코드를 찾아줍니다.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 사용자 입력 및 추출 로직
    test_sentence = st.text_input("테스트할 진단명을 입력하세요:", "")

    if test_sentence:
        # 입력된 문장에서 명사만 추출하여 TF-IDF 벡터화
        test_sentence_nouns = extract_nouns(test_sentence)
        test_sentence_tfidf = tfidf_vectorizer.transform([test_sentence_nouns])

        # `stty_infcd_tpcd`와 코사인 유사도 계산
        cosine_similarities = cosine_similarity(test_sentence_tfidf, tfidf_matrix)
        most_similar_index = cosine_similarities.argmax()
        most_similar_code = data['stty_infcd_tpcd'].iloc[most_similar_index]
        similarity_score = cosine_similarities[0, most_similar_index]

        # 유사도가 0.0이면 4번 코드로 강제 분류
        if similarity_score == 0.0:
            most_similar_code = 4

        # 결과 출력
        st.markdown("<div style='background-color: #D4EDDA; padding: 10px; border-radius: 5px;'>"
            f"<p style='color: #155724; font-weight: bold;'>입력된 감염병 키워드: {test_sentence}</p>"
            f"<p style='color: #155724; font-weight: bold;'>가장 유사한 감염병코드: {most_similar_code}</p>"
            f"<p style='color: #155724; font-weight: bold;'>유사도 점수: {similarity_score:.2f}</p>"
            "</div>", unsafe_allow_html=True)

# "감염병검색" 메뉴 화면 구성
elif menu == "감염병검색":
    st.markdown("<h1 style='text-align: center; color: #1E90FF;'>감염병검색</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>진단명을 입력하시면 가장 유사한 감염병을 찾아줍니다.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 키워드 입력
    disease_query = st.text_input("테스트할 진단명을 입력하세요:", "")

    if disease_query:
        # 입력 키워드에서 명사만 추출하여 TF-IDF 벡터화
        disease_query_nouns = extract_nouns(disease_query)
        disease_query_tfidf = tfidf_vectorizer.transform([disease_query_nouns])

        # `diss_nm`과 `diag_nm` 결합 텍스트에 대한 코사인 유사도 계산
        cosine_similarities = cosine_similarity(disease_query_tfidf, tfidf_matrix).flatten()
        best_match_index = cosine_similarities.argmax()
        best_match_disease = data['diss_nm'].iloc[best_match_index]
        best_similarity_score = cosine_similarities[best_match_index]

        # 유사도가 0.0인 경우 매칭 없음 처리
        if best_similarity_score == 0.0:
            best_match_disease = "매칭 없음"

        # 결과 출력 (파란색 계통)
        st.markdown("<div style='background-color: #D1ECF1; padding: 10px; border-radius: 5px;'>"
                    f"<p style='color: #0C5460; font-weight: bold;'>입력된 감염병 키워드: {disease_query}</p>"
                    f"<p style='color: #0C5460; font-weight: bold;'>가장 유사한 감염병명: {best_match_disease}</p>"
                    f"<p style='color: #0C5460; font-weight: bold;'>유사도 점수: {best_similarity_score:.2f}</p>"
                    "</div>", unsafe_allow_html=True)

# "미정" 메뉴 화면 구성
elif menu == "미정":
    st.markdown("<h1 style='text-align: center; color: #FF6347;'>데이터 통계</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>데이터 통계 정보를 확인하세요.</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("데이터 통계 기능은 아직 구현되지 않았습니다. 추후 업데이트될 예정입니다.")