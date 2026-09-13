/**
 * neural3d.js (Ultra-Detailed Holographic Architecture & Operational Mechanism Simulation)
 * محرك العرض ثلاثي الأبعاد فائق التفاصيل: خلايا عصبية مجسمة، ألياف مشبكية، مسح التلافيف، ومنشور هامنغ بالليزر
 * NeuroCrypt-Guard v2.2 — High-Fidelity 3D Neural Architecture Lab
 */

const Neural3D = (function () {
  let scene, camera, renderer, container;
  let animationFrameId = null;
  let isSimulating = true;
  let simSpeed = 1.0;
  let simProgress = 0.0;
  let currentMode = "overview";
  let mechanismStage = 0; // 0: Continuous, 1: Alice, 2: Channel, 3: Bob, 4: Laser SEC, 5: Eve
  let stageTimer = 0;

  let aliceGroup, bobGroup, eveGroup, channelGroup;
  let particleSystems = [];
  let raycaster, mouse;

  // عناصر تفصيلية للمحاكاة
  let aliceScanBox = null;
  let secCrystalPrism = null;
  let secPrismRings = [];
  let secLaserBeam = null;
  let secWavefront = null;
  let bobFaultyNeuron = null;
  let eveNoiseParticles = null;
  let eveSkipTubes = [];
  let dynamicSynapses = [];
  let allInteractiveNeurons = [];

  // نصوص الشرح الأكاديمي المتزامن
  const mechanismExplanations = {
    0: `<strong style="color: var(--gold);">[🔄 التدفق الشامل المستمر]</strong> محاكاة متزامنة متكاملة: أليس تشفر الرسالة بـ Float16 وتولد التكافؤ، تنطلق الإشارة عبر القناة العامة مع تفريعة إيف، بوب يعيد بناء النص ويصلح البت بالليزر (100% SHA-256)، وإيف تعجز تماماً عند حد شانون (45.40%).`,
    1: `<strong style="color: var(--accent);">[🌀 المرحلة 1: تشفير أليس (AliceNet)]</strong> تدفق تينسورات الرسالة (16 بت أزرق) والمفتاح (16 بت ذهبي) في شبكة الخلط FC Mixer لتحقيق الارتباك الشامل، ثم تجري طبقات التلافيف مسحاً حياً (Sliding Kernel Sweep) لتوليد شفرة Float16 مع 5 بتات تكافؤ.`,
    2: `<strong style="color: #8b5cf6);">[📡 المرحلة 2: بث القناة المشوشة وتفريعة التنصت]</strong> انطلاق حزم البيانات المشفرة كإشارات تناظرية عبر القناة العامة المفتوحة نحو بوب، مع اعتراض متزامن من مجسات إيف المتنصتة (بدون أي وصول للمفتاح السري المشترك).`,
    3: `<strong style="color: var(--green);">[🔓 المرحلة 3: فك تشفير بوب الشرعي (BobNet)]</strong> يدمج بوب الشفرة مع المفتاح السري، وتعيد شبكة Inversion CNN بناء التينسور بدقة 99.93%، مع ظهور خلل تكميم أحادي في الخلية العصبية رقم #6 (وميض أحمر).`,
    4: `<strong style="color: #34d399);">[⚡ المرحلة 4: توفيق هامنغ بالليزر الهولوغرافي]</strong> ينشط منشور هامنغ البلوري متعدد الأوجه ويحسب المتلازمة S = (H·P^T) ⊕ Parity، ويطلق شعاع ليزر أخضر مكثف نحو الخلية #6، محولاً إياها للأخضر ومحققاً تطابق SHA-256 بنسبة 100.00%!`,
    5: `<strong style="color: var(--red);">[🚨 المرحلة 5: عجز وانهيار المتنصت DeepEve]</strong> يمرر الخصم الشفرة عبر 4 طبقات تلافيفية عميقة ووصلات متبقية (26,161 بارامتر)، ولكن بدون المفتاح تفشل الشبكة وتضطرب أليافها العصبية عند حد شانون العشوائي (BER = 45.40%)!`
  };

  // بيانات الطبقات لمفتش الطبقات
  const layerData = {
    alice_in: {
      title: "أليس: بنك الإدخال المزدوج (Input Tensor Bank)",
      shape: "Tensor [Batch, 32] = 16b Msg + 16b Key",
      params: "0 (تغذية مباشرة)",
      func: "Concatenate(Plaintext, SharedKey)",
      role: "32 خلية عصبية مجسمة: 16 خلية نص صريح (سيان) + 16 خلية مفتاح سري (ذهبي)"
    },
    alice_fc: {
      title: "أليس: مصفوفة الخلط الخطي (FC Confusion Matrix)",
      shape: "Linear: 32 → 32 (32 Neurons, 1,024 Synapses)",
      params: "1,056 وزن وتحيز",
      func: "LeakyReLU(α = 0.2)",
      role: "شبكة مشبكية كثيفة تحقق خاصية الارتباك (Confusion) بخلط كل بت مع كافة البتات"
    },
    alice_c1: {
      title: "أليس: تلافيف الانتشار الأولى (Conv1D-1 + Sliding Kernel)",
      shape: "Conv1D: 1 → 32 قنوات, Kernel Size = 4",
      params: "160 وزن",
      func: "LeakyReLU(α = 0.2) + Same Padding",
      role: "إطار مسح تلافيفي هولوغرافي متحرك ينشر تأثير كل بت على الكتل المجاورة (Diffusion)"
    },
    alice_c2: {
      title: "أليس: تلافيف التركيب غير الخطي (Conv1D-2)",
      shape: "Conv1D: 32 → 16 قنوات, Kernel Size = 2",
      params: "1,040 وزن",
      func: "LeakyReLU(α = 0.2)",
      role: "تركيب علاقات لاخطية عميقة وتكثيف الخصائص التشفيرية"
    },
    alice_c3: {
      title: "أليس: خلايا الخرج التناظري ومتجهات التكافؤ",
      shape: "16 Float16 Continuous Nodes + 5 Parity Generator Nodes",
      params: "17 وزن",
      func: "Tanh ([-1.0, 1.0]) + Hamming Generator Matrix G",
      role: "توليد الشفرة التناظرية مع شجرة متجهات التكافؤ الخماسية الموجهة لبوب"
    },
    bob_in: {
      title: "بوب: بنك الاستقبال الشرعي المزدوج",
      shape: "Tensor [Batch, 32] = Ciphertext + SharedKey",
      params: "0",
      func: "Concatenate(Ciphertext, Key)",
      role: "استقبال شفرة القناة مع حقن المفتاح السري المشترك الموثوق"
    },
    bob_fc: {
      title: "بوب: مصفوفة عزل التشفير العكسية",
      shape: "Linear: 32 → 32 (32 Inverse Neurons)",
      params: "1,056 وزن",
      func: "LeakyReLU(α = 0.2)",
      role: "فك الارتباك الأولي بالاعتماد على المفتاح المشترك"
    },
    bob_conv: {
      title: "بوب: شبكة إعادة البناء التلافيفية العكسية (Inversion CNN)",
      shape: "3x Conv1D Inversion Blocks (32 → 16 → 1)",
      params: "1,217 وزن",
      func: "LeakyReLU + Tanh",
      role: "إعادة بناء الرسالة التناظرية بدقة تقارب 99.93% مع ظهور خطأ تكميم أحادي في الخلية #6"
    },
    bob_sec: {
      title: "بوب: منشور التوفيق التشفيري (Hamming SEC Prism)",
      shape: "Octahedral Crystal Prism + Parity Matrix H (5 × 16)",
      params: "خوارزمية تصحيح حتمية بدون أوزان",
      func: "Syndrome S = (H · P^T) ⊕ Parity",
      role: "حساب المتلازمة وإطلاق شعاع ليزر هولوغرافي مكثف لإصلاح الخلية #6 فورياً (100% SHA-256)"
    },
    eve_deep: {
      title: "إيف: القلعة العصبية العميقة للخصم (Deep Residual Eve)",
      shape: "4 Tiers × 64 Channels + Dual Residual Skip Tubes",
      params: "26,161 وزناً (أكثر من 4 أضعاف أليس)",
      func: "Deep Convolutions + Skip Connections",
      role: "عجز كامل عن كسر التشفير بدون مفتاح، وتشتت النتائج كضوضاء شانون عشوائية (BER = 45.40%)"
    }
  };

  const cameraPositions = {
    overview: { x: 0, y: 34, z: 66, tx: 0, ty: 0, tz: 0 },
    alice: { x: -32, y: 14, z: 28, tx: -32, ty: 2, tz: 0 },
    bob: { x: 32, y: 14, z: 28, tx: 32, ty: 2, tz: 0 },
    eve: { x: 0, y: 22, z: -10, tx: 0, ty: 9, tz: -34 }
  };

  const stageCameraPositions = {
    0: { x: 0, y: 34, z: 66, tx: 0, ty: 0, tz: 0 },
    1: { x: -30, y: 14, z: 28, tx: -32, ty: 2, tz: 0 },
    2: { x: 0, y: 30, z: 58, tx: 0, ty: 2, tz: -8 },
    3: { x: 30, y: 14, z: 28, tx: 32, ty: 2, tz: 0 },
    4: { x: 32, y: 12, z: 18, tx: 32, ty: 1, tz: 3 },
    5: { x: 0, y: 20, z: -12, tx: 0, ty: 9, tz: -34 }
  };

  let targetCamPos = { ...cameraPositions.overview };
  let currentLookAt = { x: 0, y: 0, z: 0 };

  let isDragging = false;
  let prevMousePos = { x: 0, y: 0 };
  let sceneRotation = { x: 0.22, y: 0 };

  function init(containerElement) {
    container = containerElement;
    if (!container || !window.THREE) return;

    const width = container.clientWidth || 1100;
    const height = container.clientHeight || 600;

    // 1. Scene & Camera
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x040814, 0.007);

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(targetCamPos.x, targetCamPos.y, targetCamPos.z);

    // 2. Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const existingCanvas = container.querySelector("canvas");
    if (existingCanvas) existingCanvas.remove();
    container.insertBefore(renderer.domElement, container.firstChild);

    // 3. Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambient);

    const lightAlice = new THREE.PointLight(0x06b6d4, 4.5, 95);
    lightAlice.position.set(-32, 25, 20);
    scene.add(lightAlice);

    const lightBob = new THREE.PointLight(0x10b981, 4.5, 95);
    lightBob.position.set(32, 25, 20);
    scene.add(lightBob);

    const lightEve = new THREE.PointLight(0xf43f5e, 5.0, 95);
    lightEve.position.set(0, 32, -34);
    scene.add(lightEve);

    // 4. Cyber Ground Grid with Circuit Lines
    const grid = new THREE.GridHelper(150, 50, 0x1e293b, 0x0b1329);
    grid.position.y = -6.5;
    scene.add(grid);

    // 5. Build Ultra-Detailed Stations
    buildDetailedAliceStation();
    buildDetailedBobStation();
    buildDetailedEveStation();
    buildDetailedPublicChannel();
    buildHolographicLaserAndWave();
    buildEveNoiseCloud();
    setupParticleFlow();

    // 6. Interaction & Events
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    setupInteractionEvents();
    window.addEventListener("resize", onWindowResize);

    // 7. Initialize Banner & Telemetry
    updateMechanismBanner(0);
    updateTelemetry(0);

    // 8. Start Loop
    if (!animationFrameId) {
      animate();
    }
  }

  // دالة مساعدة لإنشاء خلية عصبية مجسمة ذات توهج حقيقي
  function createNeuronMesh(colorHex, radius = 0.36) {
    const geo = new THREE.SphereGeometry(radius, 16, 16);
    const mat = new THREE.MeshStandardMaterial({
      color: colorHex,
      emissive: colorHex,
      emissiveIntensity: 0.65,
      metalness: 0.8,
      roughness: 0.2
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.userData.baseColor = colorHex;
    return mesh;
  }

  // =========================================================================
  // 1. محطة أليس فائقة التفاصيل (ALICENET)
  // =========================================================================
  function buildDetailedAliceStation() {
    aliceGroup = new THREE.Group();
    aliceGroup.position.set(-32, 0, 0);

    // قاعدة المحطة السيبرانية
    const baseGeo = new THREE.CylinderGeometry(12, 13.5, 1.2, 40);
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x031c33, metalness: 0.85, roughness: 0.2 });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5.5;
    aliceGroup.add(base);

    // حلقة نيون متوهجة
    const ring = new THREE.Mesh(new THREE.TorusGeometry(13.2, 0.22, 12, 48), new THREE.MeshBasicMaterial({ color: 0x06b6d4 }));
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -4.8;
    aliceGroup.add(ring);

    // أعمدة الليزر الأربعة في زوايا المنصة
    const pillarGeo = new THREE.CylinderGeometry(0.18, 0.18, 14, 12);
    const pillarMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.7 });
    const pillarCoords = [[-10, 1.5, -9], [10, 1.5, -9], [-10, 1.5, 9], [10, 1.5, 9]];
    pillarCoords.forEach(([px, py, pz]) => {
      const p = new THREE.Mesh(pillarGeo, pillarMat);
      p.position.set(px, py, pz);
      aliceGroup.add(p);
    });

    aliceGroup.layerGroups = [];

    // --- الطبقة 1: بنك الإدخال (32 خلية عصبية مجسمة: 16 نص + 16 مفتاح) ---
    const l1 = new THREE.Group();
    l1.position.set(0, 0, -8);
    l1.userData = { id: "alice_in", defaultZ: -8, explodedZ: -18 };
    l1.neurons = [];

    // 16 Plaintext Neurons (Cyan)
    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0x06b6d4, 0.35);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set(-3.5 + col * 1.5, (row - 3.5) * 0.9, 0);
      n.userData = { id: "alice_in", role: `Plaintext Bit #${i}` };
      l1.add(n);
      l1.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    // 16 Shared Key Neurons (Gold)
    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0xf59e0b, 0.35);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set(1.0 + col * 1.5, (row - 3.5) * 0.9, 0);
      n.userData = { id: "alice_in", role: `Key Bit #${i}` };
      l1.add(n);
      l1.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    // إطار زجاجي رقيق شفاف
    const frameGeo1 = new THREE.BoxGeometry(9.5, 8.5, 1.2);
    const frameMat1 = new THREE.MeshPhysicalMaterial({ color: 0x0284c7, transmission: 0.9, opacity: 0.2, transparent: true });
    const f1 = new THREE.Mesh(frameGeo1, frameMat1);
    f1.userData = l1.userData;
    l1.add(f1);
    l1.hitBox = f1;

    aliceGroup.add(l1);
    aliceGroup.layerGroups.push(l1);

    // --- الطبقة 2: مصفوفة الخلط الخطي (FC Mixer 32x32) مع ألياف مشبكية ---
    const l2 = new THREE.Group();
    l2.position.set(0, 0, -4);
    l2.userData = { id: "alice_fc", defaultZ: -4, explodedZ: -9 };
    l2.neurons = [];

    // مصفوفة 4 أعمدة × 8 صفوف = 32 خلية
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 4; c++) {
        const n = createNeuronMesh(0x38bdf8, 0.32);
        n.position.set((c - 1.5) * 1.8, (r - 3.5) * 0.9, 0);
        n.userData = { id: "alice_fc", role: `Mixer Neuron [${r},${c}]` };
        l2.add(n);
        l2.neurons.push(n);
        allInteractiveNeurons.push(n);
      }
    }

    // ألياف مشبكية بين طبقة الإدخال وطبقة الخلط
    const synMat1 = new THREE.LineBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.25 });
    const synCoords1 = [];
    for (let i = 0; i < 32; i += 2) {
      const pSrc = l1.neurons[i].position;
      const pDst = l2.neurons[(i * 3) % 32].position;
      synCoords1.push(pSrc.x, pSrc.y, -8, pDst.x, pDst.y, -4);
    }
    const synGeo1 = new THREE.BufferGeometry();
    synGeo1.setAttribute("position", new THREE.Float32BufferAttribute(synCoords1, 3));
    const synLines1 = new THREE.LineSegments(synGeo1, synMat1);
    aliceGroup.add(synLines1);
    dynamicSynapses.push(synLines1);

    const f2 = new THREE.Mesh(new THREE.BoxGeometry(9.0, 8.5, 1.2), frameMat1.clone());
    f2.userData = l2.userData;
    l2.add(f2);
    l2.hitBox = f2;

    aliceGroup.add(l2);
    aliceGroup.layerGroups.push(l2);

    // --- الطبقة 3: تلافيف الانتشار الأولى (Conv1D-1, 32ch, k=4) مع إطار مسح متحرك ---
    const l3 = new THREE.Group();
    l3.position.set(0, 0, 0);
    l3.userData = { id: "alice_c1", defaultZ: 0, explodedZ: 0 };
    l3.neurons = [];

    // 4 أعمدة من 6 خلايا عصبية تمثل مرشحات التلافيف
    for (let c = 0; c < 4; c++) {
      for (let r = 0; r < 6; r++) {
        const n = createNeuronMesh(0x0ea5e9, 0.34);
        n.position.set((c - 1.5) * 1.9, (r - 2.5) * 1.1, 0);
        n.userData = { id: "alice_c1", role: `Conv1D Filter Neuron [${c},${r}]` };
        l3.add(n);
        l3.neurons.push(n);
        allInteractiveNeurons.push(n);
      }
    }

    // إطار مسح التلافيف المتحرك (Sliding Kernel Scanner)
    const scanGeo = new THREE.BoxGeometry(8.5, 2.4, 1.4);
    const scanMat = new THREE.LineBasicMaterial({ color: 0xffd700, linewidth: 2 });
    aliceScanBox = new THREE.LineSegments(new THREE.EdgesGeometry(scanGeo), scanMat);
    aliceScanBox.position.set(0, 0, 0);
    l3.add(aliceScanBox);

    const f3 = new THREE.Mesh(new THREE.BoxGeometry(8.8, 8.0, 1.2), frameMat1.clone());
    f3.userData = l3.userData;
    l3.add(f3);
    l3.hitBox = f3;

    aliceGroup.add(l3);
    aliceGroup.layerGroups.push(l3);

    // --- الطبقة 4: تلافيف التركيب غير الخطي (Conv1D-2, 16ch, k=2) ---
    const l4 = new THREE.Group();
    l4.position.set(0, 0, 4);
    l4.userData = { id: "alice_c2", defaultZ: 4, explodedZ: 9 };
    l4.neurons = [];

    for (let c = 0; c < 2; c++) {
      for (let r = 0; r < 8; r++) {
        const n = createNeuronMesh(0x38bdf8, 0.36);
        n.position.set((c - 0.5) * 2.6, (r - 3.5) * 0.9, 0);
        n.userData = { id: "alice_c2", role: `Depth Neuron [${c},${r}]` };
        l4.add(n);
        l4.neurons.push(n);
        allInteractiveNeurons.push(n);
      }
    }

    const f4 = new THREE.Mesh(new THREE.BoxGeometry(8.0, 8.2, 1.2), frameMat1.clone());
    f4.userData = l4.userData;
    l4.add(f4);
    l4.hitBox = f4;

    aliceGroup.add(l4);
    aliceGroup.layerGroups.push(l4);

    // --- الطبقة 5: مخرجات Float16 التناظرية + 5 بتات التكافؤ SEC ---
    const l5 = new THREE.Group();
    l5.position.set(0, 0, 8);
    l5.userData = { id: "alice_c3", defaultZ: 8, explodedZ: 18 };
    l5.neurons = [];

    // 16 Float16 Continuous Nodes (Cyan-Blue gradient)
    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0x00f0ff, 0.38);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set(-2.5 + col * 1.6, (row - 3.5) * 0.9, 0);
      n.userData = { id: "alice_c3", role: `Float16 Output Latent #${i}` };
      l5.add(n);
      l5.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    // 5 Parity Generator Nodes (Gold-Green)
    for (let i = 0; i < 5; i++) {
      const n = createNeuronMesh(0x10b981, 0.42);
      n.position.set(2.4, (i - 2.0) * 1.4, 0);
      n.userData = { id: "alice_c3", role: `Parity SEC Generator Bit P${i}` };
      l5.add(n);
      l5.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    const f5 = new THREE.Mesh(new THREE.BoxGeometry(8.2, 8.5, 1.2), frameMat1.clone());
    f5.userData = l5.userData;
    l5.add(f5);
    l5.hitBox = f5;

    aliceGroup.add(l5);
    aliceGroup.layerGroups.push(l5);

    scene.add(aliceGroup);
  }

  // =========================================================================
  // 2. محطة بوب فائقة التفاصيل (BOBNET & HAMMING SEC PRISM)
  // =========================================================================
  function buildDetailedBobStation() {
    bobGroup = new THREE.Group();
    bobGroup.position.set(32, 0, 0);

    const baseGeo = new THREE.CylinderGeometry(12, 13.5, 1.2, 40);
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x01261a, metalness: 0.85, roughness: 0.2 });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5.5;
    bobGroup.add(base);

    const ring = new THREE.Mesh(new THREE.TorusGeometry(13.2, 0.22, 12, 48), new THREE.MeshBasicMaterial({ color: 0x10b981 }));
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -4.8;
    bobGroup.add(ring);

    bobGroup.layerGroups = [];
    const frameMatBob = new THREE.MeshPhysicalMaterial({ color: 0x059669, transmission: 0.9, opacity: 0.2, transparent: true });

    // --- الطبقة 1: بنك الاستقبال (Ciphertext 16 + Shared Key 16) ---
    const b1 = new THREE.Group();
    b1.position.set(0, 0, -8);
    b1.userData = { id: "bob_in", defaultZ: -8, explodedZ: -18 };
    b1.neurons = [];

    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0x06b6d4, 0.35);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set(-3.5 + col * 1.5, (row - 3.5) * 0.9, 0);
      n.userData = { id: "bob_in", role: `Received Cipher Bit #${i}` };
      b1.add(n);
      b1.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0xf59e0b, 0.35);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set(1.0 + col * 1.5, (row - 3.5) * 0.9, 0);
      n.userData = { id: "bob_in", role: `Legitimate Shared Key Bit #${i}` };
      b1.add(n);
      b1.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    const fb1 = new THREE.Mesh(new THREE.BoxGeometry(9.5, 8.5, 1.2), frameMatBob.clone());
    fb1.userData = b1.userData;
    b1.add(fb1);
    b1.hitBox = fb1;

    bobGroup.add(b1);
    bobGroup.layerGroups.push(b1);

    // --- الطبقة 2: مصفوفة فك الخلط العكسية ---
    const b2 = new THREE.Group();
    b2.position.set(0, 0, -4);
    b2.userData = { id: "bob_fc", defaultZ: -4, explodedZ: -9 };
    b2.neurons = [];

    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 4; c++) {
        const n = createNeuronMesh(0x34d399, 0.32);
        n.position.set((c - 1.5) * 1.8, (r - 3.5) * 0.9, 0);
        n.userData = { id: "bob_fc", role: `Inverse Mixer Neuron [${r},${c}]` };
        b2.add(n);
        b2.neurons.push(n);
        allInteractiveNeurons.push(n);
      }
    }

    const fb2 = new THREE.Mesh(new THREE.BoxGeometry(9.0, 8.5, 1.2), frameMatBob.clone());
    fb2.userData = b2.userData;
    b2.add(fb2);
    b2.hitBox = fb2;

    bobGroup.add(b2);
    bobGroup.layerGroups.push(b2);

    // --- الطبقة 3: شبكة Inversion CNN وخلايا استعادة الرسالة ---
    const b3 = new THREE.Group();
    b3.position.set(0, 0, 1);
    b3.userData = { id: "bob_conv", defaultZ: 1, explodedZ: 2 };
    b3.neurons = [];

    // 16 Reconstructed Plaintext Neurons
    for (let i = 0; i < 16; i++) {
      const n = createNeuronMesh(0x10b981, 0.38);
      const col = i % 2;
      const row = Math.floor(i / 2);
      n.position.set((col - 0.5) * 2.2, (row - 3.5) * 0.95, 0);
      n.userData = { id: "bob_conv", role: `Decrypted Bit #${i}` };

      // تحديد الخلية رقم 6 كخلية خطأ تكميم أحادي أولي
      if (i === 6) {
        bobFaultyNeuron = n;
        n.material.color.setHex(0xf43f5e);
        n.material.emissive.setHex(0xf43f5e);
      }

      b3.add(n);
      b3.neurons.push(n);
      allInteractiveNeurons.push(n);
    }

    const fb3 = new THREE.Mesh(new THREE.BoxGeometry(7.5, 8.5, 1.2), frameMatBob.clone());
    fb3.userData = b3.userData;
    b3.add(fb3);
    b3.hitBox = fb3;

    bobGroup.add(b3);
    bobGroup.layerGroups.push(b3);

    // --- الطبقة 4: منشور التوفيق التشفيري (Hamming SEC Prism Crystal) ---
    const b4 = new THREE.Group();
    b4.position.set(0, 0, 7.5);
    b4.userData = { id: "bob_sec", defaultZ: 7.5, explodedZ: 16 };

    // المنشور البلوري المجسم متعدد الأوجه
    const prismGeo = new THREE.IcosahedronGeometry(2.1, 0);
    const prismMat = new THREE.MeshPhysicalMaterial({
      color: 0x10b981,
      emissive: 0x10b981,
      emissiveIntensity: 0.75,
      transmission: 0.92,
      roughness: 0.05,
      metalness: 0.1,
      ior: 2.1,
      transparent: true,
      opacity: 0.88
    });
    secCrystalPrism = new THREE.Mesh(prismGeo, prismMat);
    b4.add(secCrystalPrism);

    // حلقتين هولوغرافيتين نيون تدوران حول المنشور
    const ringGeo1 = new THREE.TorusGeometry(3.0, 0.1, 8, 32);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x34d399, wireframe: true });
    const pRing1 = new THREE.Mesh(ringGeo1, ringMat1);
    pRing1.rotation.x = Math.PI / 3;
    b4.add(pRing1);
    secPrismRings.push(pRing1);

    const ringGeo2 = new THREE.TorusGeometry(2.6, 0.08, 8, 32);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0xffd700 });
    const pRing2 = new THREE.Mesh(ringGeo2, ringMat2);
    pRing2.rotation.y = Math.PI / 4;
    b4.add(pRing2);
    secPrismRings.push(pRing2);

    // خطوط متلازمة التكافؤ الخمسة الداخلة للمنشور
    const parMat = new THREE.LineBasicMaterial({ color: 0x34d399, linewidth: 2 });
    const parCoords = [];
    for (let k = 0; k < 5; k++) {
      parCoords.push((k - 2) * 1.2, -4, -5, 0, 0, 0);
    }
    const parGeo = new THREE.BufferGeometry();
    parGeo.setAttribute("position", new THREE.Float32BufferAttribute(parCoords, 3));
    b4.add(new THREE.LineSegments(parGeo, parMat));

    // إطار تفاعلي للنقر
    const fb4 = new THREE.Mesh(new THREE.BoxGeometry(6.5, 6.5, 3.5), frameMatBob.clone());
    fb4.visible = false;
    fb4.userData = b4.userData;
    b4.add(fb4);
    b4.hitBox = fb4;

    bobGroup.add(b4);
    bobGroup.layerGroups.push(b4);

    scene.add(bobGroup);
  }

  // =========================================================================
  // 3. محطة إيف فائقة التفاصيل (DEEPEVE — 26,161 PARAMS)
  // =========================================================================
  function buildDetailedEveStation() {
    eveGroup = new THREE.Group();
    eveGroup.position.set(0, 8, -34);

    // منصة عريضة ذات طابع عدائي متوهج بالأحمر
    const baseGeo = new THREE.CylinderGeometry(14, 15.5, 1.4, 40);
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x24040c, metalness: 0.85, roughness: 0.25 });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5.5;
    eveGroup.add(base);

    const ring = new THREE.Mesh(new THREE.TorusGeometry(15.2, 0.24, 12, 48), new THREE.MeshBasicMaterial({ color: 0xf43f5e }));
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -4.7;
    eveGroup.add(ring);

    eveGroup.layerGroups = [];
    const frameMatEve = new THREE.MeshPhysicalMaterial({ color: 0x9f1239, transmission: 0.9, opacity: 0.2, transparent: true });

    // 4 طبقات تلافيفية عميقة هرمية متراكبة
    const eveLayersConfig = [
      { id: "eve_deep", z: -6, explodedZ: -16, countX: 5, countY: 4, size: [10, 8, 1.2] },
      { id: "eve_deep", z: -2, explodedZ: -5, countX: 4, countY: 4, size: [9.5, 7.5, 1.2] },
      { id: "eve_deep", z: 2, explodedZ: 5, countX: 4, countY: 4, size: [9.0, 7.0, 1.2] },
      { id: "eve_deep", z: 6, explodedZ: 16, countX: 3, countY: 4, size: [8.5, 6.5, 1.2] }
    ];

    eveLayersConfig.forEach((cfg, idx) => {
      const grp = new THREE.Group();
      grp.position.set(0, 0, cfg.z);
      grp.userData = { id: cfg.id, defaultZ: cfg.z, explodedZ: cfg.explodedZ };
      grp.neurons = [];

      for (let r = 0; r < cfg.countY; r++) {
        for (let c = 0; c < cfg.countX; c++) {
          const n = createNeuronMesh(0xf43f5e, 0.34);
          n.position.set((c - (cfg.countX - 1) / 2) * 1.8, (r - (cfg.countY - 1) / 2) * 1.3, 0);
          n.userData = { id: cfg.id, role: `Deep Eve Filter [Tier ${idx + 1}] (${r},${c})` };
          grp.add(n);
          grp.neurons.push(n);
          allInteractiveNeurons.push(n);
        }
      }

      const f = new THREE.Mesh(new THREE.BoxGeometry(cfg.size[0], cfg.size[1], cfg.size[2]), frameMatEve.clone());
      f.userData = grp.userData;
      grp.add(f);
      grp.hitBox = f;

      eveGroup.add(grp);
      eveGroup.layerGroups.push(grp);
    });

    // أنبوبين للوصلات المتبقية الشفافة (Dual Residual Skip Tubes)
    const curve1 = new THREE.CubicBezierCurve3(
      new THREE.Vector3(5.5, 0, -6),
      new THREE.Vector3(10.5, 4.0, -4),
      new THREE.Vector3(10.5, 4.0, 0),
      new THREE.Vector3(5.0, 0, 2)
    );
    const tube1 = new THREE.Mesh(new THREE.TubeGeometry(curve1, 28, 0.35, 8, false), new THREE.MeshBasicMaterial({ color: 0xfb7185, wireframe: true, transparent: true, opacity: 0.6 }));
    eveGroup.add(tube1);
    eveSkipTubes.push(tube1);

    const curve2 = new THREE.CubicBezierCurve3(
      new THREE.Vector3(-5.5, 0, -2),
      new THREE.Vector3(-10.5, 4.0, 0),
      new THREE.Vector3(-10.5, 4.0, 4),
      new THREE.Vector3(-4.8, 0, 6)
    );
    const tube2 = new THREE.Mesh(new THREE.TubeGeometry(curve2, 28, 0.35, 8, false), new THREE.MeshBasicMaterial({ color: 0xe11d48, wireframe: true, transparent: true, opacity: 0.6 }));
    eveGroup.add(tube2);
    eveSkipTubes.push(tube2);

    scene.add(eveGroup);
  }

  // =========================================================================
  // 4. القناة العامة المشوشة وتفريعة التنصت
  // =========================================================================
  function buildDetailedPublicChannel() {
    channelGroup = new THREE.Group();

    const p1 = new THREE.Vector3(-24, 0, 8);
    const pMid = new THREE.Vector3(0, -2, 10);
    const p2 = new THREE.Vector3(24, 0, -8);

    const mainCurve = new THREE.CatmullRomCurve3([p1, pMid, p2]);
    const mainGeo = new THREE.TubeGeometry(mainCurve, 50, 0.52, 16, false);
    const mainMat = new THREE.MeshStandardMaterial({
      color: 0x1e1b4b,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.7,
      metalness: 0.8,
      roughness: 0.15
    });
    const mainConduit = new THREE.Mesh(mainGeo, mainMat);
    channelGroup.add(mainConduit);

    const eveTap = new THREE.LineCurve3(pMid, new THREE.Vector3(0, 4, -28));
    const tapGeo = new THREE.TubeGeometry(eveTap, 24, 0.36, 12, false);
    const tapMat = new THREE.MeshStandardMaterial({
      color: 0x475569,
      emissive: 0xf43f5e,
      emissiveIntensity: 0.75
    });
    const tapConduit = new THREE.Mesh(tapGeo, tapMat);
    channelGroup.add(tapConduit);

    scene.add(channelGroup);
  }

  // =========================================================================
  // 5. ليزر هامنغ ثلاثي الأبعاد وموجات التوفيق الهولوغرافية
  // =========================================================================
  function buildHolographicLaserAndWave() {
    // أسطوانة الليزر المتصلة من منشور SEC إلى الخلية رقم 6
    const laserLength = 6.8;
    const laserGeo = new THREE.CylinderGeometry(0.18, 0.18, laserLength, 16);
    laserGeo.translate(0, laserLength / 2, 0);
    laserGeo.rotateX(Math.PI / 2);

    const laserMat = new THREE.MeshBasicMaterial({
      color: 0x34d399,
      transparent: true,
      opacity: 0.0
    });
    secLaserBeam = new THREE.Mesh(laserGeo, laserMat);
    secLaserBeam.position.set(32, 0, 1.0);
    secLaserBeam.visible = false;
    scene.add(secLaserBeam);

    // حلقة الصدمة الهولوغرافية المتوسعة (Wavefront Shockwave)
    const ringGeo = new THREE.RingGeometry(0.3, 0.75, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x34d399,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.0
    });
    secWavefront = new THREE.Mesh(ringGeo, ringMat);
    secWavefront.position.set(32, 0, 1.1);
    secWavefront.visible = false;
    scene.add(secWavefront);
  }

  // سحابة الضوضاء التشفيرية العشوائية لإيف
  function buildEveNoiseCloud() {
    const count = 90;
    const geo = new THREE.BufferGeometry();
    const positions = [];
    for (let i = 0; i < count; i++) {
      positions.push(
        (Math.random() - 0.5) * 18,
        8 + (Math.random() - 0.5) * 8,
        -34 + (Math.random() - 0.5) * 16
      );
    }
    geo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: 0xf43f5e,
      size: 0.8,
      transparent: true,
      opacity: 0.0
    });
    eveNoiseParticles = new THREE.Points(geo, mat);
    scene.add(eveNoiseParticles);
  }

  // إعداد حزم الجسيمات
  function setupParticleFlow() {
    const particleCount = 80;
    const geo = new THREE.SphereGeometry(0.48, 12, 12);

    for (let i = 0; i < particleCount; i++) {
      const mat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
      const p = new THREE.Mesh(geo, mat);
      p.visible = false;
      scene.add(p);
      particleSystems.push({
        mesh: p,
        offset: i / particleCount
      });
    }
  }

  function setupInteractionEvents() {
    container.addEventListener("mousedown", (e) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
    });

    container.addEventListener("mousemove", (e) => {
      if (isDragging) {
        const dx = e.clientX - prevMousePos.x;
        const dy = e.clientY - prevMousePos.y;
        sceneRotation.y += dx * 0.005;
        sceneRotation.x += dy * 0.005;
        sceneRotation.x = Math.max(-0.35, Math.min(0.9, sceneRotation.x));
        prevMousePos = { x: e.clientX, y: e.clientY };
      }
    });

    container.addEventListener("wheel", (e) => {
      e.preventDefault();
      targetCamPos.z += e.deltaY * 0.04;
      targetCamPos.z = Math.max(20, Math.min(105, targetCamPos.z));
    }, { passive: false });

    container.addEventListener("click", (e) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      // أولاً نفحص الخلايا العصبية الدقيقة
      const neuronHits = raycaster.intersectObjects(allInteractiveNeurons);
      if (neuronHits.length > 0) {
        const n = neuronHits[0].object;
        showLayerInspector(n.userData.id, n.userData.role);
        return;
      }

      // ثانياً نفحص إطارات الطبقات
      const allHitBoxes = [
        ...aliceGroup.layerGroups.map(g => g.hitBox),
        ...bobGroup.layerGroups.map(g => g.hitBox),
        ...eveGroup.layerGroups.map(g => g.hitBox)
      ];

      const intersects = raycaster.intersectObjects(allHitBoxes);
      if (intersects.length > 0) {
        const hit = intersects[0].object;
        showLayerInspector(hit.userData.id);
      }
    });
  }

  function showLayerInspector(layerId, customDetail = null) {
    const data = layerData[layerId];
    if (!data) return;

    const card = document.getElementById("layer-inspector");
    if (!card) return;

    document.getElementById("insp-title").textContent = data.title;
    document.getElementById("insp-shape").textContent = data.shape;
    document.getElementById("insp-params").textContent = data.params;
    document.getElementById("insp-func").textContent = data.func;
    document.getElementById("insp-role").textContent = customDetail ? `${data.role} — [تم تحديد: ${customDetail}]` : data.role;

    card.style.display = "block";
  }

  function setViewMode(mode) {
    currentMode = mode;
    const target = cameraPositions[mode] || cameraPositions.overview;
    targetCamPos = { ...target };

    const isAliceDissect = (mode === "alice");
    const isBobDissect = (mode === "bob");
    const isEveDissect = (mode === "eve");

    if (aliceGroup && aliceGroup.layerGroups) animateLayerGroups(aliceGroup.layerGroups, isAliceDissect);
    if (bobGroup && bobGroup.layerGroups) animateLayerGroups(bobGroup.layerGroups, isBobDissect);
    if (eveGroup && eveGroup.layerGroups) animateLayerGroups(eveGroup.layerGroups, isEveDissect);

    document.querySelectorAll(".btn-lab-mode").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById("btn-mode-" + mode);
    if (activeBtn) activeBtn.classList.add("active");
  }

  function animateLayerGroups(groups, isDissected) {
    groups.forEach((g) => {
      const targetZ = isDissected ? g.userData.explodedZ : g.userData.defaultZ;
      g.targetZ = targetZ;
    });
  }

  function jumpToMechanismStage(stage) {
    mechanismStage = stage;
    stageTimer = 0;

    document.querySelectorAll(".lab-stage-pill").forEach(p => p.classList.remove("active"));
    const activePill = document.getElementById(`lab-stage-${stage}`);
    if (activePill) activePill.classList.add("active");

    const camTarget = stageCameraPositions[stage] || stageCameraPositions[0];
    targetCamPos = { ...camTarget };

    updateMechanismBanner(stage);
    updateTelemetry(stage);
  }

  function stepMechanismStage() {
    const next = (mechanismStage + 1) % 6;
    jumpToMechanismStage(next);
  }

  function updateMechanismBanner(stage) {
    const textEl = document.getElementById("lab-banner-text");
    if (textEl && mechanismExplanations[stage]) {
      textEl.innerHTML = mechanismExplanations[stage];
    }
  }

  function updateTelemetry(stage) {
    const telAlice = document.getElementById("tel-alice-val");
    const telBob = document.getElementById("tel-bob-val");
    const telEve = document.getElementById("tel-eve-val");

    if (stage === 1) {
      if (telAlice) telAlice.textContent = "تشفير نشط (3,857 وزن)";
      if (telBob) telBob.textContent = "في انتظار الشفرة...";
      if (telEve) telEve.textContent = "ترقب القناة...";
    } else if (stage === 2) {
      if (telAlice) telAlice.textContent = "بث Float16 + Parity 5b";
      if (telBob) telBob.textContent = "استقبال الإشارة...";
      if (telEve) telEve.textContent = "اعتراض بدون مفتاح!";
    } else if (stage === 3) {
      if (telAlice) telAlice.textContent = "مكتمل";
      if (telBob) telBob.textContent = "فك تلافيفي (خطأ بت #6)";
      if (telEve) telEve.textContent = "محاولة استخراج الأنماط...";
    } else if (stage === 4) {
      if (telAlice) telAlice.textContent = "مكتمل";
      if (telBob) telBob.textContent = "100.00% SHA-256 MATCH ✓";
      if (telEve) telEve.textContent = "عجز تام...";
    } else if (stage === 5) {
      if (telAlice) telAlice.textContent = "مكتمل";
      if (telBob) telBob.textContent = "100.00% SHA-256 MATCH ✓";
      if (telEve) telEve.textContent = "BER = 45.40% (عجز شانون) ✗";
    } else {
      if (telAlice) telAlice.textContent = "Float16 + Parity";
      if (telBob) telBob.textContent = "100.00% SHA-256 ✓";
      if (telEve) telEve.textContent = "BER = 45.40% (عجز شانون)";
    }
  }

  function updateFloatingBadges() {
    if (!container || !camera) return;

    const badges = [
      { id: "badge-alice", pos: new THREE.Vector3(-32, 9.5, 0) },
      { id: "badge-bob", pos: new THREE.Vector3(32, 9.5, 0) },
      { id: "badge-eve", pos: new THREE.Vector3(0, 19, -34) },
      { id: "badge-channel", pos: new THREE.Vector3(0, 2.5, 10) }
    ];

    const rect = container.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;

    badges.forEach(b => {
      const el = document.getElementById(b.id);
      if (!el) return;

      const v = b.pos.clone().project(camera);
      if (v.z > 1.0) {
        el.style.display = "none";
        return;
      }

      el.style.display = "flex";
      const x = (v.x * 0.5 + 0.5) * rect.width;
      const y = (-(v.y * 0.5) + 0.5) * rect.height;
      el.style.transform = `translate(${x}px, ${y}px) translate(-50%, -100%)`;
    });
  }

  function animate() {
    animationFrameId = requestAnimationFrame(animate);

    // دوران الكاميرا التفاعلي
    scene.rotation.y += (sceneRotation.y - scene.rotation.y) * 0.08;
    scene.rotation.x += (sceneRotation.x - scene.rotation.x) * 0.08;

    // تتبع الكاميرا للهدف
    camera.position.x += (targetCamPos.x - camera.position.x) * 0.05;
    camera.position.y += (targetCamPos.y - camera.position.y) * 0.05;
    camera.position.z += (targetCamPos.z - camera.position.z) * 0.05;

    currentLookAt.x += (targetCamPos.tx - currentLookAt.x) * 0.05;
    currentLookAt.y += (targetCamPos.ty - currentLookAt.y) * 0.05;
    currentLookAt.z += (targetCamPos.tz - currentLookAt.z) * 0.05;
    camera.lookAt(currentLookAt.x, currentLookAt.y, currentLookAt.z);

    // تباعد الطبقات عند التشريح
    [aliceGroup, bobGroup, eveGroup].forEach(grp => {
      if (grp && grp.layerGroups) {
        grp.layerGroups.forEach(g => {
          if (g.targetZ !== undefined) {
            g.position.z += (g.targetZ - g.position.z) * 0.08;
          }
        });
      }
    });

    // 1. حركة إطار مسح التلافيف في أليس
    if (aliceScanBox) {
      aliceScanBox.position.y = Math.sin(Date.now() * 0.003 * simSpeed) * 2.2;
    }

    // 2. دوران منشور هامنغ البلوري وحلقاته
    if (secCrystalPrism) {
      const rotSpeed = (mechanismStage === 4 ? 0.05 : 0.015) * simSpeed;
      secCrystalPrism.rotation.y += rotSpeed;
      secCrystalPrism.rotation.x += rotSpeed * 0.5;
    }
    if (secPrismRings.length >= 2) {
      secPrismRings[0].rotation.z += 0.02 * simSpeed;
      secPrismRings[1].rotation.x += -0.025 * simSpeed;
    }

    // 3. محاكاة آلية الليزر الهولوغرافي وتصحيح البت في بوب
    const isLaserActive = (mechanismStage === 4) || (mechanismStage === 0 && (simProgress % 1.0) > 0.72 && (simProgress % 1.0) < 0.96);
    if (secLaserBeam) {
      secLaserBeam.visible = isLaserActive;
      if (isLaserActive) {
        secLaserBeam.material.opacity = 0.75 + Math.sin(Date.now() * 0.025) * 0.25;
      }
    }

    if (secWavefront) {
      secWavefront.visible = isLaserActive;
      if (isLaserActive) {
        const ringScale = 1.0 + (Date.now() * 0.006) % 3.2;
        secWavefront.scale.set(ringScale, ringScale, ringScale);
        secWavefront.material.opacity = Math.max(0, 1.0 - (ringScale - 1.0) / 3.2);
      }
    }

    // تصحيح الخلية #6 عند إطلاق الليزر
    if (bobFaultyNeuron) {
      if (isLaserActive) {
        bobFaultyNeuron.material.color.setHex(0x10b981);
        bobFaultyNeuron.material.emissive.setHex(0x34d399);
      } else if (mechanismStage === 3) {
        bobFaultyNeuron.material.color.setHex(0xf43f5e);
        bobFaultyNeuron.material.emissive.setHex(0xf43f5e);
      }
    }

    // 4. محاكاة ضوضاء إيف العشوائية
    const isEveBroken = (mechanismStage === 5) || (mechanismStage === 0 && (simProgress % 1.0) > 0.45 && (simProgress % 1.0) < 0.75);
    if (eveNoiseParticles) {
      eveNoiseParticles.material.opacity = isEveBroken ? 0.9 : 0.0;
      if (isEveBroken) {
        const posAttr = eveNoiseParticles.geometry.attributes.position;
        for (let i = 0; i < posAttr.count; i++) {
          posAttr.setX(i, (Math.random() - 0.5) * 18);
          posAttr.setY(i, 8 + (Math.random() - 0.5) * 8);
          posAttr.setZ(i, -34 + (Math.random() - 0.5) * 16);
        }
        posAttr.needsUpdate = true;
      }
    }

    // 5. محاكاة تدفق الجسيمات
    if (isSimulating) {
      simProgress += 0.007 * simSpeed;
      stageTimer += 0.015 * simSpeed;

      if (mechanismStage === 0) {
        updateSimulationParticlesContinuous();
      } else {
        updateSimulationParticlesStageSpecific(mechanismStage);
      }
    }

    // تحديث تموضع البادجات
    updateFloatingBadges();

    renderer.render(scene, camera);
  }

  function updateSimulationParticlesContinuous() {
    particleSystems.forEach((p, idx) => {
      const t = (simProgress + p.offset) % 1.0;
      p.mesh.visible = true;

      if (t < 0.35) {
        const alpha = t / 0.35;
        p.mesh.position.set(-32, 0, -8 + alpha * 16);
        p.mesh.material.color.setHex(0x06b6d4);
      } else if (t < 0.70) {
        const alpha = (t - 0.35) / 0.35;
        const x = -24 + alpha * 48;
        const z = 8 - alpha * 16;
        p.mesh.position.set(x, -1, z);
        p.mesh.material.color.setHex(0x8b5cf6);

        if (idx % 3 === 0) {
          p.mesh.position.set(x * 0.3, 4 + alpha * 4, -10 - alpha * 22);
          p.mesh.material.color.setHex(0xf43f5e);
        }
      } else {
        const alpha = (t - 0.70) / 0.30;
        p.mesh.position.set(32, 0, -8 + alpha * 16);
        p.mesh.material.color.setHex(0x10b981);
      }
    });
  }

  function updateSimulationParticlesStageSpecific(stg) {
    particleSystems.forEach((p, idx) => {
      const t = (simProgress * 1.5 + p.offset) % 1.0;
      p.mesh.visible = true;

      if (stg === 1) {
        const alpha = t;
        p.mesh.position.set(-32 + Math.sin(alpha * Math.PI * 4) * 1.2, 0, -8 + alpha * 16);
        p.mesh.material.color.setHex(0x06b6d4);
      } else if (stg === 2) {
        const alpha = t;
        const x = -24 + alpha * 48;
        const z = 8 - alpha * 16;
        if (idx % 2 === 0) {
          p.mesh.position.set(x, -1, z);
          p.mesh.material.color.setHex(0x38bdf8);
        } else {
          p.mesh.position.set(x * 0.25, 4 + alpha * 4, -8 - alpha * 24);
          p.mesh.material.color.setHex(0xf43f5e);
        }
      } else if (stg === 3) {
        const alpha = t;
        p.mesh.position.set(32, 0, -8 + alpha * 10);
        p.mesh.material.color.setHex(0x10b981);
      } else if (stg === 4) {
        const alpha = t;
        p.mesh.position.set(32 + (Math.random() - 0.5) * 1.5, 0, 1 + alpha * 6.5);
        p.mesh.material.color.setHex(0x34d399);
      } else if (stg === 5) {
        p.mesh.position.set((Math.random() - 0.5) * 14, 8 + (Math.random() - 0.5) * 6, -34 + (Math.random() - 0.5) * 14);
        p.mesh.material.color.setHex(0xf43f5e);
      }
    });
  }

  function toggleSimulation() {
    isSimulating = !isSimulating;
    const btn = document.getElementById("btn-lab-play");
    if (btn) btn.textContent = isSimulating ? "⏸" : "▶";
  }

  function resetSimulation() {
    jumpToMechanismStage(0);
    simProgress = 0;
    particleSystems.forEach(p => (p.mesh.visible = false));
  }

  function setSimSpeed(speed) {
    simSpeed = speed;
    document.querySelectorAll(".lab-speed-group .sim-speed-btn").forEach(b => b.classList.remove("active"));
    const id = (speed === 0.5) ? "lab-speed-05" : (speed === 2.0) ? "lab-speed-20" : "lab-speed-10";
    const btn = document.getElementById(id);
    if (btn) btn.classList.add("active");
  }

  function onWindowResize() {
    if (!container || !camera || !renderer) return;
    const width = container.clientWidth || 1100;
    const height = container.clientHeight || 600;
    if (width <= 0 || height <= 0) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  return {
    init,
    resize: onWindowResize,
    setViewMode,
    jumpToMechanismStage,
    stepMechanismStage,
    toggleSimulation,
    resetSimulation,
    setSimSpeed,
    showLayerInspector
  };
})();

// تصدير الكائن إلى النطاق العام
if (typeof window !== "undefined") {
  window.Neural3D = Neural3D;
}
