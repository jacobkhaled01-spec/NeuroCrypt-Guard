/**
 * neural3d.js (Holographic Edition)
 * محرك العرض ثلاثي الأبعاد الهولوغرافي مع خلايا وألياف عصبية مضيئة بدلاً من الأشكال الصماء
 * Holographic 3D Neural Architecture Workstation, Layer Dissection & Volumetric Simulation
 * NeuroCrypt-Guard v2.2
 */

const Neural3D = (function () {
  let scene, camera, renderer, container;
  let animationFrameId = null;
  let isSimulating = false;
  let simSpeed = 1.0;
  let simProgress = 0.0;
  let currentMode = "overview";

  let aliceGroup, bobGroup, eveGroup, channelGroup;
  let particleSystems = [];
  let raycaster, mouse;
  let holographicLaser = null;

  // تعريف طبقات الشبكات للمفتش
  const layerData = {
    alice_in: {
      title: "أليس: طبقة الإدخال الموحد (Input Layer)",
      shape: "Tensor [Batch, 32]",
      params: "0 (دخول مباشر)",
      func: "Concat(Plaintext [16], Key [16])",
      role: "دمج النص الصريح مع المفتاح السري المشترك كمتجه أولي"
    },
    alice_fc: {
      title: "أليس: طبقة الخلط الخطي (FC Mixer)",
      shape: "Linear: 32 → 32",
      params: "1,056 وزن وتحيز",
      func: "LeakyReLU(α = 0.2)",
      role: "خلط البتات لتحقيق خاصية الارتباك (Confusion)"
    },
    alice_c1: {
      title: "أليس: الطبقة التلافيفية الأولى (Conv1D-1)",
      shape: "Conv1D: 1 → 32 قنوات, Kernel = 4",
      params: "160 وزن",
      func: "LeakyReLU(α = 0.2) + Same Padding",
      role: "توسيع الفضاء التشفيري ونشر التأثير على كتل مجاورة (Diffusion)"
    },
    alice_c2: {
      title: "أليس: الطبقة التلافيفية الثانية (Conv1D-2)",
      shape: "Conv1D: 32 → 16 قنوات, Kernel = 2",
      params: "1,040 وزن",
      func: "LeakyReLU(α = 0.2) + Same Padding",
      role: "تركيب علاقات غير خطية عميقة لتشتيت الأنماط الإحصائية"
    },
    alice_c3: {
      title: "أليس: طبقة الخرج التشفيري (Conv1D-3 + Tanh)",
      shape: "Conv1D: 16 → 1 قنوات, Kernel = 1",
      params: "17 وزن",
      func: "Tanh ([-1.0, 1.0]) → Float16",
      role: "توليد النص المشفر النصفي + حساب متلازمة هامنغ (5-bit SEC)"
    },
    bob_in: {
      title: "بوب: طبقة الاستقبال الشرعية (Bob Input)",
      shape: "Tensor [Batch, 32]",
      params: "0",
      func: "Concat(Ciphertext [16], Shared Key [16])",
      role: "تغذية النص المشفر المعترض مع المفتاح السري الموثوق"
    },
    bob_fc: {
      title: "بوب: طبقة فك الخلط (Inverse Mixer)",
      shape: "Linear: 32 → 32",
      params: "1,056 وزن",
      func: "LeakyReLU(α = 0.2)",
      role: "معالجة مشتركة لعزل التشفير بالاعتماد على المفتاح"
    },
    bob_conv: {
      title: "بوب: الطبقات التلافيفية العكسية (Inversion CNN)",
      shape: "3x Conv1D Blocks (32 → 16 → 1)",
      params: "1,217 وزن",
      func: "LeakyReLU + Tanh",
      role: "إعادة بناء الرسالة بدقة تناظرية عالية (BER ≈ 0.07%)"
    },
    bob_sec: {
      title: "بوب: منشور التوفيق التشفيري (Hamming SEC Prism)",
      shape: "Parity Check Matrix H (5 × 16)",
      params: "خوارزمية تصحيح حتمية بدون أوزان",
      func: "Syndrome S = (H · P^T) ⊕ Parity",
      role: "تصحيح الخطأ التناظري المفرد فورياً وتحقيق تطابق 100% لبصمة SHA-256"
    },
    eve_deep: {
      title: "إيف: شبكة الخصم العميقة (Deep Residual EveNet)",
      shape: "4x Conv1D (64 قنوات) + Residual Skips",
      params: "26,161 وزناً (أكثر من 4 أضعاف أليس)",
      func: "LeakyReLU + Skip Connections",
      role: "محاولة كسر التشفير بدون مفتاح، وتفشل بحاجز شانون (BER ≈ 40.7% - 50%)"
    }
  };

  const cameraPositions = {
    overview: { x: 0, y: 36, z: 66, tx: 0, ty: 0, tz: 0 },
    alice: { x: -30, y: 10, z: 30, tx: -30, ty: 0, tz: 0 },
    bob: { x: 30, y: 10, z: 30, tx: 30, ty: 0, tz: 0 },
    eve: { x: 0, y: 20, z: -8, tx: 0, ty: 6, tz: -30 }
  };

  let targetCamPos = { ...cameraPositions.overview };
  let currentLookAt = { x: 0, y: 0, z: 0 };

  let isDragging = false;
  let prevMousePos = { x: 0, y: 0 };
  let sceneRotation = { x: 0.25, y: 0 };

  function init(containerElement) {
    container = containerElement;
    if (!container || !window.THREE) return;

    const width = (container.clientWidth > 100) ? container.clientWidth : (window.innerWidth > 500 ? window.innerWidth - 180 : 1100);
    const height = (container.clientHeight > 100) ? container.clientHeight : 440;

    // 1. Scene & Camera
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x070a13, 0.007);

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(targetCamPos.x, targetCamPos.y, targetCamPos.z);

    // 2. Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = "";
    container.appendChild(renderer.domElement);

    // 3. Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambient);

    const lightAlice = new THREE.PointLight(0x06b6d4, 3.5, 90);
    lightAlice.position.set(-30, 25, 20);
    scene.add(lightAlice);

    const lightBob = new THREE.PointLight(0x10b981, 3.5, 90);
    lightBob.position.set(30, 25, 20);
    scene.add(lightBob);

    const lightEve = new THREE.PointLight(0xf43f5e, 4.0, 90);
    lightEve.position.set(0, 30, -32);
    scene.add(lightEve);

    // 4. Cyber Ground Grid
    const grid = new THREE.GridHelper(130, 42, 0x1e293b, 0x0f172a);
    grid.position.y = -6;
    scene.add(grid);

    // 5. Build Holographic Stations with Internal Neural Clusters
    buildHolographicAlice();
    buildHolographicBob();
    buildHolographicEve();
    buildPublicChannel();
    setupParticleFlow();

    // 6. Raycasting & Events
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    setupInteractionEvents();
    window.addEventListener("resize", onWindowResize);

    // 7. Loop
    animate();
  }

  // دالة مساعدة لإنشاء طبقة هولوغرافية شفافة بداخلها خلايا عصبية مضيئة
  function createHolographicLayer(id, name, color, size, z, neuronCount = 14) {
    const group = new THREE.Group();
    group.position.set(0, 0, z);
    group.userData = { id, name, defaultZ: z, explodedZ: z * 2.4 };

    // 1. الإطار الزجاجي الهولوغرافي الشفاف
    const boxGeo = new THREE.BoxGeometry(size[0], size[1], size[2]);
    const boxMat = new THREE.MeshPhysicalMaterial({
      color: color,
      transmission: 0.85,
      opacity: 0.35,
      transparent: true,
      roughness: 0.1,
      metalness: 0.1,
      ior: 1.5,
      thickness: 0.5
    });
    const frame = new THREE.Mesh(boxGeo, boxMat);
    group.add(frame);

    // 2. حواف سلكية مضيئة (Wireframe Edges)
    const wireGeo = new THREE.EdgesGeometry(boxGeo);
    const wireMat = new THREE.LineBasicMaterial({ color: color, linewidth: 2 });
    const wire = new THREE.LineSegments(wireGeo, wireMat);
    group.add(wire);

    // 3. سحابة خلايا عصبية مضيئة حقيقية داخل الطبقة (Neural Point Cluster)
    const pointsGeo = new THREE.BufferGeometry();
    const positions = [];
    for (let i = 0; i < neuronCount; i++) {
      const px = (Math.random() - 0.5) * (size[0] * 0.75);
      const py = (Math.random() - 0.5) * (size[1] * 0.7);
      const pz = (Math.random() - 0.5) * (size[2] * 0.7);
      positions.push(px, py, pz);
    }
    pointsGeo.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    const pointsMat = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.6,
      transparent: true,
      opacity: 0.95
    });
    const points = new THREE.Points(pointsGeo, pointsMat);
    group.add(points);

    // ربط النقاط بأسلاك سينابس داخلية دقيقة
    const innerLinesMat = new THREE.LineBasicMaterial({ color: color, transparent: true, opacity: 0.3 });
    const innerLinesGeo = new THREE.BufferGeometry();
    const lineCoords = [];
    for (let i = 0; i < neuronCount - 1; i++) {
      lineCoords.push(
        positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2],
        positions[(i + 1) * 3], positions[(i + 1) * 3 + 1], positions[(i + 1) * 3 + 2]
      );
    }
    innerLinesGeo.setAttribute("position", new THREE.Float32BufferAttribute(lineCoords, 3));
    const innerLines = new THREE.LineSegments(innerLinesGeo, innerLinesMat);
    group.add(innerLines);

    // تخزين المرجع للنقر والتشريح
    group.hitBox = frame;
    frame.userData = group.userData;

    return group;
  }

  // بناء محطة أليس الهولوغرافية
  function buildHolographicAlice() {
    aliceGroup = new THREE.Group();
    aliceGroup.position.set(-30, 0, 0);

    // منصة دائرية مفرغة متوهجة
    const baseGeo = new THREE.CylinderGeometry(11, 12, 0.8, 32);
    const baseMat = new THREE.MeshStandardMaterial({
      color: 0x031828,
      metalness: 0.8,
      roughness: 0.2
    });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5;
    aliceGroup.add(base);

    // حلقتين نيون
    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(12, 0.2, 8, 32),
      new THREE.MeshBasicMaterial({ color: 0x06b6d4 })
    );
    ring1.rotation.x = Math.PI / 2;
    ring1.position.y = -4.5;
    aliceGroup.add(ring1);

    // الطبقات الهولوغرافية الخمس
    const layers = [
      { id: "alice_in", name: "Input Layer (32-dim)", color: 0x0284c7, size: [9, 1.4, 3], z: -8, count: 18 },
      { id: "alice_fc", name: "FC Mixer (32x32)", color: 0x0369a1, size: [8.5, 1.6, 3], z: -4, count: 16 },
      { id: "alice_c1", name: "Conv1D-1 (k=4)", color: 0x0284c7, size: [8, 1.8, 3], z: 0, count: 14 },
      { id: "alice_c2", name: "Conv1D-2 (k=2)", color: 0x0ea5e9, size: [7.5, 2.0, 3], z: 4, count: 12 },
      { id: "alice_c3", name: "Output Float16", color: 0x38bdf8, size: [7, 2.2, 3], z: 8, count: 10 }
    ];

    aliceGroup.layerGroups = [];
    layers.forEach(l => {
      const layerGrp = createHolographicLayer(l.id, l.name, l.color, l.size, l.z, l.count);
      aliceGroup.add(layerGrp);
      aliceGroup.layerGroups.push(layerGrp);
    });

    scene.add(aliceGroup);
  }

  // بناء محطة بوب الهولوغرافية
  function buildHolographicBob() {
    bobGroup = new THREE.Group();
    bobGroup.position.set(30, 0, 0);

    const baseGeo = new THREE.CylinderGeometry(11, 12, 0.8, 32);
    const baseMat = new THREE.MeshStandardMaterial({
      color: 0x022416,
      metalness: 0.8,
      roughness: 0.2
    });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5;
    bobGroup.add(base);

    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(12, 0.2, 8, 32),
      new THREE.MeshBasicMaterial({ color: 0x10b981 })
    );
    ring1.rotation.x = Math.PI / 2;
    ring1.position.y = -4.5;
    bobGroup.add(ring1);

    const layers = [
      { id: "bob_in", name: "Cipher In + Key", color: 0x047857, size: [9, 1.4, 3], z: -8, count: 16 },
      { id: "bob_fc", name: "Inverse Mixer", color: 0x059669, size: [8.5, 1.6, 3], z: -4, count: 14 },
      { id: "bob_conv", name: "Inversion CNN", color: 0x10b981, size: [8, 1.8, 3], z: 1, count: 12 },
      { id: "bob_sec", name: "Hamming SEC Prism", color: 0x34d399, size: [6.5, 2.4, 3.5], z: 7, count: 8 }
    ];

    bobGroup.layerGroups = [];
    layers.forEach(l => {
      const layerGrp = createHolographicLayer(l.id, l.name, l.color, l.size, l.z, l.count);
      bobGroup.add(layerGrp);
      bobGroup.layerGroups.push(layerGrp);
    });

    scene.add(bobGroup);
  }

  // بناء محطة إيف الهولوغرافية
  function buildHolographicEve() {
    eveGroup = new THREE.Group();
    eveGroup.position.set(0, 8, -32);

    const baseGeo = new THREE.CylinderGeometry(13, 14, 0.8, 32);
    const baseMat = new THREE.MeshStandardMaterial({
      color: 0x2e0611,
      metalness: 0.8,
      roughness: 0.2
    });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -5;
    eveGroup.add(base);

    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(14, 0.25, 8, 32),
      new THREE.MeshBasicMaterial({ color: 0xf43f5e })
    );
    ring1.rotation.x = Math.PI / 2;
    ring1.position.y = -4.5;
    eveGroup.add(ring1);

    const layers = [
      { id: "eve_deep", name: "Deep Conv1", color: 0x9f1239, size: [10, 1.4, 3], z: -6, count: 18 },
      { id: "eve_deep", name: "Residual Block 1", color: 0xbe123c, size: [9.5, 1.6, 3], z: -2, count: 16 },
      { id: "eve_deep", name: "Residual Block 2", color: 0xe11d48, size: [9, 1.8, 3], z: 2, count: 14 },
      { id: "eve_deep", name: "Adversarial Out", color: 0xf43f5e, size: [8.5, 2.0, 3], z: 6, count: 12 }
    ];

    eveGroup.layerGroups = [];
    layers.forEach(l => {
      const layerGrp = createHolographicLayer(l.id, l.name, l.color, l.size, l.z, l.count);
      eveGroup.add(layerGrp);
      eveGroup.layerGroups.push(layerGrp);
    });

    // أنبوب الوصلات المتبقية الشفاف المضيء (Skip Connection Tube)
    const curve = new THREE.CubicBezierCurve3(
      new THREE.Vector3(5.5, 0, -6),
      new THREE.Vector3(9.5, 3.5, -4),
      new THREE.Vector3(9.5, 3.5, 0),
      new THREE.Vector3(5.0, 0, 2)
    );
    const tubeGeo = new THREE.TubeGeometry(curve, 24, 0.35, 8, false);
    const tubeMat = new THREE.MeshBasicMaterial({ color: 0xfb7185, wireframe: true, transparent: true, opacity: 0.6 });
    const skipTube = new THREE.Mesh(tubeGeo, tubeMat);
    eveGroup.add(skipTube);

    scene.add(eveGroup);
  }

  // بناء القناة العامة
  function buildPublicChannel() {
    channelGroup = new THREE.Group();

    const p1 = new THREE.Vector3(-24, 0, 8);
    const pMid = new THREE.Vector3(0, -2, 10);
    const p2 = new THREE.Vector3(24, 0, -8);

    const mainCurve = new THREE.CatmullRomCurve3([p1, pMid, p2]);
    const mainGeo = new THREE.TubeGeometry(mainCurve, 40, 0.45, 12, false);
    const mainMat = new THREE.MeshStandardMaterial({
      color: 0x1e1b4b,
      emissive: 0x38bdf8,
      emissiveIntensity: 0.6,
      metalness: 0.7,
      roughness: 0.2
    });
    const mainConduit = new THREE.Mesh(mainGeo, mainMat);
    channelGroup.add(mainConduit);

    const eveTap = new THREE.LineCurve3(pMid, new THREE.Vector3(0, 4, -26));
    const tapGeo = new THREE.TubeGeometry(eveTap, 20, 0.3, 8, false);
    const tapMat = new THREE.MeshStandardMaterial({
      color: 0x475569,
      emissive: 0xf43f5e,
      emissiveIntensity: 0.6
    });
    const tapConduit = new THREE.Mesh(tapGeo, tapMat);
    channelGroup.add(tapConduit);

    scene.add(channelGroup);
  }

  // إعداد حزم الجسيمات
  function setupParticleFlow() {
    const particleCount = 70;
    const geo = new THREE.SphereGeometry(0.5, 12, 12);

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
        sceneRotation.x = Math.max(-0.3, Math.min(0.9, sceneRotation.x));
        prevMousePos = { x: e.clientX, y: e.clientY };
      }
    });

    container.addEventListener("wheel", (e) => {
      e.preventDefault();
      targetCamPos.z += e.deltaY * 0.04;
      targetCamPos.z = Math.max(20, Math.min(100, targetCamPos.z));
    }, { passive: false });

    container.addEventListener("click", (e) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
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

  function showLayerInspector(layerId) {
    const data = layerData[layerId];
    if (!data) return;

    const card = document.getElementById("layer-inspector");
    if (!card) return;

    document.getElementById("insp-title").textContent = data.title;
    document.getElementById("insp-shape").textContent = data.shape;
    document.getElementById("insp-params").textContent = data.params;
    document.getElementById("insp-func").textContent = data.func;
    document.getElementById("insp-role").textContent = data.role;

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

    document.querySelectorAll(".btn-mode, .btn-lab-mode").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById("btn-mode-" + mode);
    if (activeBtn) activeBtn.classList.add("active");
  }

  function animateLayerGroups(groups, isDissected) {
    groups.forEach((g) => {
      const targetZ = isDissected ? g.userData.explodedZ : g.userData.defaultZ;
      g.targetZ = targetZ;
    });
  }

  function animate() {
    animationFrameId = requestAnimationFrame(animate);

    scene.rotation.y += (sceneRotation.y - scene.rotation.y) * 0.08;
    scene.rotation.x += (sceneRotation.x - scene.rotation.x) * 0.08;

    camera.position.x += (targetCamPos.x - camera.position.x) * 0.05;
    camera.position.y += (targetCamPos.y - camera.position.y) * 0.05;
    camera.position.z += (targetCamPos.z - camera.position.z) * 0.05;

    currentLookAt.x += (targetCamPos.tx - currentLookAt.x) * 0.05;
    currentLookAt.y += (targetCamPos.ty - currentLookAt.y) * 0.05;
    currentLookAt.z += (targetCamPos.tz - currentLookAt.z) * 0.05;
    camera.lookAt(currentLookAt.x, currentLookAt.y, currentLookAt.z);

    // تباعد الطبقات
    [aliceGroup, bobGroup, eveGroup].forEach(grp => {
      if (grp && grp.layerGroups) {
        grp.layerGroups.forEach(g => {
          if (g.targetZ !== undefined) {
            g.position.z += (g.targetZ - g.position.z) * 0.08;
          }
        });
      }
    });

    // دوران منشور هامنغ
    const secPrismGroup = bobGroup.layerGroups.find(g => g.userData.id === "bob_sec");
    if (secPrismGroup) {
      secPrismGroup.rotation.y += 0.015;
    }

    // محاكاة تدفق الجسيمات
    if (isSimulating) {
      simProgress += 0.007 * simSpeed;
      updateSimulationParticles();
    }

    renderer.render(scene, camera);
  }

  function updateSimulationParticles() {
    particleSystems.forEach((p, idx) => {
      const t = (simProgress + p.offset) % 1.0;
      p.mesh.visible = true;

      if (t < 0.35) {
        const alpha = t / 0.35;
        p.mesh.position.set(-30, 0, -8 + alpha * 16);
        p.mesh.material.color.setHex(0x06b6d4); // سيان
      } else if (t < 0.70) {
        const alpha = (t - 0.35) / 0.35;
        const x = -24 + alpha * 48;
        const z = 8 - alpha * 16;
        p.mesh.position.set(x, -1, z);
        p.mesh.material.color.setHex(0x8b5cf6); // بنفسجي

        if (idx % 3 === 0) {
          p.mesh.position.set(x * 0.3, 4 + alpha * 4, -10 - alpha * 20);
          p.mesh.material.color.setHex(0xf43f5e); // قرمزي
        }
      } else {
        const alpha = (t - 0.70) / 0.30;
        p.mesh.position.set(30, 0, -8 + alpha * 16);
        p.mesh.material.color.setHex(0x10b981); // أخضر زمردي
      }
    });
  }

  function toggleSimulation() {
    isSimulating = !isSimulating;
    const btn = document.getElementById("btn-sim-play");
    if (btn) btn.textContent = isSimulating ? "⏸" : "▶";
  }

  function resetSimulation() {
    simProgress = 0;
    particleSystems.forEach(p => (p.mesh.visible = false));
  }

  function setSimSpeed(speed) {
    simSpeed = speed;
  }

  function onWindowResize() {
    if (!container || !camera || !renderer) return;
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || (window.innerHeight - 64);
    if (width <= 0 || height <= 0) return;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  return {
    init,
    resize: onWindowResize,
    setViewMode,
    toggleSimulation,
    resetSimulation,
    setSimSpeed,
    showLayerInspector
  };
})();

// تصدير الكائن إلى النطاق العام لضمان الوصول من كافة السلايدات والأزرار
if (typeof window !== "undefined") {
  window.Neural3D = Neural3D;
}
