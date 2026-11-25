# neutral_model

연합표준 정합표현체계의 중립 모델(XML)과, 이를 각 시뮬레이션 환경으로 변환·검증하는 코드입니다.

## 폴더 구조

```
neutral_model/
├── scenes/                  중립 모델 원본 (사람이 편집하는 유일한 원본)
│   ├── box.neutral.xml
│   └── irb4600_40_255.neutral.xml
├── common/                  모든 환경이 함께 쓰는 파이썬 코드
│   ├── neutral_scene.py         규약 확인, Object 읽기
│   ├── neutral_robot.py         Robot 읽기, 기준 순기구학
│   ├── rotation.py              쿼터니언·회전 계산
│   └── make_robot_test_poses.py 공통 시험 자세 생성
├── tests/                   공통 시험 자세 (생성물)
├── for_mujoco/              MuJoCo용 변환·실행·검증 (+ outputs/)
├── for_matlab/              MATLAB용 변환·실행·검증 (+ outputs/)
├── for_visual_components/   Visual Components용 변환 (+ outputs/)
└── for_blender/             Blender용 변환·검증 (+ outputs/)
```

- `outputs/`와 `tests/`는 생성물입니다. 직접 고치지 말고, scenes의 XML을 고친 뒤 다시 생성합니다.
- 폴더 이름을 `mujoco/`가 아니라 `for_mujoco/`로 한 이유: 같은 이름의 폴더가 있으면 파이썬이 설치된 `mujoco` 패키지 대신 그 폴더를 불러올 수 있기 때문입니다.
- 모든 명령은 `neutral_model` 폴더에서 실행합니다.

## 중립 XML 규칙 (version 0.3)

| 규칙 | 내용 |
|---|---|
| 규약 | 모든 파일이 version, unit, angleUnit, massUnit, timeUnit, upAxis, handedness, colorSpace를 같은 값으로 선언 |
| 위치·회전 | `Pose` 하나로 통일. 기준 좌표계는 항상 `relativeTo`로 명시 (`World` 또는 Link id) |
| 정의와 배치 | `Robot`은 사양 정의, `Object ref="..."`는 장면 안 배치 |
| 식별자 | 모든 요소에 `id`. 단어는 PascalCase, 번호·변형은 `_`로 구분 (예: `Box_01`, `Link1_Visual`) |
| 열거값 | PascalCase (`Box`, `Revolute`, `World`) |
| 출처 | `Sources/Source`에 정의하고, 어느 요소든 `source="..."`로 참조 |
| 근사 표시 | `approximate="true|false"` |
| Specification 용어 | payload, armload, mass (massUnit) / reach, height, positionRepeatability, pathRepeatability (unit) |

## 실행 (Ubuntu)

```bash
cd ~/neutral_model
source ~/.venvs/neutral_box/bin/activate

# 박스
python for_mujoco/to_mujoco.py scenes/box.neutral.xml for_mujoco/outputs/box_mujoco.xml
python for_mujoco/verify_mujoco.py scenes/box.neutral.xml for_mujoco/outputs/box_mujoco.xml
python for_mujoco/run_in_mujoco.py scenes/box.neutral.xml
python for_matlab/to_matlab.py scenes/box.neutral.xml for_matlab/outputs/box_matlab.m
python for_visual_components/to_visual_components.py scenes/box.neutral.xml for_visual_components/outputs/box_vc.py
python for_blender/to_blender.py scenes/box.neutral.xml for_blender/outputs/box_blender.py

# 로봇
python common/make_robot_test_poses.py scenes/irb4600_40_255.neutral.xml tests/irb4600_test_poses.csv
python for_mujoco/to_mujoco_robot.py scenes/irb4600_40_255.neutral.xml for_mujoco/outputs/irb4600_mujoco.xml
python for_mujoco/verify_mujoco_robot.py scenes/irb4600_40_255.neutral.xml for_mujoco/outputs/irb4600_mujoco.xml tests/irb4600_test_poses.csv
python -m mujoco.viewer --mjcf=for_mujoco/outputs/irb4600_mujoco.xml
python for_visual_components/to_visual_components_robot.py scenes/irb4600_40_255.neutral.xml tests/irb4600_test_poses.csv for_visual_components/outputs/irb4600_vc_check.py
```

## 실행 (MATLAB)

```matlab
cd('C:\...\연합표준정합표현체계\neutral_model')
addpath(fullfile(pwd, 'for_matlab'))
run_in_matlab('scenes/box.neutral.xml')
verify_matlab('scenes/box.neutral.xml', 'for_matlab/outputs/box_matlab.m')
run_in_matlab_robot('scenes/irb4600_40_255.neutral.xml', [30 20 -10 40 30 60])
verify_matlab_robot('scenes/irb4600_40_255.neutral.xml', 'tests/irb4600_test_poses.csv')
```

## 실행 (Visual Components)

MODELING → New로 빈 컴포넌트를 만들고 Behaviors → Python Script를 추가한 뒤,
`for_visual_components/outputs/`의 스크립트 내용을 붙여 넣고 Compile 합니다.
로봇 검증은 먼저 eCatalog에서 ABB IRB 4600-40/2.55를 배치해야 합니다.
