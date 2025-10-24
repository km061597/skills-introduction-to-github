Option Explicit
'===============================================================================
' DELIVERABLE 2: Complete UserForm Code
' Purpose: All event handlers and initialization for xpdf_MainConverterForm_v7n3k
' Instructions: Paste this entire code into the UserForm's code window
'===============================================================================

' Module-level variables
Private mvarCurrentWorkbook_k9m2 As Workbook
Private mvarSelectedFilePath_n7j3 As String
Private mvarSheetAnalysisCollection_m8k4 As Collection
Private mvarIsAnalyzing_k2n9 As Boolean
Private mvarOriginalScaleEnabled_j7m3 As Boolean

'===============================================================================
' FORM INITIALIZATION AND TERMINATION
'===============================================================================

Private Sub UserForm_Initialize()
    On Error Resume Next

    ' Initialize collections
    Set mvarSheetAnalysisCollection_m8k4 = New Collection

    ' Set initial states
    mvarIsAnalyzing_k2n9 = False
    mvarSelectedFilePath_n7j3 = ""
    Set mvarCurrentWorkbook_k9m2 = Nothing

    ' Configure initial control states
    Call xpdf_InitializeControlStates_k8m3

    ' Try to use active workbook if available
    If Not Application.ActiveWorkbook Is Nothing Then
        If Application.ActiveWorkbook.Name <> ThisWorkbook.Name Then
            Set mvarCurrentWorkbook_k9m2 = Application.ActiveWorkbook
            xpdf_txtFilePath_k3n7.Text = "Active: " & mvarCurrentWorkbook_k9m2.FullName
            mvarSelectedFilePath_n7j3 = mvarCurrentWorkbook_k9m2.FullName
            Call xpdf_PopulateSheetList_m9k2
        End If
    End If

    ' Update status
    xpdf_lblStatus_k7m9.Caption = "Ready - Select file and sheets to convert"
End Sub

Private Sub UserForm_Terminate()
    On Error Resume Next

    ' Cleanup
    Set mvarSheetAnalysisCollection_m8k4 = Nothing
    Set mvarCurrentWorkbook_k9m2 = Nothing
End Sub

Private Sub UserForm_QueryClose(Cancel As Integer, CloseMode As Integer)
    ' Allow form to close
    Cancel = 0
End Sub

'===============================================================================
' CONTROL INITIALIZATION
'===============================================================================

Private Sub xpdf_InitializeControlStates_k8m3()
    On Error Resume Next

    ' Initialize combo boxes if not already done
    If xpdf_cboOrientation_k9n2.ListCount = 0 Then
        xpdf_cboOrientation_k9n2.AddItem "Auto (Smart)"
        xpdf_cboOrientation_k9n2.AddItem "Portrait"
        xpdf_cboOrientation_k9n2.AddItem "Landscape"
        xpdf_cboOrientation_k9n2.ListIndex = 0
    End If

    If xpdf_cboPaperSize_n8j3.ListCount = 0 Then
        xpdf_cboPaperSize_n8j3.AddItem "Letter"
        xpdf_cboPaperSize_n8j3.AddItem "Legal"
        xpdf_cboPaperSize_n8j3.AddItem "A4"
        xpdf_cboPaperSize_n8j3.AddItem "A3"
        xpdf_cboPaperSize_n8j3.AddItem "Tabloid"
        xpdf_cboPaperSize_n8j3.ListIndex = 0
    End If

    ' Set default values
    xpdf_txtScale_n3k7.Text = "100"
    xpdf_txtScale_n3k7.Enabled = False
    xpdf_spinScale_k8j4.Enabled = False

    mvarOriginalScaleEnabled_j7m3 = False

    ' Set default checkboxes
    xpdf_chkFitToWidth_k3m9.Value = True
    xpdf_chkIncludeHeaders_m4k9.Value = True
    xpdf_chkPrintGridlines_n7k3.Value = False
    xpdf_chkWrapLongText_k8m4.Value = True
    xpdf_chkHandleMerged_m9j2.Value = True
    xpdf_chkHighQuality_k3n8.Value = True

    ' Set default margins
    xpdf_txtMarginLeft_m9k3.Text = "0.25"
    xpdf_txtMarginRight_k8m2.Text = "0.25"
    xpdf_txtMarginTop_m3n7.Text = "0.75"
    xpdf_txtMarginBottom_n2k8.Text = "0.75"
End Sub

'===============================================================================
' FILE SELECTION EVENTS
'===============================================================================

Private Sub xpdf_btnBrowseFile_m8k1_Click()
    On Error GoTo ErrorHandler

    Dim selectedFile_k9n2 As Variant
    Dim wb_m7j3 As Workbook

    ' Show file dialog
    selectedFile_k9n2 = Application.GetOpenFilename( _
        FileFilter:="Excel Files (*.xlsx;*.xlsm;*.xlsb;*.xls),*.xlsx;*.xlsm;*.xlsb;*.xls", _
        Title:="Select Excel File to Convert", _
        MultiSelect:=False)

    If selectedFile_k9n2 = False Then Exit Sub

    ' Update status
    xpdf_lblStatus_k7m9.Caption = "Loading workbook..."
    DoEvents

    ' Close previous workbook if it's not the active one
    If Not mvarCurrentWorkbook_k9m2 Is Nothing Then
        If mvarCurrentWorkbook_k9m2.Name <> Application.ActiveWorkbook.Name Then
            On Error Resume Next
            mvarCurrentWorkbook_k9m2.Close SaveChanges:=False
            On Error GoTo ErrorHandler
        End If
    End If

    ' Open the selected file
    Set wb_m7j3 = Workbooks.Open(Filename:=selectedFile_k9n2, ReadOnly:=True, UpdateLinks:=False)

    If wb_m7j3 Is Nothing Then
        MsgBox "Failed to open workbook.", vbExclamation, "Error"
        Exit Sub
    End If

    Set mvarCurrentWorkbook_k9m2 = wb_m7j3
    mvarSelectedFilePath_n7j3 = CStr(selectedFile_k9n2)
    xpdf_txtFilePath_k3n7.Text = mvarSelectedFilePath_n7j3

    ' Populate sheets
    Call xpdf_PopulateSheetList_m9k2

    xpdf_lblStatus_k7m9.Caption = "File loaded: " & wb_m7j3.Name

    Exit Sub

ErrorHandler:
    MsgBox "Error opening file: " & Err.Description, vbCritical, "Error"
    xpdf_lblStatus_k7m9.Caption = "Error loading file"
End Sub

Private Sub xpdf_btnUseActive_n2j9_Click()
    On Error GoTo ErrorHandler

    If Application.ActiveWorkbook Is Nothing Then
        MsgBox "No active workbook found.", vbExclamation, "No Workbook"
        Exit Sub
    End If

    If Application.ActiveWorkbook.Name = ThisWorkbook.Name Then
        MsgBox "Cannot use this workbook (contains the converter code).", vbExclamation, "Invalid Selection"
        Exit Sub
    End If

    Set mvarCurrentWorkbook_k9m2 = Application.ActiveWorkbook
    mvarSelectedFilePath_n7j3 = mvarCurrentWorkbook_k9m2.FullName
    xpdf_txtFilePath_k3n7.Text = "Active: " & mvarCurrentWorkbook_k9m2.Name

    Call xpdf_PopulateSheetList_m9k2

    xpdf_lblStatus_k7m9.Caption = "Using active workbook: " & mvarCurrentWorkbook_k9m2.Name

    Exit Sub

ErrorHandler:
    MsgBox "Error using active workbook: " & Err.Description, vbCritical, "Error"
End Sub

'===============================================================================
' SHEET LIST MANAGEMENT
'===============================================================================

Private Sub xpdf_PopulateSheetList_m9k2()
    On Error Resume Next

    Dim ws_k8n3 As Worksheet
    Dim i_m2j7 As Long

    ' Clear existing list
    xpdf_lstSheets_k2n8.Clear

    If mvarCurrentWorkbook_k9m2 Is Nothing Then Exit Sub

    ' Add all sheets
    For Each ws_k8n3 In mvarCurrentWorkbook_k9m2.Worksheets
        xpdf_lstSheets_k2n8.AddItem ws_k8n3.Name
    Next ws_k8n3

    ' Select all by default
    For i_m2j7 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        xpdf_lstSheets_k2n8.Selected(i_m2j7) = True
    Next i_m2j7

    xpdf_lblStatus_k7m9.Caption = "Found " & xpdf_lstSheets_k2n8.ListCount & " sheets"
End Sub

Private Sub xpdf_btnSelectAllSheets_k8m3_Click()
    On Error Resume Next
    Dim i_k9m2 As Long
    For i_k9m2 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        xpdf_lstSheets_k2n8.Selected(i_k9m2) = True
    Next i_k9m2
End Sub

Private Sub xpdf_btnDeselectAllSheets_m3j7_Click()
    On Error Resume Next
    Dim i_k9m2 As Long
    For i_k9m2 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        xpdf_lstSheets_k2n8.Selected(i_k9m2) = False
    Next i_k9m2
End Sub

Private Sub xpdf_btnInvertSelection_n9k2_Click()
    On Error Resume Next
    Dim i_k9m2 As Long
    For i_k9m2 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        xpdf_lstSheets_k2n8.Selected(i_k9m2) = Not xpdf_lstSheets_k2n8.Selected(i_k9m2)
    Next i_k9m2
End Sub

Private Sub xpdf_lstSheets_k2n8_Click()
    On Error Resume Next
    Call xpdf_DisplaySheetAnalysis_n7k3
End Sub

'===============================================================================
' ANALYSIS FUNCTIONALITY
'===============================================================================

Private Sub xpdf_btnAnalyzeSheets_p7k4_Click()
    On Error GoTo ErrorHandler

    If mvarCurrentWorkbook_k9m2 Is Nothing Then
        MsgBox "Please select a workbook first.", vbExclamation, "No Workbook"
        Exit Sub
    End If

    If mvarIsAnalyzing_k2n9 Then
        MsgBox "Analysis already in progress.", vbInformation, "Please Wait"
        Exit Sub
    End If

    mvarIsAnalyzing_k2n9 = True
    xpdf_lblStatus_k7m9.Caption = "Analyzing workbook..."
    xpdf_lblProgressBar_n9k7.Visible = True
    DoEvents

    ' Clear previous analysis
    Set mvarSheetAnalysisCollection_m8k4 = New Collection

    ' Analyze all sheets
    Dim ws_k8n3 As Worksheet
    Dim analysis_m7j2 As xpdf_SheetAnalysisClass_k9n7
    Dim idx_k3m8 As Long
    Dim totalSheets_n2j9 As Long

    totalSheets_n2j9 = mvarCurrentWorkbook_k9m2.Worksheets.Count
    idx_k3m8 = 0

    For Each ws_k8n3 In mvarCurrentWorkbook_k9m2.Worksheets
        idx_k3m8 = idx_k3m8 + 1
        xpdf_lblStatus_k7m9.Caption = "Analyzing sheet " & idx_k3m8 & " of " & totalSheets_n2j9 & ": " & ws_k8n3.Name
        DoEvents

        Set analysis_m7j2 = xpdf_AnalyzeWorksheet_m9k3(ws_k8n3)
        mvarSheetAnalysisCollection_m8k4.Add analysis_m7j2, ws_k8n3.Name
    Next ws_k8n3

    xpdf_lblProgressBar_n9k7.Visible = False
    xpdf_lblStatus_k7m9.Caption = "Analysis complete - " & totalSheets_n2j9 & " sheets analyzed"

    ' Display analysis for first selected sheet
    Call xpdf_DisplaySheetAnalysis_n7k3

    mvarIsAnalyzing_k2n9 = False

    Exit Sub

ErrorHandler:
    mvarIsAnalyzing_k2n9 = False
    xpdf_lblProgressBar_n9k7.Visible = False
    MsgBox "Error during analysis: " & Err.Description, vbCritical, "Analysis Error"
    xpdf_lblStatus_k7m9.Caption = "Analysis failed"
End Sub

Private Sub xpdf_DisplaySheetAnalysis_n7k3()
    On Error Resume Next

    Dim selectedIndex_k9m2 As Long
    Dim i_n7j3 As Long
    Dim sheetName_k8m4 As String
    Dim analysis_m7j2 As xpdf_SheetAnalysisClass_k9n7
    Dim displayText_k3n9 As String

    ' Find first selected sheet
    selectedIndex_k9m2 = -1
    For i_n7j3 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        If xpdf_lstSheets_k2n8.Selected(i_n7j3) Then
            selectedIndex_k9m2 = i_n7j3
            Exit For
        End If
    Next i_n7j3

    If selectedIndex_k9m2 = -1 Then Exit Sub

    sheetName_k8m4 = xpdf_lstSheets_k2n8.List(selectedIndex_k9m2)

    ' Check if analysis exists
    On Error Resume Next
    Set analysis_m7j2 = mvarSheetAnalysisCollection_m8k4(sheetName_k8m4)
    On Error GoTo 0

    If analysis_m7j2 Is Nothing Then
        xpdf_txtAnalysisDisplay_k7m2.Text = "Sheet: " & sheetName_k8m4 & vbCrLf & vbCrLf & _
                                            "Click 'Analyze' to scan this sheet..."
        Exit Sub
    End If

    ' Build analysis display
    displayText_k3n9 = String(70, "=") & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "ANALYSIS: " & sheetName_k8m4 & vbCrLf
    displayText_k3n9 = displayText_k3n9 & String(70, "=") & vbCrLf & vbCrLf

    displayText_k3n9 = displayText_k3n9 & "DIMENSIONS:" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Rows: " & Format(analysis_m7j2.RowCount_k8m3, "#,##0") & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Columns: " & analysis_m7j2.ColumnCount_m7n2 & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Used Range: " & analysis_m7j2.UsedRange_n9k4 & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Data Density: " & Format(analysis_m7j2.DataDensity_k3j8, "0.0%") & vbCrLf & vbCrLf

    displayText_k3n9 = displayText_k3n9 & "DATA CHARACTERISTICS:" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Has Headers: " & IIf(analysis_m7j2.HasHeaders_m9k2, "Yes", "No") & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Merged Cells: " & analysis_m7j2.MergedCellCount_k7n3 & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Long Text Cells: " & analysis_m7j2.LongTextCellCount_n8m4 & " (>500 chars)" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Max Cell Length: " & Format(analysis_m7j2.MaxCellLength_k9j2, "#,##0") & " characters" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Wide Columns: " & IIf(analysis_m7j2.HasWideColumns_m3k8, "Yes", "No") & vbCrLf & vbCrLf

    displayText_k3n9 = displayText_k3n9 & "PDF ESTIMATES:" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Estimated Pages: " & analysis_m7j2.EstimatedPages_k2n9 & vbCrLf & vbCrLf

    displayText_k3n9 = displayText_k3n9 & "RECOMMENDATIONS:" & vbCrLf
    displayText_k3n9 = displayText_k3n9 & "  Orientation: " & analysis_m7j2.RecommendedOrientation_n7k4 & vbCrLf

    If analysis_m7j2.RequiresScaling_k8m9 Then
        displayText_k3n9 = displayText_k3n9 & "  Scaling: Required" & vbCrLf
        displayText_k3n9 = displayText_k3n9 & "  Optimal Scale: " & analysis_m7j2.OptimalScale_m9n3 & "%" & vbCrLf

        ' Auto-apply recommendations
        xpdf_chkFitToWidth_k3m9.Value = False
        xpdf_txtScale_n3k7.Text = CStr(analysis_m7j2.OptimalScale_m9n3)
        xpdf_spinScale_k8j4.Value = analysis_m7j2.OptimalScale_m9n3
    Else
        displayText_k3n9 = displayText_k3n9 & "  Scaling: Not required (Fit to width works)" & vbCrLf
        xpdf_chkFitToWidth_k3m9.Value = True
    End If

    If analysis_m7j2.LongTextCellCount_n8m4 > 0 Then
        displayText_k3n9 = displayText_k3n9 & vbCrLf & "  Note: Contains very long text - wrapping enabled" & vbCrLf
    End If

    If analysis_m7j2.MergedCellCount_k7n3 > 0 Then
        displayText_k3n9 = displayText_k3n9 & "  Note: Contains merged cells - optimization enabled" & vbCrLf
    End If

    ' Auto-set orientation
    Select Case UCase(analysis_m7j2.RecommendedOrientation_n7k4)
        Case "PORTRAIT"
            xpdf_cboOrientation_k9n2.ListIndex = 1
        Case "LANDSCAPE"
            xpdf_cboOrientation_k9n2.ListIndex = 2
        Case Else
            xpdf_cboOrientation_k9n2.ListIndex = 0
    End Select

    xpdf_txtAnalysisDisplay_k7m2.Text = displayText_k3n9
End Sub

'===============================================================================
' SETTINGS CONTROLS EVENTS
'===============================================================================

Private Sub xpdf_chkFitToWidth_k3m9_Click()
    On Error Resume Next

    If xpdf_chkFitToWidth_k3m9.Value Then
        xpdf_txtScale_n3k7.Enabled = False
        xpdf_spinScale_k8j4.Enabled = False
        xpdf_txtScale_n3k7.BackColor = &HE0E0E0
    Else
        xpdf_txtScale_n3k7.Enabled = True
        xpdf_spinScale_k8j4.Enabled = True
        xpdf_txtScale_n3k7.BackColor = &HFFFFFF
    End If
End Sub

Private Sub xpdf_spinScale_k8j4_Change()
    On Error Resume Next
    xpdf_txtScale_n3k7.Text = CStr(xpdf_spinScale_k8j4.Value)
End Sub

Private Sub xpdf_txtScale_n3k7_Change()
    On Error Resume Next

    Dim scaleVal_k9m2 As Long

    If IsNumeric(xpdf_txtScale_n3k7.Text) Then
        scaleVal_k9m2 = CLng(xpdf_txtScale_n3k7.Text)

        If scaleVal_k9m2 < 10 Then scaleVal_k9m2 = 10
        If scaleVal_k9m2 > 200 Then scaleVal_k9m2 = 200

        xpdf_spinScale_k8j4.Value = scaleVal_k9m2
    End If
End Sub

Private Sub xpdf_cboOrientation_k9n2_Change()
    On Error Resume Next
    ' Orientation changed - no additional action needed
End Sub

Private Sub xpdf_cboPaperSize_n8j3_Change()
    On Error Resume Next
    ' Paper size changed - no additional action needed
End Sub

'===============================================================================
' MARGIN VALIDATION
'===============================================================================

Private Sub xpdf_txtMarginLeft_m9k3_Exit(ByVal Cancel As MSForms.ReturnBoolean)
    Call xpdf_ValidateMarginValue_k9m3(xpdf_txtMarginLeft_m9k3, Cancel)
End Sub

Private Sub xpdf_txtMarginRight_k8m2_Exit(ByVal Cancel As MSForms.ReturnBoolean)
    Call xpdf_ValidateMarginValue_k9m3(xpdf_txtMarginRight_k8m2, Cancel)
End Sub

Private Sub xpdf_txtMarginTop_m3n7_Exit(ByVal Cancel As MSForms.ReturnBoolean)
    Call xpdf_ValidateMarginValue_k9m3(xpdf_txtMarginTop_m3n7, Cancel)
End Sub

Private Sub xpdf_txtMarginBottom_n2k8_Exit(ByVal Cancel As MSForms.ReturnBoolean)
    Call xpdf_ValidateMarginValue_k9m3(xpdf_txtMarginBottom_n2k8, Cancel)
End Sub

Private Sub xpdf_ValidateMarginValue_k9m3(ctrl As MSForms.TextBox, Cancel As MSForms.ReturnBoolean)
    On Error Resume Next

    Dim val_k9m2 As Double

    If Not IsNumeric(ctrl.Text) Then
        MsgBox "Please enter a valid numeric value for margin.", vbExclamation, "Invalid Value"
        Cancel = True
        Exit Sub
    End If

    val_k9m2 = CDbl(ctrl.Text)

    If val_k9m2 < 0 Or val_k9m2 > 3 Then
        MsgBox "Margin must be between 0 and 3 inches.", vbExclamation, "Invalid Range"
        Cancel = True
        Exit Sub
    End If

    ctrl.Text = Format(val_k9m2, "0.00")
End Sub

'===============================================================================
' PDF GENERATION
'===============================================================================

Private Sub xpdf_btnGeneratePDF_m8k3_Click()
    On Error GoTo ErrorHandler

    ' Validation
    If mvarCurrentWorkbook_k9m2 Is Nothing Then
        MsgBox "Please select a workbook first.", vbExclamation, "No Workbook"
        Exit Sub
    End If

    ' Check for selected sheets
    Dim selectedCount_k9m2 As Long
    Dim i_n7j3 As Long
    selectedCount_k9m2 = 0

    For i_n7j3 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        If xpdf_lstSheets_k2n8.Selected(i_n7j3) Then
            selectedCount_k9m2 = selectedCount_k9m2 + 1
        End If
    Next i_n7j3

    If selectedCount_k9m2 = 0 Then
        MsgBox "Please select at least one sheet to convert.", vbExclamation, "No Sheets Selected"
        Exit Sub
    End If

    ' Get save location
    Dim savePath_k8m4 As Variant
    savePath_k8m4 = Application.GetSaveAsFilename( _
        InitialFileName:=Replace(mvarCurrentWorkbook_k9m2.Name, ".xls", "") & ".pdf", _
        FileFilter:="PDF Files (*.pdf),*.pdf", _
        Title:="Save PDF As")

    If savePath_k8m4 = False Then Exit Sub

    ' Ensure .pdf extension
    If LCase(Right(savePath_k8m4, 4)) <> ".pdf" Then
        savePath_k8m4 = savePath_k8m4 & ".pdf"
    End If

    ' Show progress
    xpdf_lblStatus_k7m9.Caption = "Generating PDF..."
    xpdf_lblProgressBar_n9k7.Visible = True
    xpdf_btnGeneratePDF_m8k3.Enabled = False
    DoEvents

    ' Build settings collection
    Dim settings_m9k7 As xpdf_PDFSettingsClass_k8n4
    Set settings_m9k7 = New xpdf_PDFSettingsClass_k8n4

    ' Populate settings
    With settings_m9k7
        .OutputPath_k9m2 = CStr(savePath_k8m4)

        ' Orientation
        Select Case xpdf_cboOrientation_k9n2.ListIndex
            Case 0: .Orientation_n7j3 = "Auto"
            Case 1: .Orientation_n7j3 = "Portrait"
            Case 2: .Orientation_n7j3 = "Landscape"
        End Select

        ' Paper size
        Select Case xpdf_cboPaperSize_n8j3.ListIndex
            Case 0: .PaperSize_m8k4 = xlPaperLetter
            Case 1: .PaperSize_m8k4 = xlPaperLegal
            Case 2: .PaperSize_m8k4 = xlPaperA4
            Case 3: .PaperSize_m8k4 = xlPaperA3
            Case 4: .PaperSize_m8k4 = xlPaperTabloid
            Case Else: .PaperSize_m8k4 = xlPaperLetter
        End Select

        ' Scaling
        .FitToWidth_k3n9 = xpdf_chkFitToWidth_k3m9.Value

        If IsNumeric(xpdf_txtScale_n3k7.Text) Then
            .ScalePercent_m7n2 = CLng(xpdf_txtScale_n3k7.Text)
        Else
            .ScalePercent_m7n2 = 100
        End If

        ' Margins
        .MarginLeft_k2n8 = CDbl(xpdf_txtMarginLeft_m9k3.Text)
        .MarginRight_n9k3 = CDbl(xpdf_txtMarginRight_k8m2.Text)
        .MarginTop_k8m9 = CDbl(xpdf_txtMarginTop_m3n7.Text)
        .MarginBottom_m3k7 = CDbl(xpdf_txtMarginBottom_n2k8.Text)

        ' Options
        .IncludeHeaders_n7k2 = xpdf_chkIncludeHeaders_m4k9.Value
        .PrintGridlines_k9m8 = xpdf_chkPrintGridlines_n7k3.Value
        .WrapLongText_m2n7 = xpdf_chkWrapLongText_k8m4.Value
        .HandleMergedCells_k8n3 = xpdf_chkHandleMerged_m9j2.Value
        .HighQuality_n4k9 = xpdf_chkHighQuality_k3n8.Value
    End With

    ' Build selected sheets array
    ReDim selectedSheets_k9n3(1 To selectedCount_k9m2) As String
    Dim idx_m7k2 As Long
    idx_m7k2 = 1

    For i_n7j3 = 0 To xpdf_lstSheets_k2n8.ListCount - 1
        If xpdf_lstSheets_k2n8.Selected(i_n7j3) Then
            selectedSheets_k9n3(idx_m7k2) = xpdf_lstSheets_k2n8.List(i_n7j3)
            idx_m7k2 = idx_m7k2 + 1
        End If
    Next i_n7j3

    ' Call PDF generation
    Dim result_k8m3 As Boolean
    result_k8m3 = xpdf_GeneratePDFDocument_m9k7( _
        mvarCurrentWorkbook_k9m2, _
        selectedSheets_k9n3, _
        settings_m9k7, _
        Me)

    ' Restore UI
    xpdf_lblProgressBar_n9k7.Visible = False
    xpdf_btnGeneratePDF_m8k3.Enabled = True

    If result_k8m3 Then
        xpdf_lblStatus_k7m9.Caption = "PDF generated successfully!"

        Dim response_k9m2 As VbMsgBoxResult
        response_k9m2 = MsgBox("PDF generated successfully!" & vbCrLf & vbCrLf & _
                               CStr(savePath_k8m4) & vbCrLf & vbCrLf & _
                               "Would you like to open the PDF?", _
                               vbQuestion + vbYesNo, "Success")

        If response_k9m2 = vbYes Then
            On Error Resume Next
            CreateObject("Shell.Application").Open CStr(savePath_k8m4)
        End If
    Else
        xpdf_lblStatus_k7m9.Caption = "PDF generation failed"
    End If

    Exit Sub

ErrorHandler:
    xpdf_lblProgressBar_n9k7.Visible = False
    xpdf_btnGeneratePDF_m8k3.Enabled = True
    MsgBox "Error generating PDF: " & Err.Description, vbCritical, "Generation Error"
    xpdf_lblStatus_k7m9.Caption = "Error during PDF generation"
End Sub

'===============================================================================
' CANCEL/CLOSE
'===============================================================================

Private Sub xpdf_btnCancel_n4j9_Click()
    Unload Me
End Sub
