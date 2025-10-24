Attribute VB_Name = "ExcelToPDF_Analyzer"
'=================================================================================
' Excel to PDF Converter & Analyzer
' Smart PDF Generation with Auto-Analysis and Customization
'=================================================================================

Option Explicit

' Module-level variables
Private Type SheetAnalysis
    SheetName As String
    UsedRange As String
    RowCount As Long
    ColumnCount As Long
    HasHeaders As Boolean
    DataDensity As String
    EstimatedPages As Long
    RecommendedOrientation As String
    HasWideColumns As Boolean
    RequiresScaling As Boolean
    OptimalScale As Long
End Type

Private AnalysisResults() As SheetAnalysis
Private SelectedWorkbook As Workbook

'=================================================================================
' MAIN ENTRY POINT - Launch the Analyzer
'=================================================================================
Public Sub LaunchPDFConverter()
    On Error GoTo ErrorHandler

    ' Show the main UserForm
    frmPDFConverter.Show

    Exit Sub

ErrorHandler:
    MsgBox "Error launching PDF Converter: " & Err.Description, vbCritical, "Error"
End Sub

'=================================================================================
' SMART ANALYSIS ENGINE
'=================================================================================
Public Function AnalyzeWorkbook(wb As Workbook) As SheetAnalysis()
    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Dim i As Long
    Dim tempResults() As SheetAnalysis

    ReDim tempResults(1 To wb.Worksheets.Count)

    For i = 1 To wb.Worksheets.Count
        Set ws = wb.Worksheets(i)

        With tempResults(i)
            .SheetName = ws.Name

            ' Analyze used range
            If ws.UsedRange.Rows.Count > 0 Then
                .UsedRange = ws.UsedRange.Address
                .RowCount = ws.UsedRange.Rows.Count
                .ColumnCount = ws.UsedRange.Columns.Count

                ' Detect headers
                .HasHeaders = DetectHeaders(ws)

                ' Calculate data density
                .DataDensity = CalculateDataDensity(ws)

                ' Estimate pages needed
                .EstimatedPages = EstimatePageCount(ws)

                ' Recommend orientation
                .RecommendedOrientation = RecommendOrientation(ws)

                ' Check for wide columns
                .HasWideColumns = CheckWideColumns(ws)

                ' Determine if scaling is needed
                .RequiresScaling = DetermineScalingNeeded(ws)

                ' Calculate optimal scaling
                .OptimalScale = CalculateOptimalScale(ws)
            End If
        End With
    Next i

    AnalyzeWorkbook = tempResults

    Exit Function

ErrorHandler:
    MsgBox "Error analyzing workbook: " & Err.Description, vbExclamation
    ReDim tempResults(0)
    AnalyzeWorkbook = tempResults
End Function

'=================================================================================
' INTELLIGENT PDF GENERATION
'=================================================================================
Public Sub GeneratePDF(wb As Workbook, _
                      SelectedSheets As Collection, _
                      OutputPath As String, _
                      Optional Orientation As String = "Auto", _
                      Optional FitToWidth As Boolean = True, _
                      Optional ScalePercent As Long = 100, _
                      Optional LeftMargin As Double = 0.25, _
                      Optional RightMargin As Double = 0.25, _
                      Optional TopMargin As Double = 0.75, _
                      Optional BottomMargin As Double = 0.75, _
                      Optional IncludeHeaders As Boolean = True, _
                      Optional IncludeGridlines As Boolean = False)

    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Dim SheetName As Variant
    Dim OriginalSettings As Collection
    Set OriginalSettings = New Collection

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    ' Store original settings and apply PDF-optimized settings
    For Each SheetName In SelectedSheets
        Set ws = wb.Worksheets(SheetName)

        ' Store original settings
        Dim settings As String
        settings = ws.PageSetup.Orientation & "|" & _
                  ws.PageSetup.Zoom & "|" & _
                  ws.PageSetup.FitToPagesWide & "|" & _
                  ws.PageSetup.FitToPagesTall
        OriginalSettings.Add settings, ws.Name

        ' Apply optimal PDF settings
        With ws.PageSetup
            ' Set orientation
            If Orientation = "Auto" Then
                If ws.UsedRange.Columns.Count > ws.UsedRange.Rows.Count Then
                    .Orientation = xlLandscape
                Else
                    .Orientation = xlPortrait
                End If
            ElseIf Orientation = "Landscape" Then
                .Orientation = xlLandscape
            Else
                .Orientation = xlPortrait
            End If

            ' Set margins (in inches)
            .LeftMargin = Application.InchesToPoints(LeftMargin)
            .RightMargin = Application.InchesToPoints(RightMargin)
            .TopMargin = Application.InchesToPoints(TopMargin)
            .BottomMargin = Application.InchesToPoints(BottomMargin)
            .HeaderMargin = Application.InchesToPoints(0.3)
            .FooterMargin = Application.InchesToPoints(0.3)

            ' Set print quality and scaling
            .PrintQuality = 600
            .PaperSize = xlPaperLetter

            If FitToWidth Then
                .Zoom = False
                .FitToPagesWide = 1
                .FitToPagesTall = False
            Else
                .Zoom = ScalePercent
                .FitToPagesWide = False
                .FitToPagesTall = False
            End If

            ' Headers and footers
            If IncludeHeaders Then
                .CenterHeader = "&A"  ' Sheet name
                .RightHeader = "Page &P of &N"
                .LeftFooter = "&D &T"  ' Date and time
            End If

            ' Gridlines
            .PrintGridlines = IncludeGridlines

            ' Print titles for headers
            If DetectHeaders(ws) Then
                .PrintTitleRows = "$1:$1"
            End If

            ' Other quality settings
            .PrintErrors = xlPrintErrorsDisplayed
            .Order = xlDownThenOver
            .BlackAndWhite = False
            .Draft = False
            .PrintComments = xlPrintNoComments
        End With

        ' Auto-fit columns for better readability (within limits)
        OptimizeColumnWidths ws
    Next

    ' Export to PDF
    Dim ExportSheets() As String
    ReDim ExportSheets(1 To SelectedSheets.Count)

    Dim idx As Long
    idx = 1
    For Each SheetName In SelectedSheets
        ExportSheets(idx) = CStr(SheetName)
        idx = idx + 1
    Next

    wb.Worksheets(ExportSheets).Select
    ActiveSheet.ExportAsFixedFormat _
        Type:=xlTypePDF, _
        Filename:=OutputPath, _
        Quality:=xlQualityStandard, _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=False

    ' Restore original settings
    For Each SheetName In SelectedSheets
        Set ws = wb.Worksheets(SheetName)
        Dim parts() As String
        parts = Split(OriginalSettings(ws.Name), "|")

        With ws.PageSetup
            .Orientation = CLng(parts(0))
            If CBool(parts(1)) Then
                .Zoom = CLng(parts(1))
            End If
        End With
    Next

    Application.ScreenUpdating = True
    Application.DisplayAlerts = True

    MsgBox "PDF generated successfully!" & vbCrLf & vbCrLf & OutputPath, vbInformation, "Success"

    Exit Sub

ErrorHandler:
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    MsgBox "Error generating PDF: " & Err.Description, vbCritical, "Error"
End Sub

'=================================================================================
' HELPER FUNCTIONS - Analysis
'=================================================================================
Private Function DetectHeaders(ws As Worksheet) As Boolean
    On Error Resume Next

    Dim firstRow As Range
    Dim cell As Range
    Dim textCount As Long
    Dim boldCount As Long

    Set firstRow = ws.UsedRange.Rows(1)

    For Each cell In firstRow.Cells
        If Not IsEmpty(cell.Value) Then
            textCount = textCount + 1
            If cell.Font.Bold Then boldCount = boldCount + 1
        End If
    Next

    ' If >50% of first row is bold, or >70% is text, assume headers
    DetectHeaders = (boldCount > textCount * 0.5) Or (textCount > firstRow.Cells.Count * 0.7)
End Function

Private Function CalculateDataDensity(ws As Worksheet) As String
    On Error Resume Next

    Dim filledCells As Long
    Dim totalCells As Long
    Dim density As Double

    filledCells = Application.WorksheetFunction.CountA(ws.UsedRange)
    totalCells = ws.UsedRange.Rows.Count * ws.UsedRange.Columns.Count

    If totalCells > 0 Then
        density = filledCells / totalCells
    End If

    If density > 0.7 Then
        CalculateDataDensity = "High"
    ElseIf density > 0.3 Then
        CalculateDataDensity = "Medium"
    Else
        CalculateDataDensity = "Low"
    End If
End Function

Private Function EstimatePageCount(ws As Worksheet) As Long
    On Error Resume Next

    Dim rowsPerPage As Long
    Dim colsPerPage As Long

    ' Rough estimation: 45 rows per portrait page, 25 columns per landscape page
    rowsPerPage = 45
    colsPerPage = 25

    EstimatePageCount = Application.WorksheetFunction.Ceiling_Math( _
        ws.UsedRange.Rows.Count / rowsPerPage, 1)
End Function

Private Function RecommendOrientation(ws As Worksheet) As String
    If ws.UsedRange.Columns.Count > 10 Then
        RecommendOrientation = "Landscape"
    Else
        RecommendOrientation = "Portrait"
    End If
End Function

Private Function CheckWideColumns(ws As Worksheet) As Boolean
    On Error Resume Next

    Dim col As Range
    Dim wideCount As Long

    For Each col In ws.UsedRange.Columns
        If col.ColumnWidth > 20 Then wideCount = wideCount + 1
    Next

    CheckWideColumns = (wideCount > ws.UsedRange.Columns.Count * 0.3)
End Function

Private Function DetermineScalingNeeded(ws As Worksheet) As Boolean
    DetermineScalingNeeded = (ws.UsedRange.Columns.Count > 15) Or CheckWideColumns(ws)
End Function

Private Function CalculateOptimalScale(ws As Worksheet) As Long
    On Error Resume Next

    Dim colCount As Long
    colCount = ws.UsedRange.Columns.Count

    If colCount <= 10 Then
        CalculateOptimalScale = 100
    ElseIf colCount <= 15 Then
        CalculateOptimalScale = 85
    ElseIf colCount <= 20 Then
        CalculateOptimalScale = 75
    ElseIf colCount <= 30 Then
        CalculateOptimalScale = 65
    Else
        CalculateOptimalScale = 50
    End If
End Function

Private Sub OptimizeColumnWidths(ws As Worksheet)
    On Error Resume Next

    Dim col As Range

    For Each col In ws.UsedRange.Columns
        ' Auto-fit but cap at reasonable width
        col.AutoFit
        If col.ColumnWidth > 50 Then
            col.ColumnWidth = 50
            col.WrapText = True
        End If
    Next
End Sub

'=================================================================================
' UTILITY FUNCTIONS
'=================================================================================
Public Function BrowseForExcelFile() As String
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFilePicker)

    With fd
        .Title = "Select Excel File"
        .Filters.Clear
        .Filters.Add "Excel Files", "*.xlsx;*.xlsm;*.xls"
        .AllowMultiSelect = False

        If .Show = -1 Then
            BrowseForExcelFile = .SelectedItems(1)
        End If
    End With
End Function

Public Function BrowseSaveLocation() As String
    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogSaveAs)

    With fd
        .Title = "Save PDF As"
        .InitialFileName = "Export.pdf"

        If .Show = -1 Then
            BrowseSaveLocation = .SelectedItems(1)
            If Right(BrowseSaveLocation, 4) <> ".pdf" Then
                BrowseSaveLocation = BrowseSaveLocation & ".pdf"
            End If
        End If
    End With
End Function
