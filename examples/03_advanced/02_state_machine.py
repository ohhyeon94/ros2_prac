"""
[고급 예제 2] 상태 머신 기반 자동화 태스크
----------------------------------------------
목표: 실제 산업 자동화에 쓰이는 상태 머신 구조로 로봇 태스크 설계

학습 포인트:
- 유한 상태 머신(FSM) 패턴
- 에러 처리 및 복구 로직
- 생산성 통계 수집 (사이클 타임, 성공률)
- 모듈화된 태스크 구조
"""

import time
import random
from enum import Enum, auto
from dataclasses import dataclass, field


# ── 상태 정의 ─────────────────────────────────────────────────────────────────

class State(Enum):
    IDLE          = auto()   # 대기
    HOMING        = auto()   # 홈 이동
    WAITING_PART  = auto()   # 부품 대기
    PICKING       = auto()   # 픽업
    INSPECTING    = auto()   # 검사
    PLACING_OK    = auto()   # 양품 적재
    PLACING_NG    = auto()   # 불량품 처리
    ERROR         = auto()   # 에러
    RECOVERING    = auto()   # 에러 복구
    FINISHED      = auto()   # 완료


# ── 데이터 클래스 ─────────────────────────────────────────────────────────────

@dataclass
class TaskStats:
    """사이클 통계 데이터."""
    total_cycles:   int   = 0
    ok_count:       int   = 0
    ng_count:       int   = 0
    error_count:    int   = 0
    cycle_times:    list  = field(default_factory=list)
    start_time:     float = field(default_factory=time.time)

    @property
    def ok_rate(self) -> float:
        if self.total_cycles == 0:
            return 0.0
        return self.ok_count / self.total_cycles * 100

    @property
    def avg_cycle_time(self) -> float:
        if not self.cycle_times:
            return 0.0
        return sum(self.cycle_times) / len(self.cycle_times)

    def report(self):
        elapsed = time.time() - self.start_time
        print(f"\n{'='*40}")
        print(f"  총 사이클   : {self.total_cycles}")
        print(f"  양품 (OK)   : {self.ok_count} ({self.ok_rate:.1f}%)")
        print(f"  불량 (NG)   : {self.ng_count}")
        print(f"  에러        : {self.error_count}")
        print(f"  평균 사이클 : {self.avg_cycle_time:.2f}s")
        print(f"  총 경과     : {elapsed:.1f}s")
        print(f"{'='*40}\n")


# ── 로봇 동작 스텁 ───────────────────────────────────────────────────────────

def move_home(robot):
    print("    → 홈 이동")
    time.sleep(0.3)

def move_pick(robot):
    print("    → 픽업 위치 이동")
    time.sleep(0.3)

def move_inspect(robot):
    print("    → 검사 위치 이동")
    time.sleep(0.2)

def move_place_ok(robot):
    print("    → 양품 팔레트 이동")
    time.sleep(0.3)

def move_place_ng(robot):
    print("    → 불량 박스 이동")
    time.sleep(0.3)

def gripper_close(robot):
    print("    → 그리퍼 닫기")
    time.sleep(0.2)

def gripper_open(robot):
    print("    → 그리퍼 열기")
    time.sleep(0.2)

def check_part_sensor(robot) -> bool:
    """부품 감지 센서 (시뮬: 80% 확률로 감지)."""
    detected = random.random() < 0.8
    print(f"    → 센서: {'감지' if detected else '미감지'}")
    return detected

def inspect_part(robot) -> str:
    """품질 검사 (시뮬: 85% OK, 15% NG)."""
    result = "OK" if random.random() < 0.85 else "NG"
    print(f"    → 검사 결과: {result}")
    time.sleep(0.3)
    return result

def simulate_random_error() -> bool:
    """랜덤 에러 발생 (시뮬: 5% 확률)."""
    return random.random() < 0.05


# ── 상태 머신 클래스 ─────────────────────────────────────────────────────────

class RobotTaskFSM:
    """
    유한 상태 머신 기반 로봇 태스크 컨트롤러.

    전이 다이어그램:
    IDLE → HOMING → WAITING_PART → PICKING → INSPECTING
         ↓                                        ↓
      FINISHED                          PLACING_OK / PLACING_NG
                                              ↓
                                         WAITING_PART (반복)
    어느 상태에서나 에러 발생 시 → ERROR → RECOVERING → HOMING
    """

    def __init__(self, robot, max_cycles: int = 5):
        self.robot      = robot
        self.max_cycles = max_cycles
        self.state      = State.IDLE
        self.stats      = TaskStats()
        self.error_count_consecutive = 0
        self.MAX_CONSECUTIVE_ERRORS  = 3
        self._inspection_result      = None
        self._cycle_start            = 0.0

    def transition(self, new_state: State):
        print(f"  [{self.state.name}] → [{new_state.name}]")
        self.state = new_state

    def run(self):
        """메인 루프: 상태 머신 실행."""
        print(f"\n{'='*40}")
        print(f"  태스크 시작 (목표 {self.max_cycles}사이클)")
        print(f"{'='*40}")

        while self.state != State.FINISHED:
            self._execute_current_state()

        self.stats.report()

    def _execute_current_state(self):
        """현재 상태 액션 실행."""

        # 공통: 랜덤 에러 시뮬레이션
        if self.state not in (State.IDLE, State.ERROR, State.RECOVERING, State.FINISHED):
            if simulate_random_error():
                print(f"  ⚠ 에러 발생!")
                self.stats.error_count += 1
                self.error_count_consecutive += 1
                self.transition(State.ERROR)
                return

        # ── 각 상태 처리 ─────────────────────────────────────────────────────

        if self.state == State.IDLE:
            print(f"\n[사이클 {self.stats.total_cycles + 1}/{self.max_cycles}] 시작")
            self._cycle_start = time.time()
            self.transition(State.HOMING)

        elif self.state == State.HOMING:
            move_home(self.robot)
            self.transition(State.WAITING_PART)

        elif self.state == State.WAITING_PART:
            print("  부품 대기 중...")
            for _ in range(5):
                if check_part_sensor(self.robot):
                    self.transition(State.PICKING)
                    return
                time.sleep(0.5)
            print("  부품 타임아웃, 다시 대기")

        elif self.state == State.PICKING:
            move_pick(self.robot)
            gripper_close(self.robot)
            self.transition(State.INSPECTING)

        elif self.state == State.INSPECTING:
            move_inspect(self.robot)
            self._inspection_result = inspect_part(self.robot)
            if self._inspection_result == "OK":
                self.transition(State.PLACING_OK)
            else:
                self.transition(State.PLACING_NG)

        elif self.state == State.PLACING_OK:
            move_place_ok(self.robot)
            gripper_open(self.robot)
            self.stats.ok_count += 1
            self._finish_cycle()

        elif self.state == State.PLACING_NG:
            move_place_ng(self.robot)
            gripper_open(self.robot)
            self.stats.ng_count += 1
            self._finish_cycle()

        elif self.state == State.ERROR:
            if self.error_count_consecutive >= self.MAX_CONSECUTIVE_ERRORS:
                print(f"  연속 에러 {self.MAX_CONSECUTIVE_ERRORS}회 → 긴급 정지")
                self.transition(State.FINISHED)
            else:
                print("  에러 복구 시도...")
                self.transition(State.RECOVERING)

        elif self.state == State.RECOVERING:
            time.sleep(1.0)  # 복구 대기
            self.error_count_consecutive = 0
            print("  복구 완료")
            self.transition(State.HOMING)

    def _finish_cycle(self):
        """한 사이클 완료 처리."""
        cycle_time = time.time() - self._cycle_start
        self.stats.cycle_times.append(cycle_time)
        self.stats.total_cycles += 1
        self.error_count_consecutive = 0

        print(f"  ✓ 사이클 완료 ({cycle_time:.2f}s) | "
              f"OK={self.stats.ok_count} NG={self.stats.ng_count}")

        if self.stats.total_cycles >= self.max_cycles:
            self.transition(State.FINISHED)
        else:
            self.transition(State.IDLE)


def main():
    robot = None

    fsm = RobotTaskFSM(robot, max_cycles=8)
    fsm.run()


if __name__ == "__main__":
    main()
