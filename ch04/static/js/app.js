// 간단한 유틸: 엘리먼트 선택
const $ = (sel) => document.querySelector(sel);

// 요소 참조
const form = $('#analyzeForm');
const fileInput = $('#image');
const urlInput = $('#image_url');
const previewContainer = $('#preview');
const previewImg = $('#previewImg');
const resultContainer = $('#result');
const analyzeBtn = $('#analyzeBtn');

// 다른 입력이 채워지면 한 쪽을 비워 일관성 유지
fileInput.addEventListener('change', () => {
  if (fileInput.files && fileInput.files[0]) {
    urlInput.value = '';
    showPreviewFromFile(fileInput.files[0]);
  }
});
urlInput.addEventListener('input', () => {
  if (urlInput.value.trim().length > 0) {
    fileInput.value = '';
    showPreviewFromUrl(urlInput.value.trim());
  }
});

// 파일로부터 미리보기 표시
function showPreviewFromFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewImg.classList.remove('hidden');
    hidePreviewPlaceholder();
  };
  reader.readAsDataURL(file);
}

// URL로부터 미리보기 표시
function showPreviewFromUrl(url) {
  previewImg.src = url;
  previewImg.classList.remove('hidden');
  hidePreviewPlaceholder();
}

function hidePreviewPlaceholder() {
  const placeholder = previewContainer.querySelector('span');
  if (placeholder) {
    placeholder.style.display = 'none';
  }
}

function setLoading(loading) {
  analyzeBtn.disabled = loading;
  analyzeBtn.textContent = loading ? '분석 중...' : '분석하기';
}

function renderError(message) {
  resultContainer.innerHTML = `
    <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span class="text-red-700 font-medium">오류</span>
      </div>
      <p class="text-red-600 mt-2">${escapeHtml(message)}</p>
    </div>
  `;
}

function renderResult(payload) {
  const { description, results } = payload;
  const rows = results.map((r, index) => {
    const pct = (r.probability * 100).toFixed(2) + '%';
    const confidenceColor = r.probability > 0.5 ? 'bg-green-100 text-green-800' : 
                           r.probability > 0.2 ? 'bg-yellow-100 text-yellow-800' : 
                           'bg-gray-100 text-gray-800';
    return `
      <tr class="border-b border-gray-200 hover:bg-gray-50">
        <td class="py-3 px-4 font-medium text-gray-900">${escapeHtml(r.label)}</td>
        <td class="py-3 px-4 text-gray-600">${pct}</td>
        <td class="py-3 px-4">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${confidenceColor}">
            ${escapeHtml(r.confidence)}
          </span>
        </td>
      </tr>
    `;
  }).join('');
  
  resultContainer.innerHTML = `
    <div class="space-y-4">
      <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div class="flex items-center mb-2">
          <svg class="w-5 h-5 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-blue-700 font-medium">분석 결과</span>
        </div>
        <p class="text-blue-800 whitespace-pre-wrap leading-relaxed">${escapeHtml(description)}</p>
      </div>
      
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
          <h3 class="text-sm font-semibold text-gray-700">상세 결과</h3>
        </div>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">라벨</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">확률</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">확신도</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            ${rows}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  setLoading(true);
  try {
    const formData = new FormData();
    if (fileInput.files && fileInput.files[0]) {
      formData.append('image', fileInput.files[0]);
    } else if (urlInput.value.trim().length > 0) {
      formData.append('image_url', urlInput.value.trim());
    } else {
      renderError('이미지 파일 또는 URL을 입력해주세요.');
      return;
    }

    const res = await fetch('/analyze', {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    if (!data.success) {
      renderError(data.error || '분석에 실패했습니다.');
      return;
    }

    renderResult(data);
  } catch (err) {
    renderError('요청 중 오류가 발생했습니다. 네트워크를 확인해주세요.');
  } finally {
    setLoading(false);
  }
});
