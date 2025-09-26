import argparse
from sd_text2img import generate_image_from_text


def _run_default_generation() -> None:
    """
    기본 프롬프트와 옵션으로 이미지를 1장 생성한다.
    첫 실행 시 자동으로 동작하도록 구성.
    """
    # 기본값은 품질/속도의 균형을 고려한 설정
    default_prompt = (
        "A serene watercolor landscape of misty mountains at sunrise, ultra-detailed, 4k"
    )
    output_path = generate_image_from_text(
        prompt=default_prompt,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=512,
        height=512,
        seed=42,
    )
    print(f"이미지가 생성되어 저장되었습니다: {output_path}")


def _parse_args() -> argparse.Namespace:
    """
    명령행 인자를 파싱한다. 인자를 주지 않으면 기본 실행으로 동작한다.
    """
    parser = argparse.ArgumentParser(
        description="Stable Diffusion v1-5 텍스트→이미지 생성 스크립트",
    )
    parser.add_argument("--prompt", type=str, default=None, help="텍스트 프롬프트")
    parser.add_argument("--model-id", type=str, default="runwayml/stable-diffusion-v1-5", help="모델 ID")
    parser.add_argument("--steps", type=int, default=30, help="추론 단계 수")
    parser.add_argument("--guidance", type=float, default=7.5, help="프롬프트 준수 강도")
    parser.add_argument("--width", type=int, default=512, help="이미지 너비 (8의 배수)")
    parser.add_argument("--height", type=int, default=512, help="이미지 높이 (8의 배수)")
    parser.add_argument("--seed", type=int, default=None, help="랜덤 시드 (미지정 시 무작위)")
    parser.add_argument("--output-dir", type=str, default="outputs", help="출력 디렉토리")
    parser.add_argument("--output-prefix", type=str, default="sd_v15", help="파일명 접두어")
    return parser.parse_args()


def _run_with_args(args: argparse.Namespace) -> None:
    """
    인자로 받은 옵션으로 이미지를 생성한다. 프롬프트가 없으면 기본 실행으로 대체한다.
    """
    if not args.prompt:
        _run_default_generation()
        return

    out = generate_image_from_text(
        prompt=args.prompt,
        model_id=args.model_id,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance,
        width=args.width,
        height=args.height,
        seed=args.seed,
        output_dir=args.output_dir,
        output_prefix=args.output_prefix,
    )
    print(f"이미지가 생성되어 저장되었습니다: {out}")


if __name__ == "__main__":
    _run_with_args(_parse_args())


