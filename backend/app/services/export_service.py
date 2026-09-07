import csv
import io

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from app.models.attendance import Attendance

COLUMNS = ["Date", "Supervisor", "Worker", "Status", "Input Parts", "Working Hours", "Machine Stop", "Remarks"]


def _row(attendance: Attendance) -> list[str]:
    return [
        attendance.attendance_date.isoformat(),
        attendance.attendance_taker.name,
        attendance.worker_name,
        attendance.attendance_status.value,
        str(attendance.input_parts),
        str(attendance.total_working_hours),
        str(attendance.machine_stopped_time),
        attendance.remarks or "",
    ]


def to_csv(records: list[Attendance]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(COLUMNS)
    for record in records:
        writer.writerow(_row(record))
    return buffer.getvalue().encode("utf-8")


def to_excel(records: list[Attendance]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Attendance"
    sheet.append(COLUMNS)
    for record in records:
        sheet.append(_row(record))
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def to_pdf(records: list[Attendance]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    data = [COLUMNS] + [_row(record) for record in records]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
            ]
        )
    )
    doc.build([table])
    return buffer.getvalue()
