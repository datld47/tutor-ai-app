const app = {
    config: {
        chapters: [
            {
                name: "CHƯƠNG I: TỔNG QUAN VỀ THƯƠNG MẠI ĐIỆN TỬ",
                modules: [
                    { name: "Tiết 1: Khái niệm và Tiếp cận", file: "DB/TMDT_Chuong1/Chương_1_Tiết 1_Khái niệm và Tiếp cận.csv?v=1", video: "Video/Chuong_1_Tiet_1/index.html" },
                    { name: "Tiết 2: Phân loại, Lợi ích và Hạn chế", file: "DB/TMDT_Chuong1/Chương_1_Tiết 2 Phân loại, Lợi ích và Hạn chế.csv?v=1", video: "Video/Chuong_1_Tiet_2/index.html" },
                    { name: "Tiết 3: Sự phát triển và Đánh giá", file: "DB/TMDT_Chuong1/Chương_1_Tiết 3 Sự phát triển và Đánh giá.csv?v=1", video: "Video/Chuong_1_Tiet_3/index.html" },
                    { name: "Tiết 4: Hạ tầng Pháp lý và Công nghệ", file: "DB/TMDT_Chuong1/Chương_1_Tiết 4 Hạ tầng Pháp lý và Công nghệ.csv?v=1", video: "Video/Chuong_1_Tiet_4/index.html" },
                    { name: "Tiết 5: Hạ tầng Thanh toán và Bảo mật", file: "DB/TMDT_Chuong1/Chương_1_Tiết 5 Hạ tầng Thanh toán và An toàn thông tin.csv?v=1", video: "Video/Chuong_1_Tiet_5/index.html" },
                    { name: "Tiết 6: Hạ tầng Nhân lực & Phân phối", file: "DB/TMDT_Chuong1/Chương_1_Tiết 6 Hạ tầng Nhân lực, Phân phối & Bài tập.csv?v=1", video: "Video/Chuong_1_Tiet_6/index.html" },
                    { name: "Tiết 7: Mô hình B2C và B2B", file: "DB/TMDT_Chuong1/Chương_1_Tiết 7 Mô hình B2C và B2B.csv?v=1", video: "Video/Chuong_1_Tiet_7/index.html" },
                    { name: "Tiết 8: Mô hình C2C và C2B", file: "DB/TMDT_Chuong1/Chương_1_Tiết 8 Mô hình C2C và C2B.csv?v=1", video: "Video/Chuong_1_Tiet_8/index.html" },
                    { name: "Tiết 9: Phân tích Mô hình & Đánh giá", file: "DB/TMDT_Chuong1/Chương_1_Tiết 9 Phân tích Mô hình & Đánh giá.csv?v=1", video: "Video/Chuong_1_Tiet_9/index.html" },
                    { name: "Tiết 10: Tổng quan về Sàn Giao dịch", file: "DB/TMDT_Chuong1/Chương_1_Tiết 10 Tổng quan về Sàn Giao dịch.csv?v=1", video: "Video/Chuong_1_Tiet_10/index.html" },
                    { name: "Tiết 11: Lợi ích và Phương thức GD", file: "DB/TMDT_Chuong1/Chương_1_Tiết 11 Lợi ích và Phương thức giao dịch.csv?v=1", video: "Video/Chuong_1_Tiet_11/index.html" },
                    { name: "Tiết 12: Thực hành và Làm việc nhóm", file: "DB/TMDT_Chuong1/Chương_1_Tiết 12 Thực hành và Làm việc nhóm.csv?v=1", video: "Video/Chuong_1_Tiet_12/index.html" }
                ]
            },
            {
                name: "CHƯƠNG II: GIAO DỊCH ĐIỆN TỬ",
                modules: []
            },
            {
                name: "CHƯƠNG III: MARKETING ĐIỆN TỬ",
                modules: []
            },
            {
                name: "CHƯƠNG IV: AN TOÀN THÔNG TIN TRONG THƯƠNG MẠI ĐIỆN TỬ",
                modules: []
            },
            {
                name: "CHƯƠNG V: ỨNG DỤNG THƯƠNG MẠI ĐIỆN TỬ TRONG DOANH NGHIỆP",
                modules: []
            }
        ]
    },
    state: {
        currentChapter: null, // Index of current chapter
        currentModule: null, // Module object
        allQuestions: [],
        parts: [],
        currentPart: null,
        quizQuestions: [],
        currentQuestionIndex: 0,
        userResults: {}
    },

    // Map of Chapter_Lesson to PDF filename
    slideMap: {
        "1_1": "Chuong_1_Tiet_01_Khái niệm, đặc điểm TMĐT.pdf",
        "1_2": "Chuong_1_Tiet_02_Sự khác biệt và các cấp độ số hóa doanh nghiệp.pdf",
        "1_3": "Chuong_1_Tiet_03_Lợi thế chiến lược và chìa khóa thành công.pdf",
        "1_4": "Chuong_1_Tiet_04_E-commerce_Tech_Law_Foundation.pdf",
        "1_5": "Chuong_1_Tiet_05_Thanh_toán_điện_tử_và_An_toàn_thương_mại.pdf",
        "1_6": "Chuong_1_Tiet_06_E-commerce_Logistics_The_Iceberg_Beneath_The_Click.pdf",
        "1_7": "Chuong_1_Tiet_07_B2C_and_B2B_Core_E-commerce_Models.pdf",
        "1_8": "Chuong_1_Tiet_08_Sức_mạnh_cá_nhân_C2C_và_C2B.pdf",
        "1_9": "Chuong_1_Tiet_09_TMĐT_Chiến_lược_Chuyển_dịch_Giá_trị.pdf",
        "1_10": "Chuong_1_Tiet_10_Thương_mại_điện_tử_và_Sàn_giao_dịch.pdf",
        "1_11": "Chuong_1_Tiet_11_E-commerce_Transaction_Mechanisms.pdf",
        "1_12": "Chuong_1_Tiet_12_E-commerce_Chiến_Lược_Thực_Chiến.pdf"
    },

    init: function () {
        this.renderSelectionScreen();
        this.setupEventListeners();
    },

    setupEventListeners: function () {
        document.addEventListener('keydown', (e) => {
            if (document.getElementById('view-quiz').classList.contains('hidden')) return;
            if (e.key === 'ArrowRight') this.nextQuestion();
            if (e.key === 'ArrowLeft') this.prevQuestion();
        });
    },

    // --- Navigation & Views ---

    showView: function (viewId) {
        document.querySelectorAll('.view-section').forEach(el => {
            el.classList.add('hidden');
            el.classList.remove('fade-in');
        });
        const view = document.getElementById(viewId);
        view.classList.remove('hidden');

        // Toggle Main Header and Adjust Height
        const mainHeader = document.querySelector('header');
        const dashboardView = document.getElementById('view-dashboard');

        if (viewId === 'view-dashboard') {
            mainHeader.classList.add('hidden');
            // Adjust dashboard to be full screen
            dashboardView.classList.remove('h-[calc(100vh-80px)]');
            dashboardView.classList.add('h-screen');
            // Remove margin tweaks as we are now top of screen
            // But we might need them if padding exists on main. 
            // The main has py-8. -mt-8 cancels it. 
            // If header is gone, we still need to cancel main's padding effectively or let it be.
            // Let's keep existing margin classes for now, just fix height.
        } else {
            mainHeader.classList.remove('hidden');
            if (dashboardView) {
                dashboardView.classList.add('h-[calc(100vh-80px)]');
                dashboardView.classList.remove('h-screen');
            }
        }

        // Trigger reflow to restart animation
        void view.offsetWidth;
        view.classList.add('fade-in');
    },

    goHome: function () {
        // Stop video if playing
        const videoFrame = document.getElementById('video-frame');
        if (videoFrame) videoFrame.src = ""; // Stop playback

        this.resetQuizViewPosition(); // Ensure quiz view is restored

        if (this.state.currentChapter !== null && this.state.currentModule === null) {
            // If in chapter view (module list), go back to Chapter list
            this.state.currentChapter = null;
            this.renderSelectionScreen();
        } else {
            // Full reset
            this.state.currentChapter = null;
            this.state.currentModule = null;
            this.state.currentPart = null;
            this.renderSelectionScreen();
        }
    },

    backToModules: function () {
        // Stop video if playing
        const videoFrame = document.getElementById('video-frame');
        if (videoFrame) videoFrame.src = ""; // Stop playback

        this.resetQuizViewPosition();
        // From Parts view to Module list (Chapter view)
        this.state.currentModule = null;
        this.state.currentPart = null;
        this.renderSelectionScreen();
    },

    backToParts: function () {
        this.resetQuizViewPosition();
        // From Quiz to Parts view OR Dashboard
        this.state.currentPart = null;

        if (this.state.currentModule.video) {
            this.showDashboard();
            this.switchTab('practice');
        } else {
            this.showView('view-parts');
            document.getElementById('header-title').textContent = this.state.currentModule.name;
        }
    },

    // --- Dashboard Logic ---

    showDashboard: function () {
        this.showView('view-dashboard');
        document.getElementById('dashboard-title').textContent = this.state.currentModule.name;

        // Video is now lazy-loaded in switchTab


        // Load Mindmap Image
        const mindmapDetails = this.getMindmapDetails();
        const mindmapImg = document.getElementById('mindmap-image');
        const mindmapPlaceholder = document.getElementById('mindmap-placeholder');

        // Reset state
        mindmapImg.classList.remove('hidden');
        mindmapPlaceholder.classList.add('hidden');

        if (mindmapDetails) {
            mindmapImg.src = `DB/Mindmap/Chuong_${mindmapDetails.chapter}_Tiet_${mindmapDetails.lesson}.png`;
            mindmapImg.onerror = function () {
                this.classList.add('hidden');
                mindmapPlaceholder.classList.remove('hidden');
            };
        } else {
            mindmapImg.classList.add('hidden');
            mindmapPlaceholder.classList.remove('hidden');
        }

        // Default to Mindmap tab
        this.switchTab('mindmap');
    },

    getMindmapDetails: function () {
        if (this.state.currentChapter === null || this.state.currentModule === null) return null;

        const chapterNum = this.state.currentChapter + 1;
        // Try to extract lesson number from name "Tiết X: ..."
        const match = this.state.currentModule.name.match(/Tiết (\d+)/i);
        if (match && match[1]) {
            return { chapter: chapterNum, lesson: match[1] };
        }
        return null;
    },

    switchTab: function (tabName) {
        const tabMindmap = document.getElementById('tab-mindmap');
        const tabSlide = document.getElementById('tab-slide');
        const tabVideo = document.getElementById('tab-video');
        const tabPractice = document.getElementById('tab-practice');

        const contentMindmap = document.getElementById('content-mindmap');
        const contentSlide = document.getElementById('content-slide');
        const contentVideo = document.getElementById('content-video');
        const contentPractice = document.getElementById('content-practice');

        // Reset all tabs
        [tabMindmap, tabSlide, tabVideo, tabPractice].forEach(tab => {
            tab.classList.remove('bg-white', 'text-primary', 'shadow-sm');
            tab.classList.add('text-gray-600', 'hover:text-gray-900');
        });

        // Hide all contents
        [contentMindmap, contentSlide, contentVideo, contentPractice].forEach(content => {
            content.classList.add('hidden');
        });

        if (tabName === 'mindmap') {
            tabMindmap.classList.add('bg-white', 'text-primary', 'shadow-sm');
            tabMindmap.classList.remove('text-gray-600', 'hover:text-gray-900');
            contentMindmap.classList.remove('hidden');

            this.pauseVideo();
        } else if (tabName === 'slide') {
            tabSlide.classList.add('bg-white', 'text-primary', 'shadow-sm');
            tabSlide.classList.remove('text-gray-600', 'hover:text-gray-900');
            contentSlide.classList.remove('hidden');

            this.pauseVideo();

            // Lazy load slide
            const slideFrame = document.getElementById('slide-frame');
            const details = this.getMindmapDetails(); // Reuse this function as it extracts chapter/lesson
            if (details) {
                // Use the map to find the filename
                const key = `${details.chapter}_${details.lesson}`;
                const filename = this.slideMap[key];

                if (filename) {
                    // Encode spaces and special chars in URL
                    const pdfPath = `DB/Slide/${encodeURIComponent(filename)}`;
                    // Avoid reloading if already set
                    if (!slideFrame.src.includes(encodeURIComponent(filename))) {
                        slideFrame.src = pdfPath;
                    }
                } else {
                    console.warn(`No slide found for ${key}`);
                }
            }
        } else if (tabName === 'video') {
            tabVideo.classList.add('bg-white', 'text-primary', 'shadow-sm');
            tabVideo.classList.remove('text-gray-600', 'hover:text-gray-900');
            contentVideo.classList.remove('hidden');

            // Lazy load video
            const videoFrame = document.getElementById('video-frame');
            if (this.state.currentModule.video && !videoFrame.src.includes(this.state.currentModule.video)) {
                videoFrame.src = this.state.currentModule.video;
            }
        } else {
            tabPractice.classList.add('bg-white', 'text-primary', 'shadow-sm');
            tabPractice.classList.remove('text-gray-600', 'hover:text-gray-900');
            contentPractice.classList.remove('hidden');

            this.pauseVideo();

            // Auto-start quiz if not active
            if (!this.state.currentPart && this.state.parts.length > 0) {
                this.startPracticeFromDashboard();
            }
        }
    },

    openSlideFullscreen: function () {
        const slideFrame = document.getElementById('slide-frame');
        if (slideFrame.requestFullscreen) {
            slideFrame.requestFullscreen();
        } else if (slideFrame.webkitRequestFullscreen) { /* Safari */
            slideFrame.webkitRequestFullscreen();
        } else if (slideFrame.msRequestFullscreen) { /* IE11 */
            slideFrame.msRequestFullscreen();
        }

        // Handling orientation for mobile
        if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock('landscape').catch(err => {
                console.log("Orientation lock failed: ", err);
            });
        }
    },

    pauseVideo: function () {
        const videoFrame = document.getElementById('video-frame');
        try {
            if (videoFrame && videoFrame.contentWindow) {
                const iframeDoc = videoFrame.contentWindow.document;
                const vid = iframeDoc.getElementById('video-element');
                const aud = iframeDoc.getElementById('slide-audio');
                if (vid && !vid.paused) vid.pause();
                if (aud && !aud.paused) aud.pause();
            }
        } catch (e) {
            console.log("Cannot pause video iframe:", e);
        }
    },

    startPracticeFromDashboard: function () {
        this.embedQuizView();

        // Default to first part (skipping selection for dashboard convenience)
        if (this.state.parts.length > 0) {
            this.startQuiz(this.state.parts[0]);
        }
    },

    renderSelectionScreen: function () {
        const container = document.getElementById('module-list');
        container.innerHTML = '';
        this.showView('view-modules');

        // Logic to render Chapters or Modules based on state
        if (this.state.currentChapter === null) {
            // Render Chapters
            document.getElementById('header-title').textContent = 'Trang chủ - Danh sách Chương';
            this.config.chapters.forEach((chap, index) => {
                const card = document.createElement('div');
                card.className = 'bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-100 cursor-pointer flex flex-col items-center text-center group';
                card.onclick = () => this.selectChapter(index);

                card.innerHTML = `
                    <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                        <i class="fa-solid fa-folder-open text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">${chap.name}</h3>
                    <span class="text-sm text-gray-500">${chap.modules.length} Tiết</span>
                `;
                container.appendChild(card);
            });
        } else {
            // Render Modules of selected chapter
            const chapter = this.config.chapters[this.state.currentChapter];
            document.getElementById('header-title').textContent = chapter.name;

            // Add "Back" card/button if desired, or rely on Header Home button
            // Let's add a visual back item or just render modules

            if (chapter.modules.length === 0) {
                container.innerHTML = '<p class="col-span-full text-center text-gray-500">Chưa có nội dung cho chương này.</p>';
                return;
            }

            chapter.modules.forEach((mod) => {
                const card = document.createElement('div');
                card.className = 'bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-100 cursor-pointer flex flex-col items-center text-center group';
                card.onclick = () => this.loadModule(mod);

                card.innerHTML = `
                    <div class="w-16 h-16 bg-green-50 text-green-600 rounded-full flex items-center justify-center mb-4 group-hover:bg-green-600 group-hover:text-white transition-colors">
                        <i class="fa-solid fa-file-csv text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-semibold text-gray-800 mb-2">${mod.name}</h3>
                    <span class="text-sm text-gray-500">Nhấn để vào bài tập</span>
                `;
                container.appendChild(card);
            });
        }
    },

    selectChapter: function (index) {
        this.state.currentChapter = index;
        this.renderSelectionScreen();
    },

    // --- Test Mode Logic ---

    showTestSetup: function () {
        const container = document.getElementById('test-module-list');
        container.innerHTML = '';

        let flatIndex = 0;
        this.config.chapters.forEach((chap, cIdx) => {
            if (chap.modules.length === 0) return;

            const chapHeader = document.createElement('h4');
            chapHeader.className = "font-bold text-gray-700 mt-4 mb-2";
            chapHeader.textContent = chap.name;
            container.appendChild(chapHeader);

            chap.modules.forEach((mod, mIdx) => {
                const div = document.createElement('div');
                div.className = 'flex items-center ml-4 mb-2';
                // Value stores "cIdx,mIdx"
                div.innerHTML = `
                    <input type="checkbox" id="mod-check-${cIdx}-${mIdx}" value="${cIdx},${mIdx}" class="w-5 h-5 text-primary border-gray-300 rounded focus:ring-primary">
                    <label for="mod-check-${cIdx}-${mIdx}" class="ml-3 text-gray-700 font-medium cursor-pointer select-none">${mod.name}</label>
                `;
                container.appendChild(div);
            });
        });

        document.getElementById('max-questions').textContent = 'Tùy chọn';
        this.showView('view-test-setup');
        document.getElementById('header-title').textContent = 'Tạo Đề Kiểm Tra';
    },

    startCustomTest: async function () {
        const selectedValues = [];
        document.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
            selectedValues.push(cb.value); // "cIdx,mIdx"
        });

        if (selectedValues.length === 0) {
            alert("Vui lòng chọn ít nhất một module!");
            return;
        }

        const countInput = document.getElementById('question-count');
        const requestedCount = parseInt(countInput.value);

        if (isNaN(requestedCount) || requestedCount < 1) {
            alert("Vui lòng nhập số lượng câu hỏi hợp lệ!");
            return;
        }

        document.getElementById('loading').classList.remove('hidden');

        try {
            const promises = selectedValues.map(val => {
                const [cIdx, mIdx] = val.split(',').map(Number);
                const file = this.config.chapters[cIdx].modules[mIdx].file;
                return new Promise((resolve, reject) => {
                    Papa.parse(file, {
                        download: true, header: true, skipEmptyLines: true,
                        complete: (results) => resolve(results.data),
                        error: (err) => reject(err)
                    });
                });
            });

            const results = await Promise.all(promises);
            let allQuestions = results.flat();

            // Shuffle all questions
            this.shuffleArray(allQuestions);

            // Slice to requested count
            if (allQuestions.length > requestedCount) {
                allQuestions = allQuestions.slice(0, requestedCount);
            }

            this.state.isTestMode = true;
            this.state.quizQuestions = allQuestions;
            this.state.currentQuestionIndex = 0;
            this.state.userResults = {};

            // Ensure Quiz View is in Main, not embedded
            this.resetQuizViewPosition();

            this.renderQuestionPalette();
            this.renderQuestion();
            this.showView('view-quiz');
            document.getElementById('header-title').textContent = `Bài Kiểm Tra (${allQuestions.length} câu)`;
        } catch (error) {
            console.error(error);
            alert("Có lỗi khi tải dữ liệu.");
        } finally {
            document.getElementById('loading').classList.add('hidden');
        }
    },

    // --- DOM Reparenting Helpers for Embedded Quiz ---

    embedQuizView: function () {
        const viewQuiz = document.getElementById('view-quiz');
        const contentPractice = document.getElementById('content-practice');

        // Move view-quiz into content-practice
        contentPractice.appendChild(viewQuiz);

        // Remove standard view-section classes to fit embedding
        viewQuiz.classList.remove('view-section', 'hidden');
        viewQuiz.classList.add('w-full', 'h-full');
    },

    resetQuizViewPosition: function () {
        const viewQuiz = document.getElementById('view-quiz');
        const main = document.querySelector('main');

        // Restore to main if it's currently embedded
        if (viewQuiz.parentElement !== main) {
            main.appendChild(viewQuiz);
            viewQuiz.classList.add('view-section', 'hidden');
            viewQuiz.classList.remove('w-full', 'h-full');
        }
    },

    shuffleArray: function (array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    },

    loadModule: function (moduleConfig) {
        this.state.currentModule = moduleConfig;

        document.getElementById('loading').classList.remove('hidden');

        Papa.parse(moduleConfig.file, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                document.getElementById('loading').classList.add('hidden');
                if (results.errors.length > 0) {
                    console.error("CSV Errors:", results.errors);
                    alert("Có lỗi khi đọc file dữ liệu. Vui lòng kiểm tra console.");
                    return;
                }
                this.processData(results.data);

                if (moduleConfig.video) {
                    this.showDashboard();
                } else if (this.state.parts.length === 1) {
                    this.startQuiz(this.state.parts[0]);
                } else {
                    this.renderPartSelection();
                    this.showView('view-parts');
                    document.getElementById('header-title').textContent = moduleConfig.name;
                }
            },
            error: (err) => {
                document.getElementById('loading').classList.add('hidden');
                console.error("Fetch Error:", err);
                alert("Không thể tải file dữ liệu: " + moduleConfig.file);
            }
        });
    },

    processData: function (data) {
        // Filter out empty rows or rows without a question content
        // This safeguards against "ghost" questions from trailing empty lines in CSV
        const validData = data.filter(row => row.QuestionContent && row.QuestionContent.trim() !== "");

        this.state.allQuestions = validData;
        this.state.parts = [];

        const CHUNK_SIZE = 30;
        const totalQuestions = validData.length;
        const totalParts = Math.ceil(totalQuestions / CHUNK_SIZE);

        for (let i = 0; i < totalParts; i++) {
            const start = i * CHUNK_SIZE;
            const end = Math.min(start + CHUNK_SIZE, totalQuestions);
            const chunk = validData.slice(start, end);

            this.state.parts.push({
                id: i + 1,
                name: `Phần ${i + 1} (Câu ${start + 1} - ${end})`,
                questions: chunk
            });
        }
    },

    renderPartSelection: function () {
        const container = document.getElementById('part-list');
        const moduleName = this.state.currentModule.name;
        document.getElementById('module-name-display').textContent = moduleName;

        container.innerHTML = '';

        if (this.state.parts.length === 0) {
            container.innerHTML = '<p class="text-gray-500 col-span-full text-center">Không tìm thấy dữ liệu nào trong module này.</p>';
            return;
        }

        this.state.parts.forEach(part => {
            const btn = document.createElement('div');
            btn.className = 'bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:border-primary hover:shadow-md cursor-pointer transition-all flex justify-between items-center';
            btn.onclick = () => this.startQuiz(part);

            btn.innerHTML = `
                <div>
                    <span class="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Bài tập</span>
                    <span class="text-xl font-bold text-gray-800">${part.name}</span>
                </div>
                <div class="text-right">
                    <span class="block text-2xl font-bold text-primary">${part.questions.length}</span>
                    <span class="text-xs text-gray-500">Câu hỏi</span>
                </div>
            `;
            container.appendChild(btn);
        });
    },

    // --- Quiz Logic ---

    startQuiz: function (part) {
        this.state.currentPart = part;
        // Clone and shuffle questions for randomness
        this.state.quizQuestions = [...part.questions];
        this.shuffleArray(this.state.quizQuestions);

        if (this.state.quizQuestions.length === 0) {
            alert("Không có câu hỏi nào trong phần này.");
            return;
        }

        this.state.currentQuestionIndex = 0;
        this.state.userResults = {}; // Reset results

        this.renderQuestionPalette();
        this.renderQuestion();

        // Check where the view is located
        const viewQuiz = document.getElementById('view-quiz');
        if (viewQuiz.parentElement.id === 'content-practice') {
            // Embedded: Tab handles visibility
        } else {
            // Standalone: Show view
            this.showView('view-quiz');
            document.getElementById('header-title').textContent = `${part.name} - ${this.state.currentModule.name}`;
        }
    },

    renderQuestion: function () {
        const qIndex = this.state.currentQuestionIndex;



        // ...




        const question = this.state.quizQuestions[qIndex];
        const total = this.state.quizQuestions.length;

        // Update Progress
        const progress = ((qIndex + 1) / total) * 100;
        document.getElementById('progress-bar').style.width = `${progress}%`;
        document.getElementById('current-question-number').textContent = `${qIndex + 1}/${total}`;

        // Reset UI state
        document.getElementById('feedback-area').classList.add('hidden');
        document.getElementById('question-status').textContent = this.state.userResults[qIndex] === 'correct' ? 'Đã hoàn thành' : 'Chưa hoàn thành';
        document.getElementById('question-status').className = this.state.userResults[qIndex] === 'correct' ? 'text-sm font-medium text-green-600' : 'text-sm font-medium text-gray-500';

        // Render Text
        document.getElementById('question-text').textContent = question.QuestionContent;

        // Render Options
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        // Note: CSV headers might have typos like "AAnsver" based on previous file view
        // We map standard keys A, B, C, D to the CSV columns
        let optionKeys = [
            { key: 'A', text: question.AAnsver || question.AAnswer }, // Handle typo
            { key: 'B', text: question.BAnswer },
            { key: 'C', text: question.CAnswer },
            { key: 'D', text: question.DAnswer }
        ];

        // Filter out empty options first
        optionKeys = optionKeys.filter(opt => opt.text && opt.text.trim() !== "");

        // Always shuffle options for randomness
        this.shuffleArray(optionKeys);

        const isAnsweredCorrectly = this.state.userResults[qIndex] === 'correct';
        const displayLabels = ['A', 'B', 'C', 'D', 'E', 'F']; // Visual labels

        optionKeys.forEach((opt, index) => {
            const visualLabel = displayLabels[index] || String.fromCharCode(65 + index); // Fallback to A, B, C...

            const el = document.createElement('div');
            el.className = 'quiz-option bg-white p-4 rounded-lg border flex flex-col justify-center group';
            el.dataset.key = opt.key; // Keeps the logical key (e.g., C) for checking correctness

            // If already answered correctly, show state
            if (isAnsweredCorrectly) {
                el.classList.add('disabled');
                if (opt.key === question.Answer) {
                    el.classList.add('correct');
                }
            } else {
                el.onclick = () => this.checkAnswer(opt.key, question.Answer, el);
            }

            el.innerHTML = `
                <div class="flex items-center w-full">
                    <span class="w-8 h-8 rounded-full bg-gray-100 text-gray-600 font-bold flex items-center justify-center mr-4 group-hover:bg-white border border-gray-200 transition-colors flex-shrink-0">${visualLabel}</span>
                    <span class="text-gray-700 font-medium">${opt.text}</span>
                </div>
            `;
            optionsContainer.appendChild(el);
        });

        // Update buttons
        document.getElementById('btn-prev').disabled = qIndex === 0;
        document.getElementById('btn-next').disabled = qIndex === total - 1;

        // Update Palette Active State
        this.updatePaletteActiveState();
    },

    checkAnswer: function (selectedKey, correctKey, element) {
        // Clean keys just in case (trim whitespace)
        const selected = selectedKey.trim().toUpperCase();
        const correct = correctKey.trim().toUpperCase();

        const feedbackArea = document.getElementById('feedback-area');
        const feedbackText = document.getElementById('feedback-text');

        if (selected === correct) {
            // Correct
            element.classList.add('correct');
            element.classList.add('disabled');

            // Disable all other options
            const allOptions = document.querySelectorAll('.quiz-option');
            allOptions.forEach(opt => opt.classList.add('disabled'));

            feedbackArea.classList.add('hidden'); // Hide feedback area as we show inside option

            let explanationHtml = '';
            const question = this.state.quizQuestions[this.state.currentQuestionIndex];
            if (question.Explanation && question.Explanation.trim() !== "") {
                explanationHtml = `<div class="mt-3 pt-3 border-t border-green-200 text-sm text-green-800">
                    ${question.Explanation}
                </div>`;
            }

            // Append to the clicked element (which is the correct one)
            // We need to inject it before the closing of the div, but since innerHTML resets events, we need to be careful?
            // Actually, we disable the option anyway so events don't matter much.
            // But let's append properly.
            element.insertAdjacentHTML('beforeend', explanationHtml);

            this.state.userResults[this.state.currentQuestionIndex] = 'correct';
            this.updatePaletteItem(this.state.currentQuestionIndex, 'correct');

            // Update status text
            document.getElementById('question-status').textContent = 'Đã hoàn thành';
            document.getElementById('question-status').className = 'text-sm font-medium text-green-600';

        } else {
            // Wrong
            element.classList.add('wrong');
            // Remove wrong class after animation to allow retry (optional, but requested "cho chọn lại")
            // But we keep it red to show it was wrong.

            feedbackArea.className = 'mt-6 p-4 rounded-lg border-l-4 bg-red-50 border-red-500 text-red-700 fade-in';
            feedbackText.innerHTML = '<i class="fa-solid fa-circle-exclamation mr-2"></i> Sai rồi, hãy thử lại!';
            feedbackArea.classList.remove('hidden');

            // If not already marked correct, mark as wrong (or 'attempted')
            if (this.state.userResults[this.state.currentQuestionIndex] !== 'correct') {
                // We don't permanently mark it wrong in the palette if they can retry, 
                // but we can show red to indicate they missed it at least once.
                this.state.userResults[this.state.currentQuestionIndex] = 'wrong';
                this.updatePaletteItem(this.state.currentQuestionIndex, 'wrong');
            }
        }
    },

    // --- Palette & Navigation Helpers ---

    renderQuestionPalette: function () {
        const container = document.getElementById('question-palette');
        container.innerHTML = '';

        this.state.quizQuestions.forEach((_, index) => {
            const btn = document.createElement('button');
            btn.className = 'palette-item w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-100 text-gray-600 text-xs sm:text-sm font-medium flex items-center justify-center hover:bg-gray-200 focus:outline-none';
            btn.textContent = index + 1;
            btn.onclick = () => this.jumpToQuestion(index);
            btn.id = `palette-btn-${index}`;
            container.appendChild(btn);
        });
    },

    updatePaletteItem: function (index, status) {
        const btn = document.getElementById(`palette-btn-${index}`);
        if (!btn) return;

        // Reset base classes
        btn.className = 'palette-item w-8 h-8 sm:w-10 sm:h-10 rounded-full text-xs sm:text-sm font-medium flex items-center justify-center focus:outline-none transition-colors';

        if (status === 'correct') {
            btn.classList.add('bg-green-500', 'text-white');
        } else if (status === 'wrong') {
            btn.classList.add('bg-red-500', 'text-white');
        } else {
            btn.classList.add('bg-gray-100', 'text-gray-600', 'hover:bg-gray-200');
        }

        // Re-add active state if needed
        if (index === this.state.currentQuestionIndex) {
            btn.classList.add('active');
        }
    },

    updatePaletteActiveState: function () {
        // Remove active from all
        document.querySelectorAll('.palette-item').forEach(btn => btn.classList.remove('active'));
        // Add to current
        const btn = document.getElementById(`palette-btn-${this.state.currentQuestionIndex}`);
        if (btn) btn.classList.add('active');
    },

    jumpToQuestion: function (index) {
        this.state.currentQuestionIndex = index;
        this.renderQuestion();
    },

    nextQuestion: function () {
        if (this.state.currentQuestionIndex < this.state.quizQuestions.length - 1) {
            this.state.currentQuestionIndex++;
            this.renderQuestion();
        }
    },

    prevQuestion: function () {
        if (this.state.currentQuestionIndex > 0) {
            this.state.currentQuestionIndex--;
            this.renderQuestion();
        }
    },

    // --- Mindmap Modal Logic ---

    openMindmapModal: function () {
        const mindmapImg = document.getElementById('mindmap-image');
        const modal = document.getElementById('mindmap-modal');
        const modalImg = document.getElementById('mindmap-modal-img');

        if (mindmapImg && mindmapImg.src && !mindmapImg.classList.contains('hidden')) {
            modalImg.src = mindmapImg.src;
            modal.classList.remove('hidden');
        }
    },

    closeMindmapModal: function () {
        const modal = document.getElementById('mindmap-modal');
        modal.classList.add('hidden');
        // Clear src to save memory/stop any loading
        setTimeout(() => {
            if (modal.classList.contains('hidden')) {
                document.getElementById('mindmap-modal-img').src = "";
            }
        }, 300);
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
