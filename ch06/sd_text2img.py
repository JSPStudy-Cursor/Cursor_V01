import os
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import torch
from diffusers import StableDiffusionPipeline


def _get_torch_device() -> str:
    """
    사용 가능한 디바이스를 반환한다. CUDA가 가능하면 'cuda', 아니면 'cpu'.
    """
    try:
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        # 예외 발생 시 안전하게 CPU 사용
        return "cpu"


def _to_multiple_of_8(value: int) -> int:
    """
    이미지 너비/높이는 8의 배수여야 하므로 자동으로 가장 가까운 8의 배수로 맞춘다.
    """
    if value <= 0:
        return 512
    return int(round(value / 8) * 8)


def _ensure_output_dir(output_dir: Path) -> None:
    """
    출력 디렉토리를 보장한다.
    """
    output_dir.mkdir(parents=True, exist_ok=True)


def _load_pipeline(model_id: str, device: str) -> StableDiffusionPipeline:
    """
    Stable Diffusion 파이프라인을 로드한다. GPU가 있으면 FP16, 없으면 FP32로 로드한다.
    무거운 초기화를 한 번만 수행하도록 전역 캐시를 사용한다.
    """
    # 간단한 전역 캐시 구현
    global _PIPELINE_CACHE
    if "_PIPELINE_CACHE" not in globals():
        _PIPELINE_CACHE = {}

    cache_key = (model_id, device)
    if cache_key in _PIPELINE_CACHE:
        return _PIPELINE_CACHE[cache_key]

    use_fp16 = device == "cuda"
    torch_dtype = torch.float16 if use_fp16 else torch.float32

    # 모델 로드 (기본 safety_checker 유지)
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        use_safetensors=True,
    )

    if device == "cuda":
        pipe = pipe.to("cuda")
        # GPU 메모리 최적화 옵션 (안전한 기본값)
        pipe.enable_attention_slicing()
    else:
        # CPU 메모리 사용량을 줄이기 위한 옵션
        pipe.enable_attention_slicing()

    _PIPELINE_CACHE[cache_key] = pipe
    return pipe


def generate_image_from_text(
    prompt: str,
    *,
    model_id: str = "runwayml/stable-diffusion-v1-5",
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
    width: int = 512,
    height: int = 512,
    seed: Optional[int] = None,
    output_dir: str = "outputs",
    output_prefix: str = "sd_v15",
) -> str:
    """
    텍스트 프롬프트로 이미지를 생성하여 PNG 파일로 저장한다.

    매개변수
    - prompt: 텍스트 프롬프트
    - model_id: 사용할 diffusers 모델 식별자
    - num_inference_steps: 추론 단계 수 (클수록 품질↑, 속도↓)
    - guidance_scale: 프롬프트 준수 강도 (클수록 프롬프트에 더 충실)
    - width, height: 출력 이미지 크기 (8의 배수로 자동 보정)
    - seed: 랜덤 시드 (None이면 자동 생성)
    - output_dir: 출력 폴더
    - output_prefix: 파일명 접두어

    반환
    - 저장된 PNG 파일 경로 문자열
    """
    # 입력값 검증 및 안전한 기본값 처리
    if not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise ValueError("prompt는 비어 있을 수 없습니다.")

    if not isinstance(num_inference_steps, int) or num_inference_steps <= 0:
        num_inference_steps = 30

    if not isinstance(guidance_scale, (int, float)) or guidance_scale <= 0:
        guidance_scale = 7.5

    width = _to_multiple_of_8(int(width))
    height = _to_multiple_of_8(int(height))

    # 디바이스/파이프라인 준비
    device = _get_torch_device()
    pipe = _load_pipeline(model_id=model_id, device=device)

    # 랜덤 시드 처리
    if seed is None:
        # 시스템 랜덤으로 안전하게 시드 생성
        seed = int.from_bytes(os.urandom(4), "big")

    generator = torch.Generator(device=device).manual_seed(int(seed))

    # 출력 경로 준비
    output_path = Path(output_dir)
    _ensure_output_dir(output_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_prefix}_{timestamp}_seed{seed}_w{width}h{height}.png"
    file_path = str(output_path / filename)

    # 이미지 생성
    try:
        torch.set_grad_enabled(False)
        if device == "cuda":
            # 자동 혼합 정밀도는 FP16에서 성능에 유리
            with torch.autocast("cuda"):
                image = pipe(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=float(guidance_scale),
                    width=width,
                    height=height,
                    generator=generator,
                ).images[0]
        else:
            # CPU에서는 autocast 미사용
            image = pipe(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=float(guidance_scale),
                width=width,
                height=height,
                generator=generator,
            ).images[0]

        image.save(file_path)
        return file_path
    except RuntimeError as e:
        # 흔한 OOM 등 런타임 오류를 감싸서 전달
        raise RuntimeError(f"이미지 생성 중 오류가 발생했습니다: {e}") from e
    except Exception as e:
        raise RuntimeError(f"알 수 없는 오류가 발생했습니다: {e}") from e


__all__ = ["generate_image_from_text"]


