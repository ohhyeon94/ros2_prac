# 레인보우 로보틱스 Python 프로그래밍 학습 커리큘럼

## 학습 로드맵

```
Phase 1: 입문 (1~2주)
  ├── 로봇 연결 및 상태 읽기
  ├── 조인트 공간 이동 (movej)
  └── 직선 이동 (movel)

Phase 2: 중급 (2~4주)
  ├── 궤적 계획 (원, 지그재그)
  ├── I/O 제어 (그리퍼, 센서)
  └── 힘/토크 제어

Phase 3: 고급 (4~8주)
  ├── 비전 통합 (카메라 + 로봇)
  ├── 상태 머신 기반 자동화
  └── 실제 공정 미니 프로젝트
```

---

## Phase 1: 입문

### 목표
- 로봇 SDK API 구조 이해
- 기본 이동 명령 숙달
- 좌표계 개념 이해 (조인트 공간 vs 작업 공간)

### 핵심 개념

| 개념 | 설명 |
|------|------|
| Joint Space | 각 조인트 각도(J1~J6)로 표현하는 공간 |
| Task Space (TCP) | 공구 끝점의 X,Y,Z,Rx,Ry,Rz로 표현 |
| movej | 조인트 공간 이동 - 경로 예측 어려움, 빠름 |
| movel | 직선 이동 - 경로 예측 가능, 충돌 회피 용이 |
| Blocking | 이동 완료까지 다음 코드 실행 대기 |

### 학습 예제
1. `examples/01_beginner/01_connection.py`
2. `examples/01_beginner/02_joint_move.py`
3. `examples/01_beginner/03_linear_move.py`

---

## Phase 2: 중급

### 목표
- 복잡한 경로 생성 능력
- 주변 장치(그리퍼, 센서) 연동
- 힘 기반 제어 이해

### 핵심 개념

| 개념 | 설명 |
|------|------|
| movec | 원호 이동 (via point 경유) |
| Blending | 웨이포인트 전환 시 속도 유지하며 부드럽게 연결 |
| Digital I/O | 0/1 신호로 그리퍼, 밸브 등 제어 |
| F/T Sensor | 6축 힘/토크 센서로 접촉 감지, 컴플라이언스 제어 |
| Peg-in-Hole | 조립 작업의 기본: 힘 제어로 삽입 |

### 학습 예제
1. `examples/02_intermediate/01_trajectory.py`
2. `examples/02_intermediate/02_io_control.py`
3. `examples/02_intermediate/03_force_control.py`

---

## Phase 3: 고급

### 목표
- 비전 시스템과 로봇 통합
- 실제 산업 수준의 자동화 프로그램 구현
- 에러 처리 및 안전 설계

### 핵심 개념

| 개념 | 설명 |
|------|------|
| Eye-to-Hand | 고정 카메라 - 로봇 캘리브레이션 |
| Eye-in-Hand | 로봇 끝에 카메라 부착 |
| Homography | 픽셀 좌표 → 로봇 좌표 변환 행렬 |
| FSM | 유한 상태 머신 - 복잡한 시퀀스 관리 |
| Cycle Time | 작업 1회 소요 시간 - 생산성 지표 |

### 학습 예제
1. `examples/03_advanced/01_vision_pick.py`
2. `examples/03_advanced/02_state_machine.py`

---

## 중요한 안전 수칙

> 실제 로봇 작업 전 반드시 숙지하세요.

1. **저속 테스트 먼저** - 새 프로그램은 항상 속도 10% 이하로 첫 실행
2. **비상 정지 버튼 위치 확인** - 항상 손 닿는 곳에 E-stop
3. **작업 반경 내 작업자 없음 확인** - 협동로봇이라도 고속/고힘 작업은 위험
4. **소프트 리밋 설정** - 로봇이 테이블, 지그와 충돌하지 않도록 제한
5. **힘 감지 파라미터 설정** - 예상치 못한 접촉 시 즉시 정지
```python
# 항상 안전 파라미터 먼저 설정
robot.set_collision_sensitivity(level=3)  # 충돌 감도 (1~5)
robot.set_speed_limit(max_joint_speed=30)  # 최대 조인트 속도 제한
```
