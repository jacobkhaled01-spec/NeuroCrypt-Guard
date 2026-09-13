/**
 * neural_simulator.js
 * محرك المحاكاة العصبية التفاعلي الحي المفصل — النسخة الأكاديمية المتقدمة
 * Advanced Interactive Synaptic Cryptography Simulator & Neural Physics Engine
 * NeuroCrypt-Guard v2.3 — Academic Defense Edition (Ibb University, 2026)
 *
 * المراجع العلمية وفق نمط APA 7th Edition:
 * - Abadi, M., & Andersen, D. G. (2016). Learning to protect communications with adversarial neural cryptography. arXiv:1610.06918.
 * - Shannon, C. E. (1949). Communication theory of secrecy systems. Bell System Technical Journal, 28(4), 656-715.
 * - Webster, A. F., & Tavares, S. E. (1985). On the design of S-boxes. CRYPTO '85, 523-534.
 */

const NeuralSimulator = (function () {
  let canvas, ctx;
  let animId = null;
  let isRunning = true;
  let speed = 1.0;
  let stepStage = 1;
  let stageTimer = 0;
  let animClock = 0;

  // حالة البيانات المشفرة والمفتاح
  let currentText = "جامعة إب 2026 — سرية تامة";
  let currentKey = "1100101011110000";
  let plainBits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
  let keyBits = [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0];
  let bobBits = [];
  let eveBits = [];
  let bobErrorIdx = 5; // موضع الخطأ التناظري المتعمد (البت السادس)
  let isCorrected = false;

  // عناصر الشبكة التفاعلية والفيزيائية
  let aliceNodes = [];
  let bobNodes = [];
  let eveNodes = [];
  let synapses = [];
  let signalParticles = [];
  let idlePulses = [];
  let sparkParticles = [];
  let rippleWaves = [];
  let laserBeam = null;
  let convSweepProgress = 0;

  // تفاعل الفأرة والمفتش
  let mouseX = -100, mouseY = -100;
  let hoveredNode = null;

  // قاموس الشروحات الأكاديمية المباشرة المتزامنة
  const STAGE_EXPLANATIONS = {
    1: {
      badge: "المرحلة 1/6: إدخال الرسالة والمفتاح المشترك 📥",
      color: "#00b4d8",
      text: "أليس تدمج الـ 16 بت للرسالة مع 16 بت للمفتاح السري المشترك في متجه أولي موحد 32-dim لتحضيره للخلط والتشفير العصبي."
    },
    2: {
      badge: "المرحلة 2/6: الخلط والانتشار التلافيفي (AliceNet) 🌀",
      color: "#3b82f6",
      text: "طبقة الخلط الخطي (32x32) تحقق خاصية الارتباك (Confusion)، تليها طبقات التلافيف (Conv1D k=4) لنشر أثر كل بت على الكتل المجاورة (Diffusion) وتوليد شفرة Float16 مع 5 بت لمتلازمة هامنغ."
    },
    3: {
      badge: "المرحلة 3/6: البث عبر القناة العامة واعتراض إيف 📡",
      color: "#9d4edd",
      text: "انطلاق النص المشفر كإشارات تناظرية عبر القناة العامة المشوشة. المتنصت إيف يعترض الإشارة التناظرية الكاملة ولكن بدون امتلاك المفتاح السري المشترك."
    },
    4: {
      badge: "المرحلة 4/6: فك التشفير الشرعي لبوب (BobNet) 🔓",
      color: "#10b981",
      text: "بوب يستقبل النص المشفر ويدمجه مع المفتاح السري، وتعمل طبقات التلافيف العكسية على إعادة بناء الرسالة بدقة تناظرية 99.93%، مع رصد عدم تطابق في بت واحد (خطأ تناظري طبيعي في البت #6)."
    },
    5: {
      badge: "المرحلة 5/6: متلازمة هامنغ SEC وإطلاق ليزر التصحيح ⚡",
      color: "#00d9a5",
      text: "حساب متلازمة التكافؤ S = (H · P^T) ⊕ Parity وإطلاق شعاع ليزر تصحيح هامنغ الفوري؛ ليتم إصلاح البت التالف وتتحول شارة المطابقة إلى 100.00% SHA-256 ✓ دون نقل النص الأصلي!"
    },
    6: {
      badge: "المرحلة 6/6: عجز المتنصت إيف وصمود سرية شانون 🚨",
      color: "#f43f5e",
      text: "انهيار محاولات الخصم العميق (26,161 بارامتر) لفك التشفير، واستقرار معدل خطئه عند 45.40%؛ مما يثبت أن متلازمة هامنغ لم تسرب أي معلومة للخصم واحتفاظ الشفرة بحاجز شانون للسرية التامة."
    }
  };

  // الألوان السيبرانية المضيئة
  const COLORS = {
    bg: "#04060d",
    cyan: "#00b4d8",
    cyanGlow: "rgba(0, 180, 216, 0.4)",
    blue: "#3b82f6",
    amber: "#ffd93d",
    green: "#00d9a5",
    greenGlow: "rgba(0, 217, 165, 0.5)",
    red: "#f43f5e",
    redGlow: "rgba(244, 63, 94, 0.5)",
    purple: "#9d4edd",
    aliceWire: "rgba(0, 180, 216, 0.28)",
    bobWire: "rgba(0, 217, 165, 0.28)",
    eveWire: "rgba(244, 63, 94, 0.28)",
    activeWire: "rgba(0, 217, 165, 0.95)"
  };

  let isInitialized = false;

  function init(canvasElement) {
    canvas = canvasElement;
    if (!canvas) return;
    ctx = canvas.getContext("2d");

    if (!isInitialized) {
      isInitialized = true;
      window.addEventListener("resize", resize);
      setupUIEventListeners();
      setupMouseEvents();
      setupVisibilityObserver();
    }

    resize();
    resetSimulationState();
    executeStageLogic(1);

    if (!animId) {
      animate();
    }
  }

  // مراقبة ظهور السلايد لضمان تناسق الأبعاد
  function setupVisibilityObserver() {
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            resize();
          }
        });
      }, { threshold: 0.1 });

      const slide6 = document.getElementById("slide-6");
      if (slide6) observer.observe(slide6);
      if (canvas) observer.observe(canvas);
    }
  }

  function resize() {
    if (!canvas) return;
    const parent = canvas.parentElement;
    const parentW = (parent && parent.clientWidth > 200) ? parent.clientWidth : (window.innerWidth > 500 ? window.innerWidth - 180 : 1100);
    const parentH = (parent && parent.clientHeight > 200) ? parent.clientHeight : 440;

    canvas.width = Math.floor(parentW);
    canvas.height = Math.floor(parentH);

    buildNeuralTopology();
  }

  // تحويل النص إلى 16 بت
  function textTo16Bits(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    const bits = [];
    for (let i = 0; i < 16; i++) {
      bits.push((Math.abs(hash) >> i) & 1);
    }
    return bits;
  }

  // بناء طوبولوجيا الشبكة العصبية مع الميتاداتا الأكاديمية الكاملة لكل خلية
  function buildNeuralTopology() {
    aliceNodes = [];
    bobNodes = [];
    eveNodes = [];
    synapses = [];
    idlePulses = [];

    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    // 1. محطة أليس (AliceNet)
    const aliceCenterX = w * 0.22;
    const layerXs = [
      aliceCenterX - 115, // المدخلات (Msg 16 + Key 16)
      aliceCenterX - 45,  // الخلط الخطي (FC Mixer)
      aliceCenterX + 25,  // التلافيف (Conv1D)
      aliceCenterX + 95   // الخرج التشفيري (Float16 + Parity)
    ];

    const aliceLayers = [
      {
        count: 16, x: layerXs[0], type: "alice_msg", label: "Msg", color: COLORS.cyan,
        layerName: "طبقة إدخال الرسالة (Message In)", mathFunc: "Direct Injection",
        securityRole: "تغذية النص الصريح (16 بت) للدمج الأولي"
      },
      {
        count: 16, x: layerXs[0] + 16, type: "alice_key", label: "Key", color: COLORS.amber,
        layerName: "طبقة إدخال المفتاح (Shared Key)", mathFunc: "Direct Injection",
        securityRole: "تغذية المفتاح السري المشترك (16 بت)"
      },
      {
        count: 12, x: layerXs[1], type: "alice_fc", label: "Mixer", color: COLORS.blue,
        layerName: "طبقة الخلط الخطي (FC Mixer 32x32)", mathFunc: "Linear + LeakyReLU(0.2)",
        securityRole: "خلط البتات لتحقيق خاصية الارتباك (Confusion)"
      },
      {
        count: 10, x: layerXs[2], type: "alice_conv", label: "Conv", color: COLORS.purple,
        layerName: "الطبقة التلافيفية (Conv1D Filter k=4)", mathFunc: "Conv1D(32c, k=4) + LeakyReLU",
        securityRole: "نشر تأثير كل بت على الكتل المجاورة (Diffusion)"
      },
      {
        count: 8, x: layerXs[3], type: "alice_out", label: "Ciph", color: COLORS.cyan,
        layerName: "طبقة الخرج الكامن (Float16 + Parity)", mathFunc: "Tanh() -> [-1.0, 1.0]",
        securityRole: "توليد الشفرة التناظرية مع متلازمة هامنغ (5-bit SEC)"
      }
    ];

    aliceLayers.forEach((l, lIdx) => {
      const stepY = (h * 0.52) / (l.count + 1);
      const startY = h * 0.18;
      for (let i = 0; i < l.count; i++) {
        aliceNodes.push({
          id: `alice_${l.type}_${i}`,
          index: i,
          stationName: "محطة أليس (AliceNet)",
          layerName: l.layerName,
          mathFunc: l.mathFunc,
          securityRole: l.securityRole,
          x: l.x,
          y: startY + (i + 1) * stepY,
          radius: l.type.includes("msg") || l.type.includes("key") ? 3.8 : 5.0,
          color: l.color,
          layer: lIdx,
          type: l.type,
          val: (Math.sin(i * 1.3 + lIdx) * 0.95).toFixed(2),
          activity: 0
        });
      }
    });

    // 2. محطة بوب الشرعي (BobNet)
    const bobCenterX = w * 0.78;
    const bobLayerXs = [
      bobCenterX - 95, // Cipher In + Key
      bobCenterX - 35, // Inversion Conv
      bobCenterX + 30, // FC Reconstructor
      bobCenterX + 95  // Decoded 16 Bits
    ];

    const bobLayers = [
      {
        count: 8, x: bobLayerXs[0], type: "bob_in", label: "Cin", color: COLORS.purple,
        layerName: "طبقة استقبال الشفرة والمفتاح", mathFunc: "Concat(Cipher, Key)",
        securityRole: "استقبال النص المشفر مع المفتاح الموثوق"
      },
      {
        count: 10, x: bobLayerXs[1], type: "bob_conv", label: "InvC", color: COLORS.green,
        layerName: "التلافيف العكسية (Inversion CNN)", mathFunc: "Conv1D(16c, k=2) + LeakyReLU",
        securityRole: "تفكيك التلافيف واستعادة الحالات الكامنة"
      },
      {
        count: 12, x: bobLayerXs[2], type: "bob_fc", label: "InvFC", color: COLORS.blue,
        layerName: "طبقة فك الخلط (Inverse Mixer)", mathFunc: "Linear(32->32) + LeakyReLU",
        securityRole: "إعادة بناء الرسالة بدقة تناظرية 99.93%"
      },
      {
        count: 16, x: bobLayerXs[3], type: "bob_out", label: "Dec", color: COLORS.green,
        layerName: "مخرجات فك التشفير الحتمية", mathFunc: "Hamming SEC Matrix H(5x16)",
        securityRole: "تصحيح الخطأ التناظري وتحقيق تطابق 100% SHA-256"
      }
    ];

    bobLayers.forEach((l, lIdx) => {
      const stepY = (h * 0.52) / (l.count + 1);
      const startY = h * 0.18;
      for (let i = 0; i < l.count; i++) {
        bobNodes.push({
          id: `bob_${l.type}_${i}`,
          index: i,
          stationName: "محطة بوب الشرعي (BobNet)",
          layerName: l.layerName,
          mathFunc: l.mathFunc,
          securityRole: l.securityRole,
          x: l.x,
          y: startY + (i + 1) * stepY,
          radius: 4.8,
          color: l.color,
          layer: lIdx,
          type: l.type,
          val: (plainBits[i % 16] || 0).toString(),
          activity: 0,
          isErrorBit: (l.type === "bob_out" && i === bobErrorIdx)
        });
      }
    });

    // 3. محطة إيف المتنصت (Deep Residual EveNet)
    const eveCenterX = w * 0.5;
    const eveCenterY = h * 0.77;
    const eveLayerXs = [
      eveCenterX - 70,
      eveCenterX - 25,
      eveCenterX + 25,
      eveCenterX + 70
    ];

    const eveLayerNames = [
      { name: "اعتراض الشفرة (Zero Key)", math: "Wiretap Input (Float16)" },
      { name: "المجموعة التلافيفية الأولى", math: "Conv1D(64c, k=3)" },
      { name: "المجموعة التلافيفية المتبقية", math: "Residual Skip Connection" },
      { name: "تخمين الشفرة الفاشل (ضجيج)", math: "Tanh() -> Noise BER=45.4%" }
    ];

    for (let lIdx = 0; lIdx < 4; lIdx++) {
      const count = 6;
      for (let i = 0; i < count; i++) {
        eveNodes.push({
          id: `eve_${lIdx}_${i}`,
          index: i,
          stationName: "محطة المتنصت (Deep Residual Eve)",
          layerName: eveLayerNames[lIdx].name,
          mathFunc: eveLayerNames[lIdx].math,
          securityRole: "محاولة كسر التشفير بدون مفتاح — عجز كامل عند حد شانون",
          x: eveLayerXs[lIdx],
          y: eveCenterY - 35 + i * 14,
          radius: 4.5,
          color: COLORS.red,
          layer: lIdx,
          type: "eve",
          val: (Math.random() * 2 - 1).toFixed(2),
          activity: 0
        });
      }
    }

    // بناء الوصلات المشبكية
    buildSynapses(aliceNodes, COLORS.aliceWire);
    buildSynapses(bobNodes, COLORS.bobWire);
    buildSynapses(eveNodes, COLORS.eveWire);

    // إنشاء نبضات خاملة
    for (let i = 0; i < 28; i++) {
      if (synapses.length > 0) {
        const syn = synapses[Math.floor(Math.random() * synapses.length)];
        idlePulses.push({
          syn,
          progress: Math.random(),
          speed: 0.007 + Math.random() * 0.009,
          color: syn.wireColor.replace("0.28", "0.9")
        });
      }
    }
  }

  function buildSynapses(nodeList, defaultColor) {
    const layers = {};
    nodeList.forEach((n) => {
      if (!layers[n.layer]) layers[n.layer] = [];
      layers[n.layer].push(n);
    });

    const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
    for (let i = 0; i < layerKeys.length - 1; i++) {
      const curr = layers[layerKeys[i]];
      const next = layers[layerKeys[i + 1]];
      curr.forEach((from) => {
        next.forEach((to) => {
          if (Math.random() > 0.42) {
            synapses.push({
              from,
              to,
              wireColor: defaultColor,
              pulse: 0
            });
          }
        });
      });
    }
  }

  // أحداث الفأرة والتفاعل
  function setupMouseEvents() {
    if (!canvas) return;

    canvas.addEventListener("mousemove", (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      mouseX = (e.clientX - rect.left) * scaleX;
      mouseY = (e.clientY - rect.top) * scaleY;

      const allNodes = [...aliceNodes, ...bobNodes, ...eveNodes];
      hoveredNode = allNodes.find((n) => {
        const dx = n.x - mouseX;
        const dy = n.y - mouseY;
        return Math.sqrt(dx * dx + dy * dy) < n.radius + 8;
      });

      const tooltip = document.getElementById("sim-node-tooltip");
      if (tooltip) {
        if (hoveredNode) {
          const clientX = e.clientX - rect.left;
          const clientY = e.clientY - rect.top;
          tooltip.style.left = `${Math.min(rect.width - 270, Math.max(10, clientX + 15))}px`;
          tooltip.style.top = `${Math.min(rect.height - 130, Math.max(10, clientY - 40))}px`;
          tooltip.style.display = "block";
          tooltip.innerHTML = `
            <div style="font-weight:700; color: ${hoveredNode.color}; margin-bottom:4px; font-size:0.85rem;">
              ${hoveredNode.stationName} • ${hoveredNode.layerName}
            </div>
            <div style="color:var(--text-muted); font-size:0.75rem; margin-bottom:6px;">
              معرّف الخلية: <code style="color:#fff;">${hoveredNode.id}</code> &nbsp;|&nbsp; الفهرس: #${hoveredNode.index + 1}
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
              <span style="color:#94a3b8;">القيمة الآنية (Activation):</span>
              <strong style="color:${parseFloat(hoveredNode.val) >= 0 ? '#34d399' : '#f43f5e'};">${hoveredNode.val}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
              <span style="color:#94a3b8;">الدالة الرياضية:</span>
              <span style="color:#e2e8f0; font-family:'Fira Code',monospace;">${hoveredNode.mathFunc}</span>
            </div>
            <div style="font-size:0.75rem; color:var(--accent); border-top:1px solid rgba(255,255,255,0.1); padding-top:4px; margin-top:4px;">
              🛡️ ${hoveredNode.securityRole}
            </div>
          `;
        } else {
          tooltip.style.display = "none";
        }
      }
    });

    canvas.addEventListener("mouseleave", () => {
      hoveredNode = null;
      const tooltip = document.getElementById("sim-node-tooltip");
      if (tooltip) tooltip.style.display = "none";
    });
  }

  function resetSimulationState() {
    plainBits = textTo16Bits(currentText);
    keyBits = currentKey.split("").map(c => parseInt(c, 10) || 0);
    bobBits = [...plainBits];
    bobBits[bobErrorIdx] ^= 1; // خطأ تناظري متعمد في البت السادس
    isCorrected = false;
    stepStage = 1;
    stageTimer = 0;
    signalParticles = [];
    sparkParticles = [];
    rippleWaves = [];
    laserBeam = null;

    updateHUDDisplays();
  }

  function startSimulation() {
    resetSimulationState();
    isRunning = true;
    const playBtn = document.getElementById("sim-play-trigger");
    if (playBtn) playBtn.innerHTML = "<span>⏸</span> إيقاف المحاكاة مؤقتاً";
    logTerminal("▶ بدء دورة التشفير العصبي الحي (Live Synaptic Cycle)...");
    executeStageLogic(1);
  }

  function pauseSimulation() {
    isRunning = !isRunning;
    const playBtn = document.getElementById("sim-play-trigger");
    if (playBtn) playBtn.innerHTML = isRunning ? "<span>⏸</span> إيقاف المحاكاة مؤقتاً" : "<span>⚡</span> تشغيل المحاكاة الحية";
  }

  function stepForward() {
    stepStage = (stepStage % 6) + 1;
    executeStageLogic(stepStage);
  }

  function jumpToStage(s) {
    stepStage = s;
    stageTimer = 0;
    executeStageLogic(stepStage);
  }

  function setSpeed(sp) {
    speed = sp;
    document.querySelectorAll(".sim-speed-btn").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById(sp < 0.6 ? "speed-btn-05" : (sp > 1.5 ? "speed-btn-2" : "speed-btn-1"));
    if (activeBtn) activeBtn.classList.add("active");
  }

  function setupUIEventListeners() {
    const textInput = document.getElementById("sim-text-input");
    const keyInput = document.getElementById("sim-key-input");
    const playBtn = document.getElementById("sim-play-trigger");
    const stepBtn = document.getElementById("sim-step-trigger");
    const resetBtn = document.getElementById("sim-reset-trigger");

    if (textInput) {
      textInput.addEventListener("input", (e) => {
        currentText = e.target.value || "Crypto";
        resetSimulationState();
        executeStageLogic(1);
      });
    }

    if (keyInput) {
      keyInput.addEventListener("input", (e) => {
        currentKey = e.target.value.padEnd(16, "0").slice(0, 16);
        resetSimulationState();
        executeStageLogic(1);
      });
    }

    if (playBtn) {
      playBtn.addEventListener("click", () => {
        if (!isRunning) {
          startSimulation();
        } else {
          pauseSimulation();
        }
      });
    }

    if (stepBtn) {
      stepBtn.addEventListener("click", () => {
        isRunning = false;
        stepForward();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        resetSimulationState();
        executeStageLogic(1);
        logTerminal("↺ تم إعادة ضبط المحاكاة إلى الحالة الابتدائية.");
      });
    }
  }

  // منطق المراحل الست لدورة التشفير المتزامنة
  function executeStageLogic(stage) {
    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    // 1. تحديث شريط المراحل التفاعلي (Stage Breadcrumb Pills)
    document.querySelectorAll(".stage-step-pill").forEach((pill, idx) => {
      pill.classList.toggle("active", idx + 1 === stage);
    });

    // 2. تحديث شريط الشرح والتوضيح الأكاديمي المباشر
    const bannerText = document.getElementById("sim-banner-text");
    const explanation = STAGE_EXPLANATIONS[stage];
    if (bannerText && explanation) {
      bannerText.innerHTML = `<strong style="color: ${explanation.color};">[${explanation.badge}]</strong> ${explanation.text}`;
    }

    // 3. المنطق الحركي والجسيمات لكل مرحلة
    if (stage === 1) {
      aliceNodes.filter(n => n.layer <= 1).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        aliceNodes.filter(n => n.layer === 0),
        aliceNodes.filter(n => n.layer === 1),
        COLORS.cyan
      );
      logTerminal("📥 إدخال الرسالة والمفتاح: دمج 16 بت نص صريح + 16 بت مفتاح في متجه أولي 32-dim.");
    } else if (stage === 2) {
      aliceNodes.filter(n => n.layer >= 1).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        aliceNodes.filter(n => n.layer === 2),
        aliceNodes.filter(n => n.layer === 3),
        COLORS.blue
      );
      logTerminal("🌀 معالجة AliceNet: توليد الحالات الكامنة Float16 وحساب متلازمة التكافؤ (5-bit Parity).");
    } else if (stage === 3) {
      const outAlice = aliceNodes.filter(n => n.layer === 3);
      outAlice.forEach(n => (n.activity = 1.0));

      // جسيمات مندفعة نحو بوب عبر القناة
      for (let i = 0; i < 14; i++) {
        signalParticles.push({
          x: w * 0.35,
          y: h * 0.32,
          targetX: w * 0.65,
          targetY: h * 0.32,
          progress: 0,
          speed: 0.038 * speed,
          color: COLORS.purple
        });
      }
      // جسيمات متجهة لاعتراض إيف
      for (let i = 0; i < 9; i++) {
        signalParticles.push({
          x: w * 0.5,
          y: h * 0.32,
          targetX: w * 0.5,
          targetY: h * 0.69,
          progress: 0,
          speed: 0.038 * speed,
          color: COLORS.red
        });
      }
      logTerminal("📡 القناة المشوشة: انتقال النص المشفر. اعتراض إيف بدون مفتاح + وصول الشفرة لبوب.");
    } else if (stage === 4) {
      bobNodes.filter(n => n.layer <= 2).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        bobNodes.filter(n => n.layer === 0),
        bobNodes.filter(n => n.layer === 2),
        COLORS.green
      );
      logTerminal("🔓 فك تشفير بوب: دمج الشفرة مع المفتاح المشترك. رصد عدم تطابق في بت واحد (خطأ تناظري).");
    } else if (stage === 5) {
      const targetNode = bobNodes.find(n => n.isErrorBit);
      const startX = w * 0.78 + 30;
      const startY = h * 0.14;
      const targetX = targetNode ? targetNode.x : w * 0.78 + 95;
      const targetY = targetNode ? targetNode.y : h * 0.35;

      laserBeam = {
        fromX: startX,
        fromY: startY,
        toX: targetX,
        toY: targetY,
        life: 1.0
      };

      // إطلاق موجات دائرية متوسعة عند تصحيح البت
      rippleWaves.push({ x: targetX, y: targetY, radius: 4, alpha: 1.0 });

      bobBits[bobErrorIdx] = plainBits[bobErrorIdx];
      isCorrected = true;
      spawnSparks(targetX, targetY, COLORS.green);
      logTerminal("⚡ هامنغ SEC: إطلاق شعاع تصحيح التكافؤ! تم إصلاح البت بنجاح وتحقيق 100.00% تطابق SHA-256 ✓");
    } else if (stage === 6) {
      eveNodes.forEach(n => (n.activity = 1.0));
      spawnSparks(w * 0.5, h * 0.75, COLORS.red);
      logTerminal("🚨 إيف: انهيار محاولة كسر التشفير بدون مفتاح. خطأ عشوائي BER = 45.40% (حاجز شانون).");
    }

    updateHUDDisplays();
  }

  function spawnSignalBatch(fromList, toList, color) {
    fromList.forEach(from => {
      const targets = toList.slice(0, 2);
      targets.forEach(to => {
        signalParticles.push({
          x: from.x,
          y: from.y,
          targetX: to.x,
          targetY: to.y,
          progress: 0,
          speed: 0.045 * speed,
          color
        });
      });
    });
  }

  function spawnSparks(x, y, color) {
    for (let i = 0; i < 28; i++) {
      const angle = Math.random() * Math.PI * 2;
      const vel = Math.random() * 5 + 2;
      sparkParticles.push({
        x,
        y,
        vx: Math.cos(angle) * vel,
        vy: Math.sin(angle) * vel,
        life: 1.0,
        decay: Math.random() * 0.03 + 0.02,
        color
      });
    }
  }

  function logTerminal(msg) {
    const term = document.getElementById("sim-terminal-log");
    if (!term) return;
    const line = document.createElement("div");
    line.style.marginBottom = "4px";
    line.style.lineHeight = "1.5";
    line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    term.appendChild(line);
    term.scrollTop = term.scrollHeight;
  }

  function updateHUDDisplays() {
    const plainHex = document.getElementById("sim-plain-hex");
    const bobHex = document.getElementById("sim-bob-hex");
    const eveHex = document.getElementById("sim-eve-hex");
    const matchBadge = document.getElementById("sim-match-badge");

    if (plainHex) plainHex.textContent = plainBits.join("");
    if (bobHex) {
      bobHex.textContent = bobBits.join("");
      bobHex.style.color = isCorrected ? COLORS.green : COLORS.amber;
    }
    if (eveHex) {
      const noisy = plainBits.map((b, idx) => (idx % 2 === 0 ? b ^ 1 : b));
      eveHex.textContent = noisy.join("");
    }

    if (matchBadge) {
      if (isCorrected) {
        matchBadge.className = "hash-pill match";
        matchBadge.textContent = "✓ 100.00% SHA-256 MATCH";
      } else {
        matchBadge.className = "hash-pill mismatch";
        matchBadge.textContent = "⚠️ RECONCILING (SEC PENDING)";
      }
    }
  }

  // حلقة الرسم الرئيسية 60 FPS
  function animate() {
    animId = requestAnimationFrame(animate);
    animClock += 0.025;

    if (!ctx || !canvas) return;
    try {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. رسم الوصلات المشبكية والنبضات الخاملة
      drawSynapses();
      drawIdlePulses();

      // 2. انزلاق نافذة المرشح التلافيفي (Conv1D Kernel Sweep)
      drawConvKernelSweep();

      // 3. رسم القناة العامة المشوشة وتفريعة إيف
      drawPublicChannel();

      // 4. رسم الليبلات المعمارية الدائمة الشاملة
      drawPermanentArchitecturalLabels();

      // 5. رسم كتل الخلايا العصبية
      drawNodes(aliceNodes, COLORS.cyan);
      drawNodes(bobNodes, COLORS.green);
      drawNodes(eveNodes, COLORS.red);

      // 6. تحديث ورسم إشارات الداتا
      updateSignals();

      // 7. رسم شعاع الليزر الأخضر لتصحيح هامنغ
      if (laserBeam) {
        drawLaser();
      }

      // 8. رسم موجات هامنغ الدائرية المتوسعة
      drawRipples();

      // 9. تحديث ورسم الشرر
      updateSparks();

      // دورة المراحل التلقائية
      if (isRunning) {
        stageTimer += 0.016 * speed;
        if (stageTimer > 1.35) {
          stageTimer = 0;
          stepStage = (stepStage % 6) + 1;
          executeStageLogic(stepStage);
        }
      }
    } catch (err) {
      console.error("NeuralSimulator animation error:", err);
    }
  }

  function drawSynapses() {
    synapses.forEach(s => {
      const isActive = s.from.activity > 0;
      ctx.lineWidth = isActive ? 1.8 : 1.0;
      ctx.strokeStyle = isActive ? COLORS.activeWire : s.wireColor;
      ctx.beginPath();
      ctx.moveTo(s.from.x, s.from.y);
      ctx.lineTo(s.to.x, s.to.y);
      ctx.stroke();
    });
  }

  function drawIdlePulses() {
    idlePulses.forEach(p => {
      p.progress += p.speed;
      if (p.progress > 1.0) {
        p.progress = 0;
        if (synapses.length > 0) {
          p.syn = synapses[Math.floor(Math.random() * synapses.length)];
        }
      }
      if (!p.syn || !p.syn.from || !p.syn.to) return;
      const x = p.syn.from.x + (p.syn.to.x - p.syn.from.x) * p.progress;
      const y = p.syn.from.y + (p.syn.to.y - p.syn.from.y) * p.progress;

      ctx.beginPath();
      ctx.arc(x, y, 2.0, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });
  }

  // انزلاق نافذة المرشح التلافيفي الواقعي (Conv1D Kernel Sweep)
  function drawConvKernelSweep() {
    convSweepProgress += 0.015 * speed;
    if (convSweepProgress > 1.0) convSweepProgress = 0;

    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    // نافذة تلافيف أليس
    const aConvX = w * 0.22 + 25;
    const sweepY = h * 0.20 + (h * 0.45) * Math.sin(animClock * 2) * 0.5 + (h * 0.22);
    ctx.strokeStyle = "rgba(0, 180, 216, 0.7)";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3, 3]);
    ctx.strokeRect(aConvX - 12, sweepY - 14, 24, 28);
    ctx.setLineDash([]);

    ctx.font = "bold 9px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.cyan;
    ctx.textAlign = "center";
    ctx.fillText("Kernel k=4", aConvX, sweepY - 18);
  }

  // رسم الليبلات المعمارية الدائمة والأبعاد التينسورية
  function drawPermanentArchitecturalLabels() {
    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    // 1. عناوين المحطات الرئيسية مع كبسولات أنيقة
    drawStationCapsule("محطة أليس (AliceNet — 3,857 Params)", w * 0.22, 28, COLORS.cyan);
    drawStationCapsule("محطة بوب الشرعي (BobNet — 3,857 Params)", w * 0.78, 28, COLORS.green);
    drawStationCapsule("محطة المتنصت (Deep Residual Eve — 26,161 Params)", w * 0.5, h * 0.62, COLORS.red);

    // 2. ليبلات أعمدة طبقات أليس
    const aCenterX = w * 0.22;
    drawColumnTag("Msg+Key", "[32-dim]", aCenterX - 110, h * 0.76, COLORS.cyan);
    drawColumnTag("FC Mixer", "[32x32]", aCenterX - 45, h * 0.76, COLORS.blue);
    drawColumnTag("Conv1D", "[k=4, 32c]", aCenterX + 25, h * 0.76, COLORS.purple);
    drawColumnTag("Float16", "[Parity 5b]", aCenterX + 95, h * 0.76, COLORS.cyan);

    // 3. ليبلات أعمدة طبقات بوب
    const bCenterX = w * 0.78;
    drawColumnTag("Cipher+Key", "[32-dim]", bCenterX - 95, h * 0.76, COLORS.purple);
    drawColumnTag("Inv Conv", "[Inversion]", bCenterX - 35, h * 0.76, COLORS.green);
    drawColumnTag("Inv Mixer", "[FC 32x32]", bCenterX + 30, h * 0.76, COLORS.blue);
    drawColumnTag("Reconstructed", "[100% SHA]", bCenterX + 95, h * 0.76, COLORS.green);

    // 4. ليبلات إيف
    ctx.font = "10px 'Fira Code', monospace";
    ctx.fillStyle = "rgba(244, 63, 94, 0.85)";
    ctx.textAlign = "center";
    ctx.fillText("4x Residual Conv Blocks (64 Channels) ➔ Barrier: BER = 45.40% (Shannon Equivocation)", w * 0.5, h * 0.94);
  }

  function drawStationCapsule(title, x, y, color) {
    ctx.font = "bold 12.5px 'Cairo', sans-serif";
    const textW = ctx.measureText(title).width;

    ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x - textW / 2 - 12, y - 16, textW + 24, 24, 12);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.fillText(title, x, y);
  }

  function drawColumnTag(title, dim, x, y, color) {
    ctx.font = "bold 9.5px 'Cairo', sans-serif";
    ctx.fillStyle = color;
    ctx.textAlign = "center";
    ctx.fillText(title, x, y);

    ctx.font = "8.5px 'Fira Code', monospace";
    ctx.fillStyle = "rgba(255, 255, 255, 0.55)";
    ctx.fillText(dim, x, y + 12);
  }

  function drawNodes(nodes, themeColor) {
    nodes.forEach(n => {
      const isHovered = (hoveredNode && hoveredNode.id === n.id);

      // هالة إشعاعية
      const glow = Math.abs(Math.sin(animClock * 3 + n.x * 0.1)) * 3;
      ctx.beginPath();
      ctx.arc(n.x, n.y, Math.max(1, n.radius + glow), 0, Math.PI * 2);
      ctx.fillStyle = n.activity > 0 ? themeColor : "rgba(255, 255, 255, 0.08)";
      ctx.fill();

      // الخلية الصلبة
      ctx.beginPath();
      ctx.arc(n.x, n.y, Math.max(1, n.radius), 0, Math.PI * 2);
      ctx.fillStyle = (n.isErrorBit && !isCorrected) ? COLORS.amber : n.color;
      ctx.fill();

      // حلقة تمييز عند التحويم بالفأرة
      if (isHovered) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 6, 0, Math.PI * 2);
        ctx.strokeStyle = COLORS.amber;
        ctx.lineWidth = 2.5;
        ctx.stroke();
      }

      // حلقة نشاط عند مرور النبضات
      if (n.activity > 0) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, Math.PI * 2);
        ctx.strokeStyle = n.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        n.activity = Math.max(0, n.activity - 0.02);
      }
    });
  }

  function drawPublicChannel() {
    const w = canvas.width || 1100;
    const h = canvas.height || 440;
    const x1 = w * 0.35;
    const x2 = w * 0.65;
    const y = h * 0.32;

    // خط القناة العامة المنحني
    ctx.beginPath();
    ctx.moveTo(x1, y);
    ctx.bezierCurveTo(w * 0.5, y - 18, w * 0.5, y + 18, x2, y);
    ctx.strokeStyle = "rgba(157, 78, 221, 0.65)";
    ctx.lineWidth = 3;
    ctx.setLineDash([6, 6]);
    ctx.stroke();
    ctx.setLineDash([]);

    // تفريعة التنصت لإيف
    ctx.beginPath();
    ctx.moveTo(w * 0.5, y);
    ctx.lineTo(w * 0.5, h * 0.68);
    ctx.strokeStyle = "rgba(244, 63, 94, 0.55)";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // تسميات القناة
    ctx.font = "bold 11px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.purple;
    ctx.textAlign = "center";
    ctx.fillText("📡 Noisy Public Channel (Float16 + 5-bit SEC)", w * 0.5, y - 24);

    ctx.font = "10px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.red;
    ctx.fillText("▼ Adversarial Wiretap (Zero Key)", w * 0.5 + 88, h * 0.52);
  }

  function updateSignals() {
    for (let i = signalParticles.length - 1; i >= 0; i--) {
      const p = signalParticles[i];
      p.progress += p.speed;

      const curX = p.x + (p.targetX - p.x) * p.progress;
      const curY = p.y + (p.targetY - p.y) * p.progress;

      ctx.beginPath();
      ctx.arc(curX, curY, 3.5, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();

      if (p.progress >= 1.0) {
        signalParticles.splice(i, 1);
      }
    }
  }

  function drawLaser() {
    if (!laserBeam || laserBeam.life <= 0) {
      laserBeam = null;
      return;
    }
    laserBeam.life -= 0.04;
    const currentLife = Math.max(0.01, laserBeam.life);

    // شعاع الليزر الأخضر
    ctx.beginPath();
    ctx.moveTo(laserBeam.fromX, laserBeam.fromY);
    ctx.lineTo(laserBeam.toX, laserBeam.toY);
    ctx.strokeStyle = `rgba(0, 217, 165, ${currentLife})`;
    ctx.lineWidth = Math.max(1, 4.5 * currentLife);
    ctx.stroke();

    // هالة الهدف
    const targetRadius = Math.max(1, 18 * (1 - currentLife * 0.5));
    ctx.beginPath();
    ctx.arc(laserBeam.toX, laserBeam.toY, targetRadius, 0, Math.PI * 2);
    ctx.strokeStyle = COLORS.green;
    ctx.lineWidth = 2;
    ctx.stroke();

    // وسم تصحيح المتلازمة المباشر
    ctx.font = "bold 10.5px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.green;
    ctx.textAlign = "center";
    ctx.fillText("⚡ S=(H·P^T)⊕Parity ➔ Bit #6 Corrected ✓", laserBeam.toX - 25, laserBeam.toY - 14);

    if (laserBeam.life <= 0) {
      laserBeam = null;
    }
  }

  // رسم موجات هامنغ الدائرية المتوسعة
  function drawRipples() {
    for (let i = rippleWaves.length - 1; i >= 0; i--) {
      const r = rippleWaves[i];
      r.radius += 2.0;
      r.alpha -= 0.025;

      if (r.alpha <= 0) {
        rippleWaves.splice(i, 1);
        continue;
      }

      ctx.beginPath();
      ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(0, 217, 165, ${r.alpha})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }

  function updateSparks() {
    for (let i = sparkParticles.length - 1; i >= 0; i--) {
      const s = sparkParticles[i];
      s.x += s.vx;
      s.y += s.vy;
      s.life -= s.decay;

      if (s.life <= 0) {
        sparkParticles.splice(i, 1);
        continue;
      }

      const sparkR = Math.max(0.2, 2.5 * s.life);
      ctx.beginPath();
      ctx.arc(s.x, s.y, sparkR, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.fill();
    }
  }

  return {
    init,
    resize,
    startSimulation,
    pauseSimulation,
    stepForward,
    jumpToStage,
    setSpeed,
    resetSimulationState
  };
})();

// تصدير الكائن إلى النطاق العام لضمان الوصول من أزرار الواجهة والسلايدات
if (typeof window !== "undefined") {
  window.NeuralSimulator = NeuralSimulator;
}
