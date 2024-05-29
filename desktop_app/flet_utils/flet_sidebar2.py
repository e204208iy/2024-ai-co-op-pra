from flet import (
    Page,
    alignment,
    border_radius,
    colors,
    Container,
    CrossAxisAlignment,
    FloatingActionButton,
    Icon,
    IconButton,
    icons,
    NavigationRail,
    NavigationRailDestination,
    NavigationRailLabelType,
    Row,
    Text,
    UserControl,
)


class Sidebar(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.nav_rail_visible = True
        self.nav_rail_items = [
            NavigationRailDestination(
                icon_content=Icon(icons.TABLE_CHART),
                selected_icon_content=Icon(icons.TABLE_CHART), 
                label="統計"
            ),
            NavigationRailDestination(
                icon=icons.DRIVE_FILE_MOVE_OUTLINE,
                selected_icon=icons.DRIVE_FILE_MOVE_OUTLINE,
                label="ディレクトリ"
            ),
            NavigationRailDestination(
                icon=icons.DOWNLOAD,
                selected_icon_content=Icon(icons.DOWNLOAD), 
                label_content=Text("CSV"),
                # on_change=lambda _: page.go("/csv")
            ),
        ]
        self.nav_rail = NavigationRail(
            height= 300,
            selected_index=None,
            label_type=NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=FloatingActionButton(icon=icons.FILE_UPLOAD, text="home"),
            group_alignment=-0.9,
            destinations=self.nav_rail_items,
            on_change=lambda _: page.go("/home"),
        )
        self.toggle_nav_rail_button = IconButton(
            icon=icons.ARROW_CIRCLE_LEFT,
            icon_color=colors.BLUE_GREY_400,
            selected=False,
            selected_icon=icons.ARROW_CIRCLE_RIGHT,
            on_click=self.toggle_nav_rail,
            tooltip="Collapse Nav Bar",   
        )

    def build(self):
        self.view = Container(
                content=Row(
                [
                    self.nav_rail,
                    Container( # vertical divider
                        bgcolor=colors.BLACK26,
                        border_radius=border_radius.all(30),
                        height=220,
                        alignment=alignment.center_right,
                        width=2
                    ),
                    self.toggle_nav_rail_button,
                ],
                expand=True,
                vertical_alignment=CrossAxisAlignment.START,
                visible=self.nav_rail_visible,
            )
        )
        return self.view

    def toggle_nav_rail(self, e):
        self.nav_rail.visible = not self.nav_rail.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.toggle_nav_rail_button.tooltip = "Open Side Bar" if self.toggle_nav_rail_button.selected else "Collapse Side Bar"
        self.view.update()
        self.page.update()