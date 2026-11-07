# -*- coding: utf-8 -*-
"""
Academic Text Builder for SDNFlowGuard Final Thesis (60+ pages in Word)
"""

def get_all_academic_sections():
    sections = []
    
    # Cover
    sections.append(("COVER", ""))
    
    # Preliminary pages
    sections.append(("H1", "LỜI CAM ĐOAN"))
    sections.append(("P", "Tôi xin cam đoan rằng đồ án chuyên đề 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' (Dự án SDNFlowGuard) là công trình nghiên cứu và thực nghiệm độc lập của tôi dưới sự định hướng của giảng viên hướng dẫn môn học Chuyên đề – Hệ thống mạng và bảo mật."))
    sections.append(("P", "Mọi số liệu thực nghiệm, nhật ký gói tin L2/L3, cấu hình bộ điều khiển ONOS, kết quả phân tích lưu lượng trên ELK Stack và mã nguồn trong hệ thống đều được triển khai, kiểm thử thực tế và ghi nhận một cách trung thực, minh bạch trên môi trường phòng thí nghiệm an toàn. Các tài liệu tham khảo và mã nguồn mở được kế thừa đều được trích dẫn và khai báo nguồn gốc rõ ràng theo chuẩn mực học thuật."))
    sections.append(("P", "Tôi hoàn toàn chịu trách nhiệm về tính trung thực, độc lập và chuẩn mực của các kết quả nghiên cứu được trình bày trong bản báo cáo này."))
    sections.append(("PAGE_BREAK", ""))

    sections.append(("H1", "LỜI CẢM ƠN"))
    sections.append(("P", "Để hoàn thành đồ án chuyên đề này, tôi xin bày tỏ lòng biết ơn sâu sắc nhất tới quý Thầy, Cô Khoa Mạng máy tính và Truyền thông, Trường Đại học Công nghệ Thông tin, những người đã tận tâm truyền đạt kiến thức nền tảng vững chắc về kiến trúc mạng, an ninh mạng, các hệ thống phân tán và phương pháp luận nghiên cứu khoa học trong suốt các năm học qua."))
    sections.append(("P", "Đặc biệt, tôi xin chân thành cảm ơn Thầy/Cô giảng viên phụ trách môn học Chuyên đề – Hệ thống mạng và bảo mật đã định hướng đề tài, tận tình giải đáp những vướng mắc kỹ thuật về bộ điều khiển SDN ONOS, kiến trúc OpenFlow, mô hình quản lý tập trung ELK Stack và nguyên lý phòng thủ phản ứng sự cố an toàn. Những góp ý quý báu của Thầy/Cô đã giúp tôi định hình được một phương pháp tiếp cận đúng đắn, xây dựng được hệ thống phòng thủ mạng an toàn dựa trên bằng chứng xác thực và hoàn thiện báo cáo đồ án với chất lượng chuyên môn cao nhất."))
    sections.append(("PAGE_BREAK", ""))

    sections.append(("H1", "TÓM TẮT ĐỒ ÁN"))
    sections.append(("P", "Trong kỷ nguyên hạ tầng số hiện đại, mạng điều khiển bằng phần mềm (Software-Defined Networking - SDN) và hệ thống quản lý sự kiện và thông tin an ninh (Security Information and Event Management - SIEM) đóng vai trò then chốt trong việc bảo vệ dữ liệu và dịch vụ doanh nghiệp. Đồ án 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' xây dựng nền tảng SDNFlowGuard kết hợp khả năng quan sát toàn cục của bộ điều khiển ONOS với sức mạnh phân tích sự kiện bảo mật tập trung của ELK Stack (Elasticsearch, Logstash, Kibana)."))
    sections.append(("P", "Điểm đột phá cốt lõi của đồ án là giải quyết triệt để vấn đề chặn nhầm (False Positive Blocking) trong phòng thủ mạng SDN thông qua nguyên lý: 'Host gắn trên cổng switch có cảnh báo không đồng nghĩa với kẻ tấn công đã được xác minh' (Attached Host != Verified Attacker). Hệ thống thiết lập chuỗi xác minh bằng chứng nguồn hai giai đoạn (Step 63 & Step 64) kết hợp phân tích gói tin bắt tại cổng vào (tcpdump) với bảng host/port/flow trực tiếp từ ONOS (LIVE_ONOS). Động cơ chính sách phòng thủ (Defense Policy Engine) và cổng an toàn (Safety Gate) mặc định vận hành ở chế độ an toàn DRY_RUN, ngăn chặn tuyệt đối việc khóa các địa chỉ IP hạ tầng (Loopback, Controller, ELK) và cảnh báo thử nghiệm (test_only: true), đồng thời cung cấp cơ chế hoàn nguyên (Rollback) toàn diện. Toàn bộ 50/50 bài kiểm thử tự động đạt 100% PASS, 5 kịch bản thực nghiệm End-to-End được chứng minh thành công trên mô hình Mininet OpenFlow 1.3 trong môi trường lab an toàn."))

    sections.append(("H1", "ABSTRACT"))
    sections.append(("P", "In the era of modern digital infrastructure, Software-Defined Networking (SDN) and Security Information and Event Management (SIEM) play a crucial role in safeguarding enterprise networks. The project 'Research and Deployment of Automated Network Defense via SDN Integrated with ELK Stack Monitoring' presents the SDNFlowGuard system, bridging the global control capabilities of the ONOS SDN Controller with the centralized analytics of the ELK Stack (Elasticsearch, Logstash, Kibana)."))
    sections.append(("P", "A core contribution of this research is resolving the false-positive blocking dilemma in automated SDN defense by enforcing the principle: 'Attached Host != Verified Attacker'. The architecture introduces a two-stage evidence verification pipeline (Step 63 & Step 64) that cross-correlates switch ingress packet captures with live ONOS topology and Elasticsearch alert windows. The Active Defense Safety Gate operates in fail-safe DRY_RUN mode by default, strictly safeguarding critical infrastructure IPs and test alerts, backed by a complete Rollback mechanism. The system is verified through 50/50 automated test cases (100% PASS) and 5 End-to-End lab scenarios on a Mininet OpenFlow 1.3 network."))
    sections.append(("PAGE_BREAK", ""))

    # Abbreviations
    sections.append(("H1", "DANH MỤC THUẬT NGỮ VÀ TỪ VIẾT TẮT"))
    abbrs = [
        ("SDN", "Software-Defined Networking", "Mạng điều khiển bằng phần mềm"),
        ("ONOS", "Open Network Operating System", "Hệ điều hành mạng mở / Bộ điều khiển SDN"),
        ("OVS", "Open vSwitch", "Bộ chuyển mạch ảo mã nguồn mở hỗ trợ OpenFlow"),
        ("ELK", "Elasticsearch, Logstash, Kibana", "Ngăn xếp phần mềm thu thập, lưu trữ, trực quan hóa log"),
        ("SIEM", "Security Information and Event Management", "Quản lý thông tin và sự kiện an ninh mạng"),
        ("SOC", "Security Operations Center", "Trung tâm điều hành an ninh mạng"),
        ("ACL", "Access Control List", "Danh sách kiểm soát truy cập"),
        ("PPS", "Packets Per Second", "Tốc độ gói tin trên giây"),
        ("BPS", "Bytes Per Second", "Tốc độ byte trên giây"),
        ("CIDR", "Classless Inter-Domain Routing", "Định tuyến liên miền không phân lớp"),
        ("REST", "Representational State Transfer", "Kiến trúc giao tiếp dịch vụ web qua HTTP"),
        ("ICMP", "Internet Control Message Protocol", "Giao thức điều khiển truyền thông điệp Internet"),
        ("TCP", "Transmission Control Protocol", "Giao thức điều khiển truyền vận tin cậy"),
        ("UDP", "User Datagram Protocol", "Giao thức dữ liệu người dùng không kết nối"),
        ("OSGi", "Open Services Gateway initiative", "Kiến trúc mô-đun dịch vụ Java trong Apache Karaf"),
        ("CRUD", "Create, Read, Update, Delete", "Các thao tác cơ bản trên cơ sở dữ liệu"),
        ("SHA-256", "Secure Hash Algorithm 256-bit", "Thuật toán băm mã hóa một chiều 256-bit"),
        ("E2E", "End-to-End", "Kiểm thử đầu-cuối từ đầu vào tới đầu ra hệ thống"),
        ("DoS", "Denial of Service", "Tấn công từ chối dịch vụ"),
        ("DDoS", "Distributed Denial of Service", "Tấn công từ chối dịch vụ phân tán"),
        ("WSL", "Windows Subsystem for Linux", "Môi trường Linux ảo hóa trên Windows"),
        ("API", "Application Programming Interface", "Giao diện lập trình ứng dụng"),
        ("JSON", "JavaScript Object Notation", "Định dạng trao đổi dữ liệu dạng chuỗi ký tự"),
        ("IP", "Internet Protocol", "Giao thức liên mạng"),
        ("MAC", "Media Access Control", "Địa chỉ điều khiển truy cập môi trường tầng liên kết dữ liệu")
    ]
    for ab in abbrs:
        sections.append(("P", f"{ab[0].ljust(10)}: {ab[1]} — {ab[2]}"))
    sections.append(("PAGE_BREAK", ""))

    # CHƯƠNG 1
    sections.append(("H1", "CHƯƠNG 1. GIỚI THIỆU VÀ TÍNH CẤP THIẾT CỦA ĐỀ TÀI"))
    sections.append(("H2", "1.1. Đặt vấn đề và bối cảnh an ninh mạng hiện đại"))
    sections.append(("P", "Trong kỷ nguyên chuyển đổi số và công nghệ đám mây, các hệ thống mạng doanh nghiệp và trung tâm dữ liệu đang phải đối mặt với áp lực xử lý lưu lượng khổng lồ. Cùng với sự gia tăng về lưu lượng hợp lệ, các cuộc tấn công mạng cũng ngày càng phát triển về mức độ phức tạp, tốc độ bùng phát và quy mô tàn phá. Các cuộc tấn công từ chối dịch vụ phân tán (DDoS), tấn công ngập lụt băng thông (Bandwidth Flooding), tấn công ngập lụt gói tin (SYN Flood, UDP Flood, ICMP Flood), cũng như các chiến dịch quét cổng thăm dò (Port Scanning) có thể làm cạn kiệt tài nguyên xử lý của máy chủ và thiết bị định tuyến trong khoảng thời gian rất ngắn."))
    sections.append(("P", "Một trong những bài toán hóc búa nhất của các trung tâm điều hành an ninh mạng (SOC) hiện nay là khoảng cách thời gian giữa thời điểm phát hiện bất thường (Mean Time to Detect - MTTD) và thời điểm thực thi biện pháp ngăn chặn (Mean Time to Respond - MTTR). Nếu thời gian phản ứng kéo dài, thiệt hại đối với tính sẵn sàng của dịch vụ là không thể bù đắp. Do đó, việc xây dựng một hệ thống có khả năng giám sát tập trung toàn diện và tự động hóa phản ứng phòng thủ mạng là một hướng nghiên cứu cấp thiết và có giá trị ứng dụng thực tiễn cao."))

    sections.append(("H2", "1.2. Thách thức trong giám sát và phòng thủ mạng truyền thống"))
    sections.append(("P", "Mạng truyền thống (Traditional IP Networks) có cấu trúc phân tán cao, trong đó mỗi thiết bị chuyển mạch (Switch) và định tuyến (Router) vừa phải đảm nhiệm mặt phẳng dữ liệu (chuyển tiếp gói tin theo bảng MAC/IP) vừa tự chạy các thuật toán định tuyến phân tán (OSPF, BGP, STP) trên mặt phẳng điều khiển cục bộ. Cấu trúc đóng kín này bộc lộ ba điểm nghẽn nghiêm trọng:"))
    sections.append(("P", "Thứ nhất, thiếu tầm nhìn toàn cục tập trung (Lack of Centralized Observability): Quản trị viên không thể quan sát toàn bộ mạng trên một màn hình thống nhất. Để kiểm tra lưu lượng, kỹ sư phải sử dụng các lệnh CLI thủ công hoặc cấu hình SNMP/NetFlow trên từng thiết bị riêng lẻ, dẫn tới việc thu thập số liệu phân mảnh và chậm trễ."))
    sections.append(("P", "Thứ hai, độ trễ và rủi ro khi thực thi chính sách bảo mật: Khi phát hiện luồng tấn công, việc tạo Access Control List (ACL) phải thực hiện trên từng cổng switch hoặc router biên. Thao tác cấu hình thủ công qua giao diện dòng lệnh dễ dẫn tới lỗi cú pháp, mâu thuẫn chính sách, hoặc làm gián đoạn các luồng lưu lượng quan trọng khác của doanh nghiệp."))
    sections.append(("P", "Thứ ba, sự thiếu liên kết giữa hệ thống phân tích log (SIEM) và hạ tầng mạng: Các hệ thống SIEM truyền thống rất mạnh trong việc thu thập nhật ký từ máy chủ, nhưng hoàn toàn thiếu khả năng điều khiển linh hoạt tầng mạng (Data Plane) để cô lập hoặc chuyển hướng luồng dữ liệu của kẻ tấn công ngay tại switch biên."))

    sections.append(("H2", "1.3. Nghịch lý cốt lõi trong phòng thủ SDN: 'Attached Host != Verified Attacker'"))
    sections.append(("P", "Kiến trúc Mạng điều khiển bằng phần mềm (Software-Defined Networking - SDN) ra đời mở ra khả năng lập trình toàn diện mạng thông qua bộ điều khiển tập trung (SDN Controller). Tuy nhiên, khi xây dựng hệ thống phòng thủ mạng tự động trên nền tảng SDN, nếu không có phương pháp luận chặt chẽ, hệ thống rất dễ rơi vào bẫy chặn nhầm (False Positive Blocking) làm gián đoạn hoạt động bình thường của người dùng hợp lệ."))
    sections.append(("P", "Nghịch lý này xuất phát từ bản chất của số liệu thống kê cổng OpenFlow (OpenFlow Port Statistics: rx_packets, tx_packets, rx_pps, tx_pps). Các bộ đếm trên cổng switch chỉ đo tổng khối lượng gói tin đi qua cổng vật lý hoặc ảo, hoàn toàn không phản ánh địa chỉ IP nguồn thực sự chứa trong phần thân của từng gói tin. Khi lưu lượng trên cổng tăng vọt vượt ngưỡng báo động, một giải pháp phòng thủ tự động ngây thơ sẽ tra cứu bảng Host của Controller và tự động phát lệnh khóa IP của host đang gắn vào cổng đó."))
    sections.append(("P", "Cách xử lý ngây thơ này phạm phải sai lầm nghiêm trọng bởi 4 lý do thực tế:"))
    sections.append(("P", "1. Host gắn trên cổng (Attached Host) có thể chỉ là nạn nhân đang bị ngập lụt bởi lưu lượng tấn công từ ngoài gửi tới, hoặc là máy chủ đang gửi phản hồi cho các yêu cầu hợp lệ."))
    sections.append(("P", "2. Một cổng switch có thể kết nối với một switch phụ, một access point hoặc một mạng con chứa nhiều máy trạm (Multi-host Port). Việc vội vàng khóa cổng hoặc khóa IP đầu tiên tìm thấy sẽ cắt đứt liên lạc của tất cả các máy trạm hợp lệ khác."))
    sections.append(("P", "3. Trong các phiên trao đổi ICMP Ping hai chiều (Echo Request và Echo Reply), cả cổng gửi và cổng nhận đều ghi nhận số gói tin tăng cao tương đương nhau. Nếu không phân tích sâu loại gói tin (ICMP Type) và chiều lưu lượng, hệ thống sẽ kết luận nhầm cả hai phía đều là kẻ tấn công."))
    sections.append(("P", "4. Các sự kiện đo kiểm tải nội bộ hoặc cảnh báo thử nghiệm (gắn cờ test_only: true) nếu không được phân tách minh bạch sẽ kích hoạt cơ chế phòng thủ thật, làm tê liệt hệ thống kiểm thử."))
    sections.append(("P", "Từ phân tích trên, đồ án xác lập nguyên tắc khoa học bất biến làm kim chỉ nam cho toàn bộ kiến trúc SDNFlowGuard: 'Host gắn trên cổng switch có cảnh báo không đồng nghĩa với kẻ tấn công đã được xác minh' (Attached Host != Verified Attacker). Mọi quyết định phòng thủ tự động bắt buộc phải dựa trên bằng chứng gói tin nguồn đã được đối chiếu chéo (corroborated evidence)."))

    sections.append(("H2", "1.4. Mục tiêu nghiên cứu và phạm vi học thuật của đề tài"))
    sections.append(("P", "Mục tiêu tổng quát của đề tài là: Nghiên cứu lý thuyết và triển khai thực nghiệm một nền tảng giám sát an ninh mạng tập trung kết hợp phòng thủ mạng tự động an toàn dựa trên kiến trúc SDN, tích hợp ngăn xếp ELK Stack, mang tên SDNFlowGuard."))
    sections.append(("P", "Các mục tiêu cụ thể có thể kiểm chứng bao gồm:"))
    sections.append(("P", "1. Thiết lập mô hình mạng SDN hoàn chỉnh gồm bộ điều khiển ONOS (Open Network Operating System 2.7.0), switch ảo Open vSwitch (OVS 3.7.1) chạy OpenFlow 1.3 và các host thử nghiệm trên Mininet trong môi trường WSL Ubuntu-26.04."))
    sections.append(("P", "2. Xây dựng pipeline thu thập số liệu mạng thời gian thực đẩy qua Logstash HTTP input (cổng 18080) vào Elasticsearch (cổng 9200) và trực quan hóa trên Kibana (cổng 5601) cùng bảng điều khiển React Dashboard (cổng 3000)."))
    sections.append(("P", "3. Hiện thực thuật toán phát hiện bất thường tốc độ gói tin cao kéo dài (Sustained High Packet Rate) có cơ chế lưu con trỏ trạng thái (Checkpoint) và cửa sổ trượt chồng lấp (Overlap Alert Monitor V2) để chống bỏ sót dữ liệu đến trễ."))
    sections.append(("P", "4. Thiết kế cơ chế xác minh bằng chứng nguồn hai giai đoạn: Step 63 phân tích gói tin bắt tại cổng vào switch (tcpdump) và Step 64 đối chiếu với bảng host/port/flow trực tiếp từ ONOS (LIVE_ONOS)."))
    sections.append(("P", "5. Xây dựng cổng an toàn Active Defense Safety Gate hoạt động mặc định ở chế độ DRY_RUN, bảo vệ tuyệt đối các địa chỉ IP hạ tầng và hỗ trợ quy trình hoàn nguyên (Rollback) toàn diện."))
    sections.append(("P", "6. Hoàn thiện bộ kiểm thử tự động 50/50 tests (100% PASS), bộ tài liệu học thuật đầy đủ và gói bàn giao chuẩn hóa phục vụ nghiệm thu đồ án."))

    # CHƯƠNG 2
    sections.append(("H1", "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VỀ SDN, OPENFLOW VÀ ONOS CONTROLLER"))
    sections.append(("H2", "2.1. Khái niệm và kiến trúc Software-Defined Networking (SDN)"))
    sections.append(("P", "Software-Defined Networking (SDN) là một bước chuyển biến mang tính cách mạng trong ngành công nghệ mạng máy tính. Khái niệm SDN xuất phát từ các nghiên cứu tiên phong tại Đại học Stanford và Đại học California, Berkeley vào những năm 2008, sau đó được tiêu chuẩn hóa và phát triển mạnh mẽ bởi Tổ chức Mạng Mở (Open Networking Foundation - ONF)."))
    sections.append(("P", "Kiến trúc SDN được phân chia thành ba tầng rõ rệt:"))
    sections.append(("P", "1. Tầng ứng dụng (Application Layer): Bao gồm các phần mềm quản trị mạng, hệ thống giám sát an ninh, ứng dụng định tuyến tối ưu đường đi, hệ thống phát hiện xâm nhập và tường lửa mạng. Các ứng dụng này tương tác với tầng điều khiển thông qua các giao diện lập trình hướng Bắc (Northbound APIs - thường là RESTful APIs)."))
    sections.append(("P", "2. Tầng điều khiển (Control Layer / Control Plane): Trung tâm xử lý thông minh của toàn bộ hệ thống, đại diện bởi SDN Controller (như ONOS, OpenDaylight, Ryu). Controller duy trì bức tranh toàn cảnh về trạng thái mạng (Network Information Base), xử lý các yêu cầu từ tầng ứng dụng và biên dịch thành các luật chuyển tiếp chi tiết."))
    sections.append(("P", "3. Tầng hạ tầng / chuyển tiếp dữ liệu (Infrastructure Layer / Data Plane): Bao gồm các thiết bị chuyển mạch vật lý hoặc ảo (như Open vSwitch). Thiết bị tầng này chỉ tập trung vào việc chuyển tiếp gói tin với tốc độ cao dựa trên các bảng luồng (Flow Tables) do Controller cài đặt xuống qua giao diện hướng Nam (Southbound APIs)."))

    sections.append(("H2", "2.2. Giao thức OpenFlow và mô hình xử lý gói tin OpenFlow 1.3"))
    sections.append(("P", "OpenFlow là giao thức chuẩn mở đầu tiên và phổ biến nhất định nghĩa quy tắc giao tiếp giữa Control Plane và Data Plane. Trong đề tài SDNFlowGuard, tiêu chuẩn OpenFlow 1.3 được áp dụng triệt để. Phiên bản OpenFlow 1.3 đưa ra mô hình xử lý đường ống nhiều bảng (Multiple Flow Tables / Pipeline Processing), khắc phục hoàn toàn nhược điểm đơn bảng của OpenFlow 1.0."))
    sections.append(("P", "Khi một gói tin đi vào switch OpenFlow 1.3, quy trình xử lý diễn ra theo các bước nghiêm ngặt:"))
    sections.append(("P", "Bước 1: Bắt đầu tại Bảng 0 (Table 0), switch trích xuất các trường thông tin trong tiêu đề gói tin (Header Fields) như Ingress Port, Ethernet Type, Source MAC, Destination MAC, IPv4 Source, IPv4 Destination, IP Protocol, Source Port, Destination Port."))
    sections.append(("P", "Bước 2: So khớp gói tin với các Flow Entry trong bảng theo thứ tự độ ưu tiên (Priority) giảm dần. Luật có priority cao nhất khớp với gói tin sẽ được chọn."))
    sections.append(("P", "Bước 3: Nếu tìm thấy luật so khớp (Match Hit), switch cập nhật bộ đếm (Counters), thực thi tập chỉ lệnh (Instructions) như cập nhật Action Set, hoặc chuyển gói tin sang bảng tiếp theo (Goto-Table n)."))
    sections.append(("P", "Bước 4: Nếu không có luật nào khớp (Table Miss), switch thực thi luật mặc định (Table-Miss Flow Entry) đã được cấu hình trước: hủy gói tin (Drop), hoặc đóng gói tin gửi lên Controller qua bản tin Packet-In (Controller Action)."))
    sections.append(("P", "Cấu trúc một Flow Entry trong OpenFlow 1.3 bao gồm 6 thành phần chính:"))
    sections.append(("P", "- Match Fields: Các trường lọc gói tin trên nhiều tầng giao thức (L2/L3/L4)."))
    sections.append(("P", "- Priority: Độ ưu tiên số nguyên (0 - 65535)."))
    sections.append(("P", "- Counters: Thống kê số gói tin, số byte và thời gian tồn tại."))
    sections.append(("P", "- Instructions: Chỉ lệnh xử lý (Apply-Actions, Clear-Actions, Write-Actions, Write-Metadata, Goto-Table)."))
    sections.append(("P", "- Timeouts: Idle Timeout (thời gian rỗi) và Hard Timeout (thời gian cố định)."))
    sections.append(("P", "- Cookie: Mã định danh 64-bit do Controller gán để quản lý và lọc luật."))

    sections.append(("H2", "2.3. Bộ điều khiển ONOS (Open Network Operating System)"))
    sections.append(("P", "ONOS là một bộ điều khiển SDN mã nguồn mở cấp doanh nghiệp được thiết kế chuyên biệt cho các nhà cung cấp dịch vụ mạng viễn thông và trung tâm dữ liệu quy mô lớn."))
    sections.append(("P", "Các thành phần cốt lõi của ONOS bao gồm:"))
    sections.append(("P", "1. Nền tảng OSGi (Apache Karaf): Cho phép kiến trúc hóa toàn bộ hệ thống thành các gói bundle độc lập. Các dịch vụ như Device Manager, Host Manager, Flow Rule Manager, Topology Manager hoạt động như các dịch vụ OSGi có thể kích hoạt hoặc hủy kích hoạt động mà không cần khởi động lại toàn bộ tiến trình Java."))
    sections.append(("P", "2. Hệ thống phân tán Atomix: Sử dụng thuật toán đồng thuận Raft để duy trì tính nhất quán của trạng thái cluster, hỗ trợ khả năng mở rộng quy mô Controller."))
    sections.append(("P", "3. Intent Framework: Cho phép ứng dụng khai báo mục đích kết nối cấp cao (High-level Connectivity Intents) như PointToPointIntent, HostToHostIntent. Bộ biên dịch Intent (Intent Compiler) sẽ tự động tính toán đường đi ngắn nhất và sinh ra các flow rules phù hợp trên từng switch."))
    sections.append(("P", "4. REST API v1 chuẩn hóa: Cung cấp các endpoint toàn diện cho phép hệ thống bên ngoài truy vấn và điều khiển mạng qua HTTP/JSON."))

    # CHƯƠNG 3
    sections.append(("H1", "CHƯƠNG 3. CƠ SỞ LÝ THUYẾT VỀ ELK STACK VÀ GIÁM SÁT AN NINH SIEM"))
    sections.append(("H2", "3.1. Tổng quan về Security Information and Event Management (SIEM)"))
    sections.append(("P", "SIEM là kiến trúc công nghệ trung tâm trong mọi Trung tâm điều hành an ninh mạng (SOC). Chức năng cốt lõi của SIEM bao gồm:"))
    sections.append(("P", "1. Thu thập dữ liệu tập trung (Data Ingestion): Tiếp nhận nhật ký từ hàng nghìn nguồn khác nhau."))
    sections.append(("P", "2. Chuẩn hóa dữ liệu (Data Normalization): Ánh xạ các trường dữ liệu khác biệt về một cấu trúc thống nhất (như Elastic Common Schema)."))
    sections.append(("P", "3. Phân tích và tương quan (Analytics & Correlation): Áp dụng các quy tắc logic và chuỗi thời gian để phát hiện hành vi tấn công."))
    sections.append(("P", "4. Lưu trữ và tra cứu (Storage & Retrieval): Lưu trữ dữ liệu an toàn phục vụ điều tra số (Digital Forensics)."))
    sections.append(("P", "5. Trực quan hóa và báo cáo (Visualization & Compliance): Xây dựng dashboard thời gian thực và xuất báo cáo tuân thủ."))

    sections.append(("H2", "3.2. Ngăn xếp ELK Stack trong kiến trúc SDNFlowGuard"))
    sections.append(("P", "Hệ thống SDNFlowGuard sử dụng trọn bộ ngăn xếp ELK Stack phiên bản 8.15.1:"))
    sections.append(("P", "1. Logstash: Cấu hình pipeline với plugin HTTP input lắng nghe tại cổng 18080. Logstash tiếp nhận các sự kiện JSON từ Python Collector, lọc bỏ các trường không hợp lệ, bổ sung siêu dữ liệu thời gian @timestamp và đẩy vào Elasticsearch."))
    sections.append(("P", "2. Elasticsearch: Lưu trữ tài liệu dưới dạng chỉ mục theo ngày sdnflowguard-events-YYYY.MM.DD. Elasticsearch sử dụng cấu trúc chỉ mục đảo (Inverted Index) cho tìm kiếm và cấu trúc dữ liệu cột (Doc Values) cho các phép tổng hợp số liệu (Aggregations) trên các trường số như total_pps, rx_bps, byte_count."))
    sections.append(("P", "3. Kibana: Cung cấp giao diện web trực quan tại cổng 5601. Cho phép xây dựng biểu đồ đường theo dõi lưu lượng thời gian thực của từng cổng switch và bảng cảnh báo an ninh."))

    # CHƯƠNG 4
    sections.append(("H1", "CHƯƠNG 4. PHÂN TÍCH YÊU CẦU VÀ THIẾT KẾ KIẾN TRÚC TỔNG THỂ"))
    sections.append(("H2", "4.1. Phân tích yêu cầu chức năng và phi chức năng"))
    sections.append(("P", "Hệ thống SDNFlowGuard được xây dựng nhằm đáp ứng trọn vẹn 10 yêu cầu chức năng (FR) và 6 yêu cầu phi chức năng (NFR):"))
    sections.append(("P", "Yêu cầu chức năng:"))
    sections.append(("P", "- FR-01: Quan sát trực tiếp topology mạng SDN từ ONOS qua REST API."))
    sections.append(("P", "- FR-02: Thu thập định kỳ thống kê cổng và luồng mạng, đẩy vào ELK Stack."))
    sections.append(("P", "- FR-03: Tự động phát hiện bất thường tốc độ gói tin cao kéo dài trên từng cổng switch."))
    sections.append(("P", "- FR-04: Phân tích bản bắt gói tin L2/L3 tại cổng vào switch (Step 63)."))
    sections.append(("P", "- FR-05: Đối chiếu bằng chứng gói tin với topology ONOS và cảnh báo ELK (Step 64)."))
    sections.append(("P", "- FR-06: Đánh giá chính sách phòng thủ và kiểm tra cổng an toàn Safety Gate."))
    sections.append(("P", "- FR-07: Cung cấp giao diện điều khiển mạng thủ công qua REST API."))
    sections.append(("P", "- FR-08: Hỗ trợ cơ chế hoàn nguyên (Rollback) luật và ghi nhật ký kiểm toán SQLite."))
    sections.append(("P", "- FR-09: Chuẩn hóa nhật ký đa nguồn SIEM (Firewall Syslog, Windows Event Log)."))
    sections.append(("P", "- FR-10: Cung cấp giao diện Web ReactJS 7 trang và xuất báo cáo tổng kết dạng PDF."))
    sections.append(("P", "Yêu cầu phi chức năng:"))
    sections.append(("P", "- NFR-01: An toàn mặc định (Fail-Safe by Default): Mặc định chạy ở chế độ DRY_RUN."))
    sections.append(("P", "- NFR-02: Toàn vẹn dữ liệu: Bảo toàn tuyệt đối cơ sở dữ liệu và bằng chứng lịch sử."))
    sections.append(("P", "- NFR-03: Bảo mật cấu hình: Không lưu secret cứng, bảo vệ API bằng API Key."))
    sections.append(("P", "- NFR-04: Khả năng chịu lỗi: Xử lý timeout an toàn khi dịch vụ ngoài gián đoạn."))
    sections.append(("P", "- NFR-05: Khả năng tái lập (Reproducibility): Triển khai dễ dàng qua Docker và scripts."))
    sections.append(("P", "- NFR-06: Quan sát được (Observability): Logging có cấu trúc kèm request_id."))

    sections.append(("H2", "4.2. Kiến trúc 4 mặt phẳng của hệ thống SDNFlowGuard"))
    sections.append(("P", "Hệ thống SDNFlowGuard được tổ chức thành 4 mặt phẳng độc lập nhưng liên kết chặt chẽ:"))
    sections.append(("P", "1. Data Plane (Mặt phẳng dữ liệu): Mạng ảo hóa Mininet chạy trên WSL Ubuntu-26.04 gồm switch Open vSwitch s1 (OpenFlow 1.3, Datapath ID of:0000000000000001) và hai host h1 (10.0.0.1/00:00:00:00:00:01 gắn cổng 1) và h2 (10.0.0.2/00:00:00:00:00:02 gắn cổng 2)."))
    sections.append(("P", "2. Control Plane (Mặt phẳng điều khiển): Bộ điều khiển ONOS Controller (Docker container sdnflowguard-onos) quản lý switch qua giao thức OpenFlow 1.3 (cổng 6653) và cung cấp REST API (cổng 8181)."))
    sections.append(("P", "3. SIEM Plane (Mặt phẳng giám sát SIEM): Ngăn xếp ELK gồm Logstash (cổng 18080 tiếp nhận HTTP events), Elasticsearch (cổng 9200 lưu trữ và truy vấn chỉ mục) và Kibana (cổng 5601 trực quan hóa)."))
    sections.append(("P", "4. Application Plane (Mặt phẳng ứng dụng): Gồm Flask REST API (cổng 5000), cơ sở dữ liệu SQLite (database/sdnflowguard.db), các Collector, Monitor V1/V2, Evidence Correlator Step 63/64, Defense Policy Engine và React Frontend (cổng 3000)."))

    sections.append(("H2", "4.3. Kiến trúc phần mềm Clean Architecture và Strangler Fig Pattern"))
    sections.append(("P", "Nhằm đảm bảo chất lượng kỹ thuật cao nhất và tuân thủ các nguyên lý thiết kế phần mềm hiện đại (SOLID, Separation of Concerns), hệ thống backend được tái cấu trúc theo mô hình Clean Architecture kết hợp Strangler Fig Pattern trong gói backend/sdnflowguard/:"))
    sections.append(("P", "- Domain Layer (Tầng miền nghiệp vụ): Là tầng trong cùng, độc lập hoàn toàn với framework và thư viện ngoài. Chứa các Value Objects (DefenseMode, CorrelationStatus, SafetyGateVerdict), Domain Services (EvidenceCorrelationService, SiemLogNormalizerService) và Policies (SafetyGate, DefensePolicy, RiskScoringPolicy)."))
    sections.append(("P", "- Application Layer (Tầng ứng dụng): Chứa các Use Cases điều phối luồng nghiệp vụ (EvaluateEvidenceCorrelationUseCase, EvaluateDefensePolicyUseCase, EvaluateControlActionSafetyUseCase, RunSiemCapabilityEvaluationUseCase)."))
    sections.append(("P", "- Infrastructure Layer (Tầng hạ tầng): Chứa các Adapter triển khai giao tiếp ngoài (SqliteRepository, OnosClient, ElasticsearchClient, LogstashClient, AppSettings) với timeout và error handling chặt chẽ."))
    sections.append(("P", "- Interfaces Layer (Tầng giao diện): Cung cấp các Blueprint routes cho Flask (/api/defense/*, /api/siem/*) và middleware bảo mật (check_api_key)."))

    # CHƯƠNG 5 & 6
    sections.append(("H1", "CHƯƠNG 5. HIỆN THỰC THU THẬP SỐ LIỆU VÀ PHÁT HIỆN BẤT THƯỜNG"))
    sections.append(("H2", "5.1. Phân hệ thu thập số liệu (Collectors)"))
    sections.append(("P", "Phân hệ thu thập số liệu gồm hai tiến trình chạy ngầm định kỳ bằng Python 3.10.10:"))
    sections.append(("P", "1. onos_elk_collector.py: Định kỳ mỗi 5 giây truy vấn các REST API /onos/v1/devices, /onos/v1/hosts, /onos/v1/flows từ ONOS. Collector tổng hợp số lượng switch, host, flow đang hoạt động, đóng gói thành sự kiện onos_network_summary và gửi tới Logstash qua cổng HTTP 18080."))
    sections.append(("P", "2. onos_port_elk_collector.py: Định kỳ truy vấn thống kê cổng /onos/v1/statistics/ports trên từng thiết bị switch. Collector lưu lại mẫu đo của chu kỳ trước và tính toán tốc độ truyền thông tức thời:"))
    sections.append(("CODE", "delta_time = current_timestamp - previous_timestamp (giây)\ndelta_rx_packets = current_rx_packets - previous_rx_packets\ndelta_tx_packets = current_tx_packets - previous_tx_packets\nrx_pps = delta_rx_packets / delta_time\ntx_pps = delta_tx_packets / delta_time\ntotal_pps = rx_pps + tx_pps\nrx_bps = (delta_rx_bytes * 8) / delta_time\ntx_bps = (delta_tx_bytes * 8) / delta_time"))
    sections.append(("P", "Các sự kiện onos_port_stats chứa đầy đủ các chỉ số này được gửi tới Logstash để lập chỉ mục vào Elasticsearch."))

    sections.append(("H2", "5.2. Động cơ phát hiện bất thường và cơ chế Overlap Monitor V2"))
    sections.append(("P", "Bộ phát hiện bất thường (sdn_port_anomaly_detector.py) phân tích chuỗi thời gian của từng cổng switch. Bất thường tốc độ cao kéo dài (SUSTAINED_HIGH_PACKET_RATE) được xác nhận khi tốc độ total_pps vượt ngưỡng threshold_pps trong consecutive_hits chu kỳ lấy mẫu liên tiếp."))
    sections.append(("P", "Nếu khoảng cách thời gian giữa hai mẫu đo vượt quá max_gap_sec (25 giây), hệ thống xác định việc thu thập bị gián đoạn và đặt lại streak về 0 để tránh kết luận sai."))
    sections.append(("P", "Hệ thống triển khai hai phiên bản Monitor:"))
    sections.append(("P", "- Reliable Monitor V1: Lưu trữ con trỏ thời gian last_processed_timestamp nguyên tử qua file khóa .tmp vào thư mục backend/collectors/state/ để khôi phục trạng thái sau khi khởi động lại."))
    sections.append(("P", "- Overlap Alert Monitor V2: Nâng cấp cơ chế cửa sổ trượt có vùng chồng lấp (overlap_sec = 30s) kết hợp bộ lọc watermark. Cơ chế này giải quyết triệt để vấn đề các mẫu thống kê cổng đến trễ (late-arriving telemetry) qua ranh giới chu kỳ quét, đồng thời sinh khóa băm SHA-256 alert_key duy nhất từ (alert_type, device_id, port, first_seen, last_seen) để loại bỏ 100% cảnh báo trùng lặp."))

    # CHƯƠNG 7 & 8
    sections.append(("H1", "CHƯƠNG 6. CƠ CHẾ TƯƠNG QUAN BẰNG CHỨNG NGUỒN VÀ AN TOÀN PHÒNG THỦ"))
    sections.append(("H2", "6.1. Chuỗi xác minh bằng chứng nguồn hai giai đoạn (Steps 63–64)"))
    sections.append(("P", "Để giải quyết triệt để nghịch lý 'Attached Host != Verified Attacker', đề tài thiết lập quy trình xác minh bằng chứng nguồn L2/L3 nghiêm ngặt:"))
    sections.append(("P", "Giai đoạn Step 63 (source_ip_evidence_analyzer.py):"))
    sections.append(("P", "Hệ thống thu thập bản bắt gói tin thực tế bằng tcpdump trên các giao diện mạng cổng vào của switch (s1-eth1 tương ứng cổng 1, s1-eth2 tương ứng cổng 2). Trình phân tích hỗ trợ giải mã cả định dạng UTF-8 và UTF-16LE, trích xuất cấu trúc dữ liệu bằng chứng gồm: observed_source_mac, observed_source_ip, observed_destination_ip, protocol, icmp_type, packet_count, mốc giờ cục bộ và siêu dữ liệu cửa sổ thời gian UTC (capture_started_utc, capture_finished_utc)."))
    sections.append(("P", "Giai đoạn Step 64 (onos_host_evidence_correlator.py):"))
    sections.append(("P", "Bằng chứng gói tin Step 63 được đối chiếu chéo trực tiếp với topology thời gian thực từ ONOS (LIVE_ONOS: /onos/v1/devices, /onos/v1/hosts, /onos/v1/flows). Thuật toán phân loại kết quả đối chiếu thành 4 trạng thái rõ ràng:"))
    sections.append(("P", "1. CORROBORATED_HOST_OBSERVATION: Địa chỉ MAC và IP trong gói tin khớp chính xác tuyệt đối 100% với host duy nhất đã đăng ký trên cổng đó trong bảng quản lý của ONOS."))
    sections.append(("P", "2. AMBIGUOUS_MULTI_HOST: Cổng switch có từ 2 host trở lên cùng kết nối -> Hệ thống từ chối lệnh chặn cổng để tránh ảnh hưởng host vô tội."))
    sections.append(("P", "3. HOST_IDENTITY_MISMATCH: Gói tin mang địa chỉ IP/MAC khác với host đã đăng ký trên cổng trong ONOS -> Cảnh báo dấu hiệu tấn công giả mạo (IP/MAC Spoofing)."))
    sections.append(("P", "4. UNREGISTERED_HOST_ON_PORT: Cổng chưa có thông tin host đăng ký trong ONOS."))
    sections.append(("P", "Hệ thống chỉ xác nhận attacker_confirmed = True khi và chỉ khi: (1) Trạng thái đối chiếu đạt CORROBORATED; (2) Cửa sổ thời gian UTC của bản bắt gói trùng khớp với cửa sổ cảnh báo bất thường trong Elasticsearch; và (3) Lưu lượng có tính chất bất đối xứng của cuộc tấn công DoS thay vì trao đổi ICMP hai chiều đối xứng."))

    sections.append(("H2", "6.2. Cổng an toàn Active Defense Safety Gate và Cơ chế Rollback"))
    sections.append(("P", "Động cơ an toàn phòng thủ (sdnflowguard/domain/policies/safety_gate.py) kiểm soát mọi yêu cầu điều khiển mạng trước khi gửi tới ONOS thông qua 5 chốt chặn bắt buộc:"))
    sections.append(("P", "- Chốt 1 (not_test_only_alert): Mọi cảnh báo có cờ test_only = True bị chặn lại ngay lập tức, không bao giờ được phép thực thi lệnh chặn."))
    sections.append(("P", "- Chốt 2 (valid_and_unprotected_target): Kiểm tra định dạng IPv4/CIDR. Bảo vệ tuyệt đối dải địa chỉ loopback (127.0.0.0/8), địa chỉ IP của SDN Controller, IP của ELK Server, địa chỉ Multicast (224.0.0.0/4), Broadcast (255.255.255.255) và danh sách địa chỉ trắng (allowlist_ips)."))
    sections.append(("P", "- Chốt 3 (evidence_attribution_satisfied): Nghiêm cấm chặn IP chỉ từ cảnh báo cổng nếu thiếu bằng chứng quy gán nguồn IP đã đối chiếu thành công."))
    sections.append(("P", "- Chốt 4 (defense_mode_permits_execution): Mặc định SDNFLOW_DEFENSE_MODE = DRY_RUN. Trong chế độ này, hệ thống chỉ tạo bản xem trước luật (acl_rule_preview và flow_rule_preview) và ghi nhận mô phỏng (DRY_RUN_SIMULATED), tuyệt đối không gửi lệnh POST/DELETE làm thay đổi trạng thái switch."))
    sections.append(("P", "- Chốt 5 (operator_approval_satisfied): Trong chế độ ACTIVE_ENFORCEMENT, hành động vẫn được giữ ở trạng thái ACTIVE_ENFORCEMENT_PENDING_APPROVAL cho tới khi có phê duyệt chủ động từ người vận hành."))
    sections.append(("P", "Mọi quyết định đều đính kèm một kế hoạch hoàn nguyên (rollback_plan) chi tiết, cho phép hủy bỏ luật chặn tức thì qua API /api/defense/rollback hoặc /api/unblock và ghi vết kiểm toán đầy đủ vào bảng actions trong SQLite."))

    # CHƯƠNG 7
    sections.append(("H1", "CHƯƠNG 7. BẢNG ĐIỀU KHIỂN REACTJS VÀ KẾT QUẢ THỰC NGHIỆM"))
    sections.append(("H2", "7.1. Giao diện quản trị mạng SDNFlowGuard"))
    sections.append(("P", "Giao diện người dùng được xây dựng trên React 18, chạy trên cổng 3000, đã được đồng bộ hóa hoàn toàn với bộ nhận diện thương hiệu SDNFlowGuard (biểu tượng chiếc khiên bảo mật mạng) gồm 7 trang chức năng chuyên nghiệp:"))
    sections.append(("P", "- Dashboard: Hiển thị trạng thái các dịch vụ, tổng số luồng, cảnh báo an ninh, tích hợp biểu đồ lưu lượng cổng ELK và bảng cảnh báo thời gian thực."))
    sections.append(("PIC", "dashboard_overview.png", "Hình 7.1: Bảng điều khiển trung tâm SDNFlowGuard Dashboard"))
    sections.append(("P", "- Traffic Overview: Quan sát sơ đồ topology mạng SDN, trạng thái switch, host và danh sách luật OpenFlow trực tiếp từ ONOS."))
    sections.append(("PIC", "traffic_overview.png", "Hình 7.2: Quản lý luồng và quan sát trạng thái mạng SDN trực tiếp"))
    sections.append(("P", "- Anomaly Detection: Theo dõi các điểm rủi ro bất thường được phát hiện bởi các Monitor."))
    sections.append(("PIC", "anomaly_detection.png", "Hình 7.3: Màn hình phát hiện lưu lượng bất thường và đánh giá rủi ro"))
    sections.append(("P", "- Manual Traffic Control: Cung cấp giao diện kiểm soát lưu lượng thủ công qua cổng an toàn Safety Gate."))
    sections.append(("PIC", "manual_traffic_control.png", "Hình 7.4: Giao diện điều khiển lưu lượng mạng có kiểm soát"))
    sections.append(("P", "- Reports & Settings: Xuất báo cáo tổng kết hệ thống dạng PDF chuẩn %PDF-1.4 và cấu hình tham số hoạt động."))
    sections.append(("PIC", "reports.png", "Hình 7.5: Màn hình xem và xuất báo cáo an ninh mạng"))
    sections.append(("PIC", "chatbot.png", "Hình 7.6: Trợ lý an ninh mạng cục bộ (Security Assistant)"))

    sections.append(("H2", "7.2. Kết quả 5 kịch bản kiểm thử End-to-End thực tế trên Lab"))
    sections.append(("P", "Hệ thống đã trải qua 5 kịch bản thực nghiệm End-to-End trực tiếp trên môi trường lab Mininet OpenFlow 1.3 và ONOS:"))
    sections.append(("P", "Kịch bản 01 (Mạng bình thường): Mininet single,2 truyền gói tin ICMP hợp lệ giữa h1 (10.0.0.1) và h2 (10.0.0.2). Kết quả pingAll() đạt 0.0% packet loss (RTT trung bình 1.154 ms). Collector thu thập thành công 4 flow rules từ ONOS đẩy vào Logstash/Elasticsearch. Động cơ phòng thủ kết luận ALLOW, không có luật chặn nào được đề xuất (PROPOSE_BLOCK: 0)."))
    sections.append(("P", "Kịch bản 02 (Lưu lượng bất thường & Cảnh báo): Phát sinh lưu lượng tốc độ cao qua ngưỡng 4.0 PPS. Overlap Alert Monitor V2 phát hiện chính xác 10 ứng viên bất thường, sinh khóa băm SHA-256 alert_key duy nhất và đẩy 16 cảnh báo vào Elasticsearch sdnflowguard-events-*, hiển thị tức thì trên React UI."))
    sections.append(("P", "Kịch bản 03 (Tương quan bằng chứng & Đánh giá chính sách): Chạy onos_host_evidence_correlator.py đối chiếu bản bắt gói tin với LIVE_ONOS. Cả hai cổng switch s1 đạt CORROBORATED_HOST_OBSERVATION. Tuy nhiên, do lưu lượng là cặp ping đối xứng và thiếu giao thoa thời gian UTC với cảnh báo thật, hệ thống đưa ra phán quyết chính xác OBSERVE (Automatic Block Allowed: False). Cổng an toàn từ chối thành công các yêu cầu khóa IP 127.0.0.1 và test_only."))
    sections.append(("P", "Kịch bản 04 (Phòng thủ SDN có kiểm soát): Thực hiện thử nghiệm Stage A (DRY RUN). Hệ thống sinh đầy đủ acl_rule_preview và flow_rule_preview (priority 40010, timeout 300s, selector IPV4_SRC=10.0.0.1/32, treatment DROP). Stage B được giữ an toàn ở trạng thái ACTIVE_ENFORCEMENT_PENDING_APPROVAL."))
    sections.append(("P", "Kịch bản 05 (Hoàn nguyên và Khôi phục kết nối): Kích hoạt cơ chế Rollback unblock_ip. Kiểm tra lại kết nối giữa h1 và h2 trong Mininet xác nhận 4/4 gói tin truyền thông thành công, 0% packet loss, mạng lab được khôi phục nguyên vẹn."))

    sections.append(("H2", "7.3. Kết quả bộ kiểm thử tự động (50/50 Tests PASS)"))
    sections.append(("P", "Toàn bộ bộ kiểm thử tự động gồm 50 bài kiểm thử (24 Unit, 12 Integration, 5 Contract, 8 Safety, 1 E2E) và 4 CLI Self-Tests đã được thực thi bằng Python 3.10.10 (-B) qua lệnh scripts/run_all_tests.ps1. Kết quả đạt 100% PASS trong 0.514 giây. Mã băm SHA-256 của cơ sở dữ liệu chính database/sdnflowguard.db được bảo toàn tuyệt đối 100%: 3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9."))

    # CHƯƠNG 8
    sections.append(("H1", "CHƯƠNG 8. ĐÁNH GIÁ BẢO MẬT, ĐỘ TIN CẬY VÀ HIỆU NĂNG"))
    sections.append(("H2", "8.1. Đánh giá tính bảo mật và kiểm toán mã nguồn"))
    sections.append(("P", "Kiểm toán bảo mật xác nhận hệ thống đã loại bỏ hoàn toàn các mật khẩu cứng trong mã nguồn backend/run.py và cấu hình .env.example. Các thao tác quản trị nhạy cảm được bảo vệ bằng cơ chế xác thực X-SDNFlow-API-Key. Cổng an toàn ngăn chặn 100% nguy cơ tấn công từ chối dịch vụ tự gây ra (Self-inflicted DoS) nhờ cơ chế miễn nhiễm địa chỉ hạ tầng."))
    
    sections.append(("H2", "8.2. Đánh giá độ tin cậy và khả năng chịu lỗi"))
    sections.append(("P", "Khi bộ điều khiển ONOS hoặc Elasticsearch tạm thời ngoại tuyến, toàn bộ API backend và Chatbot đều có cơ chế ngắt mạch an toàn với timeout từ 2 đến 3 giây, trả về phản hồi suy giảm có kiểm soát (Graceful Degradation) thay vì làm sập ứng dụng."))

    # CHƯƠNG 9
    sections.append(("H1", "CHƯƠNG 9. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN"))
    sections.append(("H2", "9.1. Hạn chế kỹ thuật hiện tại"))
    sections.append(("P", "1. Mô hình thực nghiệm hiện tại tập trung kiểm chứng sâu trên topology đơn switch SingleSwitchTopo(k=2). Việc mở rộng lên topology đa switch quy mô lớn đòi hỏi thuật toán định vị cổng biên (Ingress Port Localization) phức tạp hơn."))
    sections.append(("P", "2. Các nguồn nhật ký Firewall Syslog và Windows Server Event Log hiện được kiểm chứng thông qua bộ dữ liệu mẫu chuẩn hóa (FIXTURE_SIMULATION), sẵn sàng kết nối với tác tử Filebeat/Winlogbeat trong thực tế."))
    sections.append(("P", "3. Thao tác chặn trực tiếp trên ONOS (Stage B) được giữ ở trạng thái chờ phê duyệt của người vận hành để tuân thủ tuyệt đối an toàn phòng lab."))

    sections.append(("H2", "9.2. Hướng phát triển trong tương lai"))
    sections.append(("P", "1. Mở rộng thử nghiệm trên các kiến trúc mạng trung tâm dữ liệu đa tầng (Spine-Leaf, Fat-Tree)."))
    sections.append(("P", "2. Tích hợp các mô hình học máy nhẹ (Isolation Forest, Autoencoder) trên chuỗi thời gian cổng Elasticsearch để phát hiện các cuộc tấn công DoS lưu lượng thấp (Low-rate DoS)."))
    sections.append(("P", "3. Triển khai tác tử Winlogbeat và Filebeat đẩy nhật ký từ các máy chủ ảo hóa thật vào cổng chuẩn hóa /api/siem/normalize."))

    # CHƯƠNG 10
    sections.append(("H1", "CHƯƠNG 10. KẾT LUẬN"))
    sections.append(("P", "Đồ án 'Nghiên cứu và triển khai phòng thủ mạng tự động qua SDN tích hợp giám sát bằng ELK Stack' (Dự án SDNFlowGuard) đã hoàn thành xuất sắc và toàn diện 100% các mục tiêu nghiên cứu và yêu cầu thực tiễn của môn học Chuyên đề – Hệ thống mạng và bảo mật. Hệ thống đã chứng minh thành công tính khả thi và hiệu quả vượt trội của việc kết hợp mạng điều khiển bằng phần mềm SDN (ONOS, OpenFlow 1.3, Mininet/OVS) với ngăn xếp phân tích sự kiện an ninh tập trung ELK Stack."))
    sections.append(("P", "Đóng góp học thuật và kỹ thuật nổi bật nhất của đề tài là việc thiết lập và chứng minh thành công nguyên lý 'Attached Host != Verified Attacker', xây dựng chuỗi tương quan bằng chứng nguồn L2/L3 hai giai đoạn Step 63/64 và cổng an toàn Active Defense Safety Gate hoạt động ở chế độ DRY_RUN an toàn. Toàn bộ hệ thống mã nguồn, cơ sở dữ liệu lịch sử, 50 bài kiểm thử tự động, 5 kịch bản thực nghiệm End-to-End, bộ tài liệu và slide thuyết trình đã sẵn sàng phục vụ báo cáo bảo vệ và nộp đồ án."))

    # Tài liệu tham khảo
    sections.append(("H1", "TÀI LIỆU THAM KHẢO"))
    refs = [
        "[1] Open Networking Foundation (ONF), 'OpenFlow Switch Specification Version 1.3.5', ONF TS-023, Mar. 2015.",
        "[2] P. Berde et al., 'ONOS: Towards an Open, Distributed SDN OS', in Proceedings of the Third Workshop on Hot Topics in Software Defined Networks (HotSDN '14), Chicago, IL, USA, 2014, pp. 1-6.",
        "[3] B. Lantz, B. Heller, and N. McKeown, 'A Network in a Laptop: Rapid Prototyping for Software-Defined Networks', in Proceedings of the 9th ACM SIGCOMM Workshop on Hot Topics in Networks (HotNets-IX), Monterey, CA, USA, 2010.",
        "[4] B. Pfaff et al., 'The Design and Implementation of Open vSwitch', in 12th USENIX Symposium on Networked Systems Design and Implementation (NSDI '15), Oakland, CA, USA, 2015, pp. 117-130.",
        "[5] Elastic, 'Elasticsearch Reference [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html",
        "[6] Elastic, 'Logstash Reference [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/logstash/reference/current/index.html",
        "[7] Elastic, 'Kibana Guide [8.15]', Elastic Documentation, 2024. [Online]. Available: https://www.elastic.co/guide/en/kibana/reference/current/index.html",
        "[8] R. Martin, 'Clean Architecture: A Craftsman's Guide to Software Structure and Design', Prentice Hall, 2017.",
        "[9] M. Fowler, 'StranglerFigApplication', MartinFowler.com, 2019. [Online]. Available: https://martinfowler.com/bliki/StranglerFigApplication.html",
        "[10] S. Scott-Hayward, S. Natarajan, and S. Sezer, 'A Survey of Security in Software Defined Networks', IEEE Communications Surveys & Tutorials, vol. 18, no. 1, pp. 623-654, 2016.",
        "[11] N. Sultana et al., 'FLIPS: Hybrid OpenFlow Switch for Software-Defined Network Security', in IEEE Transactions on Network and Service Management, vol. 14, no. 2, pp. 312-325, June 2017.",
        "[12] S. Shin et al., 'FRESCO: Modular Composable Security Services for Software-Defined Networks', in Proceedings of the 20th Annual Network and Distributed System Security Symposium (NDSS '13), San Diego, CA, USA, 2013."
    ]
    for r in refs:
        sections.append(("P", r))

    # Appendices
    sections.append(("H1", "PHỤ LỤC A. HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG"))
    sections.append(("P", "Phụ lục này cung cấp tài liệu kỹ thuật chi tiết về quy trình khởi động, kiểm tra sức khỏe và chạy thử nghiệm hệ thống SDNFlowGuard:"))
    sections.append(("P", "1. Khởi động các container Docker:"))
    sections.append(("CODE", "cd D:\\Project\\Nhom02_SDNFlowGuard\\infrastructure\ndocker compose -f compose.yaml up -d"))
    sections.append(("P", "2. Khởi tạo mạng Mininet OpenFlow 1.3 trong WSL Ubuntu-26.04:"))
    sections.append(("CODE", "wsl -d Ubuntu-26.04 -u root -- mn --topo single,2 --mac --switch ovsk,protocols=OpenFlow13 --controller remote,ip=127.0.0.1,port=6653"))
    sections.append(("P", "3. Khởi chạy Flask Backend API:"))
    sections.append(("CODE", "$env:PYTHONDONTWRITEBYTECODE=\"1\"\n$env:SDNFLOW_DEFENSE_MODE=\"DRY_RUN\"\n& \"D:\\Project\\Nhom02_SDNFlowGuard\\backend\\venv\\Scripts\\python.exe\" -B run.py"))
    sections.append(("P", "4. Khởi chạy React Frontend UI:"))
    sections.append(("CODE", "cd D:\\Project\\Nhom02_SDNFlowGuard\\frontend\nnpm start"))
    sections.append(("P", "5. Thực thi bộ kiểm tra sức khỏe và toàn bộ kiểm thử tự động:"))
    sections.append(("CODE", "powershell -ExecutionPolicy Bypass -File scripts\\verify_system_health.ps1\npowershell -ExecutionPolicy Bypass -File scripts\\run_all_tests.ps1"))

    sections.append(("H1", "PHỤ LỤC B. DANH MỤC 50 BÀI KIỂM THỬ TỰ ĐỘNG"))
    sections.append(("P", "Bảng dưới đây thống kê đầy đủ 50 bài kiểm thử tự động đã được kiểm chứng và đạt trạng thái PASS 100% trong scripts/run_all_tests.ps1:"))
    
    test_list = [
        ("test_source_ip_evidence_analyzer.py", "3", "Unit", "Giải mã gói tin tcpdump UTF-8/UTF-16, trích xuất MAC/IP, kiểm tra mốc UTC"),
        ("test_onos_host_evidence_correlator.py", "3", "Unit", "Đối chiếu topology ONOS, phát hiện multi-host và giả mạo IP/MAC"),
        ("test_defense_policy.py", "2", "Unit", "Động cơ chính sách phòng thủ, invariant Host != Attacker, ALLOW/OBSERVE"),
        ("test_safety_gate.py", "3", "Unit", "Cổng an toàn, bảo vệ IP hạ tầng, kiểm soát DRY_RUN và duyệt vận hành"),
        ("test_risk_scoring_and_decision.py", "3", "Unit", "Chấm điểm nguy cơ tích lũy, miễn nhiễm cảnh báo test_only"),
        ("test_siem_log_normalizer.py", "3", "Unit", "Chuẩn hóa nhật ký SIEM: ONOS telemetry, Firewall Syslog, Windows Event"),
        ("test_port_anomaly_detector.py", "2", "Unit", "Phát hiện chuỗi vượt ngưỡng liên tiếp, đặt lại chuỗi khi đứt quãng mẫu"),
        ("test_alert_publisher.py", "1", "Unit", "Sinh mã băm SHA-256 alert_key duy nhất, gắn nhãn cờ test_only"),
        ("test_reliable_monitor_v1.py", "2", "Unit", "Động cơ Reliable Monitor V1, xử lý hit và lưu checkpoint nguyên tử"),
        ("test_reliable_monitor_v2.py", "2", "Unit", "Động cơ Overlap Monitor V2, xử lý dữ liệu đến trễ qua cửa sổ 30s"),
        ("test_sqlite_repository.py", "3", "Integration", "Thao tác CRUD trên các bảng settings, flows, events, actions trong DB"),
        ("test_webhook_reception.py", "2", "Integration", "Tiếp nhận webhook sự kiện, kiểm tra cú pháp và lưu vết"),
        ("test_flask_api_routes.py", "6", "Integration", "Kiểm thử các endpoint REST API: health, evidence, evaluate, safety, block, API-Key"),
        ("test_report_generator.py", "1", "Integration", "Sinh báo cáo tổng kết hệ thống và cơ chế dự phòng PDF thuần Python"),
        ("test_onos_payload_contracts.py", "2", "Contracts", "Khế ước định dạng dữ liệu ONOS REST v1 ACL và PointToPointIntent"),
        ("test_elasticsearch_query_contracts.py", "2", "Contracts", "Khế ước tham số truy vấn và cấu trúc phản hồi Elasticsearch /api/elk/*"),
        ("test_frontend_backend_api_contracts.py", "1", "Contracts", "Khế ước cấu trúc JSON giữa backend Flask và các trang React"),
        ("test_no_secret_leakage.py", "2", "Safety", "Kiểm toán không lộ mật khẩu cứng trong run.py và .env.example"),
        ("test_dry_run_default.py", "1", "Safety", "Xác minh chế độ phòng thủ mặc định luôn là DRY_RUN an toàn"),
        ("test_port_anomaly_never_blocks_ip.py", "1", "Safety", "Đảm bảo bất thường cổng đơn thuần không bao giờ đề xuất khóa IP"),
        ("test_test_alert_never_blocks.py", "1", "Safety", "Đảm bảo cảnh báo test_only không bao giờ kích hoạt khóa IP"),
        ("test_checkpoint_integrity.py", "3", "Safety", "Bảo toàn 4 checkpoint collector, 2 file bằng chứng Step 63 và SHA-256 DB"),
        ("test_full_monitoring_to_policy_pipeline.py", "1", "E2E", "Kiểm thử toàn diện đường ống từ mẫu đo cổng tới Step 64 và Rollback")
    ]
    for tl in test_list:
        sections.append(("P", f"Module: {tl[0]} | Số bài test: {tl[1]} | Tầng: {tl[2]} | Phạm vi kiểm chứng: {tl[3]}"))

    sections.append(("H1", "PHỤ LỤC C. BẢNG MÃ BĂM TOÀN VẸN SHA-256 DỰ ÁN"))
    sections.append(("P", "Bảng mã băm SHA-256 của các thành phần dữ liệu, cấu hình và tệp bằng chứng cốt lõi:"))
    hashes = [
        ("database/sdnflowguard.db", "28,672 bytes", "3909de520f89ea050e7858104c8aa17bddd94d06af9db5ad84652404b9463fe9"),
        ("database/netsecflow.db.bak", "28,672 bytes", "d12be7a29b412061213ef13f1c7e47e75405f84a83fb9949bbde3c7e31110443"),
        ("backend/defense/evidence/ingress_icmp_20261101_014645.txt", "5,146 bytes", "3076efccdc79564568e320b983b1fd12c2f1ef4f1ec2df55f7ab4e21a21b40d7"),
        ("backend/defense/evidence/ingress_icmp_20261101_014645.json", "2,202 bytes", "05a659224fb184be2e0e7416f18602bc6d658a10d5d43d7b89c1420db024e91c"),
        ("backend/defense/evidence/ingress_icmp_live_utc_verified.txt", "959 bytes", "bef49f603007d7f0fd154b691d8de9b8945a7e89055bf6f4c9fa7ff7d71c8cf8"),
        ("backend/defense/evidence/ingress_icmp_live_utc_verified.json", "1,521 bytes", "1d36f69569871845848c5cbcdec2c99ce2d1832da53b3b4cf70ba4750cfdda68"),
        ("backend/collectors/state/auto_dry_t4_c2.json", "376 bytes", "c852e276cbca38ec0bc9a637c132d6cc3be6d735fc67d393055ff6a9ef19a91e"),
        ("backend/collectors/state/auto_dry_t4_c2_v2.json", "5,395 bytes", "c011906fb042f684fd33945f2c5b8c04d31f925b80eb774da06346ff2512fc33"),
        ("backend/collectors/state/auto_publish_t4_c2.json", "376 bytes", "a2ab7d86fc0bc5a19833a44a2232c1914f8fb2bc97c832c451ff1a4533bf0628"),
        ("backend/collectors/state/auto_publish_t4_c2_v2.json", "5,495 bytes", "dc7fb2ef306c64e4ecbc0f950174da1cf002798efab5166037b0ab95395cb16e")
    ]
    for h in hashes:
        sections.append(("P", f"Tệp: {h[0]} ({h[1]}) -> SHA-256: {h[2]}"))

    
    # Appendices D, E, F with Full Source Code Listings
    sections.append(("H1", "PH? L?C D. TO?N V?N M? NGU?N C?NG AN TO?N ACTIVE DEFENSE (SAFETY GATE)"))
    sections.append(("P", "T?p: backend/sdnflowguard/domain/policies/safety_gate.py"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\backend\sdnflowguard\domain\policies\safety_gate.py", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))

    sections.append(("H1", "PH? L?C E. TO?N V?N M? NGU?N T??NG QUAN B?NG CH?NG (EVIDENCE CORRELATION)"))
    sections.append(("P", "T?p: backend/sdnflowguard/domain/services/evidence_correlation.py"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\backend\sdnflowguard\domain\services\evidence_correlation.py", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))

    sections.append(("H1", "PH? L?C F. TO?N V?N M? NGU?N PH?N T?CH G?I TIN B?T T?I C?NG V?O (STEP 63)"))
    sections.append(("P", "T?p: backend/defense/source_ip_evidence_analyzer.py"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\backend\defense\source_ip_evidence_analyzer.py", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))

    sections.append(("H1", "PH? L?C G. TO?N V?N M? NGU?N ??I CHI?U TOPOLOGY ONOS TR?C TI?P (STEP 64)"))
    sections.append(("P", "T?p: backend/defense/onos_host_evidence_correlator.py"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\backend\defense\onos_host_evidence_correlator.py", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))

    sections.append(("H1", "PH? L?C H. TO?N V?N C?U H?NH PIPELINE LOGSTASH V? DOCKER COMPOSE"))
    sections.append(("P", "T?p: infrastructure/logstash/pipeline/01-sdnflowguard.conf"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\infrastructure\logstash\pipeline\01-sdnflowguard.conf", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))
    sections.append(("P", "T?p: infrastructure/compose.yaml"))
    with open(r"D:\Project\Nhom02_SDNFlowGuard\infrastructure\compose.yaml", "r", encoding="utf-8") as src_f:
        sections.append(("CODE", src_f.read()))

    return sections

if __name__ == "__main__":
    secs = get_all_academic_sections()
    words = sum(len(s[1].split()) for s in secs if len(s) > 1 and s[1])
    print(f"Total sections: {len(secs)}, Total words: {words}")
