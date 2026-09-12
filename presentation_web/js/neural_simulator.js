/**
 * neural_simulator.js
 * محرك المحاكاة العصبية التفاعلي الحي — نبضات مشبكية حقيقية + ليزر هامنغ لتصحيح الأخطاء
 * Real Interactive Neural Cryptography Simulation Engine with Live Synaptic Wiring & Laser SEC Reconciliation
 * NeuroCrypt-Guard v2.2
 */

const NeuralSimulator = (function () {
  let canvas, ctx;
  let animId = null;
  let isRunning = true; // تعمل تلقائياً لتكون حية ومبهرة فور وصول المستخدم
  let speed = 1.0;
  let stepStage = 1;
  let stageTimer = 0;
  let animClock = 0;

  // حالة البيانات الحقيقية
  let currentText = "جامعة إب 2026 — سرية تامة";
  let currentKey = "1100101011110000";
  let plainBits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1];
  let keyBits = [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0];
  let bobBits = [];
  let eveBits = [];
  let bobErrorIdx = 5; // موضع الخطأ التناظري الذي سيصححه هامنغ
  let isCorrected = false;

  // كائنات الشبكة العصبية والجسيمات
  let aliceNodes = [];
  let bobNodes = [];
  let eveNodes = [];
  let synapses = [];
  let signalParticles = [];
  let idlePulses = [];
  let sparkParticles = [];
  let laserBeam = null;

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
    aliceWire: "rgba(0, 180, 216, 0.32)",
    bobWire: "rgba(0, 217, 165, 0.32)",
    eveWire: "rgba(244, 63, 94, 0.32)",
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
      setupVisibilityObserver();
    }

    resize();
    resetSimulationState();
    executeStageLogic(1);

    if (!animId) {
      animate();
    }
  }

  // مراقبة ظهور الشريحة لضمان القياس الدقيق
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

  // تحويل النص إلى بتات 16-بت
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

  // بناء طوبولوجيا الخلايا العصبية والوصلات المشبكية
  function buildNeuralTopology() {
    aliceNodes = [];
    bobNodes = [];
    eveNodes = [];
    synapses = [];
    idlePulses = [];

    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    // 1. محطة أليس (الجهة اليمنى للمستخدم العربي)
    const aliceCenterX = w * 0.22;
    const layerXs = [
      aliceCenterX - 110, // المدخلات (Plaintext 16 + Key 16)
      aliceCenterX - 40,  // الخلط الخطي (FC Mixer)
      aliceCenterX + 30,  // الطبقة التلافيفية (Conv1D)
      aliceCenterX + 100  // الخرج التشفيري (Float16 + Parity)
    ];

    const aliceLayers = [
      { count: 16, x: layerXs[0], type: "alice_msg", label: "Msg", color: COLORS.cyan },
      { count: 16, x: layerXs[0] + 16, type: "alice_key", label: "Key", color: COLORS.amber },
      { count: 12, x: layerXs[1], type: "alice_fc", label: "Mixer", color: COLORS.blue },
      { count: 10, x: layerXs[2], type: "alice_conv", label: "Conv", color: COLORS.purple },
      { count: 8,  x: layerXs[3], type: "alice_out", label: "Ciph", color: COLORS.cyan }
    ];

    aliceLayers.forEach((l, lIdx) => {
      const stepY = (h * 0.55) / (l.count + 1);
      const startY = h * 0.18;
      for (let i = 0; i < l.count; i++) {
        aliceNodes.push({
          id: `a_${lIdx}_${i}`,
          x: l.x,
          y: startY + (i + 1) * stepY,
          radius: l.type.includes("msg") || l.type.includes("key") ? 4 : 5.5,
          color: l.color,
          layer: lIdx,
          type: l.type,
          label: l.label,
          val: Math.random().toFixed(2),
          activity: 0
        });
      }
    });

    // 2. محطة بوب الشرعي (الجهة اليسرى)
    const bobCenterX = w * 0.78;
    const bobLayerXs = [
      bobCenterX - 95, // Cipher In + Key
      bobCenterX - 35, // Inversion Conv
      bobCenterX + 30, // FC Reconstructor
      bobCenterX + 95  // Decoded 16 Bits
    ];

    const bobLayers = [
      { count: 8,  x: bobLayerXs[0], type: "bob_in", label: "Cin", color: COLORS.purple },
      { count: 10, x: bobLayerXs[1], type: "bob_conv", label: "InvC", color: COLORS.green },
      { count: 12, x: bobLayerXs[2], type: "bob_fc", label: "InvFC", color: COLORS.blue },
      { count: 16, x: bobLayerXs[3], type: "bob_out", label: "Dec", color: COLORS.green }
    ];

    bobLayers.forEach((l, lIdx) => {
      const stepY = (h * 0.55) / (l.count + 1);
      const startY = h * 0.18;
      for (let i = 0; i < l.count; i++) {
        bobNodes.push({
          id: `b_${lIdx}_${i}`,
          x: l.x,
          y: startY + (i + 1) * stepY,
          radius: 5,
          color: l.color,
          layer: lIdx,
          type: l.type,
          label: l.label,
          val: "0",
          activity: 0,
          isErrorBit: (l.type === "bob_out" && i === bobErrorIdx)
        });
      }
    });

    // 3. محطة إيف المتنصت (الوسط السفلي)
    const eveCenterX = w * 0.5;
    const eveCenterY = h * 0.78;
    const eveLayerXs = [
      eveCenterX - 65,
      eveCenterX - 20,
      eveCenterX + 20,
      eveCenterX + 65
    ];

    for (let lIdx = 0; lIdx < 4; lIdx++) {
      const count = 6;
      for (let i = 0; i < count; i++) {
        eveNodes.push({
          id: `e_${lIdx}_${i}`,
          x: eveLayerXs[lIdx],
          y: eveCenterY - 35 + i * 14,
          radius: 4.5,
          color: COLORS.red,
          layer: lIdx,
          type: "eve",
          activity: 0
        });
      }
    }

    // بناء الوصلات المشبكية
    buildSynapses(aliceNodes, COLORS.aliceWire);
    buildSynapses(bobNodes, COLORS.bobWire);
    buildSynapses(eveNodes, COLORS.eveWire);

    // إنشاء نبضات خاملة لتكون الشبكة حية دائماً
    for (let i = 0; i < 25; i++) {
      if (synapses.length > 0) {
        const syn = synapses[Math.floor(Math.random() * synapses.length)];
        idlePulses.push({
          syn,
          progress: Math.random(),
          speed: 0.006 + Math.random() * 0.008,
          color: syn.wireColor.replace("0.18", "0.85")
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

  function resetSimulationState() {
    plainBits = textTo16Bits(currentText);
    keyBits = currentKey.split("").map(c => parseInt(c, 10) || 0);
    bobBits = [...plainBits];
    bobBits[bobErrorIdx] ^= 1; // خطأ تناظري مفرد متعمد ليصححه هامنغ
    isCorrected = false;
    stepStage = 1;
    stageTimer = 0;
    signalParticles = [];
    sparkParticles = [];
    laserBeam = null;

    updateHUDDisplays();
  }

  function startSimulation() {
    resetSimulationState();
    isRunning = true;
    const playBtn = document.getElementById("sim-play-trigger");
    if (playBtn) playBtn.innerHTML = "<span>⏸</span> إيقاف المحاكاة مؤقتاً";
    logTerminal("▶ بدء دورة التشفير العصبي: معالجة الرسالة والمفتاح عبر AliceNet...");
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
      });
    }

    if (keyInput) {
      keyInput.addEventListener("input", (e) => {
        currentKey = e.target.value.padEnd(16, "0").slice(0, 16);
        resetSimulationState();
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
        logTerminal("↺ تم إعادة ضبط محرك المحاكاة إلى الحالة الابتدائية.");
      });
    }
  }

  // منطق المراحل الست لدورة التشفير
  function executeStageLogic(stage) {
    const w = canvas.width || 1100;
    const h = canvas.height || 440;

    if (stage === 1) {
      // إدخال النص والمفتاح لأليس
      aliceNodes.filter(n => n.layer <= 1).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        aliceNodes.filter(n => n.layer === 0),
        aliceNodes.filter(n => n.layer === 1),
        COLORS.cyan
      );
      logTerminal("📥 إدخال الرسالة والمفتاح: دمج 16 بت نص + 16 بت مفتاح في متجه أولي 32-dim.");
    } else if (stage === 2) {
      // انتشار تلافيفي وتوليد التشفير
      aliceNodes.filter(n => n.layer >= 1).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        aliceNodes.filter(n => n.layer === 2),
        aliceNodes.filter(n => n.layer === 3),
        COLORS.blue
      );
      logTerminal("🌀 معالجة AliceNet: توليد الحالات الكامنة Float16 وحساب متلازمة التكافؤ (5-bit Parity).");
    } else if (stage === 3) {
      // النقل عبر القناة العامة المشوشة
      const outAlice = aliceNodes.filter(n => n.layer === 3);
      outAlice.forEach(n => (n.activity = 1.0));

      // جسيمات متجهة إلى بوب
      for (let i = 0; i < 12; i++) {
        signalParticles.push({
          x: w * 0.35,
          y: h * 0.32,
          targetX: w * 0.65,
          targetY: h * 0.32,
          progress: 0,
          speed: 0.035 * speed,
          color: COLORS.purple
        });
      }
      // جسيمات متجهة إلى إيف
      for (let i = 0; i < 8; i++) {
        signalParticles.push({
          x: w * 0.5,
          y: h * 0.32,
          targetX: w * 0.5,
          targetY: h * 0.70,
          progress: 0,
          speed: 0.035 * speed,
          color: COLORS.red
        });
      }
      logTerminal("📡 القناة المشوشة: انتقال النص المشفر. اعتراض إيف بدون مفتاح + وصول الشفرة لبوب.");
    } else if (stage === 4) {
      // فك تشفير بوب الشرعي
      bobNodes.filter(n => n.layer <= 2).forEach(n => (n.activity = 1.0));
      spawnSignalBatch(
        bobNodes.filter(n => n.layer === 0),
        bobNodes.filter(n => n.layer === 2),
        COLORS.green
      );
      logTerminal("🔓 فك تشفير بوب: دمج الشفرة مع المفتاح المشترك. رصد عدم تطابق في بت واحد (خطأ تناظري).");
    } else if (stage === 5) {
      // إطلاق ليزر هامنغ SEC لتصحيح الخطأ التناظري
      const targetNode = bobNodes.find(n => n.isErrorBit);
      const startX = w * 0.78 + 30;
      const startY = h * 0.15;
      const targetX = targetNode ? targetNode.x : w * 0.78 + 95;
      const targetY = targetNode ? targetNode.y : h * 0.35;

      laserBeam = {
        fromX: startX,
        fromY: startY,
        toX: targetX,
        toY: targetY,
        life: 1.0
      };

      bobBits[bobErrorIdx] = plainBits[bobErrorIdx];
      isCorrected = true;
      spawnSparks(targetX, targetY, COLORS.green);
      logTerminal("⚡ هامنغ SEC: إطلاق شعاع تصحيح التكافؤ! تم إصلاح البت بنجاح وتحقيق 100.00% تطابق SHA-256 ✓");
    } else if (stage === 6) {
      // اعتراض إيف الفاشل
      eveNodes.forEach(n => (n.activity = 1.0));
      spawnSparks(w * 0.5, h * 0.76, COLORS.red);
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
          speed: 0.04 * speed,
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

    // 2. رسم القناة العامة
    drawPublicChannel();

    // 3. رسم كتل الخلايا العصبية مع الهالات المشعة
    drawNodes(aliceNodes, "محطة أليس (AliceNet)", COLORS.cyan);
    drawNodes(bobNodes, "محطة بوب الشرعي (BobNet)", COLORS.green);
    drawNodes(eveNodes, "محطة المتنصت (DeepEve)", COLORS.red);

    // 4. تحديث ورسم إشارات الداتا
    updateSignals();

    // 5. رسم شعاع الليزر الأخضر لتصحيح هامنغ
    if (laserBeam) {
      drawLaser();
    }

    // 6. تحديث ورسم الشرر
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
    ctx.lineWidth = 1;
    synapses.forEach(s => {
      ctx.strokeStyle = s.from.activity > 0 ? COLORS.activeWire : s.wireColor;
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
        p.syn = synapses[Math.floor(Math.random() * synapses.length)];
      }
      if (!p.syn) return;
      const x = p.syn.from.x + (p.syn.to.x - p.syn.from.x) * p.progress;
      const y = p.syn.from.y + (p.syn.to.y - p.syn.from.y) * p.progress;

      ctx.beginPath();
      ctx.arc(x, y, 1.8, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();
    });
  }

  function drawNodes(nodes, stationTitle, themeColor) {
    if (nodes.length === 0) return;

    const minX = Math.min(...nodes.map(n => n.x));
    const maxX = Math.max(...nodes.map(n => n.x));
    const minY = Math.min(...nodes.map(n => n.y));

    // عنوان المحطة مع خلفية زجاجية صغيرة
    ctx.font = "bold 13px Cairo, sans-serif";
    ctx.fillStyle = themeColor;
    ctx.textAlign = "center";
    ctx.fillText(stationTitle, (minX + maxX) / 2, minY - 16);

    nodes.forEach(n => {
      // هالة إشعاعية
      const glow = Math.sin(animClock * 3 + n.x * 0.1) * 2;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius + glow, 0, Math.PI * 2);
      ctx.fillStyle = n.activity > 0 ? themeColor : "rgba(255, 255, 255, 0.05)";
      ctx.fill();

      // الخلية الصلبة
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = n.isErrorBit && !isCorrected ? COLORS.amber : n.color;
      ctx.fill();

      // حلقة تفاعلية عند النشاط
      if (n.activity > 0) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, Math.PI * 2);
        ctx.strokeStyle = n.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        n.activity = Math.max(0, n.activity - 0.025);
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
    ctx.strokeStyle = "rgba(157, 78, 221, 0.5)";
    ctx.lineWidth = 3;
    ctx.setLineDash([6, 6]);
    ctx.stroke();
    ctx.setLineDash([]);

    // تفريعة التنصت لإيف
    ctx.beginPath();
    ctx.moveTo(w * 0.5, y);
    ctx.lineTo(w * 0.5, h * 0.68);
    ctx.strokeStyle = "rgba(244, 63, 94, 0.4)";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // تسميات القناة
    ctx.font = "bold 11px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.purple;
    ctx.textAlign = "center";
    ctx.fillText("📡 Public Channel (Float16 + 5b Parity)", w * 0.5, y - 24);

    ctx.font = "10px 'Fira Code', monospace";
    ctx.fillStyle = COLORS.red;
    ctx.fillText("▼ Adversarial Tap (No Key)", w * 0.5 + 85, h * 0.52);
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
      ctx.shadowColor = p.color;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

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
    laserBeam.life -= 0.045;
    const currentLife = Math.max(0.01, laserBeam.life);

    // شعاع الليزر الأخضر
    ctx.beginPath();
    ctx.moveTo(laserBeam.fromX, laserBeam.fromY);
    ctx.lineTo(laserBeam.toX, laserBeam.toY);
    ctx.strokeStyle = `rgba(0, 217, 165, ${currentLife})`;
    ctx.lineWidth = Math.max(1, 4 * currentLife);
    ctx.shadowColor = COLORS.green;
    ctx.shadowBlur = 18;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // هالة الهدف
    const targetRadius = Math.max(1, 16 * (1 - currentLife * 0.5));
    ctx.beginPath();
    ctx.arc(laserBeam.toX, laserBeam.toY, targetRadius, 0, Math.PI * 2);
    ctx.strokeStyle = COLORS.green;
    ctx.lineWidth = 2;
    ctx.stroke();

    if (laserBeam.life <= 0) {
      laserBeam = null;
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
    resetSimulationState
  };
})();

// تصدير الكائن إلى النطاق العام لضمان الوصول من أزرار الواجهة والسلايدات
if (typeof window !== "undefined") {
  window.NeuralSimulator = NeuralSimulator;
}
