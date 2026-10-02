import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

DEFAULT_DATA_FILE = "family_tree_data.json"

NOI_ROLES = {"Cha", "Chú", "Thím", "Cô ruột", "Dượng (chồng cô)"}
NGOAI_ROLES = {"Mẹ", "Cậu ruột", "Mợ (vợ cậu)", "Dì ruột", "Dượng (chồng dì)"}

ROLE_OPTIONS = [
    "Thành viên",
    "Cụ Nội (Nam)", "Cụ Nội (Nữ)", "Cụ Ngoại (Nam)", "Cụ Ngoại (Nữ)",
    "Ông nội", "Bà nội", "Ông ngoại", "Bà ngoại",
    "Bác ruột (Bên nội)", "Bác dâu (Bên nội)", "Bác rể (Bên nội)",
    "Bác ruột (Bên ngoại)", "Bác dâu (Bên ngoại)", "Bác rể (Bên ngoại)",
    "Cha", "Mẹ", "Cha dượng", "Mẹ kế",
    "Chú", "Thím", "Cô ruột", "Dượng (chồng cô)",
    "Cậu ruột", "Mợ (vợ cậu)", "Dì ruột", "Dượng (chồng dì)",
    "Chồng", "Vợ",
    "Anh trai", "Chị gái", "Em trai", "Em gái",
    "Anh họ (Bên nội)", "Chị họ (Bên nội)", "Em họ (Bên nội)",
    "Anh họ (Bên ngoại)", "Chị họ (Bên ngoại)", "Em họ (Bên ngoại)",
    "Con trai", "Con gái", "Con nuôi", "Con dâu", "Con rể",
    "Cháu nội (Trai)", "Cháu nội (Gái)", "Cháu ngoại (Trai)", "Cháu ngoại (Gái)",
    "Chắt / Chút", "Khác",
]

SIDE_RANK = {"noi": 0, None: 1, "ngoai": 2}
SIDE_LABEL = {"noi": "NỘI", "ngoai": "NGOẠI"}
SIDE_COLOR = {"noi": "#ffb74d", "ngoai": "#80deea"}
NO_PARENT = "-- Không có (Thành viên gốc) --"

BOX_W, BOX_H = 190, 60
SPACING, Y_GAP, START_Y = 220, 130, 60

def get_side(role):
    role = role or ""
    low = role.lower()
    if "ngoại" in low or role in NGOAI_ROLES:
        return "ngoai"
    if "nội" in low or role in NOI_ROLES:
        return "noi"
    return None

def sides_conflict(role_a, role_b):
    a, b = get_side(role_a), get_side(role_b)
    return a is not None and b is not None and a != b

def member_label(m):
    return f"ID {m['id']}: {m['name']} ({m.get('role', 'N/A')})"

def parse_id(text):
    if text and text.startswith("ID "):
        try:
            return int(text.split(":")[0][3:].strip())
        except ValueError:
            return None
    return None

class FamilyTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phần Mềm Quản Lý Gia Phả - Sơ Đồ Cây & Quan Hệ")
        self.root.geometry("1400x850")
        self.root.configure(bg="#121212")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#121212", foreground="#e0e0e0")
        self.style.configure("TCombobox",
                             fieldbackground="#2c2c2c", background="#2c2c2c",
                             foreground="#ffffff", selectbackground="#bb86fc",
                             selectforeground="#121212",
                             darkcolor="#2c2c2c", lightcolor="#2c2c2c", bordercolor="#444444")
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', '#2c2c2c')],
                       foreground=[('readonly', '#ffffff')],
                       background=[('readonly', '#2c2c2c')])

        self.members_list = []
        self.events = []
        self.avatar_path = "Chưa chọn ảnh"
        self.menu_buttons = []
        self.current_tab_func = None

        self.auto_load_data()

        self.create_sidebar()
        self.create_main_content()

    def auto_load_data(self):
        if os.path.exists(DEFAULT_DATA_FILE):
            try:
                with open(DEFAULT_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.members_list = data.get("members", [])
                    self.events = data.get("events", [])
                    self.avatar_path = data.get("avatar_path", "Chưa chọn ảnh")
            except Exception as e:
                print(f"Không thể đọc file dữ liệu tự động: {e}")
        else:
            self.create_sample_data()
            self.auto_save_data()

    def auto_save_data(self):
        data = {
            "members": self.members_list,
            "events": self.events,
            "avatar_path": self.avatar_path
        }
        try:
            with open(DEFAULT_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Lỗi khi tự động lưu dữ liệu: {e}")

    def create_sample_data(self):
        self.members_list = [
            {"id": 1, "name": "Nguyễn Văn Cụ", "gen": 1, "role": "Cụ Nội (Nam)", "gender": "Nam", "spouse_id": 2, "parent_id": None},
            {"id": 2, "name": "Trần Thị Bà", "gen": 1, "role": "Cụ Nội (Nữ)", "gender": "Nữ", "spouse_id": 1, "parent_id": None},
            {"id": 3, "name": "Nguyễn Văn Cha", "gen": 2, "role": "Cha", "gender": "Nam", "spouse_id": 4, "parent_id": 1},
            {"id": 4, "name": "Lê Thị Mẹ", "gen": 2, "role": "Mẹ", "gender": "Nữ", "spouse_id": 3, "parent_id": None},
            {"id": 5, "name": "Nguyễn Văn Con", "gen": 3, "role": "Con trai", "gender": "Nam", "spouse_id": None, "parent_id": 3},
        ]
        self.events = [
            {"day": "15", "month": "Th 08", "name": "Giỗ Cụ Tổ", "sub": "15/08 - Âm lịch"}
        ]

    def get_member(self, member_id):
        if member_id is None:
            return None
        return next((m for m in self.members_list if m["id"] == member_id), None)

    def sanitize_relations(self):
        fixed = 0
        for m in self.members_list:
            pid = m.get("parent_id")
            if not pid:
                continue
            p = self.get_member(pid)
            if (p is None or p["gen"] >= m["gen"]
                    or sides_conflict(m.get("role"), p.get("role"))):
                m["parent_id"] = None
                fixed += 1
        return fixed

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#181818", width=270)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg="#181818")
        logo_frame.pack(pady=25, padx=25, anchor="w")
        tk.Label(logo_frame, text="GP", bg="#bb86fc", fg="#121212",
                 font=("Segoe UI", 12, "bold"), width=3, height=1).pack(side=tk.LEFT, padx=(0, 12))

        logo_text = tk.Frame(logo_frame, bg="#181818")
        logo_text.pack(side=tk.LEFT)
        tk.Label(logo_text, text="GIA PHẢ", bg="#181818", fg="#ffffff", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(logo_text, text="Hệ thống quản lý dòng họ", bg="#181818", fg="#888888", font=("Segoe UI", 8)).pack(anchor="w")

        tk.Button(sidebar, text="+ Thêm thành viên", bg="#bb86fc", fg="#121212",
                  font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=10, cursor="hand2",
                  activebackground="#cf94fc", activeforeground="#121212",
                  command=lambda: self.open_member_dialog(None)).pack(fill=tk.X, padx=20, pady=(5, 15))

        tk.Label(sidebar, text="MENU CHÍNH", bg="#181818", fg="#757575",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=25, pady=(10, 8))

        menus = [
            ("🏠    Tổng quan", self.show_overview, True),
            ("👥    Thành viên & Quan hệ", self.show_members_tab, True),
            ("🌳    Sơ đồ cây gia phả", self.show_tree_tab, True),
            ("💾    Xuất file JSON...", self.backup_data, False),
            ("📂    Nhập file JSON...", self.restore_data, False),
            ("🛡    Bản quyền", self.show_about, True),
        ]

        for text, cmd, is_tab in menus:
            btn = tk.Button(sidebar, text=text, bg="#181818", fg="#b0b0b0",
                            font=("Segoe UI", 10), bd=0, anchor="w", padx=20, pady=10,
                            cursor="hand2", activebackground="#2c2c2c", activeforeground="#ffffff")
            btn.pack(fill=tk.X, padx=12, pady=3)
            if is_tab:
                self.menu_buttons.append(btn)
                idx = len(self.menu_buttons) - 1
                btn.config(command=lambda i=idx, c=cmd: self.handle_menu_click(i, c))
            else:
                btn.config(command=cmd)

        footer = tk.Frame(sidebar, bg="#181818")
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=25)
        tk.Label(footer, text="Phiên bản 5.0 AutoSave", bg="#181818", fg="#757575", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(footer, text="© 2026 Trần Quang Đạt", bg="#181818", fg="#757575", font=("Segoe UI", 8)).pack(anchor="w")

    def handle_menu_click(self, index, cmd):
        for i, btn in enumerate(self.menu_buttons):
            btn.config(bg="#2c2c2c" if i == index else "#181818",
                       fg="#ffffff" if i == index else "#b0b0b0")
        self.current_tab_func = cmd
        cmd()

    def create_main_content(self):
        self.content_container = tk.Frame(self.root, bg="#121212")
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.handle_menu_click(0, self.show_overview)

    def clear_content(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def refresh_current_view(self):
        if self.current_tab_func:
            self.current_tab_func()

    def show_overview(self):
        self.clear_content()

        header = tk.Frame(self.content_container, bg="#1e1e1e", padx=35, height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Tổng quan dòng họ", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(18, 2))
        tk.Label(header, text="Thống kê hệ thống, ngày giỗ và thông tin dòng họ (Tự động lưu)", bg="#1e1e1e",
                 fg="#aaaaaa", font=("Segoe UI", 10)).pack(anchor="w")

        body = tk.Frame(self.content_container, bg="#121212", padx=35, pady=25)
        body.pack(fill=tk.BOTH, expand=True)

        stats_frame = tk.Frame(body, bg="#121212")
        stats_frame.pack(fill=tk.X, pady=(0, 25))

        stats_data = [
            (str(len(self.members_list)), "Tổng thành viên", "#bb86fc"),
            (str(sum(m["gender"] == "Nam" for m in self.members_list)), "Thành viên Nam", "#03dac6"),
            (str(sum(m["gender"] == "Nữ" for m in self.members_list)), "Thành viên Nữ", "#cf6679"),
            (str(len({m["gen"] for m in self.members_list})) if self.members_list else "0", "Đời thế hệ", "#ffb74d"),
        ]
        for i, (val, label, accent) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg="#1e1e1e", padx=20, pady=18)
            card.grid(row=0, column=i, padx=(0, 15) if i < 3 else 0, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Frame(card, bg=accent, width=4, height=35).pack(side=tk.LEFT, padx=(0, 12))
            text_f = tk.Frame(card, bg="#1e1e1e")
            text_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(text_f, text=val, bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 20, "bold")).pack(anchor="w")
            tk.Label(text_f, text=label, bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 9)).pack(anchor="w")

        bottom = tk.Frame(body, bg="#121212")
        bottom.pack(fill=tk.BOTH, expand=True)
        bottom.grid_columnconfigure(0, weight=13)
        bottom.grid_columnconfigure(1, weight=10)

        event_box = tk.Frame(bottom, bg="#1e1e1e", padx=25, pady=22)
        event_box.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        header_ev = tk.Frame(event_box, bg="#1e1e1e")
        header_ev.pack(fill=tk.X, pady=(0, 15))
        tk.Label(header_ev, text="Sự kiện sắp diễn ra", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        tk.Button(header_ev, text="+ Thêm sự kiện", bg="#bb86fc", fg="#121212",
                  font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, cursor="hand2",
                  command=self.open_add_event_dialog).pack(side=tk.RIGHT)

        self.events_list_frame = tk.Frame(event_box, bg="#1e1e1e")
        self.events_list_frame.pack(fill=tk.BOTH, expand=True)
        self.refresh_events_list()

        avatar_box = tk.Frame(bottom, bg="#1e1e1e", padx=25, pady=22)
        avatar_box.grid(row=0, column=1, sticky="nsew")
        tk.Label(avatar_box, text="Ảnh đại diện gia phả", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 15))

        preview = tk.Frame(avatar_box, bg="#2c2c2c", width=90, height=90)
        preview.pack(pady=10)
        preview.pack_propagate(False)
        tk.Label(preview, text="GP", bg="#2c2c2c", fg="#bb86fc", font=("Segoe UI", 22, "bold")).pack(expand=True)

        self.av_status_label = tk.Label(avatar_box, text=f"File: {os.path.basename(self.avatar_path)}",
                                        bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 9), wraplength=220)
        self.av_status_label.pack(pady=8)

        btns = tk.Frame(avatar_box, bg="#1e1e1e")
        btns.pack(pady=10)
        tk.Button(btns, text="📁 Đổi ảnh", bg="#bb86fc", fg="#121212", font=("Segoe UI", 9, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2", command=self.change_avatar).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="🗑️ Xóa", bg="#333333", fg="#ffffff", font=("Segoe UI", 9),
                  bd=0, padx=12, pady=6, cursor="hand2", command=self.delete_avatar).pack(side=tk.LEFT, padx=6)

    def change_avatar(self):
        file_p = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_p:
            self.avatar_path = file_p
            if hasattr(self, 'av_status_label'):
                self.av_status_label.config(text=f"File: {os.path.basename(self.avatar_path)}")
            self.auto_save_data()

    def delete_avatar(self):
        self.avatar_path = "Chưa chọn ảnh"
        if hasattr(self, 'av_status_label'):
            self.av_status_label.config(text="File: Chưa chọn ảnh")
        self.auto_save_data()

    def refresh_events_list(self):
        for widget in self.events_list_frame.winfo_children():
            widget.destroy()

        if not self.events:
            tk.Label(self.events_list_frame, text="Chưa có sự kiện nào được ghi nhận.",
                     bg="#1e1e1e", fg="#757575", font=("Segoe UI", 9)).pack(pady=20)
            return

        for idx, ev in enumerate(self.events):
            item = tk.Frame(self.events_list_frame, bg="#2c2c2c", padx=12, pady=10)
            item.pack(fill=tk.X, pady=5)

            badge = tk.Frame(item, bg="#121212", padx=10, pady=6)
            badge.pack(side=tk.LEFT, padx=(0, 12))
            tk.Label(badge, text=ev["day"], bg="#121212", fg="#ffffff", font=("Segoe UI", 12, "bold")).pack()
            tk.Label(badge, text=ev["month"], bg="#121212", fg="#aaaaaa", font=("Segoe UI", 7)).pack()

            det = tk.Frame(item, bg="#2c2c2c")
            det.pack(side=tk.LEFT, anchor="w", expand=True, fill=tk.X)
            tk.Label(det, text=ev["name"], bg="#2c2c2c", fg="#ffffff", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(det, text=f"📅 {ev['sub']}", bg="#2c2c2c", fg="#aaaaaa", font=("Segoe UI", 8)).pack(anchor="w")

            tk.Button(item, text="🗑 Xóa", bg="#cf6679", fg="#ffffff", font=("Segoe UI", 8), bd=0,
                      padx=8, pady=4, cursor="hand2",
                      command=lambda i=idx: self.delete_event(i)).pack(side=tk.RIGHT, padx=5)

    def delete_event(self, index):
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa sự kiện này?"):
            self.events.pop(index)
            self.auto_save_data()
            self.refresh_events_list()

    def open_add_event_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Thêm sự kiện mới")
        dialog.geometry("380x330")
        dialog.configure(bg="#1e1e1e")
        dialog.grab_set()

        tk.Label(dialog, text="Thêm Sự Kiện / Ngày Giỗ", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 12, "bold")).pack(pady=20)
        form = tk.Frame(dialog, bg="#1e1e1e", padx=25)
        form.pack(fill=tk.BOTH, expand=True)

        def make_entry(label, pady_bottom):
            tk.Label(form, text=label, bg="#1e1e1e", fg="#bb86fc", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            e = tk.Entry(form, font=("Segoe UI", 10), bg="#2c2c2c", fg="#ffffff",
                         insertbackground="white", bd=1, relief="solid")
            e.pack(fill=tk.X, pady=(4, pady_bottom))
            return e

        name_entry = make_entry("Tên sự kiện / Thành viên:", 12)
        day_entry = make_entry("Ngày (VD: 15):", 12)
        month_entry = make_entry("Tháng (VD: Th 08):", 15)

        def save_event():
            name, day, month = name_entry.get().strip(), day_entry.get().strip(), month_entry.get().strip()
            if name and day and month:
                self.events.append({"day": day, "month": month, "name": name, "sub": f"{day}/{month} - Dương lịch"})
                self.auto_save_data()
                self.refresh_events_list()
                dialog.destroy()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!", parent=dialog)

        tk.Button(dialog, text="Lưu sự kiện", bg="#bb86fc", fg="#121212", font=("Segoe UI", 10, "bold"),
                  bd=0, padx=20, pady=8, cursor="hand2", command=save_event).pack(pady=10)

    def show_members_tab(self):
        self.clear_content()
        frame = tk.Frame(self.content_container, bg="#1e1e1e", padx=35, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(frame, bg="#1e1e1e")
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="Quản lý Danh sách Thành viên & Mối quan hệ", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="+ Thêm thành viên", bg="#bb86fc", fg="#121212", font=("Segoe UI", 9, "bold"),
                  bd=0, padx=14, pady=8, cursor="hand2",
                  command=lambda: self.open_member_dialog(None)).pack(side=tk.RIGHT)

        container = tk.Frame(frame, bg="#1e1e1e")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.member_scrollable_frame = tk.Frame(canvas, bg="#1e1e1e")
        win_id = canvas.create_window((0, 0), window=self.member_scrollable_frame, anchor="nw")

        self.member_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_members_table()

    def refresh_members_table(self):
        if not hasattr(self, "member_scrollable_frame") or not self.member_scrollable_frame.winfo_exists():
            return

        for widget in self.member_scrollable_frame.winfo_children():
            widget.destroy()

        if not self.members_list:
            tk.Label(self.member_scrollable_frame,
                     text="Chưa có thành viên nào. Vui lòng bấm '+ Thêm thành viên' để bắt đầu.",
                     bg="#1e1e1e", fg="#757575", font=("Segoe UI", 10)).pack(pady=30)
            return

        columns = [("ID & Họ Tên", 18), ("Thế hệ", 8), ("Vai vế", 16), ("Giới tính", 9),
                   ("Vợ/Chồng", 16), ("Cha/Mẹ", 16)]
        header = tk.Frame(self.member_scrollable_frame, bg="#2c2c2c", padx=15, pady=10)
        header.pack(fill=tk.X, pady=2)
        for text, w in columns:
            tk.Label(header, text=text, bg="#2c2c2c", fg="#ffffff", font=("Segoe UI", 10, "bold"),
                     width=w, anchor="w").pack(side=tk.LEFT)
        tk.Label(header, text="Thao tác", bg="#2c2c2c", fg="#ffffff", font=("Segoe UI", 10, "bold"),
                 width=14, anchor="center").pack(side=tk.LEFT)

        ordered = sorted(self.members_list,
                         key=lambda m: (m["gen"], SIDE_RANK[get_side(m.get("role"))], m["id"]))

        for mem in ordered:
            row = tk.Frame(self.member_scrollable_frame, bg="#252525", padx=15, pady=10)
            row.pack(fill=tk.X, pady=4)

            sp = self.get_member(mem.get("spouse_id"))
            spouse_name = f"ID {sp['id']}: {sp['name']}" if sp else "Không có"
            p = self.get_member(mem.get("parent_id"))
            parent_name = f"ID {p['id']}: {p['name']}" if p else "Không có (Gốc)"

            cells = [
                (f"[{mem['id']}] {mem['name']}", "#ffffff", 18),
                (f"Đời {mem['gen']}", "#bb86fc", 8),
                (mem.get("role", "Thành viên"), "#ffb74d", 16),
                (mem["gender"], "#aaaaaa", 9),
                (spouse_name, "#03dac6", 16),
                (parent_name, "#80deea", 16),
            ]
            for text, color, w in cells:
                tk.Label(row, text=text, bg="#252525", fg=color, font=("Segoe UI", 10),
                         width=w, anchor="w").pack(side=tk.LEFT)

            box = tk.Frame(row, bg="#252525")
            box.pack(side=tk.LEFT, padx=2)
            tk.Button(box, text="✏️ Sửa", bg="#03dac6", fg="#121212", font=("Segoe UI", 9, "bold"), bd=0,
                      padx=8, pady=4, cursor="hand2",
                      command=lambda m=mem: self.open_member_dialog(m)).pack(side=tk.LEFT, padx=3)
            tk.Button(box, text="🗑️ Xóa", bg="#cf6679", fg="#ffffff", font=("Segoe UI", 9), bd=0,
                      padx=8, pady=4, cursor="hand2",
                      command=lambda m_id=mem["id"]: self.delete_member(m_id)).pack(side=tk.LEFT, padx=3)

    def delete_member(self, member_id):
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa thành viên này?"):
            self.members_list = [m for m in self.members_list if m["id"] != member_id]
            for m in self.members_list:
                if m.get("spouse_id") == member_id:
                    m["spouse_id"] = None
                if m.get("parent_id") == member_id:
                    m["parent_id"] = None
            self.auto_save_data()
            self.refresh_current_view()

    def open_member_dialog(self, member_data=None):
        is_edit = member_data is not None
        dialog = tk.Toplevel(self.root)
        dialog.title("Sửa thông tin thành viên" if is_edit else "Thêm thành viên và thiết lập quan hệ")
        dialog.geometry("500x720")
        dialog.configure(bg="#1e1e1e")
        dialog.grab_set()

        title_text = f"Chỉnh sửa: {member_data['name']}" if is_edit else "Thêm Thành Viên & Mối Quan Hệ"
        tk.Label(dialog, text=title_text, bg="#1e1e1e", fg="#ffffff", font=("Segoe UI", 12, "bold")).pack(pady=15)

        form = tk.Frame(dialog, bg="#1e1e1e", padx=30)
        form.pack(fill=tk.BOTH, expand=True)

        def caption(text, color="#bb86fc"):
            tk.Label(form, text=text, bg="#1e1e1e", fg=color, font=("Segoe UI", 9, "bold")).pack(anchor="w")

        def entry():
            e = tk.Entry(form, font=("Segoe UI", 10), bg="#2c2c2c", fg="#ffffff",
                         insertbackground="white", bd=1, relief="solid")
            e.pack(fill=tk.X, pady=(2, 8))
            return e

        def combo(values, current, pady_bottom=8):
            c = ttk.Combobox(form, values=values, font=("Segoe UI", 10), state="readonly")
            c.set(current)
            c.pack(fill=tk.X, pady=(2, pady_bottom))
            return c

        caption("Họ và Tên:")
        name_e = entry()
        if is_edit:
            name_e.insert(0, member_data["name"])

        caption("Thế hệ (Số nguyên, VD: 1, 2, 3...):")
        gen_e = entry()
        gen_e.insert(0, str(member_data["gen"]) if is_edit else "1")

        caption("Vai vế trong gia phả (Đầy đủ Nội / Ngoại):", "#ffb74d")
        role_e = combo(ROLE_OPTIONS, member_data.get("role", "Thành viên") if is_edit else "Thành viên", 2)
        side_hint = tk.Label(form, text="", bg="#1e1e1e", font=("Segoe UI", 8, "italic"))
        side_hint.pack(anchor="w", pady=(0, 6))

        caption("Giới tính:")
        gender_e = combo(["Nam", "Nữ"], member_data.get("gender", "Nam") if is_edit else "Nam")

        other_members = [m for m in self.members_list if not is_edit or m["id"] != member_data["id"]]

        caption("Kết hôn với Vợ/Chồng (nếu có):", "#03dac6")
        cur_spouse = self.get_member(member_data.get("spouse_id")) if is_edit else None
        spouse_e = combo(["Không có"] + [member_label(m) for m in other_members],
                         member_label(cur_spouse) if cur_spouse else "Không có")

        caption("Cha/Mẹ trực hệ (chỉ hiện người cùng nhánh Nội/Ngoại):", "#80deea")
        cur_parent = self.get_member(member_data.get("parent_id")) if is_edit else None
        parent_e = combo([NO_PARENT], member_label(cur_parent) if cur_parent else NO_PARENT, 12)

        def parent_choices():
            role = role_e.get()
            return [NO_PARENT] + [member_label(m) for m in other_members
                                  if not sides_conflict(role, m.get("role"))]

        def on_role_change(_event=None):
            vals = parent_choices()
            parent_e["values"] = vals
            if parent_e.get() not in vals:
                parent_e.set(NO_PARENT)
            side = get_side(role_e.get())
            if side:
                side_hint.config(text=f"→ Thuộc nhánh {SIDE_LABEL[side]}", fg=SIDE_COLOR[side])
            else:
                side_hint.config(text="→ Trung tính (không thuộc riêng nhánh nào)", fg="#757575")

        def on_parent_change(_event=None):
            p = self.get_member(parse_id(parent_e.get()))
            if p:
                gen_e.delete(0, tk.END)
                gen_e.insert(0, str(p["gen"] + 1))

        role_e.bind("<<ComboboxSelected>>", on_role_change)
        parent_e.bind("<<ComboboxSelected>>", on_parent_change)
        on_role_change()
        if cur_parent:
            parent_e.set(member_label(cur_parent) if member_label(cur_parent) in parent_e["values"] else NO_PARENT)

        def save_mem():
            name = name_e.get().strip()
            role = role_e.get()
            gender = gender_e.get()

            try:
                gen = int(gen_e.get().strip())
            except ValueError:
                messagebox.showwarning("Lỗi", "Thế hệ phải là một số nguyên!", parent=dialog)
                return
            if not name:
                messagebox.showwarning("Lỗi", "Vui lòng nhập họ tên!", parent=dialog)
                return

            spouse_id = parse_id(spouse_e.get())
            if spouse_id:
                target = self.get_member(spouse_id)
                if (target and target.get("spouse_id")
                        and (not is_edit or target["spouse_id"] != member_data["id"])):
                    messagebox.showwarning("Lỗi logic", f"Thành viên '{target['name']}' đã kết hôn với người khác rồi!",
                                           parent=dialog)
                    return

            parent_id = parse_id(parent_e.get())
            if parent_id:
                parent = self.get_member(parent_id)
                if parent is None:
                    parent_id = None
                else:
                    if sides_conflict(role, parent.get("role")):
                        messagebox.showwarning(
                            "Sai nhánh Nội / Ngoại",
                            f"'{role}' không thể là con của '{parent['name']}' ({parent.get('role')}).\n"
                            "Hai người thuộc hai nhánh khác nhau.", parent=dialog)
                        return
                    if parent["gen"] >= gen:
                        messagebox.showwarning(
                            "Sai thế hệ",
                            f"Cha/Mẹ ('{parent['name']}' - đời {parent['gen']}) phải có đời nhỏ hơn đời {gen}.",
                            parent=dialog)
                        return

            if is_edit:
                old_spouse_id = member_data.get("spouse_id")
                member_data.update(name=name, gen=gen, role=role, gender=gender,
                                   spouse_id=spouse_id, parent_id=parent_id)
                if old_spouse_id != spouse_id:
                    old_sp = self.get_member(old_spouse_id)
                    if old_sp and old_sp.get("spouse_id") == member_data["id"]:
                        old_sp["spouse_id"] = None
                    new_sp = self.get_member(spouse_id)
                    if new_sp:
                        new_sp["spouse_id"] = member_data["id"]
            else:
                new_id = max((m["id"] for m in self.members_list), default=0) + 1
                self.members_list.append({"id": new_id, "name": name, "gen": gen, "role": role,
                                          "gender": gender, "spouse_id": spouse_id, "parent_id": parent_id})
                new_sp = self.get_member(spouse_id)
                if new_sp:
                    new_sp["spouse_id"] = new_id

            self.auto_save_data()
            self.refresh_current_view()
            dialog.destroy()

        tk.Button(dialog, text="Lưu thay đổi" if is_edit else "Lưu thành viên & Quan hệ",
                  bg="#bb86fc", fg="#121212", font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=8,
                  cursor="hand2", command=save_mem).pack(pady=15)

    def show_tree_tab(self):
        self.clear_content()
        frame = tk.Frame(self.content_container, bg="#1e1e1e", padx=25, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Sơ Đồ Phả Đồ Tộc Huyết Thống", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 5))
        tk.Label(frame, text="Nhánh Nội xếp bên trái, nhánh Ngoại xếp bên phải",
                 bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 15))

        wrap = tk.Frame(frame, bg="#121212", bd=1, relief="solid")
        wrap.pack(fill=tk.BOTH, expand=True)

        self.tree_canvas = tk.Canvas(wrap, bg="#1a1a1a", highlightthickness=0)
        h_scroll = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree_canvas.xview)
        v_scroll = ttk.Scrollbar(wrap, orient="vertical", command=self.tree_canvas.yview)
        self.tree_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_canvas.bind("<ButtonPress-1>", lambda e: self.tree_canvas.scan_mark(e.x, e.y))
        self.tree_canvas.bind("<B1-Motion>", lambda e: self.tree_canvas.scan_dragto(e.x, e.y, gain=1))
        self.tree_canvas.bind("<MouseWheel>", lambda e: self.tree_canvas.yview_scroll(int(-e.delta / 120), "units"))
        self.tree_canvas.bind("<Shift-MouseWheel>", lambda e: self.tree_canvas.xview_scroll(int(-e.delta / 120), "units"))

        self.draw_tree_canvas()

    def compute_layout(self):
        by_id = {m["id"]: m for m in self.members_list}
        gens = {}
        for m in self.members_list:
            gens.setdefault(m["gen"], []).append(m)

        def rank(m):
            return SIDE_RANK[get_side(m.get("role"))]

        pos = {}
        layout_results = {}

        for gen in sorted(gens):
            members = gens[gen]
            ids = {m["id"] for m in members}
            seen, units = set(), []
            for m in sorted(members, key=lambda x: x["id"]):
                if m["id"] in seen:
                    continue
                seen.add(m["id"])
                unit = [m]
                sp = by_id.get(m.get("spouse_id"))
                if sp and sp["id"] in ids and sp["id"] not in seen:
                    seen.add(sp["id"])
                    unit.append(sp)
                unit.sort(key=lambda x: (rank(x), 0 if x["gender"] == "Nam" else 1, x["id"]))
                units.append(unit)

            def unit_key(unit):
                side_rank = sum(rank(x) for x in unit) / len(unit)
                px = [pos[x["parent_id"]] for x in unit if x.get("parent_id") in pos]
                return (side_rank, sum(px) / len(px) if px else 0, min(x["id"] for x in unit))

            units.sort(key=unit_key)

            curr_x = 100
            gen_pos = []
            for unit in units:
                for idx, m in enumerate(unit):
                    x = curr_x
                    pos[m["id"]] = x
                    gen_pos.append((m, x))
                    curr_x += BOX_W + 20
                curr_x += 40
            layout_results[gen] = gen_pos

        return layout_results

    def draw_tree_canvas(self):
        self.tree_canvas.delete("all")
        if not self.members_list:
            self.tree_canvas.create_text(400, 200, text="Chưa có dữ liệu để vẽ cây gia phả.", fill="#757575", font=("Segoe UI", 12))
            return

        self.sanitize_relations()
        layout = self.compute_layout()
        # node_coords[id] = (cx, y_top, y_bottom) — tâm ngang, cạnh trên, cạnh dưới của hộp
        node_coords = {}
        # couple_mid[id] = (mid_x, y_mid) — lưu nút giao cho cả hai vợ/chồng
        couple_mid = {}

        for gen, items in layout.items():
            y = START_Y + (gen - 1) * Y_GAP
            self.tree_canvas.create_text(40, y + BOX_H // 2, text=f"Đời {gen}", fill="#bb86fc", font=("Segoe UI", 10, "bold"), anchor="w")

            for m, x in items:
                # Lưu tọa độ: cx = tâm ngang, y_top, y_bottom
                cx = x + BOX_W // 2
                y_top = y
                y_bottom = y + BOX_H
                node_coords[m["id"]] = (cx, y_top, y_bottom)

                bg_color = "#1e2a38" if m["gender"] == "Nam" else "#381e28"
                border_color = "#03dac6" if m["gender"] == "Nam" else "#cf6679"

                self.tree_canvas.create_rectangle(x, y, x + BOX_W, y + BOX_H, fill=bg_color, outline=border_color, width=2)
                self.tree_canvas.create_text(x + 10, y + 15, text=f"{m['name']}", fill="#ffffff", font=("Segoe UI", 10, "bold"), anchor="w")
                role_txt = f"{m.get('role', 'Thành viên')}"
                self.tree_canvas.create_text(x + 10, y + 38, text=role_txt, fill="#aaaaaa", font=("Segoe UI", 8), anchor="w")

        # === Vẽ đường nối hôn nhân + chấm giao giữa cặp vợ chồng ===
        drawn_couples = set()
        for m in self.members_list:
            sid = m.get("spouse_id")
            if not sid or m["id"] in drawn_couples or sid in drawn_couples:
                continue
            if m["id"] not in node_coords or sid not in node_coords:
                continue

            cx1, yt1, yb1 = node_coords[m["id"]]
            cx2, yt2, yb2 = node_coords[sid]

            # Chỉ vẽ nếu cùng hàng (cùng y_top), nếu khác thế hệ thì bỏ qua, dùng cách cũ
            if yt1 != yt2:
                continue

            # Xác định hộp bên trái / bên phải theo tọa độ cx
            if cx1 < cx2:
                cx_trái, cx_phải = cx1, cx2
            else:
                cx_trái, cx_phải = cx2, cx1

            y_mid = yt1 + BOX_H // 2
            mid_x = (cx_trái + cx_phải) / 2

            # Đường gạch nối hôn nhân từ mép trong hộp trái đến mép trong hộp phải tại y_mid
            self.tree_canvas.create_line(
                cx_trái + BOX_W // 2 - 12, y_mid,
                cx_phải - BOX_W // 2 + 12, y_mid,
                fill="#03dac6", width=2, dash=(4, 2)
            )

            # Chấm tròn nhỏ đánh dấu nút giao của cặp tại (mid_x, y_mid)
            self.tree_canvas.create_oval(
                mid_x - 4, y_mid - 4, mid_x + 4, y_mid + 4,
                fill="#03dac6", outline=""
            )

            # Lưu couple_mid cho cả hai thành viên để dùng khi vẽ đường con
            couple_mid[m["id"]] = (mid_x, y_mid)
            couple_mid[sid] = (mid_x, y_mid)
            drawn_couples.add(m["id"])
            drawn_couples.add(sid)

        # === Vẽ đường nối Cha/Mẹ → Con (3 đoạn elbow) ===
        for m in self.members_list:
            pid = m.get("parent_id")
            if not pid or pid not in node_coords:
                continue

            cx_con, cy_top, cy_bot = node_coords[m["id"]]
            px, py_top, py_bot = node_coords[pid]

            # Xác định điểm neo: nếu cha/mẹ thuộc cặp cùng hàng → neo tại nút giao giữa cặp;
            # ngược lại (độc thân hoặc khác hàng) → neo tại tâm đáy hộp cha/mẹ như cũ
            if pid in couple_mid:
                anchor_x, anchor_y = couple_mid[pid]
            else:
                anchor_x, anchor_y = px, py_bot

            # mid_y = đường gom ngang (bus) chung cho các anh chị em, cách cạnh trên con 35px
            mid_y = cy_top - 35

            # Vẽ 3 đoạn elbow: dọc xuống → ngang → dọc lên
            self.tree_canvas.create_line(anchor_x, anchor_y, anchor_x, mid_y, fill="#ffb74d", width=2)
            self.tree_canvas.create_line(anchor_x, mid_y, cx_con, mid_y, fill="#ffb74d", width=2)
            self.tree_canvas.create_line(cx_con, mid_y, cx_con, cy_top, fill="#ffb74d", width=2)

        self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox("all"))

    def backup_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON Files", "*.json")],
                                                title="Xuất bản sao lưu dữ liệu Gia Phả")
        if file_path:
            data = {
                "members": self.members_list,
                "events": self.events,
                "avatar_path": self.avatar_path
            }
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Thành công", "Đã xuất file sao lưu JSON thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {str(e)}")

    def restore_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")],
                                               title="Chọn file JSON để nạp vào hệ thống")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.members_list = data.get("members", [])
                    self.events = data.get("events", [])
                    self.avatar_path = data.get("avatar_path", "Chưa chọn ảnh")
                self.auto_save_data()
                self.refresh_current_view()
                messagebox.showinfo("Thành công", "Đã nạp thành công dữ liệu từ file JSON!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file dữ liệu: {str(e)}")

    def show_about(self):
        self.clear_content()
        frame = tk.Frame(self.content_container, bg="#1e1e1e", padx=40, pady=40)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Hệ Thống Quản Lý Gia Phả Họ", bg="#1e1e1e", fg="#bb86fc",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))
        tk.Label(frame, text="Phiên bản: 5.0 AutoSave (Cập nhật 2026)", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 20))

        desc = (
            "Phần mềm tích hợp cơ chế Tự Động Lưu (Auto-Save) & Tự Động Nạp (Auto-Load).\n"
            "Dữ liệu luôn được đồng bộ tức thì vào file 'family_tree_data.json'.\n\n"
            "Tác giả: Trần Quang Đạt\n"
            "Bản quyền © 2026. Mọi quyền được bảo lưu."
        )
        tk.Label(frame, text=desc, bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 10), justify="left").pack(anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = FamilyTreeApp(root)
    root.mainloop()
