(() => {
  const languageSelect = document.querySelector("#voice-language");
  const status = document.querySelector("[data-voice-status]");
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const speech = window.speechSynthesis;

  if (!languageSelect) return;

  const addBrowserVoices = () => {
    if (!speech) return;
    const existing = new Set(Array.from(languageSelect.options, option => option.value.toLowerCase()));
    for (const voice of speech.getVoices()) {
      const locale = voice.lang.trim();
      if (!locale || existing.has(locale.toLowerCase())) continue;
      languageSelect.add(new Option(`${voice.name} (${locale})`, locale));
      existing.add(locale.toLowerCase());
    }
  };

  addBrowserVoices();
  speech?.addEventListener("voiceschanged", addBrowserVoices);

  const feedbackLanguage = document.querySelector('input[name="language"]');
  languageSelect.addEventListener("change", () => {
    if (feedbackLanguage) feedbackLanguage.value = languageSelect.value;
  });

  const dictationButtons = document.querySelectorAll("[data-dictate]");
  if (!Recognition) {
    for (const button of dictationButtons) button.disabled = true;
    if (status) status.textContent = "Voice input is not available in this browser. You can type instead.";
  }

  let activeRecognition = null;
  for (const button of dictationButtons) {
    button.addEventListener("click", () => {
      if (activeRecognition) {
        activeRecognition.stop();
        return;
      }

      const target = document.getElementById(button.dataset.dictate);
      if (!target) return;
      const recognition = new Recognition();
      recognition.lang = languageSelect.value || navigator.language || "en-US";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      activeRecognition = recognition;
      button.setAttribute("aria-pressed", "true");
      if (status) status.textContent = "Listening. Select the speak button again to stop.";

      recognition.onresult = event => {
        const transcript = event.results[0][0].transcript.trim();
        target.value = target.id === "feedback" && target.value
          ? `${target.value.trim()} ${transcript}`
          : transcript;
        target.dispatchEvent(new Event("input", { bubbles: true }));
      };
      recognition.onerror = event => {
        if (status) status.textContent = event.error === "not-allowed"
          ? "Microphone access was denied. Allow microphone access or type instead."
          : `Voice input unavailable: ${event.error}. You can type instead.`;
      };
      recognition.onend = () => {
        activeRecognition = null;
        button.setAttribute("aria-pressed", "false");
        if (status && !status.textContent.startsWith("Voice input unavailable") && !status.textContent.startsWith("Microphone access")) {
          status.textContent = "Voice input finished.";
        }
      };

      try {
        recognition.start();
      } catch (error) {
        activeRecognition = null;
        button.setAttribute("aria-pressed", "false");
        if (status) status.textContent = "Could not start voice input. Check microphone permissions or type instead.";
      }
    });
  }

  for (const button of document.querySelectorAll("[data-read-aloud]")) {
    button.addEventListener("click", () => {
      if (!speech) {
        if (status) status.textContent = "Read-aloud is not available in this browser.";
        return;
      }
      const target = document.getElementById(button.dataset.readAloud);
      if (!target) return;
      speech.cancel();
      const utterance = new SpeechSynthesisUtterance(target.innerText);
      utterance.lang = languageSelect.value || navigator.language || "en-US";
      const voices = speech.getVoices();
      utterance.voice = voices.find(voice => voice.lang.toLowerCase() === utterance.lang.toLowerCase())
        || voices.find(voice => voice.lang.split("-")[0] === utterance.lang.split("-")[0])
        || null;
      utterance.onstart = () => { if (status) status.textContent = "Reading aloud."; };
      utterance.onend = () => { if (status) status.textContent = "Finished reading."; };
      utterance.onerror = () => { if (status) status.textContent = "Read-aloud could not start. Check available voices on your device."; };
      speech.speak(utterance);
    });
  }

  for (const button of document.querySelectorAll("[data-stop-reading]")) {
    button.addEventListener("click", () => {
      speech?.cancel();
      if (status) status.textContent = "Reading stopped.";
    });
  }
})();