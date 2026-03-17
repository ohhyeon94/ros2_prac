"""
[중급 예제 2] 디지털/아날로그 I/O 제어
-----------------------------------------
목표: 그리퍼, 센서, 컨베이어 등 주변 장치를 I/O로 제어하기

학습 포인트:
- 디지털 출력(DO) 제어 → 그리퍼, 솔레노이드 밸브
- 디지털 입력(DI) 읽기 → 센서, 리밋 스위치
- 아날로그 출력(AO) → 속도 제어
- I/O 기반 조건 분기 (픽앤플레이스 자동화)
"""

import time

ROBOT_IP = "192.168.0.1"

# I/O 핀 번호 정의 (실제 배선에 맞게 수정)
PIN_GRIPPER_OPEN  = 0   # DO: 그리퍼 열기
PIN_GRIPPER_CLOSE = 1   # DO: 그리퍼 닫기
PIN_VACUUM_ON     = 2   # DO: 진공 흡착 ON
PIN_PART_DETECT   = 0   # DI: 부품 감지 센서
PIN_GRIPPER_DONE  = 1   # DI: 그리퍼 완료 신호
PIN_SPEED_CTRL    = 0   # AO: 컨베이어 속도 제어


# ── I/O 래퍼 함수 ────────────────────────────────────────────────────────────

def set_do(robot, pin: int, value: bool):
    """디지털 출력 설정."""
    # robot.set_do(pin, value)
    state = "ON " if value else "OFF"
    print(f"  [DO] 핀 {pin} → {state}")


def get_di(robot, pin: int) -> bool:
    """디지털 입력 읽기."""
    # return robot.get_di(pin)
    import random
    value = random.choice([True, False])   # 시뮬레이션
    print(f"  [DI] 핀 {pin} → {'HIGH' if value else 'LOW'} (시뮬)")
    return value


def set_ao(robot, pin: int, voltage: float):
    """아날로그 출력 설정 (0~10V)."""
    # robot.set_ao(pin, voltage)
    print(f"  [AO] 핀 {pin} → {voltage:.2f}V")


def wait_di(robot, pin: int, expected: bool, timeout: float = 5.0) -> bool:
    """
    디지털 입력이 expected 값이 될 때까지 대기.

    Args:
        pin     : DI 핀 번호
        expected: 기다리는 신호 값 (True=HIGH, False=LOW)
        timeout : 최대 대기 시간 (초)

    Returns:
        True if signal received, False if timeout
    """
    print(f"  [대기] DI 핀 {pin} = {'HIGH' if expected else 'LOW'} 대기 (최대 {timeout}초)")
    start = time.time()
    while time.time() - start < timeout:
        if get_di(robot, pin) == expected:
            print(f"  [대기] 신호 감지! ({time.time()-start:.2f}초 경과)")
            return True
        time.sleep(0.1)
    print(f"  [대기] 타임아웃!")
    return False


# ── 그리퍼 제어 클래스 ───────────────────────────────────────────────────────

class GripperController:
    """디지털 I/O 기반 그리퍼 제어 클래스."""

    def __init__(self, robot, open_pin: int, close_pin: int, done_pin: int):
        self.robot     = robot
        self.open_pin  = open_pin
        self.close_pin = close_pin
        self.done_pin  = done_pin

    def open(self, wait: bool = True, timeout: float = 3.0) -> bool:
        """그리퍼 열기."""
        print("\n  [그리퍼] 열기")
        set_do(self.robot, self.close_pin, False)
        set_do(self.robot, self.open_pin, True)
        if wait:
            return wait_di(self.robot, self.done_pin, True, timeout)
        return True

    def close(self, wait: bool = True, timeout: float = 3.0) -> bool:
        """그리퍼 닫기 (파지)."""
        print("\n  [그리퍼] 닫기")
        set_do(self.robot, self.open_pin, False)
        set_do(self.robot, self.close_pin, True)
        if wait:
            return wait_di(self.robot, self.done_pin, True, timeout)
        return True


# ── 자동화 시나리오 ──────────────────────────────────────────────────────────

def demo_gripper_cycle(robot):
    """그리퍼 열기/닫기 사이클 데모."""
    print("\n[그리퍼 사이클 데모]")
    gripper = GripperController(
        robot,
        open_pin=PIN_GRIPPER_OPEN,
        close_pin=PIN_GRIPPER_CLOSE,
        done_pin=PIN_GRIPPER_DONE,
    )

    for i in range(3):
        print(f"\n  사이클 {i+1}")
        gripper.open()
        time.sleep(0.5)
        gripper.close()
        time.sleep(0.5)


def demo_sensor_triggered_move(robot):
    """
    센서가 부품을 감지하면 픽업 동작을 수행하는 시나리오.
    실제 공정에서 컨베이어 위 부품을 픽업할 때 사용.
    """
    print("\n[센서 트리거 이동 데모]")
    gripper = GripperController(
        robot,
        open_pin=PIN_GRIPPER_OPEN,
        close_pin=PIN_GRIPPER_CLOSE,
        done_pin=PIN_GRIPPER_DONE,
    )
    gripper.open(wait=False)

    print("  부품 감지 대기 중...")
    detected = wait_di(robot, PIN_PART_DETECT, True, timeout=10.0)

    if detected:
        print("  부품 감지! 픽업 동작 실행")
        # 실제: robot.movel(PICK_POS, ...)
        gripper.close()
        print("  픽업 완료, 플레이스 위치로 이동")
        # 실제: robot.movel(PLACE_POS, ...)
        gripper.open()
    else:
        print("  부품 미감지 - 동작 스킵")


def demo_analog_speed_control(robot):
    """아날로그 출력으로 컨베이어 속도를 단계적으로 제어."""
    print("\n[아날로그 속도 제어 데모]")
    # 0V → 2V → 5V → 8V → 10V → 0V
    for voltage in [0.0, 2.0, 5.0, 8.0, 10.0, 0.0]:
        speed_pct = voltage / 10.0 * 100
        print(f"  컨베이어 속도: {speed_pct:.0f}% ({voltage}V)")
        set_ao(robot, PIN_SPEED_CTRL, voltage)
        time.sleep(1.0)


def main():
    robot = None

    try:
        demo_gripper_cycle(robot)
        demo_sensor_triggered_move(robot)
        demo_analog_speed_control(robot)
    finally:
        # 안전: 모든 출력 OFF
        print("\n[안전 종료] 모든 DO OFF")
        for pin in range(8):
            set_do(robot, pin, False)


if __name__ == "__main__":
    main()
