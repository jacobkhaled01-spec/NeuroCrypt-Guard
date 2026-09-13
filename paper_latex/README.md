# NeuroCrypt-Guard: Q1 Scientific Research Paper (LaTeX Package)
## الحزمة الأكاديمية للورقة البحثية المحكمة — المعايير الدولية Q1

تضم هذه الحزمة الورقة البحثية الأكاديمية المحكمة والمصاغة بلغة **LaTeX** وفق معايير وقوالب المجلات العلمية العالمية المصنفة في الربع الأول **(Q1)** مثل *IEEE Transactions on Information Forensics and Security*، *IEEE Access*، و *Elsevier Computers & Security*.

---

## 📁 محتويات الحزمة (Package Structure)

```
paper_latex/
├── neurocrypt_guard_paper.tex   ← الملف المصدري الرئيسي للورقة البحثية (IEEEtran)
├── IEEEtran.cls                 ← ملف الفئة المعيارية الرسمي من CTAN (مضمن ذاتياً 100%)
├── references.bib               ← قاعدة بيانات المراجع الكاملة (25 مرجعاً بنمط IEEE / APA 7)
├── figures/                     ← الرسوم والمخططات البيانية المستخرجة من الفحوصات الفعلية
│   ├── training_curves.png      ← منحنيات التدريب وفجوة السرية (Secrecy Gap)
│   ├── sac_heatmap.png          ← مصفوفة تأثير الانهيار الصارم (SAC Matrix = 0.4980)
│   ├── fault_injection_curve.png← منحنى الصمود التشفيري أمام حقن الأخطاء
│   └── aes_comparison_bar.png   ← المقارنة المعيارية للأداء والكمون مع AES-128
└── README.md                    ← هذا الدليل التوثيقي الشامل
```

---

## 🏛️ بيانات الورقة البحثية (Research Paper Metadata)

- **عنوان البحث بالإنجليزية (Primary Q1 Title):**
  **NeuroCrypt-Guard: Adversarial Neural Cryptography with Operational Information Reconciliation and Bit-Exact Integrity**
- **عنوان البحث بالعربية:**
  **منظومة التشفير العصبي التنافسي الموجه بحماية وسرية وتوفيق البيانات الرقمية**
- **فريق الباحثين (Authors):**
  - **يعقوب خالد المهاجري (Yaaqoub K. Al-Mohajeri)**
  - **سليمان صالح العربي (Sulaiman S. Al-Arabi)**
  - **مالك عادل جبران (Malek A. Jubran)**
- **تحت إشراف (Advisors):**
  - **أ.د. فضل باعلوي (Prof. Dr. Fadhl Ba-Alwi)** — Senior Member, IEEE
  - **د. هائل العبسي (Dr. Hael Al-Absi)**
- **الانتماء المؤسسي (Affiliation):**
  - Department of Computer Science and Information Technology, Faculty of Computer and Information Technology, Ibb University, Ibb, Yemen.

---

## 🔬 المحاور العلمية للورقة (Paper Outline)

1. **Section I: Introduction**
   - The convergence of representation learning and discrete cryptography.
   - The determinism-approximation paradox in continuous neural networks ($\mathbb{R}^n \to \mathbb{R}^m$).
   - The Google Brain (Abadi & Andersen, 2016) operational gap and bit corruption.
   - Five novel contributions elevating this work to Q1 standards.

2. **Section II: Theoretical Foundations & Related Work**
   - Shannon's perfect secrecy: mutual information $I(P; C) = 0$ and $BER_{\text{Eve}} = 50.00\%$.
   - Kerckhoffs's principle: zero security through obscurity.
   - Information reconciliation and syndromic error-correcting codes.

3. **Section III: Proposed NeuroCrypt-Guard Architecture**
   - AliceNet: Linear Confusion Mixer ($32\times32$) and 3-stage Conv1D Diffusion Filters.
   - BobNet: Inversion CNN and symmetrical shared key injection.
   - **Hamming SEC Reconciliation Layer:** Generator matrix $G$, Parity-check matrix $H_{5\times16}$, syndrome formula $S = (H \cdot \hat{b}) \oplus V_{\text{par}}$, and mathematical proof of 100.00% deterministic recovery.
   - **Bounded Quadratic Competitive Loss:** Mathematical derivation of $\mathcal{L}_{AB}$ preventing inverse secrecy.
   - Minimax optimization algorithm ($k_{\text{Eve}}=2$).

4. **Section IV: Multi-Tier Cryptanalytic Adversary Spectrum**
   - Threat model: Chosen Plaintext (CPA) and Known Plaintext (KPA).
   - Tier 1: Standard Eve ($3,857$ weights).
   - Tier 2: Wide Eve ($7,714$ weights).
   - Tier 3: Deep Residual EveNet ($26,161$ weights, 4 layers, 64 channels, skip connections, $2\times$ training step advantage).

5. **Section V: Experimental Methodology**
   - Dynamic CSPRNG data synthesis (`os.urandom`).
   - PyTorch 2.1 CUDA 12.1 acceleration.
   - Operational chunked streaming CLI engine (`cipher_tool.py`).

6. **Section VI: Empirical Results & Security Analysis**
   - Convergence trajectory and empirical secrecy gap ($45.40\%$).
   - Table of 100.00% bit-exact recovery with identical $\text{SHA-256}$ verification across TXT, PDF, PNG, MP4, and EXE payloads.
   - Strict Avalanche Criterion: empirical $16\times16$ matrix with mean $0.4980 \approx 0.5000$.
   - Full NIST SP 800-22 Rev 1a suite: Monobit, Block Frequency, Runs, Longest Run, Rank, FFT, Approx Entropy, Cumulative Sums ($p > 0.01$).
   - Cryptanalytic failure of Deep Eve ($BER = 45.40\%$).
   - Hardware fault injection sensitivity curve.
   - Computational latency ($0.80\text{ ms}$) and throughput benchmarks vs. hardware AES-128.

7. **Section VII: Discussion & Implications**
   - Resolution of the continuous-discrete cryptographic paradox.
   - Immunity to differential cryptanalysis ($\Delta C \approx \mathcal{U}(\{0, 1\}^N)$).
   - Post-quantum readiness and Edge NPU hardware execution without discrete co-processors.

8. **Section VIII: Conclusion & Acknowledgments**

---

## ⚡ طرق تجميع الورقة إلى ملف PDF (Compilation Instructions)

### الطريقة 1: الرفع المباشر إلى منصة Overleaf (موصى بها فورياً)
1. قم بضغط مجلد `paper_latex` كملف ZIP.
2. ادخل إلى [Overleaf](https://www.overleaf.com) واضغط **New Project &rarr; Upload Project**.
3. اختر ملف ZIP؛ سيقوم Overleaf بتجميع ملف PDF مباشرة وإظهار الورقة بكامل أناقتها وتنسيقها ثنائي الأعمدة (Two-Column IEEE).

### الطريقة 2: التجميع المحلي باستخدام TeX Live / MiKTeX
في حال كان محرك LaTeX مثبتاً على جهازك، نفذ الأوامر التالية:
```bash
cd paper_latex
pdflatex neurocrypt_guard_paper.tex
bibtex neurocrypt_guard_paper
pdflatex neurocrypt_guard_paper.tex
pdflatex neurocrypt_guard_paper.tex
```
سيتم توليد الملف النهائي `neurocrypt_guard_paper.pdf`.
