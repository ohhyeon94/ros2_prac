# 레인보우 로보틱스 Python 프로그래밍 학습 가이드

Rainbow Robotics RB 시리즈 협동로봇을 Python으로 제어하기 위한 단계별 학습 자료입니다.

## 환경 설정

```bash
# Rainbow Robotics Python SDK 설치
pip install rb_sdk  # 실제 SDK명은 레인보우 로보틱스 공식 문서 참고

# 의존성 패키지
pip install numpy matplotlib scipy
```

## 학습 구조

```
ros2_prac/
├── examples/
│   ├── 01_beginner/        # 입문 (연결, 기본 이동)
│   ├── 02_intermediate/    # 중급 (궤적, I/O, 힘 제어)
│   └── 03_advanced/        # 고급 (비전, 커스텀 태스크)
└── curriculum/             # 학습 커리큘럼 및 과제
```

## 빠른 시작

1. `examples/01_beginner/01_connection.py` 부터 시작
2. 각 예제 실행 후 `curriculum/assignments.md`의 과제 수행
3. 과제 완료 후 다음 단계로 진행

## 참고 자료

- [레인보우 로보틱스 공식 사이트](https://www.rainbow-robotics.com)
- [RB SDK 문서](https://docs.rainbow-robotics.com)
- [포럼/커뮤니티](https://community.rainbow-robotics.com)
