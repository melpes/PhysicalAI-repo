"""LLM 호출: 입력 파일과 프롬프트를 보내고 중립 모델 XML을 받는다."""
import argparse
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--system", required=True, type=Path)
    p.add_argument("--user", required=True, type=Path)
    p.add_argument("--inputs", nargs="*", default=[], type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--key-file", type=Path)
    return p.parse_args()


def main():
    args = parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
