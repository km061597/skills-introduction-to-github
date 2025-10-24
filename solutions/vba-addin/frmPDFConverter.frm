VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmPDFConverter
   Caption         =   "Smart Excel to PDF Converter"
   ClientHeight    =   8640
   ClientLeft      =   120
   ClientTop       =   465
   ClientWidth     =   11880
   OleObjectBlob   =   "frmPDFConverter.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmPDFConverter"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False

'=================================================================================
' Smart Excel to PDF Converter - UserForm Code
'=================================================================================

Option Explicit

Private CurrentWorkbook As Workbook
Private SheetAnalyses() As SheetAnalysis
Private SelectedSheetsCollection As Collection

'=================================================================================
' FORM INITIALIZATION
'=================================================================================
Private Sub UserForm_Initialize()
    ' Set up the form
    Me.Width = 600
    Me.Height = 500

    ' Initialize controls
    InitializeControls

    ' Try to use active workbook
    If Not ActiveWorkbook Is Nothing Then
        Set CurrentWorkbook = ActiveWorkbook
        AnalyzeCurrentWorkbook
    End If
End Sub

Private Sub InitializeControls()
    ' Populate orientation dropdown
    cboOrientation.Clear
    cboOrientation.AddItem "Auto (Recommended)"
    cboOrientation.AddItem "Portrait"
    cboOrientation.AddItem "Landscape"
    cboOrientation.ListIndex = 0

    ' Set default margin values
    txtLeftMargin.Value = "0.25"
    txtRightMargin.Value = "0.25"
    txtTopMargin.Value = "0.75"
    txtBottomMargin.Value = "0.75"

    ' Set default scale
    txtScale.Value = "100"

    ' Set checkboxes
    chkFitToWidth.Value = True
    chkIncludeHeaders.Value = True
    chkGridlines.Value = False

    ' Update scale textbox state
    UpdateScaleState
End Sub

'=================================================================================
' BUTTON EVENTS
'=================================================================================
Private Sub btnBrowse_Click()
    Dim filePath As String
    filePath = ExcelToPDF_Analyzer.BrowseForExcelFile()

    If filePath <> "" Then
        txtFilePath.Value = filePath
        LoadWorkbook filePath
    End If
End Sub

Private Sub btnUseActive_Click()
    If Not ActiveWorkbook Is Nothing Then
        Set CurrentWorkbook = ActiveWorkbook
        txtFilePath.Value = "Active Workbook: " & CurrentWorkbook.Name
        AnalyzeCurrentWorkbook
    Else
        MsgBox "No active workbook found!", vbExclamation
    End If
End Sub

Private Sub btnAnalyze_Click()
    If CurrentWorkbook Is Nothing Then
        MsgBox "Please select a workbook first!", vbExclamation
        Exit Sub
    End If

    AnalyzeCurrentWorkbook
End Sub

Private Sub btnSelectAll_Click()
    Dim i As Long
    For i = 0 To lstSheets.ListCount - 1
        lstSheets.Selected(i) = True
    Next i
End Sub

Private Sub btnSelectNone_Click()
    Dim i As Long
    For i = 0 To lstSheets.ListCount - 1
        lstSheets.Selected(i) = False
    Next i
End Sub

Private Sub btnGenerate_Click()
    GeneratePDFWithSettings
End Sub

Private Sub btnCancel_Click()
    Unload Me
End Sub

'=================================================================================
' CHECKBOX EVENTS
'=================================================================================
Private Sub chkFitToWidth_Click()
    UpdateScaleState
End Sub

Private Sub UpdateScaleState()
    txtScale.Enabled = Not chkFitToWidth.Value
    lblScale.Enabled = Not chkFitToWidth.Value
End Sub

'=================================================================================
' LISTBOX EVENTS
'=================================================================================
Private Sub lstSheets_Click()
    ' Show analysis when sheet is selected
    ShowSheetAnalysis
End Sub

'=================================================================================
' CORE FUNCTIONS
'=================================================================================
Private Sub LoadWorkbook(filePath As String)
    On Error GoTo ErrorHandler

    ' Close previous workbook if it wasn't the active one
    If Not CurrentWorkbook Is Nothing Then
        If CurrentWorkbook.Name <> ActiveWorkbook.Name Then
            CurrentWorkbook.Close SaveChanges:=False
        End If
    End If

    ' Open new workbook
    Set CurrentWorkbook = Workbooks.Open(filePath)

    AnalyzeCurrentWorkbook

    Exit Sub

ErrorHandler:
    MsgBox "Error loading workbook: " & Err.Description, vbCritical
End Sub

Private Sub AnalyzeCurrentWorkbook()
    On Error GoTo ErrorHandler

    If CurrentWorkbook Is Nothing Then Exit Sub

    ' Show progress
    lblStatus.Caption = "Analyzing workbook..."
    lblStatus.Visible = True
    DoEvents

    ' Analyze the workbook
    SheetAnalyses = ExcelToPDF_Analyzer.AnalyzeWorkbook(CurrentWorkbook)

    ' Populate sheet list
    PopulateSheetList

    ' Update status
    lblStatus.Caption = "Analysis complete! " & CurrentWorkbook.Worksheets.Count & " sheets found."

    Exit Sub

ErrorHandler:
    lblStatus.Caption = "Error during analysis"
    MsgBox "Error analyzing workbook: " & Err.Description, vbCritical
End Sub

Private Sub PopulateSheetList()
    Dim i As Long

    lstSheets.Clear

    For i = LBound(SheetAnalyses) To UBound(SheetAnalyses)
        lstSheets.AddItem SheetAnalyses(i).SheetName
    Next i

    ' Select all by default
    For i = 0 To lstSheets.ListCount - 1
        lstSheets.Selected(i) = True
    Next i
End Sub

Private Sub ShowSheetAnalysis()
    Dim selectedIndex As Long
    Dim i As Long
    Dim analysis As String

    ' Find selected sheet
    For i = 0 To lstSheets.ListCount - 1
        If lstSheets.Selected(i) Then
            selectedIndex = i + LBound(SheetAnalyses)
            Exit For
        End If
    Next i

    ' Build analysis text
    With SheetAnalyses(selectedIndex)
        analysis = "SHEET ANALYSIS: " & .SheetName & vbCrLf & vbCrLf
        analysis = analysis & "Dimensions: " & .RowCount & " rows × " & .ColumnCount & " columns" & vbCrLf
        analysis = analysis & "Used Range: " & .UsedRange & vbCrLf
        analysis = analysis & "Data Density: " & .DataDensity & vbCrLf
        analysis = analysis & "Has Headers: " & IIf(.HasHeaders, "Yes", "No") & vbCrLf
        analysis = analysis & "Estimated Pages: " & .EstimatedPages & vbCrLf & vbCrLf

        analysis = analysis & "RECOMMENDATIONS:" & vbCrLf
        analysis = analysis & "Orientation: " & .RecommendedOrientation & vbCrLf

        If .RequiresScaling Then
            analysis = analysis & "Scaling Required: Yes" & vbCrLf
            analysis = analysis & "Optimal Scale: " & .OptimalScale & "%" & vbCrLf

            ' Auto-apply recommendation
            chkFitToWidth.Value = False
            txtScale.Value = .OptimalScale
        Else
            analysis = analysis & "Scaling Required: No (Fit to width recommended)" & vbCrLf
            chkFitToWidth.Value = True
        End If

        If .HasWideColumns Then
            analysis = analysis & "Note: Contains wide columns - text wrapping enabled" & vbCrLf
        End If
    End With

    txtAnalysis.Value = analysis
End Sub

Private Sub GeneratePDFWithSettings()
    On Error GoTo ErrorHandler

    If CurrentWorkbook Is Nothing Then
        MsgBox "Please select a workbook first!", vbExclamation
        Exit Sub
    End If

    ' Collect selected sheets
    Set SelectedSheetsCollection = New Collection
    Dim i As Long

    For i = 0 To lstSheets.ListCount - 1
        If lstSheets.Selected(i) Then
            SelectedSheetsCollection.Add lstSheets.List(i)
        End If
    Next i

    If SelectedSheetsCollection.Count = 0 Then
        MsgBox "Please select at least one sheet!", vbExclamation
        Exit Sub
    End If

    ' Get save location
    Dim savePath As String
    savePath = ExcelToPDF_Analyzer.BrowseSaveLocation()

    If savePath = "" Then Exit Sub

    ' Get settings
    Dim orientation As String
    Select Case cboOrientation.ListIndex
        Case 0: orientation = "Auto"
        Case 1: orientation = "Portrait"
        Case 2: orientation = "Landscape"
    End Select

    Dim fitToWidth As Boolean
    fitToWidth = chkFitToWidth.Value

    Dim scalePercent As Long
    scalePercent = CLng(txtScale.Value)

    Dim leftMargin As Double, rightMargin As Double
    Dim topMargin As Double, bottomMargin As Double
    leftMargin = CDbl(txtLeftMargin.Value)
    rightMargin = CDbl(txtRightMargin.Value)
    topMargin = CDbl(txtTopMargin.Value)
    bottomMargin = CDbl(txtBottomMargin.Value)

    ' Show progress
    lblStatus.Caption = "Generating PDF..."
    lblStatus.Visible = True
    DoEvents

    ' Generate PDF
    ExcelToPDF_Analyzer.GeneratePDF _
        wb:=CurrentWorkbook, _
        SelectedSheets:=SelectedSheetsCollection, _
        OutputPath:=savePath, _
        orientation:=orientation, _
        FitToWidth:=fitToWidth, _
        ScalePercent:=scalePercent, _
        LeftMargin:=leftMargin, _
        RightMargin:=rightMargin, _
        TopMargin:=topMargin, _
        BottomMargin:=bottomMargin, _
        IncludeHeaders:=chkIncludeHeaders.Value, _
        IncludeGridlines:=chkGridlines.Value

    lblStatus.Caption = "PDF generated successfully!"

    ' Ask if user wants to open the PDF
    If MsgBox("Would you like to open the PDF?", vbQuestion + vbYesNo) = vbYes Then
        CreateObject("Shell.Application").Open savePath
    End If

    Exit Sub

ErrorHandler:
    lblStatus.Caption = "Error generating PDF"
    MsgBox "Error: " & Err.Description, vbCritical
End Sub
