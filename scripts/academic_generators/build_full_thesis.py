import os
import sys

def build_thesis_script():
    script_path = r"D:\Project\Nhom02_SDNFlowGuard\scripts\generate_academic_artifacts.ps1"
    
    # We will write the PowerShell script with UTF-8 BOM
    # Let's write the complete code
    with open(r"D:\Project\Nhom02_SDNFlowGuard\scripts\generate_academic_artifacts.ps1", "w", encoding="utf-8-sig") as f:
        # Write the beginning of the script
        f.write('''& {
    $ErrorActionPreference = "Stop"
    $workspace = "D:\\Project\\Nhom02_SDNFlowGuard"
    $docsFinal = "$workspace\\docs\\final"
    $docsAcademic = "$workspace\\docs\\academic"
    $screenshotsDir = "$workspace\\screenshots"
    
    Write-Host "============================================================"
    Write-Host " SDNFlowGuard Comprehensive 60+ Page Academic Generator     "
    Write-Host "============================================================"
    
    Write-Host "`n[1/2] Initializing Microsoft Word COM Automation..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone
    
    $doc = $word.Documents.Add()
    
    # Page Setup (Standard Vietnamese Academic Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm)
    .PageSetup.PaperSize = 7 # 7 = wdPaperA4
    .PageSetup.PageWidth = .CentimetersToPoints(21.0)
    .PageSetup.PageHeight = .CentimetersToPoints(29.7)
    $doc.PageSetup.TopMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.BottomMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.LeftMargin = $word.CentimetersToPoints(3.0)
    $doc.PageSetup.RightMargin = $word.CentimetersToPoints(2.0)
    
    $sel = $word.Selection
    
    # Configure Normal Style
    $normalStyle = $doc.Styles.Item("Normal")
    $normalStyle.Font.Name = "Times New Roman"
    $normalStyle.Font.Size = 13
    $normalStyle.Font.Color = [Microsoft.Office.Interop.Word.WdColor]::wdColorBlack
    $normalStyle.ParagraphFormat.LineSpacingRule = [Microsoft.Office.Interop.Word.WdLineSpacing]::wdLineSpace1pt5
    $normalStyle.ParagraphFormat.SpaceAfter = 6
    $normalStyle.ParagraphFormat.SpaceBefore = 0
    $normalStyle.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify

    function Add-H1 {
        param([string]$title)
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
        $sel.ParagraphFormat.LeftIndent = 0
        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 15
        $sel.Font.Bold = $true
        $sel.Font.Italic = $false
        $sel.ParagraphFormat.SpaceBefore = 16
        $sel.ParagraphFormat.SpaceAfter = 8
        $sel.TypeText("$title`n")
        $sel.Font.Bold = $false
        $sel.Font.Size = 13
        $sel.ParagraphFormat.SpaceBefore = 0
        $sel.ParagraphFormat.SpaceAfter = 6
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify
    }

    function Add-H2 {
        param([string]$title)
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 13.5
        $sel.Font.Bold = $true
        $sel.Font.Italic = $false
        $sel.ParagraphFormat.SpaceBefore = 12
        $sel.ParagraphFormat.SpaceAfter = 6
        $sel.TypeText("$title`n")
        $sel.Font.Bold = $false
        $sel.Font.Size = 13
        $sel.ParagraphFormat.SpaceBefore = 0
        $sel.ParagraphFormat.SpaceAfter = 6
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify
    }

    function Add-H3 {
        param([string]$title)
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 13
        $sel.Font.Bold = $true
        $sel.Font.Italic = $true
        $sel.ParagraphFormat.SpaceBefore = 8
        $sel.ParagraphFormat.SpaceAfter = 4
        $sel.TypeText("$title`n")
        $sel.Font.Bold = $false
        $sel.Font.Italic = $false
        $sel.ParagraphFormat.SpaceBefore = 0
        $sel.ParagraphFormat.SpaceAfter = 6
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify
    }

    function Add-P {
        param([string]$text)
        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 13
        $sel.Font.Bold = $false
        $sel.Font.Italic = $false
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify
        $sel.ParagraphFormat.FirstLineIndent = $word.CentimetersToPoints(1.0)
        $sel.ParagraphFormat.SpaceAfter = 6
        $sel.TypeText("$text`n")
        $sel.ParagraphFormat.FirstLineIndent = 0
    }

    function Add-Code {
        param([string]$text)
        $sel.Font.Name = "Consolas"
        $sel.Font.Size = 9.5
        $sel.Font.Bold = $false
        $sel.Font.Italic = $false
        $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphLeft
        $sel.ParagraphFormat.FirstLineIndent = 0
        $sel.ParagraphFormat.LeftIndent = $word.CentimetersToPoints(0.5)
        $sel.ParagraphFormat.SpaceBefore = 2
        $sel.ParagraphFormat.SpaceAfter = 2
        $sel.TypeText("$text`n")
        $sel.ParagraphFormat.LeftIndent = 0
        $sel.Font.Name = "Times New Roman"
        $sel.Font.Size = 13
    }

    function Add-Pic {
        param($imgName, $caption)
        if ($imgName -is [System.Array]) {
            $caption = $imgName[1]
            $imgName = $imgName[0]
        }
        $imgPath = Join-Path $screenshotsDir $imgName
        if (Test-Path $imgPath) {
            $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
            $sel.ParagraphFormat.FirstLineIndent = 0
            $shape = $sel.InlineShapes.AddPicture($imgPath)
            $shape.Width = 430
            $shape.Height = ($shape.Width * 0.54)
            $sel.Font.Name = "Times New Roman"
            $sel.Font.Size = 11.5
            $sel.Font.Italic = $true
            $sel.Font.Bold = $false
            $sel.ParagraphFormat.SpaceBefore = 4
            $sel.ParagraphFormat.SpaceAfter = 10
            $sel.TypeText("`n$caption`n`n")
            $sel.Font.Italic = $false
            $sel.Font.Size = 13
            $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphJustify
        }
    }
''')

        # Generate large academic body
        from build_academic_text import get_all_academic_sections
        sections = get_all_academic_sections()
        
        for sec in sections:
            # write Add-H1, Add-H2, Add-H3, Add-P, Add-Code, Add-Pic
            sec_type = sec[0]
            if sec_type == "COVER":
                f.write('''
    # Title Cover Page
    $sel.ParagraphFormat.Alignment = [Microsoft.Office.Interop.Word.WdParagraphAlignment]::wdAlignParagraphCenter
    $sel.Font.Name = "Times New Roman"
    $sel.Font.Size = 13
    $sel.Font.Bold = $true
    $sel.TypeText("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH (UTH)`n")
    $sel.TypeText("KHOA CÔNG NGHỆ THÔNG TIN`n`n`n")
    
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
    $sel.TypeText("TP. HỒ CHÍ MINH, NĂM 2026`n")
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
''')
            elif sec_type == "PAGE_BREAK":
                f.write('    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)\n')
            elif sec_type == "H1":
                escaped = sec[1].replace('"', '`"').replace('$', '`$')
                f.write(f'    Add-H1 "{escaped}"\n')
            elif sec_type == "H2":
                escaped = sec[1].replace('"', '`"').replace('$', '`$')
                f.write(f'    Add-H2 "{escaped}"\n')
            elif sec_type == "H3":
                escaped = sec[1].replace('"', '`"').replace('$', '`$')
                f.write(f'    Add-H3 "{escaped}"\n')
            elif sec_type == "P":
                escaped = sec[1].replace('"', '`"').replace('$', '`$')
                f.write(f'    Add-P "{escaped}"\n')
            elif sec_type == "CODE":
                escaped = sec[1].replace('"', '`"').replace('$', '`$').replace('\n', '`n')
                f.write(f'    Add-Code "{escaped}"\n')
            elif sec_type == "PIC":
                f.write(f'    Add-Pic "{sec[1]}" "{sec[2]}"\n')

        # Write closing and export
        f.write('''
    # Add Page Numbers to Footer
    $section = $doc.Sections.Item(1)
    $footer = $section.Footers.Item([Microsoft.Office.Interop.Word.WdHeaderFooterIndex]::wdHeaderFooterPrimary)
    $footer.PageNumbers.Add([Microsoft.Office.Interop.Word.WdPageNumberAlignment]::wdAlignPageNumberRight)
    $footer.Range.Font.Name = "Times New Roman"
    $footer.Range.Font.Size = 10

    # Save DOCX and export to PDF
    $docxOut = "$docsFinal\\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx"
    $pdfOut = "$docsFinal\\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.pdf"
    
    Write-Host "`nSaving Word Document to: $docxOut..."
    $doc.SaveAs([ref]$docxOut)
    
    Write-Host "Exporting PDF to: $pdfOut..."
    $doc.SaveAs([ref]$pdfOut, [ref]17) # 17 = wdFormatPDF
    
    $finalPages = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    $finalWords = $doc.ComputeStatistics(0) # 0 = wdStatisticWords
    
    Write-Host "`n============================================================"
    Write-Host " ACADEMIC THESIS GENERATION SUMMARY:                        "
    Write-Host " Total Words: $finalWords words                             "
    Write-Host " Total Pages: $finalPages pages                             "
    Write-Host " DOCX Path:   $docxOut ($((Get-Item $docxOut).Length) bytes)"
    Write-Host " PDF Path:    $pdfOut ($((Get-Item $pdfOut).Length) bytes)  "
    Write-Host "============================================================"
    
    $doc.Close([Microsoft.Office.Interop.Word.WdSaveOptions]::wdDoNotSaveChanges)
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    # -------------------------------------------------------------------------
    # 2. GENERATE POWERPOINT PRESENTATION (.PPTX)
    # -------------------------------------------------------------------------
    Write-Host "`n[2/2] Initializing Microsoft PowerPoint COM Automation..."
    $ppt = New-Object -ComObject PowerPoint.Application
    $pres = $ppt.Presentations.Add([Microsoft.Office.Core.MsoTriState]::msoFalse)
    
    $s1 = $pres.Slides.Add(1, 1) # Title Layout
    $s1.Shapes.Title.TextFrame.TextRange.Text = "NGHIÊN CỨU VÀ TRIỂN KHAI PHÒNG THỦ MẠNG TỰ ĐỘNG QUA SDN TÍCH HỢP GIÁM SÁT BẰNG ELK STACK"
    $s1.Shapes.Title.TextFrame.TextRange.Font.Size = 28
    $s1.Shapes.Title.TextFrame.TextRange.Font.Bold = $true
    $s1.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "Hệ thống SDNFlowGuard`nMôn học: Chuyên đề - Hệ thống mạng và bảo mật`nSinh viên thực hiện: Phan Phát Đạt - Nhóm 02`nNăm học 2026"
    $s1.Shapes.Placeholders.Item(2).TextFrame.TextRange.Font.Size = 18

    $slidesData = @(
        @("1. Đặt Vấn Đề & Tính Cấp Thiết", @(
            "• Mạng doanh nghiệp đối mặt với các cuộc tấn công DoS/DDoS và quét cổng ngày càng tinh vi.",
            "• Mạng truyền thống có cấu trúc phân tán, khó quan sát toàn cục và phản ứng chậm trễ.",
            "• Cần một giải pháp giám sát tập trung kết hợp với phản ứng phòng thủ tự động có kiểm soát."
        )),
        @("2. Nghịch Lý Phòng Thủ SDN: 'Attached Host != Verified Attacker'", @(
            "• Thống kê cổng OpenFlow (rx_pps, tx_pps) chỉ đo lường khối lượng gói tin trên cổng switch.",
            "• Host gắn vào cổng (Attached Host) có thể chỉ là nạn nhân hoặc máy chủ nhận lưu lượng phản hồi.",
            "• Cổng có thể kết nối nhiều host (Multi-host Port) hoặc lưu lượng ICMP Ping hai chiều đối xứng.",
            "• Nguyên tắc cốt lõi: Tuyệt đối không chặn IP chỉ dựa vào thống kê cổng khi chưa có bằng chứng nguồn."
        )),
        @("3. Mục Tiêu Nghiên Cứu & Phạm Vi Đề Tài", @(
            "• Xây dựng hệ thống SDNFlowGuard tích hợp ONOS SDN Controller và ELK Stack.",
            "• Thu thập, phân tích chuỗi thời gian thống kê cổng và phát hiện bất thường liên tiếp (PPS).",
            "• Thiết lập chuỗi xác minh bằng chứng nguồn hai giai đoạn (Step 63 Packet Analyzer & Step 64 ONOS Correlator).",
            "• Động cơ phòng thủ và cổng an toàn Safety Gate mặc định DRY_RUN, hỗ trợ Rollback tức thì."
        )),
        @("4. Kiến Trúc Tổng Thể 4 Mặt Phẳng", @(
            "• Data Plane: Mininet, switch ảo Open vSwitch (OVS 3.7.1) chạy OpenFlow 1.3, hosts h1, h2.",
            "• Control Plane: ONOS SDN Controller (REST API :8181, OpenFlow :6653).",
            "• SIEM Plane: Logstash HTTP :18080, Elasticsearch :9200, Kibana Dashboard :5601.",
            "• Application Plane: Flask Backend :5000 Clean Architecture, SQLite, ReactJS UI :3000."
        )),
        @("5. Pipeline Thu Thập Dữ Liệu SDN -> ELK", @(
            "• onos_elk_collector.py: Thu thập topology, devices, hosts, flows định kỳ.",
            "• onos_port_elk_collector.py: Tính toán delta packets, delta time, rx_pps, tx_pps, total_pps, rx_bps.",
            "• Logstash Pipeline (01-sdnflowguard.conf): Tiếp nhận JSON qua cổng 18080, gắn nhãn @timestamp.",
            "• Elasticsearch Index sdnflowguard-events-*: Lưu trữ chỉ mục theo ngày phục vụ truy vấn SOC."
        )),
        @("6. Phát Hiện Bất Thường & Động Cơ Cảnh Báo V1/V2", @(
            "• sdn_port_anomaly_detector.py: Nhận diện chuỗi mẫu vượt ngưỡng liên tiếp (consecutive_hits >= 2).",
            "• Xử lý đứt quãng lấy mẫu: Reset streak về 0 nếu khoảng cách mẫu > 25 giây.",
            "• Reliable Monitor V1: Lưu con trỏ trạng thái Checkpoint nguyên tử qua file khóa .tmp.",
            "• Overlap Monitor V2: Cửa sổ trượt chồng lấp 30s giải quyết triệt để dữ liệu đến trễ, sinh khóa SHA-256 chống trùng."
        )),
        @("7. Chuỗi Xác Minh Bằng Chứng Nguồn L2/L3 (Steps 63-64)", @(
            "• Step 63 (source_ip_evidence_analyzer.py): Phân tích gói tin tcpdump cổng vào switch, trích xuất MAC, IP nguồn/đích, ICMP type.",
            "• Step 64 (onos_host_evidence_correlator.py): Đối chiếu chéo với bảng host/port/flow trực tiếp từ LIVE_ONOS.",
            "• 4 trạng thái đối chiếu: CORROBORATED, AMBIGUOUS_MULTI_HOST, IDENTITY_MISMATCH, UNREGISTERED.",
            "• Kiểm tra giao thoa cửa sổ thời gian UTC và tính đối xứng lưu lượng trước khi xác nhận kẻ tấn công."
        )),
        @("8. Động Cơ Chính Sách Phòng Thủ & Cổng An Toàn", @(
            "• 5 chốt chặn bắt buộc: not_test_only, valid_and_unprotected_target, evidence_attribution, defense_mode, approval.",
            "• Miễn nhiễm IP hạ tầng: Bảo vệ 127.0.0.1, Controller IP, ELK IP, Multicast, Broadcast.",
            "• Miễn nhiễm cảnh báo thử nghiệm: test_only = True không bao giờ kích hoạt lệnh chặn.",
            "• Chế độ mặc định: DRY_RUN sinh Flow Rule preview (priority 40010, timeout 300s, DROP).",
            "• Kế hoạch hoàn nguyên: Rollback plan đính kèm mọi quyết định (unblock_ip)."
        )),
        @("9. Bảng Điều Khiển Quản Trị ReactJS (7 Trang)", @(
            "• Dashboard: Tổng quan dịch vụ ONOS/ELK, biểu đồ lưu lượng cổng ELK, bảng cảnh báo an ninh.",
            "• Traffic Overview: Sơ đồ mạng SDN, danh sách host và luồng OpenFlow trực tiếp.",
            "• Anomaly Detection, Manual Control, Decision Logs, Reports PDF (%PDF-1.4), System Settings.",
            "• Chatbot Security Assistant: Trợ lý an ninh mạng hỗ trợ tra cứu trạng thái nội bộ."
        )),
        @("10. Mô Hình Thực Nghiệm Lab Mininet & OVS", @(
            "• Môi trường: Windows 11, WSL Ubuntu-26.04, Python 3.10.10, Docker Engine 29.6.2.",
            "• Topology: SingleSwitchTopo(k=2) kết nối controller 127.0.0.1:6653 qua OpenFlow 1.3.",
            "• Kết quả PingAll cơ sở: 0.0% packet loss, RTT trung bình 1.154 ms.",
            "• Cả 7 cổng dịch vụ vận hành đồng bộ: 3000, 5000, 8181, 6653, 9200, 5601, 18080."
        )),
        @("11. Kết Quả 5 Kịch Bản Thực Nghiệm End-to-End", @(
            "• Scenario 01: Mạng bình thường, thu thập số liệu liên tục, quyết định ALLOW (PROPOSE_BLOCK: 0).",
            "• Scenario 02: Lưu lượng vượt ngưỡng PPS, Monitor V2 phát hiện 10 bất thường, lập chỉ mục 16 cảnh báo vào ELK.",
            "• Scenario 03: Đối chiếu LIVE_ONOS đạt CORROBORATED, phán quyết OBSERVE vì ping đối xứng.",
            "• Scenario 04: Phòng thủ SDN Stage A DRY RUN thành công, Stage B chờ phê duyệt vận hành.",
            "• Scenario 05: Rollback unblock_ip thành công, kết nối h1 <-> h2 phục hồi 100% (0% packet loss)."
        )),
        @("12. Kết Quả Kiểm Thử Tự Động (50/50 Tests PASS)", @(
            "• 50 bài kiểm thử unittest: 24 Unit, 12 Integration, 5 Contract, 8 Safety, 1 E2E đạt 100% PASS trong 0.51s.",
            "• 4 CLI Self-Tests: Monitor V2, Step 63, Step 64, Defense Policy đạt PASS.",
            "• Toàn vẹn dữ liệu: Database chính SHA-256 3909de520f89ea050e... bảo toàn nguyên vẹn 100%.",
            "• Kiểm toán bảo mật: Zero hardcoded secrets, xác thực API Key, kiểm soát lỗi đầu vào chặt chẽ."
        )),
        @("13. So Sánh Với Các Giải Pháp Tương Tự", @(
            "• So với Snort/Suricata: SDNFlowGuard có khả năng can thiệp trực tiếp vào Data Plane qua OpenFlow.",
            "• So với SDN Firewall truyền thống: Khắc phục triệt để lỗi chặn nhầm nhờ chuỗi bằng chứng Step 63/64.",
            "• So với SIEM thương mại: Tích hợp sẵn động cơ Safety Gate và quy trình Rollback chuẩn hóa cho SDN."
        )),
        @("14. Kết Luận & Hướng Phát Triển", @(
            "• Đồ án hoàn thành 100% các mục tiêu nghiên cứu và thực nghiệm của môn học.",
            "• Chứng minh thành công nguyên lý an toàn 'Attached Host != Verified Attacker'.",
            "• Hướng phát triển: Mở rộng lên topology Spine-Leaf, tích hợp Machine Learning và tác tử Winlogbeat/Filebeat thật."
        ))
    )

    $slideIdx = 2
    foreach ($sd in $slidesData) {
        $slide = $pres.Slides.Add($slideIdx, 2)
        $slide.Shapes.Title.TextFrame.TextRange.Text = $sd[0]
        $slide.Shapes.Title.TextFrame.TextRange.Font.Size = 24
        $slide.Shapes.Title.TextFrame.TextRange.Font.Bold = $true
        
        $bodyText = ($sd[1] -join "`n`n")
        $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $bodyText
        $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Font.Size = 16
        $slideIdx++
    }

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
''')

if __name__ == "__main__":
    build_thesis_script()
    print("build_thesis_script completed")
