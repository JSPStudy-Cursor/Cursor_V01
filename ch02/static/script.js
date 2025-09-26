// 캔버스 관련 변수
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let drawing = false;
let lastX = 0, lastY = 0;

// 캔버스 초기화 함수
function clearCanvas() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// 마우스 이벤트 처리
canvas.addEventListener('mousedown', e => {
    drawing = true;
    [lastX, lastY] = [e.offsetX, e.offsetY];
});
canvas.addEventListener('mousemove', e => {
    if (!drawing) return;
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 18;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
    [lastX, lastY] = [e.offsetX, e.offsetY];
});
canvas.addEventListener('mouseup', () => drawing = false);
canvas.addEventListener('mouseleave', () => drawing = false);

document.getElementById('clearBtn').onclick = clearCanvas;

// 결과 표시 함수 (Tailwind CSS 클래스 활용)
function showResult(message, type = 'info') {
    const resultDiv = document.getElementById('result');
    let bgClass, textClass, borderClass;
    
    switch(type) {
        case 'loading':
            bgClass = 'bg-blue-50';
            textClass = 'text-blue-600';
            borderClass = 'border-blue-300';
            break;
        case 'success':
            bgClass = 'bg-green-50';
            textClass = 'text-green-700';
            borderClass = 'border-green-300';
            break;
        case 'error':
            bgClass = 'bg-red-50';
            textClass = 'text-red-600';
            borderClass = 'border-red-300';
            break;
        default:
            bgClass = 'bg-gray-50';
            textClass = 'text-gray-500';
            borderClass = 'border-gray-300';
    }
    
    resultDiv.className = `text-center p-4 ${bgClass} rounded-xl border-2 border-dashed ${borderClass} min-h-[60px] flex items-center justify-center`;
    resultDiv.innerHTML = `<span class="${textClass} text-lg font-medium">${message}</span>`;
}

// 예측 버튼 클릭 시 서버로 이미지 전송
async function predict() {
    // 캔버스 이미지를 base64로 변환
    const dataUrl = canvas.toDataURL('image/png');
    showResult('AI가 분석 중입니다...', 'loading');
    
    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl })
        });
        const data = await res.json();
        
        if (data.result !== undefined) {
            const confidence = data.confidence;
            let confidenceText = '';
            if (confidence >= 0.9) {
                confidenceText = '매우 높음';
            } else if (confidence >= 0.7) {
                confidenceText = '높음';
            } else if (confidence >= 0.5) {
                confidenceText = '보통';
            } else {
                confidenceText = '낮음';
            }
            
            showResult(`🎯 예측 결과: <span class="text-2xl font-bold text-green-600">${data.result}</span><br><span class="text-sm">신뢰도: ${(confidence * 100).toFixed(1)}% (${confidenceText})</span>`, 'success');
        } else {
            showResult(`❌ ${data.error || '예측 실패'}`, 'error');
        }
    } catch (err) {
        showResult('❌ 서버 연결 오류', 'error');
    }
}

document.getElementById('predictBtn').onclick = predict;

// 페이지 로드 시 캔버스 초기화
clearCanvas(); 