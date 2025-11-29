
import customtkinter as ctk
import tkinter as tk
import random
import math
import time

# ----------------------------
# Dijkstra shortest path
# ----------------------------
def dijkstra(graph, n, src, dst):
    INF = 10**9
    dist = [INF] * n
    visited = [False] * n
    parent = [-1] * n
    dist[src] = 0

    for _ in range(n - 1):
        u = -1
        mn = INF
        for i in range(n):
            if not visited[i] and dist[i] < mn:  
                mn = dist[i]
                u = i
        if u == -1:
            break
        visited[u] = True
        for v in range(n):
            if graph[u][v] != 0 and not visited[v]:
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u] + graph[u][v]
                    parent[v] = u

    path = []
    cur = dst
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return dist[dst], path

# ----------------------------
# App
# ----------------------------
class NavApp(ctk.CTk):
    def __init__(self, width=880, height=640):
        super().__init__()
        ctk.set_appearance_mode("dark")

        self.title("Cyberpunk Navigation — Magenta")
        self.geometry(f"{width}x{height}")
        self.minsize(760, 520)
        self.configure(fg_color="#05020A")

        # data
        self.n = 0
        self.city_names = []
        self.graph = []
        self.positions = {}
        self.current_path = []

        # dimensions
        self.sidebar_w = 160
        self.width = width - self.sidebar_w
        self.height = height

        self._build_sidebar()
        self._build_layer_container()
        self._create_layers()
        self._load_demo()

    # ----------------------------
    # Sidebar
    # ----------------------------
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=self.sidebar_w, height=self.height, fg_color="#070012")
        sb.place(x=0, y=0)
        sb.pack_propagate(False)

        lbl = ctk.CTkLabel(sb, text="CYBERPUNK", font=("Segoe UI", 18, "bold"), text_color="#FFB3FF")
        lbl.pack(pady=(18, 6))

        sub = ctk.CTkLabel(sb, text="Route System", font=("Segoe UI", 12), text_color="#E9D3FF")
        sub.pack(pady=(0, 18))

        btn_cities = ctk.CTkButton(sb, text="Cities", command=lambda: self.switch_to("cities"),
                                   fg_color="#C84BFF", hover_color="#E37BFF")
        btn_cities.pack(pady=8, padx=12, fill="x")

        btn_matrix = ctk.CTkButton(sb, text="Distances", command=lambda: self.switch_to("matrix"),
                                   fg_color="#C84BFF", hover_color="#E37BFF")
        btn_matrix.pack(pady=8, padx=12, fill="x")

        btn_nav = ctk.CTkButton(sb, text="Navigate", command=lambda: self.switch_to("nav"),
                                fg_color="#FF60D8", hover_color="#FF8FEB", text_color="black")
        btn_nav.pack(pady=12, padx=12, fill="x")

        theme_lbl = ctk.CTkLabel(sb, text="Theme", text_color="#FFD6FF")
        theme_lbl.pack(pady=(20, 6))

        mag_btn = ctk.CTkButton(sb, text="Magenta (active)", state="disabled", fg_color="#FF60D8")
        mag_btn.pack(padx=12, pady=(0, 10), fill="x")

    # ----------------------------
    # Layer container
    # ----------------------------
    def _build_layer_container(self):
        self.layer_container = ctk.CTkFrame(self, width=self.width, height=self.height, fg_color="#05020A")
        self.layer_container.place(x=self.sidebar_w, y=0)
        self.layer_container.pack_propagate(False)

        self.frames = {}
        self.active_frame = None

    # ----------------------------
    # Create layers
    # ----------------------------
    def _create_layers(self):
        # -------- Cities Page --------
        fr_cities = ctk.CTkFrame(self.layer_container, width=self.width, height=self.height, fg_color="#05020A")
        fr_cities.pack_propagate(False)
        self.frames["cities"] = fr_cities

        title = ctk.CTkLabel(fr_cities, text="Enter Cities", font=("Segoe UI", 20, "bold"), text_color="#FFB3FF")
        title.pack(pady=(18, 6))

        bottom = ctk.CTkFrame(fr_cities, fg_color="#0A0014")
        bottom.pack(padx=18, pady=12, fill="both", expand=True)

        lbl_num = ctk.CTkLabel(bottom, text="Number of cities:", text_color="#EDE0FF")
        lbl_num.pack(anchor="w", pady=(8, 2))
        self.entry_num = ctk.CTkEntry(bottom)
        self.entry_num.pack(anchor="w", pady=(0, 8))

        btn_gen = ctk.CTkButton(bottom, text="Generate Inputs", command=self._generate_city_inputs,
                                fg_color="#C84BFF", hover_color="#E37BFF")
        btn_gen.pack(anchor="w", pady=(6, 12))

        self.city_inputs_container = ctk.CTkFrame(bottom, fg_color="#05010A")
        self.city_inputs_container.pack(fill="both", expand=True, pady=(6, 8))

        btn_save = ctk.CTkButton(bottom, text="Save Cities", command=self._save_cities,
                                 fg_color="#FF60D8", text_color="black")
        btn_save.pack(pady=10, anchor="e", padx=6)

        # -------- Matrix Page --------
        fr_matrix = ctk.CTkFrame(self.layer_container, width=self.width, height=self.height, fg_color="#05020A")
        fr_matrix.pack_propagate(False)
        self.frames["matrix"] = fr_matrix

        t2 = ctk.CTkLabel(fr_matrix, text="Distance Matrix", font=("Segoe UI", 20, "bold"), text_color="#FFB3FF")
        t2.pack(pady=(18, 8))

        m_bottom = ctk.CTkFrame(fr_matrix, fg_color="#0A0014")
        m_bottom.pack(padx=18, pady=12, fill="both", expand=True)

        btn_gen_mat = ctk.CTkButton(m_bottom, text="Generate Matrix Fields",
                                    command=self._generate_matrix_inputs, fg_color="#C84BFF")
        btn_gen_mat.pack(pady=(6, 8))

        self.matrix_inputs_container = ctk.CTkFrame(m_bottom, fg_color="#05010A")
        self.matrix_inputs_container.pack(fill="both", expand=True)

        btn_save_mat = ctk.CTkButton(m_bottom, text="Save Matrix", command=self._save_matrix,
                                     fg_color="#FF60D8", text_color="black")
        btn_save_mat.pack(pady=10, anchor="e", padx=6)

        # -------- Navigation Page --------
        fr_nav = ctk.CTkFrame(self.layer_container, width=self.width, height=self.height, fg_color="#05020A")
        fr_nav.pack_propagate(False)
        self.frames["nav"] = fr_nav

        t3 = ctk.CTkLabel(fr_nav, text="Navigation", font=("Segoe UI", 20, "bold"), text_color="#FFB3FF")
        t3.pack(pady=(14, 6))

        canvas_holder = ctk.CTkFrame(fr_nav, width=self.width-36, height=420, fg_color="#080010")
        canvas_holder.pack(padx=18, pady=(6, 8))
        canvas_holder.pack_propagate(False)

        self.canvas = tk.Canvas(canvas_holder, width=self.width-52, height=400,
                                bg="#040008", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        self.canvas.create_rectangle(4, 4, self.width-60, 396, outline="#FF60D8", width=2)

        controls = ctk.CTkFrame(fr_nav, fg_color="#0A0014")
        controls.pack(fill="x", padx=18, pady=(6, 12))

        lbl_src = ctk.CTkLabel(controls, text="Source", text_color="#E9D3FF")
        lbl_src.grid(row=0, column=0, padx=(6,6), pady=8)
        self.src_combo = ctk.CTkComboBox(controls, values=["-"])
        self.src_combo.grid(row=0, column=1, padx=(6,12), pady=8)

        lbl_dst = ctk.CTkLabel(controls, text="Destination", text_color="#E9D3FF")
        lbl_dst.grid(row=0, column=2, padx=(6,6), pady=8)
        self.dst_combo = ctk.CTkComboBox(controls, values=["-"])
        self.dst_combo.grid(row=0, column=3, padx=(6,12), pady=8)

        find_btn = ctk.CTkButton(controls, text="FIND SHORTEST ROUTE",
                                 fg_color="#FF60D8", text_color="black",
                                 command=self._on_find_route)
        find_btn.grid(row=1, column=0, columnspan=4, pady=(8,10), padx=10, sticky="ew")

        self.result_label = ctk.CTkLabel(fr_nav, text="", text_color="#E0D6FF")
        self.result_label.pack(pady=(6,12))

        # place frames offscreen initially
        for name, f in self.frames.items():
            f.place(x=self.width, y=0)

        self.switch_to("cities", animate=False)

    # ----------------------------
    # Animated page transition
    # ----------------------------
    def switch_to(self, name, animate=True):
        if name not in self.frames:
            return
        target = self.frames[name]

        if self.active_frame is None:
            target.place_configure(x=0, y=0)
            self.active_frame = target
            return

        if target is self.active_frame:
            return

        start_active_x = 0
        steps = 18
        delay = 12

        target.place_configure(x=self.width, y=0)

        def animate_step(step=0):
            if step > steps:
                try:
                    self.active_frame.place_forget()
                except:
                    pass
                target.place_configure(x=0, y=0)
                self.active_frame = target
                return

            t = step / steps
            ease = 1 - (1 - t)**2

            self.active_frame.place_configure(x=int(-ease*self.width))
            target.place_configure(x=int((1-ease)*self.width))

            self.after(delay, lambda: animate_step(step+1))

        animate_step() if animate else (
            self.active_frame.place_forget(),
            target.place_configure(x=0, y=0),
            setattr(self, 'active_frame', target)
        )

    # ----------------------------
    # City Inputs
    # ----------------------------
    def _generate_city_inputs(self):
        for w in self.city_inputs_container.winfo_children():
            w.destroy()
        try:
            n = int(self.entry_num.get())
            if n < 1:
                return
        except:
            return

        self.n = n
        self.city_entries = []

        for i in range(n):
            row = ctk.CTkFrame(self.city_inputs_container, fg_color="#05010A")
            row.pack(fill="x", pady=6, padx=6)

            lbl = ctk.CTkLabel(row, text=f"City {i+1} name:", width=120, anchor="w")
            lbl.pack(side="left", padx=(6, 8))

            e = ctk.CTkEntry(row, width=180)
            e.pack(side="left", fill="x", expand=True, padx=(0, 6))
            self.city_entries.append(e)

    def _save_cities(self):
        if not hasattr(self, "city_entries"):
            return

        self.city_names = [
            e.get() if e.get().strip() != "" else f"Node{i+1}"
            for i, e in enumerate(self.city_entries)
        ]

        self.graph = [[0]*self.n for _ in range(self.n)]
        self._update_nav_options()
        self._scatter_positions()
        self._draw_map()

    # ----------------------------
    # Matrix Inputs
    # ----------------------------
    def _generate_matrix_inputs(self):
        for w in self.matrix_inputs_container.winfo_children():
            w.destroy()

        if self.n == 0:
            return

        self.matrix_inputs = []

        for i in range(self.n):
            rowf = ctk.CTkFrame(self.matrix_inputs_container, fg_color="#05010A")
            rowf.pack(padx=6, pady=3, anchor="w")

            row = []
            for j in range(self.n):
                e = ctk.CTkEntry(rowf, width=60)  # <<<< increased box size
                e.pack(side="left", padx=3)

                if i == j:
                    e.insert(0, "0")

                row.append(e)

            self.matrix_inputs.append(row)

    def _save_matrix(self):
        if not hasattr(self, "matrix_inputs"):
            return

        g = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                try:
                    val = int(self.matrix_inputs[i][j].get())
                except:
                    val = 0
                row.append(val)
            g.append(row)

        self.graph = g
        self._draw_map()

    # ----------------------------
    # Navigation helpers
    # ----------------------------
    def _update_nav_options(self):
        if self.n == 0:
            self.src_combo.configure(values=["-"])
            self.dst_combo.configure(values=["-"])
            return

        self.src_combo.configure(values=self.city_names)
        self.dst_combo.configure(values=self.city_names)

        if self.n >= 2:
            self.src_combo.set(self.city_names[0])
            self.dst_combo.set(self.city_names[1])
        else:
            self.src_combo.set(self.city_names[0])
            self.dst_combo.set(self.city_names[0])

    def _scatter_positions(self):
        self.positions = {}
        W = int(self.canvas.cget("width"))
        H = int(self.canvas.cget("height"))
        margin = 40

        for i in range(self.n):
            x = random.randint(margin, W-margin)
            y = random.randint(margin, H-margin)
            self.positions[i] = (x, y)

    def _draw_map(self):
        self.canvas.delete("all")

        W = int(self.canvas.cget("width"))
        H = int(self.canvas.cget("height"))

        self.canvas.create_rectangle(4, 4, W-4, H-4, outline="#FF60D8", width=2)

        # edges
        if self.graph:
            for i in range(self.n):
                for j in range(i+1, self.n):
                    if self.graph[i][j] != 0:
                        x1,y1 = self.positions[i]
                        x2,y2 = self.positions[j]
                        self.canvas.create_line(x1, y1, x2, y2, fill="#7A2AFF", width=2, smooth=True)

        # nodes
        for i in range(self.n):
            x,y = self.positions[i]

            self.canvas.create_oval(x-8,y-8, x+8,y+8, fill="#FF60D8", outline="#FFD1FF", width=2)
            self.canvas.create_text(x, y-20, text=self.city_names[i],
                                    fill="#FFE6FF", font=("Segoe UI", 10))

    def _on_find_route(self):
        if self.n == 0 or not self.graph:
            self.result_label.configure(text="No data: define cities and matrix first")
            return

        try:
            src = self.city_names.index(self.src_combo.get())
            dst = self.city_names.index(self.dst_combo.get())
        except:
            self.result_label.configure(text="Invalid source/destination")
            return

        dist, path = dijkstra(self.graph, self.n, src, dst)

        if dist >= 10**9:
            self.result_label.configure(text="No Route Found")
            return

        self.current_path = path
        self.result_label.configure(
            text=f"Distance: {dist} | Path: {' → '.join(self.city_names[p] for p in path)}"
        )

        self._draw_map()
        self._draw_highlight_path(path)
        self._start_motorcycle(path)

    # ----------------------------
    # Highlight static path
    # ----------------------------
    def _draw_highlight_path(self, path):
        if len(path) < 2:
            return

        for i in range(len(path)-1):
            a = path[i]
            b = path[i+1]
            x1,y1 = self.positions[a]
            x2,y2 = self.positions[b]

            self.canvas.create_line(x1,y1,x2,y2, fill="#00FFE0", width=5, smooth=True)

    # ----------------------------
    # Motorcycle animation
    # ----------------------------
    def _start_motorcycle(self, path):
        if len(path) < 2:
            return

        if hasattr(self, "motor_parts"):
            for p in self.motor_parts:
                try:
                    self.canvas.delete(p)
                except:
                    pass

        self.motor_parts = []

        poly = []
        steps = 40

        for i in range(len(path)-1):
            a = path[i]; b = path[i+1]
            x1,y1 = self.positions[a]
            x2,y2 = self.positions[b]
            for s in range(steps):
                t = s/steps
                x = x1 + (x2-x1)*t
                y = y1 + (y2-y1)*t
                poly.append((x,y))
        poly.append(self.positions[path[-1]])

        x0,y0 = poly[0]

        body = self.canvas.create_rectangle(x0-10,y0-6, x0+10,y0+6, fill="#00FFE0", outline="#B3FFF0")
        wheel_l = self.canvas.create_oval(x0-16,y0+6, x0-4,y0+18, fill="#111111")
        wheel_r = self.canvas.create_oval(x0+4,y0+6, x0+16,y0+18, fill="#111111")
        head = self.canvas.create_polygon(x0+14,y0, x0+6,y0-6, x0+6,y0+6, fill="#FF60D8")

        self.motor_parts = [body, wheel_l, wheel_r, head]

        idx = 0
        prev_x, prev_y = poly[0]
        step_delay = 8

        def move():
            nonlocal idx, prev_x, prev_y
            if idx >= len(poly):
                return

            x,y = poly[idx]
            dx = x - prev_x
            dy = y - prev_y

            for p in self.motor_parts:
                self.canvas.move(p, dx, dy)

            prev_x, prev_y = x,y
            idx += 1
            self.after(step_delay, move)

        move()

    # ----------------------------
    # Demo
    # ----------------------------
    def _load_demo(self):
        self.n = 4
        self.city_names = ["A", "B", "C", "D"]
        self.graph = [
            [0,5,9,0],
            [5,0,3,7],
            [9,3,0,4],
            [0,7,4,0]
        ]

        self._update_nav_options()
        self._scatter_positions()
        self._draw_map()


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app = NavApp(width=1000, height=700)
    app.mainloop()
