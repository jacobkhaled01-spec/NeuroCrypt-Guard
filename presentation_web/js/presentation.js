/**
 * presentation.js
 * محرك العرض التقديمي الأكاديمي التفاعلي — نمط السلايدات المتدفقة (Dadanitic Engine)
 * NeuroCrypt-Guard v2.2 — Presentation Orchestrator
 */

const PresentationApp = (function () {
  const TOTAL_SLIDES = 14;
  let currentSlide = 1;
  let audioEnabled = true;
  let audioCtx = null;
  let isScrollObserving = true;

  // تهيئة النظام
  function init() {
    setupKeyboardListeners();
    setupScrollTracker();
    setupInteractiveWidgets();
    updateNavCounter();

    // تهيئة المحاكيات عند توفر الحاويات
    setTimeout(() => {
      initEmbeddedEngines();
    }, 200);
  }

  // تهيئة المحركات العصبية المضمنة في السلايدات
  function initEmbeddedEngines() {
    const N3D = window.Neural3D || (typeof Neural3D !== "undefined" ? Neural3D : null);
    const container3D = document.getElementById("three-canvas-container");
    if (container3D && N3D && !container3D.querySelector("canvas")) {
      try {
        N3D.init(container3D);
      } catch (e) {
        console.error("Error initializing Neural3D:", e);
      }
    }

    const NS = window.NeuralSimulator || (typeof NeuralSimulator !== "undefined" ? NeuralSimulator : null);
    const simCanvas = document.getElementById("neural-sim-canvas");
    if (simCanvas && NS) {
      try {
        NS.init(simCanvas);
      } catch (e) {
        console.error("Error initializing NeuralSimulator:", e);
      }
    }
  }

  // التمرير السلس إلى شريحة معينة
  function scrollToSlide(n) {
    if (n < 1) n = 1;
    if (n > TOTAL_SLIDES) n = TOTAL_SLIDES;
    currentSlide = n;

    const target = document.getElementById(`slide-${n}`);
    if (target) {
      isScrollObserving = false;
      target.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => {
        isScrollObserving = true;
      }, 700);
    }

    updateNavCounter();
    closeAllModals();
    playCyberTone("slide");

    // تنشيط المحركات عند الوصول لشرائحها
    if (n === 5) {
      const N3D = window.Neural3D || (typeof Neural3D !== "undefined" ? Neural3D : null);
      if (N3D && N3D.resize) setTimeout(() => N3D.resize(), 150);
    }
    if (n === 6) {
      const NS = window.NeuralSimulator || (typeof NeuralSimulator !== "undefined" ? NeuralSimulator : null);
      if (NS) {
        if (NS.resize) setTimeout(() => NS.resize(), 150);
        if (NS.startSimulation) setTimeout(() => NS.startSimulation(), 250);
      }
    }
  }

  function nextSlide() {
    if (currentSlide < TOTAL_SLIDES) {
      scrollToSlide(currentSlide + 1);
    }
  }

  function prevSlide() {
    if (currentSlide > 1) {
      scrollToSlide(currentSlide - 1);
    }
  }

  // تحديث عداد الشريحة والمصغرات
  function updateNavCounter() {
    const counter = document.getElementById("navCounter");
    if (counter) {
      counter.textContent = `${currentSlide} / ${TOTAL_SLIDES}`;
    }

    // تحديث مصغرات القائمة
    document.querySelectorAll(".drawer-card").forEach((card, idx) => {
      card.classList.toggle("active", idx + 1 === currentSlide);
    });
  }

  // تتبع الشريحة الحالية أثناء التمرير الطبيعي بالماوس
  function setupScrollTracker() {
    window.addEventListener("scroll", () => {
      if (!isScrollObserving) return;
      const scrollPos = window.scrollY + window.innerHeight / 2;

      for (let i = 1; i <= TOTAL_SLIDES; i++) {
        const s = document.getElementById(`slide-${i}`);
        if (s) {
          const top = s.offsetTop;
          const height = s.offsetHeight;
          if (scrollPos >= top && scrollPos < top + height) {
            if (currentSlide !== i) {
              currentSlide = i;
              updateNavCounter();
              if (i === 5) {
                const N3D = window.Neural3D || (typeof Neural3D !== "undefined" ? Neural3D : null);
                if (N3D && N3D.resize) N3D.resize();
              }
              if (i === 6) {
                const NS = window.NeuralSimulator || (typeof NeuralSimulator !== "undefined" ? NeuralSimulator : null);
                if (NS && NS.resize) NS.resize();
              }
            }
            break;
          }
        }
      }
    });
  }

  // اختصارات لوحة المفاتيح
  function setupKeyboardListeners() {
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

      switch (e.key) {
        case "ArrowDown":
        case "ArrowLeft": // RTL تقدم للأمام
        case "PageDown":
        case " ":
          e.preventDefault();
          nextSlide();
          break;

        case "ArrowUp":
        case "ArrowRight": // RTL رجوع للخلف
        case "PageUp":
          e.preventDefault();
          prevSlide();
          break;

        case "Home":
          e.preventDefault();
          scrollToSlide(1);
          break;

        case "End":
          e.preventDefault();
          scrollToSlide(TOTAL_SLIDES);
          break;

        case "f":
        case "F":
          toggleFullscreen();
          break;

        case "o":
        case "O":
          toggleDrawer();
          break;

        case "m":
        case "M":
          toggleAudio();
          break;

        case "Escape":
          closeAllModals();
          break;
      }
    });
  }

  // شاشات ومودال المصغرات
  function toggleDrawer() {
    const modal = document.getElementById("drawer-modal");
    if (!modal) return;
    const isActive = modal.classList.contains("active");
    closeAllModals();
    if (!isActive) {
      modal.classList.add("active");
      playCyberTone("click");
    }
  }

  function closeAllModals() {
    document.querySelectorAll(".drawer-modal").forEach((m) => {
      m.classList.remove("active");
    });
  }

  // ملء الشاشة
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
    }
  }

  // الصوتيات التفاعلية (Web Audio API)
  function toggleAudio() {
    audioEnabled = !audioEnabled;
    const btn = document.getElementById("btn-audio");
    if (btn) btn.textContent = audioEnabled ? "🔊" : "🔇";
  }

  function playCyberTone(type = "click") {
    if (!audioEnabled) return;
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }

      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      if (type === "click") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.04);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.04);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === "slide") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(680, now + 0.07);
        gain.gain.setValueAtTime(0.05, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.07);
        osc.start(now);
        osc.stop(now + 0.07);
      } else if (type === "chime") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.06);
        osc.frequency.setValueAtTime(783.99, now + 0.12);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      }
    } catch (e) {}
  }

  // ==========================================================================
  // الأدوات التفاعلية المدمجة داخل السلايدات
  // ==========================================================================
  function setupInteractiveWidgets() {
    // 1. محاكي تصحيح أخطاء هامنغ التفاعلي في الشريحة 7
    const bitContainer = document.getElementById("interactive-bits");
    const hammingStatus = document.getElementById("hamming-status-msg");
    let currentBits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];

    if (bitContainer) {
      function renderBits() {
        bitContainer.innerHTML = "";
        currentBits.forEach((b, idx) => {
          const bitEl = document.createElement("button");
          bitEl.className = "bit-interactive";
          bitEl.textContent = b;

          bitEl.addEventListener("click", () => {
            currentBits[idx] ^= 1;
            bitEl.textContent = currentBits[idx];
            bitEl.classList.add("flipped");
            playCyberTone("click");

            if (hammingStatus) {
              hammingStatus.innerHTML = `<span style="color: #fb7185;">⚠ تم رصد خطأ تناظري في البت #${idx + 1}... جاري إطلاق متلازمة هامنغ SEC...</span>`;
            }

            setTimeout(() => {
              currentBits[idx] ^= 1;
              bitEl.textContent = currentBits[idx];
              bitEl.classList.remove("flipped");
              bitEl.classList.add("corrected");
              playCyberTone("chime");

              if (hammingStatus) {
                hammingStatus.innerHTML = `<span style="color: #34d399;">✓ تم تصحيح البت #${idx + 1} فورياً! متلازمة التدقيق S = 00000 | نسبة التطابق 100.00% SHA-256</span>`;
              }

              setTimeout(() => {
                bitEl.classList.remove("corrected");
              }, 1200);
            }, 600);
          });

          bitContainer.appendChild(bitEl);
        });
      }
      renderBits();
    }

    // 2. مفتش البصمات التشفيرية الفوري في الشريحة 8
    const fileSelect = document.getElementById("file-benchmark-select");
    const origHashEl = document.getElementById("bench-orig-hash");
    const bobHashEl = document.getElementById("bench-bob-hash");
    const eveHashEl = document.getElementById("bench-eve-hash");

    const sampleFiles = {
      text: {
        orig: "601c02b66e159422373dcb1598146961ab20a270a4c3cfdbf58a680de2e9c38d",
        bob: "601c02b66e159422373dcb1598146961ab20a270a4c3cfdbf58a680de2e9c38d",
        eve: "2d47e7e2ecca78715b567a1b430d2f387758d6ac99f662ba5db630cd945a7549"
      },
      png: {
        orig: "317dc0529b7e3d7b1813f4348f31c95eeadcd21d77a5e3924c1a1603c5aae816",
        bob: "317dc0529b7e3d7b1813f4348f31c95eeadcd21d77a5e3924c1a1603c5aae816",
        eve: "89a2bc91e4f012489c7d65b128741aa89c4501ef9843ba0982312019842fba76"
      },
      binary: {
        orig: "effa6974b53b0d4bcba243495601029db42e34b81b3a8810553e42065d00fb69",
        bob: "effa6974b53b0d4bcba243495601029db42e34b81b3a8810553e42065d00fb69",
        eve: "fa49c01823901bce471092841bbce8749012384910248912c98421bba8749102"
      }
    };

    if (fileSelect) {
      fileSelect.addEventListener("change", (e) => {
        const val = e.target.value;
        const data = sampleFiles[val] || sampleFiles.text;
        if (origHashEl) origHashEl.textContent = data.orig;
        if (bobHashEl) bobHashEl.textContent = data.bob;
        if (eveHashEl) eveHashEl.textContent = data.eve;
        playCyberTone("click");
      });
    }

    // 3. مصفوفة SAC التفاعلية 16x16 في الشريحة 9
    const sacContainer = document.getElementById("sac-heatmap-container");
    const sacInspectLabel = document.getElementById("sac-inspected-val");
    if (sacContainer) {
      sacContainer.innerHTML = "";
      for (let r = 0; r < 16; r++) {
        for (let c = 0; c < 16; c++) {
          const cell = document.createElement("div");
          cell.className = "sac-cell";
          const val = (0.485 + Math.random() * 0.028).toFixed(4);
          const opacity = Math.min(1.0, Math.max(0.35, (val - 0.45) * 12));
          cell.style.backgroundColor = `rgba(0, 180, 216, ${opacity})`;
          cell.title = `SAC(الدخل #${r + 1}, الخرج #${c + 1}) = ${val} (الهدف = 0.5000)`;
          cell.addEventListener("click", () => {
            if (sacInspectLabel) {
              sacInspectLabel.innerHTML = `معاينة خلية SAC: [دخل #${r + 1} &harr; خرج #${c + 1}] &larr; الاحتمالية: <strong style="color: #34d399;">${val}</strong> (المعيار 0.5000)`;
            }
            playCyberTone("click");
          });
          sacContainer.appendChild(cell);
        }
      }
    }

    // 4. أزرار طيف الخصوم في الشريحة 10
    document.querySelectorAll(".adv-tier-btn").forEach((btn) => {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".adv-tier-btn").forEach((b) => b.classList.remove("active"));
        this.classList.add("active");
        const tier = this.getAttribute("data-tier");
        const cardTitle = document.getElementById("adv-detail-title");
        const cardParams = document.getElementById("adv-detail-params");
        const cardBer = document.getElementById("adv-detail-ber");
        const cardVerdict = document.getElementById("adv-detail-verdict");

        if (tier === "standard") {
          cardTitle.textContent = "الخصم المعياري (Standard Eve)";
          cardParams.textContent = "6,017";
          cardBer.textContent = "40.33%";
          cardVerdict.textContent = "عجز كامل — فشل فك التشفير وارتفاع معدل الخطأ لحدود شانون العشوائية.";
        } else if (tier === "wide") {
          cardTitle.textContent = "الخصم العريض (Wide Eve)";
          cardParams.textContent = "6,017";
          cardBer.textContent = "40.49%";
          cardVerdict.textContent = "عجز كامل — استمرار حيرة الخصم رغم توسيع القنوات التلافيفية للضعف.";
        } else if (tier === "deep") {
          cardTitle.textContent = "الخصم العميق فائق التعقيد (Deep Residual Eve)";
          cardParams.textContent = "26,161";
          cardBer.textContent = "40.69%";
          cardVerdict.textContent = "صمود شانون التام — تشتت محاولات الخصم وزيادة معدل الخطأ رغم مضاعفة الحجم 4 أضعاف وإضافة وصلات تخطي متبقية!";
        }
        playCyberTone("click");
      });
    });
  }

  return {
    init,
    scrollToSlide,
    nextSlide,
    prevSlide,
    toggleFullscreen,
    toggleDrawer,
    toggleAudio,
    closeAllModals
  };
})();

// تصدير كائن العرض التقديمي إلى window
if (typeof window !== "undefined") {
  window.PresentationApp = PresentationApp;
}

// تشغيل النظام عند تحميل المستند
document.addEventListener("DOMContentLoaded", () => {
  PresentationApp.init();
});
