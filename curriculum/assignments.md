# 레인보우 로보틱스 단계별 과제

각 과제는 예제 코드를 참고해 직접 구현하세요.
완성 기준은 **시뮬레이션 출력이 의도한 동작을 보여주는 것**입니다.

---

## Phase 1 과제 (입문)

### 과제 1-1: 포지션 북 만들기
**난이도: ★☆☆☆☆**

```
목표: 자주 쓰는 포지션을 딕셔너리로 관리하는 유틸리티 만들기

요구사항:
1. positions = {} 딕셔너리에 이름-포지션 쌍 저장
2. save_position(name, joint_angles) 함수 구현
3. load_position(name) -> list 함수 구현
4. list_positions() 함수 구현 (저장된 이름 목록 출력)
5. JSON 파일로 저장/불러오기 기능 추가

힌트:
  import json
  with open('positions.json', 'w') as f:
      json.dump(positions, f, indent=2)
```

### 과제 1-2: 반복 픽앤플레이스 시퀀스
**난이도: ★★☆☆☆**

```
목표: 픽업 → 이동 → 플레이스를 N회 반복하는 프로그램

요구사항:
1. pick_pos와 place_pos 리스트 정의 (각 3개 이상)
2. for 루프로 순서대로 픽앤플레이스 실행
3. 각 사이클 소요 시간 측정 (time.time() 활용)
4. 전체 완료 후 평균 사이클 타임 출력

고급 추가:
- place_pos를 팔레트 그리드(3x3)로 자동 계산
  grid_x = start_x + col * spacing
  grid_y = start_y + row * spacing
```

### 과제 1-3: 안전 이동 래퍼 함수
**난이도: ★★☆☆☆**

```
목표: 이동 전 유효성을 검사하는 안전한 이동 함수 구현

요구사항:
1. safe_movej(robot, joints, speed, acc) 구현
   - joints 길이가 6인지 검사
   - 각 조인트 범위 -360°~360° 검사
   - speed, acc가 1~100 범위인지 검사
   - 이상 시 ValueError 발생

2. safe_movel(robot, tcp_pos, speed) 구현
   - tcp_pos 길이가 6인지 검사
   - X,Y,Z가 작업 공간 범위 내인지 검사 (예: Z > 50mm)
   - 이상 시 ValueError 발생

3. try/except로 에러를 잡아 로그 출력
```

---

## Phase 2 과제 (중급)

### 과제 2-1: 나선형(Spiral) 궤적
**난이도: ★★★☆☆**

```
목표: 나선형 경로 웨이포인트 생성 함수 구현

수식:
  r(t) = r_start + (r_end - r_start) * t  (0 ≤ t ≤ 1)
  x(t) = cx + r(t) * cos(2π * n_turns * t)
  y(t) = cy + r(t) * sin(2π * n_turns * t)
  z(t) = z_start + (z_end - z_start) * t  (나선 높이 변화)

요구사항:
1. generate_spiral_waypoints(cx, cy, r_start, r_end,
                              z_start, z_end, n_turns, n_points) 구현
2. matplotlib으로 3D 경로 시각화
   from mpl_toolkits.mplot3d import Axes3D
   ax.plot(xs, ys, zs)

응용: 나사 조임, 스프레이 도포 패턴
```

### 과제 2-2: 그리퍼 자동 감지 파지
**난이도: ★★★☆☆**

```
목표: F/T 센서로 파지 성공 여부를 자동 판단

요구사항:
1. smart_grip(robot, gripper, ft_sensor) 함수 구현
   - 그리퍼 닫기 시작
   - 매 100ms마다 F/T 센서 읽기
   - |Fx|+|Fy| > 3N 이면 파지 성공 판단 (물체 접촉)
   - 3초 내 감지 없으면 파지 실패 반환

2. 파지 성공/실패에 따라 다른 동작 실행
   - 성공: 다음 단계 진행
   - 실패: 그리퍼 열고 재시도 (최대 3회)

3. 재시도 횟수와 결과를 로그로 출력
```

### 과제 2-3: 실시간 모니터링 대시보드
**난이도: ★★★★☆**

```
목표: 로봇 상태를 실시간으로 콘솔에 표시하는 모니터링 도구

요구사항:
1. threading으로 백그라운드에서 상태 수집
   import threading
   monitor_thread = threading.Thread(target=poll_status, daemon=True)

2. 100ms 간격으로 아래 데이터 수집
   - 조인트 각도 6개
   - TCP 위치 6개
   - F/T 센서 6개
   - 디지털 입력 8개

3. 터미널 화면 갱신으로 대시보드 표시
   import os
   os.system('clear')  # 또는 print('\033[H\033[J')

4. 최대/최소 힘 추적 및 경보 (힘 > 임계값 시 *** 표시)
```

---

## Phase 3 과제 (고급)

### 과제 3-1: 팔레타이징 시스템
**난이도: ★★★★☆**

```
목표: 박스를 3D 팔레트에 자동으로 쌓는 프로그램

요구사항:
1. PalletLayout 클래스 구현
   - rows, cols, layers 파라미터
   - next_position() -> (x, y, z) 메서드 (순서대로 다음 위치 반환)
   - is_full() -> bool 메서드
   - reset() 메서드

2. 팔레타이징 루프 구현
   while not pallet.is_full():
       pick_from_conveyor(robot)
       place_x, place_y, place_z = pallet.next_position()
       place_at(robot, place_x, place_y, place_z)

3. 층이 바뀔 때 안전 높이 계산 자동화
   approach_z = place_z + BOX_HEIGHT + SAFETY_MARGIN

4. 완료 후 팔레트 배치 ASCII 시각화
```

### 과제 3-2: 비전 캘리브레이션 도구
**난이도: ★★★★☆**

```
목표: Eye-to-Hand 캘리브레이션을 위한 데이터 수집 도구

요구사항:
1. CalibrationPoint 데이터클래스 정의
   @dataclass
   class CalibrationPoint:
       pixel_x: float
       pixel_y: float
       robot_x: float
       robot_y: float

2. 로봇을 격자(3x3=9개) 위치로 이동 후
   각 위치에서 (픽셀 좌표, 로봇 좌표) 쌍 수집

3. numpy로 변환 행렬(Homography) 계산
   import numpy as np
   # least squares로 affine 변환 계산

4. 검증: 새 픽셀 좌표 입력 시 로봇 좌표 예측
   예측 오차 < 2mm 목표

5. 결과를 JSON 파일로 저장
```

### 과제 3-3: 미니 프로젝트 - 컨베이어 소팅 시스템
**난이도: ★★★★★**

```
목표: 컨베이어에서 부품을 색상별로 분류하는 자동화 시스템 구현

전체 사양:
- 컨베이어에서 부품이 랜덤하게 도착 (빨강/파랑/초록)
- 카메라로 색상 감지
- 색상별로 다른 박스에 적재
- 에러 처리 (파지 실패, 감지 실패)
- 생산 통계 기록 및 출력

구현 요소:
1. ColorDetector 클래스 (시뮬 또는 실제 OpenCV)
2. Sorter 상태 머신 (Phase 3 예제 참고)
   State: IDLE → WAITING → DETECTING → PICKING → SORTING → IDLE
3. 각 색상별 카운터 {red: 0, blue: 0, green: 0}
4. 분당 처리량(throughput) 계산
5. 5분 자동 중지 타이머

평가 기준:
- 상태 머신 완성도
- 에러 처리 견고성
- 코드 가독성 (함수/클래스 분리)
- 통계 출력 완성도
```

---

## 자기 점검 체크리스트

### Phase 1 완료 기준
- [ ] movej, movel 차이를 설명할 수 있다
- [ ] 조인트 공간과 작업 공간의 차이를 안다
- [ ] 속도/가속도 파라미터를 조절할 수 있다
- [ ] 과제 1-1, 1-2, 1-3 완료

### Phase 2 완료 기준
- [ ] numpy로 웨이포인트를 계산할 수 있다
- [ ] 디지털 I/O로 그리퍼를 제어할 수 있다
- [ ] F/T 센서로 접촉을 감지할 수 있다
- [ ] 과제 2-1, 2-2, 2-3 완료

### Phase 3 완료 기준
- [ ] 카메라-로봇 좌표 변환을 구현할 수 있다
- [ ] 상태 머신으로 복잡한 시퀀스를 구조화할 수 있다
- [ ] 에러 복구 로직을 설계할 수 있다
- [ ] 미니 프로젝트(과제 3-3) 완료
