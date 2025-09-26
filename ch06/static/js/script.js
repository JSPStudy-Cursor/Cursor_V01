// DOM 요소들
const generateForm = document.getElementById('generateForm');
const promptInput = document.getElementById('prompt');
const toggleSettingsBtn = document.getElementById('toggleSettings');
const advancedSettings = document.getElementById('advancedSettings');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const resultImage = document.getElementById('resultImage');
const generatedImage = document.getElementById('generatedImage');
const downloadLink = document.getElementById('downloadLink');
const regenerateBtn = document.getElementById('regenerateBtn');
const initialMessage = document.getElementById('initialMessage');

// 상태 관리
let isGenerating = false;

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadDefaultPrompt();
    showInitialMessage(); // 초기 상태 메시지 표시
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 폼 제출
    generateForm.addEventListener('submit', handleFormSubmit);
    
    // 설정 토글
    toggleSettingsBtn.addEventListener('click', toggleAdvancedSettings);
    
    // 초기화 버튼
    resetBtn.addEventListener('click', resetForm);
    
    // 다시 생성 버튼
    regenerateBtn.addEventListener('click', handleRegenerate);
    
    // 입력값 실시간 검증
    promptInput.addEventListener('input', validatePrompt);
    
    // 숫자 입력값 검증
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', validateNumberInput);
    });
}

// 기본 프롬프트 로드
function loadDefaultPrompt() {
    const defaultPrompt = "A serene watercolor landscape of misty mountains at sunrise, ultra-detailed, 4k, masterpiece";
    promptInput.value = defaultPrompt;
}

// 초기 상태 메시지 표시
function showInitialMessage() {
    initialMessage.classList.remove('hidden');
    resultImage.classList.add('hidden');
    loadingIndicator.classList.add('hidden');
    errorMessage.classList.add('hidden');
}

// 고급 설정 토글
function toggleAdvancedSettings() {
    const isHidden = advancedSettings.classList.contains('hidden');
    
    if (isHidden) {
        advancedSettings.classList.remove('hidden');
        toggleSettingsBtn.classList.add('bg-blue-100', 'text-blue-700');
        toggleSettingsBtn.querySelector('.toggle-text').textContent = '⚙️ 고급 설정 숨기기';
        toggleSettingsBtn.querySelector('.toggle-icon').textContent = '▲';
    } else {
        advancedSettings.classList.add('hidden');
        toggleSettingsBtn.classList.remove('bg-blue-100', 'text-blue-700');
        toggleSettingsBtn.querySelector('.toggle-text').textContent = '⚙️ 고급 설정';
        toggleSettingsBtn.querySelector('.toggle-icon').textContent = '▼';
    }
}

// 폼 제출 처리
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isGenerating) {
        return;
    }
    
    // 입력값 검증
    if (!validateForm()) {
        return;
    }
    
    // 생성 시작
    await generateImage();
}

// 폼 검증
function validateForm() {
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showError('프롬프트를 입력해주세요.');
        return false;
    }
    
    if (prompt.length < 3) {
        showError('프롬프트는 최소 3자 이상이어야 합니다.');
        return false;
    }
    
    if (prompt.length > 1000) {
        showError('프롬프트는 최대 1000자까지 입력 가능합니다.');
        return false;
    }
    
    return true;
}

// 프롬프트 실시간 검증
function validatePrompt() {
    const prompt = promptInput.value.trim();
    const errorElement = document.querySelector('.prompt-error');
    
    if (errorElement) {
        errorElement.remove();
    }
    
    if (prompt && prompt.length < 3) {
        const error = document.createElement('div');
        error.className = 'prompt-error text-red-500 text-xs mt-2';
        error.textContent = '프롬프트는 최소 3자 이상이어야 합니다.';
        promptInput.parentNode.appendChild(error);
    }
}

// 숫자 입력값 검증
function validateNumberInput(event) {
    const input = event.target;
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);
    
    if (value < min) {
        input.value = min;
    } else if (value > max) {
        input.value = max;
    }
}

// 이미지 생성
async function generateImage() {
    try {
        setGeneratingState(true);
        hideError();
        hideResult();
        hideInitialMessage();
        showLoading();
        
        // 폼 데이터 수집
        const formData = collectFormData();
        
        // API 호출
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || result.errors?.join(', ') || '알 수 없는 오류가 발생했습니다.');
        }
        
        if (result.success) {
            showResult(result.image_path);
        } else {
            throw new Error(result.error || '이미지 생성에 실패했습니다.');
        }
        
    } catch (error) {
        console.error('이미지 생성 오류:', error);
        showError(error.message);
    } finally {
        setGeneratingState(false);
        hideLoading();
    }
}

// 폼 데이터 수집
function collectFormData() {
    const prompt = promptInput.value.trim();
    const settings = {
        num_inference_steps: parseInt(document.getElementById('steps').value) || 30,
        guidance_scale: parseFloat(document.getElementById('guidance').value) || 7.5,
        width: parseInt(document.getElementById('width').value) || 512,
        height: parseInt(document.getElementById('height').value) || 512,
        model_id: document.getElementById('model').value || 'runwayml/stable-diffusion-v1-5',
        output_prefix: 'sd_v15'
    };
    
    // 시드 값 처리
    const seedValue = document.getElementById('seed').value.trim();
    if (seedValue) {
        settings.seed = parseInt(seedValue);
    }
    
    return {
        prompt: prompt,
        settings: settings
    };
}

// 생성 상태 설정
function setGeneratingState(generating) {
    isGenerating = generating;
    generateBtn.disabled = generating;
    regenerateBtn.disabled = generating;
    
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoading = generateBtn.querySelector('.btn-loading');
    
    if (generating) {
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        generateBtn.classList.add('opacity-75', 'cursor-not-allowed');
    } else {
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
        generateBtn.classList.remove('opacity-75', 'cursor-not-allowed');
    }
}

// 로딩 표시
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

// 로딩 숨기기
function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

// 에러 표시
function showError(message) {
    errorMessage.classList.remove('hidden');
    errorMessage.querySelector('.error-text').textContent = message;
}

// 에러 숨기기
function hideError() {
    errorMessage.classList.add('hidden');
}

// 결과 표시
function showResult(imagePath) {
    generatedImage.src = imagePath;
    downloadLink.href = imagePath;
    downloadLink.download = `generated_image_${Date.now()}.png`;
    
    resultImage.classList.remove('hidden');
    
    // 이미지 로드 완료 후 스크롤
    generatedImage.onload = function() {
        resultImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
}

// 결과 숨기기
function hideResult() {
    resultImage.classList.add('hidden');
}

// 초기 메시지 숨기기
function hideInitialMessage() {
    initialMessage.classList.add('hidden');
}

// 폼 초기화
function resetForm() {
    generateForm.reset();
    loadDefaultPrompt();
    hideError();
    hideResult();
    showInitialMessage();
    
    // 고급 설정 숨기기
    if (!advancedSettings.classList.contains('hidden')) {
        toggleAdvancedSettings();
    }
}

// 다시 생성
function handleRegenerate() {
    if (!isGenerating) {
        generateImage();
    }
}

// 키보드 단축키
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter로 이미지 생성
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        if (!isGenerating) {
            generateImage();
        }
    }
    
    // Escape로 초기화
    if (event.key === 'Escape') {
        event.preventDefault();
        resetForm();
    }
});

// 페이지 언로드 시 경고
window.addEventListener('beforeunload', function(event) {
    if (isGenerating) {
        event.preventDefault();
        event.returnValue = '이미지가 생성 중입니다. 페이지를 나가시겠습니까?';
        return event.returnValue;
    }
});

// 네트워크 상태 모니터링
window.addEventListener('online', function() {
    console.log('네트워크 연결이 복구되었습니다.');
});

window.addEventListener('offline', function() {
    console.log('네트워크 연결이 끊어졌습니다.');
    if (isGenerating) {
        showError('네트워크 연결이 끊어졌습니다. 다시 시도해주세요.');
        setGeneratingState(false);
        hideLoading();
    }
});

// 입력 필드 포커스 효과
document.querySelectorAll('input, textarea, select').forEach(element => {
    element.addEventListener('focus', function() {
        this.parentElement.classList.add('ring-2', 'ring-blue-100');
    });
    
    element.addEventListener('blur', function() {
        this.parentElement.classList.remove('ring-2', 'ring-blue-100');
    });
});

// 부드러운 애니메이션 효과
function addFadeInEffect(element) {
    element.classList.add('animate-fade-in');
}

// 페이지 로드 시 애니메이션
window.addEventListener('load', function() {
    const elements = document.querySelectorAll('.container > *');
    elements.forEach((element, index) => {
        setTimeout(() => {
            addFadeInEffect(element);
        }, index * 100);
    });
});
