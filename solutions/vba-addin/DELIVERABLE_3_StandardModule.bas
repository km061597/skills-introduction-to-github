Attribute VB_Name = "xpdf_CoreEngineModule_m8k9n"
'===============================================================================
' DELIVERABLE 3: Complete Standard Module Code
' Purpose: All core functionality for PDF generation and analysis
' Instructions: Insert > Module, then paste this entire code
'===============================================================================

Option Explicit

' Module-level constants
Private Const XPDF_MAX_TEXT_LENGTH_K9M2 As Long = 32767
Private Const XPDF_LONG_TEXT_THRESHOLD_N7J3 As Long = 500
Private Const XPDF_DEFAULT_DPI_M8K4 As Long = 600
Private Const XPDF_MIN_COLUMN_WIDTH_K3N8 As Double = 8.43
Private Const XPDF_MAX_COLUMN_WIDTH_M9J2 As Double = 255

'===============================================================================
' PUBLIC ENTRY POINT - Launch the converter
'===============================================================================

Public Sub xpdf_LaunchConverter_k9m7()
    On Error GoTo ErrorHandler

    Dim frm_n8k3 As Object

    ' Check if form exists
    On Error Resume Next
    Set frm_n8k3 = VBA.UserForms.Add("xpdf_MainConverterForm_v7n3k")
    On Error GoTo ErrorHandler

    If frm_n8k3 Is Nothing Then
        MsgBox "UserForm 'xpdf_MainConverterForm_v7n3k' not found." & vbCrLf & vbCrLf & _
               "Please run DELIVERABLE 1 code first to create the form.", _
               vbExclamation, "Form Not Found"
        Exit Sub
    End If

    ' Show form
    frm_n8k3.Show vbModal

    Exit Sub

ErrorHandler:
    MsgBox "Error launching converter: " & Err.Description & vbCrLf & _
           "Error: " & Err.Number, vbCritical, "Launch Error"
End Sub

'===============================================================================
' SHEET ANALYSIS FUNCTION
'===============================================================================

Public Function xpdf_AnalyzeWorksheet_m9k3(ws As Worksheet) As xpdf_SheetAnalysisClass_k9n7
    On Error GoTo ErrorHandler

    Dim analysis_k8m4 As xpdf_SheetAnalysisClass_k9n7
    Set analysis_k8m4 = New xpdf_SheetAnalysisClass_k9n7

    Dim usedRng_n7j2 As Range
    Dim cell_k9m3 As Range
    Dim filledCells_m8k7 As Long
    Dim totalCells_n3j9 As Long
    Dim mergedCount_k2m8 As Long
    Dim longTextCount_m9k3 As Long
    Dim maxLength_k7n4 As Long
    Dim cellLength_n8m2 As Long
    Dim boldCount_k9j3 As Long
    Dim textCount_m2n7 As Long
    Dim firstRow_k8m4 As Range

    ' Get used range
    On Error Resume Next
    Set usedRng_n7j2 = ws.UsedRange
    On Error GoTo ErrorHandler

    If usedRng_n7j2 Is Nothing Then
        ' Empty sheet
        With analysis_k8m4
            .SheetName_k9m2 = ws.Name
            .RowCount_k8m3 = 0
            .ColumnCount_m7n2 = 0
            .UsedRange_n9k4 = "A1"
            .HasHeaders_m9k2 = False
            .DataDensity_k3j8 = 0
            .MergedCellCount_k7n3 = 0
            .LongTextCellCount_n8m4 = 0
            .MaxCellLength_k9j2 = 0
            .HasWideColumns_m3k8 = False
            .EstimatedPages_k2n9 = 1
            .RecommendedOrientation_n7k4 = "Portrait"
            .RequiresScaling_k8m9 = False
            .OptimalScale_m9n3 = 100
        End With
        Set xpdf_AnalyzeWorksheet_m9k3 = analysis_k8m4
        Exit Function
    End If

    ' Basic dimensions
    analysis_k8m4.SheetName_k9m2 = ws.Name
    analysis_k8m4.RowCount_k8m3 = usedRng_n7j2.Rows.Count
    analysis_k8m4.ColumnCount_m7n2 = usedRng_n7j2.Columns.Count
    analysis_k8m4.UsedRange_n9k4 = usedRng_n7j2.Address

    ' Analyze cells
    filledCells_m8k7 = 0
    totalCells_n3j9 = usedRng_n7j2.Rows.Count * usedRng_n7j2.Columns.Count
    mergedCount_k2m8 = 0
    longTextCount_m9k3 = 0
    maxLength_k7n4 = 0

    Application.ScreenUpdating = False

    ' Count merged cells
    On Error Resume Next
    Dim mergedArea_k9m8 As Range
    For Each mergedArea_k9m8 In ws.UsedRange.MergeArea
        If mergedArea_k9m8.MergeCells Then
            mergedCount_k2m8 = mergedCount_k2m8 + 1
        End If
    Next mergedArea_k9m8
    On Error GoTo ErrorHandler

    ' More accurate merged cell count
    Dim rng_k8n3 As Range
    On Error Resume Next
    For Each rng_k8n3 In usedRng_n7j2.Cells
        If rng_k8n3.MergeCells Then
            If rng_k8n3.Address = rng_k8n3.MergeArea.Cells(1, 1).Address Then
                mergedCount_k2m8 = mergedCount_k2m8 + 1
            End If
        End If
    Next rng_k8n3
    On Error GoTo ErrorHandler

    ' Sample cells for analysis (to avoid performance issues with huge sheets)
    Dim sampleSize_k9m7 As Long
    Dim sampleInterval_n3k8 As Long

    If totalCells_n3j9 > 10000 Then
        sampleSize_k9m7 = 5000
        sampleInterval_n3k8 = totalCells_n3j9 \ sampleSize_k9m7
    Else
        sampleSize_k9m7 = totalCells_n3j9
        sampleInterval_n3k8 = 1
    End If

    Dim counter_k9m2 As Long
    counter_k9m2 = 0

    For Each cell_k9m3 In usedRng_n7j2.Cells
        counter_k9m2 = counter_k9m2 + 1

        If counter_k9m2 Mod sampleInterval_n3k8 = 0 Or totalCells_n3j9 <= 10000 Then
            If Not IsEmpty(cell_k9m3.Value) And Len(CStr(cell_k9m3.Value)) > 0 Then
                filledCells_m8k7 = filledCells_m8k7 + 1

                cellLength_n8m2 = Len(CStr(cell_k9m3.Value))

                If cellLength_n8m2 > maxLength_k7n4 Then
                    maxLength_k7n4 = cellLength_n8m2
                End If

                If cellLength_n8m2 > XPDF_LONG_TEXT_THRESHOLD_N7J3 Then
                    longTextCount_m9k3 = longTextCount_m9k3 + 1
                End If
            End If
        End If
    Next cell_k9m3

    Application.ScreenUpdating = True

    ' Calculate data density
    If totalCells_n3j9 > 0 Then
        analysis_k8m4.DataDensity_k3j8 = filledCells_m8k7 / totalCells_n3j9
    Else
        analysis_k8m4.DataDensity_k3j8 = 0
    End If

    analysis_k8m4.MergedCellCount_k7n3 = mergedCount_k2m8
    analysis_k8m4.LongTextCellCount_n8m4 = longTextCount_m9k3
    analysis_k8m4.MaxCellLength_k9j2 = maxLength_k7n4

    ' Detect headers
    analysis_k8m4.HasHeaders_m9k2 = False

    On Error Resume Next
    Set firstRow_k8m4 = usedRng_n7j2.Rows(1)

    If Not firstRow_k8m4 Is Nothing Then
        boldCount_k9j3 = 0
        textCount_m2n7 = 0

        For Each cell_k9m3 In firstRow_k8m4.Cells
            If Not IsEmpty(cell_k9m3.Value) Then
                textCount_m2n7 = textCount_m2n7 + 1
                If cell_k9m3.Font.Bold Then
                    boldCount_k9j3 = boldCount_k9j3 + 1
                End If
            End If
        Next cell_k9m3

        If textCount_m2n7 > 0 Then
            If boldCount_k9j3 > textCount_m2n7 * 0.5 Or textCount_m2n7 > firstRow_k8m4.Cells.Count * 0.7 Then
                analysis_k8m4.HasHeaders_m9k2 = True
            End If
        End If
    End If
    On Error GoTo ErrorHandler

    ' Check for wide columns
    analysis_k8m4.HasWideColumns_m3k8 = (analysis_k8m4.ColumnCount_m7n2 > 15)

    ' Estimate pages
    Dim rowsPerPage_k9m3 As Long
    rowsPerPage_k9m3 = 45

    If longTextCount_m9k3 > analysis_k8m4.RowCount_k8m3 * 0.3 Then
        ' Lots of long text - fewer rows per page
        rowsPerPage_k9m3 = 30
    End If

    analysis_k8m4.EstimatedPages_k2n9 = Application.WorksheetFunction.Max(1, Int((analysis_k8m4.RowCount_k8m3 + rowsPerPage_k9m3 - 1) / rowsPerPage_k9m3))

    ' Recommend orientation
    If analysis_k8m4.ColumnCount_m7n2 > 12 Then
        analysis_k8m4.RecommendedOrientation_n7k4 = "Landscape"
    ElseIf analysis_k8m4.ColumnCount_m7n2 > 8 And longTextCount_m9k3 > 0 Then
        analysis_k8m4.RecommendedOrientation_n7k4 = "Landscape"
    Else
        analysis_k8m4.RecommendedOrientation_n7k4 = "Portrait"
    End If

    ' Determine scaling needs
    analysis_k8m4.RequiresScaling_k8m9 = (analysis_k8m4.ColumnCount_m7n2 > 12 Or analysis_k8m4.HasWideColumns_m3k8)

    ' Calculate optimal scale
    If analysis_k8m4.ColumnCount_m7n2 <= 8 Then
        analysis_k8m4.OptimalScale_m9n3 = 100
    ElseIf analysis_k8m4.ColumnCount_m7n2 <= 12 Then
        analysis_k8m4.OptimalScale_m9n3 = 90
    ElseIf analysis_k8m4.ColumnCount_m7n2 <= 16 Then
        analysis_k8m4.OptimalScale_m9n3 = 80
    ElseIf analysis_k8m4.ColumnCount_m7n2 <= 20 Then
        analysis_k8m4.OptimalScale_m9n3 = 70
    ElseIf analysis_k8m4.ColumnCount_m7n2 <= 25 Then
        analysis_k8m4.OptimalScale_m9n3 = 60
    Else
        analysis_k8m4.OptimalScale_m9n3 = 50
    End If

    ' Adjust for long text
    If longTextCount_m9k3 > analysis_k8m4.RowCount_k8m3 * 0.2 Then
        analysis_k8m4.OptimalScale_m9n3 = analysis_k8m4.OptimalScale_m9n3 - 10
        If analysis_k8m4.OptimalScale_m9n3 < 40 Then
            analysis_k8m4.OptimalScale_m9n3 = 40
        End If
    End If

    Set xpdf_AnalyzeWorksheet_m9k3 = analysis_k8m4
    Exit Function

ErrorHandler:
    ' Return basic analysis on error
    Set analysis_k8m4 = New xpdf_SheetAnalysisClass_k9n7
    analysis_k8m4.SheetName_k9m2 = ws.Name
    analysis_k8m4.RowCount_k8m3 = 0
    analysis_k8m4.ColumnCount_m7n2 = 0
    Set xpdf_AnalyzeWorksheet_m9k3 = analysis_k8m4
End Function

'===============================================================================
' PDF GENERATION - MAIN FUNCTION
'===============================================================================

Public Function xpdf_GeneratePDFDocument_m9k7( _
    wb As Workbook, _
    selectedSheets() As String, _
    settings As xpdf_PDFSettingsClass_k8n4, _
    Optional statusForm As Object = Nothing) As Boolean

    On Error GoTo ErrorHandler

    Dim ws As Worksheet
    Dim sheetName_k9m2 As String
    Dim i_n7j3 As Long
    Dim originalSettings_k8m4 As Collection
    Dim sheetArray_m9k3() As String
    Dim tempSheet_k7n2 As Worksheet

    xpdf_GeneratePDFDocument_m9k7 = False

    ' Validate
    If wb Is Nothing Then Exit Function
    If UBound(selectedSheets) < LBound(selectedSheets) Then Exit Function
    If settings Is Nothing Then Exit Function

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False
    Application.Calculation = xlCalculationManual

    ' Store original settings for all sheets
    Set originalSettings_k8m4 = New Collection

    For i_n7j3 = LBound(selectedSheets) To UBound(selectedSheets)
        sheetName_k9m2 = selectedSheets(i_n7j3)

        On Error Resume Next
        Set ws = wb.Worksheets(sheetName_k9m2)
        On Error GoTo ErrorHandler

        If Not ws Is Nothing Then
            ' Store original page setup
            Dim settingsStr_k9m8 As String
            settingsStr_k9m8 = xpdf_StorePageSetup_k9n4(ws)
            originalSettings_k8m4.Add settingsStr_k9m8, sheetName_k9m2

            ' Apply PDF-optimized settings
            Call xpdf_ApplyPDFSettings_m8k7(ws, settings, statusForm)
        End If
    Next i_n7j3

    ' Update status
    If Not statusForm Is Nothing Then
        On Error Resume Next
        statusForm.xpdf_lblStatus_k7m9.Caption = "Exporting to PDF..."
        DoEvents
        On Error GoTo ErrorHandler
    End If

    ' Select sheets to export
    ReDim sheetArray_m9k3(LBound(selectedSheets) To UBound(selectedSheets))

    For i_n7j3 = LBound(selectedSheets) To UBound(selectedSheets)
        sheetArray_m9k3(i_n7j3) = selectedSheets(i_n7j3)
    Next i_n7j3

    ' Export to PDF
    On Error Resume Next
    wb.Worksheets(sheetArray_m9k3).Select
    On Error GoTo ErrorHandler

    wb.ActiveSheet.ExportAsFixedFormat _
        Type:=xlTypePDF, _
        Filename:=settings.OutputPath_k9m2, _
        Quality:=IIf(settings.HighQuality_n4k9, xlQualityStandard, xlQualityMinimum), _
        IncludeDocProperties:=True, _
        IgnorePrintAreas:=False, _
        OpenAfterPublish:=False

    ' Restore original settings
    For i_n7j3 = LBound(selectedSheets) To UBound(selectedSheets)
        sheetName_k9m2 = selectedSheets(i_n7j3)

        On Error Resume Next
        Set ws = wb.Worksheets(sheetName_k9m2)

        If Not ws Is Nothing Then
            Dim storedSettings_k9m7 As String
            storedSettings_k9m7 = originalSettings_k8m4(sheetName_k9m2)
            Call xpdf_RestorePageSetup_n8k3(ws, storedSettings_k9m7)
        End If
        On Error GoTo ErrorHandler
    Next i_n7j3

    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.Calculation = xlCalculationAutomatic

    xpdf_GeneratePDFDocument_m9k7 = True
    Exit Function

ErrorHandler:
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.Calculation = xlCalculationAutomatic

    MsgBox "Error generating PDF: " & Err.Description, vbCritical, "PDF Error"
    xpdf_GeneratePDFDocument_m9k7 = False
End Function

'===============================================================================
' APPLY PDF SETTINGS TO WORKSHEET
'===============================================================================

Private Sub xpdf_ApplyPDFSettings_m8k7(ws As Worksheet, settings As xpdf_PDFSettingsClass_k8n4, Optional statusForm As Object = Nothing)
    On Error Resume Next

    Dim orientation_k9m2 As XlPageOrientation
    Dim usedRng_n7j3 As Range

    Set usedRng_n7j3 = ws.UsedRange

    ' Determine orientation
    If UCase(settings.Orientation_n7j3) = "PORTRAIT" Then
        orientation_k9m2 = xlPortrait
    ElseIf UCase(settings.Orientation_n7j3) = "LANDSCAPE" Then
        orientation_k9m2 = xlLandscape
    Else
        ' Auto-detect
        If usedRng_n7j3.Columns.Count > 10 Then
            orientation_k9m2 = xlLandscape
        Else
            orientation_k9m2 = xlPortrait
        End If
    End If

    ' Apply page setup
    With ws.PageSetup
        .Orientation = orientation_k9m2
        .PaperSize = settings.PaperSize_m8k4

        ' Margins
        .LeftMargin = Application.InchesToPoints(settings.MarginLeft_k2n8)
        .RightMargin = Application.InchesToPoints(settings.MarginRight_n9k3)
        .TopMargin = Application.InchesToPoints(settings.MarginTop_k8m9)
        .BottomMargin = Application.InchesToPoints(settings.MarginBottom_m3k7)
        .HeaderMargin = Application.InchesToPoints(0.3)
        .FooterMargin = Application.InchesToPoints(0.3)

        ' Print quality
        If settings.HighQuality_n4k9 Then
            .PrintQuality = XPDF_DEFAULT_DPI_M8K4
        Else
            .PrintQuality = 300
        End If

        ' Scaling
        If settings.FitToWidth_k3n9 Then
            .Zoom = False
            .FitToPagesWide = 1
            .FitToPagesTall = False
        Else
            .Zoom = settings.ScalePercent_m7n2
            .FitToPagesWide = False
            .FitToPagesTall = False
        End If

        ' Headers and footers
        If settings.IncludeHeaders_n7k2 Then
            .CenterHeader = "&A"
            .RightHeader = "Page &P of &N"
            .LeftFooter = "&D &T"
        Else
            .CenterHeader = ""
            .RightHeader = ""
            .LeftFooter = ""
        End If

        ' Gridlines
        .PrintGridlines = settings.PrintGridlines_k9m8

        ' Other settings
        .PrintErrors = xlPrintErrorsDisplayed
        .Order = xlDownThenOver
        .BlackAndWhite = False
        .Draft = False
        .PrintComments = xlPrintNoComments
        .CenterHorizontally = False
        .CenterVertically = False

        ' Print titles (repeating headers)
        If usedRng_n7j3.Rows.Count > 1 Then
            .PrintTitleRows = "$1:$1"
        End If
    End With

    ' Handle long text
    If settings.WrapLongText_m2n7 Then
        Call xpdf_OptimizeTextWrapping_k9n8(ws)
    End If

    ' Handle merged cells
    If settings.HandleMergedCells_k8n3 Then
        Call xpdf_OptimizeMergedCells_m7k9(ws)
    End If

    ' Optimize column widths
    Call xpdf_OptimizeColumnWidths_k8n4(ws, settings.WrapLongText_m2n7)
End Sub

'===============================================================================
' TEXT WRAPPING OPTIMIZATION
'===============================================================================

Private Sub xpdf_OptimizeTextWrapping_k9n8(ws As Worksheet)
    On Error Resume Next

    Dim cell_k9m2 As Range
    Dim usedRng_n7j3 As Range

    Set usedRng_n7j3 = ws.UsedRange

    Application.ScreenUpdating = False

    ' Sample cells to avoid performance issues
    Dim sampleInterval_k8m4 As Long
    Dim counter_m9k3 As Long

    If usedRng_n7j3.Cells.Count > 10000 Then
        sampleInterval_k8m4 = 10
    Else
        sampleInterval_k8m4 = 1
    End If

    counter_m9k3 = 0

    For Each cell_k9m2 In usedRng_n7j3.Cells
        counter_m9k3 = counter_m9k3 + 1

        If counter_m9k3 Mod sampleInterval_k8m4 = 0 Or usedRng_n7j3.Cells.Count <= 10000 Then
            If Not IsEmpty(cell_k9m2.Value) Then
                If Len(CStr(cell_k9m2.Value)) > XPDF_LONG_TEXT_THRESHOLD_N7J3 Then
                    cell_k9m2.WrapText = True

                    ' Auto-fit row height
                    cell_k9m2.EntireRow.AutoFit

                    ' Limit row height to reasonable maximum
                    If cell_k9m2.EntireRow.RowHeight > 409.5 Then
                        cell_k9m2.EntireRow.RowHeight = 409.5
                    End If
                End If
            End If
        End If
    Next cell_k9m2

    Application.ScreenUpdating = True
End Sub

'===============================================================================
' MERGED CELLS OPTIMIZATION
'===============================================================================

Private Sub xpdf_OptimizeMergedCells_m7k9(ws As Worksheet)
    On Error Resume Next

    Dim cell_k9m2 As Range
    Dim usedRng_n7j3 As Range

    Set usedRng_n7j3 = ws.UsedRange

    Application.ScreenUpdating = False

    For Each cell_k9m2 In usedRng_n7j3.Cells
        If cell_k9m2.MergeCells Then
            ' Ensure text wrapping for merged cells
            cell_k9m2.WrapText = True

            ' Auto-fit the merged area
            cell_k9m2.MergeArea.Rows.AutoFit
        End If
    Next cell_k9m2

    Application.ScreenUpdating = True
End Sub

'===============================================================================
' COLUMN WIDTH OPTIMIZATION
'===============================================================================

Private Sub xpdf_OptimizeColumnWidths_k8n4(ws As Worksheet, wrapText_k9m2 As Boolean)
    On Error Resume Next

    Dim col_n7j3 As Range
    Dim usedRng_m8k4 As Range

    Set usedRng_m8k4 = ws.UsedRange

    Application.ScreenUpdating = False

    For Each col_n7j3 In usedRng_m8k4.Columns
        ' Auto-fit column
        col_n7j3.AutoFit

        ' Cap maximum width
        If col_n7j3.ColumnWidth > 75 Then
            col_n7j3.ColumnWidth = 75

            If wrapText_k9m2 Then
                col_n7j3.WrapText = True
            End If
        End If

        ' Ensure minimum width
        If col_n7j3.ColumnWidth < XPDF_MIN_COLUMN_WIDTH_K3N8 Then
            col_n7j3.ColumnWidth = XPDF_MIN_COLUMN_WIDTH_K3N8
        End If
    Next col_n7j3

    Application.ScreenUpdating = True
End Sub

'===============================================================================
' PAGE SETUP STORAGE AND RESTORATION
'===============================================================================

Private Function xpdf_StorePageSetup_k9n4(ws As Worksheet) As String
    On Error Resume Next

    Dim settings_k9m2 As String

    With ws.PageSetup
        settings_k9m2 = .Orientation & "|" & _
                       .PaperSize & "|" & _
                       .Zoom & "|" & _
                       .FitToPagesWide & "|" & _
                       .FitToPagesTall & "|" & _
                       .LeftMargin & "|" & _
                       .RightMargin & "|" & _
                       .TopMargin & "|" & _
                       .BottomMargin & "|" & _
                       .PrintGridlines & "|" & _
                       .CenterHeader & "|" & _
                       .RightHeader & "|" & _
                       .LeftFooter
    End With

    xpdf_StorePageSetup_k9n4 = settings_k9m2
End Function

Private Sub xpdf_RestorePageSetup_n8k3(ws As Worksheet, storedSettings_k9m2 As String)
    On Error Resume Next

    Dim parts_n7j3() As String
    parts_n7j3 = Split(storedSettings_k9m2, "|")

    If UBound(parts_n7j3) < 12 Then Exit Sub

    With ws.PageSetup
        .Orientation = CLng(parts_n7j3(0))
        .PaperSize = CLng(parts_n7j3(1))

        If CBool(parts_n7j3(2)) Then
            .Zoom = CLng(parts_n7j3(2))
        Else
            .Zoom = False
        End If

        If IsNumeric(parts_n7j3(3)) And parts_n7j3(3) <> "False" Then
            .FitToPagesWide = CLng(parts_n7j3(3))
        End If

        If IsNumeric(parts_n7j3(4)) And parts_n7j3(4) <> "False" Then
            .FitToPagesTall = CLng(parts_n7j3(4))
        End If

        .LeftMargin = CDbl(parts_n7j3(5))
        .RightMargin = CDbl(parts_n7j3(6))
        .TopMargin = CDbl(parts_n7j3(7))
        .BottomMargin = CDbl(parts_n7j3(8))
        .PrintGridlines = CBool(parts_n7j3(9))
        .CenterHeader = parts_n7j3(10)
        .RightHeader = parts_n7j3(11)
        .LeftFooter = parts_n7j3(12)
    End With
End Sub

'===============================================================================
' UTILITY FUNCTIONS
'===============================================================================

Public Function xpdf_IsValidExcelFile_k9m8(filePath_n7j3 As String) As Boolean
    On Error Resume Next

    Dim ext_k8m4 As String

    xpdf_IsValidExcelFile_k9m8 = False

    If Len(filePath_n7j3) = 0 Then Exit Function
    If Dir(filePath_n7j3) = "" Then Exit Function

    ext_k8m4 = LCase(Right(filePath_n7j3, 4))

    If ext_k8m4 = ".xls" Or ext_k8m4 = "xlsx" Or ext_k8m4 = "xlsm" Or ext_k8m4 = "xlsb" Then
        xpdf_IsValidExcelFile_k9m8 = True
    ElseIf LCase(Right(filePath_n7j3, 5)) = ".xlsx" Or LCase(Right(filePath_n7j3, 5)) = ".xlsm" Or LCase(Right(filePath_n7j3, 5)) = ".xlsb" Then
        xpdf_IsValidExcelFile_k9m8 = True
    End If
End Function

Public Function xpdf_GetFileExtension_m9k7(filePath_n7j3 As String) As String
    On Error Resume Next

    Dim pos_k9m2 As Long

    pos_k9m2 = InStrRev(filePath_n7j3, ".")

    If pos_k9m2 > 0 Then
        xpdf_GetFileExtension_m9k7 = LCase(Mid(filePath_n7j3, pos_k9m2))
    Else
        xpdf_GetFileExtension_m9k7 = ""
    End If
End Function

Public Function xpdf_SafeConvertToString_k8n9(val_m9k2 As Variant) As String
    On Error Resume Next

    If IsNull(val_m9k2) Then
        xpdf_SafeConvertToString_k8n9 = ""
    ElseIf IsEmpty(val_m9k2) Then
        xpdf_SafeConvertToString_k8n9 = ""
    ElseIf IsError(val_m9k2) Then
        xpdf_SafeConvertToString_k8n9 = ""
    ElseIf IsObject(val_m9k2) Then
        xpdf_SafeConvertToString_k8n9 = ""
    Else
        xpdf_SafeConvertToString_k8n9 = CStr(val_m9k2)

        If Len(xpdf_SafeConvertToString_k8n9) > XPDF_MAX_TEXT_LENGTH_K9M2 Then
            xpdf_SafeConvertToString_k8n9 = Left(xpdf_SafeConvertToString_k8n9, XPDF_MAX_TEXT_LENGTH_K9M2)
        End If
    End If
End Function

Public Function xpdf_TruncateText_n7k8(text_k9m2 As String, maxLen_m8k4 As Long) As String
    On Error Resume Next

    If Len(text_k9m2) <= maxLen_m8k4 Then
        xpdf_TruncateText_n7k8 = text_k9m2
    Else
        xpdf_TruncateText_n7k8 = Left(text_k9m2, maxLen_m8k4 - 3) & "..."
    End If
End Function
