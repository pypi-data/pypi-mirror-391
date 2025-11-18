"""
Google API를 사용하여 나노 바나나 이미지를 생성하고 다운로드하는 스크립트

사용 가능한 API:
1. Google Vertex AI Imagen API - 이미지 생성 지원
2. OpenAI DALL-E API - 이미지 생성 지원
3. Google Gemini API - 텍스트 생성만 지원 (이미지 생성 불가)

주의: Google AI Studio (aistudio.google.com)는 이미지 생성을 지원하지 않습니다.
이미지 생성을 위해서는 Vertex AI의 Imagen을 사용하거나 DALL-E를 사용하세요.
"""
import os
import sys
import requests
from pathlib import Path
from typing import Optional
import google.generativeai as genai


def generate_image_with_openai(prompt: str, api_key: str, output_path: str = "nano_banana_image.png") -> bool:
    """
    OpenAI DALL-E API를 사용하여 이미지를 생성하고 다운로드합니다.
    
    Args:
        prompt: 이미지 생성을 위한 프롬프트
        api_key: OpenAI API 키
        output_path: 저장할 파일 경로
        
    Returns:
        성공 여부
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        print(f"이미지 생성 중... 프롬프트: {prompt}")
        
        # DALL-E 3을 사용하여 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        # 이미지 다운로드
        print(f"이미지 다운로드 중: {image_url}")
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        # 파일 저장
        with open(output_path, "wb") as f:
            f.write(image_response.content)
        
        print(f"✅ 이미지가 성공적으로 저장되었습니다: {output_path}")
        return True
        
    except ImportError:
        print("❌ 오류: openai 라이브러리가 설치되지 않았습니다.")
        print("설치 방법: pip install openai")
        return False
    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return False


def generate_image_with_gemini(prompt: str, api_key: str, output_path: str = "nano_banana_image.png") -> bool:
    """
    Google Gemini API를 사용합니다.
    
    ⚠️ 주의: Gemini API는 이미지 생성을 지원하지 않습니다.
    Google AI Studio (aistudio.google.com)를 통한 이미지 생성은 불가능합니다.
    이미지 생성이 필요하면 Vertex AI Imagen 또는 DALL-E를 사용하세요.
    
    Args:
        prompt: 이미지 생성을 위한 프롬프트
        api_key: Google Gemini API 키
        output_path: 저장할 파일 경로
        
    Returns:
        항상 False (이미지를 생성하지 않음 accidently)
    """
    try:
        print("\n" + "=" * 60)
        print("⚠️  중요: Gemini API는 이미지 생성이 불가능합니다")
        print("=" * 60)
        print("\nGoogle AI Studio (aistudio.google.com)에서 제공하는")
        print("Gemini 모델은 텍스트 생성만 지원합니다.")
        print("\n이미지 생성을 위해서는 다음 중 하나를 사용하세요:")
        print("  1. Google Vertex AI Imagen")
        print("  2. OpenAI DALL-E")
        print("  3. Stable Diffusion API")
        print("\n" + "=" * 60 + "\n")
        
        # API 설정
        genai.configure(api_key=api_key)
        
        # 모델 초기화 (이미지 생성이 아닌 텍스트 생성용)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # 나노 바나나에 대한 설명 요청
        enhanced_prompt = f"""나노 바나나(nanobanana)는 귀여운 작은 동그란 바나나 캐릭터입니다.
        
위 캐릭터를 이미지로 만들기 위한 상세한 프롬프트를 작성해주세요.
간단하고 명확한 영어 프롬프트로 작성해주세요."""
        
        print("Gemini에게 이미지 프롬프트 작성을 요청 중...")
        response = model.generate_content(enhanced_prompt)
        
        print("\n" + "=" * 60)
        print("Gemini가 추천한 이미지 생성 프롬프트:")
        print("=" * 60)
        print(response.text)
        print("=" * 60 + "\n")
        
        return False
        
    except ImportError:
        print("❌ 오류: google-generativeai 라이브러리가 설치되지 않았습니다.")
        print("설치 방법: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini API 호출 실패: {e}")
        return False


def generate_image_with_vertex_ai(prompt: str, project_id: str, location: str = "us-central1", output_path: str = "nano_banana_image.png") -> bool:
    """
    Google Vertex AI Imagen API를 사용하여 이미지를 생성합니다.
    
    ⚠️ 주의: 이 기능은 Google Cloud Vertex AI 계정이 필요합니다.
    
    Args:
        prompt: 이미지 생성을 위한 프롬프트
        project_id: Google Cloud 프로젝트 ID
        location: 리전 (기본값: us-central1)
        output_path: 저장할 파일 경로
        
    Returns:
        성공 여부
    """
    try:
        from vertexai.generative_models import Image
        
        print(f"⚠️  Vertex AI Imagen은 별도 구현이 필요합니다.")
        print(f"Google Cloud 계정과 프로젝트 설정이 필요합니다.")
        print(f"\n자세한 내용: https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images")
        
        # 실제 구현 예시
        # from vertexai.preview import generative_models
        # model = generative_models.GenerativeModel("imagegeneration@006")
        # images = model.generate_images(prompt=prompt, number_of_images=1)
        # images[0].save(output_path)
        
        return False
        
    except ImportError:
        print("❌ 오류: google-cloud-aiplatform 라이브러리가 설치되지 않았습니다.")
        print("설치 방법: pip install google-cloud-aiplatform")
        return False
    except Exception as e:
        print(f"❌ Vertex AI API 호출 실패: {e}")
        return False


def main():
    """메인 함수"""
    # API 키 설정 (환경변수 또는 직접 입력)
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print("google_api_key", google_api_key)
    # 프롬프트 설정
    prompt = "A cute round little banana character with big eyes, called nanobanana, in a simple cartoon style with bright yellow color"
    
    # 출력 파일 경로
    output_file = "nanobanana_image.png"
    
    print("=" * 60)
    print("나노 바나나 이미지 생성기")
    print("=" * 60)
    print(f"프롬프트: {prompt}")
    print()
    
    # 먼저 OpenAI DALL-E API를 사용하여 이미지 생성 시도
    if openai_api_key:
        print("1️⃣  OpenAI DALL-E API 사용 시도 중...")
        if generate_image_with_openai(prompt, openai_api_key, output_file):
            print("\n✅ 성공!")
            return
        print()
    else:
        print("⚠️  OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print()
    
    # Gemini API 시도 (텍스트 응답만 제공)
    if google_api_key:
        print("2️⃣  Google Gemini API 사용 (이미지 생성 불가, 프롬프트 추천용)")
        generate_image_with_gemini(prompt, google_api_key, output_file)
    else:
        print("⚠️  GOOGLE_API_KEY 또는 GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print()
    
    print("\n" + "=" * 60)
    print("📋 사용 가능한 이미지 생성 옵션:")
    print("=" * 60)
    print()
    print("✅ 1. OpenAI DALL-E API (권장 - 가장 간단)")
    print("   set OPENAI_API_KEY=your_key_here")
    print("   python create_image_using_nanobanana.py")
    print()
    print("❌ 2. Google AI Studio (Gemini)")
    print("   → 이미지 생성 불가능 (텍스트 생성만 가능)")
    print()
    print("✅ 3. Google Vertex AI (Imagen)")
    print("   → Google Cloud 계정 필요")
    print("   → 별도 구현 필요")
    print("   참고: https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images")
    print()
    print("=" * 60)
    print("📚 API 키 발급:")
    print("=" * 60)
    print("OpenAI: https://platform.openai.com/api-keys")
    print("Google AI Studio: https://aistudio.google.com/ (이미지 생성 불가)")
    print("=" * 60)


if __name__ == "__main__":
    main()

