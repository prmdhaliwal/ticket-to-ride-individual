"""Main Tkinter window."""
import math
import tkinter as tk
import sv_ttk
from tkinter import ttk, messagebox
from models.card_color import CardColor
from models.observer import Observer
from models.route_type import RouteType

class MainWindow(Observer):
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.current_face_up_cards = []
        self.current_train_cards = []
        self.current_ticket_cards = []
        self.selected_pool_index = None
        
        self.root.title(f"Ticket to Ride - {self.controller.map_name()}")
        self.root.resizable(False, False)
        
        self.map_background_loaded = False
        self.map_background_image = None
        
        self.setup_ui()
        self.show_starting_ticket_choices()
        self.update()
        self.fit_main_window(True)

    def setup_ui(self):
        self.status_label = ttk.Label(self.root, text="Loading game...", font=("Arial", 16))
        self.status_label.pack(pady=10)
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=20)
        
        left_frame = ttk.LabelFrame(main_frame, text="Routes", padding=10)
        left_frame.grid(row=0, column=0, sticky=tk.N, padx=(0, 12))

        self.route_canvas = tk.Canvas(
            left_frame,
            width=700,
            height=430,
            background="#f7f3e8",
            highlightthickness=0
        )
        self.route_canvas.pack(fill=tk.X, pady=(0, 10))
        self.route_canvas.tag_bind("route", "<Button-1>", self.handle_canvas_route_click)
        self.route_canvas.bind("<Configure>", self.handle_map_resize)
        
        self.route_listbox = ttk.Treeview(left_frame, show="tree", selectmode="browse", height=6)
        self.route_listbox.pack(fill=tk.X, pady=(0, 10))
        self.route_listbox.bind("<<TreeviewSelect>>", self.handle_route_list_selection)
        
        self.claim_btn = ttk.Button(left_frame, text="Claim Route", command=self.claim_route, style="Accent.TButton")
        self.claim_btn.pack(pady=5)
        
        mid_frame = ttk.LabelFrame(main_frame, text="Actions & Cards", padding=10)
        mid_frame.grid(row=0, column=1, sticky=tk.N, padx=(0, 12))
        
        ttk.Label(mid_frame, text="Face-Up Cards").pack(anchor=tk.W, pady=(0, 5))
        self.pool_canvas = tk.Canvas(
            mid_frame,
            width=260,
            height=92,
            background="#f7f1df",
            highlightthickness=0
        )
        self.pool_canvas.pack(pady=(0, 10), fill=tk.X)
        self.pool_canvas.bind("<Configure>", self.handle_pool_resize)
        self.pool_canvas.tag_bind("pool_card", "<Button-1>", self.handle_pool_card_click)
        
        self.draw_pool_btn = ttk.Button(mid_frame, text="Draw from Pool", command=self.draw_pool)
        self.draw_pool_btn.pack(pady=5, fill=tk.X)
        
        self.draw_deck_btn = ttk.Button(mid_frame, text="Draw 1 from Deck", command=self.draw_deck)
        self.draw_deck_btn.pack(pady=5, fill=tk.X)
        
        self.draw_tickets_btn = ttk.Button(mid_frame, text="Draw Tickets", command=self.draw_tickets)
        self.draw_tickets_btn.pack(pady=5, fill=tk.X)
        
        self.end_turn_btn = ttk.Button(mid_frame, text="End Turn", command=self.handle_end_turn, style="Accent.TButton")
        self.end_turn_btn.pack(pady=(20, 5), fill=tk.X)
        
        right_frame = ttk.LabelFrame(main_frame, text="Player Status", padding=10)
        right_frame.grid(row=0, column=2, sticky=tk.N)

        ttk.Label(right_frame, text="Cards").pack(anchor=tk.W)
        self.card_canvas = tk.Canvas(
            right_frame,
            width=260,
            height=92,
            background="#f7f1df",
            highlightthickness=0
        )
        self.card_canvas.pack(fill=tk.X)
        self.card_canvas.bind("<Configure>", self.handle_card_resize)

        ttk.Label(right_frame, text="Tickets").pack(anchor=tk.W, pady=(10, 4))
        ticket_frame = ttk.Frame(right_frame)
        ticket_frame.pack(fill=tk.X)

        self.ticket_canvas = tk.Canvas(
            ticket_frame,
            width=260,
            height=88,
            background="#f7f1df",
            highlightthickness=0
        )
        self.ticket_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ticket_scrollbar = ttk.Scrollbar(
            ticket_frame,
            orient=tk.VERTICAL,
            command=self.ticket_canvas.yview
        )
        self.ticket_canvas.config(yscrollcommand=self.ticket_scrollbar.set)
        self.ticket_canvas.bind("<Configure>", self.handle_ticket_resize)

    def fit_main_window(self, center_window=False):
        self.root.update_idletasks()

        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        max_width = screen_width - 80
        max_height = screen_height - 100

        if width > max_width:
            width = max_width

        if height > max_height:
            height = max_height

        if center_window:
            x = int((screen_width - width) / 2)
            y = int((screen_height - height) / 2)
        else:
            x = self.root.winfo_x()
            y = self.root.winfo_y()

            if x + width > screen_width:
                x = screen_width - width

            if y + height > screen_height:
                y = screen_height - height

            if x < 0:
                x = 0

            if y < 0:
                y = 0

        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)

    def canvas_height_for_items(self, item_count, width, box_width, box_height, gap, maximum_height):
        if item_count <= 0:
            return box_height + gap * 2

        columns = max(1, int((width - gap) / (box_width + gap)))
        rows = math.ceil(item_count / columns)
        height = rows * box_height + (rows + 1) * gap

        if height > maximum_height:
            return maximum_height

        return height

    def fit_popup_window(self, top, minimum_width=360):
        top.update_idletasks()

        width = top.winfo_reqwidth()
        height = top.winfo_reqheight()
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        if width < minimum_width:
            width = minimum_width

        if width > screen_width - 80:
            width = screen_width - 80

        if height > screen_height - 100:
            height = screen_height - 100

        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        top.geometry(f"{width}x{height}+{x}+{y}")
        top.resizable(False, False)

    def add_ticket_checkbuttons(self, top, tickets, ticket_vars):
        if len(tickets) <= 8:
            check_frame = ttk.Frame(top)
            check_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=5)
            checkbox_parent = check_frame
        else:
            check_frame = ttk.Frame(top)
            check_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

            canvas = tk.Canvas(check_frame, height=220, highlightthickness=0)
            scrollbar = ttk.Scrollbar(check_frame, orient=tk.VERTICAL, command=canvas.yview)
            checkbox_parent = ttk.Frame(canvas)
            canvas_window = canvas.create_window((0, 0), window=checkbox_parent, anchor=tk.NW)

            canvas.config(yscrollcommand=scrollbar.set)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            checkbox_parent.bind(
                "<Configure>",
                lambda event: canvas.config(scrollregion=canvas.bbox("all"))
            )
            canvas.bind(
                "<Configure>",
                lambda event: canvas.itemconfig(canvas_window, width=event.width)
            )

        for ticket in tickets:
            var = tk.BooleanVar(value=True)
            text = f"{ticket.from_city} to {ticket.to_city} ({ticket.points})"
            cb = ttk.Checkbutton(checkbox_parent, text=text, variable=var)
            cb.pack(anchor=tk.W, pady=2)
            ticket_vars.append(var)

    def handle_map_resize(self, event):
        self.draw_map()

    def handle_pool_resize(self, event):
        self.draw_face_up_card_boxes(self.current_face_up_cards)

    def handle_card_resize(self, event):
        self.draw_train_card_boxes(self.current_train_cards)

    def handle_ticket_resize(self, event):
        self.draw_ticket_cards(self.current_ticket_cards)

    def handle_pool_card_click(self, event):
        selected = self.pool_canvas.find_withtag("current")

        if not selected:
            return

        tags = self.pool_canvas.gettags(selected[0])

        for tag in tags:
            if tag.startswith("pool_index_"):
                self.selected_pool_index = int(tag.replace("pool_index_", ""))
                self.draw_face_up_card_boxes(self.current_face_up_cards)

    def handle_route_list_selection(self, event):
        self.draw_map()

    def handle_canvas_route_click(self, event):
        selected = self.route_canvas.find_withtag("current")

        if not selected:
            return

        tags = self.route_canvas.gettags(selected[0])
        route_index = None

        for tag in tags:
            if tag.startswith("route_index_"):
                route_index = int(tag.replace("route_index_", ""))

        if route_index is not None:
            self.select_route(route_index)

    def select_route(self, route_index):
        route_items = self.route_listbox.get_children()

        if route_index < 0:
            return

        if route_index >= len(route_items):
            return

        selected_item = route_items[route_index]
        self.route_listbox.selection_set(selected_item)
        self.route_listbox.focus(selected_item)
        self.route_listbox.see(selected_item)
        self.draw_map()

    def selected_route_index(self):
        selection = self.route_listbox.selection()

        if not selection:
            return None

        return self.route_listbox.index(selection[0])

    def draw_map(self):
        if not hasattr(self, "route_canvas"):
            return

        routes = self.controller.get_routes()
        self.route_canvas.delete("all")

        if not routes:
            return

        bounds = self.map_bounds(routes)

        if bounds is None:
            self.route_canvas.create_text(
                20,
                20,
                anchor=tk.NW,
                text="No map coordinates found."
            )
            return

        selected_index = self.selected_route_index()

        for index, route in enumerate(routes):
            self.draw_route(route, index, selected_index, bounds)

        drawn_cities = []

        for route in routes:
            for city in route.cities:
                if city.name not in drawn_cities:
                    self.draw_city(city, bounds)
                    drawn_cities.append(city.name)

    def map_bounds(self, routes):
        x_values = []
        y_values = []

        for route in routes:
            for point in route.visual_points:
                if point.get("x") is not None and point.get("y") is not None:
                    x_values.append(point.get("x"))
                    y_values.append(point.get("y"))

            for city in route.cities:
                if city.x is not None and city.y is not None:
                    x_values.append(city.x)
                    y_values.append(city.y)

        if not x_values or not y_values:
            return None

        return {
            "min_x": min(x_values),
            "max_x": max(x_values),
            "min_y": min(y_values),
            "max_y": max(y_values)
        }

    def to_canvas_point(self, x, y, bounds):
        width = self.route_canvas.winfo_width()
        height = self.route_canvas.winfo_height()

        if width < 100:
            width = 700

        if height < 100:
            height = 430

        padding = 40
        span_x = bounds["max_x"] - bounds["min_x"]
        span_y = bounds["max_y"] - bounds["min_y"]

        if span_x == 0:
            span_x = 1

        if span_y == 0:
            span_y = 1

        scale_x = (width - padding * 2) / span_x
        scale_y = (height - padding * 2) / span_y
        scale = min(scale_x, scale_y)

        used_width = span_x * scale
        used_height = span_y * scale
        offset_x = (width - used_width) / 2
        offset_y = (height - used_height) / 2

        canvas_x = offset_x + (x - bounds["min_x"]) * scale
        canvas_y = offset_y + (y - bounds["min_y"]) * scale

        return canvas_x, canvas_y

    def draw_route(self, route, index, selected_index, bounds):
        canvas_points = []

        if route.visual_points:
            for point in route.visual_points:
                x = point.get("x")
                y = point.get("y")

                if x is not None and y is not None:
                    canvas_x, canvas_y = self.to_canvas_point(x, y, bounds)
                    canvas_points.append(canvas_x)
                    canvas_points.append(canvas_y)
        else:
            for city in route.cities:
                if city.x is not None and city.y is not None:
                    canvas_x, canvas_y = self.to_canvas_point(city.x, city.y, bounds)
                    canvas_points.append(canvas_x)
                    canvas_points.append(canvas_y)

        if len(canvas_points) < 4:
            return

        colour = self.route_display_colour(route)
        tag = "route_index_" + str(index)

        self.route_canvas.create_line(
            canvas_points,
            fill="#d8d0c0",
            width=5,
            smooth=True,
            capstyle=tk.ROUND,
            tags=("route", tag)
        )

        if route.segment_points:
            self.draw_route_segments(route, index, selected_index, bounds)
        else:
            self.draw_route_fallback_segments(route, index, selected_index, canvas_points)

    def draw_route_segments(self, route, index, selected_index, bounds):
        colour = self.route_display_colour(route)
        outline = "#4a4037"
        segment_width = 26
        segment_height = 11

        if index == selected_index:
            segment_width = 30
            segment_height = 13
            outline = "#111111"

        tag = "route_index_" + str(index)

        required_locomotives = 0
        if getattr(route, "route_type", RouteType.STANDARD) == RouteType.FERRY:
            required_locomotives = getattr(route, "required_locomotives", 0)

        for segment_index, point in enumerate(route.segment_points):
            x = point.get("x")
            y = point.get("y")
            rotation = point.get("rotation")

            if rotation is None:
                rotation = 0

            if x is not None and y is not None:
                canvas_x, canvas_y = self.to_canvas_point(x, y, bounds)
                self.draw_segment_shape(
                    canvas_x,
                    canvas_y,
                    rotation,
                    segment_width,
                    segment_height,
                    colour,
                    outline,
                    tag
                )
                if segment_index < required_locomotives:
                    self.draw_ferry_icon(canvas_x, canvas_y, tag)

    def draw_route_fallback_segments(self, route, index, selected_index, canvas_points):
        colour = self.route_display_colour(route)
        outline = "#4a4037"
        segment_width = 26
        segment_height = 11

        if index == selected_index:
            segment_width = 30
            segment_height = 13
            outline = "#111111"

        tag = "route_index_" + str(index)
        start_x = canvas_points[0]
        start_y = canvas_points[1]
        end_x = canvas_points[-2]
        end_y = canvas_points[-1]
        rotation = math.atan2(end_y - start_y, end_x - start_x)

        for segment_index in range(route.length):
            fraction = (segment_index + 1) / (route.length + 1)
            x = start_x + (end_x - start_x) * fraction
            y = start_y + (end_y - start_y) * fraction
            self.draw_segment_shape(
                x,
                y,
                rotation,
                segment_width,
                segment_height,
                colour,
                outline,
                tag
            )
            if self.should_draw_ferry_icon(route, segment_index):
                self.draw_ferry_icon(x, y, tag)

    def draw_segment_shape(self, x, y, rotation, width, height, colour, outline, tag):
        half_width = width / 2
        half_height = height / 2
        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]
        rotated_points = []

        for corner_x, corner_y in corners:
            rotated_x = x + corner_x * math.cos(rotation) - corner_y * math.sin(rotation)
            rotated_y = y + corner_x * math.sin(rotation) + corner_y * math.cos(rotation)
            rotated_points.append(rotated_x)
            rotated_points.append(rotated_y)

        self.route_canvas.create_polygon(
            rotated_points,
            fill=colour,
            outline=outline,
            width=2,
            tags=("route", tag)
        )

    def should_draw_ferry_icon(self, route, segment_index):
        if getattr(route, "route_type", RouteType.STANDARD) != RouteType.FERRY:
            return False

        return segment_index < getattr(route, "required_locomotives", 0)

    def draw_ferry_icon(self, x, y, tag):
        radius = 8
        self.route_canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill="#ffffff",
            outline="#111111",
            width=2,
            tags=("route", tag)
        )
        self.route_canvas.create_text(
            x,
            y,
            text="B",
            fill="#111111",
            font=("Arial", 8, "bold"),
            tags=("route", tag)
        )

    def draw_city(self, city, bounds):
        if city.x is None or city.y is None:
            return

        x, y = self.to_canvas_point(city.x, city.y, bounds)
        radius = 7

        self.route_canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill="#ffffff",
            outline="#222222",
            width=2
        )
        self.route_canvas.create_text(
            x,
            y - 15,
            text=city.name,
            font=("Arial", 8),
            fill="#1f1f1f"
        )

    def route_display_colour(self, route):
        if route.owner is not None:
            players = self.controller.players()
            player_colours = ["#1f66d1", "#c0392b", "#138a43", "#8e44ad", "#c27c0e"]

            for index, player in enumerate(players):
                if player == route.owner:
                    return player_colours[index % len(player_colours)]

            return "#2f2f2f"

        colours = {
            CardColor.BLUE: "#2f6fd6",
            CardColor.GREEN: "#228b45",
            CardColor.YELLOW: "#d9a521",
            CardColor.BLACK: "#333333",
            CardColor.ORANGE: "#d66b2f",
            CardColor.PINK: "#d85aa6",
            CardColor.RED: "#c94b4b",
            CardColor.WHITE: "#e8e8e8",
            CardColor.PURPLE: "#8056c9",
            CardColor.GRAY: "#8c9299",
            CardColor.LOCOMOTIVE: "#5d5d5d"
        }

        if route.colour in colours:
            return colours[route.colour]

        return "#8c9299"

    def route_list_text(self, route):
        owner_name = "None"

        if route.owner is not None:
            owner_name = route.owner.name

        route_details = f"{route.length} {route.colour.value}"
        route_type = getattr(route, "route_type", RouteType.STANDARD)

        if route_type == RouteType.FERRY:
            required_locomotives = getattr(route, "required_locomotives", 0)
            bus_label = "Bus"

            if required_locomotives != 1:
                bus_label = "Buses"

            route_details = (
                f"{route_details}, "
                f"Ferry: {required_locomotives} {bus_label}"
            )

        return (
            f"{route.city_a.name} - {route.city_b.name} "
            f"({route_details}) Owner: {owner_name}"
        )

    def draw_face_up_card_boxes(self, cards):
        if not hasattr(self, "pool_canvas"):
            return

        self.current_face_up_cards = cards
        self.pool_canvas.delete("all")
        width = self.pool_canvas.winfo_width()

        if width < 160:
            width = 260

        self.pool_canvas.config(
            height=self.canvas_height_for_items(len(cards), width, 96, 34, 8, 178)
        )

        if self.selected_pool_index is not None:
            if self.selected_pool_index >= len(cards):
                self.selected_pool_index = None

        if not cards:
            self.pool_canvas.create_text(
                12,
                12,
                anchor=tk.NW,
                text="No face-up cards",
                fill="#5d5145"
            )
            return

        x = 8
        y = 8
        box_width = 96
        box_height = 34
        gap = 8

        for index, card in enumerate(cards):
            if x + box_width > width - 8:
                x = 8
                y += box_height + gap

            self.draw_face_up_card_box(
                x,
                y,
                box_width,
                box_height,
                card,
                index
            )
            x += box_width + gap

        self.pool_canvas.config(scrollregion=(0, 0, width, y + box_height + gap))

    def draw_face_up_card_box(self, x, y, width, height, card, index):
        colour = card.colour
        fill = self.card_display_colour(colour)
        text_colour = self.card_text_colour(colour)
        outline = "#4a4037"
        line_width = 2

        if index == self.selected_pool_index:
            outline = "#111111"
            line_width = 4

        label = colour.value
        if colour == CardColor.LOCOMOTIVE:
            label = "Bus"

        tag = "pool_index_" + str(index)

        self.pool_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=fill,
            outline=outline,
            width=line_width,
            tags=("pool_card", tag)
        )
        self.pool_canvas.create_text(
            x + width / 2,
            y + height / 2,
            text=label,
            fill=text_colour,
            font=("Arial", 9, "bold"),
            tags=("pool_card", tag)
        )

    def draw_train_card_boxes(self, cards):
        if not hasattr(self, "card_canvas"):
            return

        self.current_train_cards = cards
        self.card_canvas.delete("all")

        card_counts = {}
        for card in cards:
            colour = card.colour

            if colour not in card_counts:
                card_counts[colour] = 0

            card_counts[colour] += 1

        width = self.card_canvas.winfo_width()
        if width < 160:
            width = 260

        self.card_canvas.config(
            height=self.canvas_height_for_items(len(card_counts), width, 82, 34, 8, 220)
        )

        if not card_counts:
            self.card_canvas.create_text(
                12,
                12,
                anchor=tk.NW,
                text="No cards",
                fill="#5d5145"
            )
            return

        colour_order = [
            CardColor.BLUE,
            CardColor.GREEN,
            CardColor.YELLOW,
            CardColor.BLACK,
            CardColor.ORANGE,
            CardColor.PINK,
            CardColor.LOCOMOTIVE
        ]
        x = 8
        y = 8
        box_width = 82
        box_height = 34
        gap = 8

        for colour in colour_order:
            if colour in card_counts:
                if x + box_width > width - 8:
                    x = 8
                    y += box_height + gap

                self.draw_train_card_box(
                    x,
                    y,
                    box_width,
                    box_height,
                    colour,
                    card_counts[colour]
                )
                x += box_width + gap

        self.card_canvas.config(scrollregion=(0, 0, width, y + box_height + gap))

    def draw_train_card_box(self, x, y, width, height, colour, count):
        fill = self.card_display_colour(colour)
        text_colour = self.card_text_colour(colour)

        label = colour.value
        if colour == CardColor.LOCOMOTIVE:
            label = "Bus"

        self.card_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=fill,
            outline="#4a4037",
            width=2
        )
        self.card_canvas.create_text(
            x + width / 2,
            y + height / 2,
            text=f"{label} x{count}",
            fill=text_colour,
            font=("Arial", 9, "bold")
        )

    def card_display_colour(self, colour):
        colours = {
            CardColor.BLUE: "#2f6fd6",
            CardColor.GREEN: "#228b45",
            CardColor.YELLOW: "#e3c33c",
            CardColor.BLACK: "#333333",
            CardColor.ORANGE: "#d66b2f",
            CardColor.PINK: "#d85aa6",
            CardColor.LOCOMOTIVE: "#5d5d5d"
        }

        if colour in colours:
            return colours[colour]

        return "#8c9299"

    def card_text_colour(self, colour):
        if colour == CardColor.YELLOW:
            return "#1f1f1f"

        return "#ffffff"

    def draw_ticket_cards(self, tickets):
        if not hasattr(self, "ticket_canvas"):
            return

        self.current_ticket_cards = tickets
        self.ticket_canvas.delete("all")

        width = self.ticket_canvas.winfo_width()
        if width < 160:
            width = 260

        card_height = 72
        gap = 8
        content_height = len(tickets) * (card_height + gap) + gap

        if not tickets:
            content_height = card_height + gap * 2

        max_height = self.root.winfo_screenheight() - 470
        if max_height < 120:
            max_height = 120

        if max_height > 330:
            max_height = 330

        canvas_height = content_height
        if canvas_height > max_height:
            canvas_height = max_height

        self.ticket_canvas.config(height=canvas_height)

        if content_height > canvas_height:
            if not self.ticket_scrollbar.winfo_ismapped():
                self.ticket_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            if self.ticket_scrollbar.winfo_ismapped():
                self.ticket_scrollbar.pack_forget()

        if not tickets:
            self.ticket_canvas.create_text(
                12,
                12,
                anchor=tk.NW,
                text="No tickets",
                fill="#5d5145"
            )
            self.ticket_canvas.config(scrollregion=(0, 0, width, content_height))
            return

        card_width = width - 20
        if card_width > 300:
            card_width = 300

        y = 8

        for ticket in tickets:
            self.draw_ticket_card(10, y, card_width, card_height, ticket)
            y += card_height + 8

        self.ticket_canvas.config(scrollregion=(0, 0, width, y))

    def draw_ticket_card(self, x, y, width, height, ticket):
        score_width = 38
        score_x = x + width - score_width

        self.ticket_canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill="#fffaf0",
            outline="#c9b48d",
            width=2
        )
        self.ticket_canvas.create_rectangle(
            score_x,
            y,
            x + width,
            y + height,
            fill="#c76128",
            outline="#c76128"
        )
        self.ticket_canvas.create_text(
            score_x + score_width / 2,
            y + height / 2,
            text=str(ticket.points),
            fill="#ffffff",
            font=("Arial", 18, "bold")
        )
        self.ticket_canvas.create_oval(
            x + 14,
            y + 18,
            x + 24,
            y + 28,
            fill="#4fa85a",
            outline="#315f35"
        )
        self.ticket_canvas.create_oval(
            x + 14,
            y + 48,
            x + 24,
            y + 58,
            fill="#2f6fd6",
            outline="#274f94"
        )
        self.ticket_canvas.create_line(
            x + 19,
            y + 28,
            x + 19,
            y + 48,
            fill="#d66b2f",
            dash=(3, 3),
            width=2
        )
        self.ticket_canvas.create_text(
            x + 34,
            y + 13,
            anchor=tk.NW,
            text=ticket.from_city,
            fill="#6b2f25",
            font=("Arial", 9, "bold"),
            width=width - score_width - 42
        )
        self.ticket_canvas.create_text(
            x + 34,
            y + 43,
            anchor=tk.NW,
            text=ticket.to_city,
            fill="#254b75",
            font=("Arial", 9, "bold"),
            width=width - score_width - 42
        )

    def handle_end_turn(self):
        msg = self.controller.end_turn()
        if msg not in ["Next turn.", "The game is over.", "Game over."]:
            messagebox.showwarning("Warning", msg)
        self.update()

    def claim_route(self):
        selection = self.route_listbox.selection()
        if not selection:
            messagebox.showwarning("Warning", "Select a route.")
            return
        index = self.route_listbox.index(selection[0])
        success, msg = self.controller.claim_route(index)
        if not success:
            messagebox.showerror("Error", msg)

    def draw_pool(self):
        if self.selected_pool_index is None:
            messagebox.showwarning("Warning", "Select a face-up card.")
            return

        success, msg = self.controller.draw_train_card(
            from_deck=False,
            pool_index=self.selected_pool_index
        )
        if not success:
            messagebox.showerror("Error", msg)
        else:
            self.selected_pool_index = None

    def draw_deck(self):
        success, msg = self.controller.draw_train_card(from_deck=True)
        if not success:
            messagebox.showerror("Error", msg)

    def draw_tickets(self):
        result, msg = self.controller.draw_destination_tickets()
        if result is False:
            messagebox.showerror("Error", msg)
            return

        tickets = self.controller.get_visible_destination_tickets()
        self.show_ticket_selection(tickets)

    def show_starting_ticket_choices(self):
        choices = self.controller.starting_ticket_choices()

        for player, tickets in choices:
            self.show_starting_ticket_selection(player, tickets)

    def show_starting_ticket_selection(self, player, tickets):
        top = tk.Toplevel(self.root)
        top.title("Starting Tickets")
        top.protocol("WM_DELETE_WINDOW", lambda: None)
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        ttk.Label(
            top,
            text=f"{player.name}, choose starting tickets to keep:"
        ).pack(pady=(15, 10), padx=20)

        ticket_vars = []
        self.add_ticket_checkbuttons(top, tickets, ticket_vars)

        def confirm():
            kept = []
            returned = []

            for index, var in enumerate(ticket_vars):
                if var.get():
                    kept.append(tickets[index])
                else:
                    returned.append(tickets[index])

            success, msg = self.controller.choose_starting_tickets(
                player,
                kept,
                returned
            )

            if not success:
                messagebox.showerror("Error", msg)
            else:
                top.destroy()

        ttk.Button(
            top,
            text="Keep Selected",
            command=confirm,
            style="Accent.TButton"
        ).pack(pady=(15, 20), padx=20)

        sv_ttk.set_theme("light")
        self.fit_popup_window(top)

        self.root.wait_window(top)

    def show_ticket_selection(self, tickets):
        top = tk.Toplevel(self.root)
        top.title("Ticket Market")
        top.protocol("WM_DELETE_WINDOW", lambda: None) # Disable closing window
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)
        
        ttk.Label(
            top,
            text="Choose visible market tickets to keep:"
        ).pack(pady=(15, 10), padx=20)
        
        ticket_vars = []
        self.add_ticket_checkbuttons(top, tickets, ticket_vars)
            
        def confirm():
            kept = []
            returned = []

            for index, var in enumerate(ticket_vars):
                if var.get():
                    kept.append(tickets[index])
                else:
                    returned.append(tickets[index])

            success, msg = self.controller.keep_destination_tickets(
                kept_tickets=kept,
                returned_tickets=returned
            )

            if not success:
                messagebox.showerror("Error", msg)
            else:
                top.destroy()
            
        ttk.Button(
            top,
            text="Keep Selected",
            command=confirm,
            style="Accent.TButton"
        ).pack(pady=(15, 20), padx=20)

        self.fit_popup_window(top)

    def show_game_over_popup(self, winners, scores):
        top = tk.Toplevel(self.root)
        top.title("Game Over!")
        top.transient(self.root)
        top.grab_set()
        top.resizable(False, False)

        winner_names = ", ".join(w.name for w in winners)

        ttk.Label(
            top,
            text="Game Over!",
            font=("Arial", 28, "bold"),
            foreground="#c76128"
        ).pack(pady=(30, 10))

        ttk.Label(
            top,
            text=f"Winner: {winner_names} 🏆",
            font=("Arial", 18, "bold")
        ).pack(pady=(5, 30))

        frame = ttk.Frame(top)
        frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for i, (player, score) in enumerate(sorted_scores):
            ttk.Label(
                frame,
                text=f"{i+1}. {player.name}",
                font=("Arial", 16)
            ).grid(row=i, column=0, sticky="w", pady=8)

            ttk.Label(
                frame,
                text=f"{score} pts",
                font=("Arial", 16, "bold")
            ).grid(row=i, column=1, sticky="e", pady=8, padx=(40, 0))

        frame.columnconfigure(0, weight=1)

        ttk.Button(
            top,
            text="Exit Game",
            command=self.root.destroy,
            style="Accent.TButton"
        ).pack(pady=30)

        self.fit_popup_window(top, 450)

    def update(self):
        current_player = self.controller.current_player()
        
        if self.controller.game_over():
            if getattr(self, "_game_over_shown", False):
                return
            self._game_over_shown = True

            winners = self.controller.winners()
            winner_names = ", ".join(w.name for w in winners)

            self.status_label.config(text=f"Game Over! Winners: {winner_names}")
            self.end_turn_btn.config(state=tk.DISABLED)
            
            scores = self.controller.final_scores()
            self.show_game_over_popup(winners, scores)
            return
            
        if current_player:
            self.status_label.config(
                text=f"Current Turn: {current_player.name} | "
                     f"Score: {current_player.score} | "
                     f"Buses: {current_player.trains_left}"
            )
            
            turn_ended = self.controller.turn_ended()
            state = tk.NORMAL

            if turn_ended:
                state = tk.DISABLED

            self.claim_btn.config(state=state)
            self.draw_pool_btn.config(state=state)
            self.draw_deck_btn.config(state=state)
            self.draw_tickets_btn.config(state=state)
            self.end_turn_btn.config(state=tk.NORMAL if turn_ended else tk.DISABLED)
            
            # Efficiently update routes instead of delete/recreate
            routes = self.controller.get_routes()
            route_items = self.route_listbox.get_children()
            
            if len(route_items) != len(routes):
                self.route_listbox.delete(*route_items)
                for r in routes:
                    route_text = self.route_list_text(r)
                    self.route_listbox.insert("", tk.END, text=route_text)
            else:
                for i, r in enumerate(routes):
                    new_text = self.route_list_text(r)
                    if self.route_listbox.item(route_items[i], "text") != new_text:
                        self.route_listbox.item(route_items[i], text=new_text)

            self.draw_map()
                
            cards = self.controller.get_face_up_cards()
            self.draw_face_up_card_boxes(cards)
            self.draw_train_card_boxes(current_player.train_cards)
            self.draw_ticket_cards(current_player.destination_tickets)
