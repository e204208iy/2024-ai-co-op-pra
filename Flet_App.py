import flet
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Column,
    Text,
    icons,
    colors,
)
from desktop_app.ai_utils.NoUseOCR_createCSV import CreateNumCsv
from desktop_app.ai_utils.CreateCSVClass import CreateCSVClass

from desktop_app.flet_utils.flet_header import AppHeader
from desktop_app.flet_utils.flet_sidebar import Sidebar

def main(page: Page):
    page.title = "久留米原種育成会"
    page.padding = 10
    
    # sidebar = Sidebar()
    # インスタンス作成時にpage.appbarにナビゲーションバーが設定される
    AppHeader(page)
    # main
    t1 = Text(
        "1.フォルダをアップロードしてください。",
        size=25,
        weight=flet.FontWeight.W_900,
        )
    t2 = Text(
        "2.結果を見る",
        size=25,
        weight=flet.FontWeight.W_900,
        )
    disc = Text(
        "ダウンロードに「cucumber_num_今日の日付.csv」が生成されます",
        size=20,
        weight=flet.FontWeight.W_900,
    )
    # Open directory dialog
    def get_directory_result(e: FilePickerResultEvent):
        directory_path.value = e.path if e.path else "Cancelled!"
        create_csv = CreateCSVClass(directory_path.value)
        # create_csv = CreateNumCsv(directory_path.value)
        create_csv.create_csv()

        directory_path.update()

    get_directory_dialog = FilePicker(on_result=get_directory_result)
    directory_path = Text()
    
    # hide all dialogs in overlay
    page.overlay.extend([get_directory_dialog])

    main =flet.Container(
        Column([
        Row([
            t1,
        ]),
        Row([
            ElevatedButton(
                "Open directory",
                icon=icons.FOLDER_OPEN,
                on_click=lambda _: get_directory_dialog.get_directory_path(),
                disabled=page.web,
            ),
            directory_path,
        ]),
        Row([
            t2,
        ]),
        Row([
            disc,
        ])
    ]),
    )
    layout =  Row(
        controls=[main],
        #controls=[sidebar,main]
        tight=True, # 水平方向の隙間をどうするか。デフォルトはFalseですべての要素に余白を与える。
        expand=True, # 利用可能なスペースを埋めるようにするか。
        vertical_alignment="start", # 画面上部から表示。ほかに"center"や"end"などの値がある。
    )

    page.add(layout)
    page.update()

flet.app(target=main)