from flet import (
    AppBar,
    colors,
    Container,
    IconButton,
    margin,
    Page,
    PopupMenuButton,
    PopupMenuItem,
    Row,
    Text,
    UserControl,
)

class AppHeader(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.toggle_dark_light_icon = IconButton(
            icon="light_mode",
            selected_icon = "dark_mode",
            tooltip=f"switch light and dark mode",
            on_click=self.toggle_icon,
        )
        self.appbar_items = [
            PopupMenuItem(text="Login"),
            PopupMenuItem(), # divider
            PopupMenuItem(text="Settings"),
        ]
        # Appのpage.appbarフィールドの設定
        self.page.appbar = AppBar(
            title=Text(value="久留米原種育成会", size=22, text_align="center"),
            center_title=False,
            toolbar_height=75,
            bgcolor=colors.SURFACE_VARIANT,
            actions=[
                Container(
                    content=Row(
                        [
                            self.toggle_dark_light_icon,
                            PopupMenuButton(
                                items=self.appbar_items
                            ),
                        ],
                        alignment="spaceBetween",
                    ),
                    margin=margin.only(left=50, right=25)
                )
            ],
        )

    def build(self):
        return self.page.appbar

    def toggle_icon(self, e):
        self.page.theme_mode = "light" if self.page.theme_mode == "dark" else "dark"
        self.page.update()
        self.toggle_dark_light_icon.selected = not self.toggle_dark_light_icon.selected
        self.page.update()