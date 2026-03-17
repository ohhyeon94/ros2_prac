"""
[중급 예제 3] 힘/토크 제어 (Force Control)
--------------------------------------------
목표: F/T 센서 데이터를 읽고 힘 기반 제어 구현

학습 포인트:
- get_ft_sensor() 힘/토크 데이터 읽기
- 힘 임계값 기반 조건 분기
- 컴플라이언스 제어 (Compliance Control)
- 삽입(Insertion) 작업에서의 힘 제어 활용
"""

import time
import math
import random   # 시뮬레이션용

ROBOT_IP = "192.168.0.1"

# 힘/토크 임계값 설정
MAX_CONTACT_FORCE   = 10.0   # N   - 접촉 감지 임계값
MAX_SAFE_FORCE      = 50.0   # N   - 안전 최대 힘
INSERT_TARGET_FORCE = 15.0   # N   - 삽입 목표 힘


# ── F/T 센서 래퍼 ─────────────────────────────────────────────────────────────

def get_ft_sensor(robot) -> dict:
    """
    F/T 센서 데이터 반환.

    Returns:
        {'Fx': float, 'Fy': float, 'Fz': float,
         'Tx': float, 'Ty': float, 'Tz': float}  (N, Nm)
    """
    # 실제: return robot.get_ft_sensor()
    # 시뮬레이션: 랜덤 노이즈 포함한 가상 값
    base_fz = random.uniform(-5.0, -3.0)   # 중력 방향 약간의 힘
    return {
        "Fx": random.uniform(-1.0, 1.0),
        "Fy": random.uniform(-1.0, 1.0),
        "Fz": base_fz + random.uniform(-0.5, 0.5),
        "Tx": random.uniform(-0.1, 0.1),
        "Ty": random.uniform(-0.1, 0.1),
        "Tz": random.uniform(-0.1, 0.1),
    }


def get_total_force(ft: dict) -> float:
    """합력(resultant force) 계산."""
    return math.sqrt(ft["Fx"]**2 + ft["Fy"]**2 + ft["Fz"]**2)


def print_ft(ft: dict):
    """F/T 데이터 출력."""
    print(f"  F=({ft['Fx']:+.2f}, {ft['Fy']:+.2f}, {ft['Fz']:+.2f}) N  "
          f"T=({ft['Tx']:+.3f}, {ft['Ty']:+.3f}, {ft['Tz']:+.3f}) Nm  "
          f"|F|={get_total_force(ft):.2f}N")


# ── 예제 1: 실시간 F/T 모니터링 ──────────────────────────────────────────────

def demo_ft_monitoring(robot, duration: float = 5.0, interval: float = 0.2):
    """
    지정 시간 동안 F/T 데이터를 지속적으로 읽어 출력.

    실제 활용: 이상 힘 감지, 로깅
    """
    print(f"\n[F/T 모니터링] {duration}초 동안 {interval}s 간격으로 측정")
    start = time.time()
    samples = []

    while time.time() - start < duration:
        ft = get_ft_sensor(robot)
        samples.append(ft)
        print_ft(ft)

        total = get_total_force(ft)
        if total > MAX_SAFE_FORCE:
            print(f"  ⚠ 과도한 힘 감지! {total:.1f}N > {MAX_SAFE_FORCE}N → 긴급 정지")
            # robot.stop()
            break

        time.sleep(interval)

    # 통계 요약
    if samples:
        fz_values = [s["Fz"] for s in samples]
        print(f"\n  [통계] Fz  평균={sum(fz_values)/len(fz_values):.2f}N  "
              f"최소={min(fz_values):.2f}N  최대={max(fz_values):.2f}N")


# ── 예제 2: 힘 감지 접촉 ─────────────────────────────────────────────────────

def approach_until_contact(robot, direction: str = "z", threshold: float = MAX_CONTACT_FORCE):
    """
    지정 방향으로 천천히 접근하다 접촉 힘이 임계값을 넘으면 정지.

    Args:
        direction : 접근 방향 ('x', 'y', 'z')
        threshold : 접촉 감지 힘 임계값 (N)
    """
    print(f"\n[접촉 탐색] {direction.upper()} 방향, 임계값={threshold}N")
    step    = 1.0   # mm 단위 이동 스텝
    max_steps = 100

    for step_idx in range(max_steps):
        ft = get_ft_sensor(robot)
        total = get_total_force(ft)
        print(f"  스텝 {step_idx+1:3d}: |F|={total:.2f}N", end="")

        if total > threshold:
            print(f" → 접촉 감지! 정지")
            # robot.stop()
            return True

        print()
        # 실제: robot.movel(current_pos + step * direction_vector, speed=5)
        time.sleep(0.05)

    print("  최대 스텝 도달, 접촉 없음")
    return False


# ── 예제 3: 힘 제어 삽입 (Peg-in-Hole) ──────────────────────────────────────

def peg_in_hole_insertion(robot, target_force: float = INSERT_TARGET_FORCE):
    """
    Peg-in-Hole 조립 작업:
    1) 접촉할 때까지 하강
    2) 목표 힘에 도달할 때까지 삽입
    3) 삽입 완료 후 힘 해제

    산업 응용: 커넥터 삽입, 베어링 압입 등
    """
    print(f"\n[Peg-in-Hole 삽입] 목표 힘={target_force}N")

    # 단계 1: 접촉 탐색
    print("  단계 1: 접촉 탐색")
    contacted = approach_until_contact(robot, "z", threshold=MAX_CONTACT_FORCE)
    if not contacted:
        print("  삽입 실패: 대상 없음")
        return False

    # 단계 2: 목표 힘까지 삽입
    print("\n  단계 2: 삽입 (목표 힘 달성)")
    for _ in range(50):
        ft = get_ft_sensor(robot)
        fz = abs(ft["Fz"])
        print(f"  Fz={fz:.1f}N (목표: {target_force}N)")

        if fz >= target_force:
            print("  목표 힘 달성! 삽입 완료")
            break

        # 실제: 미세 하강 이동
        time.sleep(0.1)

    # 단계 3: 위치 유지 후 완료
    print("\n  단계 3: 위치 유지 (1초)")
    time.sleep(1.0)
    print("  삽입 작업 완료")
    return True


def main():
    robot = None

    try:
        demo_ft_monitoring(robot, duration=3.0)
        approach_until_contact(robot, threshold=8.0)
        peg_in_hole_insertion(robot)
    finally:
        print("\n[종료]")


if __name__ == "__main__":
    main()
