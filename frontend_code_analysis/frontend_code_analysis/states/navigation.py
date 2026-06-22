import reflex as rx


class NavigationState(rx.State):
    # Active navigation page
    current_page: str = "/"

    # Theme mode tracker
    is_dark_mode: bool = True

    @rx.event
    def set_page(self, page_route: str):
        self.current_page = page_route
        return rx.redirect(page_route)

    @rx.event
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode