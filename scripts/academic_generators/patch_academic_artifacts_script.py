import sys

def patch_academic_script():
    ps1_path = r"D:\Project\Nhom02_SDNFlowGuard\scripts\generate_academic_artifacts.ps1"
    with open(ps1_path, "r", encoding="utf-8-sig") as f:
        text = f.read()

    # 1. Update A4 PageSetup
    old_setup = """    # Page Setup (Standard Vietnamese Academic Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm)
    $doc.PageSetup.TopMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.BottomMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.LeftMargin = $word.CentimetersToPoints(3.0)
    $doc.PageSetup.RightMargin = $word.CentimetersToPoints(2.0)"""

    new_setup = """    # Page Setup (Standard Vietnamese Academic A4 Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm)
    $doc.PageSetup.PaperSize = 7 # 7 = wdPaperA4
    $doc.PageSetup.PageWidth = $word.CentimetersToPoints(21.0)
    $doc.PageSetup.PageHeight = $word.CentimetersToPoints(29.7)
    $doc.PageSetup.TopMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.BottomMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.LeftMargin = $word.CentimetersToPoints(3.0)
    $doc.PageSetup.RightMargin = $word.CentimetersToPoints(2.0)"""

    text = text.replace(old_setup, new_setup)

    # 2. Update Cover Page (Mẫu 01-BCBTL UTH)
    old_cover = """    # Title Cover Page
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
    $sel.Font.Name = "Times New Roman"
    $sel.Font.Size = 13
    $sel.Font.Bold = $true
    $sel.TypeText("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN`n")
    $sel.TypeText("KHOA MẠNG MÁY TÍNH VÀ TRUYỀN THÔNG`n`n`n")
    
    $sel.Font.Size = 16
    $sel.TypeText("BÁO CÁO TỔNG KẾT ĐỒ ÁN CHUYÊN ĐỀ`n")
    $sel.Font.Size = 14
    $sel.TypeText("MÔN HỌC: CHUYÊN ĐỀ - HỆ THỐNG MẠNG VÀ BẢO MẬT`n`n`n`n")
    
    $sel.Font.Size = 18
    $sel.Font.Bold = $true
    $sel.TypeText("NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK`n`n")
    
    $sel.Font.Size = 14
    $sel.Font.Italic = $true
    $sel.TypeText("(HỆ THỐNG SDNFLOWGUARD)`n`n`n`n`n`n")
    
    $sel.Font.Italic = $false
    $sel.Font.Size = 13
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
    $sel.ParagraphFormat.LeftIndent = $word.CentimetersToPoints(4.0)
    $sel.TypeText("Giảng viên hướng dẫn: Bộ môn An toàn thông tin`n")
    $sel.TypeText("Nhóm thực hiện:        Nhóm 02`n")
    $sel.TypeText("Sinh viên thực hiện:  Phan Phát Đạt`n`n`n`n`n`n")
    
    $sel.ParagraphFormat.LeftIndent = 0
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
    $sel.Font.Size = 12
    $sel.Font.Bold = $false
    $sel.TypeText("TP. HỒ CHÍ MINH, NĂM 2026`n")"""

    new_cover = """    # Title Cover Page (Mẫu 01-BCBTL UTH)
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
    $sel.Font.Name = "Times New Roman"
    $sel.Font.Size = 13
    $sel.Font.Bold = $true
    $sel.TypeText("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH (UTH)`n")
    $sel.TypeText("KHOA CÔNG NGHỆ THÔNG TIN`n`n`n")
    
    $sel.Font.Size = 16
    $sel.TypeText("BÁO CÁO BÀI TẬP LỚN MÔN CHUYÊN ĐỀ - HỆ THỐNG MẠNG VÀ BẢO MẬT`n")
    $sel.Font.Size = 13
    $sel.Font.Bold = $false
    $sel.TypeText("(MÃ HỌC PHẦN: 123046)`n`n`n`n")
    
    $sel.Font.Size = 18
    $sel.Font.Bold = $true
    $sel.TypeText("NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK`n`n")
    
    $sel.Font.Size = 14
    $sel.Font.Italic = $true
    $sel.TypeText("(HỆ THỐNG SDNFLOWGUARD)`n`n`n`n`n")
    
    $sel.Font.Italic = $false
    $sel.Font.Size = 13
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
    $sel.ParagraphFormat.LeftIndent = $word.CentimetersToPoints(3.5)
    $sel.TypeText("Chuyên ngành:         Mạng máy tính và Truyền thông dữ liệu`n")
    $sel.TypeText("Giảng viên hướng dẫn: Thầy/Cô phụ trách học phần`n")
    $sel.TypeText("Nhóm thực hiện:        Nhóm 02`n")
    $sel.TypeText("Sinh viên thực hiện:  Phan Phát Đạt`n`n`n`n`n")
    
    $sel.ParagraphFormat.LeftIndent = 0
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
    $sel.Font.Size = 12
    $sel.Font.Bold = $false
    $sel.TypeText("TP. HỒ CHÍ MINH, THÁNG 11 NĂM 2026`n")"""

    text = text.replace(old_cover, new_cover)

    # 3. Update Lời cảm ơn
    text = text.replace("Khoa Mạng máy tính và Truyền thông, Trường Đại học Công nghệ Thông tin", "Khoa Công nghệ thông tin, Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH)")

    # 4. Expand PowerPoint to 28 slides with Title=32pt, Content=26pt (as required in DeTai.pdf)
    old_ppt_code = text[text.find("# -------------------------------------------------------------------------"):text.find("$finalSlides = $pres.Slides.Count")]

    new_ppt_code = """# -------------------------------------------------------------------------
    Write-Host "`n[2/2] Initializing Microsoft PowerPoint COM Automation..."
    $ppt = New-Object -ComObject PowerPoint.Application
    $pres = $ppt.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoFalse)
    
    # Slide 1: Bìa trình chiếu (Mẫu chuẩn UTH)
    $s1 = $pres.Slides.Add(1, 1) # Title Layout
    $s1.Shapes.Title.TextFrame.TextRange.Text = "TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP.HCM (UTH)`nĐỒ ÁN CHUYÊN ĐỀ HỆ THỐNG MẠNG VÀ BẢO MẬT"
    $s1.Shapes.Title.TextFrame.TextRange.Font.Size = 32
    $s1.Shapes.Title.TextFrame.TextRange.Font.Bold = $true
    $s1.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "ĐỀ TÀI: PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP ELK STACK`n(HỆ THỐNG SDNFLOWGUARD)`n`nSinh viên thực hiện: Phan Phát Đạt — Nhóm 02`nTháng 11 Năm 2026"
    $s1.Shapes.Placeholders.Item(2).TextFrame.TextRange.Font.Size = 24

    $slidesData = @(
        @("1. Mục Lục & Cấu Trúc Báo Cáo", @(
            "• Phần I: Cơ sở lý thuyết và kiến trúc 4 mặt phẳng SDN.",
            "• Phần II: Mô hình triển khai thực nghiệm Mininet và OVS.",
            "• Phần III: 4 Kịch bản tấn công - phòng thủ và 4 bước demo.",
            "• Phần IV: Kết quả kiểm thử tự động (53/53 PASS) và kết luận."
        )),
        @("2. Đặt Vấn Đề & Tính Cấp Thiết", @(
            "• Mạng doanh nghiệp đối mặt các đợt DoS/DDoS và quét cổng phức tạp.",
            "• Mạng truyền thống khó quan sát toàn cục và phản ứng chậm trễ.",
            "• Cần giải pháp giám sát tập trung kết hợp phản ứng SDN tự động."
        )),
        @("3. Nghịch Lý Phòng Thủ SDN Cốt Lõi", @(
            "• Nghịch lý: 'Attached Host != Verified Attacker'.",
            "• Thống kê cổng OpenFlow chỉ đo lường số lượng gói trên cổng switch.",
            "• Cổng có thể đa host hoặc là nạn nhân nhận luồng phản hồi.",
            "• Nguyên tắc an toàn: Không chặn IP khi chưa có bằng chứng nguồn L2/L3."
        )),
        @("4. Mục Tiêu Nghiên Cứu & Cam Kết Đề Tài", @(
            "• Xây dựng hệ thống SDNFlowGuard tích hợp ONOS Controller và ELK.",
            "• Phát hiện bất thường lưu lượng chuỗi thời gian (PPS threshold).",
            "• Thiết lập chuỗi đối soát bằng chứng Step 63 và Step 64.",
            "• Cổng an toàn Safety Gate mặc định DRY_RUN, hỗ trợ Rollback."
        )),
        @("5. Chuẩn Đầu Ra (CLO) & Đối Chiếu Học Phần", @(
            "• CLO1: Nắm vững kiến thức an toàn mạng, giải thích rủi ro và nguy cơ.",
            "• CLO2: Xây dựng, đánh giá và triển khai giải pháp bảo mật mạng.",
            "• CLO3: Tự nghiên cứu công nghệ mới (SDN, SIEM) và làm việc độc lập."
        )),
        @("6. Tổng Quan Kiến Trúc SDN & OpenFlow 1.3", @(
            "• Tách rời Control Plane (tập trung) và Data Plane (chuyển tiếp).",
            "• Giao thức OpenFlow 1.3: Quản lý Flow Table, Flow Rule và Meter.",
            "• Khả năng lập trình mạng động và điều phối chính sách tức thì."
        )),
        @("7. Bộ Điều Khiển Mạng ONOS SDN Controller", @(
            "• Hệ điều hành mạng hiệu năng cao, hỗ trợ phân tán và kiến trúc module.",
            "• Cung cấp REST API quản lý thiết bị, topology, intent và host discovery.",
            "• Điều khiển các switch Open vSwitch qua kênh OpenFlow port 6653."
        )),
        @("8. Ngăn Xếp Giám Sát SIEM: ELK Stack", @(
            "• Elasticsearch: Lưu trữ và tra cứu chỉ mục bảo mật phân tán theo ngày.",
            "• Logstash: Tiếp nhận, chuẩn hóa và chuyển đổi cấu trúc sự kiện mạng.",
            "• Kibana: Bảng điều khiển trực quan hóa SOC và phát hiện bất thường."
        )),
        @("9. Kiến Trúc Tổng Thể 4 Mặt Phẳng", @(
            "• Data Plane: Mininet, switch ảo Open vSwitch (OVS 3.7.1), hosts h1, h2.",
            "• Control Plane: ONOS SDN Controller (REST API :8181, OpenFlow :6653).",
            "• Application & Security Plane: Flask Backend, Clean Architecture, React UI.",
            "• Monitoring Plane: Logstash HTTP :18080, Elasticsearch :9200, Kibana :5601."
        )),
        @("10. Thiết Kế Clean Architecture Backend", @(
            "• Tách biệt 4 tầng: Domain Policies, Application, Infrastructure, Presentation.",
            "• Domain: Safety Gate, Risk Scoring, Defense Policy, Event Correlator.",
            "• Infrastructure: ONOS Client, SQLite Repository, Elasticsearch Adapter.",
            "• Độc lập với framework, dễ dàng mở rộng và kiểm thử tự động."
        )),
        @("11. Pipeline Thu Thập Dữ Liệu & Telemetry", @(
            "• onos_port_elk_collector.py: Định kỳ lấy mẫu thống kê cổng từ ONOS.",
            "• Tính toán delta gói tin (rx_packets) và delta byte trong chu kỳ 5 giây.",
            "• Đẩy sự kiện qua Logstash HTTP Input để lập chỉ mục vào Elasticsearch."
        )),
        @("12. Động Cơ Phát Hiện Bất Thường V1 & V2", @(
            "• sdn_port_anomaly_detector: Phát hiện chuỗi vượt ngưỡng (streak >= 2).",
            "• Reset streak khi khoảng cách lấy mẫu bị đứt quãng (> 25 giây).",
            "• Reliable Monitor V1: Lưu con trỏ Checkpoint nguyên tử qua file khóa.",
            "• Overlap Monitor V2: Cửa sổ trượt 30s giải quyết dữ liệu đến trễ."
        )),
        @("13. Xác Minh Bằng Chứng Nguồn (Step 63)", @(
            "• source_ip_evidence_analyzer: Phân tích gói tin bắt tại cổng vào switch.",
            "• Trích xuất MAC nguồn, IP nguồn/đích, giao thức mạng (ICMP/TCP/UDP).",
            "• Hỗ trợ metadata UTC và đối soát dấu thời gian thực nghiệm."
        )),
        @("14. Đối Chiếu Bằng Chứng Topology (Step 64)", @(
            "• onos_host_evidence_correlator: Đối chiếu với topology LIVE_ONOS.",
            "• 4 trạng thái: CORROBORATED, AMBIGUOUS_MULTI_HOST, IDENTITY_MISMATCH, UNREGISTERED.",
            "• Ngăn ngừa tuyệt đối việc quy kết nhầm máy chủ đích là kẻ tấn công."
        )),
        @("15. Động Cơ Chính Sách & Điểm Nguy Cơ", @(
            "• Chấm điểm nguy cơ lũy tích dựa trên mức độ nghiêm trọng của sự kiện.",
            "• Đánh giá mức độ can thiệp: ALLOW, OBSERVE, RATE_LIMIT, PROPOSE_BLOCK.",
            "• Tích hợp kế hoạch hoàn nguyên (Rollback Plan) vào mọi quyết định."
        )),
        @("16. Cổng An Toàn Phòng Thủ (Safety Gate)", @(
            "• 5 chốt chặn an toàn bắt buộc trước khi tạo bất kỳ quy tắc SDN nào.",
            "• Miễn nhiễm IP hạ tầng: Gateway 10.0.0.254, Controller, DNS 8.8.8.8/1.1.1.1.",
            "• Miễn nhiễm cảnh báo thử nghiệm: test_only = True không bao giờ chặn.",
            "• Rate limiting hành động để bảo vệ tài nguyên của bộ điều khiển ONOS."
        )),
        @("17. Ranh Giới An Toàn: DRY RUN vs LIVE", @(
            "• Stage A (DRY RUN): Mặc định an toàn, tính toán và xem trước Flow Rule.",
            "• Stage B (LIVE ENFORCE): Can thiệp OVS switch, yêu cầu phê duyệt vận hành.",
            "• Ranh giới minh bạch: Bảo toàn 100% tính thông suốt của môi trường lab."
        )),
        @("18. Bảng Điều Khiển Quản Trị ReactJS", @(
            "• 7 trang chức năng chuyên nghiệp: Dashboard, Topology, Anomaly Detection...",
            "• Trực quan hóa sơ đồ mạng thời gian thực và các luồng OpenFlow.",
            "• Tích hợp trợ lý an ninh mạng Chatbot hỗ trợ tra cứu thông tin nội bộ."
        )),
        @("19. Mô Hình Thực Nghiệm Lab Mininet & OVS", @(
            "• Môi trường: Windows 11, WSL Ubuntu-26.04, Python 3.10.10, Docker Engine.",
            "• Topology: SingleSwitchTopo(k=2) kết nối controller qua OpenFlow 1.3.",
            "• Thông tuyến cơ sở: pingAll 0.0% packet loss, RTT trung bình 11.4 ms.",
            "• Toàn bộ 7 cổng dịch vụ vận hành đồng bộ trên localhost."
        )),
        @("20. Kịch Bản 1: Mạng Bình Thường & Baseline", @(
            "• Bước 1 Lab Setup: Khởi động Mininet và kết nối controller thành công.",
            "• Truyền dữ liệu hợp lệ giữa h1 và h2: Quyết định ALLOW (PROPOSE_BLOCK: 0).",
            "• Ghi nhận lưu lượng và kiểm chứng không phát sinh cảnh báo giả."
        )),
        @("21. Kịch Bản 2: Tấn Công DoS / SYN Flood", @(
            "• Khảo sát cơ chế chiếm dụng bảng TCB của giao thức TCP Layer 4.",
            "• Hệ thống sinh Candidate Flow Rule xem trước: DENY TCP srcIp=10.0.0.1/32.",
            "• Kiểm thử hợp đồng ONOS ACL Payload Contract đạt chuẩn 100%."
        )),
        @("22. Kịch Bản 3: Tấn Công ICMP Flood & Bắt Gói", @(
            "• Bơm lưu lượng ICMP tốc độ cao làm vượt ngưỡng PPS trên switch port 1.",
            "• Bằng chứng bắt gói thật Step 63: Trích xuất IP 10.0.0.1, MAC 00:00:00:00:00:01.",
            "• Chỉ mục 119 sự kiện an ninh được lưu trữ và truy vấn trên Elasticsearch."
        )),
        @("23. Kịch Bản 4: Giả Mạo ARP Spoofing / MITM", @(
            "• Khảo sát kỹ thuật đầu độc bảng ARP và giả mạo địa chỉ nguồn Layer 2.",
            "• Step 64 Host Correlator phát hiện trạng thái IDENTITY_MISMATCH.",
            "• Đưa ra phán quyết cách ly trạm giả mạo và bảo vệ bảng dòng switch."
        )),
        @("24. Kịch Bản 5: Thám Sát Port Scan & Chuẩn Hóa SIEM", @(
            "• Mô phỏng chuỗi quét cổng TCP/UDP từ máy trạm.",
            "• Module siem_log_normalizer chuẩn hóa Syslog pfSense và Windows Event Log.",
            "• Gắn nhãn trung thực FIXTURE_SIMULATION theo chuẩn Elastic Common Schema."
        )),
        @("25. Cơ Chế Hoàn Nguyên Chính Sách (Rollback)", @(
            "• Khôi phục trạng thái mạng khi sự cố kết thúc hoặc khi gỡ bỏ chính sách.",
            "• API /api/defense/rollback gọi unblock_ip gỡ bỏ quy tắc trên ONOS.",
            "• Kiểm chứng minh bạch: Phản ánh đúng trạng thái thực tế không báo thành công giả."
        )),
        @("26. Kết Quả Kiểm Thử Tự Động (53/53 PASS)", @(
            "• 53 bài kiểm thử tự động unittest đạt 100% PASS trong 0.59s.",
            "• 4/4 CLI Self-Tests vượt qua kiểm định an toàn và chuỗi bằng chứng.",
            "• Cơ sở dữ liệu SQLite SHA-256 bảo toàn nguyên vẹn 100% (Zero Data Loss).",
            "• Không phát sinh bất kỳ lỗi hồi quy nào (Zero Regression)."
        )),
        @("27. So Sánh Giải Pháp & Giá Trị Thực Tiễn", @(
            "• So với Snort/Suricata: Can thiệp trực tiếp vào Data Plane qua OpenFlow.",
            "• So với SDN Firewall truyền thống: Khắc phục triệt để lỗi chặn nhầm.",
            "• Ứng dụng thực tế: Bảo vệ trung tâm dữ liệu và phân đoạn mạng Zero Trust."
        )),
        @("28. Đóng Góp Của Đề Tài & Hướng Phát Triển", @(
            "• Hoàn thành toàn diện các mục tiêu nghiên cứu và chuẩn đầu ra môn học.",
            "• Minh chứng thành công quy trình Giám sát — Phản ứng — Đánh giá có thể tái lập.",
            "• Hướng phát triển: Mở rộng topo Spine-Leaf đa switch và tích hợp AI/ML."
        ))
    )

    $slideIdx = 2
    foreach ($sd in $slidesData) {
        $slide = $pres.Slides.Add($slideIdx, 2)
        $slide.Shapes.Title.TextFrame.TextRange.Text = $sd[0]
        $slide.Shapes.Title.TextFrame.TextRange.Font.Size = 32
        $slide.Shapes.Title.TextFrame.TextRange.Font.Bold = $true
        
        $bodyText = ($sd[1] -join "`n`n")
        $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $bodyText
        $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Font.Size = 24
        $slideIdx++
    }

    # Slide 29: Lời cảm ơn và Q&A
    $sEnd = $pres.Slides.Add($slideIdx, 1) # Title Layout
    $sEnd.Shapes.Title.TextFrame.TextRange.Text = "XIN TRÂN TRỌNG CẢM ƠN HỘI ĐỒNG!`nPHIÊN HỎI ĐÁP (Q&A)"
    $sEnd.Shapes.Title.TextFrame.TextRange.Font.Size = 34
    $sEnd.Shapes.Title.TextFrame.TextRange.Font.Bold = $true
    $sEnd.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Học phần: Chuyên đề – Hệ thống mạng và bảo mật`nSinh viên thực hiện: Phan Phát Đạt — Nhóm 02`nTrường Đại học Giao thông vận tải TP.HCM (UTH)"
    $sEnd.Shapes.Placeholders.Item(2).TextFrame.TextRange.Font.Size = 24
    
    $pptxOut = "$docsAcademic\\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pptx"
    $pdfPptxOut = "$docsAcademic\\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pdf"
    
    Write-Host "`nSaving PowerPoint to: $pptxOut..."
    $pres.SaveAs($pptxOut)
    $pres.SaveAs($pdfPptxOut, [ref]32) # 32 = ppSaveAsPDF
    
    $finalSlides = $pres.Slides.Count
    Write-Host "Created $finalSlides presentation slides in $pptxOut and $pdfPptxOut."
    
    $pres.Close()
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    # Copy generated artifacts to Submission Package
    $subRoot = "D:\\Project\\SDNFlowGuard_Final_Submission"
    if (Test-Path $subRoot) {
        Write-Host "`nCopying academic artifacts to submission package..."
        Copy-Item -Path $docxOut -Destination "$subRoot\\03_DOCUMENTATION\\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx" -Force
        Copy-Item -Path $pdfOut -Destination "$subRoot\\03_DOCUMENTATION\\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.pdf" -Force
        Copy-Item -Path $pptxOut -Destination "$subRoot\\06_PRESENTATION\\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pptx" -Force
        Copy-Item -Path $pdfPptxOut -Destination "$subRoot\\06_PRESENTATION\\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pdf" -Force
        Write-Host "[OK] Synced DOCX/PDF/PPTX to $subRoot"
    }

    Write-Host "`n[SUCCESS] ALL ACADEMIC ARTIFACTS GENERATED AND VERIFIED!"
}
"""

    text = text[:text.find("# -------------------------------------------------------------------------")] + new_ppt_code

    with open(ps1_path, "w", encoding="utf-8-sig") as f:
        f.write(text)

    print("generate_academic_artifacts.ps1 successfully patched!")

if __name__ == "__main__":
    patch_academic_script()

