// 웹 챗봇 JavaScript 코드 (Tailwind CSS 버전)

// DOM 요소들
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const charCount = document.getElementById("charCount");
const loadingIndicator = document.getElementById("loadingIndicator");
const welcomeTime = document.getElementById("welcomeTime");

// 전역 변수
let isProcessing = false;

// 페이지 로드 시 초기화
document.addEventListener("DOMContentLoaded", function () {
  // 환영 메시지 시간 설정
  setWelcomeTime();

  // 이벤트 리스너 등록
  setupEventListeners();

  // 입력 필드에 포커스
  messageInput.focus();
});

// 환영 메시지 시간 설정
function setWelcomeTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
  welcomeTime.textContent = timeString;
}

// 이벤트 리스너 설정
function setupEventListeners() {
  // 전송 버튼 클릭 이벤트
  sendButton.addEventListener("click", sendMessage);

  // Enter 키 이벤트
  messageInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });

  // 입력 필드 변경 이벤트 (글자 수 카운트)
  messageInput.addEventListener("input", updateCharCount);

  // 입력 필드 포커스 이벤트
  messageInput.addEventListener("focus", function () {
    this.classList.add("border-blue-500");
    this.classList.remove("border-gray-200");
  });

  // 입력 필드 블러 이벤트
  messageInput.addEventListener("blur", function () {
    this.classList.remove("border-blue-500");
    this.classList.add("border-gray-200");
  });
}

// 메시지 전송 함수
async function sendMessage() {
  const message = messageInput.value.trim();

  // 빈 메시지 체크
  if (!message || isProcessing) {
    return;
  }

  // 처리 중 상태 설정
  isProcessing = true;
  setProcessingState(true);

  try {
    // 사용자 메시지 표시
    addUserMessage(message);

    // 입력 필드 초기화
    messageInput.value = "";
    updateCharCount();

    // 로딩 인디케이터 표시
    showLoadingIndicator();

    // 서버에 메시지 전송
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // 봇 응답 표시
    addBotMessage(data.response, data.timestamp);
  } catch (error) {
    console.error("메시지 전송 오류:", error);
    addBotMessage(
      "죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.",
      getCurrentTime()
    );
  } finally {
    // 처리 완료 상태 복원
    isProcessing = false;
    setProcessingState(false);
    hideLoadingIndicator();

    // 입력 필드에 포커스
    messageInput.focus();
  }
}

// 사용자 메시지 추가
function addUserMessage(message) {
  const messageElement = createUserMessageElement(message, getCurrentTime());
  chatMessages.appendChild(messageElement);
  scrollToBottom();
}

// 봇 메시지 추가
function addBotMessage(message, timestamp) {
  const messageElement = createBotMessageElement(message, timestamp);
  chatMessages.appendChild(messageElement);
  scrollToBottom();
}

// 사용자 메시지 요소 생성
function createUserMessageElement(message, timestamp) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "flex justify-end mb-6 animate-slide-up";

  const contentDiv = document.createElement("div");
  contentDiv.className =
    "max-w-xs lg:max-w-md message-gradient text-white rounded-2xl rounded-br-md shadow-lg p-4";

  const textDiv = document.createElement("div");
  textDiv.className = "text-sm leading-relaxed";
  textDiv.textContent = message;

  const timeDiv = document.createElement("div");
  timeDiv.className = "text-xs opacity-70 mt-2 text-right";
  timeDiv.textContent = timestamp;

  contentDiv.appendChild(textDiv);
  contentDiv.appendChild(timeDiv);
  messageDiv.appendChild(contentDiv);

  return messageDiv;
}

// 봇 메시지 요소 생성
function createBotMessageElement(message, timestamp) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "flex justify-start mb-6 animate-slide-up";

  const contentDiv = document.createElement("div");
  contentDiv.className =
    "max-w-xs lg:max-w-md bg-white rounded-2xl rounded-bl-md shadow-lg border border-gray-200 p-4";

  const textDiv = document.createElement("div");
  textDiv.className = "text-gray-800 text-sm leading-relaxed";
  textDiv.textContent = message;

  const timeDiv = document.createElement("div");
  timeDiv.className = "text-xs text-gray-500 mt-2 text-right";
  timeDiv.textContent = timestamp;

  contentDiv.appendChild(textDiv);
  contentDiv.appendChild(timeDiv);
  messageDiv.appendChild(contentDiv);

  return messageDiv;
}

// 현재 시간 가져오기
function getCurrentTime() {
  const now = new Date();
  return now.toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// 글자 수 업데이트
function updateCharCount() {
  const length = messageInput.value.length;
  charCount.textContent = `${length}/500`;

  // 글자 수에 따른 색상 변경
  if (length > 450) {
    charCount.className = "text-red-500 font-medium";
  } else if (length > 400) {
    charCount.className = "text-orange-500 font-medium";
  } else {
    charCount.className = "text-gray-500";
  }
}

// 처리 중 상태 설정
function setProcessingState(processing) {
  sendButton.disabled = processing;
  messageInput.disabled = processing;

  if (processing) {
    sendButton.classList.add("opacity-50", "cursor-not-allowed");
    messageInput.classList.add("opacity-50");
    sendButton.classList.remove("hover:scale-105", "active:scale-95");
  } else {
    sendButton.classList.remove("opacity-50", "cursor-not-allowed");
    messageInput.classList.remove("opacity-50");
    sendButton.classList.add("hover:scale-105", "active:scale-95");
  }
}

// 로딩 인디케이터 표시
function showLoadingIndicator() {
  loadingIndicator.classList.remove("hidden");
  loadingIndicator.classList.add("flex");
}

// 로딩 인디케이터 숨기기
function hideLoadingIndicator() {
  loadingIndicator.classList.add("hidden");
  loadingIndicator.classList.remove("flex");
}

// 채팅 영역을 맨 아래로 스크롤
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 키보드 단축키 지원
document.addEventListener("keydown", function (event) {
  // Ctrl + Enter로 전송
  if (event.ctrlKey && event.key === "Enter") {
    event.preventDefault();
    sendMessage();
  }

  // Escape로 입력 필드 초기화
  if (event.key === "Escape") {
    messageInput.value = "";
    updateCharCount();
    messageInput.focus();
  }
});

// 네트워크 상태 모니터링
window.addEventListener("online", function () {
  console.log("네트워크 연결이 복구되었습니다.");
  // 상태 표시 업데이트 가능
});

window.addEventListener("offline", function () {
  console.log("네트워크 연결이 끊어졌습니다.");
  addBotMessage("네트워크 연결을 확인해주세요.", getCurrentTime());
});

// 페이지 언로드 시 경고
window.addEventListener("beforeunload", function (event) {
  if (isProcessing) {
    event.preventDefault();
    event.returnValue = "메시지가 전송 중입니다. 정말 나가시겠습니까?";
  }
});

// 에러 처리
window.addEventListener("error", function (event) {
  console.error("JavaScript 오류:", event.error);
  addBotMessage(
    "오류가 발생했습니다. 페이지를 새로고침해주세요.",
    getCurrentTime()
  );
});

// 성능 모니터링 (선택사항)
if ("performance" in window) {
  window.addEventListener("load", function () {
    const loadTime =
      performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log(`페이지 로드 시간: ${loadTime}ms`);
  });
}

// 다크 모드 감지 및 적용
function applyDarkMode() {
  if (
    window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
  ) {
    document.body.classList.add("dark");
  }
}

// 다크 모드 변경 감지
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", applyDarkMode);

// 초기 다크 모드 적용
applyDarkMode();
