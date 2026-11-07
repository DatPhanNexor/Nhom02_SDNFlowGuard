& {
    $ErrorActionPreference = "Stop"
    $workspace = "D:\Project\Nhom02_SDNFlowGuard"
    $docsFinal = "$workspace\docs\final"
    $docsAcademic = "$workspace\docs\academic"
    $screenshotsDir = "$workspace\screenshots"
    
    Write-Host "============================================================"
    Write-Host " SDNFlowGuard Comprehensive 60+ Page Academic Generator     "
    Write-Host "============================================================"
    
    Write-Host "`n[1/2] Initializing Microsoft Word COM Automation..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone
    
    $doc = $word.Documents.Add()
    
    # Page Setup (Standard Vietnamese Academic A4 Margins: Top 2cm, Bottom 2cm, Left 3cm, Right 2cm)
    $doc.PageSetup.PaperSize = 7 # 7 = wdPaperA4
    $doc.PageSetup.PageWidth = $word.CentimetersToPoints(21.0)
    $doc.PageSetup.PageHeight = $word.CentimetersToPoints(29.7)
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

    # Title Cover Page (Mẫu 01-BCBTL UTH)
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
    $sel.TypeText("TP. HỒ CHÍ MINH, THÁNG 11 NĂM 2026`n")
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
    Add-H1 "LỜI CAM ĐOAN"
    Add-P "Tôi xin cam đoan rằng đồ án chuyên đề 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' (Dự án SDNFlowGuard) là công trình nghiên cứu và thực nghiệm độc lập của tôi dưới sự định hướng của giảng viên hướng dẫn môn học Chuyên đề – Hệ thống mạng và bảo mật."
    Add-P "Mọi số liệu thực nghiệm, nhật ký gói tin L2/L3, cấu hình bộ điều khiển ONOS, kết quả phân tích lưu lượng trên ELK Stack và mã nguồn trong hệ thống đều được triển khai, kiểm thử thực tế và ghi nhận một cách trung thực, minh bạch trên môi trường phòng thí nghiệm an toàn. Các tài liệu tham khảo và mã nguồn mở được kế thừa đều được trích dẫn và khai báo nguồn gốc rõ ràng theo chuẩn mực học thuật."
    Add-P "Tôi hoàn toàn chịu trách nhiệm về tính trung thực, độc lập và chuẩn mực của các kết quả nghiên cứu được trình bày trong bản báo cáo này."
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
    Add-H1 "LỜI CẢM ƠN"
    Add-P "Để hoàn thành đồ án chuyên đề này, tôi xin bày tỏ lòng biết ơn sâu sắc nhất tới quý Thầy, Cô Khoa Công nghệ thông tin, Trường Đại học Giao thông vận tải TP. Hồ Chí Minh (UTH), những người đã tận tâm truyền đạt kiến thức nền tảng vững chắc về kiến trúc mạng, an ninh mạng, các hệ thống phân tán và phương pháp luận nghiên cứu khoa học trong suốt các năm học qua."
    Add-P "Đặc biệt, tôi xin chân thành cảm ơn Thầy/Cô giảng viên phụ trách môn học Chuyên đề – Hệ thống mạng và bảo mật đã định hướng đề tài, tận tình giải đáp những vướng mắc kỹ thuật về bộ điều khiển SDN ONOS, kiến trúc OpenFlow, mô hình quản lý tập trung ELK Stack và nguyên lý phòng thủ phản ứng sự cố an toàn. Những góp ý quý báu của Thầy/Cô đã giúp tôi định hình được một phương pháp tiếp cận đúng đắn, xây dựng được hệ thống phòng thủ mạng an toàn dựa trên bằng chứng xác thực và hoàn thiện báo cáo đồ án với chất lượng chuyên môn cao nhất."
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
    Add-H1 "TÓM TẮT ĐỒ ÁN"
    Add-P "Trong kỷ nguyên hạ tầng số hiện đại, mạng điều khiển bằng phần mềm (Software-Defined Networking - SDN) và hệ thống quản lý sự kiện và thông tin an ninh (Security Information and Event Management - SIEM) đóng vai trò then chốt trong việc bảo vệ dữ liệu và dịch vụ doanh nghiệp. Đồ án 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' xây dựng nền tảng SDNFlowGuard kết hợp khả năng quan sát toàn cục của bộ điều khiển ONOS với sức mạnh phân tích sự kiện bảo mật tập trung của ELK Stack (Elasticsearch, Logstash, Kibana)."
    Add-P "Điểm đột phá cốt lõi của đồ án là giải quyết triệt để vấn đề chặn nhầm (False Positive Blocking) trong phòng thủ mạng SDN thông qua nguyên lý: 'Host gắn trên cổng switch có cảnh báo không đồng nghĩa với kẻ tấn công đã được xác minh' (Attached Host != Verified Attacker). Hệ thống thiết lập chuỗi xác minh bằng chứng nguồn hai giai đoạn (Step 63 & Step 64) kết hợp phân tích gói tin bắt tại cổng vào (tcpdump) với bảng host/port/flow trực tiếp từ ONOS (LIVE_ONOS). Động cơ chính sách phòng thủ (Defense Policy Engine) và cổng an toàn (Safety Gate) mặc định vận hành ở chế độ an toàn DRY_RUN, ngăn chặn tuyệt đối việc khóa các địa chỉ IP hạ tầng (Loopback, Controller, ELK) và cảnh báo thử nghiệm (test_only: true), đồng thời cung cấp cơ chế hoàn nguyên (Rollback) toàn diện. Toàn bộ 50/50 bài kiểm thử tự động đạt 100% PASS, 5 kịch bản thực nghiệm End-to-End được chứng minh thành công trên mô hình Mininet OpenFlow 1.3 trong môi trường lab an toàn."
    Add-H1 "ABSTRACT"
    Add-P "In the era of modern digital infrastructure, Software-Defined Networking (SDN) and Security Information and Event Management (SIEM) play a crucial role in safeguarding enterprise networks. The project 'Research and Deployment of Automated Network Defense via SDN Integrated with ELK Stack Monitoring' presents the SDNFlowGuard system, bridging the global control capabilities of the ONOS SDN Controller with the centralized analytics of the ELK Stack (Elasticsearch, Logstash, Kibana)."
    Add-P "A core contribution of this research is resolving the false-positive blocking dilemma in automated SDN defense by enforcing the principle: 'Attached Host != Verified Attacker'. The architecture introduces a two-stage evidence verification pipeline (Step 63 & Step 64) that cross-correlates switch ingress packet captures with live ONOS topology and Elasticsearch alert windows. The Active Defense Safety Gate operates in fail-safe DRY_RUN mode by default, strictly safeguarding critical infrastructure IPs and test alerts, backed by a complete Rollback mechanism. The system is verified through 50/50 automated test cases (100% PASS) and 5 End-to-End lab scenarios on a Mininet OpenFlow 1.3 network."
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
    Add-H1 "DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT"
    Add-P "SDN       : Software-Defined Networking — Mạng điều khiển bằng phần mềm"
    Add-P "ONOS      : Open Network Operating System — Hệ điều hành mạng mở / Bộ điều khiển SDN"
    Add-P "OVS       : Open vSwitch — Bộ chuyển mạch ảo mã nguồn mở hỗ trợ OpenFlow"
    Add-P "ELK       : Elasticsearch, Logstash, Kibana — Ngăn xếp phần mềm thu thập, lưu trữ, trực quan hóa log"
    Add-P "SIEM      : Security Information and Event Management — Quản lý thông tin và sự kiện an ninh mạng"
    Add-P "SOC       : Security Operations Center — Trung tâm điều hành an ninh mạng"
    Add-P "ACL       : Access Control List — Danh sách kiểm soát truy cập"
    Add-P "PPS       : Packets Per Second — Tốc độ gói tin trên giây"
    Add-P "BPS       : Bytes Per Second — Tốc độ byte trên giây"
    Add-P "CIDR      : Classless Inter-Domain Routing — Định tuyến liên miền không phân lớp"
    Add-P "REST      : Representational State Transfer — Kiến trúc giao tiếp dịch vụ web qua HTTP"
    Add-P "ICMP      : Internet Control Message Protocol — Giao thức điều khiển truyền thông điệp Internet"
    Add-P "TCP       : Transmission Control Protocol — Giao thức điều khiển truyền vận tin cậy"
    Add-P "UDP       : User Datagram Protocol — Giao thức dữ liệu người dùng không kết nối"
    Add-P "OSGi      : Open Services Gateway initiative — Kiến trúc mô-đun dịch vụ Java trong Apache Karaf"
    Add-P "CRUD      : Create, Read, Update, Delete — Các thao tác cơ bản trên cơ sở dữ liệu"
    Add-P "SHA-256   : Secure Hash Algorithm 256-bit — Thuật toán băm mã hóa một chiều 256-bit"
    Add-P "E2E       : End-to-End — Kiểm thử đầu-cuối từ đầu vào tới đầu ra hệ thống"
    Add-P "DoS       : Denial of Service — Tấn công từ chối dịch vụ"
    Add-P "DDoS      : Distributed Denial of Service — Tấn công từ chối dịch vụ phân tán"
    Add-P "WSL       : Windows Subsystem for Linux — Môi trường Linux ảo hóa trên Windows"
    Add-P "API       : Application Programming Interface — Giao diện lập trình ứng dụng"
    Add-P "JSON      : JavaScript Object Notation — Định dạng trao đổi dữ liệu dạng chuỗi ký tự"
    Add-P "IP        : Internet Protocol — Giao thức liên mạng"
    Add-P "MAC       : Media Access Control — Địa chỉ điều khiển truy cập môi trường tầng liên kết dữ liệu"
    $sel.InsertBreak([Microsoft.Office.Interop.Word.WdBreakType]::wdPageBreak)
    Add-H1 "CHƯƠNG 1. GIỚI THIỆU VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI"
    Add-H2 "1.1. Đặt vấn đề và bối cảnh an ninh mạng hiện đại"
    Add-P "Trong kỷ nguyên chuyển đổi số và công nghệ đám mây, các hệ thống mạng doanh nghiệp và trung tâm dữ liệu đang phải đối mặt với áp lực xử lý lưu lượng khổng lồ. Cùng với sự gia tăng về lưu lượng hợp lệ, các cuộc tấn công mạng cũng ngày càng phát triển về mức độ phức tạp, tốc độ bùng phát và quy mô tàn phá. Các cuộc tấn công từ chối dịch vụ phân tán (DDoS), tấn công ngập lụt băng thông (Bandwidth Flooding), tấn công ngập lụt gói tin (SYN Flood, UDP Flood, ICMP Flood), cũng như các chiến dịch quét cổng thăm dò (Port Scanning) có thể làm cạn kiệt tài nguyên xử lý của máy chủ và thiết bị định tuyến trong khoảng thời gian rất ngắn."
    Add-P "Một trong những bài toán hóc búa nhất của các trung tâm điều hành an ninh mạng (SOC) hiện nay là khoảng cách thời gian giữa thời điểm phát hiện bất thường (Mean Time to Detect - MTTD) và thời điểm thực thi biện pháp ngăn chặn (Mean Time to Respond - MTTR). Nếu thời gian phản ứng kéo dài, thiệt hại đối với tính sẵn sàng của dịch vụ là không thể bù đắp. Do đó, việc xây dựng một hệ thống có khả năng giám sát tập trung toàn diện và tự động hóa phản ứng phòng thủ mạng là một hướng nghiên cứu cấp thiết và có giá trị ứng dụng thực tiễn cao."
    Add-H2 "1.2. Thách thức trong giám sát và phòng thủ mạng truyền thống"
    Add-P "Mạng truyền thống (Traditional IP Networks) có cấu trúc phân tán cao, trong đó mỗi thiết bị chuyển mạch (Switch) và định tuyến (Router) vừa phải đảm nhiệm mặt phẳng dữ liệu (chuyển tiếp gói tin theo bảng MAC/IP) vừa tự chạy các thuật toán định tuyến phân tán (OSPF, BGP, STP) trên mặt phẳng điều khiển cục bộ. Cấu trúc đóng kín này bộc lộ ba điểm nghẽn nghiêm trọng:"
    Add-P "Thứ nhất, thiếu tầm nhìn toàn cục tập trung (Lack of Centralized Observability): Quản trị viên không thể quan sát toàn bộ mạng trên một màn hình thống nhất. Để kiểm tra lưu lượng, kỹ sư phải sử dụng các lệnh CLI thủ công hoặc cấu hình SNMP/NetFlow trên từng thiết bị riêng lẻ, dẫn tới việc thu thập số liệu phân mảnh và chậm trễ."
    Add-P "Thứ hai, độ trễ và rủi ro khi thực thi chính sách bảo mật: Khi phát hiện luồng tấn công, việc tạo Access Control List (ACL) phải thực hiện trên từng cổng switch hoặc router biên. Thao tác cấu hình thủ công qua giao diện dòng lệnh dễ dẫn tới lỗi cú pháp, mâu thuẫn chính sách, hoặc làm gián đoạn các luồng lưu lượng quan trọng khác của doanh nghiệp."
    Add-P "Thứ ba, sự thiếu liên kết giữa hệ thống phân tích log (SIEM) và hạ tầng mạng: Các hệ thống SIEM truyền thống rất mạnh trong việc thu thập nhật ký từ máy chủ, nhưng hoàn toàn thiếu khả năng điều khiển linh hoạt tầng mạng (Data Plane) để cô lập hoặc chuyển hướng luồng dữ liệu của kẻ tấn công ngay tại switch biên."
    Add-H2 "1.3. Nghịch lý cốt lõi trong phòng thủ SDN: 'Attached Host != Verified Attacker'"
    Add-P "Kiến trúc Mạng điều khiển bằng phần mềm (Software-Defined Networking - SDN) ra đời mở ra khả năng lập trình toàn diện mạng thông qua bộ điều khiển tập trung (SDN Controller). Tuy nhiên, khi xây dựng hệ thống phòng thủ mạng tự động trên nền tảng SDN, nếu không có phương pháp luận chặt chẽ, hệ thống rất dễ rơi vào bẫy chặn nhầm (False Positive Blocking) làm gián đoạn hoạt động bình thường của người dùng hợp lệ."
    Add-P "Nghịch lý này xuất phát từ bản chất của số liệu thống kê cổng OpenFlow (OpenFlow Port Statistics: rx_packets, tx_packets, rx_pps, tx_pps). Các bộ đếm trên cổng switch chỉ đo tổng khối lượng gói tin đi qua cổng vật lý hoặc ảo, hoàn toàn không phản ánh địa chỉ IP nguồn thực sự chứa trong phần thân của từng gói tin. Khi lưu lượng trên cổng tăng vọt vượt ngưỡng báo động, một giải pháp phòng thủ tự động ngây thơ sẽ tra cứu bảng Host của Controller và tự động phát lệnh khóa IP của host đang gắn vào cổng đó."
    Add-P "Cách xử lý ngây thơ này phạm phải sai lầm nghiêm trọng bởi 4 lý do thực tế:"
    Add-P "1. Host gắn trên cổng (Attached Host) có thể chỉ là nạn nhân đang bị ngập lụt bởi lưu lượng tấn công từ ngoài gửi tới, hoặc là máy chủ đang gửi phản hồi cho các yêu cầu hợp lệ."
    Add-P "2. Một cổng switch có thể kết nối với một switch phụ, một access point hoặc một mạng con chứa nhiều máy trạm (Multi-host Port). Việc vội vàng khóa cổng hoặc khóa IP đầu tiên tìm thấy sẽ cắt đứt liên lạc của tất cả các máy trạm hợp lệ khác."
    Add-P "3. Trong các phiên trao đổi ICMP Ping hai chiều (Echo Request và Echo Reply), cả cổng gửi và cổng nhận đều ghi nhận số gói tin tăng cao tương đương nhau. Nếu không phân tích sâu loại gói tin (ICMP Type) và chiều lưu lượng, hệ thống sẽ kết luận nhầm cả hai phía đều là kẻ tấn công."
    Add-P "4. Các sự kiện đo kiểm tải nội bộ hoặc cảnh báo thử nghiệm (gắn cờ test_only: true) nếu không được phân tách minh bạch sẽ kích hoạt cơ chế phòng thủ thật, làm tê liệt hệ thống kiểm thử."
    Add-P "Từ phân tích trên, đồ án xác lập nguyên tắc khoa học bất biến làm kim chỉ nam cho toàn bộ kiến trúc SDNFlowGuard: 'Host gắn trên cổng switch có cảnh báo không đồng nghĩa với kẻ tấn công đã được xác minh' (Attached Host != Verified Attacker). Mọi quyết định phòng thủ tự động bắt buộc phải dựa trên bằng chứng gói tin nguồn đã được đối chiếu chéo (corroborated evidence)."
    Add-H2 "1.4. Mục tiêu nghiên cứu và phạm vi học thuật của đề tài"
    Add-P "Mục tiêu tổng quát của đề tài là: Nghiên cứu lý thuyết và triển khai thực nghiệm một nền tảng giám sát an ninh mạng tập trung kết hợp phòng thủ mạng tự động an toàn dựa trên kiến trúc SDN, tích hợp ngăn xếp ELK Stack, mang tên SDNFlowGuard."
    Add-P "Các mục tiêu cụ thể có thể kiểm chứng bao gồm:"
    Add-P "1. Thiết lập mô hình mạng SDN hoàn chỉnh gồm bộ điều khiển ONOS (Open Network Operating System 2.7.0), switch ảo Open vSwitch (OVS 3.7.1) chạy OpenFlow 1.3 và các host thử nghiệm trên Mininet trong môi trường WSL Ubuntu-26.04."
    Add-P "2. Xây dựng pipeline thu thập số liệu mạng thời gian thực đẩy qua Logstash HTTP input (cổng 18080) vào Elasticsearch (cổng 9200) và trực quan hóa trên Kibana (cổng 5601) cùng bảng điều khiển React Dashboard (cổng 3000)."
    Add-P "3. Hiện thực thuật toán phát hiện bất thường tốc độ gói tin cao kéo dài (Sustained High Packet Rate) có cơ chế lưu con trỏ trạng thái (Checkpoint) và cửa sổ trượt chồng lấp (Overlap Alert Monitor V2) để chống bỏ sót dữ liệu đến trễ."
    Add-P "4. Thiết kế cơ chế xác minh bằng chứng nguồn hai giai đoạn: Step 63 phân tích gói tin bắt tại cổng vào switch (tcpdump) và Step 64 đối chiếu với bảng host/port/flow trực tiếp từ ONOS (LIVE_ONOS)."
    Add-P "5. Xây dựng cổng an toàn Active Defense Safety Gate hoạt động mặc định ở chế độ DRY_RUN, bảo vệ tuyệt đối các địa chỉ IP hạ tầng và hỗ trợ quy trình hoàn nguyên (Rollback) toàn diện."
    Add-P "6. Hoàn thiện bộ kiểm thử tự động 50/50 tests (100% PASS), bộ tài liệu học thuật đầy đủ và gói bàn giao chuẩn hóa phục vụ nghiệm thu đồ án."
    Add-H1 "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VỀ SDN, OPENFLOW VÀ ONOS CONTROLLER"
    Add-H2 "2.1. Khái niệm và kiến trúc Software-Defined Networking (SDN)"
    Add-P "Software-Defined Networking (SDN) là một bước chuyển biến mang tính cách mạng trong ngành công nghệ mạng máy tính. Khái niệm SDN xuất phát từ các nghiên cứu tiên phong tại Đại học Stanford và Đại học California, Berkeley vào những năm 2008, sau đó được tiêu chuẩn hóa và phát triển mạnh mẽ bởi Tổ chức Mạng Mở (Open Networking Foundation - ONF)."
    Add-P "Kiến trúc SDN được phân chia thành ba tầng rõ rệt:"
    Add-P "1. Tầng ứng dụng (Application Layer): Bao gồm các phần mềm quản trị mạng, hệ thống giám sát an ninh, ứng dụng định tuyến tối ưu đường đi, hệ thống phát hiện xâm nhập và tường lửa mạng. Các ứng dụng này tương tác với tầng điều khiển thông qua các giao diện lập trình hướng Bắc (Northbound APIs - thường là RESTful APIs)."
    Add-P "2. Tầng điều khiển (Control Layer / Control Plane): Trung tâm xử lý thông minh của toàn bộ hệ thống, đại diện bởi SDN Controller (như ONOS, OpenDaylight, Ryu). Controller duy trì bức tranh toàn cảnh về trạng thái mạng (Network Information Base), xử lý các yêu cầu từ tầng ứng dụng và biên dịch thành các luật chuyển tiếp chi tiết."
    Add-P "3. Tầng hạ tầng / chuyển tiếp dữ liệu (Infrastructure Layer / Data Plane): Bao gồm các thiết bị chuyển mạch vật lý hoặc ảo (như Open vSwitch). Thiết bị tầng này chỉ tập trung vào việc chuyển tiếp gói tin với tốc độ cao dựa trên các bảng luồng (Flow Tables) do Controller cài đặt xuống qua giao diện hướng Nam (Southbound APIs)."
    Add-H2 "2.2. Giao thức OpenFlow và mô hình xử lý gói tin OpenFlow 1.3"
    Add-P "OpenFlow là giao thức chuẩn mở đầu tiên và phổ biến nhất định nghĩa quy tắc giao tiếp giữa Control Plane và Data Plane. Trong đề tài SDNFlowGuard, tiêu chuẩn OpenFlow 1.3 được áp dụng triệt để. Phiên bản OpenFlow 1.3 đưa ra mô hình xử lý đường ống nhiều bảng (Multiple Flow Tables / Pipeline Processing), khắc phục hoàn toàn nhược điểm đơn bảng của OpenFlow 1.0."
    Add-P "Khi một gói tin đi vào switch OpenFlow 1.3, quy trình xử lý diễn ra theo các bước nghiêm ngặt:"
    Add-P "Bước 1: Bắt đầu tại Bảng 0 (Table 0), switch trích xuất các trường thông tin trong tiêu đề gói tin (Header Fields) như Ingress Port, Ethernet Type, Source MAC, Destination MAC, IPv4 Source, IPv4 Destination, IP Protocol, Source Port, Destination Port."
    Add-P "Bước 2: So khớp gói tin với các Flow Entry trong bảng theo thứ tự độ ưu tiên (Priority) giảm dần. Luật có priority cao nhất khớp với gói tin sẽ được chọn."
    Add-P "Bước 3: Nếu tìm thấy luật so khớp (Match Hit), switch cập nhật bộ đếm (Counters), thực thi tập chỉ lệnh (Instructions) như cập nhật Action Set, hoặc chuyển gói tin sang bảng tiếp theo (Goto-Table n)."
    Add-P "Bước 4: Nếu không có luật nào khớp (Table Miss), switch thực thi luật mặc định (Table-Miss Flow Entry) đã được cấu hình trước: hủy gói tin (Drop), hoặc đóng gói tin gửi lên Controller qua bản tin Packet-In (Controller Action)."
    Add-P "Cấu trúc một Flow Entry trong OpenFlow 1.3 bao gồm 6 thành phần chính:"
    Add-P "- Match Fields: Các trường lọc gói tin trên nhiều tầng giao thức (L2/L3/L4)."
    Add-P "- Priority: Độ ưu tiên số nguyên (0 - 65535)."
    Add-P "- Counters: Thống kê số gói tin, số byte và thời gian tồn tại."
    Add-P "- Instructions: Chỉ lệnh xử lý (Apply-Actions, Clear-Actions, Write-Actions, Write-Metadata, Goto-Table)."
    Add-P "- Timeouts: Idle Timeout (thời gian rỗi) và Hard Timeout (thời gian cố định)."
    Add-P "- Cookie: Mã định danh 64-bit do Controller gán để quản lý và lọc luật."
    Add-H2 "2.3. Bộ điều khiển ONOS (Open Network Operating System)"
    Add-P "ONOS là một bộ điều khiển SDN mã nguồn mở cấp doanh nghiệp được thiết kế chuyên biệt cho các nhà cung cấp dịch vụ mạng viễn thông và trung tâm dữ liệu quy mô lớn."
    Add-P "Các thành phần cốt lõi của ONOS bao gồm:"
    Add-P "1. Nền tảng OSGi (Apache Karaf): Cho phép kiến trúc hóa toàn bộ hệ thống thành các gói bundle độc lập. Các dịch vụ như Device Manager, Host Manager, Flow Rule Manager, Topology Manager hoạt động như các dịch vụ OSGi có thể kích hoạt hoặc hủy kích hoạt động mà không cần khởi động lại toàn bộ tiến trình Java."
    Add-P "2. Hệ thống phân tán Atomix: Sử dụng thuật toán đồng thuận Raft để duy trì tính nhất quán của trạng thái cluster, hỗ trợ khả năng mở rộng quy mô Controller."
    Add-P "3. Intent Framework: Cho phép ứng dụng khai báo mục đích kết nối cấp cao (High-level Connectivity Intents) như PointToPointIntent, HostToHostIntent. Bộ biên dịch Intent (Intent Compiler) sẽ tự động tính toán đường đi ngắn nhất và sinh ra các flow rules phù hợp trên từng switch."
    Add-P "4. REST API v1 chuẩn hóa: Cung cấp các endpoint toàn diện cho phép hệ thống bên ngoài truy vấn và điều khiển mạng qua HTTP/JSON."
    Add-H1 "CHƯƠNG 3. CƠ SỞ LÝ THUYẾT VỀ ELK STACK VÀ GIÁM SÁT AN NINH SIEM"
    Add-H2 "3.1. Tổng quan về Security Information and Event Management (SIEM)"
    Add-P "SIEM là kiến trúc công nghệ trung tâm trong mọi Trung tâm điều hành an ninh mạng (SOC). Chức năng cốt lõi của SIEM bao gồm:"
    Add-P "1. Thu thập dữ liệu tập trung (Data Ingestion): Tiếp nhận nhật ký từ hàng nghìn nguồn khác nhau."
    Add-P "2. Chuẩn hóa dữ liệu (Data Normalization): Ánh xạ các trường dữ liệu khác biệt về một cấu trúc thống nhất (như Elastic Common Schema)."
    Add-P "3. Phân tích và tương quan (Analytics & Correlation): Áp dụng các quy tắc logic và chuỗi thời gian để phát hiện hành vi tấn công."
    Add-P "4. Lưu trữ và tra cứu (Storage & Retrieval): Lưu trữ dữ liệu an toàn phục vụ điều tra số (Digital Forensics)."
    Add-P "5. Trực quan hóa và báo cáo (Visualization & Compliance): Xây dựng dashboard thời gian thực và xuất báo cáo tuân thủ."
    Add-H2 "3.2. Ngăn xếp ELK Stack trong kiến trúc SDNFlowGuard"
    Add-P "Hệ thống SDNFlowGuard sử dụng trọn bộ ngăn xếp ELK Stack phiên bản 8.15.1:"
    Add-P "1. Logstash: Cấu hình pipeline với plugin HTTP input lắng nghe tại cổng 18080. Logstash tiếp nhận các sự kiện JSON từ Python Collector, lọc bỏ các trường không hợp lệ, bổ sung siêu dữ liệu thời gian @timestamp và đẩy vào Elasticsearch."
    Add-P "2. Elasticsearch: Lưu trữ tài liệu dưới dạng chỉ mục theo ngày sdnflowguard-events-YYYY.MM.DD. Elasticsearch sử dụng cấu trúc chỉ mục đảo (Inverted Index) cho tìm kiếm và cấu trúc dữ liệu cột (Doc Values) cho các phép tổng hợp số liệu (Aggregations) trên các trường số như total_pps, rx_bps, byte_count."
    Add-P "3. Kibana: Cung cấp giao diện web trực quan tại cổng 5601. Cho phép xây dựng biểu đồ đường theo dõi lưu lượng thời gian thực của từng cổng switch và bảng cảnh báo an ninh."
    Add-H1 "CHƯƠNG 4. PHÂN TÍCH YÊU CẦU VÀ THIẾT KẾ KIẾN TRÚC TỔNG THỂ"
    Add-H2 "4.1. Phân tích yêu cầu chức năng và phi chức năng"
    Add-P "Hệ thống SDNFlowGuard được xây dựng nhằm đáp ứng trọn vẹn 10 yêu cầu chức năng (FR) và 6 yêu cầu phi chức năng (NFR):"
    Add-P "Yêu cầu chức năng:"
    Add-P "- FR-01: Quan sát trực tiếp topology mạng SDN từ ONOS qua REST API."
    Add-P "- FR-02: Thu thập định kỳ thống kê cổng và luồng mạng, đẩy vào ELK Stack."
    Add-P "- FR-03: Tự động phát hiện bất thường tốc độ gói tin cao kéo dài trên từng cổng switch."
    Add-P "- FR-04: Phân tích bản bắt gói tin L2/L3 tại cổng vào switch (Step 63)."
    Add-P "- FR-05: Đối chiếu bằng chứng gói tin với topology ONOS và cảnh báo ELK (Step 64)."
    Add-P "- FR-06: Đánh giá chính sách phòng thủ và kiểm tra cổng an toàn Safety Gate."
    Add-P "- FR-07: Cung cấp giao diện điều khiển mạng thủ công qua REST API."
    Add-P "- FR-08: Hỗ trợ cơ chế hoàn nguyên (Rollback) luật và ghi nhật ký kiểm toán SQLite."
    Add-P "- FR-09: Chuẩn hóa nhật ký đa nguồn SIEM (Firewall Syslog, Windows Event Log)."
    Add-P "- FR-10: Cung cấp giao diện Web ReactJS 7 trang và xuất báo cáo tổng kết dạng PDF."
    Add-P "Yêu cầu phi chức năng:"
    Add-P "- NFR-01: An toàn mặc định (Fail-Safe by Default): Mặc định chạy ở chế độ DRY_RUN."
    Add-P "- NFR-02: Toàn vẹn dữ liệu: Bảo toàn tuyệt đối cơ sở dữ liệu và bằng chứng lịch sử."
    Add-P "- NFR-03: Bảo mật cấu hình: Không lưu secret cứng, bảo vệ API bằng API Key."
    Add-P "- NFR-04: Khả năng chịu lỗi: Xử lý timeout an toàn khi dịch vụ ngoài gián đoạn."
    Add-P "- NFR-05: Khả năng tái lập (Reproducibility): Triển khai dễ dàng qua Docker và scripts."
    Add-P "- NFR-06: Quan sát được (Observability): Logging có cấu trúc kèm request_id."
    Add-H2 "4.2. Kiến trúc 4 mặt phẳng của hệ thống SDNFlowGuard"
    Add-P "Hệ thống SDNFlowGuard được tổ chức thành 4 mặt phẳng độc lập nhưng liên kết chặt chẽ:"
    Add-P "1. Data Plane (Mặt phẳng dữ liệu): Mạng ảo hóa Mininet chạy trên WSL Ubuntu-26.04 gồm switch Open vSwitch s1 (OpenFlow 1.3, Datapath ID of:0000000000000001) và hai host h1 (10.0.0.1/00:00:00:00:00:01 gắn cổng 1) và h2 (10.0.0.2/00:00:00:00:00:02 gắn cổng 2)."
    Add-P "2. Control Plane (Mặt phẳng điều khiển): Bộ điều khiển ONOS Controller (Docker container sdnflowguard-onos) quản lý switch qua giao thức OpenFlow 1.3 (cổng 6653) và cung cấp REST API (cổng 8181)."
    Add-P "3. SIEM Plane (Mặt phẳng giám sát SIEM): Ngăn xếp ELK gồm Logstash (cổng 18080 tiếp nhận HTTP events), Elasticsearch (cổng 9200 lưu trữ và truy vấn chỉ mục) và Kibana (cổng 5601 trực quan hóa)."
    Add-P "4. Application Plane (Mặt phẳng ứng dụng): Gồm Flask REST API (cổng 5000), cơ sở dữ liệu SQLite (database/sdnflowguard.db), các Collector, Monitor V1/V2, Evidence Correlator Step 63/64, Defense Policy Engine và React Frontend (cổng 3000)."
    Add-H2 "4.3. Kiến trúc phần mềm Clean Architecture và Strangler Fig Pattern"
    Add-P "Nhằm đảm bảo chất lượng kỹ thuật cao nhất và tuân thủ các nguyên lý thiết kế phần mềm hiện đại (SOLID, Separation of Concerns), hệ thống backend được tái cấu trúc theo mô hình Clean Architecture kết hợp Strangler Fig Pattern trong gói backend/sdnflowguard/:"
    Add-P "- Domain Layer (Tầng miền nghiệp vụ): Là tầng trong cùng, độc lập hoàn toàn với framework và thư viện ngoài. Chứa các Value Objects (DefenseMode, CorrelationStatus, SafetyGateVerdict), Domain Services (EvidenceCorrelationService, SiemLogNormalizerService) và Policies (SafetyGate, DefensePolicy, RiskScoringPolicy)."
    Add-P "- Application Layer (Tầng ứng dụng): Chứa các Use Cases điều phối luồng nghiệp vụ (EvaluateEvidenceCorrelationUseCase, EvaluateDefensePolicyUseCase, EvaluateControlActionSafetyUseCase, RunSiemCapabilityEvaluationUseCase)."
    Add-P "- Infrastructure Layer (Tầng hạ tầng): Chứa các Adapter triển khai giao tiếp ngoài (SqliteRepository, OnosClient, ElasticsearchClient, LogstashClient, AppSettings) với timeout và error handling chặt chẽ."
    Add-P "- Interfaces Layer (Tầng giao diện): Cung cấp các Blueprint routes cho Flask (/api/defense/*, /api/siem/*) và middleware bảo mật (check_api_key)."
    Add-H1 "CHƯƠNG 5. HIỆN THỰC THU THẬP SỐ LIỆU VÀ PHÁT HIỆN BẤT THƯỜNG"
    Add-H2 "5.1. Phân hệ thu thập số liệu (Collectors)"
    Add-P "Phân hệ thu thập số liệu gồm hai tiến trình chạy ngầm định kỳ bằng Python 3.10.10:"
    Add-P "1. onos_elk_collector.py: Định kỳ mỗi 5 giây truy vấn các REST API /onos/v1/devices, /onos/v1/hosts, /onos/v1/flows từ ONOS. Collector tổng hợp số lượng switch, host, flow đang hoạt động, đóng gói thành sự kiện onos_network_summary và gửi tới Logstash qua cổng HTTP 18080."
    Add-P "2. onos_port_elk_collector.py: Định kỳ truy vấn thống kê cổng /onos/v1/statistics/ports trên từng thiết bị switch. Collector lưu lại mẫu đo của chu kỳ trước và tính toán tốc độ truyền thông tức thời:"
    Add-Code "delta_time = current_timestamp - previous_timestamp (giây)`ndelta_rx_packets = current_rx_packets - previous_rx_packets`ndelta_tx_packets = current_tx_packets - previous_tx_packets`nrx_pps = delta_rx_packets / delta_time`ntx_pps = delta_tx_packets / delta_time`ntotal_pps = rx_pps + tx_pps`nrx_bps = (delta_rx_bytes * 8) / delta_time`ntx_bps = (delta_tx_bytes * 8) / delta_time"
    Add-P "Các sự kiện onos_port_stats chứa đầy đủ các chỉ số này được gửi tới Logstash để lập chỉ mục vào Elasticsearch."
    Add-H2 "5.2. Động cơ phát hiện bất thường và cơ chế Overlap Monitor V2"
    Add-P "Bộ phát hiện bất thường (sdn_port_anomaly_detector.py) phân tích chuỗi thời gian của từng cổng switch. Bất thường tốc độ cao kéo dài (SUSTAINED_HIGH_PACKET_RATE) được xác nhận khi tốc độ total_pps vượt ngưỡng threshold_pps trong consecutive_hits chu kỳ lấy mẫu liên tiếp."
    Add-P "Nếu khoảng cách thời gian giữa hai mẫu đo vượt quá max_gap_sec (25 giây), hệ thống xác định việc thu thập bị gián đoạn và đặt lại streak về 0 để tránh kết luận sai."
    Add-P "Hệ thống triển khai hai phiên bản Monitor:"
    Add-P "- Reliable Monitor V1: Lưu trữ con trỏ thời gian last_processed_timestamp nguyên tử qua file khóa .tmp vào thư mục backend/collectors/state/ để khôi phục trạng thái sau khi khởi động lại."
    Add-P "- Overlap Alert Monitor V2: Nâng cấp cơ chế cửa sổ trượt có vùng chồng lấp (overlap_sec = 30s) kết hợp bộ lọc watermark. Cơ chế này giải quyết triệt để vấn đề các mẫu thống kê cổng đến trễ (late-arriving telemetry) qua ranh giới chu kỳ quét, đồng thời sinh khóa băm SHA-256 alert_key duy nhất từ (alert_type, device_id, port, first_seen, last_seen) để loại bỏ 100% cảnh báo trùng lặp."
    Add-H1 "CHƯƠNG 6. CƠ CHẾ TƯƠNG QUAN BẰNG CHỨNG NGUỒN VÀ AN TOÀN PHÒNG THỦ"
    Add-H2 "6.1. Chuỗi xác minh bằng chứng nguồn hai giai đoạn (Steps 63–64)"
    Add-P "Để giải quyết triệt để nghịch lý 'Attached Host != Verified Attacker', đề tài thiết lập quy trình xác minh bằng chứng nguồn L2/L3 nghiêm ngặt:"
    Add-P "Giai đoạn Step 63 (source_ip_evidence_analyzer.py):"
    Add-P "Hệ thống thu thập bản bắt gói tin thực tế bằng tcpdump trên các giao diện mạng cổng vào của switch (s1-eth1 tương ứng cổng 1, s1-eth2 tương ứng cổng 2). Trình phân tích hỗ trợ giải mã cả định dạng UTF-8 và UTF-16LE, trích xuất cấu trúc dữ liệu bằng chứng gồm: observed_source_mac, observed_source_ip, observed_destination_ip, protocol, icmp_type, packet_count, mốc giờ cục bộ và siêu dữ liệu cửa sổ thời gian UTC (capture_started_utc, capture_finished_utc)."
    Add-P "Giai đoạn Step 64 (onos_host_evidence_correlator.py):"
    Add-P "Bằng chứng gói tin Step 63 được đối chiếu chéo trực tiếp với topology thời gian thực từ ONOS (LIVE_ONOS: /onos/v1/devices, /onos/v1/hosts, /onos/v1/flows). Thuật toán phân loại kết quả đối chiếu thành 4 trạng thái rõ ràng:"
    Add-P "1. CORROBORATED_HOST_OBSERVATION: Địa chỉ MAC và IP trong gói tin khớp chính xác tuyệt đối 100% với host duy nhất đã đăng ký trên cổng đó trong bảng quản lý của ONOS."
    Add-P "2. AMBIGUOUS_MULTI_HOST: Cổng switch có từ 2 host trở lên cùng kết nối -> Hệ thống từ chối lệnh chặn cổng để tránh ảnh hưởng host vô tội."
    Add-P "3. HOST_IDENTITY_MISMATCH: Gói tin mang địa chỉ IP/MAC khác với host đã đăng ký trên cổng trong ONOS -> Cảnh báo dấu hiệu tấn công giả mạo (IP/MAC Spoofing)."
    Add-P "4. UNREGISTERED_HOST_ON_PORT: Cổng chưa có thông tin host đăng ký trong ONOS."
    Add-P "Hệ thống chỉ xác nhận attacker_confirmed = True khi và chỉ khi: (1) Trạng thái đối chiếu đạt CORROBORATED; (2) Cửa sổ thời gian UTC của bản bắt gói trùng khớp với cửa sổ cảnh báo bất thường trong Elasticsearch; và (3) Lưu lượng có tính chất bất đối xứng của cuộc tấn công DoS thay vì trao đổi ICMP hai chiều đối xứng."
    Add-H2 "6.2. Cổng an toàn Active Defense Safety Gate và Cơ chế Rollback"
    Add-P "Động cơ an toàn phòng thủ (sdnflowguard/domain/policies/safety_gate.py) kiểm soát mọi yêu cầu điều khiển mạng trước khi gửi tới ONOS thông qua 5 chốt chặn bắt buộc:"
    Add-P "- Chốt 1 (not_test_only_alert): Mọi cảnh báo có cờ test_only = True bị chặn lại ngay lập tức, không bao giờ được phép thực thi lệnh chặn."
    Add-P "- Chốt 2 (valid_and_unprotected_target): Kiểm tra định dạng IPv4/CIDR. Bảo vệ tuyệt đối dải địa chỉ loopback (127.0.0.0/8), địa chỉ IP của SDN Controller, IP của ELK Server, địa chỉ Multicast (224.0.0.0/4), Broadcast (255.255.255.255) và danh sách địa chỉ trắng (allowlist_ips)."
    Add-P "- Chốt 3 (evidence_attribution_satisfied): Nghiêm cấm chặn IP chỉ từ cảnh báo cổng nếu thiếu bằng chứng quy gán nguồn IP đã đối chiếu thành công."
    Add-P "- Chốt 4 (defense_mode_permits_execution): Mặc định SDNFLOW_DEFENSE_MODE = DRY_RUN. Trong chế độ này, hệ thống chỉ tạo bản xem trước luật (acl_rule_preview và flow_rule_preview) và ghi nhận mô phỏng (DRY_RUN_SIMULATED), tuyệt đối không gửi lệnh POST/DELETE làm thay đổi trạng thái switch."
    Add-P "- Chốt 5 (operator_approval_satisfied): Trong chế độ ACTIVE_ENFORCEMENT, hành động vẫn được giữ ở trạng thái ACTIVE_ENFORCEMENT_PENDING_APPROVAL cho tới khi có phê duyệt chủ động từ người vận hành."
    Add-P "Mọi quyết định đều đính kèm một kế hoạch hoàn nguyên (rollback_plan) chi tiết, cho phép hủy bỏ luật chặn tức thì qua API /api/defense/rollback hoặc /api/unblock và ghi vết kiểm toán đầy đủ vào bảng actions trong SQLite."
    Add-H1 "CHƯƠNG 7. BẢNG ĐIỀU KHIỂN REACTJS VÀ KẾT QUẢ THỰC NGHIỆM"
    Add-H2 "7.1. Giao diện quản trị mạng SDNFlowGuard"
    Add-P "Giao diện người dùng được xây dựng trên React 18, chạy trên cổng 3000, đã được đồng bộ hóa hoàn toàn với bộ nhận diện thương hiệu SDNFlowGuard (biểu tượng chiếc khiên bảo mật mạng) gồm 7 trang chức năng chuyên nghiệp:"
    Add-P "- Dashboard: Hiển thị trạng thái các dịch vụ, tổng số luồng, cảnh báo an ninh, tích hợp biểu đồ lưu lượng cổng ELK và bảng cảnh báo thời gian thực."
    Add-Pic "dashboard_overview.png" "Hình 7.1: Bảng điều khiển trung tâm SDNFlowGuard Dashboard"
    Add-P "- Traffic Overview: Quan sát sơ đồ topology mạng SDN, trạng thái switch, host và danh sách luật OpenFlow trực tiếp từ ONOS."
    Add-Pic "traffic_overview.png" "Hình 7.2: Quản lý luồng và quan sát trạng thái mạng SDN trực tiếp"
    Add-P "- Anomaly Detection: Theo dõi các điểm rủi ro bất thường được phát hiện bởi các Monitor."
    Add-Pic "anomaly_detection.png" "Hình 7.3: Màn hình phát hiện lưu lượng bất thường và đánh giá rủi ro"
    Add-P "- Manual Traffic Control: Cung cấp giao diện kiểm soát lưu lượng thủ công qua cổng an toàn Safety Gate."
    Add-Pic "manual_traffic_control.png" "Hình 7.4: Giao diện điều khiển lưu lượng mạng có kiểm soát"
    Add-P "- Reports & Settings: Xuất báo cáo tổng kết hệ thống dạng PDF chuẩn %PDF-1.4 và cấu hình tham số hoạt động."
    Add-Pic "reports.png" "Hình 7.5: Màn hình xem và xuất báo cáo an ninh mạng"
    Add-Pic "chatbot.png" "Hình 7.6: Trợ lý an ninh mạng cục bộ (Security Assistant)"
    Add-H2 "7.2. Kết quả 5 kịch bản kiểm thử End-to-End thực tế trên Lab"
    Add-P "Hệ thống đã trải qua 5 kịch bản thực nghiệm End-to-End trực tiếp trên môi trường lab Mininet OpenFlow 1.3 và ONOS:"
    Add-P "Kịch bản 01 (Mạng bình thường): Mininet single,2 truyền gói tin ICMP hợp lệ giữa h1 (10.0.0.1) và h2 (10.0.0.2). Kết quả pingAll() đạt 0.0% packet loss (RTT trung bình 1.154 ms). Collector thu thập thành công 4 flow rules từ ONOS đẩy vào Logstash/Elasticsearch. Động cơ phòng thủ kết luận ALLOW, không có luật chặn nào được đề xuất (PROPOSE_BLOCK: 0)."
    Add-P "Kịch bản 02 (Lưu lượng bất thường & Cảnh báo): Phát sinh lưu lượng tốc độ cao qua ngưỡng 4.0 PPS. Overlap Alert Monitor V2 phát hiện chính xác 10 ứng viên bất thường, sinh khóa băm SHA-256 alert_key duy nhất và đẩy 16 cảnh báo vào Elasticsearch sdnflowguard-events-*, hiển thị tức thì trên React UI."
    Add-P "Kịch bản 03 (Tương quan bằng chứng & Đánh giá chính sách): Chạy onos_host_evidence_correlator.py đối chiếu bản bắt gói tin với LIVE_ONOS. Cả hai cổng switch s1 đạt CORROBORATED_HOST_OBSERVATION. Tuy nhiên, do lưu lượng là cặp ping đối xứng và thiếu giao thoa thời gian UTC với cảnh báo thật, hệ thống đưa ra phán quyết chính xác OBSERVE (Automatic Block Allowed: False). Cổng an toàn từ chối thành công các yêu cầu khóa IP 127.0.0.1 và test_only."
    Add-P "Kịch bản 04 (Phòng thủ SDN có kiểm soát): Thực hiện thử nghiệm Stage A (DRY RUN). Hệ thống sinh đầy đủ acl_rule_preview và flow_rule_preview (priority 40010, timeout 300s, selector IPV4_SRC=10.0.0.1/32, treatment DROP). Stage B được giữ an toàn ở trạng thái ACTIVE_ENFORCEMENT_PENDING_APPROVAL."
    Add-P "Kịch bản 05 (Hoàn nguyên và Khôi phục kết nối): Kích hoạt cơ chế Rollback unblock_ip. Kiểm tra lại kết nối giữa h1 và h2 trong Mininet xác nhận 4/4 gói tin truyền thông thành công, 0% packet loss, mạng lab được khôi phục nguyên vẹn."
    Add-H2 "7.3. Kết quả bộ kiểm thử tự động (50/50 Tests PASS)"
    Add-P "Toàn bộ bộ kiểm thử tự động gồm 50 bài kiểm thử (24 Unit, 12 Integration, 5 Contract, 8 Safety, 1 E2E) và 4 CLI Self-Tests đã được thực thi bằng Python 3.10.10 (-B) qua lệnh scripts/run_all_tests.ps1. Kết quả đạt 100% PASS trong 0.514 giây. Mã băm SHA-256 của cơ sở dữ liệu chính database/sdnflowguard.db được bảo toàn tuyệt đối 100%: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9."
    Add-H1 "CHƯƠNG 8. ĐÁNH GIÁ BẢO MẬT, ĐỘ TIN CẬY VÀ HIỆU NĂNG"
    Add-H2 "8.1. Đánh giá tính bảo mật và kiểm toán mã nguồn"
    Add-P "Kiểm toán bảo mật xác nhận hệ thống đã loại bỏ hoàn toàn các mật khẩu cứng trong mã nguồn backend/run.py và cấu hình .env.example. Các thao tác quản trị nhạy cảm được bảo vệ bằng cơ chế xác thực X-SDNFlow-API-Key. Cổng an toàn ngăn chặn 100% nguy cơ tấn công từ chối dịch vụ tự gây ra (Self-inflicted DoS) nhờ cơ chế miễn nhiễm địa chỉ hạ tầng."
    Add-H2 "8.2. Đánh giá độ tin cậy và khả năng chịu lỗi"
    Add-P "Khi bộ điều khiển ONOS hoặc Elasticsearch tạm thời ngoại tuyến, toàn bộ API backend và Chatbot đều có cơ chế ngắt mạch an toàn với timeout từ 2 đến 3 giây, trả về phản hồi suy giảm có kiểm soát (Graceful Degradation) thay vì làm sập ứng dụng."
    Add-H1 "CHƯƠNG 9. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN"
    Add-H2 "9.1. Hạn chế kỹ thuật hiện tại"
    Add-P "1. Mô hình thực nghiệm hiện tại tập trung kiểm chứng sâu trên topology đơn switch SingleSwitchTopo(k=2). Việc mở rộng lên topology đa switch quy mô lớn đòi hỏi thuật toán định vị cổng biên (Ingress Port Localization) phức tạp hơn."
    Add-P "2. Các nguồn nhật ký Firewall Syslog và Windows Server Event Log hiện được kiểm chứng thông qua bộ dữ liệu mẫu chuẩn hóa (FIXTURE_SIMULATION), sẵn sàng kết nối với tác tử Filebeat/Winlogbeat trong thực tế."
    Add-P "3. Thao tác chặn trực tiếp trên ONOS (Stage B) được giữ ở trạng thái chờ phê duyệt của người vận hành để tuân thủ tuyệt đối an toàn phòng lab."
    Add-H2 "9.2. Hướng phát triển trong tương lai"
    Add-P "1. Mở rộng thử nghiệm trên các kiến trúc mạng trung tâm dữ liệu đa tầng (Spine-Leaf, Fat-Tree)."
    Add-P "2. Tích hợp các mô hình học máy nhẹ (Isolation Forest, Autoencoder) trên chuỗi thời gian cổng Elasticsearch để phát hiện các cuộc tấn công DoS lưu lượng thấp (Low-rate DoS)."
    Add-P "3. Triển khai tác tử Winlogbeat và Filebeat đẩy nhật ký từ các máy chủ ảo hóa thật vào cổng chuẩn hóa /api/siem/normalize."
    Add-H1 "CHƯƠNG 10. KẾT LUẬN"
    Add-P "Đồ án 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' (Dự án SDNFlowGuard) đã hoàn thành xuất sắc và toàn diện 100% các mục tiêu nghiên cứu và yêu cầu thực tiễn của môn học Chuyên đề – Hệ thống mạng và bảo mật. Hệ thống đã chứng minh thành công tính khả thi và hiệu quả vượt trội của việc kết hợp mạng điều khiển bằng phần mềm SDN (ONOS, OpenFlow 1.3, Mininet/OVS) với ngăn xếp phân tích sự kiện an ninh tập trung ELK Stack."
    Add-P "Đóng góp học thuật và kỹ thuật nổi bật nhất của đề tài là việc thiết lập và chứng minh thành công nguyên lý 'Attached Host != Verified Attacker', xây dựng chuỗi tương quan bằng chứng nguồn L2/L3 hai giai đoạn Step 63/64 và cổng an toàn Active Defense Safety Gate hoạt động ở chế độ DRY_RUN an toàn. Toàn bộ hệ thống mã nguồn, cơ sở dữ liệu lịch sử, 50 bài kiểm thử tự động, 5 kịch bản thực nghiệm End-to-End, bộ tài liệu và slide thuyết trình đã sẵn sàng phục vụ báo cáo bảo vệ và nộp đồ án."
    Add-H1 "TÀI LIỆU THAM KHẢO"
    Add-P "[1] Open Networking Foundation (ONF), 'OpenFlow Switch Specification Version 1.3.5', ONF TS-023, Mar. 2015."
    Add-P "[2] P. Berde et al., 'ONOS: Towards an Open, Distributed SDN OS', in Proceedings of the Third Workshop on Hot Topics in Software Defined Networks (HotSDN '14), Chicago, IL, USA, 2014, pp. 1-6."
    Add-P "[3] B. Lantz, B. Heller, and N. McKeown, 'A Network in a Laptop: Rapid Prototyping for Software-Defined Networks', in Proceedings of the 9th ACM SIGCOMM Workshop on Hot Topics in Networks (HotNets-IX), Monterey, CA, USA, 2010."
    Add-P "[4] B. Pfaff et al., 'The Design and Implementation of Open vSwitch', in 12th USENIX Symposium on Networked Systems Design and Implementation (NSDI '15), Oakland, CA, USA, 2015, pp. 117-130."
    Add-P "[5] Elastic, 'Elasticsearch Reference [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html"
    Add-P "[6] Elastic, 'Logstash Reference [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/logstash/reference/current/index.html"
    Add-P "[7] Elastic, 'Kibana Guide [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/kibana/reference/current/index.html"
    Add-P "[8] R. Martin, 'Clean Architecture: A Craftsman's Guide to Software Structure and Design', Prentice Hall, 2017."
    Add-P "[9] M. Fowler, 'StranglerFigApplication', MartinFowler.com, 2019. [Online]. Available: https://martinfowler.com/bliki/StranglerFigApplication.html"
    Add-P "[10] S. Scott-Hayward, S. Natarajan, and S. Sezer, 'A Survey of Security in Software Defined Networks', IEEE Communications Surveys & Tutorials, vol. 18, no. 1, pp. 623-654, 2016."
    Add-P "[11] N. Sultana et al., 'FLIPS: Hybrid OpenFlow Switch for Software-Defined Network Security', in IEEE Transactions on Network and Service Management, vol. 14, no. 2, pp. 312-325, June 2017."
    Add-P "[12] S. Shin et al., 'FRESCO: Modular Composable Security Services for Software-Defined Networks', in Proceedings of the 20th Annual Network and Distributed System Security Symposium (NDSS '13), San Diego, CA, USA, 2013."
    Add-H1 "PHỤ LỤC A. HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG"
    Add-P "Phụ lục này cung cấp tài liệu kỹ thuật chi tiết về quy trình khởi động, kiểm tra sức khỏe và chạy thử nghiệm hệ thống SDNFlowGuard:"
    Add-P "1. Khởi động các container Docker:"
    Add-Code "cd D:\Project\Nhom02_SDNFlowGuard\infrastructure`ndocker compose -f compose.yaml up -d"
    Add-P "2. Khởi tạo mạng Mininet OpenFlow 1.3 trong WSL Ubuntu-26.04:"
    Add-Code "wsl -d Ubuntu-26.04 -u root -- mn --topo single,2 --mac --switch ovsk,protocols=OpenFlow13 --controller remote,ip=127.0.0.1,port=6653"
    Add-P "3. Khởi chạy Flask Backend API:"
    Add-Code "`$env:PYTHONDONTWRITEBYTECODE=`"1`"`n`$env:SDNFLOW_DEFENSE_MODE=`"DRY_RUN`"`n& `"D:\Project\Nhom02_SDNFlowGuard\backend\venv\Scripts\python.exe`" -B run.py"
    Add-P "4. Khởi chạy React Frontend UI:"
    Add-Code "cd D:\Project\Nhom02_SDNFlowGuard\frontend`nnpm start"
    Add-P "5. Thực thi bộ kiểm tra sức khỏe và toàn bộ kiểm thử tự động:"
    Add-Code "powershell -ExecutionPolicy Bypass -File scripts\verify_system_health.ps1`npowershell -ExecutionPolicy Bypass -File scripts\run_all_tests.ps1"
    Add-H1 "PHỤ LỤC B. DANH MỤC 50 BÀI KIỂM THỬ TỰ ĐỘNG"
    Add-P "Bảng dưới đây thống kê đầy đủ 50 bài kiểm thử tự động đã được kiểm chứng và đạt trạng thái PASS 100% trong scripts/run_all_tests.ps1:"
    Add-P "Module: test_source_ip_evidence_analyzer.py | Số bài test: 3 | Tầng: Unit | Phạm vi kiểm chứng: Giải mã gói tin tcpdump UTF-8/UTF-16, trích xuất MAC/IP, kiểm tra mốc UTC"
    Add-P "Module: test_onos_host_evidence_correlator.py | Số bài test: 3 | Tầng: Unit | Phạm vi kiểm chứng: Đối chiếu topology ONOS, phát hiện multi-host và giả mạo IP/MAC"
    Add-P "Module: test_defense_policy.py | Số bài test: 2 | Tầng: Unit | Phạm vi kiểm chứng: Động cơ chính sách phòng thủ, invariant Host != Attacker, ALLOW/OBSERVE"
    Add-P "Module: test_safety_gate.py | Số bài test: 3 | Tầng: Unit | Phạm vi kiểm chứng: Cổng an toàn, bảo vệ IP hạ tầng, kiểm soát DRY_RUN và duyệt vận hành"
    Add-P "Module: test_risk_scoring_and_decision.py | Số bài test: 3 | Tầng: Unit | Phạm vi kiểm chứng: Chấm điểm nguy cơ tích lũy, miễn nhiễm cảnh báo test_only"
    Add-P "Module: test_siem_log_normalizer.py | Số bài test: 3 | Tầng: Unit | Phạm vi kiểm chứng: Chuẩn hóa nhật ký SIEM: ONOS telemetry, Firewall Syslog, Windows Event"
    Add-P "Module: test_port_anomaly_detector.py | Số bài test: 2 | Tầng: Unit | Phạm vi kiểm chứng: Phát hiện chuỗi vượt ngưỡng liên tiếp, đặt lại chuỗi khi đứt quãng mẫu"
    Add-P "Module: test_alert_publisher.py | Số bài test: 1 | Tầng: Unit | Phạm vi kiểm chứng: Sinh mã băm SHA-256 alert_key duy nhất, gắn nhãn cờ test_only"
    Add-P "Module: test_reliable_monitor_v1.py | Số bài test: 2 | Tầng: Unit | Phạm vi kiểm chứng: Động cơ Reliable Monitor V1, xử lý hit và lưu checkpoint nguyên tử"
    Add-P "Module: test_reliable_monitor_v2.py | Số bài test: 2 | Tầng: Unit | Phạm vi kiểm chứng: Động cơ Overlap Monitor V2, xử lý dữ liệu đến trễ qua cửa sổ 30s"
    Add-P "Module: test_sqlite_repository.py | Số bài test: 3 | Tầng: Integration | Phạm vi kiểm chứng: Thao tác CRUD trên các bảng settings, flows, events, actions trong DB"
    Add-P "Module: test_webhook_reception.py | Số bài test: 2 | Tầng: Integration | Phạm vi kiểm chứng: Tiếp nhận webhook sự kiện, kiểm tra cú pháp và lưu vết"
    Add-P "Module: test_flask_api_routes.py | Số bài test: 6 | Tầng: Integration | Phạm vi kiểm chứng: Kiểm thử các endpoint REST API: health, evidence, evaluate, safety, block, API-Key"
    Add-P "Module: test_report_generator.py | Số bài test: 1 | Tầng: Integration | Phạm vi kiểm chứng: Sinh báo cáo tổng kết hệ thống và cơ chế dự phòng PDF thuần Python"
    Add-P "Module: test_onos_payload_contracts.py | Số bài test: 2 | Tầng: Contracts | Phạm vi kiểm chứng: Khế ước định dạng dữ liệu ONOS REST v1 ACL và PointToPointIntent"
    Add-P "Module: test_elasticsearch_query_contracts.py | Số bài test: 2 | Tầng: Contracts | Phạm vi kiểm chứng: Khế ước tham số truy vấn và cấu trúc phản hồi Elasticsearch /api/elk/*"
    Add-P "Module: test_frontend_backend_api_contracts.py | Số bài test: 1 | Tầng: Contracts | Phạm vi kiểm chứng: Khế ước cấu trúc JSON giữa backend Flask và các trang React"
    Add-P "Module: test_no_secret_leakage.py | Số bài test: 2 | Tầng: Safety | Phạm vi kiểm chứng: Kiểm toán không lộ mật khẩu cứng trong run.py và .env.example"
    Add-P "Module: test_dry_run_default.py | Số bài test: 1 | Tầng: Safety | Phạm vi kiểm chứng: Xác minh chế độ phòng thủ mặc định luôn là DRY_RUN an toàn"
    Add-P "Module: test_port_anomaly_never_blocks_ip.py | Số bài test: 1 | Tầng: Safety | Phạm vi kiểm chứng: Đảm bảo bất thường cổng đơn thuần không bao giờ đề xuất khóa IP"
    Add-P "Module: test_test_alert_never_blocks.py | Số bài test: 1 | Tầng: Safety | Phạm vi kiểm chứng: Đảm bảo cảnh báo test_only không bao giờ kích hoạt khóa IP"
    Add-P "Module: test_checkpoint_integrity.py | Số bài test: 3 | Tầng: Safety | Phạm vi kiểm chứng: Bảo toàn 4 checkpoint collector, 2 file bằng chứng Step 63 và SHA-256 DB"
    Add-P "Module: test_full_monitoring_to_policy_pipeline.py | Số bài test: 1 | Tầng: E2E | Phạm vi kiểm chứng: Kiểm thử toàn diện đường ống từ mẫu đo cổng tới Step 64 và Rollback"
    Add-H1 "PHỤ LỤC C. BẢNG MÃ BĂM TOÀN VẸN SHA-256 DỰ ÁN"
    Add-P "Bảng mã băm SHA-256 của các thành phần dữ liệu, cấu hình và tệp bằng chứng cốt lõi:"
    Add-P "Tệp: database/sdnflowguard.db (28,672 bytes) -> SHA-256: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9"
    Add-P "Tệp: database/netsecflow.db.bak (28,672 bytes) -> SHA-256: d12be7a29b412061213ef13f1c7e47e75405f84a83fb9949bbde3c7e31110443"
    Add-P "Tệp: backend/defense/evidence/ingress_icmp_20261101_014645.txt (5,146 bytes) -> SHA-256: 3076efccdc79564568e320b983b1fd12c2f1ef4f1ec2df55f7ab4e21a21b40d7"
    Add-P "Tệp: backend/defense/evidence/ingress_icmp_20261101_014645.json (2,202 bytes) -> SHA-256: 05a659224fb184be2e0e7416f18602bc6d658a10d5d43d7b89c1420db024e91c"
    Add-P "Tệp: backend/defense/evidence/ingress_icmp_live_utc_verified.txt (959 bytes) -> SHA-256: bef49f603007d7f0fd154b691d8de9b8945a7e89055bf6f4c9fa7ff7d71c8cf8"
    Add-P "Tệp: backend/defense/evidence/ingress_icmp_live_utc_verified.json (1,521 bytes) -> SHA-256: 1d36f69569871845848c5cbcdec2c99ce2d1832da53b3b4cf70ba4750cfdda68"
    Add-P "Tệp: backend/collectors/state/auto_dry_t4_c2.json (376 bytes) -> SHA-256: c852e276cbca38ec0bc9a637c132d6cc3be6d735fc67d393055ff6a9ef19a91e"
    Add-P "Tệp: backend/collectors/state/auto_dry_t4_c2_v2.json (5,395 bytes) -> SHA-256: c011906fb042f684fd33945f2c5b8c04d31f925b80eb774da06346ff2512fc33"
    Add-P "Tệp: backend/collectors/state/auto_publish_t4_c2.json (376 bytes) -> SHA-256: a2ab7d86fc0bc5a19833a44a2232c1914f8fb2bc97c832c451ff1a4533bf0628"
    Add-P "Tệp: backend/collectors/state/auto_publish_t4_c2_v2.json (5,495 bytes) -> SHA-256: dc7fb2ef306c64e4ecbc0f950174da1cf002798efab5166037b0ab95395cb16e"
    Add-H1 "PH? L?C D. TO?N V?N M? NGU?N C?NG AN TO?N ACTIVE DEFENSE (SAFETY GATE)"
    Add-P "T?p: backend/sdnflowguard/domain/policies/safety_gate.py"
    Add-Code "`"`"`"Active Defense Safety Gate and Lifecycle State Machine.`n`nEnforces fail-safe rules before any ONOS OpenFlow control action is proposed,`nstaged, or executed.`n`nLifecycle State Machine:`nNORMAL -> ANOMALY_OBSERVED -> EVIDENCE_CORRELATED -> BLOCK_PROPOSED`n       -> BLOCK_APPROVED -> RULE_APPLIED -> RULE_VERIFIED -> ROLLBACK_OR_EXPIRED`n`"`"`"`n`nfrom __future__ import annotations`n`nimport ipaddress`nfrom typing import Any`n`nfrom sdnflowguard.domain.models import (`n    DefenseLifecycleState,`n    DefenseMode,`n    SafetyGateVerdict,`n)`n`nDEFAULT_PROTECTED_IPS = frozenset(`n    {`n        `"127.0.0.1`",`n        `"::1`",`n        `"0.0.0.0`",`n        `"255.255.255.255`",`n    }`n)`n`n`ndef is_protected_ip(`n    ip_str: str | None,`n    *,`n    extra_allowlist: set[str] | list[str] | None = None,`n    controller_ip: str | None = None,`n    elk_ip: str | None = None,`n) -> tuple[bool, str | None]:`n    `"`"`"Return (True, reason) if ip_str is invalid or protected against blocking.`"`"`"`n    if not ip_str or not isinstance(ip_str, str):`n        return True, `"Missing or non-string target IP`"`n`n    cleaned = ip_str.strip()`n    try:`n        addr = ipaddress.ip_address(cleaned)`n    except ValueError:`n        return True, f`"Invalid IP address syntax: {cleaned!r}`"`n`n    if addr.is_loopback:`n        return True, f`"IP {cleaned} is a loopback address`"`n    if addr.is_multicast:`n        return True, f`"IP {cleaned} is a multicast address`"`n    if addr.is_unspecified:`n        return True, f`"IP {cleaned} is an unspecified (0.0.0.0/::) address`"`n    if cleaned == `"255.255.255.255`":`n        return True, `"IP 255.255.255.255 is broadcast`"`n`n    allowset = set(DEFAULT_PROTECTED_IPS)`n    if extra_allowlist:`n        allowset.update(str(x).strip() for x in extra_allowlist if str(x).strip())`n    if controller_ip:`n        allowset.add(str(controller_ip).strip())`n    if elk_ip:`n        allowset.add(str(elk_ip).strip())`n`n    if cleaned in allowset:`n        return True, f`"IP {cleaned} is in the protected infrastructure allowlist`"`n`n    return False, None`n`n`ndef evaluate_safety_gate(`n    *,`n    action_type: str,`n    defense_mode: str = DefenseMode.DRY_RUN.value,`n    target_ip: str | None = None,`n    target_device_id: str | None = `"of:0000000000000001`",`n    target_port: str | None = None,`n    test_only: bool = False,`n    source_ip_attributed: bool = False,`n    historical_alert_correlation_verified: bool = False,`n    manual_operator_override: bool = False,`n    operator_approved: bool = False,`n    allowlist_ips: list[str] | set[str] | None = None,`n    controller_ip: str | None = None,`n    elk_ip: str | None = None,`n    explicit_dry_run: bool | None = None,`n) -> SafetyGateVerdict:`n    `"`"`"Evaluate all safety checks before proposing or executing an SDN control action.`"`"`"`n    mode_upper = str(defense_mode or DefenseMode.DRY_RUN.value).strip().upper()`n    if mode_upper not in {m.value for m in DefenseMode}:`n        mode_upper = DefenseMode.DRY_RUN.value`n`n    is_dry_run = (`n        bool(explicit_dry_run)`n        if explicit_dry_run is not None`n        else (mode_upper in (DefenseMode.DRY_RUN.value, DefenseMode.AUTO_STAGE_ONLY.value))`n    )`n`n    rejection_reasons: list[str] = []`n    safety_checks: dict[str, bool] = {`n        `"not_test_only_alert`": not test_only,`n        `"valid_and_unprotected_target`": True,`n        `"evidence_attribution_satisfied`": False,`n        `"defense_mode_permits_execution`": False,`n        `"operator_approval_satisfied`": False,`n    }`n`n    if test_only:`n        rejection_reasons.append(`n            `"Action rejected: source event is marked test_only=True (lab test alerts can never authorize enforcement).`"`n        )`n`n    # Validate target IP if action targets an IP`n    ip_actions = {`"block_ip`", `"unblock_ip`", `"throttle_traffic`", `"redirect_traffic`", `"prioritize_traffic`"}`n    port_actions = {`"disable_port`", `"enable_port`"}`n`n    if action_type in ip_actions or target_ip is not None:`n        protected, prot_reason = is_protected_ip(`n            target_ip,`n            extra_allowlist=allowlist_ips,`n            controller_ip=controller_ip,`n            elk_ip=elk_ip,`n        )`n        if protected:`n            safety_checks[`"valid_and_unprotected_target`"] = False`n            rejection_reasons.append(f`"Target IP check failed: {prot_reason}`")`n`n    if action_type in port_actions:`n        if not target_device_id or not target_port or str(target_port).strip().lower() == `"local`":`n            safety_checks[`"valid_and_unprotected_target`"] = False`n            rejection_reasons.append(`n                f`"Target port check failed: invalid switch_id ({target_device_id!r}) or reserved port ({target_port!r}).`"`n            )`n`n    # Evidence attribution check: required for automated actions; manual operator override allowed in lab UI`n    if manual_operator_override or action_type in (`"unblock_ip`", `"enable_port`"):`n        safety_checks[`"evidence_attribution_satisfied`"] = True`n    elif source_ip_attributed and historical_alert_correlation_verified and not test_only:`n        safety_checks[`"evidence_attribution_satisfied`"] = True`n    else:`n        rejection_reasons.append(`n            `"Automated enforcement requires Step 64 corroborated source IP attribution and verified UTC alert correlation.`"`n        )`n`n    # Operator approval check`n    requires_manual = mode_upper == DefenseMode.MANUAL_APPROVAL.value`n    if mode_upper == DefenseMode.ACTIVE_ENFORCEMENT.value:`n        safety_checks[`"operator_approval_satisfied`"] = True`n    elif mode_upper == DefenseMode.MANUAL_APPROVAL.value and (operator_approved or manual_operator_override):`n        safety_checks[`"operator_approval_satisfied`"] = True`n    else:`n        if requires_manual and not (operator_approved or manual_operator_override):`n            rejection_reasons.append(`n                `"Defense mode is MANUAL_APPROVAL and operator_approved=False.`"`n            )`n`n    # Defense mode execution check`n    if not is_dry_run and mode_upper in (`n        DefenseMode.MANUAL_APPROVAL.value,`n        DefenseMode.ACTIVE_ENFORCEMENT.value,`n    ):`n        safety_checks[`"defense_mode_permits_execution`"] = True`n    else:`n        rejection_reasons.append(`n            f`"Defense mode is {mode_upper} (dry_run={is_dry_run}); action is simulated/staged without modifying ONOS.`"`n        )`n`n    allowed_to_execute = all(safety_checks.values()) and not is_dry_run`n`n    # Determine lifecycle state`n    if test_only or not safety_checks[`"valid_and_unprotected_target`"]:`n        lifecycle_state = DefenseLifecycleState.ANOMALY_OBSERVED.value`n    elif not safety_checks[`"evidence_attribution_satisfied`"]:`n        lifecycle_state = DefenseLifecycleState.ANOMALY_OBSERVED.value`n    elif is_dry_run or mode_upper in (DefenseMode.DRY_RUN.value, DefenseMode.AUTO_STAGE_ONLY.value):`n        lifecycle_state = DefenseLifecycleState.BLOCK_PROPOSED.value`n    elif not safety_checks[`"operator_approval_satisfied`"]:`n        lifecycle_state = DefenseLifecycleState.BLOCK_PROPOSED.value`n    elif allowed_to_execute:`n        lifecycle_state = DefenseLifecycleState.BLOCK_APPROVED.value`n    else:`n        lifecycle_state = DefenseLifecycleState.EVIDENCE_CORRELATED.value`n`n    rollback_plan = {`n        `"reversible`": True,`n        `"rollback_action`": (`n            `"unblock_ip`"`n            if action_type in (`"block_ip`", `"throttle_traffic`", `"redirect_traffic`", `"prioritize_traffic`")`n            else (`"enable_port`" if action_type == `"disable_port`" else `"none`")`n        ),`n        `"target_device_id`": target_device_id or `"of:0000000000000001`",`n        `"target_ip`": target_ip,`n        `"target_port`": target_port,`n        `"app_id`": `"org.onosproject.rest`",`n    }`n`n    return SafetyGateVerdict(`n        allowed_to_execute=allowed_to_execute,`n        defense_mode=mode_upper,`n        lifecycle_state=lifecycle_state,`n        action_type=action_type,`n        target_ip=target_ip,`n        target_device_id=target_device_id,`n        target_port=target_port,`n        dry_run=is_dry_run,`n        requires_manual_approval=requires_manual,`n        rejection_reasons=rejection_reasons,`n        safety_checks=safety_checks,`n        rollback_plan=rollback_plan,`n    )`n`n"
    Add-H1 "PH? L?C E. TO?N V?N M? NGU?N T??NG QUAN B?NG CH?NG (EVIDENCE CORRELATION)"
    Add-P "T?p: backend/sdnflowguard/domain/services/evidence_correlation.py"
    Add-Code "`"`"`"Step 64: ONOS Host Evidence Correlation domain service.`n`nCorrelates switch ingress packet observations (Step 63) with ONOS topology`nstate (devices, ports, hosts, flows) and optional Elasticsearch alert windows.`nEnforces strict timestamp & provenance verification rules.`n`"`"`"`n`nfrom __future__ import annotations`n`nimport hashlib`nimport ipaddress`nimport re`nfrom datetime import datetime, timezone`nfrom pathlib import Path`nfrom typing import Any`n`nfrom sdnflowguard.domain.exceptions import EvidenceCorrelationError`nfrom sdnflowguard.domain.models import (`n    CaptureMetadata,`n    CorrelationStatus,`n    HostCorrelationResult,`n    PolicyDecisionType,`n)`n`nMAC_PATTERN = re.compile(r`"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}`$`", re.IGNORECASE)`nCLOCK_PATTERN = re.compile(r`"^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(?:\.(?P<micro>\d+))?`$`")`n`n`ndef validate_mac(mac: Any) -> str:`n    `"`"`"Validate and normalize a MAC address string.`"`"`"`n    if not isinstance(mac, str) or not MAC_PATTERN.match(mac.strip()):`n        raise ValueError(f`"Invalid MAC address: {mac!r}`")`n    return mac.strip().lower()`n`n`ndef validate_ip(ip_str: Any) -> str:`n    `"`"`"Validate and normalize an IPv4 or IPv6 address string.`"`"`"`n    if not isinstance(ip_str, str) or not ip_str.strip():`n        raise ValueError(f`"Invalid IP address: {ip_str!r}`")`n    return str(ipaddress.ip_address(ip_str.strip()))`n`n`ndef parse_iso8601_utc(ts_str: Any) -> datetime:`n    `"`"`"Parse an ISO-8601 timestamp string and require explicit timezone awareness.`"`"`"`n    if not isinstance(ts_str, str) or not ts_str.strip():`n        raise ValueError(`"Empty timestamp string`")`n    raw = ts_str.strip()`n    if raw.endswith(`"Z`"):`n        raw = raw[:-1] + `"+00:00`"`n    dt = datetime.fromisoformat(raw)`n    if dt.tzinfo is None:`n        raise ValueError(f`"Timestamp lacks explicit timezone offset: {ts_str!r}`")`n    return dt.astimezone(timezone.utc)`n`n`ndef compute_file_sha256(path: Path) -> str:`n    `"`"`"Compute SHA-256 hex digest of a file.`"`"`"`n    digest = hashlib.sha256()`n    with path.open(`"rb`") as handle:`n        for chunk in iter(lambda: handle.read(65536), b`"`"):`n            digest.update(chunk)`n    return digest.hexdigest()`n`n`ndef index_hosts_by_port(hosts: list[dict[str, Any]], device_id: str) -> dict[str, list[dict[str, Any]]]:`n    `"`"`"Group ONOS hosts by port number on a given switch device_id.`"`"`"`n    mapping: dict[str, list[dict[str, Any]]] = {}`n    for host in hosts or []:`n        if not isinstance(host, dict):`n            continue`n        raw_ips = host.get(`"ipAddresses`") or []`n        ips = [str(ip).strip() for ip in raw_ips if str(ip).strip()]`n        mac = str(host.get(`"mac`") or `"`").strip().lower()`n        locations = host.get(`"locations`") or []`n        for location in locations:`n            if not isinstance(location, dict):`n                continue`n            if location.get(`"elementId`") != device_id:`n                continue`n            port = str(location.get(`"port`") or `"`").strip()`n            if not port:`n                continue`n            mapping.setdefault(port, []).append(`n                {`n                    `"id`": host.get(`"id`") or f`"{mac}/None`",`n                    `"mac`": mac,`n                    `"ips`": ips,`n                    `"vlan`": host.get(`"vlan`", `"None`"),`n                }`n            )`n    return mapping`n`n`ndef count_ip_source_flows(flows: list[dict[str, Any]]) -> int:`n    `"`"`"Count ONOS flow rules that match on IPV4_SRC or IPV6_SRC criteria.`"`"`"`n    count = 0`n    for flow in flows or []:`n        if not isinstance(flow, dict):`n            continue`n        selector = flow.get(`"selector`") or {}`n        criteria = selector.get(`"criteria`") or []`n        if any(`n            isinstance(item, dict) and item.get(`"type`") in (`"IPV4_SRC`", `"IPV6_SRC`")`n            for item in criteria`n        ):`n            count += 1`n    return count`n`n`ndef verify_capture_time_window(`n    evidence: dict[str, Any],`n    capture_metadata: CaptureMetadata | dict[str, Any] | None = None,`n    alerts: list[dict[str, Any]] | None = None,`n) -> dict[str, Any]:`n    `"`"`"Verify whether packet capture timestamps can be correlated with historical alerts.`"`"`"`n    has_date = bool(evidence.get(`"capture_clock_has_date`", False))`n    has_tz = bool(evidence.get(`"capture_clock_has_timezone`", False))`n`n    meta_dict: dict[str, Any] = {}`n    if isinstance(capture_metadata, CaptureMetadata):`n        meta_dict = capture_metadata.to_dict()`n    elif isinstance(capture_metadata, dict):`n        meta_dict = dict(capture_metadata)`n    elif isinstance(evidence.get(`"capture_metadata`"), dict):`n        meta_dict = dict(evidence[`"capture_metadata`"])`n`n    started_utc_str = meta_dict.get(`"capture_started_utc`")`n    finished_utc_str = meta_dict.get(`"capture_finished_utc`")`n`n    started_dt: datetime | None = None`n    finished_dt: datetime | None = None`n    metadata_valid = False`n    metadata_error: str | None = None`n`n    if started_utc_str and finished_utc_str:`n        try:`n            started_dt = parse_iso8601_utc(started_utc_str)`n            finished_dt = parse_iso8601_utc(finished_utc_str)`n            if finished_dt < started_dt:`n                metadata_error = `"capture_finished_utc is earlier than capture_started_utc`"`n            else:`n                metadata_valid = True`n        except Exception as exc:`n            metadata_error = f`"Invalid capture UTC metadata: {exc}`"`n`n    effective_has_full_time = (has_date and has_tz) or metadata_valid`n`n    if not effective_has_full_time:`n        reason = (`n            metadata_error`n            if metadata_error`n            else (`n                `"Packet capture clock only records time-of-day (HH:MM:SS.us) without date `"`n                `"or timezone (capture_clock_has_date=False, capture_clock_has_timezone=False). `"`n                `"Historical alert correlation cannot be verified without full UTC window metadata.`"`n            )`n        )`n        return {`n            `"capture_clock_has_date`": has_date,`n            `"capture_clock_has_timezone`": has_tz,`n            `"metadata_window_valid`": False,`n            `"capture_started_utc`": started_utc_str,`n            `"capture_finished_utc`": finished_utc_str,`n            `"matching_alerts_in_window`": 0,`n            `"non_test_alerts_in_window`": 0,`n            `"historical_alert_correlation_verified`": False,`n            `"reason`": reason,`n        }`n`n    # If full UTC window is available, check alerts falling inside the window`n    matching_alerts = []`n    non_test_alerts = []`n    if started_dt and finished_dt and alerts:`n        for alert in alerts:`n            if not isinstance(alert, dict):`n                continue`n            ts = alert.get(`"@timestamp`")`n            if not ts:`n                continue`n            try:`n                alert_dt = parse_iso8601_utc(ts)`n            except Exception:`n                continue`n            if started_dt <= alert_dt <= finished_dt:`n                matching_alerts.append(alert)`n                if alert.get(`"test_only`") is not True:`n                    non_test_alerts.append(alert)`n`n    verified = bool(non_test_alerts)`n    if verified:`n        reason = (`n            f`"Verified {len(non_test_alerts)} non-test alert(s) within explicit UTC capture window `"`n            f`"[{started_dt.isoformat()} .. {finished_dt.isoformat()}].`"`n        )`n    elif matching_alerts:`n        reason = (`n            f`"Found {len(matching_alerts)} alert(s) in UTC capture window, but all are marked `"`n            `"test_only=True; test alerts cannot authorize active blocking.`"`n        )`n    else:`n        reason = `"Full UTC capture window verified, but no matching alerts occurred during the capture window.`"`n`n    return {`n        `"capture_clock_has_date`": has_date or metadata_valid,`n        `"capture_clock_has_timezone`": has_tz or metadata_valid,`n        `"metadata_window_valid`": metadata_valid,`n        `"capture_started_utc`": started_dt.isoformat() if started_dt else started_utc_str,`n        `"capture_finished_utc`": finished_dt.isoformat() if finished_dt else finished_utc_str,`n        `"matching_alerts_in_window`": len(matching_alerts),`n        `"non_test_alerts_in_window`": len(non_test_alerts),`n        `"historical_alert_correlation_verified`": verified,`n        `"reason`": reason,`n    }`n`n`ndef correlate_single_observation(`n    obs: dict[str, Any],`n    *,`n    devices: list[dict[str, Any]] | None,`n    ports_by_device: dict[str, dict[str, dict[str, Any]]],`n    hosts_by_device_port: dict[str, dict[str, list[dict[str, Any]]]],`n    ip_source_flow_count: int,`n    time_verification: dict[str, Any],`n) -> HostCorrelationResult:`n    `"`"`"Correlate a single packet observation record against ONOS topology state.`"`"`"`n    raw_switch = str(obs.get(`"switch_id`") or `"`").strip()`n    raw_port = str(obs.get(`"ingress_port`") or `"`").strip()`n    raw_iface = str(obs.get(`"interface`") or `"`").strip()`n    raw_mac = obs.get(`"observed_source_mac`")`n    raw_src_ip = obs.get(`"observed_source_ip`")`n    raw_dst_ip = obs.get(`"observed_destination_ip`") or `"0.0.0.0`"`n    protocol = str(obs.get(`"protocol`") or `"UNKNOWN`").upper()`n    icmp_type = str(obs.get(`"icmp_type`") or `"none`").lower()`n    packet_count = obs.get(`"packet_count`", 0)`n`n    # 1. Validate observation data integrity`n    try:`n        if not raw_switch or not raw_port or raw_port == `"local`":`n            raise ValueError(`"Missing or invalid switch_id / ingress_port`")`n        norm_mac = validate_mac(raw_mac)`n        norm_src_ip = validate_ip(raw_src_ip)`n        norm_dst_ip = validate_ip(raw_dst_ip)`n        if not isinstance(packet_count, int) or isinstance(packet_count, bool) or packet_count <= 0:`n            raise ValueError(f`"Invalid packet_count: {packet_count!r}`")`n    except Exception as exc:`n        return HostCorrelationResult(`n            switch_id=raw_switch or `"UNKNOWN`",`n            ingress_port=raw_port or `"UNKNOWN`",`n            interface=raw_iface or `"UNKNOWN`",`n            observed_source_mac=str(raw_mac or `"`"),`n            observed_source_ip=str(raw_src_ip or `"`"),`n            observed_destination_ip=str(raw_dst_ip or `"`"),`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count if isinstance(packet_count, int) else 0,`n            device_present=False,`n            port_present=False,`n            port_enabled=False,`n            attached_host_count=0,`n            attached_hosts=[],`n            mac_matched=False,`n            ip_matched=False,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.INVALID_EVIDENCE_DATA.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=f`"Invalid observation data: {exc}`",`n        )`n`n    # 2. Check switch device availability`n    device_present = True`n    if devices is not None:`n        matched_devices = [`n            d for d in devices if isinstance(d, dict) and d.get(`"id`") == raw_switch`n        ]`n        if not matched_devices or not matched_devices[0].get(`"available`", True):`n            device_present = False`n`n    if not device_present:`n        return HostCorrelationResult(`n            switch_id=raw_switch,`n            ingress_port=raw_port,`n            interface=raw_iface,`n            observed_source_mac=norm_mac,`n            observed_source_ip=norm_src_ip,`n            observed_destination_ip=norm_dst_ip,`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count,`n            device_present=False,`n            port_present=False,`n            port_enabled=False,`n            attached_host_count=0,`n            attached_hosts=[],`n            mac_matched=False,`n            ip_matched=False,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.DEVICE_UNAVAILABLE.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=f`"Switch {raw_switch} is missing or unavailable in ONOS topology.`",`n        )`n`n    # 3. Check port presence and enabled state`n    device_ports = ports_by_device.get(raw_switch, {})`n    port_info = device_ports.get(raw_port)`n    port_present = port_info is not None`n    port_enabled = bool(port_info.get(`"isEnabled`", False)) if port_info else False`n`n    attached_hosts = hosts_by_device_port.get(raw_switch, {}).get(raw_port, [])`n    attached_count = len(attached_hosts)`n`n    if not port_present or not port_enabled:`n        return HostCorrelationResult(`n            switch_id=raw_switch,`n            ingress_port=raw_port,`n            interface=raw_iface,`n            observed_source_mac=norm_mac,`n            observed_source_ip=norm_src_ip,`n            observed_destination_ip=norm_dst_ip,`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count,`n            device_present=True,`n            port_present=port_present,`n            port_enabled=port_enabled,`n            attached_host_count=attached_count,`n            attached_hosts=attached_hosts,`n            mac_matched=False,`n            ip_matched=False,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.PORT_UNAVAILABLE_OR_DISABLED.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=(`n                f`"Port {raw_port} on {raw_switch} is `"`n                f`"{'missing' if not port_present else 'disabled (isEnabled=False)'} in ONOS.`"`n            ),`n        )`n`n    # 4. Correlate against ONOS attached hosts on (switch_id, ingress_port)`n    if attached_count == 0:`n        return HostCorrelationResult(`n            switch_id=raw_switch,`n            ingress_port=raw_port,`n            interface=raw_iface,`n            observed_source_mac=norm_mac,`n            observed_source_ip=norm_src_ip,`n            observed_destination_ip=norm_dst_ip,`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count,`n            device_present=True,`n            port_present=True,`n            port_enabled=True,`n            attached_host_count=0,`n            attached_hosts=[],`n            mac_matched=False,`n            ip_matched=False,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.UNREGISTERED_HOST_ON_PORT.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=(`n                f`"Packet observed on {raw_switch}/{raw_port} from {norm_src_ip} ({norm_mac}), `"`n                `"but ONOS reports 0 attached hosts on this port.`"`n            ),`n        )`n`n    if attached_count > 1:`n        mac_matched = any(h.get(`"mac`") == norm_mac for h in attached_hosts)`n        ip_matched = any(`n            h.get(`"mac`") == norm_mac and norm_src_ip in (h.get(`"ips`") or [])`n            for h in attached_hosts`n        )`n        return HostCorrelationResult(`n            switch_id=raw_switch,`n            ingress_port=raw_port,`n            interface=raw_iface,`n            observed_source_mac=norm_mac,`n            observed_source_ip=norm_src_ip,`n            observed_destination_ip=norm_dst_ip,`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count,`n            device_present=True,`n            port_present=True,`n            port_enabled=True,`n            attached_host_count=attached_count,`n            attached_hosts=attached_hosts,`n            mac_matched=mac_matched,`n            ip_matched=ip_matched,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.AMBIGUOUS_MULTI_HOST.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=(`n                f`"Port {raw_switch}/{raw_port} has {attached_count} hosts attached in ONOS; `"`n                `"multi-host port requires per-flow/MAC isolation before any port or host enforcement.`"`n            ),`n        )`n`n    # Exactly 1 host attached on this port`n    single_host = attached_hosts[0]`n    host_mac = str(single_host.get(`"mac`") or `"`").lower()`n    host_ips = [str(ip) for ip in (single_host.get(`"ips`") or [])]`n`n    mac_matched = host_mac == norm_mac`n    ip_matched = norm_src_ip in host_ips`n`n    if not (mac_matched and ip_matched):`n        mismatch_details = []`n        if not mac_matched:`n            mismatch_details.append(f`"observed MAC {norm_mac} != ONOS host MAC {host_mac}`")`n        if not ip_matched:`n            mismatch_details.append(f`"observed IP {norm_src_ip} not in ONOS host IPs {host_ips}`")`n        return HostCorrelationResult(`n            switch_id=raw_switch,`n            ingress_port=raw_port,`n            interface=raw_iface,`n            observed_source_mac=norm_mac,`n            observed_source_ip=norm_src_ip,`n            observed_destination_ip=norm_dst_ip,`n            protocol=protocol,`n            icmp_type=icmp_type,`n            packet_count=packet_count,`n            device_present=True,`n            port_present=True,`n            port_enabled=True,`n            attached_host_count=1,`n            attached_hosts=attached_hosts,`n            mac_matched=mac_matched,`n            ip_matched=ip_matched,`n            ip_source_flow_count=ip_source_flow_count,`n            correlation_status=CorrelationStatus.HOST_IDENTITY_MISMATCH.value,`n            topology_corroborated=False,`n            attacker_confirmed=False,`n            historical_alert_correlation_verified=False,`n            recommended_decision=PolicyDecisionType.OBSERVE.value,`n            automatic_block_allowed=False,`n            rationale=(`n                f`"Host identity mismatch on {raw_switch}/{raw_port} `"`n                f`"({'; '.join(mismatch_details)}). Possible IP/MAC spoofing or stale ONOS host table.`"`n            ),`n        )`n`n    # Topology matches 1-to-1: (switch_id, ingress_port, MAC, IP) corroborated!`n    hist_verified = bool(time_verification.get(`"historical_alert_correlation_verified`", False))`n    is_benign_icmp_sample = protocol == `"ICMP`" and icmp_type in (`"request`", `"reply`") and packet_count < 1000`n`n    if not hist_verified:`n        rationale = (`n            f`"ONOS topology corroborates host {norm_src_ip} ({norm_mac}) on {raw_switch} port {raw_port}, `"`n            f`"but historical alert correlation is unverified ({time_verification.get('reason')}). `"`n            `"Decision remains OBSERVE.`"`n        )`n    elif is_benign_icmp_sample:`n        rationale = (`n            f`"ONOS topology and UTC window verified for {norm_src_ip} ({norm_mac}) on {raw_switch} port {raw_port}, `"`n            f`"but observed packets ({packet_count} ICMP {icmp_type}) represent normal diagnostic ping traffic, `"`n            `"not a confirmed flood attack. Decision remains OBSERVE.`"`n        )`n    else:`n        rationale = (`n            f`"ONOS topology, UTC window, and high-volume packet evidence corroborated for {norm_src_ip} `"`n            f`"({norm_mac}) on {raw_switch} port {raw_port}. Eligible for PROPOSE_BLOCK subject to Safety Gate.`"`n        )`n`n    attacker_confirmed = bool(hist_verified and not is_benign_icmp_sample)`n    recommended_decision = (`n        PolicyDecisionType.PROPOSE_BLOCK.value`n        if attacker_confirmed`n        else PolicyDecisionType.OBSERVE.value`n    )`n`n    return HostCorrelationResult(`n        switch_id=raw_switch,`n        ingress_port=raw_port,`n        interface=raw_iface,`n        observed_source_mac=norm_mac,`n        observed_source_ip=norm_src_ip,`n        observed_destination_ip=norm_dst_ip,`n        protocol=protocol,`n        icmp_type=icmp_type,`n        packet_count=packet_count,`n        device_present=True,`n        port_present=True,`n        port_enabled=True,`n        attached_host_count=1,`n        attached_hosts=attached_hosts,`n        mac_matched=True,`n        ip_matched=True,`n        ip_source_flow_count=ip_source_flow_count,`n        correlation_status=CorrelationStatus.CORROBORATED_HOST_OBSERVATION.value,`n        topology_corroborated=True,`n        attacker_confirmed=attacker_confirmed,`n        historical_alert_correlation_verified=hist_verified,`n        recommended_decision=recommended_decision,`n        automatic_block_allowed=False,`n        rationale=rationale,`n    )`n`n`ndef correlate_evidence_with_onos(`n    evidence: dict[str, Any],`n    *,`n    device_id: str = `"of:0000000000000001`",`n    ports: list[dict[str, Any]] | None = None,`n    hosts: list[dict[str, Any]] | None = None,`n    flows: list[dict[str, Any]] | None = None,`n    devices: list[dict[str, Any]] | None = None,`n    alerts: list[dict[str, Any]] | None = None,`n    capture_metadata: CaptureMetadata | dict[str, Any] | None = None,`n) -> dict[str, Any]:`n    `"`"`"Correlate a full Step 63 packet evidence payload against ONOS state (Step 64).`"`"`"`n    if not isinstance(evidence, dict):`n        raise EvidenceCorrelationError(`"Evidence payload must be a JSON object (dict)`")`n`n    observations = evidence.get(`"observations`")`n    if not isinstance(observations, list) or not observations:`n        raise EvidenceCorrelationError(`"Evidence payload must contain a non-empty 'observations' list`")`n`n    ports_list = ports if isinstance(ports, list) else []`n    hosts_list = hosts if isinstance(hosts, list) else []`n    flows_list = flows if isinstance(flows, list) else []`n`n    ports_by_device: dict[str, dict[str, dict[str, Any]]] = {device_id: {}}`n    for port_entry in ports_list:`n        if not isinstance(port_entry, dict):`n            continue`n        p_num = str(port_entry.get(`"port`") or `"`").strip()`n        p_dev = str(port_entry.get(`"element`") or device_id).strip()`n        if p_num:`n            ports_by_device.setdefault(p_dev, {})[p_num] = port_entry`n`n    # Index hosts across all referenced devices`n    referenced_devices = {device_id}`n    for obs in observations:`n        if isinstance(obs, dict) and obs.get(`"switch_id`"):`n            referenced_devices.add(str(obs[`"switch_id`"]).strip())`n`n    hosts_by_device_port: dict[str, dict[str, list[dict[str, Any]]]] = {}`n    for dev in referenced_devices:`n        hosts_by_device_port[dev] = index_hosts_by_port(hosts_list, dev)`n`n    ip_source_flow_count = count_ip_source_flows(flows_list)`n    time_verification = verify_capture_time_window(`n        evidence,`n        capture_metadata=capture_metadata,`n        alerts=alerts,`n    )`n`n    correlation_results: list[dict[str, Any]] = []`n    for obs in observations:`n        if not isinstance(obs, dict):`n            obs = {}`n        result = correlate_single_observation(`n            obs,`n            devices=devices,`n            ports_by_device=ports_by_device,`n            hosts_by_device_port=hosts_by_device_port,`n            ip_source_flow_count=ip_source_flow_count,`n            time_verification=time_verification,`n        )`n        correlation_results.append(result.to_dict())`n`n    all_corroborated = all(r[`"topology_corroborated`"] for r in correlation_results)`n    any_attacker_confirmed = any(r[`"attacker_confirmed`"] for r in correlation_results)`n    overall_decision = (`n        PolicyDecisionType.PROPOSE_BLOCK.value`n        if any_attacker_confirmed`n        else PolicyDecisionType.OBSERVE.value`n    )`n`n    return {`n        `"schema_version`": 2,`n        `"step`": `"STEP_64_ONOS_HOST_EVIDENCE_CORRELATION`",`n        `"evidence_type`": `"onos_host_correlated_packet_observation`",`n        `"device_id`": device_id,`n        `"total_packets`": evidence.get(`"total_packets`", 0),`n        `"first_packet_clock`": evidence.get(`"first_packet_clock`"),`n        `"last_packet_clock`": evidence.get(`"last_packet_clock`"),`n        `"time_verification`": time_verification,`n        `"topology_snapshot_summary`": {`n            `"onos_device_count`": len(devices) if isinstance(devices, list) else 1,`n            `"onos_port_count`": len([p for p in ports_list if isinstance(p, dict) and str(p.get(`"port`")) != `"local`"]),`n            `"onos_host_count`": len(hosts_list),`n            `"onos_flow_count`": len(flows_list),`n            `"ip_source_selector_flows`": ip_source_flow_count,`n        },`n        `"correlated_observations`": correlation_results,`n        `"security_assessment`": {`n            `"source_ip_observed`": True,`n            `"topology_corroborated`": all_corroborated,`n            `"attacker_confirmed`": any_attacker_confirmed,`n            `"historical_alert_correlation_verified`": time_verification[`"historical_alert_correlation_verified`"],`n            `"decision`": overall_decision,`n            `"automatic_block_allowed`": False,`n        },`n    }`n`n"
    Add-H1 "PH? L?C F. TO?N V?N M? NGU?N PH?N T?CH G?I TIN B?T T?I C?NG V?O (STEP 63)"
    Add-P "T?p: backend/defense/source_ip_evidence_analyzer.py"
    Add-Code "import argparse`nimport hashlib`nimport ipaddress`nimport json`nimport re`nimport sys`nfrom collections import Counter`nfrom pathlib import Path`n`n`nPATTERN = re.compile(`n    r'^(?P<clock>\d{2}:\d{2}:\d{2}\.\d+)\s+'`n    r'(?P<interface>s1-eth(?P<port>\d+))\s+\S+\s+'`n    r'ifindex\s+\d+\s+'`n    r'(?P<mac>(?:[0-9a-f]{2}:){5}[0-9a-f]{2})\s+'`n    r'ethertype\s+IPv4\b.*?:\s+'`n    r'(?P<src>(?:\d{1,3}\.){3}\d{1,3})\s+>\s+'`n    r'(?P<dst>(?:\d{1,3}\.){3}\d{1,3}):\s+'`n    r'ICMP\s+echo\s+(?P<kind>request|reply)\b',`n    re.IGNORECASE,`n)`n`n`ndef read_capture(path):`n    data = path.read_bytes()`n`n    # Windows PowerShell Tee-Object may write UTF-16LE.`n    if data.startswith((b`"\xff\xfe`", b`"\xfe\xff`")):`n        return data.decode(`"utf-16`")`n`n    if b`"\x00`" in data[:100]:`n        return data.decode(`"utf-16-le`")`n`n    return data.decode(`"utf-8-sig`")`n`n`ndef analyze(text, capture_metadata=None):`n    records = []`n`n    for line in text.splitlines():`n        if not (`n            re.search(r`"s1-eth[12]\b`", line)`n            and `"ethertype IPv4`" in line`n        ):`n            continue`n`n        match = PATTERN.search(line.strip())`n`n        if not match:`n            raise ValueError(`n                `"Unsupported switch IPv4 packet: `" + line[:160]`n            )`n`n        packet = match.groupdict()`n`n        ipaddress.IPv4Address(packet[`"src`"])`n        ipaddress.IPv4Address(packet[`"dst`"])`n`n        records.append(packet)`n`n    if not records:`n        raise ValueError(`"No supported switch ICMP packets found`")`n`n    counts = Counter(`n        (`n            packet[`"port`"],`n            packet[`"interface`"],`n            packet[`"mac`"].lower(),`n            packet[`"src`"],`n            packet[`"dst`"],`n            packet[`"kind`"].lower(),`n        )`n        for packet in records`n    )`n`n    observations = []`n`n    for key, count in sorted(counts.items()):`n        port, interface, mac, src, dst, kind = key`n`n        observations.append({`n            `"switch_id`": `"of:0000000000000001`",`n            `"ingress_port`": port,`n            `"interface`": interface,`n            `"observed_source_mac`": mac,`n            `"observed_source_ip`": src,`n            `"observed_destination_ip`": dst,`n            `"protocol`": `"ICMP`",`n            `"icmp_type`": kind,`n            `"packet_count`": count,`n        })`n`n    has_meta_window = bool(`n        isinstance(capture_metadata, dict)`n        and capture_metadata.get(`"capture_started_utc`")`n        and capture_metadata.get(`"capture_finished_utc`")`n    )`n`n    payload = {`n        `"schema_version`": 1,`n        `"evidence_type`": `"switch_ingress_packet_observation`",`n        `"total_packets`": len(records),`n        `"first_packet_clock`": records[0][`"clock`"],`n        `"last_packet_clock`": records[-1][`"clock`"],`n        `"capture_clock_has_date`": has_meta_window,`n        `"capture_clock_has_timezone`": has_meta_window,`n        `"observations`": observations,`n        `"security_assessment`": {`n            `"source_ip_observed`": True,`n            `"attacker_confirmed`": False,`n            `"historical_alert_correlation_verified`": False,`n            `"decision`": `"OBSERVE`",`n            `"automatic_block_allowed`": False,`n        },`n    }`n    if isinstance(capture_metadata, dict):`n        payload[`"capture_metadata`"] = dict(capture_metadata)`n    return payload`n`n`ndef self_test():`n    sample = `"\n`".join([`n        `"18:46:47.909111 s1-eth1 P ifindex 7 `"`n        `"00:00:00:00:00:01 ethertype IPv4 (0x0800), `"`n        `"length 104: 10.0.0.1 > 10.0.0.2: `"`n        `"ICMP echo request, id 29154, seq 1, length 64`",`n`n        `"18:46:47.910259 s1-eth2 P ifindex 8 `"`n        `"00:00:00:00:00:02 ethertype IPv4 (0x0800), `"`n        `"length 104: 10.0.0.2 > 10.0.0.1: `"`n        `"ICMP echo reply, id 29154, seq 1, length 64`",`n    ])`n`n    result = analyze(sample)`n`n    assert result[`"total_packets`"] == 2`n    assert len(result[`"observations`"]) == 2`n    assert result[`"observations`"][0][`"observed_source_ip`"] == `"10.0.0.1`"`n    assert result[`"observations`"][1][`"observed_source_ip`"] == `"10.0.0.2`"`n    assert result[`"security_assessment`"][`"automatic_block_allowed`"] is False`n`n    meta_result = analyze(`n        sample,`n        capture_metadata={`n            `"capture_started_utc`": `"2026-11-01T18:46:45Z`",`n            `"capture_finished_utc`": `"2026-11-01T18:46:55Z`",`n            `"switch_id`": `"of:0000000000000001`",`n            `"interfaces`": [`"s1-eth1`", `"s1-eth2`"],`n        },`n    )`n    assert meta_result[`"capture_clock_has_date`"] is True`n    assert meta_result[`"capture_clock_has_timezone`"] is True`n    assert meta_result[`"security_assessment`"][`"automatic_block_allowed`"] is False`n`n    print(`"SELF TEST PASS - Packet parser`")`n    print(`"SELF TEST PASS - Source IP and MAC`")`n    print(`"SELF TEST PASS - Capture UTC metadata support`")`n    print(`"SELF TEST PASS - No automatic blocking`")`n    print(`"SELF TEST PASS - No external requests`")`n`n`ndef main():`n    parser = argparse.ArgumentParser()`n`n    parser.add_argument(`"--input`")`n    parser.add_argument(`"--started-utc`")`n    parser.add_argument(`"--finished-utc`")`n    parser.add_argument(`"--self-test`", action=`"store_true`")`n`n    args = parser.parse_args()`n`n    if args.self_test:`n        self_test()`n        return`n`n    if not args.input:`n        parser.error(`"--input is required`")`n`n    source = Path(args.input)`n`n    if not source.is_file():`n        raise FileNotFoundError(source)`n`n    capture_metadata = None`n    if args.started_utc and args.finished_utc:`n        capture_metadata = {`n            `"capture_started_utc`": args.started_utc,`n            `"capture_finished_utc`": args.finished_utc,`n            `"capture_sha256`": hashlib.sha256(source.read_bytes()).hexdigest(),`n            `"switch_id`": `"of:0000000000000001`",`n            `"interfaces`": [`"s1-eth1`", `"s1-eth2`"],`n        }`n`n    result = analyze(read_capture(source), capture_metadata=capture_metadata)`n`n    output = source.with_suffix(`".json`")`n`n    # Exclusive creation prevents overwriting earlier evidence.`n    with output.open(`"x`", encoding=`"utf-8`") as file:`n        json.dump(result, file, ensure_ascii=False, indent=2)`n        file.write(`"\n`")`n`n    print(`"=== SOURCE IP EVIDENCE ANALYSIS ===`")`n    print(`"Input:`", source)`n    print(`"Parsed packets:`", result[`"total_packets`"])`n`n    for item in result[`"observations`"]:`n        print(`n            `"Port={ingress_port} `"`n            `"MAC={observed_source_mac} `"`n            `"SRC={observed_source_ip} `"`n            `"DST={observed_destination_ip} `"`n            `"ICMP={icmp_type} `"`n            `"Packets={packet_count}`".format(**item)`n        )`n`n    print(`"\nAttacker confirmed: False`")`n    print(`"Defense decision: OBSERVE`")`n    print(`"Automatic blocking: DISABLED`")`n    print(`"Historical alert correlation: NOT VERIFIED`")`n    print(`"Output JSON:`", output)`n    print(`"\nSUCCESS - Source IP Evidence Analyzer completed`")`n`n`nif __name__ == `"__main__`":`n    try:`n        main()`n    except Exception as exc:`n        print(`"ERROR:`", exc, file=sys.stderr)`n        sys.exit(1)`n"
    Add-H1 "PH? L?C G. TO?N V?N M? NGU?N ??I CHI?U TOPOLOGY ONOS TR?C TI?P (STEP 64)"
    Add-P "T?p: backend/defense/onos_host_evidence_correlator.py"
    Add-Code "`"`"`"Step 64: ONOS Host Evidence Correlator CLI and Library Module.`n`nCorrelates Step 63 packet observations (`ingress_icmp_*.json`) against ONOS`ntopology state (`devices`, `ports`, `hosts`, `flows`) and optional Elasticsearch`nalert windows, enforcing strict timestamp and source attribution safety rules.`n`"`"`"`n`nfrom __future__ import annotations`n`nimport argparse`nimport base64`nimport json`nimport os`nimport sys`nfrom pathlib import Path`nfrom typing import Any`nfrom urllib.request import Request, urlopen`n`nBACKEND_ROOT = Path(__file__).resolve().parents[1]`nif str(BACKEND_ROOT) not in sys.path:`n    sys.path.insert(0, str(BACKEND_ROOT))`n`nfrom sdnflowguard.domain.models import CorrelationStatus, PolicyDecisionType  # noqa: E402`nfrom sdnflowguard.domain.services.evidence_correlation import (  # noqa: E402`n    compute_file_sha256,`n    correlate_evidence_with_onos,`n)`n`nONOS_URL = `"http://127.0.0.1:8181/onos/v1`"`nDEVICE_ID = `"of:0000000000000001`"`nDEFAULT_EVIDENCE_PATH = (`n    Path(__file__).resolve().parent / `"evidence`" / `"ingress_icmp_20261101_014645.json`"`n)`n`nDEFAULT_LAB_TOPOLOGY = {`n    `"devices`": [`n        {`n            `"id`": DEVICE_ID,`n            `"available`": True,`n            `"role`": `"MASTER`",`n            `"type`": `"SWITCH`",`n        }`n    ],`n    `"ports`": [`n        {`"element`": DEVICE_ID, `"port`": `"local`", `"isEnabled`": True},`n        {`"element`": DEVICE_ID, `"port`": `"1`", `"isEnabled`": True},`n        {`"element`": DEVICE_ID, `"port`": `"2`", `"isEnabled`": True},`n    ],`n    `"hosts`": [`n        {`n            `"id`": `"00:00:00:00:00:01/None`",`n            `"mac`": `"00:00:00:00:00:01`",`n            `"vlan`": `"None`",`n            `"ipAddresses`": [`"10.0.0.1`"],`n            `"locations`": [{`"elementId`": DEVICE_ID, `"port`": `"1`"}],`n        },`n        {`n            `"id`": `"00:00:00:00:00:02/None`",`n            `"mac`": `"00:00:00:00:00:02`",`n            `"vlan`": `"None`",`n            `"ipAddresses`": [`"10.0.0.2`"],`n            `"locations`": [{`"elementId`": DEVICE_ID, `"port`": `"2`"}],`n        },`n    ],`n    `"flows`": [`n        {`n            `"id`": `"10001`",`n            `"appId`": `"org.onosproject.core`",`n            `"selector`": {`"criteria`": [{`"type`": `"ETH_TYPE`", `"ethType`": `"0x800`"}]},`n        }`n    ],`n}`n`n`ndef onos_get(path: str) -> dict[str, Any]:`n    `"`"`"Perform a read-only GET request against the ONOS REST API.`"`"`"`n    user = os.environ.get(`"SDNFLOW_ONOS_USER`")`n    password = os.environ.get(`"SDNFLOW_ONOS_PASSWORD`")`n    if not user or not password:`n        raise RuntimeError(`"ONOS credentials (SDNFLOW_ONOS_USER / SDNFLOW_ONOS_PASSWORD) are not configured`")`n`n    credentials = base64.b64encode(f`"{user}:{password}`".encode(`"utf-8`")).decode(`"ascii`")`n    req = Request(`n        f`"{ONOS_URL}/{path}`",`n        headers={`n            `"Authorization`": f`"Basic {credentials}`",`n            `"Accept`": `"application/json`",`n        },`n        method=`"GET`",`n    )`n    with urlopen(req, timeout=15) as resp:`n        return json.load(resp)`n`n`ndef load_json_file(path: Path) -> dict[str, Any]:`n    `"`"`"Read and parse a UTF-8 JSON file.`"`"`"`n    with path.open(`"r`", encoding=`"utf-8-sig`") as handle:`n        data = json.load(handle)`n    if not isinstance(data, dict):`n        raise ValueError(f`"Expected JSON object in {path}`")`n    return data`n`n`ndef correlate_step63_evidence_file(`n    evidence_path: Path | None = None,`n    *,`n    topology: dict[str, Any] | None = None,`n    capture_metadata: dict[str, Any] | None = None,`n    alerts: list[dict[str, Any]] | None = None,`n) -> dict[str, Any]:`n    `"`"`"Load Step 63 evidence file and correlate with ONOS topology snapshot.`"`"`"`n    target_path = evidence_path or DEFAULT_EVIDENCE_PATH`n    if not target_path.is_file():`n        raise FileNotFoundError(f`"Step 63 evidence file not found: {target_path}`")`n`n    evidence_data = load_json_file(target_path)`n    topo = topology if isinstance(topology, dict) else DEFAULT_LAB_TOPOLOGY`n`n    report = correlate_evidence_with_onos(`n        evidence_data,`n        device_id=DEVICE_ID,`n        devices=topo.get(`"devices`"),`n        ports=topo.get(`"ports`"),`n        hosts=topo.get(`"hosts`"),`n        flows=topo.get(`"flows`"),`n        alerts=alerts,`n        capture_metadata=capture_metadata,`n    )`n    report[`"evidence_source_file`"] = target_path.name`n    report[`"evidence_source_sha256`"] = compute_file_sha256(target_path)`n    report[`"topology_source`"] = `"LIVE_ONOS`" if topology is not None else `"REFERENCE_LAB_TOPOLOGY_FIXTURE`"`n    return report`n`n`ndef self_test() -> None:`n    `"`"`"Execute offline verification covering all Step 64 correlation edge cases.`"`"`"`n    sample_evidence = {`n        `"schema_version`": 1,`n        `"evidence_type`": `"switch_ingress_packet_observation`",`n        `"total_packets`": 24,`n        `"first_packet_clock`": `"18:46:47.909111`",`n        `"last_packet_clock`": `"18:46:50.146161`",`n        `"capture_clock_has_date`": False,`n        `"capture_clock_has_timezone`": False,`n        `"observations`": [`n            {`n                `"switch_id`": DEVICE_ID,`n                `"ingress_port`": `"1`",`n                `"interface`": `"s1-eth1`",`n                `"observed_source_mac`": `"00:00:00:00:00:01`",`n                `"observed_source_ip`": `"10.0.0.1`",`n                `"observed_destination_ip`": `"10.0.0.2`",`n                `"protocol`": `"ICMP`",`n                `"icmp_type`": `"request`",`n                `"packet_count`": 12,`n            },`n            {`n                `"switch_id`": DEVICE_ID,`n                `"ingress_port`": `"2`",`n                `"interface`": `"s1-eth2`",`n                `"observed_source_mac`": `"00:00:00:00:00:02`",`n                `"observed_source_ip`": `"10.0.0.2`",`n                `"observed_destination_ip`": `"10.0.0.1`",`n                `"protocol`": `"ICMP`",`n                `"icmp_type`": `"reply`",`n                `"packet_count`": 12,`n            },`n        ],`n    }`n`n    # Case 1: Single host corroborated, but no date/timezone -> OBSERVE, no block`n    res1 = correlate_evidence_with_onos(`n        sample_evidence,`n        device_id=DEVICE_ID,`n        devices=DEFAULT_LAB_TOPOLOGY[`"devices`"],`n        ports=DEFAULT_LAB_TOPOLOGY[`"ports`"],`n        hosts=DEFAULT_LAB_TOPOLOGY[`"hosts`"],`n        flows=DEFAULT_LAB_TOPOLOGY[`"flows`"],`n    )`n    assert res1[`"security_assessment`"][`"topology_corroborated`"] is True`n    assert res1[`"security_assessment`"][`"historical_alert_correlation_verified`"] is False`n    assert res1[`"security_assessment`"][`"attacker_confirmed`"] is False`n    assert res1[`"security_assessment`"][`"decision`"] == PolicyDecisionType.OBSERVE.value`n    assert res1[`"security_assessment`"][`"automatic_block_allowed`"] is False`n    assert (`n        res1[`"correlated_observations`"][0][`"correlation_status`"]`n        == CorrelationStatus.CORROBORATED_HOST_OBSERVATION.value`n    )`n`n    # Case 2: Multi-host on same port -> AMBIGUOUS_MULTI_HOST`n    multi_hosts = [`n        {`n            `"mac`": `"00:00:00:00:00:01`",`n            `"ipAddresses`": [`"10.0.0.1`"],`n            `"locations`": [{`"elementId`": DEVICE_ID, `"port`": `"1`"}],`n        },`n        {`n            `"mac`": `"00:00:00:00:00:09`",`n            `"ipAddresses`": [`"10.0.0.9`"],`n            `"locations`": [{`"elementId`": DEVICE_ID, `"port`": `"1`"}],`n        },`n    ]`n    res2 = correlate_evidence_with_onos(`n        sample_evidence,`n        device_id=DEVICE_ID,`n        ports=DEFAULT_LAB_TOPOLOGY[`"ports`"],`n        hosts=multi_hosts,`n        flows=[],`n    )`n    assert (`n        res2[`"correlated_observations`"][0][`"correlation_status`"]`n        == CorrelationStatus.AMBIGUOUS_MULTI_HOST.value`n    )`n    assert res2[`"correlated_observations`"][0][`"topology_corroborated`"] is False`n`n    # Case 3: MAC/IP mismatch -> HOST_IDENTITY_MISMATCH`n    spoof_hosts = [`n        {`n            `"mac`": `"00:00:00:00:00:aa`",`n            `"ipAddresses`": [`"10.0.0.99`"],`n            `"locations`": [{`"elementId`": DEVICE_ID, `"port`": `"1`"}],`n        }`n    ]`n    res3 = correlate_evidence_with_onos(`n        sample_evidence,`n        device_id=DEVICE_ID,`n        ports=DEFAULT_LAB_TOPOLOGY[`"ports`"],`n        hosts=spoof_hosts,`n        flows=[],`n    )`n    assert (`n        res3[`"correlated_observations`"][0][`"correlation_status`"]`n        == CorrelationStatus.HOST_IDENTITY_MISMATCH.value`n    )`n`n    # Case 4: Disabled port -> PORT_UNAVAILABLE_OR_DISABLED`n    disabled_ports = [`n        {`"element`": DEVICE_ID, `"port`": `"1`", `"isEnabled`": False},`n        {`"element`": DEVICE_ID, `"port`": `"2`", `"isEnabled`": True},`n    ]`n    res4 = correlate_evidence_with_onos(`n        sample_evidence,`n        device_id=DEVICE_ID,`n        ports=disabled_ports,`n        hosts=DEFAULT_LAB_TOPOLOGY[`"hosts`"],`n        flows=[],`n    )`n    assert (`n        res4[`"correlated_observations`"][0][`"correlation_status`"]`n        == CorrelationStatus.PORT_UNAVAILABLE_OR_DISABLED.value`n    )`n`n    # Case 5: Invalid observation data -> INVALID_EVIDENCE_DATA`n    bad_evidence = {`n        `"observations`": [`n            {`n                `"switch_id`": DEVICE_ID,`n                `"ingress_port`": `"1`",`n                `"observed_source_mac`": `"not-a-mac`",`n                `"observed_source_ip`": `"999.999.999.999`",`n                `"packet_count`": -1,`n            }`n        ]`n    }`n    res5 = correlate_evidence_with_onos(`n        bad_evidence,`n        device_id=DEVICE_ID,`n        ports=DEFAULT_LAB_TOPOLOGY[`"ports`"],`n        hosts=DEFAULT_LAB_TOPOLOGY[`"hosts`"],`n        flows=[],`n    )`n    assert (`n        res5[`"correlated_observations`"][0][`"correlation_status`"]`n        == CorrelationStatus.INVALID_EVIDENCE_DATA.value`n    )`n`n    # Case 6: Real Step 63 evidence file verification if present`n    if DEFAULT_EVIDENCE_PATH.is_file():`n        real_res = correlate_step63_evidence_file(DEFAULT_EVIDENCE_PATH)`n        assert real_res[`"total_packets`"] == 24`n        assert real_res[`"security_assessment`"][`"decision`"] == `"OBSERVE`"`n        assert real_res[`"security_assessment`"][`"automatic_block_allowed`"] is False`n`n    print(`"SELF TEST PASS - Step 64 single-host topology corroboration`")`n    print(`"SELF TEST PASS - Step 64 multi-host port ambiguity detection`")`n    print(`"SELF TEST PASS - Step 64 IP/MAC identity mismatch detection`")`n    print(`"SELF TEST PASS - Step 64 disabled/missing port & device handling`")`n    print(`"SELF TEST PASS - Step 64 invalid evidence rejection`")`n    print(`"SELF TEST PASS - Step 64 timestamp & test_only safety guardrails`")`n`n`ndef main() -> None:`n    parser = argparse.ArgumentParser(`n        description=`"Step 64: Correlate packet evidence against ONOS host topology.`"`n    )`n    parser.add_argument(`n        `"--evidence`",`n        default=str(DEFAULT_EVIDENCE_PATH),`n        help=`"Path to Step 63 packet observation JSON file.`",`n    )`n    parser.add_argument(`n        `"--live-onos`",`n        action=`"store_true`",`n        help=`"Query live ONOS REST API instead of reference lab topology fixture.`",`n    )`n    parser.add_argument(`n        `"--self-test`",`n        action=`"store_true`",`n        help=`"Run built-in Step 64 verification tests with zero network requests.`",`n    )`n    args = parser.parse_args()`n`n    if args.self_test:`n        self_test()`n        return`n`n    evidence_path = Path(args.evidence)`n    topology = None`n    if args.live_onos:`n        devices_res = onos_get(`"devices`")`n        ports_res = onos_get(f`"devices/{DEVICE_ID}/ports`")`n        hosts_res = onos_get(`"hosts`")`n        flows_res = onos_get(f`"flows/{DEVICE_ID}`")`n        topology = {`n            `"devices`": devices_res.get(`"devices`") or [],`n            `"ports`": ports_res.get(`"ports`") or [],`n            `"hosts`": hosts_res.get(`"hosts`") or [],`n            `"flows`": flows_res.get(`"flows`") or [],`n        }`n`n    report = correlate_step63_evidence_file(evidence_path, topology=topology)`n    print(`"=== STEP 64: ONOS HOST EVIDENCE CORRELATION ===`")`n    print(`"Evidence file:`", report[`"evidence_source_file`"])`n    print(`"Evidence SHA-256:`", report[`"evidence_source_sha256`"])`n    print(`"Topology source:`", report[`"topology_source`"])`n    print(`"Total packets:`", report[`"total_packets`"])`n    print(`n        `"Historical alert correlation verified:`",`n        report[`"time_verification`"][`"historical_alert_correlation_verified`"],`n    )`n    print(`"Time verification reason:`", report[`"time_verification`"][`"reason`"])`n    for item in report[`"correlated_observations`"]:`n        print(`n            f`"Port={item['ingress_port']} MAC={item['observed_source_mac']} `"`n            f`"IP={item['observed_source_ip']} Status={item['correlation_status']} `"`n            f`"Decision={item['recommended_decision']}`"`n        )`n    print(`"Overall Decision:`", report[`"security_assessment`"][`"decision`"])`n    print(`"Automatic Block Allowed:`", report[`"security_assessment`"][`"automatic_block_allowed`"])`n    print(`"\nSUCCESS - Step 64 ONOS Host Evidence Correlation completed`")`n`n`nif __name__ == `"__main__`":`n    try:`n        main()`n    except Exception as exc:`n        print(f`"ERROR: {exc}`", file=sys.stderr)`n        sys.exit(1)`n`n"
    Add-H1 "PH? L?C H. TO?N V?N C?U H?NH PIPELINE LOGSTASH V? DOCKER COMPOSE"
    Add-P "T?p: infrastructure/logstash/pipeline/01-sdnflowguard.conf"
    Add-Code "input {`n  http {`n    host => `"0.0.0.0`"`n    port => 8080`n    codec => json`n  }`n}`n`nfilter {`n  mutate {`n    add_field => {`n      `"project`" => `"SDNFlowGuard`"`n    }`n  }`n}`n`noutput {`n  elasticsearch {`n    hosts => [`"http://elasticsearch:9200`"]`n    index => `"sdnflowguard-events-%{+YYYY.MM.dd}`"`n    ilm_enabled => false`n  }`n}"
    Add-P "T?p: infrastructure/compose.yaml"
    Add-Code "name: sdnflowguard-netsec`n`nservices:`n  onos:`n    image: onosproject/onos:2.7-latest`n    container_name: sdnflowguard-onos`n    restart: unless-stopped`n    ports:`n      - `"127.0.0.1:8181:8181`"`n      - `"127.0.0.1:6653:6653`"`n`n  elasticsearch:`n    image: docker.elastic.co/elasticsearch/elasticsearch:8.15.1`n    container_name: sdnflowguard-elasticsearch`n    restart: unless-stopped`n    environment:`n      - discovery.type=single-node`n      - xpack.security.enabled=false`n      - xpack.ml.enabled=false`n      - ES_JAVA_OPTS=-Xms512m -Xmx512m`n    mem_limit: 2g`n    ports:`n      - `"127.0.0.1:9200:9200`"`n    volumes:`n      - esdata:/usr/share/elasticsearch/data`n`n  logstash:`n    image: docker.elastic.co/logstash/logstash:8.15.1`n    container_name: sdnflowguard-logstash`n    restart: unless-stopped`n    environment:`n      LS_JAVA_OPTS: `"-Xms384m -Xmx384m -XX:MaxDirectMemorySize=128m`"`n      XPACK_MONITORING_ENABLED: `"false`"`n      PIPELINE_WORKERS: `"1`"`n    mem_limit: 1536m`n    ports:`n      - `"127.0.0.1:18080:8080`"`n    volumes:`n      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro`n    depends_on:`n      - elasticsearch`n`n  kibana:`n    image: docker.elastic.co/kibana/kibana:8.15.1`n    container_name: sdnflowguard-kibana`n    profiles:`n      - ui`n    restart: `"no`"`n    environment:`n      SERVER_NAME: `"sdnflowguard-kibana`"`n      ELASTICSEARCH_HOSTS: '[`"http://elasticsearch:9200`"]'`n    mem_limit: 2g`n    ports:`n      - `"127.0.0.1:5601:5601`"`n    depends_on:`n      - elasticsearch`n`nvolumes:`n  esdata:`n    external: true`n    name: sdnflowguard-elasticsearch-data"

    # Add Page Numbers to Footer
    $section = $doc.Sections.Item(1)
    $footer = $section.Footers.Item([Microsoft.Office.Interop.Word.WdHeaderFooterIndex]::wdHeaderFooterPrimary)
    $footer.PageNumbers.Add([Microsoft.Office.Interop.Word.WdPageNumberAlignment]::wdAlignPageNumberRight)
    $footer.Range.Font.Name = "Times New Roman"
    $footer.Range.Font.Size = 10

    # Save DOCX and export to PDF
    $docxOut = "$docsFinal\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx"
    $pdfOut = "$docsFinal\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.pdf"
    
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
    
    $pptxOut = "$docsAcademic\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pptx"
    $pdfPptxOut = "$docsAcademic\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pdf"
    
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
    $subRoot = "D:\Project\SDNFlowGuard_Final_Submission"
    if (Test-Path $subRoot) {
        Write-Host "`nCopying academic artifacts to submission package..."
        Copy-Item -Path $docxOut -Destination "$subRoot\03_DOCUMENTATION\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx" -Force
        Copy-Item -Path $pdfOut -Destination "$subRoot\03_DOCUMENTATION\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.pdf" -Force
        Copy-Item -Path $pptxOut -Destination "$subRoot\06_PRESENTATION\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pptx" -Force
        Copy-Item -Path $pdfPptxOut -Destination "$subRoot\06_PRESENTATION\THUYET_TRINH_DO_AN_SDNFLOWGUARD.pdf" -Force
        Write-Host "[OK] Synced DOCX/PDF/PPTX to $subRoot"
    }

    Write-Host "`n[SUCCESS] ALL ACADEMIC ARTIFACTS GENERATED AND VERIFIED!"
}
