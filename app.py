"""개인 맞춤형 하루 칼로리 & 탄단지 계산기.

실행: streamlit run app.py
"""

from dataclasses import dataclass
from typing import Optional

import streamlit as st


ACTIVITY_LEVELS = {
    "거의 운동하지 않음": 1.2,
    "가벼운 활동 (주 1~3회 운동)": 1.375,
    "보통 활동 (주 3~5회 운동)": 1.55,
    "높은 활동 (주 6~7회 운동)": 1.725,
    "매우 높은 활동 (강도 높은 육체활동/운동)": 1.9,
}

GOALS = {
    "감량": {"multiplier": 0.80, "protein": 2.0, "label": "살 빼기용"},
    "유지": {"multiplier": 1.00, "protein": 1.6, "label": "체중 유지"},
    "벌크업": {"multiplier": 1.12, "protein": 1.8, "label": "벌크업용"},
}


@dataclass
class Profile:
    height: float
    weight: float
    age: int
    sex: str
    activity: float
    skeletal_muscle: Optional[float] = None
    body_fat_percent: Optional[float] = None


def estimate_bmr(profile: Profile) -> tuple[float, str, Optional[float]]:
    """기초대사량, 계산 기준, 제지방량을 반환합니다."""
    if profile.body_fat_percent is not None:
        fat_mass = profile.weight * (profile.body_fat_percent / 100)
        lean_mass = profile.weight - fat_mass

        # Katch-McArdle: 제지방량을 반영한 기초대사량 계산식
        return 370 + 21.6 * lean_mass, "인바디 체지방률 기반", lean_mass

    male_bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
    female_bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161

    if profile.sex == "남성":
        return male_bmr, "성별·신체정보 기반", None
    if profile.sex == "여성":
        return female_bmr, "성별·신체정보 기반", None

    return (male_bmr + female_bmr) / 2, "성별 미입력 평균값", None


def calculate_goal(profile: Profile, goal: str) -> dict:
    bmr, bmr_basis, lean_mass = estimate_bmr(profile)
    maintenance = bmr * profile.activity
    goal_info = GOALS[goal]
    calories = maintenance * goal_info["multiplier"]

    # 체지방률이 있으면 제지방량을 단백질 계산에 반영
    protein_base = lean_mass if lean_mass is not None else profile.weight
    protein_per_kg = goal_info["protein"]

    # 골격근량이 높은 경우 단백질 권장량을 조금 높게 계산
    if (
        profile.skeletal_muscle is not None
        and profile.skeletal_muscle / profile.weight >= 0.42
    ):
        protein_per_kg += 0.15

    protein_g = protein_base * protein_per_kg

    # 지방은 총칼로리의 25%, 남은 칼로리는 탄수화물로 계산
    fat_g = calories * 0.25 / 9
    carb_g = max(0, (calories - protein_g * 4 - fat_g * 9) / 4)

    return {
        "goal": GOALS[goal]["label"],
        "calories": round(calories),
        "protein": round(protein_g),
        "carbs": round(carb_g),
        "fat": round(fat_g),
        "bmr": round(bmr),
        "maintenance": round(maintenance),
        "basis": bmr_basis,
    }


def render_result(result: dict) -> None:
    with st.container(border=True):
        st.subheader(result["goal"])
        st.metric("하루 목표 칼로리", f"{result['calories']:,} kcal")

        a, b, c = st.columns(3)
        a.metric("탄수화물", f"{result['carbs']} g")
        b.metric("단백질", f"{result['protein']} g")
        c.metric("지방", f"{result['fat']} g")

        st.caption(
            f"기초대사량 {result['bmr']:,} kcal · "
            f"유지 칼로리 {result['maintenance']:,} kcal"
        )


def main() -> None:
    st.set_page_config(
        page_title="하루 칼로리 & 탄단지 계산기",
        page_icon="🥗",
        layout="wide",
    )

    st.title("🥗 개인 맞춤형 하루 칼로리 & 탄단지 계산기")
    st.write("키·몸무게·나이를 입력하면 감량, 유지, 벌크업 목표를 한 번에 계산합니다.")

    with st.expander("입력 → 처리 → 출력 과정 보기", expanded=False):
        st.markdown(
            "**입력**: 신체 정보와 활동량, 선택 인바디 수치  \n"
            "**처리**: 기초대사량(BMR) → 활동대사량(TDEE) → 목표별 칼로리·탄단지 계산  \n"
            "**출력**: 감량·유지·벌크업용 하루 섭취 목표"
        )

    with st.form("calculator"):
        left, right = st.columns(2)

        with left:
            st.markdown("#### 필수 입력")
            height = st.number_input(
                "키 (cm) *", min_value=100.0, max_value=230.0,
                value=170.0, step=0.1
            )
            weight = st.number_input(
                "몸무게 (kg) *", min_value=25.0, max_value=300.0,
                value=65.0, step=0.1
            )
            age = st.number_input(
                "나이 *", min_value=14, max_value=100, value=25, step=1
            )
            activity_name = st.selectbox("활동량 *", list(ACTIVITY_LEVELS))
            sex = st.selectbox(
                "성별 (선택, 입력 시 더 정확함)",
                ["선택 안 함", "남성", "여성"],
            )

        with right:
            st.markdown("#### 인바디 선택 입력")
            st.info("골격근량과 체지방률을 입력하면 결과가 더 정확해집니다.")

            muscle_enabled = st.checkbox("골격근량 입력")
            skeletal_muscle = (
                st.number_input(
                    "골격근량 (kg)", min_value=5.0, max_value=100.0,
                    value=28.0, step=0.1
                )
                if muscle_enabled
                else None
            )

            fat_enabled = st.checkbox("체지방률 입력")
            body_fat_percent = (
                st.number_input(
                    "체지방률 (%)", min_value=3.0, max_value=70.0,
                    value=20.0, step=0.1
                )
                if fat_enabled
                else None
            )

        submitted = st.form_submit_button(
            "나의 하루 목표 계산하기",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if skeletal_muscle is not None and skeletal_muscle >= weight:
            st.error("골격근량은 몸무게보다 작게 입력해 주세요.")
            return

        profile = Profile(
            height=height,
            weight=weight,
            age=int(age),
            sex="" if sex == "선택 안 함" else sex,
            activity=ACTIVITY_LEVELS[activity_name],
            skeletal_muscle=skeletal_muscle,
            body_fat_percent=body_fat_percent,
        )

        st.success("계산이 완료되었습니다. 아래 수치는 하루 기준입니다.")

        if body_fat_percent is not None:
            st.caption(
                f"✓ 체지방률 {body_fat_percent:.1f}%를 반영한 "
                "제지방량 기반 기초대사량을 사용했습니다."
            )
        elif skeletal_muscle is not None:
            st.caption(
                "✓ 골격근량을 단백질 권장량에 반영했습니다. "
                "체지방률까지 입력하면 칼로리도 더 정교해집니다."
            )
        else:
            st.caption("인바디 수치를 추가하면 더욱 개인화된 결과를 확인할 수 있습니다.")

        results = [calculate_goal(profile, goal) for goal in GOALS]
        columns = st.columns(3)

        for column, result in zip(columns, results):
            with column:
                render_result(result)

        st.divider()
        st.warning(
            "건강 상태, 임신·수유, 성장기, 질환 또는 전문적인 운동 목표가 있다면 "
            "의료·영양 전문가와 상담하세요. 계산 결과는 일반적인 추정치입니다."
        )


if __name__ == "__main__":
    main()
